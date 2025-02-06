import subprocess
from app import celery, socketio
from main.tools import check_connectivity


ipmi_tool = "tools/SMCIPMITool_2.28.0/SMCIPMITool.exe"
sum_tool = "tools/SUM_2.14.0/sum.exe"


@celery.task(name="tasks.multiplication")
def multiplication(a, b):
    process = a * b
    test_log = (
        "The Meta Llama 3.3 multilingual large language model (LLM) is a pretrained and "
        "instruction tuned generative model in 70B (text in/text out). The Llama 3.3 instruction "
        "tuned text only model is optimized for multilingual dialogue use cases and outperform "
        "many of the available open source and closed chat models on common industry benchmarks."
    )
    socketio.emit("update_log", {"log": test_log})

    if process:
        status = "Completed"
    else:
        status = "Failed"

    socketio.emit("update_status", {"status": status, "result": process})
    return status


@celery.task(bind=True, name="tasks.update_firmware")
def update_firmware(self, device, cmd):

    self.update_state(state="PROGRESS", meta={"progress": 0})

    if device["ip_address"] != "NA" and check_connectivity(device["ip_address"]):

        command = [
            sum_tool,
            "-i", device["ip_address"],
            "-u", "ADMIN",
            "-p", device["password"],
            "-c", cmd,
            # "--file", fw_file
        ]

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        for line in iter(process.stdout.readline, ''):
            line = line.strip()
            socketio.emit("update_log", {"log": line, "sn": device["system_sn"]})
        process.wait()

        status = "Completed" if process.returncode == 0 else "Failed"

        socketio.emit("update_status", {"status": status})
        return status
