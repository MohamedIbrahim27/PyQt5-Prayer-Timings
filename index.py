import os
from PyQt5 import*
from PyQt5.QtWidgets import*
from PyQt5.QtCore import*
from PyQt5.QtGui import*
from os import path
import sys
import urllib.request
import json
import requests
from bs4 import BeautifulSoup
import datetime
from win11toast import toast
import threading
from main import Ui_MainWindow
import win32com.shell.shell as shell
import win32event
import win32api
import winreg

class MainApp(QMainWindow , Ui_MainWindow):
    def __init__(self, parent=None):
        self.toast_shown = False
        super(MainApp,self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.Handel_Ui()
        self.Handel_Button()
        self.tray_icon = QSystemTrayIcon(QIcon('ab.png'), self)
        self.setWindowIcon(QIcon('ab.png'))
        self.tray_icon.setToolTip('My App')
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

        # Create a menu for the tray icon
        self.tray_menu = QMenu(self)
        self.show_action = QAction('Show', self)
        self.hide_action = QAction('Hide', self)
        self.quit_action = QAction('Quit', self)
        self.show_action.triggered.connect(self.show_window)
        self.hide_action.triggered.connect(self.hide_window)
        self.quit_action.triggered.connect(self.quit_app)
        self.tray_menu.addAction(self.show_action)
        self.tray_menu.addAction(self.hide_action)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(self.quit_action)

        # Set the tray menu for the tray icon
        self.tray_icon.setContextMenu(self.tray_menu)

        # Show the window initially
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.tray_icon.show()

    def Handel_Ui(self):
        self.setWindowTitle("مواقيت الصلاه")
        self.update_prayer_timings()
        self.update_current_time()

        
    def Handel_Button(self):
        # self.pushButton.clicked.connect(self.Download)
        pass
    def get_prayer_timings(self):
        response = requests.get('https://www.islamicfinder.org/world/egypt/42618040/mansoura-prayer-times/?language=ar')
        soup = BeautifulSoup(response.text, 'lxml')
        p_titles = soup.find_all('div', {'class': 'prayerTiles'})

        prayer_timings = {}
        for prd in p_titles:
            prayername = prd.find('span', {'class': 'prayername'}).text
            prayertime = prd.find('span', {'class': 'prayertime'}).text
            format_str = '%I:%M %p'  # Format for parsing the time string
            prayer_datetime = datetime.datetime.strptime(prayertime, format_str)
            prayer_datetime += datetime.timedelta(hours=1)

            # Convert the adjusted datetime object back to a formatted time string
            adjusted_prayer_time = prayer_datetime.strftime(format_str)

            prayer_timings[prayername] = adjusted_prayer_time

        return prayer_timings

    def update_prayer_timings(self):
        prayer_timings = self.get_prayer_timings() 
        self.label_1.setText(prayer_timings["الفجر"]) 
        self.label_8.setText(prayer_timings["الشروق"])
        self.label_13.setText(prayer_timings["الظهر"])
        self.label_12.setText(prayer_timings["العصر"])
        self.label_11.setText(prayer_timings["المغرب"])
        self.label_14.setText(prayer_timings["العشاء"])
        
    def update_current_time(self):
        current_time_app = datetime.datetime.now().strftime('%I:%M:%S %p')
        self.label_9.setText(current_time_app)
        
        current_time = datetime.datetime.now().strftime('%I:%M %p')
        #-------   الفجر -------
        fajr_time_str = self.label_1.text()
        time_difference = self.calculate_time_difference(current_time, fajr_time_str)
        self.label_24.setText(time_difference)
        #-------   الشروق -------
        b_time_str = self.label_8.text()
        time_difference = self.calculate_time_difference(current_time, b_time_str)
        self.label_21.setText(time_difference)
        #-------   الظهر -------
        c_time_str = self.label_13.text()
        time_difference = self.calculate_time_difference(current_time, c_time_str)
        self.label_23.setText(time_difference)
        #-------   العصر -------
        d_time_str = self.label_12.text()
        time_difference = self.calculate_time_difference(current_time, d_time_str)
        self.label_22.setText(time_difference)
        #-------   المغرب -------
        e_time_str = self.label_11.text()
        time_difference = self.calculate_time_difference(current_time, e_time_str)
        self.label_25.setText(time_difference)
        #-------   العشاء -------
        f_time_str = self.label_14.text()
        time_difference = self.calculate_time_difference(current_time, f_time_str)
        self.label_26.setText(time_difference)
        
        QTimer.singleShot(1000, self.update_current_time)

    def calculate_time_difference(self, time1_str, time2_str):
        format_str = '%I:%M %p'
        time1 = datetime.datetime.strptime(time1_str, format_str)
        time2 = datetime.datetime.strptime(time2_str, format_str)

        if time1 > time2:
            time_difference = 'تمت الصلاة'
        elif abs(time1 - time2) < datetime.timedelta(seconds=60):
            if not self.toast_shown:
                self.toast_shown = True
                threading.Thread(target=self.show_notification).start()
            self.show()
            time_difference = 'الصلاة الأن'
        else:
            time_difference = time2 - time1
        return str(time_difference)
    def show_notification(self):
        toast('حان الأن موعد الصلاة', 'اذهب الي صلاتك يا صديقي ! 🤍')
    def show_window(self):
        self.show()

    def hide_window(self):
        self.hide()

    def quit_app(self):
        self.tray_icon.hide()
        QApplication.quit()

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_window()
    def closeEvent(self, event):
        event.ignore()  # Ignore the close event to prevent the window from being closed
        self.hide()
CONFIG_FILE = "config.json"
def create_registry_entry():
    # Get the path of the executable file of your application
    exe_path = os.path.abspath(sys.argv[0])

    # Key where we'll add the registry entry for startup
    key = r"Software\Microsoft\Windows\CurrentVersion\Run"

    # Get the HKEY_CURRENT_USER registry key
    hkey = winreg.HKEY_CURRENT_USER

    # Create or open the key
    try:
        key_handle = winreg.OpenKey(hkey, key, 0, winreg.KEY_SET_VALUE)
    except FileNotFoundError:
        key_handle = winreg.CreateKey(hkey, key)

    # Set the registry value to add the startup entry
    winreg.SetValueEx(key_handle, "MyAppStartup", 0, winreg.REG_SZ, exe_path)

    # Close the registry key handle
    winreg.CloseKey(key_handle)

def is_admin():
    try:
        return shell.IsUserAnAdmin()
    except:
        return False
def main():
    if is_admin():
        create_registry_entry()
        print("Startup registry entry added successfully.")
        
        # Store the flag in the configuration file
        config = {"admin_flag": True}
        with open(CONFIG_FILE, "w") as file:
            json.dump(config, file)
    else:
        # Check if the app has been run with admin privileges before
        try:
            with open(CONFIG_FILE, "r") as file:
                config = json.load(file)
            if config.get("admin_flag", False):
                # If the admin_flag is True, skip the admin privilege check
                print("Running without admin privilege.")
            else:
                # Re-run the script as an administrator to create the registry entry
                print("Please run the script as an administrator.")
                shell.ShellExecuteEx(lpVerb="runas", lpFile=sys.executable, lpParameters=" ".join(sys.argv))
                win32event.WaitForSingleObject(win32api.GetCurrentProcess(), -1)
        except FileNotFoundError:
            # If the config file doesn't exist, create it with admin_flag set to False
            config = {"admin_flag": False}
            with open(CONFIG_FILE, "w") as file:
                json.dump(config, file)
            # Re-run the script as an administrator to create the registry entry
            print("Please run the script as an administrator.")
            shell.ShellExecuteEx(lpVerb="runas", lpFile=sys.executable, lpParameters=" ".join(sys.argv))
            win32event.WaitForSingleObject(win32api.GetCurrentProcess(), -1)
    app= QApplication(sys.argv)
    window= MainApp()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()