import requests
from datetime import datetime
from bs4 import BeautifulSoup


PRESENT = datetime.now()
year = PRESENT.strftime("%Y")
month = PRESENT.strftime("%B")
day = PRESENT.day

base_url = f"http://10.43.251.40/logs/Supermicro/{year}/{month}/6U8801332583-2/29/R-PRE/"
        

def find_all_aTag(url):
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
    snumbers_list = find_all_aTag(base_url) # get all serial numbers
    try:
        snumbers_list = set(snumbers_list[5:])  # remove duplicates and extra rows
        addr = []
        for sn in snumbers_list:
            url_for_each_sn = base_url + f"{sn}"
            mac = find_all_aTag(url_for_each_sn)    # find mac address in each url
            link = base_url + f"{sn}/" + mac[5] + "/system_test-summary-json-full.json"
            addr.append(link)
        return addr
        
    except TypeError as te:
        print(te)