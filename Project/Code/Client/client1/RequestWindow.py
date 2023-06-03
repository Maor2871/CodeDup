import wx
from Colours import Colours
from RequestFileCom import RequestFileCom
from RequestValidation import RequestValidation
from Request import Request


class RequestWindow(wx.Panel):
    """
        The request window of the client gui.
    """

    def __init__(self, parent, gui):

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        # Set the background colour of the request window.
        self.SetBackgroundColour(Colours.main_window)

        # Save the parent of the window.
        self.gui = gui

        # The font of the titles.
        self.main_titles_font = wx.Font(30, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.second_titles_font = wx.Font(15, wx.DEFAULT, wx.NORMAL, wx.BOLD)

        # The titles themselves.
        self.files_title = None
        self.commitments_and_privileges_title = None
        self.properties_title = None
        self.file_to_run_title = None
        self.current_file_to_run_title = None
        self.additional_files_title = None
        self.number_of_executors_title = None

        # The button that will create the toolbar.
        self.start_request_button = None

        # The BoxSizers.
        self.sizer = wx.GridBagSizer(0, 0)

        # Set the size of each cell in the sizers.
        self.sizer.SetEmptyCellSize((10, 10))

        # Where the user drops his file.
        self.run_file_editor = None
        # The instance which allows the dropping method.
        self.run_file_target = None
        # The list of the Additional Files.
        self.additional_files = None
        # The editor of the Additional Files.
        self.additional_files_editor = None
        # The instance which allows the dropping method.
        self.additional_files_target = None
        # The current additional file being selected.
        self.selected_additional_file = None
        # The box of the number of executors.
        self.number_of_executors_box = None

        # The file that the user wishes to run.
        self.file_to_run = None

        # Build the request window.
        self.build_request()

    def build_request(self):
        """
            The function builds the request window.
        """

        self.create_tool_bar()

        self.create_files_part()

        self.create_commitments_and_privileges_part()

        # self.create_properties_part()

        self.SetSizer(self.sizer)

    def create_tool_bar(self):
        """
            The function creates the toolbar of the request window.
        """

        # Add the buttons of the toolbar.
        bmp = wx.Bitmap("Resources/send_request.jpg", wx.BITMAP_TYPE_ANY)
        self.start_request_button = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=bmp)

        # Bins the buttons with their functions.
        self.start_request_button.Bind(wx.EVT_BUTTON, self.start_request)

        # Add the toolbar to the sizer.
        self.sizer.Add(self.start_request_button, pos=(0, 0), flag=wx.BOTTOM, border=15)

    def create_files_part(self):
        """
            The function builds the file part.
        """

        # Create main title
        self.files_title = wx.StaticText(self, -1, 'Files')
        self.files_title.SetFont(self.main_titles_font)
        self.files_title.SetForegroundColour(Colours.main_title)

        # Create file to run title.
        self.file_to_run_title = wx.StaticText(self, -1, "File to run:")
        self.file_to_run_title.SetFont(self.second_titles_font)
        self.file_to_run_title.SetForegroundColour(Colours.second_title)

        # Create Additional Files to run title.
        self.additional_files_title = wx.StaticText(self, -1, "Additional Files:")
        self.additional_files_title.SetFont(self.second_titles_font)
        self.additional_files_title.SetForegroundColour(Colours.second_title)

        # Create the place where the user can drop his file.
        self.run_file_editor = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE)
        self.run_file_target = FileDrop(self.run_file_editor, 1, self.new_run_file, ["py"],
                                        self.gui.dialog_box.update_text, True)
        self.run_file_editor.SetDropTarget(self.run_file_target)
        self.run_file_editor.SetValue("Drop your file here.")

        # Create the Additional Files list.
        self.additional_files = wx.ListBox(self, 78, style=wx.LB_SINGLE | wx.LB_HSCROLL | wx.LB_NEEDED_SB)
        self.additional_files_editor = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE)
        self.additional_files_target = FileDrop(self.additional_files, 10, self.new_additional_file, None,
                                                self.gui.dialog_box.update_text, False)
        self.additional_files.SetDropTarget(self.additional_files_target)
        self.Bind(wx.EVT_LISTBOX, self.on_additional_file_select, id=78)
        self.additional_files_editor.SetValue("Drop an additional file to the box from the left. The content of the"
                                              " selected file will be shown here.")

        # Add all the items into the sizer.
        self.sizer.Add(self.files_title, pos=(1, 5))
        self.sizer.Add(self.file_to_run_title, pos=(5, 5), flag=wx.RIGHT | wx.LEFT, border=5)
        self.sizer.Add(self.run_file_editor, pos=(8, 5), span=(30, 30), flag=wx.EXPAND | wx.RIGHT | wx.LEFT, border=5)
        self.sizer.Add(self.additional_files_title, pos=(42, 5), flag=wx.RIGHT | wx.LEFT, border=5)
        self.sizer.Add(self.additional_files, pos=(45, 5), span=(32, 1), flag=wx.EXPAND | wx.RIGHT | wx.LEFT, border=5)
        self.sizer.Add(self.additional_files_editor, pos=(45, 6), span=(32, 30), flag=wx.EXPAND | wx.RIGHT | wx.LEFT,
                       border=5)

    def create_commitments_and_privileges_part(self):
        """
            The function builds the commitments and privileges part.
        """

        # Create the title for the commitments and privileges section.
        self.commitments_and_privileges_title = self.create_title('Commitments' + ' &&' + '\nPrivileges',
                                                                  self.main_titles_font, Colours.main_title)

        # Crete the titles for all the fields of the current section.
        self.number_of_executors_title = self.create_title("Executors:", self.second_titles_font, Colours.second_title)

        self.number_of_executors_box = wx.ComboBox(self, choices=[str(i) for i in range(1, 40)], style=wx.CB_READONLY)
        self.number_of_executors_box.Bind(wx.EVT_COMBOBOX, self.on_select_number_of_executors)
        self.number_of_executors_box.SetValue('1')

        self.sizer.Add(self.commitments_and_privileges_title, pos=(1, 45))
        self.sizer.Add(self.number_of_executors_title, pos=(5, 45))
        self.sizer.Add(self.number_of_executors_box, pos=(5, 46))

    def create_properties_part(self):
        """
            The function builds the properties part.
        """

        self.properties_title = wx.StaticText(self, -1, 'Properties')
        self.properties_title.SetFont(self.main_titles_font)
        self.properties_title.SetForegroundColour(Colours.main_title)

        self.sizer.Add(self.properties_title, pos=(1, 75))

    def on_additional_file_select(self, e):
        """
            The function get called when the user selects an additional file from the Additional Files list.
        """

        index = e.GetSelection()
        self.selected_additional_file = self.additional_files.GetString(index)

        try:

            with open(self.selected_additional_file, "rb") as f:

                content = f.read()
                self.additional_files_editor.SetValue(content)

        except:

            self.additional_files_editor.SetValue("Can't show the content of this file.")

    def new_run_file(self, current_run_file):
        """
            The function gets called when a new run file got supplied by the user.
        """

        try:
            with open(current_run_file, 'rb') as f:

                content = f.read()

                self.run_file_editor.SetValue(content)

        except:
            self.run_file_editor.SetValue("Could not display the content of the file although it is recognized by the"
                                          " system, change it or drag it to the editor in order to try to display its"
                                          " content again.")

        self.file_to_run = current_run_file

        # Set the file to run of the request to the one that the user has entered.
        RequestFileCom.enter_dict({"Run File": current_run_file})

    def new_additional_file(self, current_additional_file):
        """
            The function gets called when a new additional file got supplied by the user.
        """

        if current_additional_file.split(".")[-1] in [".py", ".txt"]:

            with open(current_additional_file, 'rb') as f:

                content = f.read()

                self.additional_files_editor.SetValue(content)

        self.additional_files.Append(current_additional_file)

        # Add the new additional file to the current request file..
        RequestFileCom.enter_dict({"Additional Files": '@**'.join(self.additional_files_target.loaded_files_paths)})

    def start_request(self, e):
        """
            The function is called when the user wants to execute his current request. alerts the main code of the
            client that the user wants to send the request to the server.
        """

        # Send the request only if it's valid.
        if RequestValidation.is_valid:

            self.on_select_number_of_executors(wx.EVT_COMBOBOX)
            self.gui.general.thread_com.send.received_full_request = False
            self.gui.general.current_request = Request(self.file_to_run, "Current Request/")
            self.gui.general.send_request = True
            self.clear_last_request()

        else:

            if not RequestValidation.has_must_files:

                self.gui.dialog_box.update_text("You must supply value to the following titles: File To Run.")

    def remove_value(self, title, add):
        """
            The function receives a title and removes the value of the title in the gui of the client and from the
            current request file.
        """

        if title == "Run File":

            self.run_file_editor.SetValue("")
            RequestFileCom.enter_dict({"Run File": ""})

        elif title == "Additional Files":

            path = add

            # RequestValidation is a thread and it may call this function few times before the first call has finished.
            # In this case, this code will try to delete twice the same path. Make sure the path exists.
            path_index = self.additional_files.FindString(path)

            if path_index > -1:

                # If the path is currently selected remove the file content from the editor.
                if self.additional_files.IsSelected(path_index):

                    self.additional_files_editor.SetValue("")

                # Remove the path from the list box.
                self.additional_files.Delete(path_index)

                # Remove the path from the paths of the target.
                self.additional_files_target.loaded_files_paths.remove(path)

                # Remove the path from the current request file.
                current = RequestFileCom.get_value("Additional Files")

                current = current.replace(path, "")

                while "@**@**" in current:
                    current = current.replace("@**@**", "@**")

                while current.startswith("@**"):

                    current = current[3:]

                current = self.clear_dirty_end(current, ["@**", "\n"])

                additional_files_dict = {"Additional Files": current}

                RequestFileCom.enter_dict(additional_files_dict)

    def clear_dirty_end(self, data, symbols):
        """
            The function clears all the symbols from the end of the data string.
        """

        for symbol in symbols:

            if data.endswith(symbol):

                data = data[:-1*len(symbol)]

                data = self.clear_dirty_end(data, symbols)

                break

        return data

    def create_title(self, content, font, colour):
        """
            The function receives the content of the title, the font and the colour. Returns the title itself.
        """

        title = wx.StaticText(self, -1, content)
        title.SetFont(font)
        title.SetForegroundColour(colour)
        return title

    def on_select_number_of_executors(self, e):
        """
            The function is being called when the user chooses an option from a combo list.
        """

        RequestFileCom.enter_dict({"Executors Amount": self.number_of_executors_box.GetValue()})

    def clear_last_request(self):
        """
            The function resets anything relates to the last request.
        """

        # Resets the monitors.
        self.gui.monitor_window.reset()


class FileDrop(wx.FileDropTarget):

    def __init__(self, window, files_limit, new_file_call_function, supported_file_types, dialog_box, rounded):

        wx.FileDropTarget.__init__(self)

        # The gui item where the user will be able to drop his file.
        self.window = window

        # The number of files the user can enter.
        self.number_of_files_limit = files_limit

        # A list of all the successfully loaded files.
        self.loaded_files_paths = []

        # A list with the supported file types, if None all the types are supported.
        self.supported_file_types = supported_file_types

        # The dialog box function which the output will be printed by.
        self.dialog_box = dialog_box

        # If there is no more place for additional file, replace the first file with the new one.
        self.rounded = rounded

        self.new_file_call_function = new_file_call_function

    def OnDropFiles(self, x, y, files_names):

        # Iterate over the files the user dropped.
        for index in range(len(files_names)):

            # Get the path of the current file.
            name = files_names[index]

            # Make sure it's a new file and that it's supported.
            if not name in self.loaded_files_paths:

                # Check if the file type is supported.
                if self.supported_file_types and name.split('.')[-1] not in self.supported_file_types:

                    self.dialog_box("Only the following types are supported in this box: " +
                                    ', '.join(self.supported_file_types))
                    continue

                # Check if allowed loading more files.
                if len(self.loaded_files_paths) < self.number_of_files_limit:

                    # Add the file to the loaded files paths list.
                    self.loaded_files_paths.append(name)

                    # Call the function that does something about the new file.
                    self.new_file_call_function(name)

                # Change the first loaded file with the new one.
                elif self.rounded:

                    # Add the file to the loaded files paths list.
                    self.loaded_files_paths[0] = name

                    # Call the function that does something about the new file.
                    self.new_file_call_function(name)