import requests
from requests import HTTPError
from bs4 import BeautifulSoup
from config.core import retrieve_data_from_file

from icecream import ic


def get_mac_address(part_list: list[str], sub_sn: list[str]) -> list[str]: 
    mac = [sub_sn[idx] for idx, val in enumerate(part_list) if "MAC-ADDRESS" in val or "MAC-AOC-ADDRESS" in val]
    mac_list = ["-".join(x + y for x, y in zip(mac_addr[::2], mac_addr[1::2])).lower() for mac_addr in mac]

    return mac_list


def multinode_check(part_list: list) -> bool:
    # check if the system is multinode
    is_multinode = False
    for part in part_list:
        if "NODEID" in part:
            is_multinode = True

    return is_multinode


def get_cburn_path(mac_list: list[str], ins_path: str, cburn_addr: str):
    
    final = dict(screendump = [], ins_to_sn = [])
    # screendump: list[str] = []
    screen_dump = "/screen-1.dump"

    for mac in mac_list:
        ins_file_url = f"{ins_path}/ins-{mac}".lower() # get instruction file path
        respond = requests.get(ins_file_url)
        soup = BeautifulSoup(respond.text, "html.parser")
        lines = soup.get_text().split("\n")
        paths_to_screendump = [(f"{cburn_addr}/{line[5:-1]}/{mac}").lower() for line in lines if "DIR=" in line]
        # active_nodes = [path for path in paths_to_screendump if requests.get(path)]

        for path in paths_to_screendump:
            if requests.get(path):
                final["screendump"].append(path + screen_dump)
                final["ins_to_sn"].append(path + f"/ins-{mac}")

    return final


def test(mac_list: list[str], ins_path: str, cburn_addr: str, part_list: list[str], sn: str):
    screen_dump = "/screen-1.dump"
    is_multinode = multinode_check(part_list)
    screendump = get_cburn_path(mac_list, ins_path, cburn_addr)
    # last_line = [(get_last_line_from_file(path)) for path in screendump]
    # serial = [f"{path}/ins-{mac}" for path, mac in mac_list]


    # for path in cburn_path:




    return screendump





def get_ins_address(mac_list: list[str], ins_path: str, cburn_addr: str, 
                    sn: str, order_num: str):
    screen_dmp = "screen-1.dump"
    node_id_list = []
    no_cburn: dict[str] = {}
    cburn: dict[str] = {"sn": [], "ord": [], "log": []}
        
    for mac in mac_list:
        # get instruction file path
        ins_file_url = f"{ins_path}/ins-{mac}".lower()
        try:
            respond = requests.get(ins_file_url)
            soup = BeautifulSoup(respond.text, "html.parser")
            lines = soup.get_text().split("\n")
            for line in lines:

                # get the node ID
                if line.startswith("SSN"):
                    node_id_list.append(line[5:-1])

                # get the cburn path
                if "DIR=" in line:
                    temp = f"{cburn_addr}/{line.lower()[5:-1]}/{mac.lower()}"  # link to screendump
                    # ic(temp)




                    valid = requests.get(temp)
                    if valid:
                        screendump = f"{temp}/{screen_dmp}"
                        last_line = get_last_line_from_file(screendump)      

                        cburn["sn"].append(sn)
                        cburn["ord"].append(order_num)
                        cburn["log"].append(last_line)

                    else:
                        no_cburn = {"mo": order_num, "serial number": sn}
        except HTTPError:
            return False


    return cburn, no_cburn


def get_last_line_from_file(screendump: str) -> str:
    respond = requests.get(screendump)
    soup = BeautifulSoup(respond.text, "html.parser")
    lines = soup.get_text().split("\n")
    last_line = [line for line in lines if line != ""][-1]

    return last_line


def get_screendump_helper(ins_file_list: list[str], cburn_addr: str, sn: str, order_num: str) -> tuple[str, dict]:
    screen_dmp = "screen-1.dump"
    no_cburn: dict[str] = {}
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
        order_num, sub_sn, part_list, ord_ = retrieve_data_from_file(assembly_rec_addr, sn)

        mac_list = get_mac_address(part_list, sub_sn)  # find available mac address from the SN

        
        temp = test(mac_list, ins_addr, cburn_addr, part_list, sn)
        ic(temp)

    
    return cburn_found, cburn_not_found
