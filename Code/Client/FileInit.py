import os


class FileInit():
    """
        The class initializes the files the system is going to use on this client.
    """

    @staticmethod
    def client_init_files():
        """
            The function initializes the file system of a client.
        """

        open("current_request.txt", "w")

    @staticmethod
    def executor_init_files():
        """
            The function initializes the file system of an executor.
        """

        FileInit.make_dir("Requests_To_Execute/")

    @staticmethod
    def make_dir(directory):
        """
            The function receives a directory and tries to create it.
        """

        try:
            os.makedirs(directory)
        except:
            pass