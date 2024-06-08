import requests
from bs4 import BeautifulSoup
from config.core import retrieve_data_from_file

from icecream import ic


def get_mac_address(part_list: list[str], sub_sn: list[str]) -> list[str]:
    mac_list: list[str] = []
    for idx, val in enumerate(part_list):
        if "MAC-AOC-ADDRESS" in val or "MAC-ADDRESS" in val:
            mac = sub_sn[idx]
            dashed_mac = "-".join(x + y for x, y in zip(mac[::2], mac[1::2]))
            mac_list.append(dashed_mac)

    return mac_list


def get_ins_address(mac_list: list[str], ins_path: str) -> list[str]:
    web_link: list[str] = []
    for mac in mac_list:
        ins_file_url = f"{ins_path}/ins-{mac}".lower()
        if requests.get(ins_file_url):
            web_link.append(ins_file_url)
            break
    return web_link


def get_last_line_from_file(screendump: str) -> str:
    respond = requests.get(screendump)
    soup = BeautifulSoup(respond.text, "html.parser")
    lines = soup.get_text().split("\n")
    last_line = [line for line in lines if line != ""][-1]

    return last_line


def get_screendump_helper(ins_file_list: list[str], cburn_addr: str, sn: str, order_num: str) -> tuple[str, dict]:
    screen_dmp = "screen-1.dump"
    no_cburn: dict = {}
    cburn: dict[str] = {}

    for ins_file in ins_file_list:
        mac_addr = (ins_file.partition("ins-"))[2]  # retrieve mac address back from the link
        respond = requests.get(ins_file)
        soup = BeautifulSoup(respond.text, "html.parser")
        lines = soup.get_text().split("\n")
        for line in lines:
            if "DIR=" in line:
                line = line.lower()
                temp = f"{cburn_addr}/{line[5:-1]}/{mac_addr}"  # link to screendump
                valid = requests.get(temp)
                if valid:
                    screendump = f"{temp}/{screen_dmp}"
                    last_line = get_last_line_from_file(screendump)
                    cburn = {"sn": sn, "ord": order_num, "log": last_line}
                else:
                    no_cburn = {"mo": order_num, "serial number": sn}
                
    return cburn, no_cburn


def get_screendump(sn_list: list, assembly_rec_addr: str, ins_addr: str, cburn_addr: str) -> tuple[
                    list[str], list[dict]]:
    cburn_found = []
    cburn_not_found = []
    for sn in sn_list:
        order_num, sub_sn, sub_items, ord_ = retrieve_data_from_file(assembly_rec_addr, sn)

        mac_list = get_mac_address(sub_items, sub_sn)  # find available mac address from the SN
        ins_file_list = get_ins_address(mac_list, ins_addr)  # find available ins file from mac

        cburn_result, no_cburn = get_screendump_helper(ins_file_list, cburn_addr, sn, order_num)
        
        if cburn_result:
            cburn_found.append(cburn_result)
        if no_cburn:
            cburn_not_found.append(no_cburn)
    
    return cburn_found, cburn_not_found
