import json
from MyThread import MyThread
from Request import ServerRequest
import select


class ClientCommunicator(MyThread):
    """
        The class represents a thread that is currently communicating with a specific client.
        Thread is necessary for the accept command, which may block the whole server.
    """

    def __init__(self, general, socket):

        MyThread.__init__(self, -1, "ClientCommunicator")

        # The connector to the important variables of the server.
        self.general = general

        # The socket which this thread is using to communicate with the client.
        self.socket = socket

        # The socket of the client that this thread is communicating with.
        self.client_socket = None

        # The client of this communicator.
        self.client = None

        # The instance that is responsible for receiving the data from the client.
        self.receive = None

        # The instance that is responsible for sending data to the client.
        self.send = None

        # True if there is a problem connecting to the client and the connection has to be stopped.
        self.client_disconnected = False

    def manager(self):
        """
            The function manages the communication with the client.
        """

        # Accept the client.
        (new_socket, address) = self.socket.accept()

        self.client_socket = new_socket

        # Create the instance that will receive the data from the client.
        self.receive = Receive(self, self.client_socket)

        # Start it.
        self.receive.start()

        # Create the instance that will send data to the client.
        self.send = Send(self, self.client_socket)

        # Start it.
        self.send.start()


class Receive(MyThread):
    """
        The class represents a thread that is listening for a client.
    """

    def __init__(self, communicator, client_socket):

        MyThread.__init__(self, -1, "ClientComReceive")

        # The communicator.
        self.communicator = communicator

        # The socket of the client.
        self.client_socket = client_socket

    def manager(self):
        """
            The function is responsible for receiving data from the client.
        """

        while not self.communicator.general.shut_down:

            # Receive a message from the client only if there is something to receive. Every 1 second check if the
            # server has to shut down.
            in_message, out_message, err_message = select.select([self.client_socket], [self.client_socket], [], 1)

            if in_message:

                try:

                    # Wait for data from the client.
                    message = self.client_socket.recv(1024)

                    messages = message.split("New Message::")

                    for message in messages:

                        self.follow_protocol(message)

                except Exception as e:

                    self.communicator.client_disconnected = True
                    return

    def follow_protocol(self, message):
        """
            The function checks what the client wants.
        """

        message = message.split("::")

        # Check if the client is trying to send the server new information about a request.
        if len(message) > 0 and message[0] == "Request":

            # The client wants to create new request.
            if len(message) > 2 and message[1] == "New Request":

                self.communicator.client.current_request = ServerRequest(self.communicator.client, message[2],
                                                                         "Requests/")

            elif len(message) > 1 and message[1] == "Received":

                if len(message) > 2 and message[2] == "File To Run Has Received":

                    self.communicator.client.current_request.received_file_to_run = True

                elif len(message) > 2 and message[2] == "Additional File Has Received":

                    self.communicator.client.current_request.server_received_current_additional_file = True

            # The client is trying to upload another packet with an information about the current request.
            elif len(message) > 1 and message[1] == "Uploading":

                if len(message) > 3 and message[2] == "Request Dict":

                    ServerRequest.save_current_request(json.loads(message[3]),
                                                       self.communicator.client.current_request.dir +
                                                       "current_request.txt")

                # The client is sending more data about the file to run. append it to the already received data.
                elif len(message) > 3 and message[2] == "Run File":

                    message[3].replace("%~", "::")

                    self.communicator.client.current_request.update_run_file(message[3])

                    if len(message) > 4 and message[4] == "~~Finished Sending The File~~":

                        self.communicator.send.messages_to_send.append("Request::Received::File To Run Has Received")

                elif len(message) > 3 and message[2] == "Additional File":

                    message[3].replace("%~", "::")

                    self.communicator.client.current_request.update_additional_file(message[3], message[4])

                    if len(message) > 5 and message[5] == "~~Finished Sending The File~~":

                        self.communicator.send.messages_to_send.append("Request::Received::Additional File Has " +
                                                                       "Received")

                elif len(message) > 3 and message[2] == "Executors Amount" and message[3].isdigit():

                    self.communicator.client.current_request.executors_amount = int(message[3])

            elif len(message) > 1 and message[1] == "Finished Sending":

                self.communicator.client.current_request.full_request_has_arrived = True


class Send(MyThread):
    """
        The class represents a thread that sends data to a client.
    """

    def __init__(self, communicator, client_socket):

        MyThread.__init__(self, -1, "ClientComSend")

        self.client_socket = client_socket

        self.communicator = communicator

        # Contains the messages to send the client.
        self.messages_to_send = []

    def manager(self):
        """
            The function responsible for sending data to the client.
        """

        while not self.communicator.general.shut_down:

            if self.messages_to_send:

                # Iterate over all the messages that are supposed to be sent to the client.
                for message in self.messages_to_send:

                    try:

                        # Send the message to the client.
                        self.client_socket.send("New Message::" + message)

                    except:

                        self.communicator.client_disconnected = True

                self.messages_to_send = []