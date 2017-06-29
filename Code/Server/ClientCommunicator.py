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

        # The socket of the thread as a server. With this socket the thread accepts the client.
        self.socket = socket

        # The socket of the client that the thread has accepted. with this socket the thread communicates with the client.
        self.client_socket = None

        # The client instance which this thread is communicating with.
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
		
		# save his socket so this thread will be able communicating with him.
        self.client_socket = new_socket

        # Create the instance which will receive the data from the client.
        self.receive = Receive(self, self.client_socket)

        # Start it.
        self.receive.start()

        # Create the instance which will send data to the client.
        self.send = Send(self, self.client_socket)

        # Start it.
        self.send.start()


class Receive(MyThread):
    """
        The class represents a thread that is listening for a client.
    """

    def __init__(self, communicator, client_socket):

        MyThread.__init__(self, -1, "ClientComReceive")

        # The main communicator of this thread.
        self.communicator = communicator

        # The socket of the client.
        self.client_socket = client_socket

    def manager(self):
        """
            The function is responsible for receiving data from the client.
        """
		
		# Keep this thread alive as long the server is on air.
        while not self.communicator.general.shut_down:
			
			# In case there will be a problem communicating with the client.
            try:

                # Receive a message from the client only if there is something to receive. Every 1 second check if the
                # server has to shut down and this thread should get finished.
                in_message, out_message, err_message = select.select([self.client_socket], [self.client_socket], [], 1)
				
				# Check if there is a message to receive.
                if in_message:

                    # Receive the message.
                    message = self.client_socket.recv(1024)
					
					# In case different messages stick together.
                    messages = message.split("New Message::")
					
					# Iterate over all the messages and handle each.
                    for message in messages:
						
						# handle the current message.
                        self.follow_protocol(message)
			
			# An error receiving the message form the client has occurred. Disconnect the client from the server.
            except:

                self.communicator.client_disconnected = True
				
				# Stop the thread.
                return

    def follow_protocol(self, message):
        """
            The function checks what the client wants.
        """
		
		# split the message to its headers.
        message = message.split("::")


class Send(MyThread):
    """
        The class represents a thread that sends data to a client.
    """

    def __init__(self, communicator, client_socket):

        MyThread.__init__(self, -1, "ClientComSend")
		
		# The socket of the client.
        self.client_socket = client_socket

		# The main communicator of this thread.
        self.communicator = communicator

        # Contains the messages to send the client.
        self.messages_to_send = []

    def manager(self):
        """
            The function responsible for sending data to the client.
        """

		# Keep this thread alive as long the server is on air.
        while not self.communicator.general.shut_down:
			
			# Check if there are any messages to send.
            if self.messages_to_send:

                # Iterate over all the messages that are supposed to be sent to the client.
                for message in self.messages_to_send:

                    try:

                        # Send the message to the client.
                        self.client_socket.send("New Message::" + message)
					
					# An error communicating with the client occurred. Disconnect the client.
                    except:

                        self.communicator.client_disconnected = True
				
				# Empty the messages to send list, all the messages in it were handled.
                self.messages_to_send = []