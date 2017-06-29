import wx
from Colours import Colours


class Monitor(wx.Panel):
    """
        The instances of this class are monitors that show the data received from the executors.
    """

    def __init__(self, parent, executor_id):

        wx.Panel.__init__(self, parent=parent, id=executor_id)

        # Set the colour of the monitor.
        self.SetBackgroundColour(Colours.monitor)

        # The id of the monitor.
        self.id = executor_id

        self.sizer = wx.GridBagSizer(0, 0)

        self.properties = Properties(self, self.id)

        # The output box of the monitor.
        self.output_box = OutputBox(self)

        # Add all the items to the sizer.
        self.sizer.Add(self.properties, pos=(0, 0), flag=wx.ALL, border=5)
        self.sizer.Add(self.output_box, pos=(1, 0), flag=wx.ALL | wx.EXPAND, border=5)

        self.sizer.AddGrowableRow(1)
        self.sizer.AddGrowableCol(0)

        self.SetSizer(self.sizer)

    def update_monitor(self, recorder=None, monitors_dict=None):
        """
            The function checks if the monitor have records, if he does updates it. Modifies the monitors dict with the
            new window.
        """

        # Check if there is data this monitor have already received.
        if recorder and self.id in recorder:

            # Update this data to the new monitor.
            self.output_box.new_value(recorder[self.id]["output"])

        # Make sure a monitor dict has supplied.
        if monitors_dict:

            # Add the new monitor to the monitors dict.
            monitors_dict[self.id] = self


class Properties(wx.Panel):
    """
        The class represents a properties toolbar.
    """

    def __init__(self, parent, executor_id):

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        # The main sizer of the panel.
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # The title of the executor id.
        self.id_title = wx.StaticText(self, -1, 'Executor id: ' + str(executor_id))
        self.id_title.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        self.id_title.SetForegroundColour(Colours.main_title)

        self.current_status = "Waiting              "

        # The status title.
        self.status = wx.StaticText(self, -1, 'Status: ' + self.current_status)
        self.status.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        self.status.SetForegroundColour(Colours.main_title)

        # Add all the widgets to the main sizer.
        self.main_sizer.Add(self.id_title)
        self.main_sizer.Add(self.status, flag=wx.LEFT, border=10)

        # Set the main sizer to the sizer of the current panel.
        self.SetSizer(self.main_sizer)

    def update_status(self, new_status):
        """
            The function receives new status message and set it as the current status of the executor.
        """

        # Update the current status and the text in the monitor.
        self.current_status = new_status
        self.status.SetLabelText("Status: " + new_status)


class OutputBox(wx.TextCtrl):
    """
        The class represents the output box of the monitor.
    """

    def __init__(self, parent):

        wx.TextCtrl.__init__(self, parent=parent, id=-1, style=wx.TE_MULTILINE)

        self.SetBackgroundColour(Colours.text_ctrl)

        # The content of the box.
        self.content = ""

    def append_value(self, value):
        """
            The function appends the received string and appends it to the box content and the box itself.
        """

        self.content += value

        self.AppendText(value)

    def new_value(self, value):
        """
            The function replaces the current content of the box with the received value and updates the box.
        """

        self.content = value

        self.SetValue(self.content)