from subprocess import Popen, PIPE, STDOUT
# import psutil
from time import sleep
import os
from MyThread import MyThread


class RequestExecutor(MyThread):
    """
        The class instances are responsible for anything relates to their requests execution.
    """

    def __init__(self, request, general_, update_time=5):

        MyThread.__init__(self, -1, "Request Executor")

        # The request this instance is currently handling.
        self.request = request

        # The connector to the main executor script.
        self.general = general_

        # The status of the current request.
        self.status = "Processing"

        # The process of the running file.
        self.process = None

        # How much time to wait between each monitoring.
        self.update_time = update_time

        # A thread that will monitor the running file (CPU, RAM etc.).
        self.file_monitor = None

        # The list will contain the output of the running file.
        self.stdout = []

        # The file the executor writes the running file output to.
        self.log_file = "log_file.txt"

        with open(self.request.dir + self.log_file, "w") as f:
            f.write("")

        # How much time to wait when the file to run has finished for the rest of the output.
        self.time_at_end = 1

    def manager(self):
        """
            The function that manages anything relates to the request execution.
        """

        # Keep the current working directory and restore it when finished.
        current_dir = os.getcwd()

        os.chdir(self.request.dir)

        # Make sure the status of the request is not finished.
        if not self.status == "Finished":

            # Prepare the code for running.
            self.process = Popen("python " + self.request.file_to_run, shell=True, stdout=PIPE, stderr=STDOUT)

            # Tell the server that the file is now running properly.
            self.general.thread_com.send.current_messages.append("Request::" + str(self.request.id) + "::Status::File "
                                                                                                      "is now running")

        # # Start the file monitor.
        # self.file_monitor = FilesMonitor(self.update_time, self.request.file_to_run, self.process, self)
        #
        # self.file_monitor.start()

        # The loop which runs the file to run.
        while not self.general.shut_down or not self.status == "Finished":

            # Receive the output of the file by lines.
            line = self.process.stdout.readline()

            # The code have finished running.
            if line == '' and self.process.poll() is not None:

                # Make sure that the process has finished writing everything to the log file.
                self.process.wait()

                # The rest of the output.
                output = self.process.stdout.read()

                # Write to the log file the rest of the content.
                with open(self.log_file, "a") as log_file:
                    log_file.write(output)

                # Send the server the whole output of the running file since the beginning.
                with open(self.log_file, "rb") as log_file:
                    output = log_file.read()
                    self.general.thread_com.send.current_messages.append("Request::" + str(self.request.id) +
                                                                         "::Last Output::" + output)

                break

            # Attach the new line to the output list ans send it to the server.
            # Do it only if it's not a blank line.
            if line and line != "\n":

                self.stdout.append(line)

                with open(self.log_file, "a") as log_file:

                    log_file.write(line)

                self.general.thread_com.send.current_messages.append("Request::" + str(self.request.id) +
                                                                     "::New Output::" + line)

        # The execution of the file has finished. Notify the server about it.
        self.general.thread_com.send.current_messages.append("Request::" + str(self.request.id) +
                                                             "::Status::Finished Execution")

        # Notify the executor of this current request executor that the request has finished executing.
        self.request.status = "Finished"

        os.chdir(current_dir)


class FilesMonitor(MyThread):
    """
        The class represents a thread that monitors the running files and sends the data to the server.
    """

    def __init__(self, update_time, file_name, files_process, request_executor):

        MyThread.__init__(self, -1, "FileMonitor")

        self.request_executor = request_executor

        # How much time to wait between each monitoring.
        self.update_time = update_time

        # The name of the running file.
        self.running_file = file_name

        # The Popen process of the running file.
        self.file_process = files_process

        # The psutil process of the running file.
        self.process_monitor = psutil.Process(self.file_process.pid)

        # The percentage of cpu the file consumes.
        self.cpu_percentage = 0

        # The amount of RAM the files consumes.
        self.ram = 0

    def manager(self):
        """
            The function that monitors the running files.
        """

        while not self.request_executor.general.shut_down:

            # Update the cpu percentage of the file since the last call to the function.
            self.cpu_percentage = self.process_monitor.cpu_percent(interval=0)

            # Send the new data that this thread gathered about the running file process.
            self.send_new_data()

            # Wait till the next check time arrives.
            sleep(self.update_time)

    def send_new_data(self):
        """
            The function sends the new data about the running file to the server.
        """

        self.request_executor.general.thread_com.send.current_messages.append("Request::New Data Package::" +
                                                                              self.data_to_string())

    def data_to_string(self):
        """
            The function returns a string contains all the data about the running process.
        """

        return "CPU::" + str(self.cpu_percentage)