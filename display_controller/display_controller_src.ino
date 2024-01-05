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
#define DISPLAY_RED 0xF800
#define DISPLAY_TEXT_SIZE 1
#define WIFI_SSID ""
#define WIFI_PASSWORD ""
#define API_ENDPOINT_ADDRESS ""
#define DISPLAY_REFRESH_TIME_MS 600000
#define SERIAL_BAUD 9600

unsigned long last_refreshed_at = 0;
MatrixPanel_I2S_DMA* train_display_panel = nullptr;
String live_service_data_received;
bool verbose_http_requests = false;

void setup() {
  Serial.begin(SERIAL_BAUD);

  HUB75_I2S_CFG mxconfig(
    PANEL_RES_X,
    PANEL_RES_Y,
    PANEL_CHAIN);
  mxconfig.clkphase = false;
  mxconfig.driver = HUB75_I2S_CFG::FM6047;
  train_display_panel = new MatrixPanel_I2S_DMA(mxconfig);

  Serial.println("CONFIGURING MATRIX DISPLAY");

  configure_matrix_display();
  connect_to_wifi();
}

void loop() {
  if ((millis() - last_refreshed_at) > DISPLAY_REFRESH_TIME_MS) {
    //Check if WiFi Connected
    if (WiFi.status() == WL_CONNECTED) {
      //Make Get Request
      train_display_panel->clearScreen();
      live_service_data_received = make_http_get_request(API_ENDPOINT_ADDRESS);

      if (verbose_http_requests) {
        Serial.println(live_service_data_received);
      }

      StaticJsonDocument<1024> json_doc;
      DeserializationError deserial_error = deserializeJson(json_doc, live_service_data_received);

      if (deserial_error) {
        Serial.println("Deserialisation Failed: ");
        Serial.println(deserial_error.c_str());
        return;
      }

      int service_number = 0;

      for (JsonObject train_service : json_doc["train_services"].as<JsonArray>()) {
        set_update_dispatch_line(train_service, service_number, 0);
        service_number++;
      }

      scroll_text_on_board(json_doc["warning_messages"], 25, 0);

    } else {
      Serial.println("WiFi Error -- No Longer Connected -- Retrying Cx");
      configure_matrix_display();
      connect_to_wifi();
    }
    last_refreshed_at = millis();
  }
}

void configure_matrix_display() {
  /*
  Configure the Matrix Display initially
  with cursor position; style, size and colour
  of font; as well as brightness
  */
  train_display_panel->begin();
  train_display_panel->setBrightness8(255);
  train_display_panel->fillScreen(train_display_panel->color444(0, 0, 0));
  train_display_panel->setCursor(0, 5);
  train_display_panel->setTextColor(DISPLAY_YELLOW);
  train_display_panel->setTextSize(DISPLAY_TEXT_SIZE);
  train_display_panel->setFont(&Picopixel);
}

void connect_to_wifi() {
  /*
  Connect to WiFi Network, outputting 
  IP address to display and serial console 
  once successful connection is made.

  Delay at end to allow time to read IP Address
  */
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.println("Connecting to WiFi");
  train_display_panel->println("Connecting to Net");

  while (WiFi.status() != WL_CONNECTED) {
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

String make_http_get_request(const char* endpoint) {
  /*
  Make HTTP Request to provided endpoint, return String
  of Response or empty braces if error
  Args: 
    char* endpoint = the endpoint to make the request to
  */
  WiFiClient wifi_client;
  HTTPClient http_client;

  http_client.begin(wifi_client, endpoint);

  int http_response_code = http_client.GET();

  String payload = "{}";

  if (http_response_code == 200) {
    Serial.println("Successful HTTP Response with 200");
    payload = http_client.getString();
  } else {
    Serial.println("HTTP Error");
    Serial.println(http_response_code);
  }

  http_client.end();
  return payload;
}

String shorten_text_to_space(String string_to_shorten, int max_pixels_available) {
  /*
  Because of space limitations on various parts of the display,
  this function will shorten the provided string to the space
  available. This is useful when displaying destinations.
  Args:
    max_pixels_available = maximum available pixels, used to reduce string to this size
    string_to_shorten = the string to shorten
  Returns: shortened string
  */
  int16_t x1, y1;
  uint16_t w, h;

  train_display_panel->getTextBounds(string_to_shorten, max_pixels_available, 0, &x1, &y1, &w, &h);
  while (w > max_pixels_available) {
    train_display_panel->getTextBounds(string_to_shorten, max_pixels_available, 0, &x1, &y1, &w, &h);
    string_to_shorten = string_to_shorten.substring(0, (string_to_shorten.length() - 1));
  }
  return string_to_shorten;
}

void set_update_time_data(const String time_data[2], const int line_y_position, const int x_positions[3], bool show_expected) {
  /*
  Updates and sets the time component of the dispatch line.
  Data works off Expected rather than scheduled, so if a train is delayed,
  the train time is displayed in Red.
  If the train is cancelled it displays 'CNCL'.
  If the train is on time it displays the scheduled train time in Yellow.
  Args:
    String time_data = [scheduled, expected train times]
    int line_y_position = which y-line position to update
    int x_positions[3] = [left time x, colon x, right time x positions]
    char force_display = e:expected, s:scheduled (good for alternating delayed messages)
  */

  String scheduled_train_time = time_data[0];
  String expected_train_time = time_data[1];
  String cancellation_value = "Cancelled";
  String ontime_value = "On time";
  String delayed_value = "Delayed";

  train_display_panel->setTextWrap(false);

  if (expected_train_time == delayed_value && !show_expected) {
    train_display_panel->setCursor(x_positions[0], line_y_position);
    train_display_panel->setTextColor(DISPLAY_RED);
    train_display_panel->print("DLYD");
    train_display_panel->setTextColor(DISPLAY_YELLOW);
    return;
  }

  if (expected_train_time == cancellation_value && !show_expected) {
    train_display_panel->setCursor(x_positions[0], line_y_position);
    train_display_panel->setTextColor(DISPLAY_RED);
    train_display_panel->print("CNCL");
    train_display_panel->setTextColor(DISPLAY_YELLOW);
    return;
  }

  String time_first_two_chars, time_last_two_chars;

  if (expected_train_time == ontime_value || show_expected) {
    time_first_two_chars = scheduled_train_time.substring(0, 2);
    time_last_two_chars = scheduled_train_time.substring(3, 5);
  } else {
    time_first_two_chars = expected_train_time.substring(0, 2);
    time_last_two_chars = expected_train_time.substring(3, 5);
    train_display_panel->setTextColor(DISPLAY_RED);
  }

  train_display_panel->setCursor(x_positions[0], line_y_position);
  train_display_panel->print(time_first_two_chars);

  train_display_panel->setCursor(x_positions[1], line_y_position);
  train_display_panel->print(":");

  train_display_panel->setCursor(x_positions[2], line_y_position);
  train_display_panel->print(time_last_two_chars);

  train_display_panel->setTextColor(DISPLAY_YELLOW);
}

void set_update_dispatch_line(JsonObject service_data, int dispatch_row, int component_to_update) {
  /*
  Orchestrates the update and display of the dispatch lines.
  Made up of component functions that support the orderly display of data, such
  as the time and service ordinal number in a consistent format.
  
  For consistent display, display configurations for font size and font are
  modified here.

  Args:
    service_data = the train service data extracted from the api call
    dispatch_row = the row to present the data on, between 0-2 (1-3)
    component_to_update = integer value, for later implementations
  */

  int line_y_position = 0;
  int ordinal_x_position = 0;
  int destination_x_position = 13;
  int time_left_x_position = 47;
  int time_colon_x_position = 54;
  int time_right_x_position = 56;

  train_display_panel->setTextSize(1);
  train_display_panel->setFont(&Picopixel);
  train_display_panel->setTextWrap(false);

  String train_service_ordinal = service_data["ordinal"];
  String train_service_destination = service_data["destination"];
  String train_service_sch_arrival = service_data["sch_arrival"];
  String train_service_exp_arrival = service_data["exp_arrival"];

  switch (dispatch_row) {
    case 0:
      line_y_position = 5;
      break;
    case 1:
      line_y_position = 11;
      break;
    case 2:
      line_y_position = 17;
      break;
  }

  train_service_destination = shorten_text_to_space(train_service_destination, time_left_x_position - destination_x_position - 1);

  //Later implementation to update only specific components when specified;
  switch (component_to_update) {
    case 0:
      train_display_panel->setCursor(ordinal_x_position, line_y_position);
      train_display_panel->print(train_service_ordinal);

      train_display_panel->setCursor(destination_x_position, line_y_position);
      train_display_panel->print(train_service_destination);

      String time_data[2] = { train_service_sch_arrival, train_service_exp_arrival };
      int time_positional_data[3] = { time_left_x_position, time_colon_x_position, time_right_x_position };

      set_update_time_data(time_data, line_y_position, time_positional_data);

      break;
  }
}

void scroll_text_on_board(String text_to_scroll, int y_position, int starting_x_pos){
  /*
  For scrolling text at a given location on the board without clearing the entire board of values
  Args:
    text_to_scroll = text to scroll across the screen
    starting_y_pos = the y position or line position to start the text at
    starting_x_pos = the position to start scrolling the text at
  */
  int16_t x1, y1;
  uint16_t w, h;

  train_display_panel->getTextBounds(text_to_scroll, 0, 0, &x1, &y1, &w, &h);
  train_display_panel->setTextWrap(false);

  int finishing_x_position = 0 - w;
  int current_x_pixel_position = starting_x_pos;

  while(current_x_pixel_position >= finishing_x_position){
    train_display_panel->setCursor(current_x_pixel_position, y_position);
    //clear the desired location of text, can be trimmed down, but 64 across and 7 down covers 1 line of text
    train_display_panel->fillRect(0, y_position-5, 64, 7, train_display_panel->color444(0, 0, 0));
    train_display_panel->print(text_to_scroll);
    --current_x_pixel_position;
    delay(150);
  }
}

