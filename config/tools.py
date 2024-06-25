
import subprocess
from core import retrieve_data_from_file


cmd = "arp -a | findstr '7c-c2-55-52-d5-ea'"
returned_output = subprocess.check_output((cmd), shell=True, stderr=subprocess.STDOUT)
ip = str(returned_output).split(' ')[2]
print(ip)