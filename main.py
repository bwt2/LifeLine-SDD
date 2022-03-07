# library / module imports
# Note: Screen progression goes from startup.ui (0) --> setupReminder.ui (1)
# You can choose to import only parts from a module, by using the "from" keyword

import sys
from playsound import playsound
from PyQt5.QtGui import QMovie, QFont
import SQL
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import QTimer, QRunnable, pyqtSlot, QThreadPool, QObject, pyqtSignal
from PyQt5.QtWidgets import QDialog, QApplication, QPushButton
from PyQt5.uic import loadUi
from PyQt5.QtGui import QDoubleValidator, QValidator
import time
import datetime

# Class comments with (index x) refers to its order in the QtWidgets.QstackWidget() class which "stacks" all screens ui
# objects in order

# All classes have a function called __init__(), which is always executed when the class is being initiated.

# The self parameter is a reference to the current instance of the class, and is used to access variables that belongs
# to the class.

# To create a class that inherits the functionality from another class, send the parent class as a parameter when
# creating the child class

# super() function, you do not have to use the name of the parent element, it will automatically inherit the methods and
# properties from its parent.

# runs sqlCode() in SQL.py
exec(open("./SQL.py").read())


# # # # # # # # # # # # # # # # # # # # # # # # #
# NEXT: GET THE PRIMARY KEY OF REMNINDER TO AUTOINCREMENT
# # # # # # # # # # # # # # # # # # # # # # # # #


# convert row in database to string
def rowToString(rowConvert):
    # initialize an empty string
    stringConvert = " "

    # filter out punctuation from listConvert
    for x in rowConvert:
        if x.isalnum():
            stringConvert += x
        else:
            stringConvert += "0"

    # replace extra unnecessary characters
    iter1StringConvert = stringConvert.replace("0000000", ", ")
    iter2StringConvert = iter1StringConvert.replace("0000", "")
    finalStringConvert = iter2StringConvert.replace("0", " ")

    return finalStringConvert


# Class for startup screen (Screen index 0)
class Startup(QDialog):
    def __init__(self):
        super(Startup, self).__init__()
        loadUi("startup.ui", self)


        # running the gif
        self.movie = QMovie('Lifeline-Logo.gif')
        self.gifLabel.setMovie(self.movie)
        self.movie.start()

        # Set up timer object
        timer = QTimer(self)

        # if setup is done
        if SQL.sqlCode.getSetupDone(SQL.x) == "(1,)":
            timer.singleShot(5000, self.gotoMainMenu)
        else:
            # Trigger gotoReminderSetup after 3 seconds
            timer.singleShot(5000, self.gotoReminderSetupScreen)

        # threading
        self.threadpool = QThreadPool()
        worker = Worker()
        workerInterval = WorkerInterval()
        self.threadpool.start(worker)
        self.threadpool.start(workerInterval)

        # receiving signals
        workerInterval.signals.result.connect(self.updateReminder)
        worker.signals.result.connect(self.updateReminder)

    # function to update reminder screen
    def updateReminder(self, rInfo):
        name = rInfo[0]
        note = rInfo[1]
        reminderscreenWindow.updateReminderScreen(name, note)
        widget.setCurrentIndex(6)

    # function to change to ReminderSetupScreen
    def gotoReminderSetupScreen(self):
        widget.setCurrentIndex(1)
        # updates reminder setup screen
        remindersetupWindow.updateReminderSetup()

    # function to change to main menu screen
    def gotoMainMenu(self):
        widget.setCurrentIndex(5)


# Class for reminder setup screen (Screen index 1)
class ReminderSetup(QDialog):
    def __init__(self):
        super(ReminderSetup, self).__init__()
        loadUi("reminderSetupScreen.ui", self)
        self.addPersonalizedReminderButton.clicked.connect(self.gotoAddNewReminderScreen)
        self.reminderSetupNextButton.clicked.connect(self.gotoUserSettingScreen)
        self.updateReminderSetup()

    def updateReminderSetup(self):
        self.personalizedReminderDisplayLabel.setText(rowToString(SQL.x.setTextReminderNames()))

        # check if checkbox is unchecked
        if not SQL.sqlCode.getSetupDone(SQL.x) == "(1,)":
            if self.reminderSetupHydrateCheckBox.isChecked():
                reminderStatusChoice = 1
                reminderNameChoice = "Hydrate"
                SQL.sqlCode.updateReminderStatus(SQL.x, reminderStatusChoice, reminderNameChoice)
            else:
                reminderStatusChoice = 0
                reminderNameChoice = "Hydrate"
                SQL.sqlCode.updateReminderStatus(SQL.x, reminderStatusChoice, reminderNameChoice)

            if self.reminderSetupEatCheckBox.isChecked():
                reminderStatusChoice = 1
                reminderNameChoice = "Eat"
                SQL.sqlCode.updateReminderStatus(SQL.x, reminderStatusChoice, reminderNameChoice)
            else:
                reminderStatusChoice = 0
                reminderNameChoice = "Eat"
                SQL.sqlCode.updateReminderStatus(SQL.x, reminderStatusChoice, reminderNameChoice)

            if self.reminderSetupOutsideCheckBox.isChecked():
                reminderStatusChoice = 1
                reminderNameChoice = "Go outside"
                SQL.sqlCode.updateReminderStatus(SQL.x, reminderStatusChoice, reminderNameChoice)
            else:
                reminderStatusChoice = 0
                reminderNameChoice = "Go outside"
                SQL.sqlCode.updateReminderStatus(SQL.x, reminderStatusChoice, reminderNameChoice)

            if self.reminderSetupShowerCheckBox.isChecked():
                reminderStatusChoice = 1
                reminderNameChoice = "Shower"
                SQL.sqlCode.updateReminderStatus(SQL.x, reminderStatusChoice, reminderNameChoice)
            else:
                reminderStatusChoice = 0
                reminderNameChoice = "Shower"
                SQL.sqlCode.updateReminderStatus(SQL.x, reminderStatusChoice, reminderNameChoice)

    # function to change to AddNewReminderScreen (index 2)
    def gotoAddNewReminderScreen(self):
        addnewreminderWindow.updateAddNewReminderScreen()
        widget.setCurrentIndex(2)

    # function to change to userSettingScreen (index 3)
    def gotoUserSettingScreen(self):
        usersettingscreenWindow.updateUserSettingScreen()
        widget.setCurrentIndex(3)



# Class for add new reminder screen (Screen index 2)
class AddNewReminder(QDialog):
    def __init__(self):
        super(AddNewReminder, self).__init__()
        loadUi("addNewReminderScreen.ui", self)
        self.updateAddNewReminderScreen()

        # if setup is done
        if SQL.sqlCode.getSetupDone(SQL.x) == "(1,)":
            self.cancelMakingANewReminderButton.clicked.connect(self.gotoMainMenu)
        else:
            # Assigns back back to reminder setup screen
            self.cancelMakingANewReminderButton.clicked.connect(self.gotoReminderSetupScreen)

        # add reminder button connection
        self.addNewReminderButton.clicked.connect(self.setupSaveNewReminder)

        # validates user input to numbers 0-59 for secs & min, 0-24 for hours DO NOT TOUCH PLEASE SANK YOU
        self.userInputTimeIntervalSecondsLineEdit.returnPressed.connect(self.validatingSec)
        self.userInputTimeIntervalMinutesLineEdit.returnPressed.connect(self.validatingMin)
        self.userInputTimeIntervalHoursLineEdit.returnPressed.connect(self.validatingHrs)

    # validates user input to numbers 0-59 for secs DO NOT TOUCH THIS CODE please
    def validatingSec(self):
        validation_rule = QDoubleValidator(00, 59, 0)
        if validation_rule.validate(self.userInputTimeIntervalSecondsLineEdit.text(), 12)[0] == QValidator.Acceptable:
            self.userInputTimeIntervalSecondsLineEdit.setFocus()
        else:
            self.userInputTimeIntervalSecondsLineEdit.setText("00")

    # validates user input to numbers 0-59 for min
    def validatingMin(self):
        validation_rule = QDoubleValidator(00, 59, 0)
        if validation_rule.validate(self.userInputTimeIntervalMinutesLineEdit.text(), 12)[0] == QValidator.Acceptable:
            self.userInputTimeIntervalMinutesLineEdit.setFocus()
        else:
            self.userInputTimeIntervalMinutesLineEdit.setText("00")

    # validates user input to numbers 0-24 for hours
    def validatingHrs(self):
        validation_rule = QDoubleValidator(00, 23, 0)
        if validation_rule.validate(self.userInputTimeIntervalHoursLineEdit.text(), 12)[0] == QValidator.Acceptable:
            self.userInputTimeIntervalHoursLineEdit.setFocus()
        else:
            self.userInputTimeIntervalHoursLineEdit.setText("00")

    def gotoReminderSetupScreen(self):
        self.timeChoiceTimeIntervalsRadioButton.setText("Time Interval")
        widget.setCurrentIndex(1)

        # updates reminder setup screen
        remindersetupWindow.updateReminderSetup()

    def gotoMainMenu(self):
        self.timeChoiceTimeIntervalsRadioButton.setText("Time Interval")
        widget.setCurrentIndex(5)

        # updates reminder setup screen
        mainmenuscreenWindow.updateMainMenuScreen()

    def setupSaveNewReminder(self):
        # Receives user input and processes it to be sent the database
        AddNewReminder.setupSaveNewReminder.reminderNameChoice = self.addNewReminderNameTextBox.toPlainText()
        reminderNoteChoice = self.addNewReminderNotesTextBox.toPlainText()

        # reminder based on interval
        reminderTimerIntervalChoiceSecs = int(self.userInputTimeIntervalSecondsLineEdit.text()) \
                                          + 60 * int(self.userInputTimeIntervalMinutesLineEdit.text()) \
                                          + 3600 * int(self.userInputTimeIntervalHoursLineEdit.text())

        # "boolean" to choose if the reminder is based on clock or time interval
        if self.timeChoiceBasedOnClockRadioButton.isChecked():
            reminderTimeBasedChoice = "TRUE"
            reminderTimeIntervalBasedChoice = "FALSE"
        else:
            reminderTimeBasedChoice = "FALSE"
            reminderTimeIntervalBasedChoice = "TRUE"

        # reminder based on clock
        addNewReminderTimeEdit = self.userInputReminderTimeEdit.time()
        reminderTimeSecsChoice = (addNewReminderTimeEdit.hour() * 3600) + (addNewReminderTimeEdit.minute() * 60)

        # change screens
        # if setup is done
        if SQL.sqlCode.getSetupDone(SQL.x) == "(1,)":
            screenChange = 5
        else:
            # Assigns back back to reminder setup screen
            screenChange = 1

        # time interval cannot be zero
        if reminderTimerIntervalChoiceSecs == 0 and not self.timeChoiceBasedOnClockRadioButton.isChecked():
            self.timeChoiceTimeIntervalsRadioButton.setText("Time Interval Cannot Be Set To 0!")
        else:
            widget.setCurrentIndex(screenChange)
            # reminder turned off (0) or on (1)
            reminderStatusChoice = 1

            # send the user inputted data to the database
            SQL.sqlCode.insertNewReminder(SQL.x, AddNewReminder.setupSaveNewReminder.reminderNameChoice,
                                          reminderNoteChoice, reminderTimeBasedChoice,
                                          reminderTimeIntervalBasedChoice, reminderTimerIntervalChoiceSecs,
                                          reminderTimeSecsChoice, reminderStatusChoice)

            # updates reminder setup screen
            remindersetupWindow.updateReminderSetup()

        # database reference for updating main menu
        reminderNamesList = SQL.sqlCode.getReminderNameIndividual(SQL.x)

        # updating main menu
        mainmenuscreenWindow.mainMenuReminderListComboBox.addItem(reminderNamesList[-1])

    def updateAddNewReminderScreen(self):
        # get theme
        currentTheme = SQL.sqlCode.getTheme(SQL.x)

        # get font size
        currentFontSize = SQL.sqlCode.getFontSize(SQL.x)

        # update theme and font size
        if currentFontSize == "(32,)":
            if currentTheme == "(1,)":
                self.setStyleSheet("""background-color:rgb(54, 54, 54);}""")
                self.addANewReminderLabel.setStyleSheet("""color:white;""")
                self.warningLabel.setStyleSheet("""color:white;""")
                self.nameLabel.setStyleSheet("""color:white; font-size: 32pt;""")
                self.timeLabel.setStyleSheet("""color:white; font-size: 32pt;""")
                self.notesLabel.setStyleSheet("""color:white; font-size: 32pt;""")
                self.cancelMakingANewReminderButton.setStyleSheet("""color:white; font-size: 32pt;""")
                self.addNewReminderNameTextBox.setStyleSheet("""color:white; font-size: 32pt;""")
                self.timeChoiceBasedOnClockRadioButton.setStyleSheet("""color:white; font-size: 32pt;""")
                self.userInputReminderTimeEdit.setStyleSheet("""color:white; font-size: 32pt;""")
                self.timeChoiceTimeIntervalsRadioButton.setStyleSheet("""color:white; font-size: 32pt;""")
                self.userInputTimeIntervalHoursLineEdit.setStyleSheet("""color:white; font-size: 32pt;""")
                self.userInputTimeIntervalMinutesLineEdit.setStyleSheet("""color:white; font-size: 32pt;""")
                self.userInputTimeIntervalSecondsLineEdit.setStyleSheet("""color:white; font-size: 32pt;""")
                self.hmsLabel.setStyleSheet("""color:white; font-size: 32pt;""")
                self.addNewReminderNotesTextBox.setStyleSheet("""color:white; font-size: 32pt;""")
                self.addNewReminderButton.setStyleSheet("""color:white; font-size: 32pt;""")

            elif currentTheme == "(2,)":
                self.setStyleSheet("""background-color:rgb(224, 224, 224);}""")
                self.addANewReminderLabel.setStyleSheet("""color:black;""")
                self.warningLabel.setStyleSheet("""color:black;""")
                self.nameLabel.setStyleSheet("""color:black; font-size: 32pt;""")
                self.timeLabel.setStyleSheet("""color:black; font-size: 32pt;""")
                self.notesLabel.setStyleSheet("""color:black; font-size: 32pt;""")
                self.cancelMakingANewReminderButton.setStyleSheet("""color:black; font-size: 32pt;""")
                self.addNewReminderNameTextBox.setStyleSheet("""color:black; font-size: 32pt;""")
                self.timeChoiceBasedOnClockRadioButton.setStyleSheet("""color:black; font-size: 32pt;""")
                self.userInputReminderTimeEdit.setStyleSheet("""color:black; font-size: 32pt;""")
                self.timeChoiceTimeIntervalsRadioButton.setStyleSheet("""color:black; font-size: 32pt;""")
                self.userInputTimeIntervalHoursLineEdit.setStyleSheet("""color:black; font-size: 32pt;""")
                self.userInputTimeIntervalMinutesLineEdit.setStyleSheet("""color:black; font-size: 32pt;""")
                self.userInputTimeIntervalSecondsLineEdit.setStyleSheet("""color:black; font-size: 32pt;""")
                self.hmsLabel.setStyleSheet("""color:black; font-size: 32pt;""")
                self.addNewReminderNotesTextBox.setStyleSheet("""color:black; font-size: 32pt;""")
                self.addNewReminderButton.setStyleSheet("""color:black; font-size: 32pt;""")

        elif currentFontSize == "(28,)":
            if currentTheme == "(1,)":
                self.setStyleSheet("""background-color:rgb(54, 54, 54);}""")
                self.addANewReminderLabel.setStyleSheet("""color:white;""")
                self.warningLabel.setStyleSheet("""color:white;""")
                self.nameLabel.setStyleSheet("""color:white; font-size: 28pt;""")
                self.timeLabel.setStyleSheet("""color:white; font-size: 28pt;""")
                self.notesLabel.setStyleSheet("""color:white; font-size: 28pt;""")
                self.cancelMakingANewReminderButton.setStyleSheet("""color:white; font-size: 28pt;""")
                self.addNewReminderNameTextBox.setStyleSheet("""color:white; font-size: 28pt;""")
                self.timeChoiceBasedOnClockRadioButton.setStyleSheet("""color:white; font-size: 28pt;""")
                self.userInputReminderTimeEdit.setStyleSheet("""color:white; font-size: 28pt;""")
                self.timeChoiceTimeIntervalsRadioButton.setStyleSheet("""color:white; font-size: 28pt;""")
                self.userInputTimeIntervalHoursLineEdit.setStyleSheet("""color:white; font-size: 28pt;""")
                self.userInputTimeIntervalMinutesLineEdit.setStyleSheet("""color:white; font-size: 28pt;""")
                self.userInputTimeIntervalSecondsLineEdit.setStyleSheet("""color:white; font-size: 28pt;""")
                self.hmsLabel.setStyleSheet("""color:white; font-size: 28pt;""")
                self.addNewReminderNotesTextBox.setStyleSheet("""color:white; font-size: 28pt;""")
                self.addNewReminderButton.setStyleSheet("""color:white; font-size: 28pt;""")

            elif currentTheme == "(2,)":
                self.setStyleSheet("""background-color:rgb(224, 224, 224);}""")
                self.addANewReminderLabel.setStyleSheet("""color:black;""")
                self.warningLabel.setStyleSheet("""color:black;""")
                self.nameLabel.setStyleSheet("""color:black; font-size: 28pt;""")
                self.timeLabel.setStyleSheet("""color:black; font-size: 28pt;""")
                self.notesLabel.setStyleSheet("""color:black; font-size: 28pt;""")
                self.cancelMakingANewReminderButton.setStyleSheet("""color:black; font-size: 28pt;""")
                self.addNewReminderNameTextBox.setStyleSheet("""color:black; font-size: 28pt;""")
                self.timeChoiceBasedOnClockRadioButton.setStyleSheet("""color:black; font-size: 28pt;""")
                self.userInputReminderTimeEdit.setStyleSheet("""color:black; font-size: 28pt;""")
                self.timeChoiceTimeIntervalsRadioButton.setStyleSheet("""color:black; font-size: 28pt;""")
                self.userInputTimeIntervalHoursLineEdit.setStyleSheet("""color:black; font-size: 28pt;""")
                self.userInputTimeIntervalMinutesLineEdit.setStyleSheet("""color:black; font-size: 28pt;""")
                self.userInputTimeIntervalSecondsLineEdit.setStyleSheet("""color:black; font-size: 28pt;""")
                self.hmsLabel.setStyleSheet("""color:black; font-size: 28pt;""")
                self.addNewReminderNotesTextBox.setStyleSheet("""color:black; font-size: 28pt;""")
                self.addNewReminderButton.setStyleSheet("""color:black; font-size: 28pt;""")

        elif currentFontSize == "(24,)":
            if currentTheme == "(1,)":
                self.setStyleSheet("""background-color:rgb(54, 54, 54);}""")
                self.addANewReminderLabel.setStyleSheet("""color:white;""")
                self.warningLabel.setStyleSheet("""color:white;""")
                self.nameLabel.setStyleSheet("""color:white; font-size: 24pt;""")
                self.timeLabel.setStyleSheet("""color:white; font-size: 24pt;""")
                self.notesLabel.setStyleSheet("""color:white; font-size: 24pt;""")
                self.cancelMakingANewReminderButton.setStyleSheet("""color:white; font-size: 24pt;""")
                self.addNewReminderNameTextBox.setStyleSheet("""color:white; font-size: 24pt;""")
                self.timeChoiceBasedOnClockRadioButton.setStyleSheet("""color:white; font-size: 24pt;""")
                self.userInputReminderTimeEdit.setStyleSheet("""color:white; font-size: 24pt;""")
                self.timeChoiceTimeIntervalsRadioButton.setStyleSheet("""color:white; font-size: 24pt;""")
                self.userInputTimeIntervalHoursLineEdit.setStyleSheet("""color:white; font-size: 24pt;""")
                self.userInputTimeIntervalMinutesLineEdit.setStyleSheet("""color:white; font-size: 24pt;""")
                self.userInputTimeIntervalSecondsLineEdit.setStyleSheet("""color:white; font-size: 24pt;""")
                self.hmsLabel.setStyleSheet("""color:white; font-size: 24pt;""")
                self.addNewReminderNotesTextBox.setStyleSheet("""color:white; font-size: 24pt;""")
                self.addNewReminderButton.setStyleSheet("""color:white; font-size: 24pt;""")

            elif currentTheme == "(2,)":
                self.setStyleSheet("""background-color:rgb(224, 224, 224);}""")
                self.addANewReminderLabel.setStyleSheet("""color:black;""")
                self.warningLabel.setStyleSheet("""color:black;""")
                self.nameLabel.setStyleSheet("""color:black; font-size: 24pt;""")
                self.timeLabel.setStyleSheet("""color:black; font-size: 24pt;""")
                self.notesLabel.setStyleSheet("""color:black; font-size: 24pt;""")
                self.cancelMakingANewReminderButton.setStyleSheet("""color:black; font-size: 24pt;""")
                self.addNewReminderNameTextBox.setStyleSheet("""color:black; font-size: 24pt;""")
                self.timeChoiceBasedOnClockRadioButton.setStyleSheet("""color:black; font-size: 24pt;""")
                self.userInputReminderTimeEdit.setStyleSheet("""color:black; font-size: 24pt;""")
                self.timeChoiceTimeIntervalsRadioButton.setStyleSheet("""color:black; font-size: 24pt;""")
                self.userInputTimeIntervalHoursLineEdit.setStyleSheet("""color:black; font-size: 24pt;""")
                self.userInputTimeIntervalMinutesLineEdit.setStyleSheet("""color:black; font-size: 24pt;""")
                self.userInputTimeIntervalSecondsLineEdit.setStyleSheet("""color:black; font-size: 24pt;""")
                self.hmsLabel.setStyleSheet("""color:black; font-size: 24pt;""")
                self.addNewReminderNotesTextBox.setStyleSheet("""color:black; font-size: 24pt;""")
                self.addNewReminderButton.setStyleSheet("""color:black; font-size: 24pt;""")

        elif currentFontSize == "(20,)":
            if currentTheme == "(1,)":
                self.setStyleSheet("""background-color:rgb(54, 54, 54);}""")
                self.addANewReminderLabel.setStyleSheet("""color:white;""")
                self.warningLabel.setStyleSheet("""color:white;""")
                self.nameLabel.setStyleSheet("""color:white; font-size: 20pt;""")
                self.timeLabel.setStyleSheet("""color:white; font-size: 20pt;""")
                self.notesLabel.setStyleSheet("""color:white; font-size: 20pt;""")
                self.cancelMakingANewReminderButton.setStyleSheet("""color:white; font-size: 20pt;""")
                self.addNewReminderNameTextBox.setStyleSheet("""color:white; font-size: 20pt;""")
                self.timeChoiceBasedOnClockRadioButton.setStyleSheet("""color:white; font-size: 20pt;""")
                self.userInputReminderTimeEdit.setStyleSheet("""color:white; font-size: 20pt;""")
                self.timeChoiceTimeIntervalsRadioButton.setStyleSheet("""color:white; font-size: 20pt;""")
                self.userInputTimeIntervalHoursLineEdit.setStyleSheet("""color:white; font-size: 20pt;""")
                self.userInputTimeIntervalMinutesLineEdit.setStyleSheet("""color:white; font-size: 20pt;""")
                self.userInputTimeIntervalSecondsLineEdit.setStyleSheet("""color:white; font-size: 20pt;""")
                self.hmsLabel.setStyleSheet("""color:white; font-size: 20pt;""")
                self.addNewReminderNotesTextBox.setStyleSheet("""color:white; font-size: 20pt;""")
                self.addNewReminderButton.setStyleSheet("""color:white; font-size: 20pt;""")

            elif currentTheme == "(2,)":
                self.setStyleSheet("""background-color:rgb(224, 224, 224);}""")
                self.addANewReminderLabel.setStyleSheet("""color:black;""")
                self.warningLabel.setStyleSheet("""color:black;""")
                self.nameLabel.setStyleSheet("""color:black; font-size: 20pt;""")
                self.timeLabel.setStyleSheet("""color:black; font-size: 20pt;""")
                self.notesLabel.setStyleSheet("""color:black; font-size: 20pt;""")
                self.cancelMakingANewReminderButton.setStyleSheet("""color:black; font-size: 20pt;""")
                self.addNewReminderNameTextBox.setStyleSheet("""color:black; font-size: 20pt;""")
                self.timeChoiceBasedOnClockRadioButton.setStyleSheet("""color:black; font-size: 20pt;""")
                self.userInputReminderTimeEdit.setStyleSheet("""color:black; font-size: 20pt;""")
                self.timeChoiceTimeIntervalsRadioButton.setStyleSheet("""color:black; font-size: 20pt;""")
                self.userInputTimeIntervalHoursLineEdit.setStyleSheet("""color:black; font-size: 20pt;""")
                self.userInputTimeIntervalMinutesLineEdit.setStyleSheet("""color:black; font-size: 20pt;""")
                self.userInputTimeIntervalSecondsLineEdit.setStyleSheet("""color:black; font-size: 20pt;""")
                self.hmsLabel.setStyleSheet("""color:black; font-size: 20pt;""")
                self.addNewReminderNotesTextBox.setStyleSheet("""color:black; font-size: 20pt;""")
                self.addNewReminderButton.setStyleSheet("""color:black; font-size: 20pt;""")


# Class for user settings screen (Screen index 3)
class UserSettingScreen(QDialog):
    def __init__(self):
        super(UserSettingScreen, self).__init__()
        loadUi("userSettingScreen.ui", self)
        self.updateUserSettingScreen()

    # updates Main menu when screen switches to it
    # dark (1): rgb(54, 54, 54)
    # light (2): rgb(224,224,224)
    def updateUserSettingScreen(self):
        currentTheme = SQL.sqlCode.getTheme(SQL.x)
        if currentTheme == "(1,)":
            self.setStyleSheet("""background-color:rgb(54, 54, 54);""")
            self.leaveFromSettingsScreen.setStyleSheet("""color:white;""")
            self.settingsLabel.setStyleSheet("""color:white;""")
            self.themeLabel.setStyleSheet("""color:white;""")
            self.chooseDarkThemeRadioButton.setStyleSheet("""color:white;""")
            self.chooseLightThemeRadioButton.setStyleSheet("""color:white;""")
            self.fontSizeLabel.setStyleSheet("""color:white;""")
            self.sampleLabel.setStyleSheet("""color:white;""")
            self.sampleTextSizeLabel.setStyleSheet("""color:white;""")
            self.settingSetupApplyButton.setStyleSheet("""color:white;""")
            self.fontSizeSliderNum1Label.setStyleSheet("""color:white;""")
            self.fontSizeSliderNum2Label.setStyleSheet("""color:white;""")
            self.fontSizeSliderNum3Label.setStyleSheet("""color:white;""")
            self.fontSizeSliderNum4Label.setStyleSheet("""color:white;""")

        elif currentTheme == "(2,)":
            self.setStyleSheet("""background-color:rgb(224, 224, 224);}""")
            self.leaveFromSettingsScreen.setStyleSheet("""color:black;""")
            self.settingsLabel.setStyleSheet("""color:black;""")
            self.themeLabel.setStyleSheet("""color:black;""")
            self.chooseDarkThemeRadioButton.setStyleSheet("""color:black;""")
            self.chooseLightThemeRadioButton.setStyleSheet("""color:black;""")
            self.fontSizeLabel.setStyleSheet("""color:black;""")
            self.sampleLabel.setStyleSheet("""color:black;""")
            self.sampleTextSizeLabel.setStyleSheet("""color:black;""")
            self.settingSetupApplyButton.setStyleSheet("""color:black;""")
            self.fontSizeSliderNum1Label.setStyleSheet("""color:black;""")
            self.fontSizeSliderNum2Label.setStyleSheet("""color:black;""")
            self.fontSizeSliderNum3Label.setStyleSheet("""color:black;""")
            self.fontSizeSliderNum4Label.setStyleSheet("""color:black;""")
            self.fontSizeSlider.setStyleSheet("""color:black;""")

        self.settingSetupApplyButton.clicked.connect(self.applySettings)
        self.fontSizeSlider.valueChanged.connect(self.valueChange)

        # if setup is done
        if SQL.sqlCode.getSetupDone(SQL.x) == "(1,)":
            self.leaveFromSettingsScreen.clicked.connect(self.gotoMainMenu)
        else:
            # Assigns back back to reminder setup screen
            self.leaveFromSettingsScreen.clicked.connect(self.gotoReminderSetupScreen)

    def valueChange(self):
        fontSizeValue = 16 + (4 * self.fontSizeSlider.value())
        self.sampleTextSizeLabel.setFont(QFont("Hans Kendrick", fontSizeValue))

    def realFontSizeValue(self):
        realFontSizeValue = 16 + (4 * self.fontSizeSlider.value())
        return realFontSizeValue

    def gotoReminderSetupScreen(self):
        widget.setCurrentIndex(1)

        # updates reminder setup screen
        remindersetupWindow.updateReminderSetup()

    def gotoMainMenu(self):
        widget.setCurrentIndex(5)
        mainmenuscreenWindow.updateMainMenuScreen()

    def applySettings(self):
        # set setup to be done
        setupStatusChoice = 1

        # themeChoice selection
        if self.chooseDarkThemeRadioButton.isChecked():
            userThemeChoice = 1
        elif self.chooseLightThemeRadioButton.isChecked():
            userThemeChoice = 2
        elif self.chooseTimeBasedThemeRadioButton.isChecked():
            userThemeChoice = 3

        fontSizeChoice = self.realFontSizeValue()

        # send user data to SQL.py
        SQL.sqlCode.setSettings(SQL.x, setupStatusChoice, userThemeChoice, fontSizeChoice)

        # go to settings saved screen
        settingssavedscreenWindow.updateSettingsSavedScreen()
        widget.setCurrentIndex(4)


# Class for "Settings Saved" (Screen index 4)
class SettingsSavedScreen(QDialog):
    def __init__(self):
        super(SettingsSavedScreen, self).__init__()
        loadUi("settingsSavedScreen.ui", self)
        self.updateSettingsSavedScreen()
        self.settingsSavedOkButton.clicked.connect(self.gotoMainMenu)

    # updates light / dark mode
    # dark (1): rgb(54, 54, 54)
    # light (2): rgb(224,224,224)
    def updateSettingsSavedScreen(self):
        # get theme
        currentTheme = SQL.sqlCode.getTheme(SQL.x)

        # get font size
        currentFontSize = SQL.sqlCode.getFontSize(SQL.x)

        # update theme and font size
        if currentFontSize == "(32,)":
            if currentTheme == "(1,)":
                self.setStyleSheet("""background-color:rgb(54, 54, 54);}""")
                self.settingsSavedLabel.setStyleSheet("""color:white; font-size:32pt;""")
                self.settingsSavedOkButton.setStyleSheet("""color:white; font-size:32pt;""")
            elif currentTheme == "(2,)":
                self.setStyleSheet("""background-color:rgb(224, 224, 224);}""")
                self.settingsSavedLabel.setStyleSheet("""color:black; font-size:32pt;""")
                self.settingsSavedOkButton.setStyleSheet("""color:black; font-size:32pt;""")

        elif currentFontSize == "(28,)":
            if currentTheme == "(1,)":
                self.setStyleSheet("""background-color:rgb(54, 54, 54);}""")
                self.settingsSavedLabel.setStyleSheet("""color:white; font-size:28pt;""")
                self.settingsSavedOkButton.setStyleSheet("""color:white; font-size:28pt;""")
            elif currentTheme == "(2,)":
                self.setStyleSheet("""background-color:rgb(224, 224, 224);}""")
                self.settingsSavedLabel.setStyleSheet("""color:black; font-size:28pt;""")
                self.settingsSavedOkButton.setStyleSheet("""color:black; font-size:28pt;""")

        elif currentFontSize == "(24,)":
            if currentTheme == "(1,)":
                self.setStyleSheet("""background-color:rgb(54, 54, 54);}""")
                self.settingsSavedLabel.setStyleSheet("""color:white; font-size:28pt;""")
                self.settingsSavedOkButton.setStyleSheet("""color:white; font-size:28pt;""")
            elif currentTheme == "(2,)":
                self.setStyleSheet("""background-color:rgb(224, 224, 224);}""")
                self.settingsSavedLabel.setStyleSheet("""color:black; font-size:28pt;""")
                self.settingsSavedOkButton.setStyleSheet("""color:black; font-size:28pt;""")

        elif currentFontSize == "(20,)":
            if currentTheme == "(1,)":
                self.setStyleSheet("""background-color:rgb(54, 54, 54);}""")
                self.settingsSavedLabel.setStyleSheet("""color:white; font-size:28pt;""")
                self.settingsSavedOkButton.setStyleSheet("""color:white; font-size:28pt;""")
            elif currentTheme == "(2,)":
                self.setStyleSheet("""background-color:rgb(224, 224, 224);}""")
                self.settingsSavedLabel.setStyleSheet("""color:black; font-size:28pt;""")
                self.settingsSavedOkButton.setStyleSheet("""color:black; font-size:28pt;""")

    def gotoMainMenu(self):
        widget.setCurrentIndex(5)
        mainmenuscreenWindow.updateMainMenuScreen()


# Class for Main Menu (Screen index 5)
class MainMenuScreen(QDialog):
    def __init__(self):
        super(MainMenuScreen, self).__init__()
        loadUi("mainMenuScreen.ui", self)
        self.setStyleSheet("""background-color:rgb(54, 54, 54);}""")
        self.LifelineLabel.setStyleSheet("""color: white;""")
        self.mainMenuOptionsButton.setStyleSheet("""color: white;""")
        self.mainMenuAddReminderButton.setStyleSheet("""color: white""")

        # button connections
        self.mainMenuOptionsButton.clicked.connect(self.gotoSettingsScreen)
        self.mainMenuAddReminderButton.clicked.connect(self.gotoAddNewReminderScreen)
        self.mainMenuRemoveReminderButton.clicked.connect(self.removeReminder)

        # initial combobox setup
        reminderNamesList = SQL.sqlCode.getReminderNameIndividual(SQL.x)
        self.mainMenuReminderListComboBox.addItems(reminderNamesList)

        # initial UI display
        noteText = SQL.sqlCode.getReminderNotesIndividual(SQL.x)
        timeBasedTrueArray = SQL.sqlCode.getTimeBasedTrueArray(SQL.x)

        i = self.mainMenuReminderListComboBox.findText(reminderNamesList[0])
        self.reminderNoteLabel.setText(noteText[i])
        if timeBasedTrueArray[0] == "TRUE":
            extraText = "At " + self.getRawToConverted(0)
        else:
            extraText = "Every " + self.getRawToConvertedInterval(0)
        self.reminderNextLabel.setText("Set to Ring " + extraText)

        # combobox connections
        self.mainMenuReminderListComboBox.activated.connect(self.updateMainMenuWidgets)

        # update itself
        self.updateMainMenuScreen()

    def updateMainMenuWidgets(self):
        reminderNamesList = SQL.sqlCode.getReminderNameIndividual(SQL.x)
        noteText = SQL.sqlCode.getReminderNotesIndividual(SQL.x)
        timeBasedTrueArray = SQL.sqlCode.getTimeBasedTrueArray(SQL.x)

        # current index of combobox
        currentCBoxIndex = self.mainMenuReminderListComboBox.currentIndex()

        # updates widgets on screen
        i = self.mainMenuReminderListComboBox.findText(reminderNamesList[currentCBoxIndex])
        self.reminderNoteLabel.setText(noteText[i])
        if timeBasedTrueArray[currentCBoxIndex] == "TRUE":
            extraText = "At " + self.getRawToConverted(currentCBoxIndex)
        else:
            extraText = "Every " + self.getRawToConvertedInterval(currentCBoxIndex)
        self.reminderNextLabel.setText("Set to Ring " + extraText)

    def getRawToConvertedInterval(self, j):
        SecsInterval = SQL.sqlCode.getReminderIntervalSecAll(SQL.x)
        if SecsInterval[j] == 0:
            alarm = "00:00:00"
        else:
            Hours = ((int(SecsInterval[j]) - (int(SecsInterval[j]) % 3600)) / 3600)
            Minutes = ((int(SecsInterval[j]) - (Hours * 3600)) - ((int(SecsInterval[j]) - (Hours * 3600)) % 60)) / 60
            Sec = int(SecsInterval[j]) - (Hours * 3600) - (Minutes * 60)

            # format to match time
            alarm = "{:02d}:{:02d}:{:02d}".format(int(Hours), int(Minutes), int(Sec))
        return alarm

    def getRawToConverted(self, j):
        SecsInterval = SQL.sqlCode.getReminderSecAll(SQL.x)
        Hours = ((int(SecsInterval[j]) - (int(SecsInterval[j]) % 3600)) / 3600)
        Minutes = ((int(SecsInterval[j]) - (Hours * 3600)) - ((int(SecsInterval[j]) - (Hours * 3600)) % 60)) / 60
        Sec = int(SecsInterval[j]) - (Hours * 3600) - (Minutes * 60)

        # format to match time
        alarm = "{:02d}:{:02d}:{:02d}".format(int(Hours), int(Minutes), int(Sec))
        return alarm

    # updates Main menu when screen switches to it
    # dark (1): rgb(54, 54, 54)
    # light (2): rgb(224,224,224)
    def updateMainMenuScreen(self):
        # get theme
        currentTheme = SQL.sqlCode.getTheme(SQL.x)

        # get font size
        currentFontSize = SQL.sqlCode.getFontSize(SQL.x)

        # update font size and theme
        if currentFontSize == "(32,)":
            if currentTheme == "(1,)":
                self.setStyleSheet("""background-color:rgb(54, 54, 54);}""")
                self.LifelineLabel.setStyleSheet("""color: white; font-size: 32pt;""")
                self.mainMenuOptionsButton.setStyleSheet("""color: white;font-size: 32pt;""")
                self.mainMenuAddReminderButton.setStyleSheet("""color: white;font-size: 32pt;""")
                self.mainMenuRemoveReminderButton.setStyleSheet("""color: white;font-size: 32pt;""")
                self.viewRemindersLabel.setStyleSheet("""color: white;font-size: 32pt;""")
                self.reminderNoteLabel.setStyleSheet("""color: white;font-size: 32pt;""")
                self.reminderNextLabel.setStyleSheet("""color: white;font-size: 32pt;""")
                self.mainMenuReminderListComboBox.setStyleSheet("""color: white;font-size: 32pt;""")

            elif currentTheme == "(2,)":
                self.setStyleSheet("""background-color:rgb(224, 224, 224);}""")
                self.LifelineLabel.setStyleSheet("""color: black;font-size: 32pt;""")
                self.mainMenuOptionsButton.setStyleSheet("""color: black;font-size: 32pt;""")
                self.mainMenuAddReminderButton.setStyleSheet("""color: black;font-size: 32pt;""")
                self.mainMenuRemoveReminderButton.setStyleSheet("""color: black;font-size: 32pt;""")
                self.viewRemindersLabel.setStyleSheet("""color: black;font-size: 32pt;""")
                self.reminderNoteLabel.setStyleSheet("""color: black;font-size: 32pt;""")
                self.reminderNextLabel.setStyleSheet("""color: black;font-size: 32pt;""")
                self.mainMenuReminderListComboBox.setStyleSheet("""color: black;font-size: 32pt;""")

        elif currentFontSize == "(28,)":
            if currentTheme == "(1,)":
                self.setStyleSheet("""background-color:rgb(54, 54, 54);}""")
                self.LifelineLabel.setStyleSheet("""color: white; font-size: 28pt;""")
                self.mainMenuOptionsButton.setStyleSheet("""color: white;font-size: 28pt;""")
                self.mainMenuAddReminderButton.setStyleSheet("""color: white;font-size: 28pt;""")
                self.mainMenuRemoveReminderButton.setStyleSheet("""color: white;font-size: 28pt;""")
                self.viewRemindersLabel.setStyleSheet("""color: white;font-size: 28pt;""")
                self.reminderNoteLabel.setStyleSheet("""color: white;font-size: 28pt;""")
                self.reminderNextLabel.setStyleSheet("""color: white;font-size: 28pt;""")
                self.mainMenuReminderListComboBox.setStyleSheet("""color: white;font-size: 28pt;""")

            elif currentTheme == "(2,)":
                self.setStyleSheet("""background-color:rgb(224, 224, 224);}""")
                self.LifelineLabel.setStyleSheet("""color: black;font-size: 28pt;""")
                self.mainMenuOptionsButton.setStyleSheet("""color: black;font-size: 28pt;""")
                self.mainMenuAddReminderButton.setStyleSheet("""color: black;font-size: 28pt;""")
                self.mainMenuRemoveReminderButton.setStyleSheet("""color: black;font-size: 28pt;""")
                self.viewRemindersLabel.setStyleSheet("""color: black;font-size: 28pt;""")
                self.reminderNoteLabel.setStyleSheet("""color: black;font-size: 28pt;""")
                self.reminderNextLabel.setStyleSheet("""color: black;font-size: 28pt;""")
                self.mainMenuReminderListComboBox.setStyleSheet("""color: black;font-size: 28pt;""")

        elif currentFontSize == "(24,)":
            if currentTheme == "(1,)":
                self.setStyleSheet("""background-color:rgb(54, 54, 54);}""")
                self.LifelineLabel.setStyleSheet("""color: white; font-size: 24pt;""")
                self.mainMenuOptionsButton.setStyleSheet("""color: white;font-size: 24pt;""")
                self.mainMenuAddReminderButton.setStyleSheet("""color: white;font-size: 24pt;""")
                self.mainMenuRemoveReminderButton.setStyleSheet("""color: white;font-size: 24pt;""")
                self.viewRemindersLabel.setStyleSheet("""color: white;font-size: 24pt;""")
                self.reminderNoteLabel.setStyleSheet("""color: white;font-size: 24pt;""")
                self.reminderNextLabel.setStyleSheet("""color: white;font-size: 24pt;""")
                self.mainMenuReminderListComboBox.setStyleSheet("""color: white;font-size: 24pt;""")

            elif currentTheme == "(2,)":
                self.setStyleSheet("""background-color:rgb(224, 224, 224);}""")
                self.LifelineLabel.setStyleSheet("""color: black;font-size: 24pt;""")
                self.mainMenuOptionsButton.setStyleSheet("""color: black;font-size: 24pt;""")
                self.mainMenuAddReminderButton.setStyleSheet("""color: black;font-size: 24pt;""")
                self.mainMenuRemoveReminderButton.setStyleSheet("""color: black;font-size: 24pt;""")
                self.viewRemindersLabel.setStyleSheet("""color: black;font-size: 24pt;""")
                self.reminderNoteLabel.setStyleSheet("""color: black;font-size: 24pt;""")
                self.reminderNextLabel.setStyleSheet("""color: black;font-size: 24pt;""")
                self.mainMenuReminderListComboBox.setStyleSheet("""color: black;font-size: 24pt;""")

        elif currentFontSize == "(20,)":
            if currentTheme == "(1,)":
                self.setStyleSheet("""background-color:rgb(54, 54, 54);}""")
                self.LifelineLabel.setStyleSheet("""color: white; font-size: 20pt;""")
                self.mainMenuOptionsButton.setStyleSheet("""color: white;font-size: 20pt;""")
                self.mainMenuAddReminderButton.setStyleSheet("""color: white;font-size: 20pt;""")
                self.mainMenuRemoveReminderButton.setStyleSheet("""color: white;font-size: 20pt;""")
                self.viewRemindersLabel.setStyleSheet("""color: white;font-size: 20pt;""")
                self.reminderNoteLabel.setStyleSheet("""color: white;font-size: 20pt;""")
                self.reminderNextLabel.setStyleSheet("""color: white;font-size: 20pt;""")
                self.mainMenuReminderListComboBox.setStyleSheet("""color: white;font-size: 20pt;""")

            elif currentTheme == "(2,)":
                self.setStyleSheet("""background-color:rgb(224, 224, 224);}""")
                self.LifelineLabel.setStyleSheet("""color: black;font-size: 20pt;""")
                self.mainMenuOptionsButton.setStyleSheet("""color: black;font-size: 20pt;""")
                self.mainMenuAddReminderButton.setStyleSheet("""color: black;font-size: 20pt;""")
                self.mainMenuRemoveReminderButton.setStyleSheet("""color: black;font-size: 20pt;""")
                self.viewRemindersLabel.setStyleSheet("""color: black;font-size: 20pt;""")
                self.reminderNoteLabel.setStyleSheet("""color: black;font-size: 20pt;""")
                self.reminderNextLabel.setStyleSheet("""color: black;font-size: 20pt;""")
                self.mainMenuReminderListComboBox.setStyleSheet("""color: black;font-size: 20pt;""")

    def gotoSettingsScreen(self):
        usersettingscreenWindow.updateUserSettingScreen()
        widget.setCurrentIndex(3)

    def gotoAddNewReminderScreen(self):
        addnewreminderWindow.updateAddNewReminderScreen()
        widget.setCurrentIndex(2)

    def removeReminder(self):
        reminderNamesList = SQL.sqlCode.getReminderNameIndividual(SQL.x)
        currentCBoxIndex = self.mainMenuReminderListComboBox.currentIndex()
        SQL.sqlCode.deleteReminder(SQL.x,reminderNamesList[currentCBoxIndex])




# Class for Reminder (Screen index 6)
class ReminderScreen(QDialog):
    def __init__(self):
        super(ReminderScreen, self).__init__()
        loadUi("reminder.ui", self)
        self.reminderOkayButton.clicked.connect(self.gotoMainMenuScreen)

    def gotoMainMenuScreen(self):
        widget.setCurrentIndex(5)
        mainmenuscreenWindow.updateMainMenuScreen()

    def updateReminderScreen(self, rName, rNotes):
        # change text for reminder screen
        self.reminderNameDisplayLabel.setText(rName)
        self.reminderNotesDisplayLabel.setText(rNotes)

        # get theme
        currentTheme = SQL.sqlCode.getTheme(SQL.x)

        # get font size
        currentFontSize = SQL.sqlCode.getFontSize(SQL.x)

        # update theme and font size
        if currentFontSize == "(32,)":
            if currentTheme == "(1,)":
                self.setStyleSheet("""background-color:rgb(54, 54, 54);}""")
                self.reminderNameDisplayLabel.setStyleSheet("""color:white; font-size:32pt;""")
                self.reminderNotesDisplayLabel.setStyleSheet("""color:white; font-size:32pt;""")
                self.reminderOkayButton.setStyleSheet("""color:white; font-size:32pt;""")
            elif currentTheme == "(2,)":
                self.setStyleSheet("""background-color:rgb(224, 224, 224);}""")
                self.reminderNameDisplayLabel.setStyleSheet("""color:black; font-size:32pt;""")
                self.reminderNotesDisplayLabel.setStyleSheet("""color:black; font-size:32pt;""")
                self.reminderOkayButton.setStyleSheet("""color:black; font-size:32pt;""")

        elif currentFontSize == "(28,)":
            if currentTheme == "(1,)":
                self.setStyleSheet("""background-color:rgb(54, 54, 54);}""")
                self.reminderNameDisplayLabel.setStyleSheet("""color:white; font-size:28pt;""")
                self.reminderNotesDisplayLabel.setStyleSheet("""color:white; font-size:28pt;""")
                self.reminderOkayButton.setStyleSheet("""color:white; font-size:28pt;""")
            elif currentTheme == "(2,)":
                self.setStyleSheet("""background-color:rgb(224, 224, 224);}""")
                self.reminderNameDisplayLabel.setStyleSheet("""color:black; font-size:28pt;""")
                self.reminderNotesDisplayLabel.setStyleSheet("""color:black; font-size:28pt;""")
                self.reminderOkayButton.setStyleSheet("""color:black; font-size:28pt;""")

        elif currentFontSize == "(24,)":
            if currentTheme == "(1,)":
                self.setStyleSheet("""background-color:rgb(54, 54, 54);}""")
                self.reminderNameDisplayLabel.setStyleSheet("""color:white; font-size:24pt;""")
                self.reminderNotesDisplayLabel.setStyleSheet("""color:white; font-size:24pt;""")
                self.reminderOkayButton.setStyleSheet("""color:white; font-size:24pt;""")
            elif currentTheme == "(2,)":
                self.setStyleSheet("""background-color:rgb(224, 224, 224);}""")
                self.reminderNameDisplayLabel.setStyleSheet("""color:black; font-size:24pt;""")
                self.reminderNotesDisplayLabel.setStyleSheet("""color:black; font-size:24pt;""")
                self.reminderOkayButton.setStyleSheet("""color:black; font-size:24pt;""")

        elif currentFontSize == "(20,)":
            if currentTheme == "(1,)":
                self.setStyleSheet("""background-color:rgb(54, 54, 54);}""")
                self.reminderNameDisplayLabel.setStyleSheet("""color:white; font-size:20pt;""")
                self.reminderNotesDisplayLabel.setStyleSheet("""color:white; font-size:20pt;""")
                self.reminderOkayButton.setStyleSheet("""color:white; font-size:20pt;""")

            elif currentTheme == "(2,)":
                self.setStyleSheet("""background-color:rgb(224, 224, 224);}""")
                self.reminderNameDisplayLabel.setStyleSheet("""color:black; font-size:20pt;""")
                self.reminderNotesDisplayLabel.setStyleSheet("""color:black; font-size:20pt;""")
                self.reminderOkayButton.setStyleSheet("""color:black; font-size:20pt;""")


# reminder based on time thread
class Worker(QRunnable):
    def __init__(self):
        super(Worker, self).__init__()
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        # Notification System Here
        # Reminder
        i = 0
        z = 0
        y = 0
        a = 0

        AlarmSecs = SQL.sqlCode.getReminderTimeSecsGlobal(SQL.x)
        ReminderName = SQL.sqlCode.getReminderNameGlobal(SQL.x)
        ReminderNotes = SQL.sqlCode.getReminderNotesGlobal(SQL.x)

        Alarms = []
        Name = []
        Note = []

        # Code to run notification from database
        for x in AlarmSecs:
            Hours = ((int(AlarmSecs[i]) - (int(AlarmSecs[i]) % 3600)) / 3600)
            Minutes = ((int(AlarmSecs[i]) - (Hours * 3600)) - ((int(AlarmSecs[i]) - (Hours * 3600)) % 60)) / 60
            Sec = int(AlarmSecs[i]) - (Hours * 3600) - (Minutes * 60)
            # format to match time
            alarm = "{:02d}:{:02d}:{:02d}".format(int(Hours), int(Minutes), int(Sec))

            # Add to array
            Alarms.append(alarm)
            i += 1

        for x in ReminderName:
            Name.append(ReminderName[z])
            z += 1

        for x in ReminderNotes:
            Note.append(ReminderNotes[y])
            y += 1
        while True:
            current_time = time.strftime("%H:%M:%S")
            p = 0
            while p != len(Alarms):
                if current_time == Alarms[p]:
                    # (Heading for notification, Subtext for notification)
                    reminderInfo = [Name[p], Note[p]]
                    self.signals.result.emit(reminderInfo)

                    # plays reminder sound
                    playsound('LifeLineRingtone.mp3', block=False)
                    time.sleep(1)

                else:
                    pass
                p += 1


# signal class for workerInterval
class WorkerIntervalSignals(QObject):
    result = pyqtSignal(object)


# signal class for worker
class WorkerSignals(QObject):
    result = pyqtSignal(object)


# reminder based on time interval thread
class WorkerInterval(QRunnable):
    def __init__(self):
        super(WorkerInterval, self).__init__()
        self.signals = WorkerIntervalSignals()

    @pyqtSlot()
    def run(self):
        z = 0
        y = 0

        ReminderName = SQL.sqlCode.getReminderNameInterval(SQL.x)
        ReminderNotes = SQL.sqlCode.getReminderNotesInterval(SQL.x)

        AlarmInterval = SQL.sqlCode.getReminderIntervalSec(SQL.x)  # Inputted Interval                 SHOULDN'T CHANGE
        SecsInterval = []  # 24hr second
        ReminderInterval = []  # Formatted Interval

        Name = []
        Note = []

        for x in ReminderName:
            Name.append(ReminderName[z])
            z += 1

        for x in ReminderNotes:
            Note.append(ReminderNotes[y])
            y += 1

        def TimeInterval():
            x = datetime.datetime.now()
            a = 0
            i = 0

            IntHour = int(x.strftime("%H"))
            IntMin = int(x.strftime("%M"))
            IntSec = int(x.strftime("%S"))

            Interval = (IntHour * 60 * 60) + (IntMin * 60) + IntSec

            for x in AlarmInterval:
                RealInterval = Interval + AlarmInterval[a]
                SecsInterval.append(RealInterval)
                a += 1

            for x in SecsInterval:
                # Conversion from seconds
                Hours = ((int(SecsInterval[i]) - (int(SecsInterval[i]) % 3600)) / 3600)
                Minutes = ((int(SecsInterval[i]) - (Hours * 3600)) - (
                        (int(SecsInterval[i]) - (Hours * 3600)) % 60)) / 60
                Sec = int(SecsInterval[i]) - (Hours * 3600) - (Minutes * 60)

                # format to match time
                alarm = "{:02d}:{:02d}:{:02d}".format(int(Hours), int(Minutes), int(Sec))

                # Add to array
                ReminderInterval.append(alarm)
                i += 1

        def update(j):
            Hours = ((int(SecsInterval[j]) - (int(SecsInterval[j]) % 3600)) / 3600)
            Minutes = ((int(SecsInterval[j]) - (Hours * 3600)) - ((int(SecsInterval[j]) - (Hours * 3600)) % 60)) / 60
            Sec = int(SecsInterval[j]) - (Hours * 3600) - (Minutes * 60)

            # format to match time
            alarm = "{:02d}:{:02d}:{:02d}".format(int(Hours), int(Minutes), int(Sec))

            # Add to array
            ReminderInterval[j] = alarm

        TimeInterval()

        while True:
            current_time = time.strftime("%H:%M:%S")
            j = 0
            while j != len(ReminderInterval):
                if current_time == ReminderInterval[j]:

                    # (Heading for notification, Subtext for notification) might change
                    reminderInfo = [Name[j], Note[j]]
                    self.signals.result.emit(reminderInfo)

                    # plays reminder sound
                    playsound('LifeLineRingtone.mp3', block=False)

                    # Updates the reminder that had met the conditions to loop
                    UpInterval = SecsInterval[j] + AlarmInterval[j]
                    SecsInterval[j] = UpInterval
                    update(j)
                else:
                    pass
                j += 1


#  Main // Opening the startup screen
#  (i honestly don't know what if __name__ == '__main__': means but it looks important)
if __name__ == '__main__':
    # windows
    app = QApplication(sys.argv)

    # only Startup() is initialized so it starts first
    # initialization of Startup() Class and QtWidgets.QStackedWidget() class

    # instantiation of screens in index order
    startupWindow = Startup()  # index 0
    remindersetupWindow = ReminderSetup()  # index 1
    addnewreminderWindow = AddNewReminder()  # index 2
    usersettingscreenWindow = UserSettingScreen()  # index 3
    settingssavedscreenWindow = SettingsSavedScreen()  # index 4
    mainmenuscreenWindow = MainMenuScreen()  # index 5
    reminderscreenWindow = ReminderScreen()  # index 6

    widget = QtWidgets.QStackedWidget()

    # adding startupWindow as first object in the stack (index 0 is displayed first)
    # stacking of screens in index order
    widget.insertWidget(0, startupWindow)  # index 0
    widget.insertWidget(1, remindersetupWindow)  # index 1
    widget.insertWidget(2, addnewreminderWindow)  # index 2
    widget.insertWidget(3, usersettingscreenWindow)  # index 3
    widget.insertWidget(4, settingssavedscreenWindow)  # index 4
    widget.insertWidget(5, mainmenuscreenWindow)  # index 5
    widget.insertWidget(6, reminderscreenWindow)  # index 6

    # centers opening window + Minimum size
    widget.setMinimumWidth(1000)
    widget.setMinimumHeight(800)

    widget.show()
    app.exec()
