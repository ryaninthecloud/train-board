
# Train Board

### I've always wanted a train departure/arrival board in my house, and that's what this project is: my attempt at that.

## ☕ Project Overview

This project is comprised of a [32x64 LED Matrix Display Board](https://www.waveshare.com/wiki/RGB-Matrix-P3-64x32) attached to an ESP32 embedded microcontroller - that acts as a display controller - which communicates with a customer middleware API. The custom API sits between the display controller and the National Rail Darwin Lite service which provides realtime information on train arrivals and departures for all stations across the UK.

Because of the limited storage and processing power, the middleware API acts as a predictable way of interacting with the Darwin service.

## 💭 Architecture

![diagram of architecture](https://github.com/ryaninthecloud/ryaninthecloud.github.io/blob/main/assets/train-board/architecture.png)


## ⚙️ Technology Stack

**🖥️ Server Side:** Flask, Python, Docker

**💻 ESP32 Client:** C

## 🙏 Acknowledgements

 - [National Rail: Darwin](https://www.nationalrail.co.uk/developers/darwin-data-feeds/) - provides all the data required to run the board.
