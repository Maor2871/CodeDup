import wx
from ClientMonitorWindow import ClientMonitorWindow
from ClientPreferencesWindow import ClientPreferencesWindow
from RequestWindow import RequestWindow


class NoteBook(wx.Notebook):
    """
        The class represents a notebook: multiple tabs.
    """

    def __init__(self, parent, gui):

        wx.Notebook.__init__(self, parent, id=wx.ID_ANY, style=wx.BK_DEFAULT)

        self.gui = gui

        # Set up the panel of the first tab: Request window.
        self.tab_one = RequestWindow(self, gui)
        self.gui.request_window = self.tab_one
        self.AddPage(self.tab_one, "Request")

        # Set up the panel of the second tab: Monitor window.
        self.tab_two = ClientMonitorWindow(self)
        self.gui.monitor_window = self.tab_two
        self.AddPage(self.tab_two, "Monitor")

        # # Set up the panel of the third tab: Preferences window.
        # self.tab_three = ClientPreferencesWindow(self)
        # self.gui.preferences_window = self.tab_three
        # self.AddPage(self.tab_three, "Preferences")

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