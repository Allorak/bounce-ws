# Ping Example

## Overview

This example show a primitive way of using the framework. There are:
- PingSender -- sender that can send a "ping" message on demand (using send method). Message structure:
```json
{
    "event": "ping",
    "data": {
        "ping": "ping"
    },
    "timestamp": <timestamp>
}
```
- TimedPingSender -- sender that can sends a "ping_timed" message every second. Message structure:\
```json
{
    "event": "ping_timed",
    "data": {
        "ping": "ping"
    },
    "timestamp": <timestamp>
}
```
- PingHandler -- handler that listens for incoming message with `ping` event, ignores contents of message and uses 
PingSender as a callback sender. Message that handler listens to:
```json
{
    "event": "ping",
    "data": {
        <key is required, but contents are ignored>
    },
    "timestamp": <timestamp>
}
```

## Usage

For using the example the following actions are needed:
0. Install the library and start the `main.py` file via python
1. Connect to the server with WebSockets protocol using the url `http://localhost:8080/ws`
2. Subscribe to the events sending the following message:
```json
{
    "event": "subscribe",
    "data": {
        "events": ["*"]
    },
    "timestamp": <timestamp>
}
```
The message above is used to subscribe to all events, however you can specify only the needed ones:
```json
{
    "event": "subscribe",
    "data": {
        "events": ["ping_timed"] or ["ping"] or ["ping", "ping_timed"]
    },
    "timestamp": <timestamp>
}
```
3. If you subscribed to `ping_timed` event observe the incoming message every second
4. Send `ping` message to the server, it will be processed by server. Message structure is following:
```json
{
    "event": "ping",
    "data": {
    },
    "timestamp": <timestamp>
}
```
If you are subscribed to the `ping` event, you will see a following response:
```json
{
    "event": "ping",
    "data": {
        "ping": "ping"
    },
    "timestamp": <timestamp>
}
```
5. If needed you can unsubscribe from events using the following message:
```json
{
    "event": "unsubscribe",
    "data": {
        "events": ["ping_timed"] or ["ping"] or ["ping", "ping_timed"] or ["*"]
    },
    "timestamp": <timestamp>
}
```