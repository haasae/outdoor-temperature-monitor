# Outdoor Temperature Monitor

Wireless outdoor monitoring with an Arduino Pro Mini sensor node and a Raspberry Pi receiver.

The sensor node reads temperature and humidity from a AM2301/DHT21 sensor, sends the data over nRF24L01+, and then goes back to sleep to save power. The Raspberry Pi receives packets and writes readings to a log file.

## Features

- DHT21 temperature + humidity readings
- nRF24L01+ wireless transport
- Low-power sleep cycle on the sensor node
- Timestamped logging on Raspberry Pi
- Simple packet format (`<Bff>`) for easy extension

## Hardware

### Materials needed

- 1× Raspberry Pi 3B+
- 1× Arduino Pro Mini
- 1× AM2301 (DHT21)
- 2× nRF24L01+

### Build Photos

#### Sensor side

<img width="669" height="737" alt="sensor" src="https://github.com/user-attachments/assets/66f91de4-3b8d-41fa-8a47-9914ab85f6d1" />

#### Receiver side

<img width="541" height="640" alt="server" src="https://github.com/user-attachments/assets/3f2d25ac-d1ed-452b-a48a-44c8c4c0372d" />

## Repository Layout

- `sensor/sensor.ino` – Arduino firmware
- `server/main.py` – Raspberry Pi receiver/logger

## Data Protocol

Current payload format (little-endian):

1. `protocol_id` (`uint8`) – expected value: `0x01`
2. `temperature_c` (`float32`)
3. `humidity_pct` (`float32`)

Python unpack format:

```python
PACK_FMT = "<Bff"  #9 bytes
```

## Configuration

### Sensor Node (`sensor/sensor.ino`)

- nRF24 CE pin: `14`
- nRF24 CSN pin: `10`
- DHT21 data pin: `15`
- Radio channel: `100`
- Data rate: `250kbps`
- PA level: `RF24_PA_MIN`
- TX address: `"0IWSO"`

### Receiver (`server/main.py`)

- pigpio host/port: `localhost:8888`
- nRF24 CE (BCM): `25`
- Reading pipes:
  - Pipe 1: `"0IWSO"`
  - Pipe 2: `"1IWSO"`
- Radio channel: `100`
- Data rate: `250kbps`
- PA level: `MIN`
- Log output: `/home/pi/temp.txt`

## Setup

### 1) Flash the Arduino sensor node

Install Arduino libraries:

- `DHT sensor library`
- `RF24`
- `LowPower`

Then:

1. Open `sensor/sensor.ino` in Arduino IDE.
2. Select the correct board/processor/port for your Pro Mini.
3. Upload the sketch.

### 2) Prepare the Raspberry Pi receiver

Install dependencies (example):

```bash
sudo apt update
sudo apt install -y pigpio python3-pip
pip3 install pigpio
```

> If your RF24 Python wrapper is not already installed, install the one that matches your environment and import path (`from nrf24 import NRF24, ...`).

Start pigpio:

```bash
sudo pigpiod -p 8888
```

Run receiver:

```bash
python3 server/main.py
```

## Runtime Output

Console output shows raw packet data and decoded values.

Logged lines (`/home/pi/temp.txt`) are written as:

```text
YYYY-MM-DD HH:MM:SS, <temperature_c>, <humidity_pct>
```

## Troubleshooting

- No data received:
  - Confirm both radios use the same channel, data rate, and addresses.
  - Check wiring for CE/CSN/SPI pins.
- `Cannot connect to pigpiod`:
  - Ensure daemon is running and port matches the script.
- Unstable nRF24 behavior:
  - Add a capacitor near nRF24 power pins (common hardware fix).
- Payload decode errors:
  - Keep Arduino payload packing and Python `PACK_FMT` in sync.

## Future Improvements

- Add CRC checksum in payload
- Add sensor ID to payload for multi-support
- Publish data to MQTT 
- Add receiver-side tests for payload packing/unpacking
