import requests
from bs4 import BeautifulSoup
from operator import itemgetter


class Source:
    def __init__(self, url: str, header: dict):
        self.url = url
        self.header = header

    def live_data(self):
        """
        Search and isolate data table from the RackBurn Webpage.
        url: Rack Burn URL
        header: Http header
        Return: List table
        """
        respond = requests.get(self.url, self.header)
        if not respond:
            respond.raise_for_status()
        else:
            temp: list = []
            data_tuple: list = []
            data_list: list = []
            soup = BeautifulSoup(respond.text, "html.parser")
            # Scraping html table from the url
            table = soup.find("table", attrs={"id": "heckintable"})
            for row in table.find_all("tr"):
                rows: list = []
                for cell in row.find_all("td"):
                    rows.append(cell.text)
                temp.append(rows)
            
            # Sliced unnecessary columns from the original table
            for elem in range(1, len(temp)):
                data_tuple.append(itemgetter(1, 3, 0, 6)(temp[elem]))

            for elem in data_tuple:
                data_list.append(list(elem))

            return data_list
