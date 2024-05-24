import requests, os, json
from datetime import datetime, timedelta
from bs4 import BeautifulSoup


present = datetime.now()
month = {1: "January", 2: "February", 3: "March", 4: "April", 
         5: "May", 6: "June", 7: "July", 8: "August", 
         9: "September", 10: "October", 11: "November", 12: "December"}

# t_year = int(present.strftime("%Y"))
# t_month = month.get(present.month)
# t_day = int(present.strftime("%d"))


base_url = f"http://10.43.251.40/logs/Supermicro/"


class Rack:
    def __init__(self, url):
        self.url = url


def find_all_a_tag(url: str):
    """ 
    Helper function to retrieve links from the url.
    Find all the a href link from the given link. 
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


def find_mac_summary_log(rack_url):
    """
    Find path to the mac from the given link.
    Required find_all_a_tag(url: str) to work with.
    param: eg., url=> logs/Supermicro/2024/May/'rack'
    """
    path_to_mac: list = []
    total = 0
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
                if "PASS" in temp.text and total != 5:
                    path_to_mac.append(link)
                    total += 1
        return path_to_mac
    
    except TypeError as te:
        print(te)


def get_sys_info(input_list, base_data, rb_server):
    """
    Take a (list of) serial number from user input and search it in the database. 
    Store it in a separate list along with the log ONLY IF it is in the database AND "pass" the test. 
    param: list of serial number/s input from users.
    param: base_data-- the rack burn database.
    param: rb_server-- the server to get the info from (eg: http://10.43.251.40)
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
                substr = "http://10.43.251.40" + sn_list[4].partition("/R-PRE")[0][:-2]
                get_rack.append(substr)
                get_rack = list(set(get_rack))

    return get_sn, get_rack


def get_sn_models_from_rack(rack_list):
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

    test = []
    for rack in rack_list:
        path_to_mac = find_mac_summary_log(rack)
        test.append(path_to_mac)
    return test


def last_day_of_previous_month(year, month, tday):
    """ Subtract one day from the first day of the current month """
    date = datetime(year, month, tday)
    last_day = date.replace(day=1) - timedelta(days=1)
    return last_day.day
