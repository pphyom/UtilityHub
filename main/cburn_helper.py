import requests
import asyncio
from requests import HTTPError
from bs4 import BeautifulSoup
from main.core import SPM
from urllib.error import HTTPError


spm = SPM()


def multinode_check(part_list: list) -> bool:
    # check if the system is multinode
    is_multinode = False
    for part in part_list:
        if "NODEID" in part:
            is_multinode = True

    return is_multinode


def get_each_line_from_page(in_file: str) -> list[str]:
    respond = requests.get(in_file)
    soup = BeautifulSoup(respond.text, "html.parser")
    lines = soup.get_text().split("\n")

    return lines


def get_last_line_from_file(in_file: str) -> str:
    lines = get_each_line_from_page(in_file)
    last_line = [line for line in lines if line != ""][-1]

    return last_line


def get_cburn_path(mac_list: list[str], ins_path: str, cburn_addr: str) -> list[dict[str, str]]:
    
    temp = []
    cburn_path = dict(screendump=[], ins_to_sn=[])
    screen_dump = "/screen-1.dump"

    for mac in mac_list:
        ins_file_url = f"{ins_path}/ins-{mac}".lower()  # get instruction file path

        lines = get_each_line_from_page(ins_file_url)
        paths_to_screendump = [f"{cburn_addr}/{line[5:-1]}/{mac}".lower() for line in lines if "DIR=" in line]

        for path in paths_to_screendump:
            if requests.get(path):
                cburn_path = {"screendump": (path + screen_dump), "ins_to_sn": (path + f"/ins-{mac}")}
                temp.append(cburn_path)

    return temp


def screendump(ins_path: str, cburn_addr: str, mac_list: list[str]):
    
    final = []
    node_sn, order_num = "", ""
    cburn_path = get_cburn_path(mac_list, ins_path, cburn_addr)

    for x in cburn_path:
        last_line = get_last_line_from_file(x["screendump"])
        lines = get_each_line_from_page(x["ins_to_sn"])
        for line in lines:
            if line.startswith("SSN"):
                node_sn = line[5:-1]
            if line.startswith("ORDNUM"):
                order_num = line[8:-1]
        temp = {"sn": node_sn, "log": last_line, "ord": order_num}
        final.append(temp)

    return final


def screendump_wrapper(sn_list: list, assembly_rec_addr: str, ins_path: str, cburn_addr: str):
    try:
        final: list = []
        
        out_file = asyncio.run(spm.retrieve_data_from_file(assembly_rec_addr, sn_list))
        mac_list = get_mac_address(out_file["part_list"], out_file["sub_sn"])  # find available mac address from the SN
        temp = screendump(ins_path, cburn_addr, mac_list)

        for elem in temp:
            final.append(elem)
        
        return final
    
    except HTTPError as e:
        match e.code:
            case 500:
                print("Internal Server Error. Server cannot be found!")


def get_mac_address(part_list: list[str], sub_sn: list[str]) -> list[str]:
    """
    """
    mac_addresses = [
        ssn[idx] for part, ssn in zip(part_list, sub_sn) 
        for idx, val in enumerate(part)
        if "MAC-ADDRESS" in val or "MAC-AOC-ADDRESS" in val
    ]
    mac_list = [
        "-".join(x + y for x, y in zip(mac_addr[::2], mac_addr[1::2])).lower() 
        for mac_addr in mac_addresses
    ]

    return mac_list
