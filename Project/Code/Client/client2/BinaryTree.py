from math import floor
import wx
from Monitor import Monitor


class Pair():
    """
        This class represents a binary tree. This tree is meant to be as follow:
                        pair
                pair            pair
            pair    pair    pair    pair
                        etc.
          id  id  id   id  id  id  id  id

        The value of each pair is a splitter which its parent is the splitter of the parent pair.
    """

    def __init__(self, left=None, right=None, value=None):

        # The value of the current pair.
        self.value = value

        # The parent of the current pair.
        self.parent = None

        # The left element of the pair.
        self.left = left

        # The right element of the pair.
        self.right = right

    def create_tree(self, ids):
        """
            The Recursion converts the received ids list to a tree.
        """

        if len(ids) > 2:

            self.left = Pair()
            self.right = Pair()

            max_power = Pair.get_max_power(2, len(ids))

            ids_buffer = Pair.get_by_half(max_power, len(ids))

            if ids_buffer > len(ids) / 2.0:

                ids_buffer = len(ids) - ids_buffer

            if ids_buffer <= 1:
                self.left.create_tree([ids[0]])
            else:
                self.left.create_tree(ids[: ids_buffer])

            if len(ids) - ids_buffer <= 1:
                self.right.create_tree([ids[-1]])
            else:
                self.right.create_tree(ids[ids_buffer:])

        elif len(ids) == 2:

            self.left = Pair(value=ids[0])
            self.right = Pair(value=ids[1])

        elif len(ids) == 1:

            self.left = Pair(value=ids[0])
            self.right = None

    def vlr(self, monitors_dict=None, recorder=None):
        """
            A recursion on the current tree of the form: value, left, right. This recursion creates the splitters and
            the monitors in the tree.
        """

        # It's not a monitor, it's a splitter.
        if not self.value:

            # In case it's the root of the tree set the parent panel of the splitter to the parent of the root. It
            # doesn't have value attribute like a pair instance.
            if not isinstance(self.parent, Pair):

                # True if there is only one monitor in the whole tree.
                if not self.right:

                    # Extract the id of the monitor in the left element of the pair.
                    monitor_id = self.left.value

                    # Convert this pair to a monitor.
                    self.value = Monitor(self.parent, monitor_id)

                    # Both its elements should be None.
                    self.left = None

                    # Update the monitor as described in the function.
                    self.value.update_monitor(recorder, monitors_dict)

                else:

                    # Create the splitter.
                    self.value = wx.SplitterWindow(self.parent, style=wx.SP_LIVE_UPDATE)

                    # Set the minimum size of the splitter's panels so the wouldn't be too small.
                    self.value.SetMinimumPaneSize(50)

            # It's not the first pair in the tree.
            else:

                # This pair instance has only one monitor. Therefore it shouldn't be a splitter. Convert this pair to
                # its left pair object.
                if not self.right:

                    # Convert this pair to a monitor.
                    self.value = Monitor(self.parent.value, self.left.value)

                    # Both its elements should be None.
                    self.left = None

                    # Update the monitor as described in the function.
                    self.value.update_monitor(recorder, monitors_dict)

                # It's a regular splitter.
                else:

                    # Create the splitter.
                    self.value = wx.SplitterWindow(self.parent.value, style=wx.SP_LIVE_UPDATE)

                    # Set the minimum size of the splitter's panels so the wouldn't be too small.
                    self.value.SetMinimumPaneSize(50)

                # Create a sizer.
                sizer = wx.BoxSizer(wx.VERTICAL)

                # Add the splitter / monitor to the sizer.
                sizer.Add(self.value, 1, wx.EXPAND)

                # Set the sizer as the parent's sizer.
                self.parent.value.SetSizer(sizer)

            # Keep iterating on the left pair of the current pair.
            if self.left:

                self.left.parent = self
                self.left.vlr(monitors_dict, recorder)

            # Keep iterating on the right pair of the current pair.
            if self.right:

                self.right.parent = self
                self.right.vlr(monitors_dict, recorder)

        # It's a monitor (of a splitter), the lowest pair in the tree.
        else:

            # Create the monitor.
            self.value = Monitor(self.parent.value, self.value)

            # Create a sizer.
            sizer = wx.BoxSizer(wx.VERTICAL)

            # Add the monitor to the sizer.
            sizer.Add(self.value, 1, wx.EXPAND)

            # Set the sizer as the parent's sizer.
            self.parent.value.SetSizer(sizer)

            # Update the monitor as described in the function.
            self.value.update_monitor(recorder, monitors_dict)

    def lrv(self, flag):
        """
            A recursion on the current tree of the form: left, right, value. This recursion split the splitters. The
            flag parameter is for determining weather there is a need for a horizontal split or a vertical one.
        """

        if self.left:

            self.left.lrv(not flag)

        if self.right:

            self.right.lrv(not flag)

        # Split only if there are two elements for the current pair instance.
        if self.left and self.right:

            if flag:

                self.value.SplitHorizontally(self.left.value, self.right.value)

            else:

                self.value.SplitVertically(self.left.value, self.right.value)

    @staticmethod
    def get_max_power(base, number):
        """
            This function receives a base of a power and a number. The function the calculates what is the highest power
            that its result is less than the received number. This function doesn't handle usage of number < 1, i.e.
            the smallest base that can be returned is 0.
        """

        if (number**0.5 - floor(number**0.5)) == 0 or number == 2:
            return number

        current_power = 1

        while True:

            if base**current_power > number:

                return base**(current_power - 1)

            else:

                current_power += 1

    @staticmethod
    def get_by_half(max_power, number):
        """
            The function receives a power and its max power by base 2. Returns the right ids_buffer value.
        """

        if max_power*1.5 > number:

            return max_power / 2

        return max_power