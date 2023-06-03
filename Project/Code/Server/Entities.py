class Client():
    """
        The class represent a client that has connected to the system.
    """

    # The id of the last client who has connected to the server.
    id = 0

    def __init__(self, general_, ip, id_, socket_, client_communicator):

        # The id of the client. The system uses this id in some cases in order to identify a client.
        self.id = id_
        # Alert the server that the current available id was taken.
        general_.next_client_id = -1

        # The ip of the client.
        self.ip = ip

        # The socket of the client. With this socket the system can communicate with the client.
        self.socket = socket_

        # The thread that this server is using in order to communicate with the current client.
        self.client_communicator = client_communicator

        # Set the client's communicator the client itself.
        self.client_communicator.client = self

        # Contains variables that the class needs.
        self.general = general_

        # The current request of the client.
        self.current_request = None

        # Start the communicator of the client.
        self.client_communicator.start()

    def send_connected(self):
        """
            The function sends the new client a message. This message tells him that he is now connected to the server
            and passes him the port that he'll use to communicate with his thread communicator.
        """

        self.general.send([self, "Client has connected properly::" +
                                 str(self.client_communicator.socket.getsockname()[1])])

    def disconnect(self):
        """
            The function disconnects the client from the server.
        """

        if self.current_request:
            self.current_request.status = "Finished"

        self.general.open_entities_sockets.remove(self.socket)
        self.general.clients.remove(self)
        self.client_communicator.socket.close()
        self.client_communicator.client_socket.close()

    def abort_request(self):
        """
            The function alert the client that his request was aborted and won't be executed anymore by the server.
        """

        # Send the client a message that his request will not be executed anymore in the server.
        self.client_communicator.send.messages_to_send.append("Request::Status::Finished")

        # Remove the current request of the client.
        self.current_request = None


class Executor():
    """
        The class represents an executor that has connected to the system.
    """

    def __init__(self, general_, ip, id_, socket_, executor_communicator):

        # The id of the executor. The system uses this id in some cases in order to identify an executor.
        self.id = id_

        # The ip of the executor.
        self.ip = ip

        # The socket of the executor. With this socket the system can communicate with the executor.
        self.socket = socket_

        # The thread that this server is using in order to communicate with the current executor.
        self.executor_communicator = executor_communicator

        # Set the executor's communicator the executor itself.
        self.executor_communicator.client = self

        # Contains variables that the class needs.
        self.general = general_

        # A dict containing the current requests of the executor.
        self.current_requests = {}

        # A dict with one key that contains the current data package of the executor and a flag do determine weather the
        # data package have already updated by the server in the system. {is_updated: data package}
        self.data_package = {}

        # Start the communicator of the executor.
        self.executor_communicator.start()

    def send_connected(self):
        """
            The function sends the new executor a message. This message tells him that he is now connected to the server
            and passes him the port that he'll use to communicate with his thread communicator.
        """

        self.general.send([self, "Executor has connected properly::" +
                                 str(self.executor_communicator.socket.getsockname()[1])])

    def disconnect(self):
        """
            The function disconnects the executor from the server.
        """

        # Remove the executor from the data base.
        if self.current_requests:
            for request in self.current_requests.values():
                if request in self.general.current_requests:
                    self.general.current_requests.remove(request)
        self.general.open_entities_sockets.remove(self.socket)
        self.general.executors.remove(self)
        self.executor_communicator.socket.close()
        self.executor_communicator.executor_socket.close()

    def can_execute(self, request):
        """
            The function checks if the executor has enough resources to execute the received request.
        """

        if request:
            return True

    def abort_request(self, request):
        """
            The function receives request and removes it from the current requests of the client.
        """

        # Send the executor a message that the server has no more interest in the current request.
        self.executor_communicator.send.messages_to_send.append("Request::Status::" + str(request.id) + "::Finished")

        self.current_requests.pop(request.id)