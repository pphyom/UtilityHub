from flask import Flask, redirect, url_for, render_template, request
from config.core import Source

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                  " Chrome/123.0.0.0 Safari/537.36sec-gpc: 1"
                  "Accept-Language: en-US,en;q=0.9"
}
url = "http://10.43.251.42/input_output?model=Supermicro"


smc = Source(url=url, header=header)
base_data = smc.request_data()  # assigned the data into the base_data variable
headings = ("Location", "System SN", "Status", "Rack", "Time Taken")


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        input_list = request.form["serial_num"].split(" ")  # retrieved from text input box
        input_list = [sn for sn in input_list if sn != ""]  # remove all empty item in the list
        data: list = []
        for idx, sn in enumerate(input_list):
            for sn_list in base_data:
                if sn in sn_list[0]:
                    data.append([idx+1] + sn_list)

        return render_template("index.html", headings=headings, data=data)
    
    else:
        return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=90, debug=True)
    