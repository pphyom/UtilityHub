# Description: This file contains the helper functions to support firmware_info and firmware_update files.

import dotenv
import os
import socket
from flask import jsonify
from main.cburn_helper import *
from main.ftu_helper import *
from main.core import *

ftu = FTU()
spm = SPM()
dotenv.load_dotenv()

ip_discover_10 = os.getenv("RBURN_SVR40_LEASE")
ip_discover_172 = os.getenv("CBURN_LEASE")


def check_connectivity(host, port=80, timeout=5) -> bool:
    """ Verify if the host is connected to the server. """
    try:
        with socket.create_connection((host, port), timeout):
            return True
    except (socket.timeout, socket.error):
        return False


def get_spm_bmc_info(part_list: list[str], sub_sn: list[str]) -> dict[str, str]:
    """ Retrieve the IPMI MAC and Password from the system. """
    ipmi_info = {"mac": "", "pswd": ""}
    for part, ssn in zip(part_list, sub_sn):
        if "MAC-IPMI-ADDRESS" in part:
            ipmi_info["mac"] = ssn
        if "NUM-DEFPWD" in part:
            ipmi_info["pswd"] = ssn

    return ipmi_info


def get_ip_10(part_list: list, sub_sn: list, sn) -> dict:
    """ SUBNET 10. Discover IP address from connected devices. """
    ipmi_info = get_spm_bmc_info(part_list, sub_sn)
    mac = ipmi_info["mac"]
    pswd = ipmi_info["pswd"]
    payload = {"searchtxt": mac}
    try:
        response = requests.post(ip_discover_10, data=payload, verify=False)
        soup = BeautifulSoup(response.text, "html.parser")
        ip_addr_raw = soup.select_one("body > div > div > div > div.card-body > form > "
                                      "div:nth-child(2) > div > span:nth-child(2) > font > b")
        ip_addr = ip_addr_raw.text.strip("\n")
        if ip_addr == "":
            ip_addr = "NA"
        device_info = {
            "ip_address": ip_addr,
            "username": "ADMIN",
            "password": pswd,
            "system_sn": sn
        }
        return device_info
    except Exception as e:
        print(f"Error finding the ip address for {mac}: {e}")
        device_info = {
            "ip_address": "NA",
            "username": "ADMIN",
            "password": pswd,
            "system_sn": sn
        }
        return device_info


def get_ip_172(part_list: list, sub_sn: list, sn) -> dict:
    """ SUBNET 172. Discover IP address from connected devices. """
    ipmi_info = get_spm_bmc_info(part_list, sub_sn)
    mac = ipmi_info["mac"]
    pswd = ipmi_info["pswd"]
    payload = {
        "address": mac,
        "action": "Search"
    }
    try:
        response = requests.post(ip_discover_172, data=payload, verify=False)
        soup = BeautifulSoup(response.text, "html.parser")
        tt_tag = soup.find("tt")
        ip_addr = tt_tag.get_text().split("\n")[-3]
        if ip_addr == "":
            ip_addr = "NA"
        device_info = {
            "ip_address": ip_addr,
            "username": "ADMIN",
            "password": pswd,
            "system_sn": sn
        }
        return device_info
    except Exception as e:
        print(f"Error finding the ip address for {mac}: {e}")
        device_info = {
            "ip_address": "NA",
            "username": "ADMIN",
            "password": pswd,
            "system_sn": sn
        }
        return device_info


def get_bmc_info_helper(sn_list: list) -> list:
    """ Filter the data based on the user input. """
    try:
        sys_list = []
        for sn in sn_list:
            outfile = asyncio.run(spm.retrieve_data_from_file(spm.assembly_rec, sn))
            client_connection = request.remote_addr
            if client_connection.startswith("10"):
                device_info = get_ip_10(outfile["part_list"], outfile["sub_sn"], sn)
            else:
                device_info = get_ip_172(outfile["part_list"], outfile["sub_sn"], sn)

            sys_list.append(device_info)
        return sys_list
    except Exception as e:
        return jsonify({"error": str(e)})
