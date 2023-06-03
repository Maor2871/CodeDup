import threading
from abc import abstractmethod


class MyThread(threading.Thread):
    """
        This class creates threads.
    """

    def __init__(self, thread_id, name):
        """
            Constructor- assign each value to its corresponding attribute.
        """

        # Call the super constructor with self.
        threading.Thread.__init__(self)

        # The id of the thread.
        self.id = thread_id

        # The name of the thread.
        self.name = name

    def run(self):
        """
            The function runs amd manage the current thread and prints messages.
        """

        self.manager()

    @abstractmethod
    def manager(self):
        """
            The function is intended for overriding by extended classes.
        """