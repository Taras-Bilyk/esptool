from kivy.config import Config
Config.set('graphics', 'resizable', False)
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '600')
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.metrics import dp
import firmware_downloader
import esp_filesystem
import filechooser
import subprocess
import threading
import time
import os

class esptoolApp(App):
    def build(self):
        self.main_layout = FloatLayout()
        self.is_esp_connected = False
        self.is_downloading_finished = 1
        self.pc_folder_path = "none"
        self.imported = 0
        self.global_files = []
        self.global_folders = []
        Clock.schedule_interval(self.check_esp_connection, 0.1)
        Clock.schedule_interval(self.update_log, 0.1)
        Clock.schedule_interval(self.update_install_button, 0.1)
        Clock.schedule_interval(self.update_folder_label, 0.1)
        Clock.schedule_interval(self.update_folder_info, 0.1)
        Clock.schedule_interval(self.update_pc_folder_info, 0.1)
        Clock.schedule_interval(self.update_esp_folder_ui, 0.1)
        Clock.schedule_interval(self.update_put_button, 0.1)
        threading.Thread(target=self.update_esp_folder_info, daemon=True).start()
        #main_screen
        self.main_screen = FloatLayout()
        self.main_screen_firmware_button = Button(text='firmware',
                                                  size_hint = (.2, .08),
                                                  pos_hint = {'x': .01, 'y': .9},
                                                  background_color = (.7, .7, .7, 1),
                                                  font_size = dp(15),
                                                  color = (1, 1, 1, 1),
                                                  on_release = self.go_to_firmware_screen)
        self.main_screen_is_esp_connected_label = Label(text='__________',
                                                  size_hint = (.2, .08),
                                                  pos_hint = {'x': .3, 'y': .9},
                                                  font_size = dp(15),
                                                  color = (1, 1, 1, 1))
        self.main_screen_connect_folder_button = Button(text='connect folder',
                                                  size_hint = (.2, .08),
                                                  pos_hint = {'x': .79, 'y': .9},
                                                  background_color = (.7, .7, .7, 1),
                                                  font_size = dp(15),
                                                  color = (1, 1, 1, 1),
                                                  on_release = self.connect_folder)
        self.main_screen_connected_folder_label = TextInput(text='connected folder: none',
                                                     hint_text='',
                                                     size_hint=(.98, .08),
                                                     pos_hint={'x': .01, 'y': .8},
                                                     background_color=(0, 0, 0, 1),
                                                     foreground_color=(1, 1, 1, .5),
                                                     cursor_color=(0, 0, 0, 1),
                                                     font_size=dp(15),
                                                     multiline=True)
        self.main_screen_folder_label = Label(text='__________',
                                                  size_hint = (.2, .08),
                                                  pos_hint = {'x': .5, 'y': .9},
                                                  font_size = dp(15),
                                                  color = (1, 1, 1, 1))
        self.main_screen_pc_folders_textinput = TextInput(text='__________',
                                                     hint_text='',
                                                     size_hint=(.4, .7),
                                                     pos_hint={'x': .59, 'y': .01},
                                                     background_color=(0, 0, 0, 1),
                                                     foreground_color=(1, 1, 1, 1),
                                                     cursor_color=(0, 0, 0, 1),
                                                     font_size=dp(15),
                                                     multiline=True)
        self.main_screen_esp_folders_textinput = TextInput(text='__________',
                                                     hint_text='',
                                                     size_hint=(.4, .7),
                                                     pos_hint={'x': .02, 'y': .01},
                                                     background_color=(0, 0, 0, 1),
                                                     foreground_color=(1, 1, 1, 1),
                                                     cursor_color=(0, 0, 0, 1),
                                                     font_size=dp(15),
                                                     multiline=True)
        self.main_screen_esp_label = Label(text='esp filesystem\n^^^^^^^^^^',
                                                  size_hint = (.15, .1),
                                                  pos_hint = {'x': .01, 'y': .73},
                                                  font_size = dp(15),
                                                  color = (1, 1, 1, .5))
        self.main_screen_local_label = Label(text='connected folder filesystem\n^^^^^^^^^^',
                                                  size_hint = (.2, .1),
                                                  pos_hint = {'x': .62, 'y': .73},
                                                  font_size = dp(15),
                                                  color = (1, 1, 1, .5))
        self.main_screen_put_button = Button(text='<\n\n<put\n\n<',
                                                  size_hint = (.1, .7),
                                                  pos_hint = {'x': .425, 'y': .01},
                                                  background_color = (.7, .7, .7, 1),
                                                  font_size = dp(15),
                                                  color = (1, 1, 1, 1),
                                                  on_release = self.put_files)
        #firmware_screen
        self.firmware_screen = FloatLayout()
        self.firmware_screen_back_button = Button(text='< back',
                                                  size_hint = (.2, .08),
                                                  pos_hint = {'x': .01, 'y': .9},
                                                  background_color = (.7, .7, .7, 1),
                                                  font_size = dp(15),
                                                  color = (1, 1, 1, 1),
                                                  on_release = self.go_to_main_screen)
        self.firmware_screen_firmvare_available_label = Label(text='firmware available:\nESP32_GENERIC-20251209-v1.27.0.bin',
                                                  size_hint = (.3, .1),
                                                  pos_hint = {'x': .1, 'y': .7},
                                                  font_size = dp(15),
                                                  color = (1, 1, 1, 1))
        self.firmware_screen_firmvare_warning_label = Label(text='only for ESP32 WROOM',
                                                  size_hint = (.1, .1),
                                                  pos_hint = {'x': .15, 'y': .6},
                                                  font_size = dp(15),
                                                  color = (1, 0, 0, 1))
        self.firmware_screen_firmvare_data_warning_label = Label(text='this will erase all your data on your ESP32 device',
                                                  size_hint = (.3, .1),
                                                  pos_hint = {'x': .15, 'y': .5},
                                                  font_size = dp(15),
                                                  color = (1, 0, 0, 1))
        self.firmware_screen_start_updating_button = Button(text='download firmware to esp32',
                                                    size_hint=(.6, .1),
                                                    pos_hint={'x': .01, 'y': .01},
                                                    background_color=(0, 1, 0, 1),
                                                    font_size=dp(15),
                                                    color=(1, 1, 1, 1),
                                                    on_release=self.download_firmware_to_esp)
        self.firmware_screen_log_textinput = TextInput(text='log....',
                                                     hint_text='log...',
                                                     size_hint=(.38, .98),
                                                     pos_hint={'x': .61, 'y': .01},
                                                     background_color=(0, 0, 0, 1),
                                                     foreground_color=(1, 1, 1, .5),
                                                     cursor_color=(1, 0, 0, 1),
                                                     font_size=dp(15),
                                                     multiline=True)
        if self.is_esp_connected:
            self.main_screen_is_esp_connected_label.text = "esp connected"
            self.main_screen_is_esp_connected_label.color = (0, 1, 0, 1)
        else:
            self.main_screen_is_esp_connected_label.text = "esp not connected"
            self.main_screen_is_esp_connected_label.color = (1, 0, 0, 1)
        for widget in [
            self.main_screen_firmware_button,
            self.main_screen_is_esp_connected_label,
            self.main_screen_connected_folder_label,
            self.main_screen_connect_folder_button,
            self.main_screen_folder_label,
            self.main_screen_pc_folders_textinput,
            self.main_screen_esp_folders_textinput,
            self.main_screen_esp_label,
            self.main_screen_local_label,
            self.main_screen_put_button
        ]:
            self.main_screen.add_widget(widget)
        for widget in [
            self.firmware_screen_back_button,
            self.firmware_screen_firmvare_available_label,
            self.firmware_screen_firmvare_warning_label,
            self.firmware_screen_firmvare_data_warning_label,
            self.firmware_screen_start_updating_button,
            self.firmware_screen_log_textinput
        ]:
            self.firmware_screen.add_widget(widget)
        self.main_layout.add_widget(self.main_screen)
        return self.main_layout

    def check_esp_connection(self, dt):
        self.is_esp_connected_command = subprocess.run("ls /dev/tty*", capture_output=True, text=True, shell=True)
        self.is_esp_connected_command_text = self.is_esp_connected_command.stdout.splitlines()
        if "/dev/ttyUSB0" in self.is_esp_connected_command_text:
            if self.is_esp_connected == False:
                firmware_downloader.log_to_return = (str(self.firmware_screen_log_textinput.text) + "\n[CRITICAL] esp connected")
                try:
                    self.main_screen_is_esp_connected_label.text = "esp connected"
                    self.main_screen_is_esp_connected_label.color = (0, 1, 0, 1)
                except Exception:
                    pass
            self.is_esp_connected = True
        else:
            if self.is_esp_connected == True:
                firmware_downloader.log_to_return = (str(self.firmware_screen_log_textinput.text) + "\n[CRITICAL] esp disconnected")
                try:
                    self.main_screen_is_esp_connected_label.text = "esp not connected"
                    self.main_screen_is_esp_connected_label.color = (1, 0, 0, 1)
                except Exception:
                    pass
            self.is_esp_connected = False
    def go_to_firmware_screen(self, instance):
        self.main_layout.remove_widget(self.main_screen)
        self.main_layout.add_widget(self.firmware_screen)
        self.main_screen.remove_widget(self.main_screen_is_esp_connected_label)
        self.firmware_screen.add_widget(self.main_screen_is_esp_connected_label)
    def go_to_main_screen(self, instance):
        self.main_layout.remove_widget(self.firmware_screen)
        self.main_layout.add_widget(self.main_screen)
        self.firmware_screen.remove_widget(self.main_screen_is_esp_connected_label)
        self.main_screen.add_widget(self.main_screen_is_esp_connected_label)
    def download_firmware_to_esp(self, instance):
        self.is_downloading_finished = 0
        threading.Thread(target=self.start_fmtread, daemon=True).start()
    def update_log(self, dt):
        self.firmware_screen_log_textinput.text = str(firmware_downloader.log_to_return)
        if ("[INFO] firmware installed successfully !" in str(firmware_downloader.log_to_return)) or ("[ERROR] error while installing firmware !" in str(firmware_downloader.log_to_return)):
            self.is_downloading_finished = 1
    def start_fmtread(self):
        firmware_downloader.start(str(self.firmware_screen_log_textinput.text))
    def update_install_button(self, dt):
        if self.is_downloading_finished == 1:
            self.firmware_screen_start_updating_button.background_color = (0, 1, 0, 1)
            self.firmware_screen_start_updating_button.disabled = False
            self.firmware_screen_start_updating_button.text = "download firmware to esp32"
        else:
            self.firmware_screen_start_updating_button.background_color = (1, 0, 0, 1)
            self.firmware_screen_start_updating_button.disabled = True
            self.firmware_screen_start_updating_button.text = "downloading... please wait..."
    def connect_folder(self, instance):
        threading.Thread(target=self.open_filechooser, daemon=True).start()
    def open_filechooser(self):
        filechooser.open()
    def update_folder_label(self, dt):
        if self.pc_folder_path == "connected folder: none":
            self.main_screen_folder_label.color = (1, 0, 0, 1)
            self.main_screen_folder_label.text = "folder not connected"
        else:
            self.main_screen_folder_label.color = (0, 1, 0, 1)
            self.main_screen_folder_label.text = "folder connected"
    def update_folder_info(self, dt):
        self.pc_folder_path = filechooser.path_to_return
        self.main_screen_connected_folder_label.text = self.pc_folder_path
    def build_folder_text(self, folder_path, depth=0):
        text = ""
        ignore = ["__pycache__", ".idea", ".vscode"]
        try:
            for x in os.listdir(folder_path):
                full_path = os.path.join(folder_path, x)
                if any(ign in full_path.split(os.sep) for ign in ignore):
                    continue
                prefix = "--" * depth
                if os.path.isdir(full_path):
                    text += prefix + "/ " + x + "\n"
                    self.global_folders.append(full_path)
                    text += self.build_folder_text(full_path, depth + 1)
                elif os.path.isfile(full_path):
                    text += prefix + " " + x + "\n"
                    self.global_files.append(full_path)
        except Exception:
            pass
        return text
    def update_pc_folder_info(self, dt):
        self.global_files = []
        self.global_folders = []
        if self.pc_folder_path != "connected folder: none":
            self.text_to_paste_in_pc_folders_textinput = self.build_folder_text(self.pc_folder_path)
            self.main_screen_pc_folders_textinput.text = self.text_to_paste_in_pc_folders_textinput
            self.files = [os.path.basename(f) for f in self.global_files]
            self.folders = [os.path.basename(f) for f in self.global_folders]
        else:
            self.text_to_paste_in_pc_folders_textinput = "__________"
            self.main_screen_pc_folders_textinput.text = self.text_to_paste_in_pc_folders_textinput
            self.files = []
            self.folders = []
            self.global_files = []
            self.global_folders = []
    def update_esp_folder_info(self):
        while 1:
            if not esp_filesystem.block_btn:
                try:
                    self.file_list_to_show = self.main_screen_esp_folders_textinput.text
                    self.list_for_loop = esp_filesystem.search_files()
                    self.file_list_to_show = ""
                    for x in self.list_for_loop:
                        self.file_list_to_show += "\n"
                        self.file_list_to_show += str(x.replace("/", ""))
                    if self.file_list_to_show == "":
                        self.file_list_to_show = "__________"
                except Exception:
                    pass
            time.sleep(1)
    def update_esp_folder_ui(self, dt):
        try:
            self.main_screen_esp_folders_textinput.text = self.file_list_to_show
        except Exception:
            pass
    def put_files(self, instance):
        threading.Thread(target=self.put_files_thread, daemon=True).start()
    def put_files_thread(self):
        esp_filesystem.put_files(self.global_files, self.pc_folder_path)
    def update_put_button(self, dt):
        if self.is_esp_connected and not esp_filesystem.block_btn and self.pc_folder_path != "connected folder: none":
            self.main_screen_put_button.background_color = (0, 1, 0, .5)
            self.main_screen_put_button.disabled = False
        else:
            self.main_screen_put_button.background_color = (1, 0, 0, 1)
            self.main_screen_put_button.disabled = True

if __name__ == '__main__':
    esptoolApp().run()




