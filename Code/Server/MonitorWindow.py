import wx
from Colours import Colours


class MonitorWindow(wx.Panel):
    """
        The preferences window of the client gui.
    """

    def __init__(self, parent, gui):

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.SetBackgroundColour(Colours.main_window)

        self.gui = gui