from fastapi import FastAPI

from bounce import WebSocketApi
from bounce.senders import SenderOrchestrator
from bounce.handlers import HandlerOrchestrator

from senders import PingSender
from senders import TimedPingSender
from handlers import PingHandler

def main():
    fastapi_app = FastAPI()

    ping_sender = PingSender()
    timed_ping_sender = TimedPingSender(1)

    ping_handler = PingHandler(ping_sender)

    sender_orchestrator = SenderOrchestrator()
    sender_orchestrator.register_sender(ping_sender)
    sender_orchestrator.register_sender(timed_ping_sender)

    handler_orchestrator = HandlerOrchestrator()
    handler_orchestrator.register_handler(ping_handler)

    api = WebSocketApi(fastapi_app, sender_orchestrator, handler_orchestrator)
    api.start(background=False)

if __name__ == '__main__':
    main()