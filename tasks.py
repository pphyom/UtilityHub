import subprocess
from app import celery, socketio
from main.tools import check_connectivity


ipmi_tool = "tools/SMCIPMITool_2.28.0/SMCIPMITool.exe"
sum_tool = "tools/SUM_2.14.0/sum.exe"


@celery.task(bind=True, name="tasks.update_firmware")
def update_firmware(self, device, fw_file, cmd):
    """ Update firmware of a device """

    status = "Started..."
    self.update_state(state="PROGRESS", meta={"progress": 0})

    if device["ip_address"] != "NA" and check_connectivity(device["ip_address"]):

        command = [
            sum_tool,
            "-i", device["ip_address"],
            "-u", "ADMIN",
            "-p", device["password"],
            "-c", cmd,
            "--file", fw_file,
        ]

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        estimated_total_lines = 22
        processed_lines = 0

        for line in iter(process.stdout.readline, ''):
            line = line.strip()
            if line:
                socketio.emit("update_log", {"log": line, "sn": device["system_sn"]})

                # Update progress
                processed_lines += 1
                progress = min(100, int((processed_lines / estimated_total_lines) * 100))
                self.update_state(state="PROGRESS", meta={"progress": progress})

                if progress > 5 and progress < 100:
                    status = "In Progress"

                # Emit progress updates every 5%
                if processed_lines % (estimated_total_lines // 20) == 0:
                    socketio.emit("update_status", {"progress": f"({progress}%)", "sn": device["system_sn"], "status": status})

        process.wait()

        status = "Completed" if process.returncode == 0 else "Failed"
        socketio.emit("update_status", {"status": status, "sn": device["system_sn"]})
        return status
    else:
        status = "Failed"
        socketio.emit("update_status", {"status": status, "sn": device["system_sn"]})
        return status