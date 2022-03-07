from sqlalchemy import Column, Integer, String, exists
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

engineReminders = create_engine('sqlite:///reminder.db', echo=True, connect_args={"check_same_thread": False})

Base = declarative_base()

# IMPORTANT!!! WHEN RESETTING THE DATABASE reminders have to be set EXACTLY AS FOLLOWS :
# https://gyazo.com/036a38ed6f03b90e27d9c31d9e9df3cf
# sample

# table columns
# reminder time given in seconds after 00:00
# reminder status = 1 (on); reminder status = 0 (off)
class Reminders(Base):
    __tablename__ = 'Reminders'
    id = Column(Integer, primary_key=True, autoincrement=True)
    reminder_name = Column(String)
    reminder_notes = Column(String)
    reminder_time_secs = Column(Integer)
    reminder_time_interval_secs = Column(Integer)
    reminder_time_based_true = Column(String)
    reminder_time_interval_based_true = Column(String)
    reminder_status = Column(Integer)


class Settings(Base):
    __tablename__ = 'Settings'
    id = Column(Integer, primary_key=True, autoincrement=True)
    setup_done_true = Column(Integer)
    theme = Column(Integer)
    font_size = Column(Integer)


# When new table is to be created uncomment the line below
# Base.metadata.create_all(engineReminders)


class sqlCode():  # export this
    def __init__(self):
        Session = sessionmaker(bind=engineReminders)
        self.session = Session()

    # put setup user settings in database
    def setSettings(self, displaySetupStatus, displayTheme, displayFontSize):
        # if initial setup, insert user submitted settings
        if not (self.session.query(exists().where(Settings.setup_done_true == 1)).scalar()):
            self.session.add_all([Settings(setup_done_true=displaySetupStatus, theme=displayTheme,
                                           font_size=displayFontSize)])
        else:
            # if not initial setup, update settings
            updateQuery = self.session.query(Settings).get(1)
            updateQuery.setup_done_true = displaySetupStatus
            updateQuery.theme = displayTheme
            updateQuery.font_size = displayFontSize

        self.session.commit()

    # Table rows
    def insertNewReminder(self, displayReminderName, displayReminderNote, reminderTimeBasedTrue,
                          reminderTimeIntervalBasedTrue, displayReminderTimeIntervalSecs, displayReminderTimeSecs,
                          displayReminderStatus):  # run sql code

        # does not double add if same name of reminder used
        if not (self.session.query(exists().where(Reminders.reminder_name == displayReminderName)).scalar()):
            self.session.add_all([Reminders(reminder_name=displayReminderName, reminder_notes=displayReminderNote,
                                            reminder_time_secs=displayReminderTimeSecs,
                                            reminder_time_interval_secs=displayReminderTimeIntervalSecs,
                                            reminder_time_based_true=reminderTimeBasedTrue,
                                            reminder_time_interval_based_true=reminderTimeIntervalBasedTrue,
                                            reminder_status=displayReminderStatus
                                            )])
        self.session.commit()

    # Update status of reminder
    def updateReminderStatus(self, displayReminderStatus, displayReminderName):  # run sql code
        tempUpdateObj = self.session.query(Reminders).filter_by(reminder_name=displayReminderName).first()
        tempUpdateObj.reminder_status = displayReminderStatus
        self.session.commit()


    # table queries
    def setTextReminderNames(self):
        resultquery = self.session.query(Reminders.reminder_name).all()

        # resultquery looks like [('Hydrate',), ('Eat',), ('Go outside',), ('Shower',), ('test',)]

        for names in resultquery:
            return str(resultquery)

    # return reminder time (in seconds)
    def getReminderTimeSecsGlobal(self):
        resultquery = self.session.query(Reminders).filter(Reminders.reminder_time_based_true == "TRUE")
        AlarmTime = []
        i = 0

        for time in resultquery:
            AlarmTime.append(time.reminder_time_secs)

        return AlarmTime

    # returns all the reminder names that are based on global time in a list / array
    def getReminderNameGlobal(self):
        resultquery = self.session.query(Reminders).filter(Reminders.reminder_time_based_true == "TRUE")
        ReminderName = []

        for names in resultquery:
            ReminderName.append(names.reminder_name)

        return ReminderName

    # returns all the reminder names that are based on time interval in a list / array
    def getReminderNameInterval(self):
        resultquery = self.session.query(Reminders).filter(Reminders.reminder_time_based_true == "FALSE")
        ReminderName = []

        for names in resultquery:
            ReminderName.append(names.reminder_name)

        return ReminderName

    # return all reminder names in a list / array
    def getReminderNameIndividual(self):
        resultquery = self.session.query(Reminders.reminder_name).all()
        reminderNames = []
        for names in resultquery:
            reminderNames.append(names.reminder_name)
        return reminderNames

    # return all reminder notes list / array
    def getReminderNotesIndividual(self):
        resultquery = self.session.query(Reminders.reminder_notes).all()
        ReminderNotes = []

        for notes in resultquery:
            ReminderNotes.append(notes.reminder_notes)
        return ReminderNotes

    # return all reminder notes based on global time in a list / array
    def getReminderNotesGlobal(self):
        resultquery = self.session.query(Reminders).filter(Reminders.reminder_time_based_true == "TRUE")
        ReminderNotes = []

        for notes in resultquery:
            ReminderNotes.append(notes.reminder_notes)

        return ReminderNotes

    def getReminderNotesInterval(self):
        resultquery = self.session.query(Reminders).filter(Reminders.reminder_time_based_true == "FALSE")
        ReminderNotes = []

        for notes in resultquery:
            ReminderNotes.append(notes.reminder_notes)

        return ReminderNotes

    def getReminderIntervalSec(self):
        ReminderIntervalSec = []
        resultquery = self.session.query(Reminders).filter(Reminders.reminder_time_interval_based_true == "TRUE")

        for reminder in resultquery:
            ReminderIntervalSec.append(reminder.reminder_time_interval_secs)

        return ReminderIntervalSec

    def getReminderIntervalSecAll(self):
        ReminderIntervalSecAll = []
        resultquery = self.session.query(Reminders).all()

        for reminder in resultquery:
            ReminderIntervalSecAll.append(reminder.reminder_time_interval_secs)

        return ReminderIntervalSecAll


    # return all reminder time interval seconds in a list / array
    def getReminderSecAll(self):
        ReminderSec = []
        resultquery = self.session.query(Reminders).all()

        for reminder in resultquery:
            ReminderSec.append(reminder.reminder_time_secs)

        return ReminderSec

    def getTimeBasedTrueArray(self):
        timeBasedTrueArray = []
        resultquery = self.session.query(Reminders).all()

        for reminder in resultquery:
            timeBasedTrueArray.append(reminder.reminder_time_based_true)

        return timeBasedTrueArray

    # return setup status (1 = done, 0 = not done)
    def getSetupDone(self):
        resultquery = str(self.session.query(Settings.setup_done_true).first())
        return resultquery

    # get theme (1=dark, 2=light)
    def getTheme(self):
        resultquery = str(self.session.query(Settings.theme).first())
        return resultquery

    # get theme (1=dark, 2=light)
    def getFontSize(self):
        resultquery = str(self.session.query(Settings.font_size).first())
        return resultquery

    # get amount of reminders
    def getReminderAmount(self):
        resultquery = self.session.query(Reminders).count()
        return resultquery

    # DELETE
    def deleteReminder(self, deleteName):
        resultquery = self.session.query(Reminders).filter(Reminders.reminder_name == deleteName).first()
        self.session.delete(resultquery)
        self.session.commit()


x = sqlCode()  # instantiate the class
