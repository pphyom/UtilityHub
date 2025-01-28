import subprocess
from app import celery, socketio
from main.tools import check_connectivity


ipmi_tool = "tools/SMCIPMITool_2.28.0/SMCIPMITool.exe"
sum_tool = "tools/SUM_2.14.0/sum.exe"


@celery.task(bind=True, name="tasks.update_firmware")
def update_firmware(self, device, fw_file, cmd):

    self.update_state(state="PROGRESS", meta={"progress": 0})

    if device["ip_address"] != "NA" and check_connectivity(device["ip_address"]):

        command = [
            sum_tool,
            "-i", device["ip_address"],
            "-u", "ADMIN",
            "-p", device["password"],
            "-c", cmd,
            "--file", fw_file
        ]

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print("PROCESS: ", process)
        for line in iter(process.stdout.readline, ''):
            line = line.strip()
            socketio.emit("update_log", {"log": line}, broadcast=True)
            print(line)
        process.wait()
        print("RETURN CODE: ", process.returncode)

        if process.returncode == 0:
            status = "Completed"
        else:
            status = "Failed"

        socketio.emit("update_status", {"status": status}, broadcast=True)
        return status
