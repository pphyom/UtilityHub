import json
import asyncio
import httpx
import urllib3
import requests
from bs4 import BeautifulSoup


class FTU:
    def __init__(self):
        self.bad_items = [] # stores all invalid inputs


    async def validation(self, sn_list: str, scan_log: str):
        """
        Check if the input serial number is valid or not.
        - Verify the SN exists on SPM. 
        - Yes -> go to good_list | No -> go to bad_list.
        """
        bad_list = [] # invalid inputs
        
        async with httpx.AsyncClient() as client:
            tasks = [client.get(scan_log + elem) for elem in sn_list]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            for elem, response in zip(sn_list, responses):
                if response.status_code != 200:
                    bad_list.append(elem)

        self.bad_items = bad_list
        good_list = [elem for elem in sn_list if elem not in bad_list]

        return good_list


def json_lookup(url: str):
    """
    Search .json file in a given url. Download it and return true if found. 
    Return none if not found.
    
    :param url:
        Web address (path) for .json files.
    """
    found: bool = False
    http = urllib3.PoolManager()
    html = http.request("GET", url)
    soup = BeautifulSoup(html.data, "html.parser")
    js_files = soup.find_all(string=lambda x: ".json" in x)
    if js_files:
        found = True
        for f in js_files:
            if f.endswith(".json"):
                download_file = url + f
                res = requests.get(download_file, stream=True)
                js = json.loads(res.text)
                return js, found
    else:
        return None, found


def pcie_drops_calculation(pcie_total: int, js: dict):
    """
    Calculate the PCIE Gen and Speed loss. 
    - pcie_total -> the total PCIE value from the current session state.
    - js -> use json file to retrieve total PCIE_#_CAP and PCIE_#_STA 
    """
    gen_drop = 0
    spd_drop = 0

    for elem in range(0, pcie_total):
        pcie_cap_ = js[f"PCIE_{elem}_CAP"]    # front half
        pcie_sta_ = js[f"PCIE_{elem}_STA"]    # rear half

        pcie_dict = {"Gen": [pcie_cap_[0:4], pcie_sta_[0:4]],   # Gen4 x2
                     "Spd": [pcie_cap_[5:], pcie_sta_[5:]]}     # Gen4x 2

        if pcie_dict["Gen"][0] not in pcie_dict["Gen"][1]:
            gen_drop += 1

        if pcie_dict["Spd"][0] not in pcie_dict["Spd"][1]:
            spd_drop += 1
        
    return gen_drop, spd_drop
