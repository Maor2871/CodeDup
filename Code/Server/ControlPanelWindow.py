import wx
from Colours import Colours
from wx.lib.pubsub import pub
import wx.lib.mixins.listctrl as listmix


class ControlPanelWindow(wx.Panel):
    """
        The preferences window of the client gui.
    """

    def __init__(self, parent, gui):

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.SetBackgroundColour(Colours.main_window)

        self.general = gui.general

        self.gui = gui

        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Create the connected panel and save it in the main server too.
        self.connected_panel = Connected(self)
        self.gui.general.connected_panel = self.connected_panel

        self.records = Records(self, self.general, self.gui.general.data_base, "")

        # self.main_sizer.Add(self.connected_panel)
        self.main_sizer.Add(self.records, flag=wx.LEFT, border=150)

        self.main_sizer.Add(self.connected_panel)

        self.SetSizer(self.main_sizer)

        self.Layout()

        pub.subscribe(self.update_records, "UPDATE_RECORDS")

    def pub_update_records(self, db_content):
        """
            The function calls the real update records function but with pub sub so it will be able to make changes to
            the panel.
        """

        wx.CallAfter(pub.sendMessage, "UPDATE_RECORDS", db_content=db_content)

    def update_records(self, db_content=""):
        """
            The function updates the records.
        """

        self.records.Destroy()
        self.records = Records(self, self.general, self.gui.general.data_base, db_content)

        # self.main_sizer.Add(self.connected_panel)
        self.main_sizer.Add(self.records, flag=wx.LEFT, border=150)

        self.Layout()


class Records(wx.Panel):
    """
        The class represents a panel that displays records from the data base.
    """

    def __init__(self, parent, general, db, db_content):

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.general = general

        # The main sizer of the panel.
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        # The data base that the panel uses to display the records.
        self.db = db

        # The content of the data base as a string.
        self.db_content = db_content

        # A list of the tables instances of the panel.
        self.tables = []

        # A dict of the form: {table name: content in db_content}
        self.tables_dict = {}

        # The title of the panel.
        self.main_title = wx.StaticText(self, -1, "Records:")
        font = wx.Font(25, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        font.SetUnderlined(True)
        self.main_title.SetFont(font)
        self.main_title.SetForegroundColour(Colours.main_title)

        if db_content:

            # Build the panel.
            self.build_records()

    def build_records(self):
        """
            The function creates tables panels from the tables in the database and adds them to the panel.
        """

        # Add the main title to the sizer.
        self.main_sizer.Add(self.main_title, flag=wx.ALL, border=10)

        self.tables_dict = {content.split("\n")[0]: content[content.index("\n") + 1:] for content in
                            self.db_content.split("\n**********\n")}

        # Iterate over all the tables in the data base of the server.
        for table in self.db.tables:

            # Create a Table instance for the current table.
            self.tables.append(Table(self, self.general, self.tables_dict[table], table))
            sizer = wx.BoxSizer()
            # Add the Table instance to the sizer.
            sizer.Add(self.tables[-1], flag=wx.ALL, border=13)
            self.main_sizer.Add(sizer, flag=wx.UP, border=10)

        # Set the main sizer to the sizer of the panel.
        self.SetSizer(self.main_sizer)


class Table(wx.Panel):

    def __init__(self, parent, general, content, table_name):

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.general = general

        # The main sizer of the panel.
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.table_toolbar_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # The table widget.
        self.table = wx.ListCtrl(self, size=(350, 220), style=wx.LC_REPORT | wx.BORDER_SUNKEN)

        # The tool bar of the table. It allows the manager to handle the values in the data base.
        self.toolbar = wx.ToolBar(self, -1, style=wx.TB_VERTICAL)
        self.toolbar.SetBackgroundColour(Colours.main_window)

        # Add the buttons to the toolbar.
        self.trash_button = self.toolbar.AddTool(-1, wx.Bitmap("Resources/trash.png"))
        self.remove_button = self.toolbar.AddTool(-1, wx.Bitmap("Resources/remove.png"))

        # Set up the buttons in the toolbar.
        self.toolbar.Realize()

        # Bind the buttons and their functions.
        self.toolbar.Bind(wx.EVT_TOOL, self.delete_table, self.trash_button)
        self.toolbar.Bind(wx.EVT_TOOL, self.remove_from_table, self.remove_button)

        # The content of the table as a string.
        self.content = content

        # Extract the columns of the table from its content.
        self.columns = (self.content.split("\n")[0]).split(", ")

        # Extract the rows of the table from its content.
        self.rows = self.content.split("\n")[1:]

        # The name of the table.
        self.table_name = table_name

        # The title of the name of the table.
        self.name_title = wx.StaticText(self, -1, self.table_name)
        self.name_title.SetFont(wx.Font(15, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        self.name_title.SetForegroundColour(Colours.main_title)

        # Add the table and the toolbar to their sizer.
        self.table_toolbar_sizer.Add(self.table)
        self.table_toolbar_sizer.Add(self.toolbar)

        # Add the widgets and the sub-sizers to the main sizer.
        self.main_sizer.Add(self.name_title)
        self.main_sizer.Add(self.table_toolbar_sizer)

        self.build_table()

    def build_table(self):
        """
            The function builds the table according to its content.
        """

        # Iterate over the columns of the table and add them to the table widget.
        for i in range(len(self.columns)):

            self.table.InsertColumn(i, self.columns[i])

        # Iterate over the rows of the table and add them to the table widget.
        for i in range(len(self.rows)):

            # Split the row to its columns.
            row = self.rows[i].split(", ")

            if len(row) >= 1:

                self.table.InsertStringItem(i, str(row[0]))
                self.table.SetColumnWidth(0, wx.LIST_AUTOSIZE)

            for j in range(1, len(row)):

                self.table.SetStringItem(i, j, str(row[j]))
                self.table.SetColumnWidth(j, wx.LIST_AUTOSIZE)

        self.SetSizer(self.main_sizer)

    def delete_table(self, e):
        """
            The function deletes the current table from the data base.
        """

        self.general.delete_table = self.table_name

    def remove_from_table(self, e):
        """
            The function removes the selected rows from the data base.
        """

        selected_items = self.get_selected_items()

        # A list of all the ids of the entities in the selected rows.
        ids = []

        for row_number in selected_items:

            ids.append(int(self.table.GetItem(row_number, 0).GetText()))

        self.general.remove_from_table[self.table_name] = ids

    def get_selected_items(self):
        """
            The function returns the selected items of the table.
        """

        selection = []

        # start at -1 to get the first selected item.
        current = -1

        while True:

            next_item = self.table.GetNextItem(current, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)

            # There is no more selected items, so next_item contains -1.
            if next_item == -1:

                return selection

            # Append the current selected item to the list of the selected items.
            selection.append(next_item)
            current = next_item


class Connected(wx.Panel):
    """
        The class represents a panel which displays in real time the current amount of entities that are connected to
        the system.
    """

    def __init__(self, parent):

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        # Set the colour of the background of the panel.
        self.SetBackgroundColour(Colours.main_window)

        # The main sizer of the panel.
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        # A sizer for the counters.
        self.counters_sizer = wx.BoxSizer(wx.VERTICAL)

        # The main title of the panel.
        self.main_title = wx.StaticText(self, -1, "Currently in the system:")
        font = wx.Font(25, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        font.SetUnderlined(True)
        self.main_title.SetFont(font)
        self.main_title.SetForegroundColour(Colours.main_title)

        # Create the counters.
        self.clients_counter = Counter(self, "Clients")
        self.executors_counter = Counter(self, "Executors")
        self.requests_counter = Counter(self, "Requests")

        # Add them to their sizer.
        self.counters_sizer.Add(self.clients_counter, flag=wx.UP, border=30)
        self.counters_sizer.Add(self.executors_counter, flag=wx.UP, border=30)
        self.counters_sizer.Add(self.requests_counter, flag=wx.UP, border=30)

        # Add the widgets to the main sizer.
        self.main_sizer.Add(self.main_title, flag=wx.ALL, border=10)
        self.main_sizer.Add(self.counters_sizer, flag=wx.ALL, border=10)

        self.SetSizer(self.main_sizer)


class Counter(wx.Panel):
    """
        This class represents a counter panel.
                    What is counted
            current                 max
            box                     box(editable-optional)
    """

    def __init__(self, parent, title, count_value=0, max_value=200, max_edit=True):

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY, style=wx.SUNKEN_BORDER)

        # Set the colour of the background of the panel.
        self.SetBackgroundColour(Colours.main_window)

        self.count = count_value

        self.max = max_value

        # The main sizer of the panel.
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # The menu sizer of the panel.
        self.menu_sizer = wx.BoxSizer(wx.VERTICAL)

        # The sizer that combines the counter and the max sizers together.
        self.counter_max_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # A sizer for the boxes.
        self.counter_sizer = wx.BoxSizer(wx.VERTICAL)

        # A sizer for the boxes titles.
        self.max_sizer = wx.BoxSizer(wx.VERTICAL)

        # Set the title of what is being counted.
        self.title = wx.StaticText(self, -1, title)
        self.title.SetFont(wx.Font(25, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        self.title.SetForegroundColour(Colours.second_title)

        # Set the title of the current box.
        self.counter_title = wx.StaticText(self, -1, "current")
        self.counter_title.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        self.counter_title.SetForegroundColour(Colours.second_title)

        # Set the title of the max box.
        self.max_title = wx.StaticText(self, -1, "max")
        self.max_title.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        self.max_title.SetForegroundColour(Colours.second_title)

        # Create the box of the counter.
        self.count_box = wx.TextCtrl(self, -1, value=str(self.count), size=(75, -1))
        self.count_box.SetEditable(False)

        # Check if the max box id editable and create it.
        if max_edit:
            self.max_box = wx.SpinCtrl(self, value=str(self.max), size=(75, -1), min=0, max=1000)
            self.max_box.Bind(wx.EVT_SPINCTRL, self.max_value_changed)
            self.max_box.Bind(wx.EVT_TEXT, self.max_value_changed)
        else:
            self.max_box = wx.TextCtrl(self, -1, size=(75, -1), style=wx.TE_READONLY)

        # Create the CPU widget for the counter.
        self.cpu = CPU(self)

        # Add the boxes titles to their sizer.
        self.counter_sizer.Add(self.counter_title)
        self.counter_sizer.Add(self.count_box)

        # Add the boxes to their sizer.
        self.max_sizer.Add(self.max_title)
        self.max_sizer.Add(self.max_box)

        # Combine the two sizers together.
        self.counter_max_sizer.Add(self.counter_sizer, flag=wx.RIGHT, border=10)
        self.counter_max_sizer.Add(self.max_sizer, flag=wx.RIGHT, border=10)

        # Add the widgets to the main sizer.
        self.menu_sizer.Add(self.title, flag=wx.BOTTOM, border=25)
        self.menu_sizer.Add(self.counter_max_sizer)

        self.main_sizer.Add(self.menu_sizer, flag=wx.ALIGN_BOTTOM | wx.BOTTOM | wx.LEFT, border=5)
        self.main_sizer.Add(self.cpu, flag=wx.ALIGN_BOTTOM)

        self.SetSizer(self.main_sizer)

        self.Layout()

    def inc(self):
        """
            The function increase the counter by 1.
        """

        self.count += 1

        # Update the new counter amount in the GUI.
        self.count_box.SetValue(str(self.count))

        self.cpu.set_value(round((self.count/(self.max*1.0))*100))

    def dec(self):
        """
            The function decrease the counter by 1.
        """

        self.count -= 1

        # Update the new counter amount in the GUI.
        self.count_box.SetValue(str(self.count))

        self.cpu.set_value(round((self.count/(self.max*1.0))*100))

    def max_value_changed(self, e):
        """
            The function is being called when a new value has signed to the max box.
        """

        self.max = int(self.max_box.GetValue())

        self.cpu.set_value(round((self.count/(self.max*1.0))*100))


class CPU(wx.Panel):
    """
        This class represents a cpu widget.
    """

    def __init__(self, parent, value=0):

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY, size=(80, 97))

        # Set the background colour to black.
        self.SetBackgroundColour('#000000')

        # The value of the cpu.
        self.value = value

        # Call the function on_paint when there should be a changed in the widget.
        self.Bind(wx.EVT_PAINT, self.on_paint)

    def set_value(self, value):
        """
            The function receives a value of cpu and updates the widget.
        """

        # Update the value of the cpu to the received value.
        self.value = value

        # Call on_paint to change the value of the cpu widget.
        self.Refresh()

    def on_paint(self, event):

        dc = wx.PaintDC(self)

        dc.SetDeviceOrigin(0, 100)
        dc.SetAxisOrientation(True, True)

        # Where the rectangles should get painted.
        rect = self.value / 5

        # Draw the rectangles which build the widget.
        for i in range(1, 21):

            if i > rect:

                dc.SetBrush(wx.Brush('#075100'))
                dc.DrawRectangle(10, i*4, 30, 5)
                dc.DrawRectangle(41, i*4, 30, 5)

            else:

                dc.SetBrush(wx.Brush('#36ff27'))
                dc.DrawRectangle(10, i*4, 30, 5)
                dc.DrawRectangle(41, i*4, 30, 5)