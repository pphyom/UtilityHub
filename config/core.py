import asyncio
import aiohttp
import requests
import pandas as pd
from flask import request
from bs4 import BeautifulSoup
from io import StringIO
from operator import itemgetter
from threading import Thread, Event

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
        self.scanlog = "http://10.2.7.138/order/export_scanlog.asp?print=Export+scan+log&ssn="
        self.ftu_addr = "http://10.43.251.22/prodfile/FTU/"
        self.ftu_b23 = "http://172.21.100.1/prodfile/FTU/"
        self.cburn_addr = "http://10.43.251.20/burnin"
        self.ins_path = "http://10.43.251.20/instructions"

    async def fetch(self, session, url):
        async with session.get(url) as response:
            return await response.text()
        
    async def retrieve_data_from_file(self, addr, sn_list):
        """
        
        """
        assembly_data = {"order_num": [], "sub_sn": [], "part_list": [], "ord_": []}
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch(session, (addr + sn)) for sn in sn_list]
            responses = await asyncio.gather(*tasks)

        for elem, response in zip(sn_list, responses):
            if isinstance(response, Exception):
                print(f"Error while getting data for {elem}: {response}")
                continue

            content = pd.read_html(StringIO(response), header=0)[0]
            order_num = content["ORDERNUM"]
            server_sku = content["SERVERPARTNO"]
            part_list = content["SUB-ITEM"]
            sub_sn = content["SUB-SERIAL"]

            part_list = self.strip_list(part_list)
            sub_sn = self.strip_list(sub_sn)
            ord_ = self.ord_lookup("NUM-ORD", part_list, sub_sn)

            assembly_data["order_num"].append(str(order_num.iloc[0]))  # Assuming there's always at least one element
            assembly_data["sub_sn"].append(sub_sn)
            assembly_data['part_list'].append(part_list)
            assembly_data["ord_"].append(ord_)

        return assembly_data

    @staticmethod
    def strip_list(list_item: pd.Series) -> list:
        return list_item.str.slice(14, -5).tolist()

    @staticmethod
    def ord_lookup(item_to_find: str, part_list: list, sub_sn: list):
        if item_to_find in part_list:
            idx = part_list.index(item_to_find)
            return sub_sn[idx]

        return None  # Handle case where item_to_find is not found


class RackBurn:
    def __init__(self, url: str, refresh_interval: int):
        self.url = url
        self.refresh_interval = refresh_interval
        self.rburn_server = "http://10.43.251.35"
        self.lease_ip = "http://10.43.251.35/lease"
        self.live_data = []
        self.user_input_ = []
        self.event = Event()
        self.thread = Thread(target=self.run)
        self.thread.start()

    def fetch_live_data(self) -> None:
        try:
            self.live_data: list = []
            temp: list = []
            response = requests.get(self.url)

            soup = BeautifulSoup(response.text, "html.parser")
            # Scraping html table from the url
            table = soup.find("table", attrs={"id": "heckintable"})
            rows = table.find_all("tr")
            for row in rows:
                raw_data: list = []
                cols = row.find_all("td")
                # Test logs
                logs = [link.get("href") for link in cols[-1].find_all("a")]
                for cell in cols[:-1]:
                    raw_data.append(cell.text)
                for log in logs:
                    raw_data.append(log)
                temp.append(raw_data)

            # Sliced unnecessary columns from the original table
            for elem in range(1, len(temp)):
                self.live_data.append(list(itemgetter(1, 3, 0, 6, 7)(temp[elem])))

        except Exception as e:
            # required to replace with an error page
            print(f"Error fetching live data: {e}")

    def run(self):
        while not self.event.is_set():
            self.fetch_live_data()
            self.event.wait(self.refresh_interval)

    def stop(self):
        self.event.set()
        self.thread.join()

    def filtered_data(self, input_list) -> list:
        data_set = []
        for idx, serial_n in enumerate(input_list):
            for sn_list in self.live_data:
                # if user input sn is in the database
                if serial_n in sn_list[0]:
                    # append into a new list along with its index
                    data_set.append([idx + 1] + sn_list)

        # Sort items per conditions
        data_set.sort(key=lambda item: (
            item[2] == "WARNING",
            item[2] == "FAIL",
            item[2] == "RUNNING"), reverse=True)

        return data_set


def user_input() -> list:
    """
    Get data from user input text box.
    param: none
    return: list of input data separated by a white space
    """
    input_data: list = []
    txt_ = request.form.get("serial_num").split(" ")
    # remove all empty items in the list
    temp = [sn.upper() for sn in txt_ if sn != "\t" and sn != ""]
    # remove all duplicates and maintain the index order
    [input_data.append(sn) for sn in temp if sn not in input_data]

    return input_data
