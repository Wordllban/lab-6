from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import mysql.connector
import json
import copy

with open('secret.json') as f:
    SECRET = json.load(f)

    DB_URI = "mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db}".format(
        user=SECRET["user"],
        password=SECRET["password"],
        host=SECRET["host"],
        port=SECRET["port"],
        db=SECRET["db"])

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)


class SmartDevice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float, unique=False)
    operating_voltage_in_watts = db.Column(db.Float, unique=False)
    current_consumption_in_watts = db.Column(db.Float, unique=False)
    model_name = db.Column(db.String(32), unique=False)
    manufacturer = db.Column(db.String(32), unique=False)

    def __init__(self, price=0, operating_voltage_in_watts=0.0, current_consumption_in_watts=0.0,
                 model_name='N/A', manufacturer='N/A'):
        self.price = price
        self.operating_voltage_in_watts = operating_voltage_in_watts
        self.current_consumption_in_watts = current_consumption_in_watts
        self.model_name = model_name
        self.manufacturer = manufacturer


class SmartDeviceSchema(ma.Schema):
    class Meta:
        fields = ('price', 'operating_voltage_in_watts', 'current_consumption_in_watts', 'model_name',
                  'manufacturer', 'bluetooth_connection')


smart_device_schema = SmartDeviceSchema()
smart_devices_schema = SmartDeviceSchema(many=True)


@app.route("/smart_device", methods=["POST"])
def add_smart_device():
    smart_device = SmartDevice(request.json['price'],
                               request.json['operating_voltage_in_watts'],
                               request.json['current_consumption_in_watts'],
                               request.json['model_name'],
                               request.json['manufacturer'])
    db.session.add(smart_device)
    db.session.commit()
    return smart_device_schema.jsonify(smart_device)


@app.route("/smart_device", methods=["GET"])
def get_smart_device():
    all_smart_device = SmartDevice.query.all()
    result = smart_devices_schema.dump(all_smart_device)
    return jsonify(result)


@app.route("/smart_device/<id>", methods=["GET"])
def smart_device_detail(id):
    smart_device = SmartDevice.query.get(id)
    if not smart_device:
        abort(404)
    return smart_device_schema.jsonify(smart_device)


@app.route("/smart_device/<id>", methods=["PUT"])
def smart_device_update(id):
    smart_device = SmartDevice.query.get(id)
    if not smart_device:
        abort(404)
    old_smart_device = copy.deepcopy(smart_device)
    smart_device.price = request.json['price']
    smart_device.operating_voltage_in_watts = request.json['operating_voltage_in_watts']
    smart_device.current_consumption_in_watts = request.json['current_consumption_in_watts']
    smart_device.model_name = request.json['model_name']
    smart_device.manufacturer = request.json['manufacturer']
    db.session.commit()
    return smart_device_schema.jsonify(old_smart_device)


@app.route("/smart_device/<id>", methods=["DELETE"])
def smart_device_delete(id):
    smart_device = SmartDevice.query.get(id)
    if not smart_device:
        abort(404)
    db.session.delete(smart_device)
    db.session.commit()
    return smart_device_schema.jsonify(smart_device)


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True, host='127.0.0.1')
