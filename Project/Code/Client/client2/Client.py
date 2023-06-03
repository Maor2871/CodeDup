import sys
from time import sleep
import wx
from MyThread import MyThread
from FileInit import FileInit
from ClientMainCommunicator import MainCommunication
from ClientThreadCommunicator import ThreadCommunication
from GUI import Frame
from RequestValidation import RequestValidation


#-----Classes-----#


class GeneralVariables():
    """
        The attributes of this class don't have any other class to relate but they are necessary for this client.
    """

    def __init__(self):

        # The communication instance that has the ability to communicate with the main server.
        self.main_com = None

        # The communication instance that has the ability to communicate with the thread communicator of this client in
        # the server.
        self.thread_com = None

        # The app of the GUI.
        self.app = None

        # The main frame of the GUI.
        self.window = None

        # The current request.
        self.current_request = None

        # If True the user wants to send the current request.
        self.send_request = False

        # True if the server isn't disconnected.
        self.server_online = True

        # True if the gui has closed.
        self.gui_closed = False

        # All the threads of the client are active as long as this flag is not True.
        self.shutdown = False


class Main(MyThread):
    """
        This class contains all the main operations of this client.
    """

    def __init__(self, general_):

        MyThread.__init__(self, -1, "main")

        self.general = general_

        # This instance is a thread which checks weather the current value of all the titles in the GUI request is
        # valid. If a value is not valid, erases it and notify the user the reason.
        self.request_validation = None

    def manager(self):
        """
            The function runs the main code of the client as a thread.
        """

        # Setup all the files that are necessary for this client.
        FileInit.client_init_files()

        # Set up the thread which checks the validation of the current request in the gui.
        self.request_validation = RequestValidation(self.general.window)

        # Setup the communication of this client with the Main server of the system.
        self.general.main_com = MainCommunication(self.general, "127.0.0.1", 7687, self.create_thread_communicator)

        # Start all the defined threads.
        self.general.main_com.start()
        self.request_validation.start()

        while not self.general.shutdown:

            # If the server has disconnected, wait 5 seconds so the user will be able to see the notification and
            # close the client.
            if not self.general.server_online:

                sleep(5)
                # Check if the GUI have closed.
                if not self.general.gui_closed:
                    self.general.window.on_quit(wx.EVT_CLOSE)

                sys.exit()

            # If the user wants to start the current request and it's valid.
            if self.general.send_request:

                # Send the request to the server.
                self.general.thread_com.send.send_request()

        # This client program has to be shut down for some reason, close it.
        # Check if the GUI have closed.
        if not self.general.gui_closed:
            self.general.window.on_quit(wx.EVT_CLOSE)

        sys.exit()

    def create_thread_communicator(self, ip, port):
        """
            The function receives a port and ip and creates the thread communicator.
        """

        self.general.thread_com = ThreadCommunication(self.general, ip, port)

        self.general.thread_com.start()


#-----Main Code-----#


general = GeneralVariables()

main = Main(general)

# Start the GUI of the client.
general.app = wx.App()

# Create the main frame of the GUI.
general.window = Frame(None, -1, "CodeDup", general)

# Start the main code of the client.
main.start()

# Start the GUI main loop.
general.app.MainLoop()