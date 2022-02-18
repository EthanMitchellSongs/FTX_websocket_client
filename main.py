'''
Simple websocket client to interface with FTX
'''
import asyncio
import json
import websockets
from order_class import OrderBook


async def listen2():
    '''
    Websocket listener function and main loop
    Parses messages, and prints biggest 5 trades per minute
    '''
    url = "wss://ftx.com/ws/"

    async with websockets.connect(url) as wsocket:
        await wsocket.send(
            '{"op": "subscribe", "channel": "orderbook", "market": "BTC-PERP"}'
        )

        idx = 0
        # Main loop
        while idx < 1000:
            msg = await wsocket.recv()
            parsed = json.loads(msg)

            if parsed["type"] == "partial":
                book = OrderBook(parsed)
            elif parsed["type"] == "update":
                book.update_all(parsed)
                idx += 1


asyncio.get_event_loop().run_until_complete(listen2())
