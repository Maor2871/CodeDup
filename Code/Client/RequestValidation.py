import os
from MyThread import MyThread
from RequestFileCom import RequestFileCom


class RequestValidation(MyThread):
    """
        The class checks the validation of the current request in the client's GUI. If it finds an invalid value, erases
        it from the GUI and alerts the Client.
    """

    # A class variable which indicates weather the current request is valid.
    is_valid = False

    # True if the files that must have value do have one.
    has_must_files = False

    def __init__(self, window):

        MyThread.__init__(self, -1, "Request Validation")

        self.general = window.general

        # The current limits of the server to a current available request. a dict: {title:limit}
        self.limits = {}

        # The current request in the GUI. a dict: {title:value}
        self.request_dict = None

        # The main frame of the GUI.
        self.window = window

        self.request_window = window.request_window

        # A dictionary with all the titles the user has to fill. If True the title is currently filled and is valid.
        self.titles_validation = {"Run File": False, "Additional Files": True}

        self.run_file_not_exist = ""

        # If there is a problem, keeps the current content of the dialog so it will be possible to restore it if the
        # problem will be solved.
        self.dialog_box_value = ""

    def manager(self):
        """
            The function makes the validation itself.
        """

        # Always check weather the current request in the client GUI doesn't cross the server limits.
        while not self.window.general.shutdown:

            self.request_dict = RequestFileCom.file_to_dict()

            # Check if those specific titles are in the request. A request isn't valid without them.
            if not "Run File" in self.request_dict:

                RequestValidation.is_valid = False
                RequestValidation.has_must_files = False

            else:

                # Iterate over all the titles in the request dict and check if they are valid.
                for title in self.request_dict:

                    # try:

                        if title in self.limits:

                            # The limit of the server to the current title.
                            limit = self.limits[title]

                            # Split the limit according the the protocol.
                            limit.split("::")

                        else:

                            limit = None

                        error_message, add = self.check_validation(limit, title)

                        self.not_valid_title(error_message, title, add)

                    # except Exception as e:
                    #     continue

                # Update the validation status of the current request.
                RequestValidation.is_valid = self.all_valid()

    def check_validation(self, limit, title):
        """
            The function receives a limit and a title. It checks weather the value of the title in the current request
            is valid according to the received limit and some other related parameters.
        """

        if title == "Run File":

            path = self.request_dict[title]

            if path.endswith("\n"):

                path = path[:-1]

            # The user didn't enter any path.
            if not path:

                # Check if there is a file that has removed because its path didn't exist and exist now.
                if self.run_file_not_exist and os.path.isfile(self.run_file_not_exist):

                    self.titles_validation["Run File"] = True
                    RequestValidation.has_must_files = True
                    self.request_window.new_run_file(self.run_file_not_exist)
                    self.run_file_not_exist = ""
                    if "The path of the file to run does not exist: " in self.window.dialog_box.GetValue():
                        self.window.dialog_box.update_text(self.dialog_box_value)

                else:

                    self.titles_validation["Run File"] = False
                    RequestValidation.has_must_files = False

                return "", ""

            # The path that the user has supplied no longer exists.
            if not os.path.isfile(path):

                self.titles_validation["Run File"] = False
                RequestValidation.has_must_files = False
                self.run_file_not_exist = path
                self.dialog_box_value = self.window.dialog_box.GetValue()
                return "The path of the file to run does not exist: " + path, path

            # In Case the file is currently opened by another program.
            try:

                # Check if the file contains unsupported symbols.
                with open(path, "r") as f:

                    content = f.read()

                    if "::" in content:

                        self.titles_validation["Run File"] = False
                        self.not_valid_title("The file: " + path + " contains one of the following unsupported symbols:"
                                                                   " '::'.", title, path)

                # The user has supplied a valid path.
                self.titles_validation["Run File"] = True
                return "", ""

            except Exception as e:

                self.titles_validation["Run File"] = False
                RequestValidation.has_must_files = False
                self.run_file_not_exist = path
                self.dialog_box_value = self.window.dialog_box.GetValue()
                return "The path of the file to run does not exist: " + path, path

        # NOTE: If an additional file is not valid, dealing with it locally.
        elif title == "Additional Files":

            # A list of the paths of all the Additional Files the user has supplied.
            paths = self.request_dict[title].split("@**")

            self.titles_validation["Additional Files"] = True

            # There are no Additional Files.
            if not paths:

                return "", ""

            for path in paths:

                if path.endswith("\n"):
                    path = path[:-1]

                # Check if the current path isn't empty.
                if path:

                    # The current path doesn't exist.
                    if not os.path.isfile(path):

                        self.titles_validation["Additional Files"] = False
                        self.not_valid_title("A path of an additional file does not exist: " + path, title, path)

                    else:

                        with open(path, "r") as f:

                            content = f.read()

                            if "::" in content or "@**" in content:

                                self.titles_validation["Additional Files"] = False
                                self.not_valid_title("The file: " + path + " contains one of the following unsupported "
                                                                           "symbols: '::'.", title, path)

            # All the paths are valid.
            return "", ""

        elif title == "Executors Amount":

            return "", ""

        return "An unsupported argument was supplied within the request: " + title, ""

    def all_valid(self):
        """
            The function returns True if the values of all the titles are Valid. Else returns False.
        """

        # Iterate over the validation values of all the titles.
        for value in self.titles_validation.items():

            # If one of them isn't valid then the whole request isn't valid, return False.
            if not value:

                return False

        # All the validation values are valid, return True.
        return True

    def not_valid_title(self, error_message, title, add):
        """
            The function receives an error message, title and an address. Calls the function with those parameters that
            will remove the current value from its title in the gui.
        """

        # If the value of the current title is not valid and it has error message, send him the error.
        if error_message:

            # Tell the user why the value isn't valid.
            self.window.dialog_box.update_text(error_message)

            # Erase the value.
            self.window.request_window.remove_value(title, add)