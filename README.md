
# Train Board

### I wanted a train arrivals board at home, so I built this.

## ☕ Project Overview

This project is comprised of a [32x64 LED Matrix Display Board](https://www.waveshare.com/wiki/RGB-Matrix-P3-64x32) attached to an ESP32 embedded microcontroller - that acts as a display controller - which communicates with a customer middleware API. The custom API sits between the display controller and the National Rail Darwin Lite service which provides realtime information on train arrivals and departures for all stations across the UK.

Because of the limited storage and processing power, the middleware API acts as a predictable way of interacting with the Darwin service.

## 💭 Architecture

![diagram of architecture](https://github.com/ryaninthecloud/ryaninthecloud.github.io/blob/main/assets/train-board/architecture.png)

### Design Principles
------

**Predictable Middleware API**\
One of the key design choices of this project was to have a predictable API sit between the Darwin Service and the Microcontroller. Predictability in this context means abstracting errors with Darwin away from the controller, and instead returning simplified messages for the microcontroller to display to indicate an issue.

Predictability is achieved by only programming the microcontroller to parse and display messages in accordance with a defined format. The API will always return a 200-code by design (even when it itself encounters an issue), because, in this system, even the returning an error message for display is considered a successful operation of the middleware. A total failure of the API (i.e. a non-response) is handled by the microcontroller by falling back to a pre-programmed message.

In addition, this means that modifications to the codebase can be done quicker and with greater ease, because changes can be made to the API to handle for new edge-cases, instead of instructing the microcontroller to change its behaviour.

## ⚙️ Technology Stack

**🖥️ Server Side:** Flask, Python, Docker

**💻 ESP32 Client:** C

## 🙏 Acknowledgements

 - [National Rail: Darwin](https://www.nationalrail.co.uk/developers/darwin-data-feeds/) - provides all the data required to run the board.
