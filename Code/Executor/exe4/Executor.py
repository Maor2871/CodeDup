import sys
import os
from MyThread import MyThread
from FileInit import FileInit
from ExecutorMainCommunicator import MainCommunication
from ExecutorThreadCommunicator import ThreadCommunication
from RequestExecutor import RequestExecutor


#-----Classes-----#


class GeneralVariables():
    """
        The attributes of this class don't have any other class to relate but they are necessary for this executor.
    """

    def __init__(self):

        # The communication instance that has the ability to communicate with the main server.
        self.main_com = None

        # The communication instance that has the ability to communicate with the thread communicator of this executor
        # in the server.
        self.thread_com = None

        # All the requests that this executor has to execute. {id: request}
        self.requests_to_execute = {}

        # All the requests that this executor has to execute and their executors.
        # {request to execute: the request executor}
        self.current_requests = {}

        # True if the server isn't disconnected.
        self.server_online = True

        # If True the current executor is intended to be closed.
        self.shut_down = False


class Main(MyThread):
    """
        This class contains all the main operations of this executor.
    """

    def __init__(self, general_):

        MyThread.__init__(self, -1, "main")

        self.general = general_

    def manager(self):
        """
            The function runs the main code of the executor as a thread.
        """

        # Setup all the files and folders that are necessary for this executor.
        FileInit.executor_init_files()

        # Setup the communication of this executor with the Main server of the system.
        self.general.main_com = MainCommunication(self.general, "127.0.0.1", 7687, self.create_thread_communicator)

        # Start all the defined threads.
        self.general.main_com.start()

        while not self.general.shut_down:

            # If the server has disconnected, close the executor.
            if not self.general.server_online:

                self.general.shut_down = True
                sys.exit()

            # At the end of the loop removes all the request thar are in that list.
            remove = []

            # Iterate over all the requests this executor has to execute.
            for e_request in self.general.requests_to_execute.values():

                # The request is now ready to be executed.
                if e_request.ready_to_execution:

                    # Create an executor fot this request.
                    self.general.current_requests[e_request] = RequestExecutor(e_request, general)

                    # Start the request execution.
                    self.general.current_requests[e_request].start()

                    e_request.ready_to_execution = False

                # The current request has finished what it has to do in this executor.
                elif e_request.status == "Finished":

                    remove.append(e_request)

            # Remove the requests that are in remove.
            for e_request in remove:

                self.general.current_requests.pop(e_request)
                self.general.requests_to_execute.pop(e_request.id)

        sys.exit()

    def create_thread_communicator(self, ip, port):
        """
            The function receives a port and ip and creates the thread communicator.
        """

        self.general.thread_com = ThreadCommunication(self.general, ip, port)

        self.general.thread_com.start()


#-----Functions-----#


def change_wd():
    """
        The function changes the system working directory to the script's directory.
    """

    abspath = os.path.abspath(__file__)
    dir_name = os.path.dirname(abspath)
    os.chdir(dir_name)


#-----Main Code-----#

general = GeneralVariables()

change_wd()

main = Main(general)

# Start the main code of the client.
main.start()