#include <DHT.h>
#include <RF24.h>
#include <nRF24L01.h>
#include "LowPower.h"

static const uint8_t RF24_CSN_PIN = 10;
static const uint8_t RF24_CE_PIN  = 14;

static const uint8_t  RADIO_CH     = 100;
static const rf24_crclength_e CRC  = RF24_CRC_16;
static const rf24_datarate_e  RATE = RF24_250KBPS;
static const rf24_pa_dbm_e    PA   = RF24_PA_MIN;

static const uint8_t RETRY_DELAY = 2;
static const uint8_t RETRY_COUNT = 5;

static const uint8_t PAYLOAD_CAP = 32;
static const uint8_t PROTOCOL_ID = 0x01;

RF24 radio(RF24_CE_PIN, RF24_CSN_PIN);
DHT  sensor(15, DHT21);

static const uint8_t TX_ADDR[6] = "0IWSO";
static uint8_t buf[PAYLOAD_CAP];

static void initRadio();
static void transmitReading(uint8_t proto, float tempC, float relHum);
static void goToSleepCycle();

void setup() {
  delay(100);
  initRadio();
  radio.printDetails();
  sensor.begin();
}

void loop() {
  // Read sensors
  sensor.begin(); 
  const float hum = sensor.readHumidity();
  const float tmp = sensor.readTemperature();

  // Send packet
  radio.powerUp();
  delay(150);
  transmitReading(PROTOCOL_ID, tmp, hum);
  radio.powerDown();

  delay(150);
  goToSleepCycle();
}

static void transmitReading(uint8_t proto, float tempC, float relHum) {
  uint8_t* p = buf;

  *p++ = proto;

  memcpy(p, &tempC, sizeof(tempC));
  p += sizeof(tempC);

  memcpy(p, &relHum, sizeof(relHum));
  p += sizeof(relHum);

  const uint8_t used = (uint8_t)(p - buf);
  radio.write(buf, used);
}

static void initRadio() {
  radio.begin();
  radio.enableDynamicPayloads();
  radio.setAutoAck(true);

  radio.setPALevel(PA);
  radio.setRetries(RETRY_DELAY, RETRY_COUNT);
  radio.setDataRate(RATE);
  radio.setChannel(RADIO_CH);
  radio.setCRCLength(CRC);

  radio.setPayloadSize(PAYLOAD_CAP);

  radio.openWritingPipe(TX_ADDR);
  radio.stopListening();
}

static void goToSleepCycle() {
  LowPower.powerDown(SLEEP_4S, ADC_OFF, BOD_OFF);
  LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF);
  LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF);
}
