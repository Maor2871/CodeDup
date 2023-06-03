import wx
from Colours import Colours


class ClientPreferencesWindow(wx.Panel):
    """
        The preferences window of the client gui.
    """

    def __init__(self, parent):

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.SetBackgroundColour(Colours.main_window)

        text_one = wx.TextCtrl(self, wx.ID_ANY, "")
        text_one.SetBackgroundColour(Colours.text_ctrl)

        text_two = wx.TextCtrl(self, wx.ID_ANY, "")
        text_two.SetBackgroundColour(Colours.text_ctrl)

        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(text_one, 0, wx.ALL, 5)

        sizer.Add(text_two, 0, wx.ALL, 5)

        self.SetSizer(sizer)