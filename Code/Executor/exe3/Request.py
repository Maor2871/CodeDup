import json
from RequestFileCom import RequestFileCom
from FileInit import FileInit


class Request():
    """
        This class initializes requests instances.
    """

    def __init__(self, file_to_run, dir_name, request_id=0):

        # How many computers the request asks for that will run the running file.
        self.executors_amount = 0

        self.id = request_id

        # The name of the file to run.
        self.file_to_run = file_to_run

        # A list of all the additional files paths.
        self.additional_files = []

        # The directory in which the request actually saved in.
        self.dir = dir_name + "".join(self.file_to_run.split(".")[:-1]) + str(self.id) + "/"

        # True if the request has passed a validation test.
        self.validation_checked = False

        # True when the request has dismantled and stored in the data base.
        self.dismantled = False

        # If true the request is finished being handled in the server.
        self.request_died = False

        # Indicators of the sending function.

        # True if the server has received the file to run.
        self.received_file_to_run = False
        # The index of the additional file the server is currently receiving.
        self.sent_additional_files_index = 0
        # True if the current additional file has
        self.sent_current_additional_file = False
        # True if the current additional file has received in the server.
        self.server_received_current_additional_file = False
        # True if the server has received the full request.
        self.target_received_full_request = False

        self.setup()

    def setup(self):
        """
            The function setups necessary things relates to the new request.
        """

        pass

    def prepare_to_sending(self):
        """
            The function prepares the request for new sending.
        """

        # True if the server has received the file to run.
        self.received_file_to_run = False
        # The index of the additional file the server is currently receiving.
        self.sent_additional_files_index = 0
        # True if the current additional file has
        self.sent_current_additional_file = False
        # True if the current additional file has received in the server.
        self.server_received_current_additional_file = False
        # True if the server has received the full request.
        self.target_received_full_request = False

    @staticmethod
    def save_current_request(request_dict, path="current_request.txt"):
        """
            The function creates a new request file, by the received request dict.
        """

        RequestFileCom.enter_dict(request_dict, path)

    def update_run_file(self, data):
        """
            The function appends the received data to the file to run.
        """

        FileInit.make_dir(self.dir + "/" + self.file_to_run)

        with open(self.dir + "/" + self.file_to_run, "ab") as f:

            # Append the received data to the run file.
            f.write(data)

    def update_additional_file(self, name, data):
        """
            The function receives a name of an additional file and data. The function appends the data to the
             additional file.
        """

        # If it's the first time that is updating this file content, add its path to the additional files list.
        if name not in self.additional_files:

            self.additional_files.append(name)

        with open(self.dir + "/" + name, "ab") as f:

            # Append the received data to the additional file.
            f.write(data)

    def send_request(self, socket, dialog_box, general, header, request_id=""):
        """
            The function sends the request to the socket received and prints to the received dialog box that the request
             has received properly. The general argument is for notifying that the request has sent.
        """

        self.prepare_to_sending()

        # Convert the request of the user to dictionary.
        request_dict = RequestFileCom.file_to_dict()

        # The first thing to send is the file to run.
        file_to_run = request_dict["Run File"][:-1]
        header += "::Request::"

        if request_id:
            header += request_id + "::"

        # Send the server that the current client wishes to send him a new request. In addition, send him the name of
        # The request.
        socket.send(header + "New Request::" + file_to_run.split("\\")[-1])

        bytes_to_read = 1024 - len(header + "Uploading::Run File::")

        # Send the socket the file to run.
        with open(file_to_run, "rb") as f:

            content = f.read(bytes_to_read)
            content.replace("::", "%~")

            while len(content) >= bytes_to_read:

                socket.send(header + "Uploading::Run File::" + content)

                content = f.read(bytes_to_read)
                content = content.replace("::", "%~")

            if content:

                socket.send(header + "Uploading::Run File::" + content + "::~~Finished Sending The File~~")

        # Send the dictionary of the current request file.
        socket.send(header + "Uploading::Request Dict::" + json.dumps(request_dict))

        # Send the Commitments and Privileges values.
        socket.send(header + "Uploading::Executors Amount::" + RequestFileCom.get_value(
            "Executors Amount")[:-1])

        if "Additional Files" in request_dict:
            num_of_additional_files = len(request_dict["Additional Files"].split("@**"))
        else:
            num_of_additional_files = 0

        while not self.target_received_full_request:

            # Iterate over all the titles in the dictionary and send them with their values to the server.
            for title in request_dict:

                # True If the file to run has sent and there are more additional file that has to be sent to the server.
                if self.received_file_to_run and title == "Additional Files" and num_of_additional_files >= self.\
                        sent_additional_files_index + 1:

                    # If the current file hasn't been sent
                    if not self.sent_current_additional_file:

                        # All the additional file paths.
                        additional_files_paths = request_dict["Additional Files"]

                        # Iterate over all the additional file paths and send each additional file to the server.
                        additional_file_path = additional_files_paths.split("@**")[self.sent_additional_files_index]

                        if additional_file_path[-1] == "\n":

                            additional_file_path = additional_file_path[:-1]

                        additional_file_name = additional_file_path.split("\\")[-1]

                        bytes_to_read = 1024 - len(header + "Uploading::Additional File::" +
                                                   additional_file_name + "::")

                        # Send the server the additional file.
                        with open(additional_file_path, "rb") as f:

                            content = f.read(bytes_to_read)
                            content.replace("::", "%~")

                            while len(content) >= bytes_to_read:

                                socket.send(header + "Uploading::Additional File::" +
                                            additional_file_name + "::" + content)

                                content = f.read(bytes_to_read)
                                content = content.replace("::", "%~")

                            if content:

                                socket.send(header + "Uploading::Additional File::" + additional_file_name
                                            + "::" + content + "::~~Finished Sending The File~~")

                        self.sent_current_additional_file = True

                    # The server has received the current additional file.
                    elif self.server_received_current_additional_file:

                        self.sent_additional_files_index += 1
                        self.sent_current_additional_file = False
                        self.server_received_current_additional_file = False

            # True if the target has received the whole request properly.
            if self.received_file_to_run and num_of_additional_files <= self.sent_additional_files_index:

                self.received_file_to_run = False
                self.sent_additional_files_index = 0
                self.sent_current_additional_file = False
                self.server_received_current_additional_file = False
                self.target_received_full_request = True
                if dialog_box:
                    dialog_box.update_text("Request has received properly.")

                socket.send(header + "Finished Sending")

        general.send_request = False


class ServerRequest(Request):

    # A class variable, generates ids for new requests.
    current_id = 0

    def __init__(self, client, file_to_run, dir_name):

        Request.__init__(self, file_to_run, dir_name)

        # The id of the current request.
        self.id = ServerRequest.current_id

        ServerRequest.current_id += 1

        # True if the request has received in the server.
        self.full_request_has_arrived = False

        # The client that is responsible on the request.
        self.client = client

        # A list of the computers that are going to execute the request. If empty, there are no such computers yet.
        self.executors = []

        # True if the request has received in all the executors.
        self.sent_to_executors = False

        # A dict of the form: {Executor: Boolean indicator to satisfy weather the executor has finished executing the
        # current request}
        self.executors_finished = {}

        # True if the execution has completed by all the executors.
        self.status = "Processing"

    def setup(self):
        """
            The function creates the new request on the server.
        """

        FileInit.make_dir(self.dir)

        f = open(self.dir + "/" + self.file_to_run, "w")
        f.close()

    def find_executors(self):
        """
            The function finds computers in the system which can mach the requirements of the request. If not enough
            computers have found, aborts anything relates to handling the request.
        """

        # Make sure the request still being handled in the server.
        if not self.request_died:

            # A list of all the executors that are connected to the system.
            server_execute = self.client.general.executors

            # A list of all the executors that can execute the current request.
            can_execute = []

            # Iterate over all the executors that are connected to the system.
            for executor in server_execute:

                # Check if the executor can execute that current request.
                if executor.can_execute(self):

                    # He can, append it to the list of the executors which can execute the current request.
                    can_execute.append(executor)

            # Check if there are enough executors to execute the current request.
            if len(can_execute) >= self.executors_amount:

                # Enough executors have founded, now take those which are the most efficient to the current status of
                # the system.
                self.executors = self.will_execute(can_execute)

                # Update the executors_finished dict to follow the executors list.
                for executor in self.executors:
                    self.executors_finished[executor] = False

            else:

                self.client.client_communicator.send.messages_to_send.append("Request::Status::Not enough available "
                                                                             "computers::" + str(len(can_execute)))

                # There are not enough available executors to execute the request.
                self.abort_request()

    def check_validation(self):
        """
            The function checks the validation of the request. If the request doesn't valid abort anything relates to
            it. If it's valid allow the server to move the next step in the handling process.
        """

        # The request has check and is valid.
        self.validation_checked = True

    def dismantle(self):
        """
            The function dismantles the request and enters it into the data base.
        """

        # The request has dismantled properly.
        self.dismantled = True

    def send_to_executors(self):
        """
            The function sends the request to the executors.
        """

        # iterate over all the executors.
        for executor in self.executors:

            executor.current_requests[self.id] = self
            self.send_request(executor.executor_communicator.executor_socket, None, executor.general, "New Message",
                              str(self.id))

        self.sent_to_executors = True

    def abort_request(self):
        """
            The function aborts anything relates to the request in the system.
        """

        self.request_died = True
        self.client.general.current_requests.remove(self)
        self.client.current_request = None

    def update_status(self):
        """
            The function updates the current status of the request.
        """

        # An indicator weather the request has completed or not.
        flag = True

        # Iterate over all the executors.
        for executor in self.executors:

            if not self.executors_finished[executor]:

                flag = False
                break

        # If all the executors has finished executing the request set the request status as finished. If there are no
        # executors than the request haven't started yet.
        if flag and self.executors:

            self.status = "Finished"

    def will_execute(self, can_execute):
        """
            The function receives a list of executors that can execute the current request. The function calculates
            which executors are the best choice to send the request to in terms of efficiency
        """

        # For now, return the first executors of the can executors list.
        return can_execute[:self.executors_amount]


class ExecutorRequest(Request):
    """
        This class represents a request of an executor.
    """

    def __init__(self, file_to_run, dir_name, request_id=0):

        Request.__init__(self, file_to_run, dir_name, request_id)

        # If True the request has received and is now ready to be executed in the executor's environment.
        self.ready_to_execution = False

        # True if the executor has finished executing the request.
        self.execution_completed = False

        # The current status of the request.
        self.status = "Processing"

    def setup(self):
        """
            The function setups the request in the executor's request file system.
        """

        # In case the file system of the executor isn't constructed properly.
        FileInit.make_dir(self.dir)

        f = open(self.dir + "/" + self.file_to_run, "w")
        f.close()