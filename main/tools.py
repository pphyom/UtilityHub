# Description: This file contains the helper functions to support firmware_info and firmware_update files.

import os, dotenv
import requests, socket
from icecream import ic
from bs4 import BeautifulSoup
from main.cburn_helper import *

dotenv.load_dotenv()

# ip_discover_10 = os.getenv("RBURN_SVR40_LEASE")
ip_discover_10 = "http://10.43.251.42/lease"
ip_discover_172 = os.getenv("CBURN_LEASE")


def check_connectivity(host, port=80, timeout=5) -> bool:
    """
    Verify if the host is connected to the server.
    """
    try:
        with socket.create_connection((host, port), timeout):
            return True
    except (socket.timeout, socket.error):
        return False


def get_ipmi_info(part_list: list[str], sub_sn: list[str]) -> list[str]:
    """
    Retrieve the IPMI MAC and Password from the system. 
    """
    ipmi_info = {"mac": "", "pswd": ""}
    for part, ssn in zip(part_list, sub_sn):
        if "MAC-IPMI-ADDRESS" in part:
            ipmi_info["mac"] = ssn
        if "NUM-DEFPWD" in part:
            ipmi_info["pswd"] = ssn

    return ipmi_info


def get_ip_10(part_list: list, sub_sn: list, sn) -> dict:
    """
    SUBNET 10. Discover IP address from connected devices.
    """
    ipmi_info = get_ipmi_info(part_list, sub_sn)
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
        return None


def get_ip_172(part_list: list, sub_sn: list, sn_list: list) -> list[str]:
    """
    SUBNET 172. Discover IP address from connected devices.
    """
    ipmi_info = get_ipmi_info(part_list, sub_sn)

    mac_list = [i for i in ipmi_info["mac"]]
    pswd_list = [i for i in ipmi_info["pswd"]]
    device_info = []
    for mac, pswd, sn in zip(mac_list, pswd_list, sn_list):
        payload = {
            "address": mac,
            "action": "Search"
            }
        try:
            response = requests.post(ip_discover_172, data=payload, verify=False)
            soup = BeautifulSoup(response.text, "html.parser")
            tt_tag = soup.find("tt")
            parsed_text = tt_tag.get_text().split("\n")[-3]
            if parsed_text == "":
                parsed_text = "NA"
            device_combo = {
                "ip_address": parsed_text, 
                "username": "ADMIN",
                "password": pswd,
                "system_sn": sn
                }
            device_info.append(device_combo)
        except Exception as e:
            print(f"Error finding the ip address for {mac}: {e}")
    return device_info