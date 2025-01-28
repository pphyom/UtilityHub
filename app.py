import os
import redis
import config
from datetime import datetime
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from flask import Flask, render_template, session, g, make_response, request, jsonify, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy.orm import sessionmaker, scoped_session 
from main.core import *
from main.cburn_helper import *
from main.ftu_helper import *
from main.tools import *
from main.firmware_info import *
from make_celery import make_celery
from main.extensions import db, sess, login_manager, socketio
from models.models import User, Firmware # Import the User model


rburn_live = os.getenv("RBURN_SVR40_LIVE")

app = Flask(__name__, template_folder="templates", static_folder="static", static_url_path="/")
app.config.from_object(config.Config)  # Load the configuration from config.py

# Initialize the database
db.init_app(app)

# Initialize the session extension
sess.init_app(app)

# Initialize the login manager
login_manager.init_app(app)
login_manager.login_view = "login_error"

# Initialize the socketio extension
socketio.init_app(app, message_queue=app.config["CELERY_BROKER_URL"], cors_allowed_origins="*")

# Initialize the celery extension
celery = make_celery(app)

# Create the tables in the database
with app.app_context():
    db.create_all()
    db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=db.engine))

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

# Redis connection test begins

def get_redis_connection():
    return redis.Redis(host="10.43.240.69", port=6379, decode_responses=True)

@app.route("/redis_test")
def redis_test():
    r = get_redis_connection()
    r.set("foo", "Redis connection established.")
    value = r.get("foo")
    return f"Redis Value: {value}"

# Redis connection test ends

@app.context_processor
def connected_network():
    return {"connected_ip": request.remote_addr}


@app.before_request
def set_year():
    """ Set the current year in the context. """
    current_year = datetime.now().year
    g.current_year = current_year

# Login Authentication Begins

@app.before_request
def bind_session():
    # Bind the scoped session to the current app context
    db_session()


@app.teardown_appcontext
def remove_session(exception=None):
    # Remove the scoped session after the request
    try:
        db_session.remove()
    except Exception as e:
        app.logger.error(f"Error removing session: {e}")


# Loader for flask-login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# @login_manager.unauthorized_handler
# def unauthorized():
#     return redirect(url_for("login_error"))


@app.route("/unauthorized")
def login_error():
    return render_template("unauthorized.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("input-login-user")
        password = request.form.get("input-login-passwd")
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("tools", user_id=user.id))
        else:
            return render_template("login.html", error="Invalid username or password.")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# Login Authentication Ends


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
def on_connect():
    print("Connected to the server.")
    if not current_user or not current_user.is_authenticated:
        socketio.emit("error", {"message": "User not authenticated."})
        return

    if current_user.id is not None:
        socketio.emit("connected", {"message": "Connection established!"}, to=f"user_{current_user.id}")
    else:
        socketio.emit("error", {"message": "User ID is not valid."})


# Routes for firmware updates
@app.route("/validate_serial_number", methods=["POST"])
def validate():
    """ Validate the serial number of the system. """
    try:
        sn_list = request.get_json()
        valid_serialNums = asyncio.run(ftu.validation(sn_list["system_sn_list"], scan_log))
        invalid_serialNums = ftu.bad_items
        return jsonify({"valid_serialNums": valid_serialNums, "invalid_serialNums": invalid_serialNums})
    except Exception as e:
        return jsonify({"Error": str(e)})


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


@app.route("/get_ipmi_info", methods=["POST"])
def get_ipmi_info():
    """ 
    Get the IPMI info of the system.
    Pass the system from JS, get the IP address, and pass it back to the JS. 
    """
    input_data = request.get_json()
    serial_num = asyncio.run(ftu.validation([input_data["system_sn"]], scan_log)) # change input to list for function requirement
    sys_list = get_bmc_info_helper(serial_num)
    return jsonify(sys_list)


@app.route("/upload_firmware", methods=["POST"])
def upload_firmware():
    """ Upload the firmware to the update server. """

    try:
        # filesize = request.cookies.get("filesize")
        fwtype = request.cookies.get("fw-type")
        fw = request.files["file"]  # Get the file from the request
        filename = secure_filename(fw.filename)  # Secure the filename
        filepath = os.path.join(config.Config.FIRMWARE_FOLDER, filename)
        response_message = ""
        
        # Check if the file already exists in the database and filesystem
        existing_file_in_db = Firmware.query.filter_by(filename=filename).first()

        # Check if the file already exists on the server
        if os.path.exists(filepath):
            if existing_file_in_db:
                response_message = {"alertMessage": "File already exists.", "alertType": "warning"}
            else:
                # File exists on the server, but not in the database; add it to the database
                new_file = Firmware(filename=filename, filepath=filepath)
                db.session.add(new_file)
                db.session.commit()
                response_message = {"alertMessage": "File already exists.", "alertType": "warning"}
        else:
            # Save the file to the server
            fw.save(filepath)
            if not existing_file_in_db:
                # Add file metadata to the database if not already present
                new_file = Firmware(filename=filename, filepath=filepath)
                db.session.add(new_file)
                db.session.commit()
            response_message = {"alertMessage": "File Uploaded.", "alertType": "success"}

        firmware_info = get_firmware_info(filepath, cmd=f"Get{fwtype}Info")
        response = jsonify({"firmware_info": firmware_info, "response_message": response_message})
        return response
    
    except Exception as e:
        response = make_response(jsonify({"alertMessage": "Upload failed", "error": str(e)}), 500)
        return response


@app.route("/list_firmware", methods=["GET"])
def list_firmware():
    """ List the firmware files on the server. """
    firmware_files = Firmware.query.all()
    firmware_list = [{"filename": file.filename, "filepath": file.filepath} for file in firmware_files]
    return jsonify(firmware_list)


@app.route("/start_update", methods=["POST"])
@login_required
def start_update():
    """ Update the firmware of the system. """
    data = request.get_json() # data = {"system": system:dict, "firmware": firmware:str}
    if not data:
        return jsonify({"alertMessage": "Invalid input", "alertType": "danger"}), 400
    
    system = data.get("system")
    firmware = data.get("firmware")
    firmware_path = os.path.join(config.Config.FIRMWARE_FOLDER, firmware)
    # temp = get_firmware_info(firmware_path, cmd="GetBiosInfo")
    # print(firmware_path)
    # update_firmware(system, firmware_path, cmd="UpdateBios")
    # print("RESULT: ", result)
    # if not result:
    #     return jsonify({"alertMessage": "Firmware update failed.", "alertType": "danger"}), 500
    # else:
    #     print(result)
    #     return jsonify({"alertMessage": "Firmware update started.", "alertType": "success"}), 200
    # task = update_firmware.apply_async(args=[system, firmware_path, "UpdateBios"])
    task = celery.send_task("tasks.update_firmware", args=[system, firmware_path, "UpdateBios"])

    # return jsonify({"alertMessage": "Firmware update failed.", "alertType": "danger"}), 500
    return jsonify({"task_id": task.id, "status": "Started"}), 202
        

@app.route("/tools", methods=["GET", "POST"])
@login_required
def tools():
    if User.is_active:
        if request.method == "POST":
            input_list = user_input()
            good_list = asyncio.run(ftu.validation(input_list, scan_log))
            sys_list = get_bmc_info_helper(good_list)
            return render_template("tools.html", 
                                sys_list=sys_list, 
                                sn_url=sn_url, 
                                mo_url=mo_url)
        else:
            return render_template("tools.html")
    else:
        return redirect(url_for("login"))
    

if __name__ == "__main__":
    try:
        socketio.run(app, host="0.0.0.0", debug=True)
    finally:
        live.stop()