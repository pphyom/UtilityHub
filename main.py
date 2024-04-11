from flask import Flask, redirect, url_for, render_template, request
from config.core import Source

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                  " Chrome/123.0.0.0 Safari/537.36sec-gpc: 1"
                  "Accept-Language: en-US,en;q=0.9"
}
url = "http://10.43.251.42/input_output?model=Supermicro"


# smc = Source(url=url, header=header)
# base_data = smc.request_data()  # assigned the data into the base_data variable
# headings = ("Rack", "System SN.", "Status", "Time Taken")


app = Flask(__name__)


# @app.route("/", methods=["GET", "POST"])
# def index():
#     if request.method == "POST":
#         serial_number_list = [request.form.get("serial_numbers")]
#         for i in serial_number_list:
#             print(i.strip("\n"))
#     return render_template("index.html", headings=headings, data=base_data[0:10])

@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=90, debug=True)

# f.close()
