import sqlite3 as lite
from FileInit import FileInit


class DataBase():
    """
        This class is responsible on anything relates to the server's data base.
    """

    def __init__(self, general, name, user, password, host="127.0.0.1", port=3306):

        self.general = general

        # The name of the data base.
        self.name = name

        self.user = user

        self.password = password

        self.host = host

        self.port = port

        # The data base connection handle.
        self.db = None

        # The instance which returned when connecting to the data base.
        self.connector = None

        # The cursor of the data base.
        self.cursor = None

        # The tables names of the db.
        self.tables = []

    def connect(self, db_name):
        """
            The function connects to the data base.
        """

        # Make sure the path to the .db file exists.
        FileInit.make_dir("Records")

        # Connect the data base.
        self.connector = lite.connect("Records" + "/" + db_name + ".db")

        # Get the cursor to the data base.
        self.cursor = self.connector.cursor()

    def create_table(self, table_name, columns):
        """
            The function creates new table in the data base. In addition, it inserts the columns and their types to the
            table. columns is as follow: [[column_name, type]...]
        """

        # # If the table already exist, delete it.
        # self.cursor.execute("DROP TABLE IF EXISTS " + table_name + ";")

        self.cursor.execute("CREATE TABLE if not exists " + table_name + "(" +
                            ', '.join(rubric[0] + " " + rubric[1] for rubric in columns) + ");")

        if not table_name in self.tables:

            self.tables.append(table_name)

        self.general.update_data_base_gui = True

    def insert(self, table_name, values):
        """
            The function receives a name of a table, and a list of the values of the new row by the order of the columns
            in the table.
        """

        self.cursor.execute("INSERT INTO " + table_name + " VALUES(" + ", ".join(value for value in values) + ");")

        self.general.update_data_base_gui = True

    def remove(self, table_name, condition):
        """
            The function removes rows from the received table according to the condition.
        """

        condition = self.convert_condition(condition)

        self.cursor.execute("DELETE FROM " + table_name + " WHERE " + condition + ";")

        self.general.update_data_base_gui = True

    def replace(self, table_name, condition, value):
        """
            The function receives a condition and a value and replaces the current value with the received one.
        """

        condition = self.convert_condition(condition)

        self.cursor.execute("UPDATE " + table_name + " SET " + value[0] + " = " + '"' + value[1] + '"' + " WHERE" +
                            condition + ";")

        self.general.update_data_base_gui = True

    def convert_condition(self, condition):
        """
            The function receives a condition and returns the condition as it should be written in sql.
            [[col, value], 0, [col, value], 1, [col, value]] --> ""col" = "value" OR "col" = "value" AND "col" = "value"
        """

        new_con = ""

        for item in condition:

            if item is int:

                if item == 0:

                    new_con += " OR"

                if item == 1:

                    new_con += " AND"

            elif type(item) is list:

                new_con += " " + item[0] + " = " + '"' + item[1] + '"'

        return new_con

    def delete_table(self, table_name, condition=""):
        """
            The function receives a table name and deletes its content.
        """

        if condition:

            condition = self.convert_condition(condition)

            self.cursor.execute("DELETE FROM " + table_name + " WHERE " + condition + ";")

        else:

            self.cursor.execute("DELETE FROM " + table_name + ";")

        self.general.update_data_base_gui = True

    def get_free_id(self, table_name):
        """
            The function receives a table name and returns a free id.
        """

        self.cursor.execute("SELECT Id FROM " + table_name + ";")
        content = self.cursor.fetchall()
        ids = [list(id_)[0] for id_ in content]

        if ids:

            free_ids = [item for item in range(1, len(ids) + 1) if item not in ids]

            if free_ids:

                return free_ids[0]

            else:

                return ids[-1] + 1

        return 1

    def table_to_string(self, table_name):
        """
            The function returns a string of the received table.
        """

        # The string that eventually will contain the table.
        string = table_name + "\n"

        if table_name in self.tables:

            # Get the columns of the table.
            self.cursor.execute("PRAGMA table_info(" + table_name + ");")

            # Store the columns names in the first line of the string.
            for row in self.cursor:
                string += row[1] + ", "

            string = string[:-2] + "\n"

            self.cursor.execute("SELECT * from " + table_name + ";")

            for row in self.cursor:

                string += ', '.join([str(value) for value in list(row)]) + "\n"

            # Return the string without the \n at the end.
            return string[:-1]

        else:

            return ""

    def db_to_string(self, tables=""):
        """
            The function returns a sting of the data base.
        """

        # The string that eventually will contain the data base.
        string = ""

        # If the function didn't receive tables list return all the tables.
        if not tables:
            tables = self.tables

        if tables:

            # Iterate over all the tables in the data base and add them to the main string.
            for table_name in tables:

                string += self.table_to_string(table_name) + "\n**********\n"

            # Return the string without the \n**********\n at the end.
            return string[:-12]

        else:
            return ""