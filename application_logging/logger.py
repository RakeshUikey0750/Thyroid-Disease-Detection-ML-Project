from datetime import datetime


class App_Logger:
    """
                 This class shall be used for logging all the log messages for this project.

                 Written By: Rakesh Uikey
                 Version: 1.0
                 Revisions: None

    """
    def __init__(self):
        self.current_time = None
        self.date = None
        self.now = None

    def log(self, file_object, log_message):
        self.now = datetime.now()
        self.date = self.now.date()
        self.current_time = self.now.strftime("%H:%M:%S")
        file_object.write(
            str(self.date) + "/" + str(self.current_time) + "\t\t" + log_message + "\n")
