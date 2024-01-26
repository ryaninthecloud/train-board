
# Train Board

## 📷 How's it Looking?

![photo of display](https://github.com/ryaninthecloud/ryaninthecloud.github.io/blob/main/assets/train-board/demo_photo_01.jpg?raw=true)

![video of display](https://github.com/ryaninthecloud/ryaninthecloud.github.io/blob/main/assets/train-board/demo_video_01.mp4)

## ☕ Project Overview

This project is comprised of a [32x64 LED Matrix Display Board](https://www.waveshare.com/wiki/RGB-Matrix-P3-64x32) attached to an ESP32 embedded microcontroller - that acts as a display controller - which communicates with a customer middleware API. The custom API sits between the display controller and the National Rail Darwin Lite service which provides realtime information on train arrivals and departures for all stations across the UK.

Because of the limited storage and processing power, the middleware API acts as a predictable way of interacting with the Darwin service.

## 💭 Architecture

![diagram of architecture](https://github.com/ryaninthecloud/ryaninthecloud.github.io/blob/main/assets/train-board/architecture.png)

### Design Principles
------


**Predictable Middleware API**\
One of the key design choices of this project was to have a predictable API sit between the Darwin Service and the Microcontroller. Predictability, in this context, means abstracting errors with Darwin away from the microcontroller, and instead returning simplified messages for the microcontroller to display to indicate an issue.

Predictability is achieved by only programming the microcontroller to parse and display messages in accordance with a defined format. The API will always return an HTTP 200-code by design (even when it itself encounters an issue), because, in this system, even the returning an error message for display is considered a successful operation of the middleware. A total failure of the API (i.e. a non-response) is handled by the microcontroller by falling back to a pre-programmed message.

In addition, this means that handling for new edge-cases and operability can be easily integrated into the system; where changes to the API must only comply with the defined response format and no changes to the microcontroller are required.

In order to denote a positive or negative response to the microcontroller - so it knows how to parse the message - the API embeds a 'status_code' key into the response API which the microcontroller reads. Each response from the API should contain the following keys: 

```
{
    "response_code": [200 for normal train service display, any other number for error messages],
}
```

**📊 Positive Response (Train Services returned)**

```
{
    "response_status":200,
    "data_for_station":None,
    "warning_messages":None,
    "train_services":None
}
```

- **Data for Station**: the train station full title, i.e. 'London Paddington'
- **Warning Messages**: any National Rail services messages applicable for the station.
- **Train Services**: an array of dictionaries conforming to the standard below 

**Train Services response template:**

```
{
    "ordinal":None,
    "destination":None,
    "sch_arrival":None,
    "exp_arrival":None
}
```

- **Ordinal**: the ordinal position of the service on the board, i.e. 1st, 2nd, 3rd 
- **Destination**: of train service
- **Sch_Arrival**: scheduled arrival time
- **Exp_Arrival**: the expected arrival time of the service

**📊 Negative Response (Error Message returned)**

```
{
    "response_status":500,
    "error_type": "Example Error",
    "error_message": "Message to Display"
}
```

Examples of errors returned for display are:

```
{
    "darwin_connection":"Could not connect to Darwin",
    "darwin_authorisation":"Check Darwin Token",
    "darwin_other":"Other Darwin Error",
    "darwin_station_key":"Check Station Key",
    "internal_auth":"Check IP Allwd",
    "check_logs_api":"Check Logs API"
}
```
## ✅ What's Next? 

## ⚙️ Technology Stack

**🖥️ Server Side:** Flask, Python, Docker

**💻 ESP32 Client:** C

## 🙏 Acknowledgements

 - [National Rail: Darwin](https://www.nationalrail.co.uk/developers/darwin-data-feeds/) - provides all the data required to run the board.
