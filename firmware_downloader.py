import esp_filesystem
import subprocess
import time

log_to_return = None

def start(log):
    time.sleep(0.5)
    esp_filesystem.search = 0
    global log_to_return
    log_to_return = log
    #installing esptool
    log_to_return = str(log_to_return) + "\n" + "[INFO] installing esptool..."
    subprocess.run("pip install esptool", capture_output=True, text=True, shell=True)
    command = subprocess.run("pip install esptool", capture_output=True, text=True, shell=True)
    command_text = command.stdout
    if "already satisfied" in command_text:
        log_to_return = str(log_to_return) + "\n" + "[INFO] esptool installed !"
    else:
        log_to_return = str(log_to_return) + "\n" + "[ERROR] esptool not installed !"
    #searching esp
    log_to_return = str(log_to_return) + "\n" + "[INFO] searching esp on ports..."
    command = subprocess.run("ls /dev/tty*", capture_output=True, text=True, shell=True)
    command_text = command.stdout
    if "/dev/ttyUSB0" in command_text:
        log_to_return = str(log_to_return) + "\n" + "[INFO] esp found on USB0 !"
    else:
        log_to_return = str(log_to_return) + "\n" + "[ERROR] esp not found !"
    #checking firmware
    log_to_return = str(log_to_return) + "\n" + "[INFO] checking firmware..."
    command = subprocess.run("cd firmware && ls", capture_output=True, text=True, shell=True)
    command_text = command.stdout
    if "ESP32_GENERIC-20251209-v1.27.0.bin" in command_text:
        log_to_return = str(log_to_return) + "\n" + "[INFO] firmware found !"
    else:
        log_to_return = str(log_to_return) + "\n" + "[ERROR] firmware not found !"
    #erase_flash
    log_to_return = str(log_to_return) + "\n" + "[INFO] erasing esp flash..." + "\n" + "[INFO] please wait (it can take a while)..."
    command = subprocess.run("esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash", capture_output=True, text=True, shell=True)
    command_text = command.stdout
    if "completed successfully" in command_text:
        log_to_return = str(log_to_return) + "\n" + "[INFO] esp erase completed successfully !"
    else:
        log_to_return = str(log_to_return) + "\n" + "[ERROR] error while erasing esp !"
    #installing_firmware
    log_to_return = str(log_to_return) + "\n" + "[INFO] installing firmware..." + "\n" + "[INFO] please wait (it can take about 110 seconds)..."
    command = subprocess.run("cd firmware && esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 ESP32_GENERIC-20251209-v1.27.0.bin", capture_output=True, text=True, shell=True)
    command_text = command.stdout
    if "Hash of data verified" in command_text:
        log_to_return = str(log_to_return) + "\n" + "[INFO] firmware installed successfully !"
    else:
        log_to_return = str(log_to_return) + "\n" + "[ERROR] error while installing firmware !"
    time.sleep(0.5)
    esp_filesystem.search = 1



