from flask import Flask, redirect, url_for, render_template, request
from config.core import Source


app = Flask(__name__)


obj = Source()
obj.header = {
        "User-Agent": "MMozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }
obj.url = "http://10.43.251.42/input_output?model=Supermicro"
base_data = obj.request_data(obj.url, obj.header)
request_data = {"rack": [], "system_sn": [], "status": [], "time_taken": []}


# print(base_data[1])


# Data from the Server
for elem in base_data[1:]:
    request_data["rack"].append(elem[0])
    request_data["system_sn"].append(elem[1])
    request_data["status"].append(elem[3])
    request_data["time_taken"].append(elem[6])

print(base_data[3])
print(request_data['rack'][2])

data = []
headings = ("Rack", "System SN.", "Status", "Time Taken")
# for i in range(len(request_data["system_sn"])):
data = [request_data["rack"], request_data["system_sn"], request_data["status"], request_data["time_taken"]]
    # print(i)
# data = [['testing', 1, 2, 3], [2, 3, 4, 5], ['hello', 'tedsf', 0, 3], [3, 5, 33, 232]]


# print(data[0][0])

# with open("list.txt", 'r') as f:
#     file_list = [i.strip("\n") for i in f]


# for sn in file_list:
#     if sn in request_data["system_sn"]:
#         idx = request_data["system_sn"].index(sn)
#         data = [[request_data["rack"][idx], sn, request_data["status"][idx], request_data["time_taken"][idx]]]
#     else:
#         data = [[None, None, None, None]]


@app.route("/")
def index():
    return render_template("index.html", headings=headings, data=data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=90, debug=True)


# f.close()