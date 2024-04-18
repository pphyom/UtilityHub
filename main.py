from flask import Flask, redirect, url_for, render_template, request
from config.core import Source
import time

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                  " Chrome/123.0.0.0 Safari/537.36sec-gpc: 1"
                  "Accept-Language: en-US,en;q=0.9"
}
url = "http://10.43.251.42/input_output?model=Supermicro"


smc = Source(url=url, header=header)
base_data = smc.live_data()  # assigned the data into the base_data variable
headings = ("Location", "System SN", "Status", "Rack", "Time Gap", "Log")
CONDITIONS = ("WARNING", "FAIL", "PASS")
b23rburn = smc.url_server42


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # retrieved from text input box
        input_list = request.form["serial_num"].split(" ")
        # remove all empty items in the list
        input_list = [sn for sn in input_list if sn != ""]
        data: list = []
    
        for idx, sn in enumerate(input_list):
            for sn_list in base_data:
                if sn in sn_list[0]:
                    data.append([idx+1] + sn_list)
    
        # Sort items per conditions
        data.sort(key=lambda item:
                  (item[2] == "WARNING",
                   item[2] == "FAIL",
                   item[2] == "PASS"), reverse=True)
    
        return render_template("index.html", 
                               headings=headings, 
                               data=data, 
                               cond=CONDITIONS,
                               b23rburn=b23rburn)
    
    else:
        return render_template( "index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=90, debug=True)
    