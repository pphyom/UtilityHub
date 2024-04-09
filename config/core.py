import requests
from bs4 import BeautifulSoup


class Source:
    def __init__(self):
        self.header = ""
        self.url = ""


    def request_data(self, url: str, header: str):
        """
        Search and isolate data table from the RackBurn Webpage. 
        url: Rack Burn URL
        header: Http header
        Return: List table
        """
        respond = requests.get(url, header)
        if not respond:
            respond.raise_for_status()
        else:
            data_table = []
            soup = BeautifulSoup(respond.text, "html.parser")
            table = soup.find("table", attrs={"id": "heckintable"})
            for row in table.find_all("tr"):
                rows = []
                for cell in row.find_all("td"):
                    rows.append(cell.text)
                data_table.append(rows)
            return data_table