import wx
from ControlPanelWindow import ControlPanelWindow as CPWindow
from MonitorWindow import MonitorWindow


class NoteBook(wx.Notebook):
    """
        The class represents a notebook: multiple tabs.
    """

    def __init__(self, parent, gui):

        wx.Notebook.__init__(self, parent, id=wx.ID_ANY, style=wx.BK_DEFAULT)

        self.gui = gui

        # Set up the panel of the first tab: Request window.
        self.tab_one = CPWindow(self, gui)
        self.gui.cp_window = self.tab_one
        self.AddPage(self.tab_one, "Control Panel")

        # # Set up the panel of the second tab: Monitor window.
        # self.tab_two = MonitorWindow(self, gui)
        # self.gui.monitor_window = self.tab_two
        # self.AddPage(self.tab_two, "Monitor")

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_page_changed)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.on_page_changing)

    @staticmethod
    def on_page_changed(e):
        """
            Gets here when the new tab is fully selected.
        """

        e.Skip()

    @staticmethod
    def on_page_changing(e):
        """
            Gets here when the new tab is currently been selected.
        """

        e.Skip()