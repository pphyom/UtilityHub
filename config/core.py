import requests
import pandas as pd
from flask import request
from bs4 import BeautifulSoup
from operator import itemgetter

from icecream import ic


DATA_ = {
        "live_headings": ("Location", "System SN", "Status", "Rack", "Time Gap", "Log"),
        "rburn_headings": ("System SN", "Test Result", "CPU Speed", "CPU Linpack", "DIMM", "GPU Thresholds",
                           "GPU Benchmark", "GPU Linpack", "FDT", "GDT", "GPU FW", "GPU NV"),
        "cburn_headings": ("Serial Number", "Material Order", "Current Stage"),
        "conditions": ("WARNING", "FAIL", "PASS"),
        }


class SPM:
    def __init__(self):
        self.mo_url = "http://super-spm/order/order_detail.asp?orderno="
        self.sn_url = "http://super-spm/order/order_item_detail.asp?serialno="
        self.assembly_rec = ("http://10.2.7.138/order/assembly_record_export.asp?FetchType=OP2&ListType=All&chkSPMWIP"
                    "=on&MONumber=")
        self.cburn_addr = "http://10.43.251.20/burnin"
        self.ins_path = "http://10.43.251.20/instructions"


class RackBurn:
    def __init__(self, url: str):
        self.url = url
        self.rburn_server = "http://10.43.251.40"
        self.lease_ip = "http://10.43.251.40/lease"
    

def user_input() -> list:
    """
    Get data from user input text box.
    param: none
    return: list of input data separated by a white space
    """
    temp = request.form.get("serial_num").split(" ")

    # remove all empty items in the list
    temp = [sn.upper() for sn in temp if sn != "\t" and sn != ""]

    # remove all duplicates and maintain the index order
    input_data: list = []
    [input_data.append(sn) for sn in temp if sn not in input_data]
    
    return input_data


# following functions used in ftu and cburn

def strip_list(list_item: list[str]) -> list:
    """
    Adding sliced contents from the list_item into a new list.
    Usage: strip(a list)
    """
    sub_item_slice: list = []
    for item in list_item:
        sub_item_slice.append(item[14:-5])  # remove extra words

    return sub_item_slice  # return data only


def ord_lookup(item_to_find: str, part_list: list, sub_sn: list):
    """
    Search the ORD number using "NUM-ORD" argument in the part_list.
    If found, take the index of it in the part_list and return the
    same index in the sub_sn list.
    """
    if item_to_find in part_list:
        idx = part_list.index(item_to_find)

        return sub_sn[idx]


def retrieve_data_from_file(addr: str, sn: str):
    """
    Retrieve data from addr + each SN from sn_list. 
    Get the data of the server and scrape them into each param.
    """
    url = addr + sn
    content = pd.read_html(url, header=0)[0]  # Read the web address
    order_num = content["ORDERNUM"]  # Order list
    server_sku = content["SERVERPARTNO"]  # Product list
    part_list = content["SUB-ITEM"]  # Parts list
    sub_sn = content["SUB-SERIAL"]  # Sub Serial for ORD 880

    part_list = strip_list(part_list)  # Slicing unnecessary contents -- fun: strip_list
    sub_sn = strip_list(sub_sn)  # Slicing unnecessary contents -- fun: strip_list
    ord_ = ord_lookup("NUM-ORD", part_list, sub_sn)
    return (str(order_num[0]), sub_sn, part_list, ord_)