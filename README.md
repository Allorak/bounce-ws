# WS-framework

## Overview

This project is a WebSocket-based framework built with FastAPI and Uvicorn, designed to facilitate real-time communication between the frontend and backend.

## Features

- Real-time WebSocket communication.
- Multi-threaded server for efficient handling of connections.
- Scalable and modular design for easy integration.
- Prebuilt logic for messages

## Installation

To install the project, clone the repository and install the required dependencies:

```bash
git clone https://git.miem.hse.ru/vt3/websocket-api.git
cd websocket-api
pip install -r requirements.txt
```

Alternatively you can use pip to install:

```bash
pip install git+https://git.miem.hse.ru/vt3/websocket-api.git
```

## Core ideas

The main idea is that client and server use websockets for message exchange with specified message structure:
```json
{
  "event": "<event name>",
  "data": "<message payload>",
  "timestamp": "<iso formated send time timestamp without offset>"
}
```

Framework provides following options for message exchange:
- Send message using AbstractSender calling "send" method manually
- Send message using TimedAbstractSender calling "send" method repeatedly
- Handle incoming messages with AbstractHandler, discarding messages of the same event with timestamp larger than last handled

## Example

Usage examples can be found in `examples/` folder