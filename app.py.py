from flask import Flask, render_template, jsonify
from smbus2 import SMBus
import math
import time

app = Flask(__name__)

# ============================================================
# MPU6050 CONFIGURATION
# ============================================================

MPU6050_ADDRESS = 0x68
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B

ACCEL_SCALE = 16384.0   # ±2g
GYRO_SCALE = 131.0      # ±250 °/s

bus = SMBus(1)


# ============================================================
# MPU6050 INITIALIZATION
# ============================================================

def initialize_mpu6050():
    """Wake up the MPU6050."""

    bus.write_byte_data(
        MPU6050_ADDRESS,
        PWR_MGMT_1,
        0x00
    )

    time.sleep(0.1)


# ============================================================
# SIGNED 16-BIT CONVERSION
# ============================================================

def twos_complement(value):
    """Convert unsigned 16-bit value to signed integer."""

    if value & 0x8000:
        return value - 65536

    return value


# ============================================================
# SENSOR READING
# ============================================================

def read_mpu6050():
    """
    Read accelerometer, temperature and gyroscope
    data from the MPU6050.
    """

    data = bus.read_i2c_block_data(
        MPU6050_ADDRESS,
        ACCEL_XOUT_H,
        14
    )

    # ----------------------------
    # Accelerometer
    # ----------------------------

    ax_raw = (data[0] << 8) | data[1]
    ay_raw = (data[2] << 8) | data[3]
    az_raw = (data[4] << 8) | data[5]

    ax = twos_complement(ax_raw) / ACCEL_SCALE
    ay = twos_complement(ay_raw) / ACCEL_SCALE
    az = twos_complement(az_raw) / ACCEL_SCALE

    # ----------------------------
    # Temperature
    # ----------------------------

    temp_raw = (data[6] << 8) | data[7]

    temperature = (
        twos_complement(temp_raw) / 340.0
        + 36.53
    )

    # ----------------------------
    # Gyroscope
    # ----------------------------

    gx_raw = (data[8] << 8) | data[9]
    gy_raw = (data[10] << 8) | data[11]
    gz_raw = (data[12] << 8) | data[13]

    gx = twos_complement(gx_raw) / GYRO_SCALE
    gy = twos_complement(gy_raw) / GYRO_SCALE
    gz = twos_complement(gz_raw) / GYRO_SCALE

    return {
        "accel_x": ax,
        "accel_y": ay,
        "accel_z": az,
        "gyro_x": gx,
        "gyro_y": gy,
        "gyro_z": gz,
        "temperature": temperature
    }


# ============================================================
# ORIENTATION CALCULATION
# ============================================================

def calculate_orientation(ax, ay, az):
    """
    Calculate roll and pitch from the gravity vector.

    This gives stable roll/pitch while the sensor is
    relatively stationary.

    Yaw cannot be obtained from accelerometer data alone.
    """

    roll = math.atan2(ay, az)

    pitch = math.atan2(
        -ax,
        math.sqrt(
            ay * ay +
            az * az
        )
    )

    return (
        math.degrees(roll),
        math.degrees(pitch)
    )


# ============================================================
# ROUTES
# ============================================================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/imu")
def imu():

    sensor = read_mpu6050()

    roll, pitch = calculate_orientation(
        sensor["accel_x"],
        sensor["accel_y"],
        sensor["accel_z"]
    )

    sensor["roll"] = roll
    sensor["pitch"] = pitch

    return jsonify(sensor)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    initialize_mpu6050()

    print("=" * 45)
    print("MPU6050 REAL-TIME DIGITAL TWIN")
    print("=" * 45)
    print("Server running on port 5000")
    print()
    print("Open from another device:")
    print("http://<RASPBERRY_PI_IP>:5000/")
    print()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )