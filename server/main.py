from __future__ import annotations

import sys
import time
import struct
import traceback
from datetime import datetime

import pigpio
from nrf24 import (
    NRF24,
    RF24_PAYLOAD,
    RF24_DATA_RATE,
    RF24_PA,
    RF24_RX_ADDR,
)

HOST = "localhost"
PORT = 8888

ADDR_P1 = "0IWSO"
ADDR_P2 = "1IWSO"

CHANNEL = 100
DATA_RATE = RF24_DATA_RATE.RATE_250KBPS
PA_LEVEL = RF24_PA.MIN

PROTO_EXPECTED = 0x01
PACK_FMT = "<Bff"       
PACK_LEN = struct.calcsize(PACK_FMT) 

LOG_PATH = "/home/pi/temp.txt"


def connect_pigpio(host: str, port: int) -> pigpio.pi:
    pi = pigpio.pi(host, port)
    if not pi.connected:
        print("Cannot connect to pigpiod")
        sys.exit(1)
    return pi


def configure_radio(pi: pigpio.pi) -> NRF24:
    radio = NRF24(
        pi,
        ce=25,
        payload_size=RF24_PAYLOAD.DYNAMIC,
        channel=CHANNEL,
        data_rate=DATA_RATE,
        pa_level=PA_LEVEL,
    )
    radio.set_address_bytes(len(ADDR_P1))
    radio.open_reading_pipe(RF24_RX_ADDR.P1, ADDR_P1)
    radio.open_reading_pipe(RF24_RX_ADDR.P2, ADDR_P2)
    radio.show_registers()
    return radio


def payload_hex(data: bytes | bytearray | list[int]) -> str:
    return ":".join(f"{b:02x}" for b in data)


def sensor_index_from_pipe(pipe: int) -> int:
    return {1: 0, 2: 1}.get(pipe, 99)


def handle_packet(now: datetime, pipe: int, payload: bytes | bytearray | list[int], log_file) -> None:
    proto = payload[0] if payload else -1
    print(
        f"{now:%Y-%m-%d %H:%M:%S.%f}: pipe: {pipe}, len: {len(payload)}, bytes: {payload_hex(payload)}"
    )

    if len(payload) == PACK_LEN and proto == PROTO_EXPECTED:
        proto_id, temp_c, hum = struct.unpack(PACK_FMT, bytes(payload))
        print(f"Protocol: {proto_id}, T: \033[32m{temp_c}\033[0m, H: \033[93m{hum}\033[0m")

        log_file.write(f"{now:%Y-%m-%d %H:%M:%S}, {temp_c}, {hum}\n")
        log_file.flush()

        _sensor_number = sensor_index_from_pipe(pipe) 


def main() -> None:
    pi = connect_pigpio(HOST, PORT)
    radio = configure_radio(pi)

    f = open(LOG_PATH, "a")

    try:
        while True:
            while radio.data_ready():
                now = datetime.now()
                pipe = radio.data_pipe()
                payload = radio.get_payload()
                handle_packet(now, pipe, payload, f)

            time.sleep(0.1)

    except Exception:
        f.close()
        traceback.print_exc()
        radio.power_down()
        pi.stop()


if __name__ == "__main__":
    main()
