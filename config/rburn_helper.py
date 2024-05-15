import requests
from datetime import datetime
from bs4 import BeautifulSoup


present = datetime.now()
month = {1: "January", 2: "February", 3: "March", 4: "April", 
         5: "May", 6: "June", 7: "July", 8: "August", 
         9: "September", 10: "October", 11: "November", 12: "December"}


base_url = f"http://10.43.251.40/logs/Supermicro/{present:%Y}/{month.get(present.month)}/"

class Rack:
    def __init__(self, url):
        self.url = url


def find_all_a_tag(url: str):
    """ 
    Find all the a href link from the webpage. 
    param: web url (the url tail must be R-PRE/)
    """
    try:
        respond = requests.get(url)
        respond.raise_for_status()
        soup = BeautifulSoup(respond.content, "html.parser")
        links = [(link.get("href").strip("/")) for link in soup.find_all("a")]
        return links # list of serial numbers
    
    except requests.exceptions.HTTPError as he:
        print(he)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as ce:
        print(ce)


def find_mac_summary_log():
    """ Find mac address from the given link, retrieve json test result from it. """
    snumbers_list = find_all_a_tag(base_url) # get all serial numbers
    try:
        snumbers_list = set(snumbers_list[5:])  # remove duplicates and extra rows
        mac_list: list = []
        for sn in snumbers_list:
            url_for_each_sn = base_url + f"{sn}"
            mac = find_all_a_tag(url_for_each_sn)    # find mac address in each url
            link = base_url + f"{sn}/" + mac[5] + "/system_test-summary-json-full.json"
            mac_list.append(link)
        return mac_list
        
    except TypeError as te:
        print(te)


def get_sys_info(input_list, base_data, rb_server):
    get_sn: list = []
    get_rack: list = []
    for serial_number in input_list:
        for sn_list in base_data:
            # if user input sn is in the database and pass
            if serial_number in sn_list[0] and sn_list[1] == "PASS":
                temp = {sn_list[0]: {"rack": sn_list[2], 
                                     "path": rb_server + (sn_list[4].strip("\n")) + "/system_test-summary-json-full.json"}}
                # get serial numbers 
                get_sn.append(temp)
                
                # get rack list
                get_rack.append(sn_list[2])
                # substr = "http://10.43.251.40" + sn_list[4].partition("/R-PRE")[0][:-2]
                # get_rack.append(substr)
                get_rack = list(set(get_rack))

    return get_sn, get_rack


def get_sn_models_from_rack(rack_list: list):
    racks = Rack(url=base_url)
    for rack in rack_list:
        print(f"{racks.url}{rack}")

