from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields, validate, exceptions
import json

with open('SECRET.json') as f:
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
    price = db.Column(db.Integer, unique=False)
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

    def update(self, price, operating_voltage_in_watts, current_consumption_in_watts, model_name, manufacturer):
        self.__init__(price, operating_voltage_in_watts, current_consumption_in_watts, model_name, manufacturer)


def get_device_by_id(id):
    smart_device = SmartDevice.query.get(id)
    if smart_device is None:
        return abort(404)
    return smart_device


@app.errorhandler(exceptions.ValidationError)
def handle_exception(e):
    return e.messages, 400


class SmartDeviceSchema(ma.Schema):
    price = fields.Integer(validate=validate.Regexp)
    operating_voltage_in_watts = fields.Float(validate=validate.Range(0.1, 10000))
    current_consumption_in_watts = fields.Float(validate=validate.Range(0.1, 10000))
    model_name = fields.String(validate=validate.Length(max=80))
    manufacturer = fields.String(validate=validate.Length(max=20))


smart_device_schema = SmartDeviceSchema()
smart_devices_schema = SmartDeviceSchema(many=True)


@app.route("/smart_device", methods=["POST"])
def add_smart_device():
    fields = smart_device_schema.load(request.json)
    new_smart_device = SmartDevice(**fields)

    db.session.add(new_smart_device)
    db.session.commit()

    return smart_device_schema.jsonify(new_smart_device)


@app.route("/smart_device", methods=["GET"])
def get_smart_device():
    all_smart_devices = SmartDevice.query.all()
    result = smart_devices_schema.dump(all_smart_devices)
    return jsonify(result)


@app.route("/smart_device/<id>", methods=["GET"])
def smart_device_detail(id):
    smart_device = get_device_by_id(id)
    if not smart_device:
        abort(404)
    return smart_device_schema.jsonify(smart_device)


@app.route("/smart_device/<id>", methods=["PUT"])
def smart_device_update(id):
    smart_device = get_device_by_id(id)
    fields = smart_device_schema.load(request.json)
    smart_device.update(**fields)

    if not smart_device:
        abort(404)

    db.session.commit()
    return smart_device_schema.jsonify(smart_device)


@app.route("/smart_device/<id>", methods=["DELETE"])
def smart_device_delete(id):
    smart_device = get_device_by_id(id)

    if not smart_device:
        abort(404)

    db.session.delete(smart_device)
    db.session.commit()

    return smart_device_schema.jsonify(smart_device)


if __name__ == '__main__':
    app.run(debug=True)
