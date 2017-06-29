import socket
from MyThread import MyThread
import select


class MainCommunication():
    """
        This class is responsible for everything relates to the communication with the others in the system.
    """

    def __init__(self, general_, ip, port, create_thread):

        self.general = general_

        # The socket of the main server.
        self.socket = socket.socket()

        self.ip = ip

        self.port = port

        try:
            self.socket.connect((self.ip, self.port))

            self.socket.send("New Message::Client")

        except:
            self.disconnected()

        self.send = None

        self.receive = None

        # The function that creates the thread communicator.
        self.create_thread = create_thread

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
                    message = self.socket.recv(1024)

                except:

                    self.communication.disconnected()
                    break

                self.current_message = message.split("::")

                self.follow_protocol()

    def follow_protocol(self):
        """
            The function follows the message by the protocol of the system.
        """

        message = self.current_message

        if len(message) == 2 and message[0] == "Client has connected properly" and message[1].isdigit():

            self.general.window.dialog_box.update_text("You have connected properly to the server!")

            # Make sure there isn't already such a communicator.
            if not self.general.thread_com:

                # Create and start the thread communicator.
                self.communication.create_thread(self.communication.ip, int(message[1]))

        elif len(message) == 1 and message[0] == "Server Full":

            self.general.window.dialog_box.update_text("The server is currently full, please try again later or contact"
                                                       " with your manager.")

class Send(MyThread):
    """
         This class's instance sends anything which intended to be sent to other entities in the system.
    """

    def __init__(self, communication_):

        MyThread.__init__(self, 2, "Send")

        self.general = communication_.general

        # The main socket of the current Server.
        self.socket = communication_.socket

        # The communicator of the current send instance.
        self.communicator = communication_

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

                    # call the function which send the message.
                    self.send()

    def send(self):
        """
            The function sends the message in self.message to the entity in the system it should be sent to.
        """

        # The entity to send the message to.
        entity = self.message[0]

        # The message itself.
        content = self.message[1]

        try:

            # Send the content to the entity as is.
            entity.socket.send(content)

        except:

            self.communicator.disconnected()