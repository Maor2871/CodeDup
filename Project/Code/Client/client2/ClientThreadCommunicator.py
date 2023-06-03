import socket
import select
from MyThread import MyThread
from time import sleep


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

        self.general.window.dialog_box.update_text("Server is now offline.")
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

        while not self.general.shutdown:

            # Receive a message from the server only if there is something to receive. Every 1 second check if the
            # client has to shut down.
            in_message, out_message, err_message = select.select([self.socket], [self.socket], [], 1)

            if in_message:

                try:

                    # Receives a new message from an entity in the system.
                    messages = self.socket.recv(1024)

                except:

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

            if len(message) > 1 and message[1] == "Received":

                if len(message) > 2 and message[2] == "File To Run Has Received":

                    self.communication.send.received_file_to_run = True
                    self.communicator.general.current_request.received_file_to_run = True

                elif len(message) > 2 and message[2] == "Additional File Has Received":

                    self.communication.send.server_received_current_additional_file = True
                    self.communicator.general.current_request.server_received_current_additional_file = True

            elif len(message) > 1 and message[1] == "Status":

                if len(message) > 3 and message[2] == "Not enough available computers":

                    self.communication.general.window.dialog_box.update_text("There are only: " + message[3] +
                                                                             " executors that can execute your current"
                                                                             " request.")

                elif len(message) > 2 and message[2] == "Server Full":

                    self.communication.general.window.dialog_box.update_text("There is no more room for new request "
                                                                             "currently, Talk to your manager for more"
                                                                             "information.")

                elif len(message) > 3 and message[2] == "Enough available computers":

                    request_executors_ids = message[3].split(', ')
                    request_executors_ids = [int(executor_id) for executor_id in request_executors_ids]
                    self.communication.general.window.monitor_window.init_monitors_request(request_executors_ids)

                # A new output about the current request has received.
                if len(message) > 4 and message[2] == "New Output" and message[4].isdigit():

                    new_output = message[3]

                    executor_id = int(message[4])

                    # Append the received output to the current one.
                    self.general.window.monitor_window.new_output(new_output, executor_id)

                elif len(message) > 4 and message[2] == "Last Output" and message[4].isdigit():

                    new_output = message[3]

                    executor_id = int(message[4])

                    # Replace the received output with the current one.
                    self.general.window.monitor_window.new_output(new_output, executor_id, True)

                elif len(message) > 2 and message[2] == "Finished":

                    # If True, The request was never started being executed in the server.
                    if len(message) > 3 and message[3] == "Never Started":

                        pass

                    else:

                        self.communication.general.window.dialog_box.update_text("The server has finished executing "
                                                                                 "your request. If you are convinced "
                                                                                 "that your request was not completed, "
                                                                                 "talk to your manager.")

                elif len(message) > 2 and message[2] == "File is now running":

                    executor_id = int(message[3])

                    self.communication.general.window.monitor_window.update_status(executor_id, "Executing")

                elif len(message) > 2 and message[2] == "File has finished running":

                    executor_id = int(message[3])

                    self.communication.general.window.monitor_window.update_status(executor_id, "Finished")

        elif len(message) > 0 and message[0] == "Status":

            if len(message) > 1 and message[1] == "Connection":

                if len(message) > 2 and message[2] == "Removed":

                    self.communication.general.window.dialog_box.update_text("The manager has removed you from the"
                                                                             " system.")

                    sleep(3)
                    self.general.shutdown = True


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

        while not self.general.shutdown:

            # Check if the are messages to send.
            if self.current_messages:

                # Iterate over all the messages to send.
                for message in self.current_messages:

                    self.message = message

                    # Send the content to the server thread as is.
                    self.socket.send("New Message::" + message)

                self.current_messages = []

    def send_request(self):
        """
            The function sends the current request.
        """

        self.communication.general.current_request.send_request(self.socket, self.general.window.dialog_box,
                                                                self.general, "New Message")