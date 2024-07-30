import json
import asyncio
import aiohttp
import requests
from io import StringIO
from bs4 import BeautifulSoup
from config.core import SPM


spm = SPM()

class FTU:
    def __init__(self):
        self.bad_items = []  # stores all invalid inputs

    async def validation(self, sn_list: list, scan_log: str) -> list:
        """
        Check if the input serial number is valid or not by comparing SPM scanlog.
        """
        bad_list = [sn for sn in sn_list if not requests.get(scan_log + sn)]
        good_list = [sn for sn in sn_list if sn not in bad_list]
        self.bad_items = bad_list

        return good_list

    async def json_lookup(self, url: str) -> tuple[list, bool]:
        """
        Search .json file in a given url. Download it and return true if found. 
        Return none and false if not found.
        """
        found: bool = False
        async with aiohttp.ClientSession() as session:
            task = spm.fetch(session, url)
            respond = await task

            soup = BeautifulSoup(StringIO(respond), "html.parser")
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

    def pcie_drops_calculation(self, pcie_total: int, js: dict):
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
