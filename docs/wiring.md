# MPU6050 Wiring

## Raspberry Pi Zero 2 W

| MPU6050 | Raspberry Pi        |
| ------- | ------------------- |
| VCC     | 3.3V — Pin 1        |
| GND     | GND — Pin 6         |
| SDA     | GPIO2 / SDA — Pin 3 |
| SCL     | GPIO3 / SCL — Pin 5 |

## I²C

Enable I²C:

```bash
sudo raspi-config
```

Then:

```text
Interface Options
→ I2C
→ Enable
```

Check the connection:

```bash
i2cdetect -y 1
```

The MPU6050 should normally appear at address:

```text
0x68
```

If AD0 is pulled HIGH, the address can instead be:

```text
0x69
```

## Important

Power the MPU6050 module according to the module's specifications. For the setup used in this project, the sensor is connected to the Raspberry Pi's 3.3V supply.
