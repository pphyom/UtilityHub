import requests
from datetime import datetime
from bs4 import BeautifulSoup


present = datetime.now()
year = present.year
month = {1: "January", 2: "February", 3: "March", 4: "April", 
         5: "May", 6: "June", 7: "July", 8: "August", 
         9: "September", 10: "October", 11: "November", 12: "December"}


base_url = f"http://10.43.251.40/logs/Supermicro/{year}/{month.get(present.month-1)}/6U8801332583-1/29/R-PRE/"


class Rack:
    def __init__(self) -> None:
        pass


def find_all_a_tag(url: str):
    """ 
    Find all the a href link from the webpage. 
    param: web url
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


def retrieve_sys_info(input_list, base_data, rb_server):
    trace_sn: list = []
    trace_rack: list = []
    bad_sn_list: list = []
    for serial_number in input_list:
        for sn_list in base_data:
            # if user input sn is in the database and pass
            if serial_number in sn_list[0] and sn_list[1] == "PASS":
                # temp = {"serial_num": sn_list[0], 
                #         "rack": sn_list[2], 
                #         "path": rb_server + (sn_list[4].strip("\n")) + "/system_test-summary-json-full.json"}
                temp = {sn_list[0]: {"rack": sn_list[2], "path": rb_server + (sn_list[4].strip("\n")) + "/system_test-summary-json-full.json"}}
                trace_sn.append(temp)
                # separate rack list
                substr = "http://10.43.251.40" + sn_list[4].partition("/R-PRE")[0][:-2]
                sn_list[0] = {sn_list[2]: sn_list[4]}

                trace_rack.append(sn_list[0])
                # trace_rack = list(set(trace_rack))
            # if not, throw sn into bad_sn_list
            else:
                bad_sn_list.append(serial_number)
    return trace_sn, trace_rack