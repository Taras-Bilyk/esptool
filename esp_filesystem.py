import subprocess
import time

block_btn = 0
search = 1

def search_files():
    if search == 1:
        command = subprocess.run("ampy --port /dev/ttyUSB0 ls", capture_output=True, text=True, shell=True)
        command_text = command.stdout.splitlines()
        return command_text

def put_files(files, basic_repo):
    global block_btn
    block_btn = 1
    time.sleep(0.5)
    file_sum = len(search_files())
    for rm_file in search_files():
        if file_sum > 1:
            if rm_file != "/boot.py":
                manifest_rm = "ampy --port /dev/ttyUSB0 rm " + str(rm_file).replace("/", "")
                command_rm = subprocess.run(manifest_rm, capture_output=True, text=True, shell=True)
                command_rm_text = command_rm.stderr
                time.sleep(0.5)
    for x in files:
        buf = x[(len(basic_repo)+1):]
        manifest = "ampy --port /dev/ttyUSB0 put " + str(x)
        command_put = subprocess.run(manifest, capture_output=True, text=True, shell=True)
        command_put_text = command_put.stderr
        time.sleep(0.5)
    time.sleep(0.5)
    block_btn = 0





