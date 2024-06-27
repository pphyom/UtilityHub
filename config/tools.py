from config.core import retrieve_data_from_file
from selenium import webdriver
from selenium.webdriver.common.by import By

def get_ipmi_info(part_list: list[str], sub_sn: list[str], lease_ip: str) -> list[str]:
    """
    
    """
    ipmi_pswd: list = []
    mac_pswd: list[str] = []
    for idx, val in enumerate(part_list):
        if "MAC-IPMI-ADDRESS" in val:
            mac = sub_sn[idx]
            mac_pswd.append(mac)
        if "NUM-DEFPWD" in val:
            pswd = sub_sn[idx]
            mac_pswd.append(pswd)
    ip = get_ip_from_mac(mac_pswd[0], lease_ip)
    print(ip)


    return ipmi_pswd


def get_ip_from_mac(mac_list: str, lease_ip: str):
    """
    Selenium is used to scrape ip address from MAC address. 
    """
    op = webdriver.ChromeOptions()
    op.add_argument('headless')  # to disable browser pop-up
    browser = webdriver.Chrome(options=op)
    browser.get(lease_ip)

    search_box = browser.find_element(By.ID, "searchstring")
    search_btn = browser.find_element(By.XPATH, "/html/body/div/div/div/div[2]/form/div[1]/div[2]/button")
    ip_address_list: list[str] = []
    for mac in mac_list:
        search_box.send_keys(mac)
        search_btn.click()
        ip = browser.find_element(By.XPATH, "/html/body/div/div/div/div[2]/form/div[2]/div/span[2]/font/b")
        ip_address_list.append(ip)
    
    return ip_address_list
