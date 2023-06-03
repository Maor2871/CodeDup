import wx
from Colours import Colours


class DialogBox(wx.TextCtrl):
    """
        This class represents the dialog box of the gui.
    """

    def __init__(self, parent):

        wx.TextCtrl.__init__(self, parent=parent, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.VSCROLL)

        self.SetBackgroundColour(Colours.dialog_box)

        sizer = wx.BoxSizer()

        sizer.Add(self, 1, wx.ALIGN_BOTTOM | wx.RIGHT | wx.LEFT)

        parent.SetSizer(sizer)

        self.font = wx.Font(20, wx.DEFAULT, wx.NORMAL, wx.BOLD)

        self.SetFont(self.font)

        self.SetForegroundColour(wx.RED)

    def update_text(self, message):

        self.SetValue(message)