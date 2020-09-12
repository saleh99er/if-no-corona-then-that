import flask
from IFNCTT_request import *

app = flask.Flask(__name__)
app.config['DEBUG'] = True


@app.route('/check-status/', methods=['GET'])
def check_status():
    return "IFNCTT"


@app.route('/daily-check/', methods=['POST'])
def daily_check():
    #response = daily_check_request()
    response = DailyCheckResponse.SUBMITTED
    response_code = 400
    if(response == DailyCheckResponse.SUBMITTED or response == DailyCheckResponse.ALREADY_SUBMITTED):
        response_code = 200
    return flask.jsonify(str(response), response_code)


app.run()

