import uuid
from datetime import datetime
from flask import Flask, render_template, session, g
from flask_socketio import SocketIO, emit, join_room, leave_room
from main.core import *
from main.cburn_helper import *
from main.rburn_helper import *
from main.ftu_helper import *
from main.tools import *
from main.firmware_info import *
from config import Config
from main.extensions import db, sess
from icecream import ic

rburn_live = os.getenv("RBURN_SVR40_LIVE")

app = Flask(__name__, template_folder="templates", static_folder="static", static_url_path="/")
app.config.from_object(Config)  # Load the configuration from config.py

# Initialize the database
db.init_app(app)

# Initialize the session extension
sess.init_app(app)

# Initialize the socketio extension
socketio = SocketIO(app)

# Import the LiveSession model
from models.models import LiveSession
from models.models import User

# Create the tables in the database
with app.app_context():
    db.create_all()

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


@app.context_processor
def connected_network():
    return {"connected_ip": request.remote_addr}


@app.before_request
def set_year():
    current_year = datetime.now().year
    g.current_year = current_year


# Index Page #
@app.route("/get_data", methods=["GET"])
def get_data():
    data_helper = {
        "b23rburn": live.rburn_server,
        "cond": conditions
    }
    return jsonify(data_helper)


@app.route('/update', methods=['GET'])
def update():
    # input_list = live.user_input_
    input_list = session.get("user_input", [])
    data_set = live.filtered_data(input_list)
    return jsonify(data_set)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # If there is input, pass it into input_list using user_input() method
        input_list = user_input()
        # store the user input for the periodic updates
        session["user_input"] = input_list
        data_set = live.filtered_data(input_list)

        return render_template("index.html",
                               data=data_set,
                               headings=headings)
    else:
        input_list = session.get("user_input", [])
        data_set = live.filtered_data(input_list)
        return render_template("index.html", data=data_set)


# RBurn Page #
@app.route("/rburn_log", methods=["GET", "POST"])
def rburn_log():
    if request.method == "POST":
        # 1. get the user input: get_sn for sn, path to json, and rack name, 
        #    get_rack for rack path to each unit.
        get_sn, get_rack = get_sys_info(user_input(), live.live_data, live.rburn_server)

        # 2. if the rack_data is not on database, create it.
        create_directory()

        def do_operation(item_sn):
            print(f"{item_sn} created.")

        # 3. Retrieve the rack name from each server and search if the comparison file exists.
        for item in get_sn:
            for key in item.values():
                rack = key["rack"]

                # FILE EXISTS =>
                # 1. Get the JSON file from the new user input SN.
                # 2. Compare the JSON file with the existing JSON files in the rack.
                # 3. Display the result on the page.
                if os.path.exists(f"rack_data\\{rack}.json"):
                    print("file exist")
                    do_operation(list(item.keys())[0])
                    # do_something()

                # FILE NOT EXIST =>
                # 1. Create an empty JSON file using the rack name.
                # 2. Get a minimal of 5 passed units from the rack with their JSON files. 
                # 3. Pass the JSON file to each function for the result and create the temp JSON file.
                # 4. Pass the temp JSON file to the comparison function. 
                # 5. Store the most common data into the JSON file created in number 1.
                # 6. Get the JSON file from the new user input SN.
                # 7. Compare the JSON file with the existing JSON files in the rack.
                # 8. Display the result on the page.
                else:
                    print("file not exist")
                    with open(f"rack_data\\{rack}.json", "w") as db_file:
                        # json.dump(data, db_file)
                        db_file.write(json.dumps({}))
                    do_operation(list(item.keys())[0])
                    # do_something()

        # retrieve at least 5 passed units from the rack including the user's input
        # to create the test data if not exist
        # rack_addr = get_sn_models_from_rack(get_rack)

        return render_template("rburn_log.html", data=get_rack)

    return render_template("rburn_log.html")


# FTU Page #
@app.route("/ftu_log", methods=["GET", "POST"])
def ftu_log():
    if request.method == "POST":
        input_list = user_input()
        good_list = asyncio.run(ftu.validation(input_list, scan_log))
        test = {}  # return value
        for sn in good_list:
            outfile = asyncio.run(spm.retrieve_data_from_file(spm.assembly_rec, sn))
            mac_list = get_mac_address(outfile["part_list"], outfile["sub_sn"])

            for i in range(len(good_list)):
                serial_num = good_list[i]
                order_num = outfile["order_num"]
                ord_ = outfile["ord_"]

                test[serial_num] = [order_num, ord_]

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
                # ftu_paths = [(ftu_addr + "/".join(d.split("/")[:2])) for d in directory]
                # ftu_dir = list(dict.fromkeys(ftu_paths))  # remove duplicates

            # final = []
            # for sn, dir in zip(good_list, ftu_paths):
            #     temp = {}
            #     link = f"{dir}/{sn}/"
            #     js, found = asyncio.run(ftu.json_lookup(link))
            #     # temp["MO"] = js["MO"]
            #     temp["ftu_data"] = js
            #     final.append(temp)

        return render_template("ftu_log.html", data=test)
        # return render_template("ftu_log.html", data=input_list, good_list=good_list, bad_list=ftu.bad_items)
    return render_template("ftu_log.html")


# CBurn Page #
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


# Tool Page #
# Web socket for the tools page

@socketio.on("connect")
def connect():
    session["user_id"] = str(uuid.uuid4())
    join_room(session["user_id"])
    emit("connected", {"user_id": session["user_id"]})


@socketio.on("disconnect")
def disconnect():
    user_id = session.get("user_id")
    if user_id:
        # print(f"User {user_id} disconnected.")
        leave_room(user_id)
        session.pop("user_id", None)  # Remove user_id from session if it exists.


# Routes for firmware updates

@app.route("/get_bios_ver", methods=["POST"])
def get_bios_ver():
    """ Get the BIOS version of the system. """
    try:
        system_to_parse = request.get_json()
        ver = get_bios_ipmi_ver(system_to_parse, ipmitool_cmd["bios_ver"])
        return jsonify(ver)
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/get_ipmi_ver", methods=["POST"])
def get_ipmi_ver():
    """ Get the IPMI version of the system. """
    try:
        system_to_parse = request.get_json()
        ver = get_bios_ipmi_ver(system_to_parse, ipmitool_cmd["ipmi_ver"])
        return jsonify(ver)
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/firmware_transaction", methods=["POST"])
def firmware_transaction():
    input_data = request.get_json()
    good_list = asyncio.run(ftu.validation(input_data["system_sn"], scan_log))
    sys_list = screen_data_helper(good_list)
    return jsonify(sys_list)


@app.route("/tools", methods=["GET", "POST"])
def tools():
    if request.method == "POST":
        input_list = user_input()
        good_list = asyncio.run(ftu.validation(input_list, scan_log))
        sys_list = screen_data_helper(good_list)
        return render_template("tools.html", 
                               sys_list=sys_list, 
                               sn_url=sn_url, 
                               mo_url=mo_url)
    else:
        return render_template("tools.html")
    

if __name__ == "__main__":
    try:
        socketio.run(app, host="0.0.0.0", debug=True)
    finally:
        live.stop()
