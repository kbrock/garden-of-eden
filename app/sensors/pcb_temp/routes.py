from flask import Blueprint, jsonify

import config
from app.lib.lib import check_sensor_guard, convert_temp

from .pcb_temp import get_pcb_temperature

pcb_temp_blueprint = Blueprint("pcb-temp", __name__)
check_sensor = check_sensor_guard(sensor=get_pcb_temperature, sensor_name="PCB Temp")


@pcb_temp_blueprint.route("", methods=["GET"])
@check_sensor
def get_pcb_temp():
    return jsonify({"pcb-temp": convert_temp(get_pcb_temperature()), "unit": config.TEMP_UNIT})
