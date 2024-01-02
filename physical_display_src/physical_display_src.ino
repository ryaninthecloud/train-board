/*
Display Source Code for the https://github.com/ryaninthecloud/train-board
physical display.

This code is designed for an ESP32 Development board with WiFi, combined
with a Waveshare 32x64 LED Matrix display.
*/

#define PANEL_RES_X 64
#define PANEL_RES_Y 32
#define PANEL_CHAIN 1
#define YELLOW 0XFFE0
#define TEXT_SIZE 1
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
  mxconfig.driver = HUB75_I2S_CFG:l:FM6047;
}

void loop() {

}
