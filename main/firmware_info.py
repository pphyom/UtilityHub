# This file contains functions to get firmware information of a device.

import subprocess
from main.cburn_helper import *
from main.tools import check_connectivity

ipmi_tool = "tools/SMCIPMITool_2.28.0/SMCIPMITool.exe"
sum_tool = "tools/SUM_2.14.0/sum.exe"

ipmitool_cmd = {
    "ipmi_ver": " ipmi ver",
    "bios_ver": " bios ver",
}


def sum_bios_ipmi_ver(device, cmd):
    """ Get the firmware version of the DEVICE using SUM tool. """

    if device["ip_address"] != "NA" or check_connectivity(device["ip_address"]):
        try:
            output = subprocess.Popen([sum_tool] +
                                      ["-i", device["ip_address"], "-U", "ADMIN", "-P", device["password"]] +
                                      ["-c", cmd],
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,
                                      text=True)
            output.poll()
            stdout, stderr = output.communicate()
            match cmd:
                case "GetBmcInfo":
                    firmware_version = stdout.split("\n")[-4].strip()[21:]
                case "GetBiosInfo":
                    firmware_version = stdout.split("\n")[-2].strip()[36:]
                case _:
                    firmware_version = "NA"
            print(firmware_version)

        except subprocess.CalledProcessError as e:
            print(f"Error occurred: {e}")
            return None
    else:
        print("Not connected!")


def get_bios_ipmi_ver(device, cmd):
    """ Get the firmware version of the device using IPMI tool. """

    if device["ip_address"] != "NA" or check_connectivity(device["ip_address"]):
        try:
            output = subprocess.Popen([ipmi_tool] +
                                      [device["ip_address"], " ADMIN ", device["password"], cmd],
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,
                                      text=True)
            output.poll()
            stdout, stderr = output.communicate()
            match cmd:
                case " bios ver":
                    f = stdout.split()[-1].replace("\x00", "").strip()
                    firmware_ver = f if f != "" else "NA"
                case " ipmi ver":
                    firmware_ver = stdout.split("\n")[0].split()[-1]
                case _:
                    firmware_ver = "NA"
            return firmware_ver

        except subprocess.CalledProcessError as e:
            print(f"Error occurred: {e}")
            return "NA"
    else:
        print("Host Disconnected!")
        return "NA"


def get_firmware_info(firmware_file, cmd):
    """ Get the firmware version of the FILE using SUM tool. """
    output = subprocess.Popen([sum_tool] +
                            ["-c", cmd, "--file", firmware_file, "--file_only"],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True)
    output.poll()
    stdout, stderr = output.communicate()
    firmware_build_date = "NA"
    temp = [i.strip() for i in stdout.split("\n")]
    match cmd:
        case "GetBmcInfo":
            firmware_version = [i[21:] for i in temp if "version" in i][0]
            firmware_build_date = [i[21:] for i in temp if "build date" in i][0]
        case "GetBiosInfo":
            # firmware_version = [i.strip()[36:] for i in stdout.split("\n") if "version" in i][0]
            firmware_version = [i[36:] for i in temp if "version" in i][0]
            firmware_build_date = [i[36:] for i in temp if "build date" in i][0]
        case "GetCpldInfo":
            firmware_version = [i[31:] for i in temp if "version" in i][0]
        case _:
            firmware_version = "NA"
    firmware = {
        "version": firmware_version,
        "build_date": firmware_build_date
    }
    return firmware


def update_firmware(device, cmd):
    if device["ip_address"] != "NA" or check_connectivity(device["ip_address"]):
        try:
            output = subprocess.run([sum_tool] + ["-i", device["ip_address"], "-u", "ADMIN", "-p", device["password"]] + ["-c", cmd], capture_output=True, text=True)
            return output.stdout

        except subprocess.CalledProcessError as e:
            print(f"Error occurred: {e}")
            return None
    else:
        print("Not connected!")