import flask
import socket
from IFNCTT_request import *
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os


app = flask.Flask(__name__)
app.config['DEBUG'] = True


@app.route('/check-status/', methods=['GET'])
def check_status():
    return "IFNCTT"


@app.route('/daily-check/', methods=['POST'])
def daily_check():
    response = daily_check_request()
    response_code = 400
    if(response == DailyCheckResponse.SUBMITTED or response == DailyCheckResponse.ALREADY_SUBMITTED):
        response_code = 200
    return flask.jsonify(response, response_code)

def get_this_addr():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    this_addr = s.getsockname()[0]
    s.close()
    return this_addr

# Initialization
# Use the application default credentials
cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
  'projectId': os.environ.get("IFNCTT_GC_PROJECT_ID"),
})

db = firestore.client()

print(get_this_addr())
app.run(host='0.0.0.0')

