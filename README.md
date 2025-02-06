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

For interacting with the server clients firstly have to subscribe to the needed events sending following message:
```json
{
  "event": "subscribe",
  "data": {
    "events": [<list of event names to subscribe to>]
  },
  "timestamp": "<iso formated send time timestamp without offset>"
}
```
You may specify `"*"` in `"events"` key to subscribe to all events, provided by the server

In a similar way client may unsubscribe from the specified events:
```json
{
  "event": "unsubscribe",
  "data": {
    "events": [<list of event names to unsubscribe from>]
  },
  "timestamp": "<iso formated send time timestamp without offset>"
}
```

Framework provides following options for message exchange:
- Clients can subscribe to the needed events and unsubscribe from them
- Send message using AbstractSender calling "send" method manually
- Send message using TimedAbstractSender calling "send" method repeatedly
- Handle incoming messages with AbstractHandler, discarding messages of the same event with timestamp larger than last handled

## Example

Usage examples can be found in `examples/` folder