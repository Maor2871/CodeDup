import socket
import json
from MyThread import MyThread
from Request import ExecutorRequest
from Request import Request
import select


class ThreadCommunication():
    """
        This class is responsible for everything relates to the communication with the others in the system.
    """

    def __init__(self, general_, ip, port):

        self.general = general_

        # The socket of the main server.
        self.socket = socket.socket()

        self.ip = ip

        self.port = port

        self.socket.connect((self.ip, self.port))

        self.send = None

        self.receive = None

    def start(self):
        """
            The function starts anything relates to the communication process.
        """

        self.send = Send(self)

        self.send.start()

        self.receive = Receive(self)

        self.receive.start()

    def disconnected(self):
        """
            This function gets called when the server disconnects.
        """

        self.general.server_online = False


class Receive(MyThread):
    """
        The class is responsible for anything relates to receiving data from others in the system.
    """

    def __init__(self, communication_):

        MyThread.__init__(self, 1, "Receive")

        self.communicator = communication_

        self.communication = communication_

        self.general = communication_.general

        # The main socket of the current server.
        self.socket = communication_.socket

        # The current message received.
        self.current_message = ""

    def manager(self):
        """
            The function represents the main of the class.
        """

        while not self.general.shut_down:

            # Receive a message from the server only if there is something to receive. Every 1 second check if the
            # executor has to shut down.
            in_message, out_message, err_message = select.select([self.socket], [self.socket], [], 1)

            if in_message:

                try:

                    # Receives a new message from an entity in the system.
                    messages = self.socket.recv(1024)

                except Exception as e:

                    self.communication.disconnected()
                    return

                messages = messages.split("New Message::")

                for message in messages:

                    self.current_message = message.split("::")

                    self.follow_protocol()

    def follow_protocol(self):
        """
            The function follows the message by the protocol of the system.
        """

        message = self.current_message

        if len(message) > 0 and message[0] == "Request":

            if len(message) > 2 and message[1].isdigit():

                # The id of the current request.
                request_id = int(message[1])

                # The header of the current sending.
                header = "Request::" + str(request_id) + "::"

                if request_id in self.general.requests_to_execute:
                    # The request itself.
                    current_request = self.general.requests_to_execute[request_id]
                else:
                    current_request = None

                # Update the message list from the server.
                message = [message[0]] + message[2:]

                # The server wants to create new request.
                if len(message) > 2 and message[1] == "New Request":

                    # Create a new request to execute.
                    self.general.requests_to_execute[request_id] = ExecutorRequest(message[2], "Requests_To_Execute/",
                                                                                   request_id)

                # The server is trying to upload another packet with an information about the current request.
                elif current_request and len(message) > 1 and message[1] == "Uploading":

                    if len(message) > 3 and message[2] == "Request Dict":

                        # The dictionary of the request has received, create the current_request file to the current
                        # uploaded request.

                        Request.save_current_request(json.loads(message[3]),
                                                     current_request.dir +
                                                     "/current_request.txt")

                    # The server is sending more data about the file to run. append it to the already received data.
                    elif len(message) > 3 and message[2] == "Run File":

                        message[3].replace("%~", "::")

                        current_request.update_run_file(message[3])

                        # The file to run has fully received.
                        if len(message) > 4 and message[4] == "~~Finished Sending The File~~":

                            # Tell the server that the file has received and that he can send new data about the
                            # request.
                            self.communicator.send.current_messages.append(header +
                                                                           "Received::File To Run Has Received")

                    # The server is sending more data about the current uploaded additional file.
                    elif len(message) > 3 and message[2] == "Additional File":

                        message[3].replace("%~", "::")

                        current_request.update_additional_file(message[3], message[4])

                        # The current uploaded additional file has fully received.
                        if len(message) > 5 and message[5] == "~~Finished Sending The File~~":

                            # Tell the server that the file has received and that he can send new data about the request.
                            self.communicator.send.current_messages.append(header + "Received::Additional File Has " +
                                                                           "Received")

                    elif len(message) > 3 and message[2] == "Executors Amount" and message[3].isdigit():

                        current_request.executors_amount = int(message[3])

                # The request to execute has just received from the server.
                elif current_request and len(message) > 1 and message[1] == "Finished Sending":

                    current_request.ready_to_execution = True

                # A new status was set to the request.
                elif len(message) > 4 and message[3] == "Status":

                    # The request has finished being executed in the server.
                    if message[4] == "Finished":

                        # Update the status of the request to finished.
                        self.general.requests_to_execute[request_id].status = "Finished"

        # A new message about the current status of the executor in the server.
        elif len(message) > 0 and message[0] == "Status":

            # The message relates to the status of the connection.
            if len(message) > 1 and message[1] == "Connection":

                # The server has removed the current executor.
                if len(message) > 2 and message[2] == "Removed":

                    self.general.shut_down = True


class Send(MyThread):
    """
         This class's instance sends anything which intended to be sent to other entities in the system.
    """

    def __init__(self, communication_):

        MyThread.__init__(self, 2, "Send")

        self.communication = communication_

        self.general = communication_.general

        # The main socket of the current Server.
        self.socket = communication_.socket

        # The current message this class has to send.
        self.current_messages = []

        # The current message the class sends. [client, content].
        self.message = []

    def manager(self):
        """
            The function represents the main of the class.
        """

        while not self.general.shut_down:

            # Check if the are messages to send.
            if self.current_messages:

                # Iterate over all the messages to send.
                for message in self.current_messages:

                    self.message = message

                    try:

                        # Send the content to the server thread as is.
                        self.socket.send("New Message::" + message)

                    except:

                        self.general.shut_down = True

                self.current_messages = []