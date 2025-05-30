# This file contains functions to get firmware information of a device.

import subprocess
from flask import jsonify
from main.cburn_helper import *
from main.tools import check_connectivity


ipmi_tool = "tools/SMCIPMITool_2.28.0/SMCIPMITool.exe"
sum_tool = "tools/SUM_2.14.0/sum.exe"
saa = "tools/SAA_1.1.0/saa.exe"

ipmitool_cmd = {
    "ipmi_ver": " ipmi ver",
    "bios_ver": " bios ver",
}


def execute_command(device, tool, cmd):
    """ Execute a command on the DEVICE using the specified TOOL. """
    ip_address = device["ip_address"]
    passwd = device["password"]
    tool = ipmi_tool if tool == "ipmitool" else saa
    argument = ["-i", ip_address, "-U", "ADMIN", "-P", passwd] if tool == saa else [ip_address, "ADMIN", passwd]
    status = "Started..."

    if ip_address != "NA" and check_connectivity(ip_address):
        try:
            output = subprocess.Popen([tool] +
                                    argument + cmd,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    text=True)
            stdout, stderr = output.communicate(timeout=20)

            return stdout

        except subprocess.SubprocessError as e:
            print(f"Error occurred: {e}")
            return status
    else:
        return status


def sum_bios_ipmi_ver(device, cmd):
    """ Get the firmware version of the DEVICE using SUM tool. """

    if device["ip_address"] != "NA" and check_connectivity(device["ip_address"]):
        try:
            output = subprocess.Popen([sum_tool] +
                                      ["-i", device["ip_address"], "-U", "ADMIN", "-P", device["password"]] +
                                      ["-c", cmd],
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,
                                      text=True)
            stdout, stderr = output.communicate(timeout=20)
            match cmd:
                case "GetBmcInfo":
                    firmware_version = stdout.splitlines()[-4].strip()[21:]
                case "GetBiosInfo":
                    firmware_version = stdout.splitlines()[-2].strip()[36:]
                case _:
                    firmware_version = "NA"
            print(firmware_version)

        except subprocess.SubprocessError as e:
            print(f"Error occurred: {e}")
            return None
    else:
        print("Not connected!")


def get_bios_ipmi_ver(device, cmd):
    """ Get the firmware version of the device using IPMI tool. """
    if device["ip_address"] != "NA" and check_connectivity(device["ip_address"]):
        try:
            output = subprocess.Popen([ipmi_tool] +
                                      [device["ip_address"], " ADMIN ", device["password"], cmd],
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,
                                      text=True)
            stdout, stderr = output.communicate()
            match cmd:
                case " bios ver":
                    f = stdout.split()[-1].replace("\x00", "").strip()
                    firmware_ver = f if f != "" else "NA"
                case " ipmi ver":
                    firmware_ver = stdout.splitlines()[0].split()[-1]
                case _:
                    firmware_ver = "NA"
            return firmware_ver

        except subprocess.SubprocessError as e:
            print(f"Error occurred: {e}")
            return "NA"
    else:
        print("Host Disconnected!")
        return "NA"


def get_firmware_info(firmware_file, cmd):
    """ 
    Get the firmware version of the FILE using SUM tool.
    
    Parameters:
    firmware_file (str): The path to the firmware file.
    cmd (str): The command to get the firmware information (e.g., "GetBmcInfo", "GetBiosInfo", "GetCpldInfo").
    """
    try:
        output = subprocess.Popen([sum_tool] +
                                ["-c", cmd, "--file", firmware_file, "--file_only"],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True)
        stdout, stderr = output.communicate(timeout=20)
        temp = [i.strip() for i in stdout.splitlines()]
        match cmd:
            case "GetBmcInfo":
                firmware_version = next((i[21:] for i in temp if "version" in i), "NA")
                firmware_build_date = next((i[21:] for i in temp if "build date" in i), "NA")
                firmware_image = next((i[21:] for i in temp if "FW image" in i), "NA")
                firmware_signed_key = next((i[17:] for i in temp if "Key" in i), "NA")
            case "GetBiosInfo":
                firmware_version = next((i[36:] for i in temp if "version" in i), "NA")
                firmware_build_date = next((i[36:] for i in temp if "build date" in i), "NA")
                firmware_image = next((i[36:] for i in temp if "FW image" in i), "NA")
                firmware_signed_key = next((i[32:] for i in temp if "Key" in i), "NA")
            case "GetCpldInfo":
                firmware_version = next((i[31:] for i in temp if "version" in i), "NA")
                firmware_image = next((i[31:] for i in temp if "FW image" in i), "NA")
                firmware_signed_key = next((i[27:] for i in temp if "Key" in i), "NA")
            case _:
                firmware_version = "NA"
        firmware = {
            "version": firmware_version,
            "build_date": firmware_build_date,
            "image": firmware_image,
            "signed_key": firmware_signed_key
        }
        return firmware

    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        print(f"Error occurred: {e}")
        return None
