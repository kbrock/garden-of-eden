from flask import Blueprint, jsonify

import config
from app.lib.lib import check_sensor_guard, convert_temp

from .temperature import temperature_sensor

temperature_blueprint = Blueprint("temperature", __name__)
check_sensor = check_sensor_guard(sensor=temperature_sensor, sensor_name="Temperature")


@temperature_blueprint.route("", methods=["GET"])
@check_sensor
def get_temperature():
    return jsonify(temperature=convert_temp(temperature_sensor.read()), unit=config.TEMP_UNIT)
