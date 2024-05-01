import requests
from flask import request
from bs4 import BeautifulSoup
from operator import itemgetter
from config.search import *

DATA_ = {
        "live_headings": ("Location", "System SN", "Status", "Rack", "Time Gap", "Log"),
        "rburn_headings": ("System SN","Test Result", "CPU Speed", "CPU Linpack", "DIMM", "GPU Thresholds", 
                           "GPU Benchmark", "GPU Linpack", "FDT", "GDT", "GPU FW", "GPU NV"),
        "conditions": ("WARNING", "FAIL", "PASS"),
        }


class Source:
    def __init__(self, url: str, header: dict):
        self.url = url
        self.header = header
    
    url_server40 = "http://10.43.251.40"

    def live_data(self):
        """
        Search and isolate data table from the RackBurn Webpage.
        url: Rack Burn URL
        header: Http header
        return: List table
        """
        respond = requests.get(self.url, self.header)
        if not respond:
            respond.raise_for_status()
        else:
            temp: list = []
            data_list: list = []
            soup = BeautifulSoup(respond.text, "html.parser")
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
                data_list.append(list(itemgetter(1, 3, 0, 6, 7)(temp[elem])))

            return data_list


def user_input():
    """
    Get data from user input text box.
    param: none
    return: list of input data separated by a white space
    """
    temp = request.form.get("serial_num").split(" ")
    # remove all empty items in the list
    temp = [sn for sn in temp if sn != ""]
    # remove all duplicates and maintain the index order
    input_data:list = []
    [input_data.append(sn) for sn in temp if sn not in input_data]
    return input_data


def cpu_info():
    pass