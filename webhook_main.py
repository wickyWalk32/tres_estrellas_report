
# comunication to evolition_api
from flask import Flask, request

app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():

    payload = request.json

    sender_name = payload["data"]["pushName"]
    phone_number = payload["sender"].split("@")[0]
    message = payload["data"]["message"]["conversation"]
    headers = dict(request.headers)
    body_bits = request.get_data()
    body_json = request.json

    print(sender_name)
    print(message)
    print(phone_number)
    return "OK", 200
app.run(host="0.0.0.0", port=5000)






