from flask import Flask, render_template, request, jsonify
from icecream import ic
from config.core import *
from config.cburn_helper import *
from config.rburn_helper import *
from config.tools import *
import os, threading, time


header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                  " Chrome/123.0.0.0 Safari/537.36sec-gpc: 1",
    "Accept-Language": "en-US,en;q=0.9",
}
url23 = "http://10.43.251.40/input_output?model=Supermicro"


spm = SPM()
mo_url = spm.mo_url
sn_url = spm.sn_url
assembly_rec = spm.assembly_rec
cburn_addr = spm.cburn_addr
ins_path = spm.ins_path


smc = Source(url=url23, header=header)
b23rburn = smc.rburn_server
lease_ip = smc.lease_ip


# base_data = smc.live_data()  # assigned the data into the base_data variable
headings = DATA_["live_headings"]
rburn_headings = DATA_["rburn_headings"]
cburn_headings = DATA_["cburn_headings"]
conditions = DATA_["conditions"]


app = Flask(__name__, template_folder="templates", static_folder="static", static_url_path="/")

base_data = []

def live_data():
    """
    Search and isolate data table from the RackBurn Webpage.
    url: Rack Burn URL
    header: Http header
    return: List table
    """
    global base_data
    while True:
        respond = requests.Session()
        res = respond.get(url23)
        temp: list = []
        soup = BeautifulSoup(res.text, "html.parser")
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
            base_data.append(list(itemgetter(1, 3, 0, 6, 7)(temp[elem])))
        
        time.sleep(60)


thread = threading.Thread(target=live_data)
thread.daemon = True
thread.start()


def screen_live_data(input):
    data: list = []
    for idx, sn in enumerate(input):
        for sn_list in base_data:
            # if user input sn is in the database
            if sn in sn_list[0]:
                # append into a new list along with its index
                data.append([idx+1] + sn_list)
    return data


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # If there is input, pass it into input_list using user_input() method
        input_list: list[str] = user_input()
        data = screen_live_data(input_list)

        # Sort items per conditions
        data.sort(key=lambda item:
                  (item[2] == "WARNING",
                   item[2] == "FAIL",
                   item[2] == "RUNNING"), reverse=True)
    
        # return fetch_live_data()
        return render_template("index.html", 
                               data=data,
                               headings=headings,
                               b23rburn=b23rburn,
                               cond=conditions)
    return render_template("index.html")


@app.route("/rburn_log", methods=["GET", "POST"])
def rburn_log():
    if request.method == "POST":
        # 1. get the user input: get_sn for sn, path to json, and rack name, 
        #    get_rack for rack path to each units. 
        get_sn, get_rack = get_sys_info(user_input(), base_data, b23rburn)

        # retrieve at least 5 passed units from the rack including the user's input
        # to create the test data if not exist
        rack_addr = get_sn_models_from_rack(get_rack)

        # 2. if the rack_data is not on database, create it.
        if not os.path.exists("rack_data"):
            os.makedirs("rack_data")

        # 3. Retrieve the rack name from each servers and search if the comparison file exists.
        for item in get_sn:
            for key in item.values():
                rack = key["rack"]

                # if the file exists, will be used to compare test data.
                if os.path.exists(f"rack_data\{rack}.json"):
                    ic("file exist")
                
                # if not exist, create an empty file using the rack name.
                else:
                    ic("file not exist")
                    data = {}
                    with open(f"rack_data\{rack}.json", "w") as db_file:
                        # json.dump(data, db_file)
                        db_file.write(json.dumps({}))

        return get_sn
    
    return render_template("rburn_log.html")


@app.route("/ftu_log")
def ftu_log():
    return render_template("ftu_log.html")


@app.route("/cburn_log", methods = ["GET", "POST"])
def cburn_log():
    if request.method == "POST":
        sn_list: list[str] = user_input()

        cburn_result = screendump_wrapper(sn_list, assembly_rec, ins_path, cburn_addr)
        return render_template("cburn_log.html",
                            headings = cburn_headings,
                            data = cburn_result,
                            mo_url = mo_url,
                            sn_url = sn_url)
    
    return render_template("cburn_log.html")


@app.route("/tools")
def tools():
    return render_template("tools.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
