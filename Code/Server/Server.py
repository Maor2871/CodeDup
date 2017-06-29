import select
import socket
import datetime
import wx
import sys
from ClientCommunicator import ClientCommunicator
from MyThread import MyThread
from ExecutorCommunicator import ExecutorCommunicator
from ServerFileInit import FileInit
from Data_Base import DataBase
from Entities import Client, Executor
from GUI import Frame


class GeneralVariables():
    """
        The attributes of this class don't have any other class to relate but they are necessary for the server.
    """

    def __init__(self):

        # All the clients that have signed to the system.
        self.clients = []

        # All the executors that have signed to the system.
        self.executors = []

        # All the sockets of the clients that have signed to the system.
        self.open_entities_sockets = []

        # The communication instance of the server.
        self.com = None

        # The main frame of the gui.
        self.window = None

        # Creating the data base of the current client.
        self.data_base = DataBase(self, "SystemData", "Cla9ss#if+ied", "lsdjkfn^gksfdog7#")

        # A list off all the requests that the server is currently handling.
        self.current_requests = []

        # The main code of the Server.
        self.main = None

        # The App of wx.
        self.app = None

        # The panel which is responsible on the current amount of clients and executors in the system
        # and their limits.
        self.connected_panel = None

        # If True there is a command to shut down the server.
        self.shut_down = False

        # True if the gui have closed.
        self.gui_closed = False

        # If True the GUI has to update its records about the data base.
        self.update_data_base_gui = False

        # The next free ids.
        self.next_client_id = -1
        self.next_executor_id = -1
        self.next_request_id = -1

        # Deletes the table.
        self.delete_table = ""

        # Disconnects the rows of the table. A dict of the form: {table name: [list of rows]}
        self.remove_from_table = {}

    def get_client_by_socket(self, client_socket):
        """
            The function receives a socket of a signed client. Returns the client instance which the socket belongs to.
        """

        for client in self.clients:

            if client.socket is client_socket:

                return client

        return None

    def send(self, message):
        """
            The function transfer the message to the function which sends the message to other entities. Useful for
            cleaner code.
        """

        self.com.send.current_messages.append(message)


class Communication():
    """
        This class is responsible for everything relates to the communication with the others in the system.
    """

    def __init__(self, general_):

        self.general = general_

        self.socket = socket.socket()

        self.ip = "0.0.0.0"

        self.port = 7687

        self.socket.bind((self.ip, self.port))

        self.socket.listen(10)

        # The receive instance.
        self.receive = None

        # The send instance.
        self.send = None

    def start(self):
        """
            The function starts anything relates to the communication process.
        """

        # Create the send instance.
        self.send = Send(self)

        # Start the start instance.
        self.send.start()

        # Create the receive instance.
        self.receive = Receive(self)

        # Start the receive instance.
        self.receive.start()

    def generate_socket(self):
        """
            The function generates new socket for a new client or executor.
        """

        # Create a new socket.
        new_socket = socket.socket()

        # Bind the new socket with the ip of the server but use different open port.
        new_socket.bind((self.ip, 0))

        new_socket.listen(1)

        return new_socket


class Receive(MyThread):
    """
        The class is responsible for anything relates to receiving data from others in the system. message
    """

    def __init__(self, communication_):

        MyThread.__init__(self, 1, "Receive")

        self.communication = communication_

        self.general = communication_.general

        # The main socket of the current server.
        self.socket = communication_.socket

        # The current message received.
        self.current_message = ""

        # Contains the socket of the entity which sent the current message.
        self.current_socket = None

        self.current_client = None

        self.current_executor = None

    def manager(self):
        """
            The function represents the main of the class.
        """

        while not self.general.shut_down:

            rlist, wlist, xlist = select.select([self.socket] + self.general.open_entities_sockets,
                                                self.general.open_entities_sockets, [], 1)

            for entity_socket in rlist:

                # A new client or executor is trying to connect the server.
                if entity_socket is self.socket:

                    # Accept the client to the server.
                    (new_socket, address) = self.socket.accept()

                    # Make sure the entity which is trying to connect is new.
                    if new_socket not in self.general.open_entities_sockets:

                        # The ip of the new socket.
                        ip = list(address)[0]

                        self.current_socket = new_socket

                        data = self.current_socket.recv(1024)

                        if data == "New Message::Client":

                            # Make sure the system clients population isn't full.
                            if int(self.general.connected_panel.clients_counter.count) < \
                                    int(self.general.connected_panel.clients_counter.max):

                                self.sign_up_client(ip)
                                self.general.connected_panel.clients_counter.inc()

                            else:

                                self.current_socket.send("Server Full")

                        elif data == "New Message::Executor":

                            # Make sure the system executors population isn't full.
                            if int(self.general.connected_panel.executors_counter.count) < \
                                    int(self.general.connected_panel.executors_counter.max):

                                self.sign_up_executor(ip)
                                self.general.connected_panel.executors_counter.inc()
                            else:
                                self.current_socket.send("Server Full")

                # It's an already signed in entity, check what it wants.
                else:

                    # Update the current socket.
                    self.current_socket = entity_socket

                    # In case the client has disconnected or facing network problems.
                    try:

                        # Receives a new message from the current socket.
                        message = entity_socket.recv(1024)

                    # Continue to the next entity.
                    except:

                        continue

                    # convert the message to a list, each element is the title of the next one.
                    self.current_message = message.split("::")

                    # Send the message to follow_protocol which will direct it to the right part in the code according
                    # to the protocol rules.
                    self.follow_protocol()

    def follow_protocol(self):
        """
            The function follows the message by the protocol of the system.
        """

        message = self.current_message

        # Check if it's a client or an executor.
        if message[0] == "Client":

            pass

        elif message[0] == "Executor":

            pass

    def sign_up_client(self, ip):
        """
            The function signs the socket in self.current_socket in to the system as a client. Creates a new thread
            that will communicate with him.
        """

        new_socket = self.current_socket

        # Add the socket of the client to the open_clients_socket list.
        self.general.open_entities_sockets.append(new_socket)

        # Create the new client a thread which he'll use to communicate with the server.
        client_communicator = ClientCommunicator(self.general, self.communication.generate_socket())

        # Wait until the server will supply a new id for the next new client.
        while self.general.next_client_id == -1:
            pass

        # Create the new client.
        current_client = Client(self.general, ip, self.general.next_client_id, new_socket, client_communicator)

        client_communicator.client = current_client

        # Add the new client to the system.
        self.general.clients.append(current_client)

        # Insert the client to the data base.
        self.general.main.new_clients_ids.append(current_client.id)

        # Notify the client that he is now connected to the server. Send him the new socket he'll communicate with.
        current_client.send_connected()

    def sign_up_executor(self, ip):
        """
            The function signs the socket in self.current_socket in to the system as an executor. Creates a new thread
            that will communicate with him.
        """

        new_socket = self.current_socket

        # Add the socket of the executor to the open_entities_sockets list.
        self.general.open_entities_sockets.append(new_socket)

        # Create the new executor a thread which he'll use to communicate with the server.
        executor_communicator = ExecutorCommunicator(self.general, self.communication.generate_socket())

        # Wait until the server will supply a new id for the next new client.
        while self.general.next_executor_id == -1:
            pass

        # Create the new executor.
        current_executor = Executor(self.general, ip, self.general.next_executor_id, new_socket,
                                    executor_communicator)

        executor_communicator.executor = current_executor
        executor_communicator.executor_id = current_executor.id

        # Add the new client to the system.
        self.general.executors.append(current_executor)

        # Insert the entity to the data base.
        self.general.main.new_executors_ids.append(current_executor.id)

        # Notify the client that he is now connected to the server. Send him the new socket he'll communicate with.
        current_executor.send_connected()


class Send(MyThread):
    """
         This class's instance sends anything which intended to be sent to other entities in the system.
    """

    def __init__(self, communication_):

        MyThread.__init__(self, 2, "Send")

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

                    # call the function which send the message.
                    self.send()

                self.current_messages = []

    def send(self):
        """
            The function sends the message in self.message to the entity in the system it should be sent to.
        """

        # The client to send the message to.
        client = self.message[0]

        # The message itself.
        content = self.message[1]

        # Send the content to the client.
        client.socket.send(content)


class Main(MyThread):

    def __init__(self, general_):

        MyThread.__init__(self, -1, "main")

        self.general = general_

        self.new_clients_ids = []

        self.new_executors_ids = []

    def manager(self):
        """
            The function runs the main code of the client as a thread.
        """

        # Create the files and directories of the system in the server.
        FileInit.init_files()

        # Connect to the data base.
        self.general.data_base.connect("System Data")

        self.build_data_base()

        # The instance this client is going to use in order to commit ant type of outside communication.
        general.com = Communication(general)

        # Start the communication thread. Receive and Send are beginning to operate in the background.
        general.com.start()

        while not self.general.shut_down:

            # Generate new ids if necessary.
            self.generate_ids()

            # Enter all the new entities to the data base.
            self.sign_up_new_entities_to_db()

            # Check if a client or executor has disconnected from the server or has a network problem. Disconnect him if
            # he does.
            self.look_for_disconnected_clients()
            self.look_for_disconnected_executors()

            # Check if the manager wants to delete something from the data base.
            self.delete_from_db()

            # If there are new requests, add them to the requests to handle list.
            self.look_for_new_requests()

            # Handle all the requests that are currently waiting for the server for setting them up in the system.
            self.handle_requests()

            # Check if new data packages has received and update the system according to them.
            # self.look_for_data_packages()

            if self.general.update_data_base_gui:

                self.general.window.cp_window.pub_update_records(self.general.data_base.db_to_string())

                self.general.update_data_base_gui = False

        # The server has to shut down. Stop the main process.
        if not self.general.gui_closed:
            self.general.window.on_quit(wx.EVT_CLOSE)

        sys.exit()

    def look_for_new_requests(self):
        """
            The function iterates over all the connected clients and checks if a new request has received. If a new
            request has received, inserts it to the list that handles the request in the server.
        """

        for client in self.general.clients:

            if client.current_request and not client.current_request in self.general.current_requests:

                # Insert the new request to the list of the current requests the server has to handle.
                self.general.current_requests.append(client.current_request)

                # Insert the new request to the data base.
                self.general.data_base.insert("Requests", [str(client.current_request.id),
                                                           '"' + datetime.datetime.now().
                                              strftime("%I:%M %p on %d/%m/%Y") + '"', '"' + "Online" + '"'])

                self.general.connected_panel.requests_counter.inc()

                self.general.next_request_id = -1

    def look_for_disconnected_clients(self):
        """
            The function checks if there are clients that are announced as disconnected so the connection with them has
            to be stopped.
        """

        for client in self.general.clients:

            if client.client_communicator.client_disconnected:

                self.general.data_base.replace("Clients", [["Id", str(client.id)]], ["Status", "Offline"])

                # If the client has a request abort it.
                if client.current_request:
                    client.current_request.status = "Finished"

                client.disconnect()

                self.general.connected_panel.clients_counter.dec()

    def look_for_disconnected_executors(self):
        """
            The function checks if there are executors that are announced as disconnected so the connection with them
            has to be stopped.
        """

        for executor in self.general.executors:

            if executor.executor_communicator.executor_disconnected:

                self.general.data_base.replace("Executors", [["Id", str(executor.id)]], ["Status", "Offline"])
                executor.disconnect()
                self.general.connected_panel.executors_counter.dec()

    def handle_requests(self):
        """
            The function handles all the requests in the server.
        """

        # Iterate over all the requests that the server is currently handling.
        for request in self.general.current_requests:

            # Update the current status of the request.
            request.update_status()

            # Handle the request only if it have received properly.
            if request.full_request_has_arrived and not request.status == "Finished":

                # If the request hasn't been checked yet, check if it's valid.
                if not request.validation_checked:

                    request.check_validation()

                # If the request didn't dismantle yet, dismantle it.
                if not request.dismantled:

                    request.dismantle()

                # look for computers to run the requests on.
                if not request.executors:

                    request.find_executors()

                # The request is ready. If hasn't sent to the executors, send it.
                if not request.sent_to_executors:

                    request.send_to_executors()

            # The request has finished executing or was aborted.
            elif request.status == "Finished":

                self.remove_request(request)

    def build_data_base(self):
        """
            The function creates the tables of the databases and setting it up.
        """

        self.general.data_base.create_table("Clients", [["Id", "INT"], ["Name", "TEXT"], ["Login_Date", "TEXT"],
                                                        ["Status", "TEXT"], ["IP", "TEXT"]])
        self.general.data_base.create_table("Executors", [["Id", "INT"], ["Login_Date", "TEXT"], ["Status", "TEXT"],
                                                          ["IP", "TEXT"]])
        self.general.data_base.create_table("Requests", [["Id", "INT"], ["Arrived_at", "TEXT"], ["Status", "TEXT"]])

        self.general.data_base.replace("Clients", [["Status", "Online"]], ["Status", "Offline"])
        self.general.data_base.replace("Executors", [["Status", "Online"]], ["Status", "Offline"])
        self.general.data_base.replace("Requests", [["Status", "Online"]], ["Status", "Offline"])

    def sign_up_new_entities_to_db(self):
        """
            The function enters the new client to the data base.
        """

        for i in range(len(self.new_clients_ids)):

            client = [client for client in self.general.clients if client.id == self.new_clients_ids[i]][0]

            self.general.data_base.insert("Clients",
                                          [str(self.new_clients_ids[i]), '"' + "Guest" + str(self.new_clients_ids[i]) +
                                                                         '"', '"' + datetime.datetime.now().
                                          strftime("%I:%M %p on %d/%m/%Y") + '"', '"' + "Online" + '"',
                                          '"' + client.ip + '"'])

            self.new_clients_ids[i] = "*"
            # Alert the server that the current available id was taken.
            self.general.next_client_id = -1

        for i in range(len(self.new_executors_ids)):

            executor = [executor for executor in self.general.executors if executor.id == self.new_executors_ids[i]][0]

            self.general.data_base.insert("Executors", [str(self.new_executors_ids[i]), '"' + datetime.datetime.now().
                                          strftime("%I:%M %p on %d/%m/%Y") + '"', '"' + "Online" + '"', '"' +
                                                                                                        executor.ip
                                                                                                        + '"'])

            self.new_executors_ids[i] = "*"

            # Alert the server that the current available id was taken.
            self.general.next_executor_id = -1

        self.new_clients_ids = [client_id for client_id in self.new_clients_ids if client_id != "*"]
        self.new_executors_ids = [executor_id for executor_id in self.new_executors_ids if executor_id != "*"]

    def look_for_data_packages(self):
        """
            The function iterates over all the executors and checks if there a new data packages. A data package is a
            new data from an executor about a running request.
        """

        # Iterate over all the connected executors.
        for executor in self.general.executors:

            # Check if the executor has new data package.
            if executor.data_package.keys() and executor.data_package.keys()[0]:

                # Extract the data package from the dict.
                package = executor.data_package.values()[0]

                # Update the data package in the data base.
                self.update_data_package_db(package)

                # Send the data package to the client who owns the request if he wants it.
                self.send_data_package_to_client()

    def delete_from_db(self):
        """
            The function checks if there is something to delete from the data base.
        """

        if self.general.delete_table:

            table_name = self.general.delete_table

            if table_name == "Clients" or table_name == "Executors" or table_name == "Requests":

                self.general.data_base.delete_table(table_name, [["Status", "Offline"]])
                self.general.next_client_id = -1
                self.general.next_executor_id = -1
                self.general.next_request_id = -1

            else:

                self.general.data_base.delete_table(table_name)

            self.general.delete_table = ""

        if self.general.remove_from_table:

            for table_name in self.general.remove_from_table:

                items = self.general.remove_from_table[table_name]

                if table_name == "Clients":

                    # A list of all the clients that own the ids in the ids_list.
                    entities_list = [client for client in self.general.clients if client.id in items]

                    for client in entities_list:

                        client.client_communicator.client_disconnected = True

                        # Notify the client that he has removed from the system.
                        try:
                            client.client_communicator.send.messages_to_send.append("Status::Connection::Removed")
                        except:
                            pass

                elif table_name == "Executors":

                    # A list of all the clients that own the ids in the ids_list.
                    entities_list = [executor for executor in self.general.executors if executor.id in items]

                    for executor in entities_list:

                        executor.executor_communicator.executor_disconnected = True

                        # Notify the executor that he has removed from the system.
                        try:
                            executor.executor_communicator.send.messages_to_send.append("Status::Connection::Removed")
                        except:
                            pass

                elif table_name == "Requests":

                    # A list of all the clients that own the ids in the ids_list.
                    entities_list = [request for request in self.general.current_requests if request.id in items]

                    for request in entities_list:

                        request.status = "Finished"

            self.general.remove_from_table = {}

    def generate_ids(self):
        """
            The function generates the next available ids.
        """

        if self.general.next_client_id == -1:
            self.general.next_client_id = self.general.data_base.get_free_id("Clients")

        if self.general.next_executor_id == -1:
            self.general.next_executor_id = self.general.data_base.get_free_id("Executors")

        if self.general.next_request_id == -1:
            self.general.next_request_id = self.general.data_base.get_free_id("Requests")

    def remove_request(self, request):
        """
            The function receives a request and removes it from the server.
        """

        # Change the status of the request in the data base to offline.
        self.general.data_base.replace("Requests", [["Id", str(request.id)]], ["Status", "Offline"])

        self.general.connected_panel.requests_counter.dec()

        # Abort anything the request "knows". The request point of view.
        request.abort_request()

        # Set the request offline. The server point of view.
        self.general.current_requests.remove(request)

    def update_data_package_db(self, package):
        """
            The function receives a data package and updates it in the db.
        """

        pass

    def send_data_package_to_client(self):
        """
            The function receives a data package and sends it to the client who owns the request.
        """

        pass


#-----Main Code-----#


# general is an instance that is going to contain many variables that are necessary in multiple areas in the code.
general = GeneralVariables()

general.main = Main(general)

# Start the GUI of the Server.
general.app = wx.App()

# Create the main frame of the GUI.
general.window = Frame(None, -1, "CodeDup", general)

general.main.start()

# Start the GUI main loop.
general.app.MainLoop()