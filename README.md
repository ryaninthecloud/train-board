
# Train Board

### I wanted a train arrivals board at home, so I built this.

## ☕ Project Overview

This project is comprised of a [32x64 LED Matrix Display Board](https://www.waveshare.com/wiki/RGB-Matrix-P3-64x32) attached to an ESP32 embedded microcontroller - that acts as a display controller - which communicates with a customer middleware API. The custom API sits between the display controller and the National Rail Darwin Lite service which provides realtime information on train arrivals and departures for all stations across the UK.

Because of the limited storage and processing power, the middleware API acts as a predictable way of interacting with the Darwin service.

## 💭 Architecture

![diagram of architecture](https://github.com/ryaninthecloud/ryaninthecloud.github.io/blob/main/assets/train-board/architecture.png)

### Design Principles

**Predictable Middleware API**
One of the key design choices of this project was to have a predictable API sit between the Darwin Service and the Microcontroller. Predictability in this context meant abstracting away error messages and instead returning simplified messages for the microcontroller to display in the event of an outage of Darwin; an authentication issue or other problem.

Predictability is achieved by only programming the microcontroller to parse messages and display them; the API will always return a 200-code by design (even when it itself encounters an issue) to simplify the handling of states and will return simplified error messages in a standard format for the microcontroller to parse and display.

This means that when changes, enhancements and edge-case additions are required, the work can be completed at the API level and implemented with greater ease than modifying the source code of the microcontroller.

## ⚙️ Technology Stack

**🖥️ Server Side:** Flask, Python, Docker

**💻 ESP32 Client:** C

## 🙏 Acknowledgements

 - [National Rail: Darwin](https://www.nationalrail.co.uk/developers/darwin-data-feeds/) - provides all the data required to run the board.
