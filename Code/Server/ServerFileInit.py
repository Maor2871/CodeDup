import os


class FileInit():
    """
        The class is responsible on setting up the files tree of the system on the server.
    """

    @staticmethod
    def init_files():
        """
            The function created the startup files and folders.
        """

        if not os.path.exists("./Requests"):

            os.mkdir("Requests")