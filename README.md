
# Train Board

## 📷 How's it Looking?

![photo of display](https://github.com/ryaninthecloud/ryaninthecloud.github.io/blob/main/assets/train-board/demo_photo_01.jpg?raw=true)

## ☕ Project Overview

This project is comprised of a [32x64 LED Matrix Display Board](https://www.waveshare.com/wiki/RGB-Matrix-P3-64x32) attached to an ESP32 embedded microcontroller - that acts as a display controller - which communicates with a customer middleware API. The custom API sits between the display controller and the National Rail Darwin Lite service which provides realtime information on train arrivals and departures for all stations across the UK.

Because of the limited storage and processing power, the middleware API acts as a predictable way of interacting with the Darwin service.

## 💭 Basic System Architecture

![diagram of architecture](https://github.com/ryaninthecloud/ryaninthecloud.github.io/blob/main/assets/train-board/architecture.png)

## 🧑‍🎨 Design Decisions

### 🎯 Abstracting Microcontroller Responsibility
Due to the storage and processing power limitations of the ESP32, one of the key design decisions made for this project was to abstract as much parsing and processing responsibility away from the microcontroller as possible. This both increases speed of development and simplifies the process for future changes: as modifications only need to be made to one codebase (the middleware).

Therefore, the microcontroller should merely be a conduit for receiving messages from the middleware and then displaying them.

### 🔮 Predictable Middleware API

In order to enable the Abstraction of Responsibility from the microcontroller, this project has a predictable API sitting between the Darwin Service and the Microcontroller. Predictability, in this context, means abstracting errors with Darwin away from the microcontroller, and instead returning simplified messages for the microcontroller to display to indicate an issue.

The Middleware API reaches out to the National Rail Darwin API to receive data for the specified train station, this is returned in XML format. XML can be challenging to parse, and so it makes more sense for the Python middleware to sit between the XML and the microcontroller, with the Python API passing a simplified JSON of information to display straight to the microcontroller - thusly, abstracting parsing and processing responsibility from the microcontroller.

The microcontroller makes a GET request to the middleware at a set interval to receive new information to display.

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

**📊 Embedded Train Services response template:**

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

❌ Examples of errors returned for display are:

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

### 📺 Display Efficacy

The process of receiving and displaying information on a matrix display is quite simple; but one of the key challenges with this project was ensuring that the information displayed in a readable and authentic fashion. In order to achieve a consistent, readable display output the matrix display is broken down into a series of sections that are written to - as below.

![diagram of matrix display](https://github.com/ryaninthecloud/ryaninthecloud.github.io/blob/main/assets/train-board/matrix-design.png)

In the C code, each of the sections above are given position integers for the display cursor to begin writing to. The display writing posed a challenge for consitency, so there are some design choices that were made to make life easier when displaying information.

**📍 Destination Length**

When destinations are too long, they look messy, this is because they overwrite the pixels of other display segments. Therefore, ```shorten_text_to_space()``` function was implemented. This function takes the string to be displayed and the maximum number of pixels available to display the string, if the string is too long for that space, the function recursively shortens the string until it fits within the specified space.

**⏲️ Consistent Time Display**

Initially, the time segment was one whole series of pixels. However, this meant that the colon that separates the time was in different locations on different lines and it looked off. Therefore, the ```set_update_time_data()``` function was implemented to split the time up into consistently placed segements, as seen in the diagram. T1 represents the first two digits in the time (i.e. 22), then a colon is placed at the same location on each line, then the final two digits of the time (i.e. 30).

Where a train is running late, but is providing an expected arrival time - as opposed to saying only 'Delayed' - the microcontroller will take the expected arrival time and display it in the colour red to indicate that the service is running late.

**⚠️ Service Messages**

Service messages are scrolled along the bottom of the screen, as they are too lengthy to properly display on the board.

**❌ Cancelled and Delayed**

Cancelled and Delayed services are handled differently to time units. The middleware will pass 'Cancelled' and 'Delayed' to the controller, and when that happens, the microcontroller is programmed to turn the text red and display either 'CNCL' or 'DLYD'.


### 🔒 Layering in Security

Security is a consideration for this project not just because this is an IoT device that lives on a local network, but because the middelware leverages the Darwin API from National Rail, which requires an API token. This IP token is individually issued and is rate limited to 5m requests a month. Which seems like a lot, but if a bad actor started to abuse that, then you would no longer have a train board at home.

So, there are some rudimentary steps that have been taken to prevent unauthorised access (and more on the way, see [What's Next?](#What's Next?)).

**🧱 IP Restrictions**

One of the co

## ✅ What's Next? 

## ⚙️ Technology Stack

**🖥️ Server Side:** Flask, Python, Docker

**💻 ESP32 Client:** C

## 🙏 Acknowledgements

 - [National Rail: Darwin](https://www.nationalrail.co.uk/developers/darwin-data-feeds/) - provides all the data required to run the board.
