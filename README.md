
# Train Board

I've always wanted a train departure/arrival board in my house, and that's what this project is: my attempt at that.

The physical train board prototype runs on a [32x64 LED Matrix Board](https://www.waveshare.com/wiki/RGB-Matrix-P3-64x32) with an ESP32 for compute. Data is provided by National Rail's Darwin API and a custom Flask web application acts as middleware to communicate between Darwin and the ESP32, as the Darwin API is rich in data, but requires more complex coding to parse; so providing a middleware API gives more flexibility and control over the data going to the ESP32 - and takes the load off the embedded compute module.

![diagram of architecture](https://github.com/ryaninthecloud/ryaninthecloud.github.io/blob/main/assets/train-board/architecture.png)

## Acknowledgements

 - [National Rail: Darwin](https://www.nationalrail.co.uk/developers/darwin-data-feeds/) - provides all the data required to run the board.

## ⚙️ Technology Stack

**🖥️ Server Side:** Flask, Python, Docker

**💻 ESP32 Client:** C

