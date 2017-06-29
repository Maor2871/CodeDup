import wx
from DialogBox import DialogBox
from NoteBook import NoteBook


class Frame(wx.Frame):
    """
        This class represents the main window of the application of the manager.
    """

    def __init__(self, parent, id_, title, general_):

        super(Frame, self).__init__(parent=parent, id=id_, title=title, pos=(0, 0))

        self.Maximize()

        # With this parameter the GUI can communicate with the server.
        self.general = general_

        # The main panel of the frame.
        self.sizer = wx.GridBagSizer(0, 0)

        # Set the size of each cell in the sizer.
        self.sizer.SetEmptyCellSize((10, 10))

        # The Main menu bar, where the file, windows etc. menus are located.
        self.menu_bar = None

        # The file menu, located inside the menu bar.
        self.file_menu = None

        # The windows menu, located inside the menu bar.
        self.windows_menu = None

        # The quit label inside the file menu.
        self.quit_label = None

        # Set up the panel of the first tab: Control panel window.
        self.cp_window = None

        # Set up the panel of the second tab: Monitor window.
        self.monitor_window = None

        # The main main windows and notebook panel.
        self.notebook_panel = None

        # The notebook of the main windows.
        self.notebook = None

        # The dialog box of the system.
        self.dialog_box = None

        # True if the gui has closed.
        self.quit = False

        self.Bind(wx.EVT_CLOSE, self.on_quit)

        # Build the user interface.
        self.init_ui()

        self.Layout()

        self.Show()

    def init_ui(self):
        """
            The function sets the user interface.
        """

        self.create_menu_bar()

        self.create_dialog_box()

        self.create_main_windows_notebook()

        self.SetSizer(self.sizer)

    def create_menu_bar(self):
        """
            The function creates the menu bar.
        """

        # Create the menu bar.
        self.menu_bar = wx.MenuBar()

        # Create the file menu and insert it into the menu bar.
        self.create_file_menu()

        # Create the windows menu and insert it into the menu bar.
        self.create_windows_menu()

        # Set up the menu bar.
        self.SetMenuBar(self.menu_bar)

    def create_main_windows_notebook(self):
        """
            The function creates the main windows tabs and the main windows themselves..
        """

        # Create the notebook and main windows panel.
        self.notebook_panel = wx.Panel(self)

        # Set up the notebook of the main windows.
        self.notebook = NoteBook(self.notebook_panel, self)

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        sizer.Add(self.notebook, 1, wx.EXPAND)

        self.notebook_panel.SetSizer(sizer)

        self.sizer.Add(self.notebook_panel, pos=(0, 0), span=(97, 193), flag=wx.EXPAND)

    def create_dialog_box(self):
        """
            The function creates a dialog box at the bottom of the application.
        """

        self.dialog_box = DialogBox(self)
        self.sizer.Add(self.dialog_box, pos=(97, 0), span=(1, 193), flag=wx.EXPAND)
        self.dialog_box.update_text("Hello, I'm here to notify you about the current status of the system.")

    def create_file_menu(self):
        """
            The function creates the file menu and inserts it into the menu bar.
        """

        # Create the file menu.
        self.file_menu = wx.Menu()

        # Create the quit label to the file menu.
        self.quit_label = self.file_menu.Append(wx.ID_EXIT, 'Quit', 'Quit application')

        # Insert the file menu to the menu bar.
        self.menu_bar.Append(self.file_menu, '&file')

        # When the quit label is being pressed, call on_quit.
        self.Bind(wx.EVT_MENU, self.on_quit, self.quit_label)

    def create_windows_menu(self):
        """
            The function creates the windows menu and inserts it into the menu bar.
        """

        # Create the windows menu.
        self.windows_menu = wx.Menu()

        # Insert the Control panel floating window.
        self.windows_menu.Append(wx.ID_ANY, "&Control panel")

        # Insert the Monitor floating window.
        self.windows_menu.Append(wx.ID_ANY, "&Monitor")

        self.menu_bar.Append(self.windows_menu, "&Windows")

        self.Layout()

        self.Show()

    def on_quit(self, e):
        """
            Close the application.
        """

        self.quit = True
        self.general.shut_down = True
        self.general.gui_closed = True
        self.Destroy()