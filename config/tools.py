
import requests, re
from bs4 import BeautifulSoup
from config.core import RackBurn

ip_discover_10 = "http://10.43.251.40/lease"
ip_discover_172 = "http://172.21.0.1/cgi-bin/ipdiscover1.php"


def get_ipmi_info(part_list: list[str], sub_sn: list[str]) -> list[str]:
    """
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
    """
    ipmi_info = get_ipmi_info(part_list, sub_sn)

    mac_list = [i for i in ipmi_info["mac"]]
    pswd_list = [i for i in ipmi_info["pswd"]]
    ipmi_combo = {
            "ip_address": [],
            "username": [],
            "password": []
        }
    for mac, pswd in zip(mac_list, pswd_list):
        payload = {"searchtxt": mac}
        try:
            response = requests.post(ip_discover_10, data=payload, verify=False)
            soup = BeautifulSoup(response.text, "html.parser")
            ip_addr = soup.select_one("body > div > div > div > div.card-body > form > "
                                    "div:nth-child(2) > div > span:nth-child(2) > font > b")
            ipmi_combo["ip_address"].append(ip_addr.text.strip("\n"))
            ipmi_combo["username"].append("ADMIN")
            ipmi_combo["password"].append(pswd)
            ipmi_combo["system_sn"] = [sn for sn in sn_list]
        except Exception as e:
            ipmi_combo["ip_address"].append(None)
            ipmi_combo["username"].append(None)
            ipmi_combo["password"].append(None)
            ipmi_combo["system_sn"] = [sn for sn in sn_list]
            print(f"Error finding the ip address for {mac}: {e}")

    return ipmi_combo


def get_ip_172(part_list: list, sub_sn: list, sn_list: list):
    """
    """
    ipmi_info = get_ipmi_info(part_list, sub_sn)

    mac_list = [i for i in ipmi_info["mac"]]
    pswd_list = [i for i in ipmi_info["pswd"]]
    ipmi_combo = {
            "ip_address": [],
            "username": [],
            "password": []
        }
    
    payload = {
        "address": "7CC2555F4D11",
        "action": "Search"
        }
    response = requests.post(ip_discover_172, data=payload, verify=False)
    soup = BeautifulSoup(response.text, "html.parser")
    tt_tag = soup.find("tt")
    text = tt_tag.get_text(strip=True)
    print(text)
    return response.text