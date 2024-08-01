import os
import json
import asyncio
import requests
from flask import Flask, render_template, jsonify
from config.core import *
from config.cburn_helper import *
from config.rburn_helper import *
from config.ftu_helper import *
from config.tools import *


rburn_live = "http://10.43.251.40/input_output?model=Supermicro"

app = Flask(__name__, template_folder="templates", static_folder="static", static_url_path="/")

spm = SPM()
mo_url = spm.mo_url
sn_url = spm.sn_url
scan_log = spm.scanlog
assembly_rec = spm.assembly_rec
ftu_addr = spm.ftu_addr
ftu_b23 = spm.ftu_b23
cburn_addr = spm.cburn_addr
ins_path = spm.ins_path

headings = DATA_["live_headings"]
rburn_headings = DATA_["rburn_headings"]
cburn_headings = DATA_["cburn_headings"]
conditions = DATA_["conditions"]

live = RackBurn(url=rburn_live, refresh_interval=60)
ftu = FTU()


@app.route("/get_data", methods=["GET"])
def get_data():
    data_helper = {
        "b23rburn": live.rburn_server,
        "cond": conditions
    }
    return jsonify(data_helper)


@app.route('/update', methods=['GET'])
def update():
    input_list = live.user_input_
    data_set = live.filtered_data(input_list)
    return jsonify(data_set)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # If there is input, pass it into input_list using user_input() method
        input_list = user_input()
        # store the user input for the periodic updates
        live.user_input_ = input_list
        data_set = live.filtered_data(input_list)

        return render_template("index.html",
                               data=data_set,
                               headings=headings)
    return render_template("index.html")


@app.route("/rburn_log", methods=["GET", "POST"])
def rburn_log():
    if request.method == "POST":
        # 1. get the user input: get_sn for sn, path to json, and rack name, 
        #    get_rack for rack path to each unit.
        get_sn, get_rack = get_sys_info(user_input(), live.live_data, live.rburn_server)

        # retrieve at least 5 passed units from the rack including the user's input
        # to create the test data if not exist
        rack_addr = get_sn_models_from_rack(get_rack)

        # 2. if the rack_data is not on database, create it.
        if not os.path.exists("rack_data"):
            os.makedirs("rack_data")

        # 3. Retrieve the rack name from each server and search if the comparison file exists.
        for item in get_sn:
            for key in item.values():
                rack = key["rack"]

                # if the file exists, will be used to compare test data.
                if os.path.exists(f"rack_data\\{rack}.json"):
                    print("file exist")

                # if not exist, create an empty file using the rack name.
                else:
                    print("file not exist")
                    with open(f"rack_data\\{rack}.json", "w") as db_file:
                        # json.dump(data, db_file)
                        db_file.write(json.dumps({}))

        return render_template("rburn_log.html")

    return render_template("rburn_log.html")


@app.route("/ftu_log", methods=["GET", "POST"])
def ftu_log():
    if request.method == "POST":
        input_list = user_input()
        good_list = asyncio.run(ftu.validation(input_list, scan_log))
        outfile = asyncio.run(spm.retrieve_data_from_file(spm.assembly_rec, good_list))   
        mac_list = get_mac_address(outfile["part_list"], outfile["sub_sn"])

        #  get validated instruction file
        ins_file_url = [
            ins_file for mac in mac_list 
            if requests.get(ins_file := f"{ins_path}/ins-{mac}".lower())
        ]

        #  get the directory (path) from the instruction file for each system
        directory = [
            line[5:-1]
            for elem in ins_file_url 
            for line in get_each_line_from_page(elem) 
            if "DIR=" in line
        ]

        #  create the ftu urls
        ftu_paths = [(ftu_addr + "/".join(d.split("/")[:2])) for d in directory]
        # ftu_dir = list(dict.fromkeys(ftu_paths))  # remove duplicates
        
        final = []
        for sn, dir in zip(good_list, ftu_paths):
            temp = {}
            link = f"{dir}/{sn}/"
            js, found = asyncio.run(ftu.json_lookup(link))
            temp["serial_number"] = sn
            temp["node_data"] = js
            temp["is_found"] = found
            final.append(temp)
        
        return render_template("ftu_log.html")
        # return render_template("ftu_log.html", data=input_list, good_list=good_list, bad_list=ftu.bad_items)
    return render_template("ftu_log.html")


@app.route("/cburn_log", methods=["GET", "POST"])
def cburn_log():
    if request.method == "POST":
        sn_list: list[str] = user_input()
        good_list = asyncio.run(ftu.validation(sn_list, scan_log))
        cburn_result = screendump_wrapper(good_list, assembly_rec, ins_path, cburn_addr)

        return render_template("cburn_log.html",
                               headings=cburn_headings,
                               data=cburn_result,
                               mo_url=mo_url,
                               sn_url=sn_url)

    return render_template("cburn_log.html")


@app.route("/tools", methods=["GET", "POST"])
def tools():
    if request.method == "POST":
        input_list = user_input()
        good_list = asyncio.run(ftu.validation(input_list, scan_log))
        outfile = asyncio.run(spm.retrieve_data_from_file(spm.assembly_rec, good_list))   
        temp = get_ip_addr(outfile["part_list"], outfile["sub_sn"])

        return render_template("tools.html")
    return render_template("tools.html")


if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", debug=True)
    finally:
        live.stop()
