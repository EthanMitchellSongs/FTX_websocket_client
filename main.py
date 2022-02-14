'''
Simple websocket client to interface with FTX
'''
import asyncio
import json
import websockets


def update_biggest(biggest, data):
    '''
    Updates list of biggest trades
    '''
    total_this_sale = data['price'] * data['size']
    if total_this_sale > biggest[4][0]:
        biggest[4] = [
            total_this_sale, data['price'], data['size'], data['side']
        ]
        biggest.sort(reverse=True)
    return biggest


def output(biggest):
    '''
    Outputs formatted list of biggest trades
    '''

    print("\nNew minute\n")
    print("Biggest trades last minute:")
    print(f"{'Total,': <15} {'Price,': <15} {'Size,': <15} {'Buy/Sell': <15}")
    for i in biggest:
        # Gets messy with long floats
        for j in i:
            print(f"{j: <15}", end="")
        print()
    print()
    biggest = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0],
               [0, 0, 0, 0]]  # More idiomatic way to init list?


async def listen():
    '''
    Websocket listener function and main loop
    Parses messages, and prints biggest 5 trades per minute
    '''
    url = "wss://ftx.com/ws/"

    async with websockets.connect(url) as wsocket:
        await wsocket.send(
            '{"op": "subscribe", "channel": "trades", "market": "BTC-PERP"}')

        curr_time = -1
        biggest = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0],
                   [0, 0, 0, 0]]

        # Main loop
        while True:
            msg = await wsocket.recv()
            parsed = json.loads(msg)

            if "data" in parsed:
                data = parsed["data"][0]
                tmp = data['time'].split(":")

                if tmp[1] == curr_time:
                    biggest = update_biggest(biggest, data)
                else:
                    output(biggest)
                    curr_time = tmp[1]

                print(data)


asyncio.get_event_loop().run_until_complete(listen())
