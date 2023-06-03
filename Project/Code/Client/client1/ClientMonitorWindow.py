import wx
from wx.lib.pubsub import pub
from Colours import Colours
from BinaryTree import Pair


class ClientMonitorWindow(wx.Panel):
    """
        The monitor window of the client gui.
    """

    def __init__(self, parent):

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.SetBackgroundColour(Colours.main_window)

        self.gui = parent.gui

        # The widget that's responsible on showing the multiple monitors together.
        self.splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)
        self.splitter.SetMinimumPaneSize(100)

        # The panel that shows on startup when the server haven't sent data from an executor yet.
        self.start_up_panel = wx.Panel(self)

        # The panel which responsible on the the monitors.
        self.monitors_panel = wx.Panel(self)

        # Hide the secondary panels on startup.
        self.monitors_panel.Hide()

        # Create the main panel sizer.
        self.main_panel_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_panel_sizer.Add(self.monitors_panel, 1, wx.EXPAND)
        self.main_panel_sizer.Add(self.start_up_panel, 1, wx.EXPAND)

        self.monitors_panel_sizer = wx.BoxSizer(wx.VERTICAL)

        # Set the main panel sizer to the sizer of the monitor window panel.
        self.SetSizer(self.main_panel_sizer)

        self.monitors_panel.SetSizer(self.monitors_panel_sizer)

        # The number of executors that are currently sends data about the running file.
        self.executors_count = 0

        # A dict of all the executors that have a monitor and their monitor. {executor id: monitor}
        self.executors_monitors = {}

        # Records the data of the current monitors.
        self.recorder = {}

        # The title that will be shown to the user at startup.
        self.startup_title = None

        # A list that will contain all the ids of the executors monitors as pairs, sorted.
        self.pairs = []

        # A binary tree that contains all the monitors.
        self.monitors_tree = None

        pub.subscribe(self.refresh_monitors, "REFRESH_MONITORS")

        # Initialize the start up screen.
        self.start_up()

    def check_new_executor(self, executor_id):
        """
            The function checks if that executor already has a monitor, if he doesn't creates him one.
        """

        # Check if it's a new executor so he doesn't have a monitor.
        if not executor_id in self.executors_monitors:

            # Increase the counter.
            self.executors_count += 1

            wx.CallAfter(pub.sendMessage, "REFRESH_MONITORS", executor_id=executor_id)

    def refresh_monitors(self, executor_id):
        """
            The function is being called when a changes has been made and the monitors structure should get changed.
        """

        # There are no executors.
        if not executor_id:

            # Clear the monitors panels.
            self.clear_monitors_panels()

            # Show the startup panel.
            self.monitors_panel.Hide()
            self.start_up_panel.Show()

        else:

            self.update_recorder()

            # Clear the monitors panels.
            self.clear_monitors_panels()

            # Make the window showing the multiple monitors panel.
            self.start_up_panel.Hide()
            self.monitors_panel.Show()

            # Create the monitor.
            self.executors_monitors[executor_id] = None

            #-- Modify the monitors window --#

            # Create a list of all the ids of the executors monitors as pairs, sorted.
            self.pairs = self.executors_monitors.keys()
            self.pairs.sort()

            # Create a tree out of the ids as described in the Pair class.
            self.monitors_tree = Pair()
            self.monitors_tree.create_tree(self.pairs)

            # Set the parent of the main splitter / monitor as the monitors panel.
            self.monitors_tree.parent = self.monitors_panel

            # Create the monitors and the splitters.
            self.monitors_tree.vlr(self.executors_monitors, self.recorder)

            # Split the splitters.
            self.monitors_tree.lrv(True)

            # Add to the main sizer of the monitors panel the monitors tree.
            self.monitors_panel_sizer.Add(self.monitors_tree.value, 1, wx.EXPAND)

            # Call the Layout method to construct the monitors tree on the monitors panel graphically.
            self.Layout()

    def start_up(self):
        """
            The function is responsible on anything relates to the startup page.
        """

        # Create a title that will notify the user that he has to execute a request in order to see monitors.
        self.startup_title = wx.StaticText(self.start_up_panel, -1, 'You have to start a request in order to use the'
                                                                    ' monitors.')
        self.startup_title.SetFont(wx.Font(30, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        self.startup_title.SetForegroundColour(Colours.main_title)

    def new_output(self, new_output, executor_id, replace=False):
        """
            The function updates the received output in the textbox.
        """

        # First, check if this executor has a monitor. If he doesn't, create him one.
        self.check_new_executor(executor_id)

        # Wait until the executor gets a monitor.
        while (not executor_id in self.executors_monitors) or (executor_id in self.executors_monitors
                                                               and not self.executors_monitors[executor_id]):
            pass

        if replace:

            # Replace the received output with the output box of the current executor monitor.
            self.executors_monitors[executor_id].output_box.new_value(new_output)

        else:
            # Append the received new output to the output box of the current executor monitor.
            self.executors_monitors[executor_id].output_box.append_value(new_output)

    def reset(self):
        """
            The function resets the monitor window to startup.
        """

        self.executors_count = 0

        self.executors_monitors = {}

        self.recorder = {}

        wx.CallAfter(pub.sendMessage, "REFRESH_MONITORS", executor_id=None)

    def clear_monitors_panels(self):
        """
            The function clears all the monitors panels.
        """

        self.monitors_panel_sizer.DeleteWindows()
        self.monitors_panel_sizer = wx.BoxSizer(wx.VERTICAL)
        self.monitors_panel.SetSizer(self.monitors_panel_sizer)

    def update_recorder(self):
        """
            Records all the data of the monitors.
        """

        for executor_id in self.executors_monitors:
            if self.executors_monitors[executor_id]:
                self.recorder[executor_id] = {"output": self.executors_monitors[executor_id].output_box.content}
            else:
                self.recorder[executor_id] = {"output": ""}

    def update_status(self, executor_id, new_status):

        if executor_id in self.executors_monitors:

            self.executors_monitors[executor_id].properties.update_status(new_status)

    def init_monitors_request(self, ids):
        """
            The function builds the panel with the received ids list.
        """

        self.executors_count = len(ids)

        # Insert all the monitors
        for current_id in ids:

            self.executors_monitors[current_id] = None

        # Create the monitors panel.
        wx.CallAfter(pub.sendMessage, "REFRESH_MONITORS", executor_id=ids[0])