
import requests
from bs4 import BeautifulSoup

url = 'http://10.43.251.40/lease'

def get_ipmi_info(part_list: list[str], sub_sn: list[str]) -> list[str]:
    """
    
    """
    ipmi_info = {'mac': [], 'pswd': []}
    for part, ssn in zip(part_list, sub_sn):
        for idx, val in enumerate(part):
            if 'MAC-IPMI-ADDRESS' in val:
                ipmi_info['mac'].append(ssn[idx])
            if 'NUM-DEFPWD' in val:
                ipmi_info['pswd'].append(ssn[idx])

    return ipmi_info


def get_ip_addr(part_list: list, sub_sn: list):
    ipmi_info = get_ipmi_info(part_list, sub_sn)
    mac_list = ipmi_info['mac']
    pswd_list = ipmi_info['pswd']
    for mac in mac_list:
        data = {'searchtxt': mac}
        try:
            ipmi_combo = {
                'ip_address': [],
                'username': 'ADMIN',
                'password': []
                }
            
            response = requests.post(url, data=data, verify=False)
            soup = BeautifulSoup(response.text, 'html.parser')
            ip_addr = soup.select_one('body > div > div > div > div.card-body > form > '
                                    'div:nth-child(2) > div > span:nth-child(2) > font > b')
            ipmi_combo['ip_address'].append(ip_addr.text)
            

            return ipmi_combo
            
        except Exception as e:
            return f'Error finding the ip address: {e}'
    

