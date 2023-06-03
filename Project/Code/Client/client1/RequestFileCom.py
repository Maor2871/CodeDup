from threading import Lock
import os


class RequestFileCom():
    """
        This class allows supplies methods to handle the request file.
    """

    # Create a mutex so the instances will not open the file at the same time.
    mutex = Lock()

    @staticmethod
    def file_to_dict(path="current_request.txt"):
        """
            The function reads the file and return a dict as follow: {key, value}.
        """

        # Check if the received path exists.
        if not os.path.exists(path):

            return {}

        # Wait until the file will not be in use.
        RequestFileCom.mutex.acquire()

        with open(path, "r") as f:

            content = f.readlines()

            request_dict = {}

            for line in content:

                try:
                    key = line.split("::")[0]
                    value = line.split("::")[1]
                    if value.endswith("\n"):
                        value = value[:-1]
                    request_dict[key] = value
                except:
                    continue

            RequestFileCom.mutex.release()

            return request_dict

    @staticmethod
    def get_value(key):
        """
            The function returns the value of the current title in request file.
        """

        request_dict = RequestFileCom.file_to_dict()

        try:

            return request_dict[key]

        except:

            return None

    @staticmethod
    def enter_dict(update_dict, path="current_request.txt"):
        """
            The function updates the request file by the received dictionary.
        """

        request_dict = RequestFileCom.file_to_dict(path)

        # Make sure no one changes the file content before finishes to update it.
        RequestFileCom.mutex.acquire()

        for key in update_dict:

            request_dict[key] = update_dict[key]

        request_file_string = ""

        for key in request_dict:

            request_file_string += key + "::" + request_dict[key] + "\n"

        # Update the file.
        with open(path, "w") as f:

            f.write(request_file_string)

        RequestFileCom.mutex.release()

        request_dict = RequestFileCom.file_to_dict(path)