
import requests
from bs4 import BeautifulSoup
from config.core import RackBurn
from config.cburn_helper import *

ip_discover_10 = "http://10.43.251.40/lease"
ip_discover_172 = "http://172.21.0.1/cgi-bin/ipdiscover1.php"


def get_ipmi_info(part_list: list[str], sub_sn: list[str]) -> list[str]:
    """
    Retrieve the IPMI MAC and Password from the system. 
    """
    ipmi_info = {"mac": [], "pswd": []}
    for part, ssn in zip(part_list, sub_sn):
        for idx, val in enumerate(part):
            if "MAC-IPMI-ADDRESS" in val:
                ipmi_info["mac"].append(ssn[idx])
            if "NUM-DEFPWD" in val:
                ipmi_info["pswd"].append(ssn[idx])

    return ipmi_info


def get_ip_addr(part_list: list, sub_sn: list, sn_list: list):
    """
    Discover IP address from connected devices. 
    """
    ipmi_info = get_ipmi_info(part_list, sub_sn)
    mac_list = [i for i in ipmi_info["mac"]]
    pswd_list = [i for i in ipmi_info["pswd"]]
    device_info = []
    for mac, pswd, sn in zip(mac_list, pswd_list, sn_list):
        payload = {"searchtxt": mac}
        try:
            response = requests.post(ip_discover_10, data=payload, verify=False)
            soup = BeautifulSoup(response.text, "html.parser")
            ip_addr_raw = soup.select_one("body > div > div > div > div.card-body > form > "
                                    "div:nth-child(2) > div > span:nth-child(2) > font > b")
            ip_addr = ip_addr_raw.text.strip("\n")
            if ip_addr == "":
                ip_addr = "NA"
            device_combo = {
                "ip_address": ip_addr,
                "username": "ADMIN",
                "password": pswd,
                "system_sn": sn
            }
            device_info.append(device_combo)
        except Exception as e:
            print(f"Error finding the ip address for {mac}: {e}")

    return device_info
