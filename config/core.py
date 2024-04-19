import requests
from bs4 import BeautifulSoup
from operator import itemgetter


class Source:
    def __init__(self, url: str, header: dict):
        self.url = url
        self.header = header
    
    url_server42 = "http://10.43.251.42"

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
            data_list: list = []
            soup = BeautifulSoup(respond.text, "html.parser")
            # Scraping html table from the url
            table = soup.find("table", attrs={"id": "heckintable"})
            rows = table.find_all("tr")
            for row in rows:
                raw_data: list = []
                cols = row.find_all("td")
                # Test logs
                logs = [link.get("href") for link in cols[-1].find_all("a")]
                for cell in cols[:-1]:
                    raw_data.append(cell.text)
                for log in logs:
                    raw_data.append(log)

                temp.append(raw_data)

            # Sliced unnecessary columns from the original table
            for elem in range(1, len(temp)):
                data_list.append(list(itemgetter(1, 3, 0, 6, 7)(temp[elem])))

            return data_list
