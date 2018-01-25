import os
import shutil
import time

__all__ = ["log"]


class Logger:
    def __init__(self):
        self.settings = {
            "folder": "log",
            "extention": ".tsv",
            "programLog": "main.log",
            "timestamp": "%H:%M:%S",
            "datestamp": "%d-%m-%Y",
            "keepLogsFor": 30  # in days
        }
        self._hr = "─" * 50

        self.fileManagement()

        self._writeToFile("\nProgram started\n")
        self._writeToFile("%s\n" % self._hr)

    def __call__(self, string="", name=None, end="\n", flush=False):
        """
        Log and print a message
        """
        string = self._stringReplace(string)
        print(string, end=end, flush=flush)

        string = "%s%s" % (string, end)
        self._writeToFile(string, name)

    def error(self, string="", name=None, end="\n", flush=False):
        """
        Log and print an error
        """
        string = self._stringReplace(string)
        print("\033[7;31m %s \033[0;0m" % string, end=end, flush=flush)

        string = "[ERROR] %s [/ERROR]%s" % (string, end)
        self._writeToFile(string, name)

    def blind(self, string="", name=None, end="\n"):
        """
        Log in the background
        """
        string = self._stringReplace(string)
        string = "%s%s" % (string, end)
        self._writeToFile(string, name)

    def warn(self, string="", name=None, end="\n", flush=False):
        """
        Log and print a warning
        """
        string = self._stringReplace(string)
        print("\033[1;34m%s\033[0;0m" % string, end=end, flush=flush)

        string = "!!! %s !!!%s" % (string, end)
        self._writeToFile(string, name)

    def success(self, string="", name=None, end="\n", flush=False):
        """
        Log and print a success message
        """
        string = self._stringReplace(string)
        print("\033[7;32m %s \033[0;0m" % string, end=end, flush=flush)

        string = "[%s]%s" % (string, end)
        self._writeToFile(string, name)

    def highlight(self, string="", name=None, end="\n", flush=False):
        """
        Log and print a highlighted message
        """
        string = self._stringReplace(string)
        print("\033[1;36m%s\033[0;0m" % string, end=end, flush=flush)

        string = "%s%s" % (string, end)
        self._writeToFile(string, name)

    def summary(self, values):
        """
        Log a summary dict
        """
        self.__call__("\n")
        self.row()
        self.__call__("RUNTIME SUMMARY")
        self.__call__("Generated on [datetime]")
        self.row()
        for key in values:
            if type(values[key]) is dict:
                self.__call__("%s:" % key)
                for subkey in values[key]:
                    self.__call__("\t%s:\t\t%s" % (
                        subkey, values[key][subkey])
                    )
            else:
                self.__call__("%s:\t\t%s" % (key, values[key]))
        self.__call__()
        self._writeToFile("\n\n\n\n\n")

    def row(self):
        """
        Log a separator row of default length.
        """
        self.__call__(self._hr)

    def _fileHeaders(self, name):
        """
        Build file headers
        """
        return "%s\t%s\t%s\t%s\t%s\t%s\n" % (
            "Timestamp",
            "Brightness",
            "Color",
            "Power",
            "Observer update",
            "Deviation active"
        )

    def _writeToFile(self, string, name=None):
        """
        Add a log entry to logfile
        """
        extention = self.settings['extention']
        if name is None:
            name = self.settings['programLog']
            extention = ""
        else:
            if not os.path.exists("%s/%s%s" % (
                                  self.folderPath, name, extention)):
                string = self._fileHeaders(name) + string

        with open("%s/%s%s" % (self.folderPath, name, extention), 'a') as f:
            f.write(string)

    def _stringReplace(self, string):
        string = string.replace("[datetime]", "[date] [time]")
        string = string.replace(
            "[time]",
            time.strftime(self.settings['timestamp'])
        )
        string = string.replace(
            "[date]",
            time.strftime(self.settings['datestamp'])
        )

        return string

    def fileManagement(self):
        # Check if main logging folder exists and create if it doesn't
        path = os.path.dirname(os.path.abspath(__file__))
        self.folderPath = '%s/%s' % (path, self.settings['folder'])
        if not os.path.exists(self.folderPath):
            os.makedirs(self.folderPath)

        # Remove old log files
        for f in os.listdir(self.folderPath):
            path = os.path.join(self.folderPath, f)
            offset = time.time() - (self.settings['keepLogsFor'] * 86400)
            if os.path.getmtime(path) < offset:
                shutil.rmtree(path)

        # Check if daily logging folder exists and create if it doesn't
        self.folderPath = '%s/%s' % (
            self.folderPath,
            time.strftime(self.settings['datestamp'])
        )
        if not os.path.exists(self.folderPath):
            os.makedirs(self.folderPath)

        # Check if program log file exists and create if it doesn't
        filePath = "%s/%s" % (self.folderPath, self.settings['programLog'])
        if not os.path.isfile(filePath) or not os.path.getsize(filePath) > 0:
            with open(filePath, 'w') as f:
                self.__call__("Log opened on [datetime]")


log = Logger()
