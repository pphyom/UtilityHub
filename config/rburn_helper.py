import requests, os
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
    Helper function for find_mac_summary_log().
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
    """
    Required find_all_a_tag(url: str) to work with.
    Find mac address from the given link, retrieve json test result from it.
    """
    snumbers_list = find_all_a_tag(base_url) # get all serial numbers from /R-PRE/SN
    try:
        snumbers_list = set(snumbers_list[5:])  # remove duplicates and extra rows
        mac_list: list = []
        for sn in snumbers_list:
            url_for_each_sn = base_url + f"/{sn}"
            mac = find_all_a_tag(url_for_each_sn)    # find mac address in each url
            link = base_url + f"/{sn}/" + mac[5] + "/system_test-summary-json-full.json"
            mac_list.append(link)
        return mac_list
        
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


def get_sn_models_from_rack(rack_list: list):
    racks = Rack(url=base_url)
    count = 0
    rack_addr: list = []
    # Create a directory that stores test data for each rack
    if not os.path.exists("rack_data"):
            os.makedirs("rack_data")

    for rack in rack_list:
        print(rack)
    
    return rack_addr


def last_day_of_previous_month(year, month, tday):
    """ Subtract one day from the first day of the current month """
    date = datetime(year, month, tday)
    last_day = date.replace(day=1) - timedelta(days=1)
    return last_day.day
