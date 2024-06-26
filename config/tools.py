import subprocess
from config.core import retrieve_data_from_file


def get_ipmi_info(part_list: list[str], sub_sn: list[str]) -> list[str]:
    """
    
    """
    ipmi_pswd: list = []
    for idx, val in enumerate(part_list):
        if "MAC-IPMI-ADDRESS" in val:
            mac = sub_sn[idx]
            mac_dashed = "-".join(x + y for x, y in zip(mac[::2], mac[1::2])).lower()
            print(mac_dashed)
            ip = get_ip_from_mac(mac_dashed)
            print(ip)
        if "NUM-DEFPWD" in val:
            pswd = sub_sn[idx]
    # ipmi_pswd.append(temp)

    return ipmi_pswd


def get_ip_from_mac(mac: str):
    try:
        cmd = f'arp -a | findstr "{mac}"'
        returned_output = subprocess.check_output((cmd), shell=True, stderr=subprocess.STDOUT)
        ip = str(returned_output).split(' ')[2]
        return ip
    except subprocess.CalledProcessError as e:
        print(f"Error: Command '{e.cmd}' failed with exit code '{e.returncode}'")
