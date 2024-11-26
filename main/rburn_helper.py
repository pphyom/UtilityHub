import os
import requests
from bs4 import BeautifulSoup

RBURN_LOG = os.getenv("RBURN_LOG")
RBURN_SVR40 = os.getenv("RBURN_SVR40")


def find_all_a_tag(url: str):
    """ 
    Helper function to retrieve links from the url.
    Find all the 'a href' links from the given link.
    param: web url
    """
    try:
        respond = requests.get(url)
        respond.raise_for_status()
        soup = BeautifulSoup(respond.content, "html.parser")
        links = [(link.get("href").strip("/")) for link in soup.find_all("a")]
        return links
    
    except requests.exceptions.HTTPError as he:
        print(he)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as ce:
        print(ce)


def find_mac_summary_log(rack_url: str) -> list:
    """
    Find path to the mac from the given input URL.
    Required find_all_a_tag(url: str) to work with.
    param: e.g., url=> logs/Supermicro/2024/May/'rack'
    """
    path_to_mac: list = []
    count = 0
    try:
        dates = find_all_a_tag(rack_url)[5:]    # Search test date by each rack
        dates = list(set(dates))                # Remove date duplicates
        dates.sort(reverse=True)
        for date in dates:
            path = f"{rack_url}{date}/R-PRE/"
            sn_list = find_all_a_tag(path)[5:]  # Search system sn
            sn_list = list(set(sn_list))        # Remove sn duplicates
            for sn in sn_list:
                url_for_each_sn = path + sn
                mac = find_all_a_tag(url_for_each_sn)   # Search mac address
                link = f"{url_for_each_sn}/{mac[5]}/"

                # Validating if the system passed the test. Only passed unit will be added to the list.
                temp = requests.get(f"{link}system_final-test-result.txt")
                if "PASS" in temp.text and count != 5:
                    path_to_mac.append(link)
                    count += 1

        return path_to_mac
    
    except TypeError as te:
        print(te)


def get_sys_info(input_list: list, base_data: list, rb_server: str) -> tuple[list, list]:
    """
    Take a (list of) serial number from user input and search it in the database. 
    Store it in a separate list along with the log ONLY IF it is in the database AND "pass" the test. 
    param: list of serial number/s input from users.
    param: base_data-- the rack burn database.
    param: rb_server-- the server to get the info from.
    """
    get_sn: list = []
    get_rack: list = []
    for serial_number in input_list:
        for sn_list in base_data:
            # if user input sn is in the database and pass
            if serial_number in sn_list[0] and sn_list[1] == "PASS":
                temp = {sn_list[0]: {"rack": sn_list[2], 
                                     "path": rb_server + (sn_list[4].strip("\n")) + "/system_test-summary-json-full.json"}}
                # append the combination of sn, rack, and url to json file into get_sn list
                get_sn.append(temp)
                
                # get racks belong to each input sn
                substr = RBURN_SVR40 + sn_list[4].partition("/R-PRE")[0][:-2]
                get_rack.append(substr)
                get_rack = list(set(get_rack))

    return get_sn, get_rack


def get_sn_models_from_rack(rack_list: list):
    # Create a directory that stores test data for each rack
    if not os.path.exists("rack_data"):
        os.makedirs("rack_data")

    test_dict = {
                    "CPU": {
                        "speed": "100",
                        "core": "",
                        "linpack_hpl": ""
                    },

                    "DIMM": {
                        "total_available_size": "",
                        "stream_memory_bandwidth": ""
                    },

                    "DISK": {
                        "disk_speed_test": "",
                        "disk_fio_benchmark128": ""
                    },

                    "GPU": {
                        "bandwidth_test": "",
                        "linpack_hpl": "",
                        "threasholds": "",
                        "nv_topology": "",
                        "GDT": "",
                        "FDT": "",
                        "FW_Retimer": ""
                    }
                }

    for rack in rack_list:
        path_to_mac = find_mac_summary_log(rack)

        for full_path in path_to_mac:
            elem = full_path + "system_test-summary-json-full.json"
            print(elem)
        
    return "Hello"
