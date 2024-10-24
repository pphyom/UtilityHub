# This file contains functions to get firmware information of a device.

import subprocess
from main.cburn_helper import *
from main.tools import check_connectivity


ipmi_tool = "SMCIPMITool_2.28.0/SMCIPMITool.exe"
sum_tool = "sum_2.14.0/sum.exe"


ipmitool_cmd = {
    "ipmi_ver": " ipmi ver", 
    "bios_ver": " bios ver",
    }


def sum_ipmi_ver(device, cmd):
    """ Get the firmware version of the device using SUM tool. """

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
            firmware_version = ""
            match cmd:
                case "GetBmcInfo":
                    firmware_version = stdout.split("\n")[-4].strip()[21:]
                case "GetBiosInfo":
                    firmware_version = stdout.split("\n")[-2].strip()[36:]
                case _:
                    firmware_version = "NA"
            print(firmware_version)
        
        except subprocess.CalledProcessError as e:
            print(f"Error occured: {e}")
            return None
    else:
        print("Not connected!")


def ipmi_ver(device, cmd):
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
            firmware_ver = "NA"
            match cmd:
                case " bios ver":
                    f = stdout.split()[-1].replace("\x00", "").strip()
                    firmware_ver = f if f != "" else "NA"
                case " ipmi ver":
                    firmware_ver = stdout.split("\n")[0].split()[-1]
                case _:
                    firmware_version = "NA"
            print(firmware_ver)

        except subprocess.CalledProcessError as e:
            print(f"Error occured: {e}")
            return None
    else:
        print("Host Disconnected!")