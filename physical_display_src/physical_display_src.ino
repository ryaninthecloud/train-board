/*
Display Source Code for the https://github.com/ryaninthecloud/train-board
physical display.

This code is designed for an ESP32 Development board with WiFi, combined
with a Waveshare 32x64 LED Matrix display.

Styling Guidelines followed: https://www.cs.umd.edu/~nelson/classes/resources/cstyleguide/
*/
#include "ESP32-HUB75-MatrixPanel-I2S-DMA.h"
#include "Fonts/Picopixel.h"
#include <ArduinoJson.h>
#include <ArduinoJson.hpp>
#include <WiFi.h>
#include <HTTPClient.h>

#define PANEL_RES_X 64
#define PANEL_RES_Y 32
#define PANEL_CHAIN 1
#define DISPLAY_YELLOW 0XFFE0
#define DISPLAY_TEXT_SIZE 1
#define WIFI_SSID ssid_here
#define WIFI_PASSWORD ssid_password_here
#define API_ENDPOINT_ADDRESS endpoint_address_here
#define DISPLAY_REFRESH_TIME_MS 5000
#define SERIAL_BAUD 9600

unsigned long last_refreshed_at = 0;
MatrixPanel_I2S_DMA* train_display_panel = nullptr;
String live_service_data_received;

void setup() {
  Serial.begin(SERIAL_BAUD);

  HUB75_I2S_CFG mxconfig(
    PANEL_RES_X,
    PANEL_RES_Y,
    PANEL_CHAIN
  );
  mxconfig.clkphase = false;
  mxconfig.driver = HUB75_I2S_CFG::FM6047;
  rain_display_panel = new MatrixPanel_I2S_DMA(mxconfig);

  Serial.println("CONFIGURING MATRIX DISPLAY");
  
  configure_matrix_display();
  connect_to_wifi();
}

void loop() {
}

void configure_matrix_display(){
  /*
  Configure the Matrix Display initially
  with cursor position; style, size and colour
  of font; as well as brightness
  */
  train_display_panel->begin();
  train_display_panel->setBrightness(255);
  train_display_panel->fillScreen(train_display_panel->color444(0, 0, 0));
  train_display_panel->setCursor(0, 5);
  train_display_panel->setTextColor(DISPLAY_YELLOW);
  train_display_panel->setTextSize(DISPLAY_TEXT_SIZE);
  train_display_panel->setFont(&Picopixel);
}

void connect_to_wifi(){
  /*
  Connect to WiFi Network, outputting 
  IP address to display and serial console 
  once successful connection is made.

  Delay at end to allow time to read IP Address
  */
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.println("Connecting to WiFi");
  train_display_panel->println(("Connecting to Net");

  while(WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("Awaiting WiFi Cx");
  }

  Serial.println("-----");
  Serial.println("Connected with IP: ");
  Serial.print(WiFi.localIP());

  train_display_panel->println("Connected with IP: ");
  train_display_panel->println(WiFi.localIP());

  delay(5000);
}

