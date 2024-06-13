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


def get_each_line_from_page(in_file: str) -> list[str]:
    respond = requests.get(in_file)
    soup = BeautifulSoup(respond.text, "html.parser")
    lines = soup.get_text().split("\n")

    return lines


def get_last_line_from_file(in_file: str) -> str:
    lines = get_each_line_from_page(in_file)
    last_line = [line for line in lines if line != ""][-1]

    return last_line


def get_cburn_path(mac_list: list[str], ins_path: str, cburn_addr: str) -> dict[list, list]:
    

    temp = []

    cburn_path = dict(screendump = [], ins_to_sn = [])
    screen_dump = "/screen-1.dump"

    for mac in mac_list:
        ins_file_url = f"{ins_path}/ins-{mac}".lower() # get instruction file path
        lines = get_each_line_from_page(ins_file_url)
        paths_to_screendump = [(f"{cburn_addr}/{line[5:-1]}/{mac}").lower() for line in lines if "DIR=" in line]

        for path in paths_to_screendump:
            if requests.get(path):
                cburn_path = {"screendump": (path + screen_dump), "ins_to_sn": (path + f"/ins-{mac}")}
                # cburn_path["screendump"].append(path + screen_dump)
                # cburn_path["ins_to_sn"].append(path + f"/ins-{mac}")
                temp.append(cburn_path)

    return temp


def screendump(ins_path: str, cburn_addr: str, mac_list: list[str], mo: str):
    

    final = []

    # final = dict(node_sn = [], log = [], order_num = [])
    cburn_path = get_cburn_path(mac_list, ins_path, cburn_addr)

    for i in cburn_path:
        last_line = get_last_line_from_file(i["screendump"])
        lines = get_each_line_from_page(i["ins_to_sn"])
        for line in lines:
            if line.startswith("SSN"):
                node_sn = line[5:-1]

                temp = {"sn": node_sn, "log": last_line, "ord": mo}
                final.append(temp)


    # for elem in cburn_path.get("ins_to_sn"):
    #     lines = get_each_line_from_page(elem)
    #     for line in lines:
    #         if line.startswith("SSN"):
    #             final["node_sn"].append(line[5:-1])

    # for elem in cburn_path.get("screendump"):
    #     last_line = get_last_line_from_file(elem)
    #     final["log"].append(last_line)
    #     final["order_num"].append(mo)

    return final


def screendump_wrapper(sn_list: list, assembly_rec_addr: str, ins_path: str, cburn_addr: str):

    final: list = []
    for sn in sn_list:
        order_num, sub_sn, part_list, ord_ = retrieve_data_from_file(assembly_rec_addr, sn)
        mac_list = get_mac_address(part_list, sub_sn)  # find available mac address from the SN
        temp = screendump(ins_path, cburn_addr, mac_list, order_num)
        for i in temp:
            final.append(i)

    return final
