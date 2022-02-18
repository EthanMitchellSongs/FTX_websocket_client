'''
Contains Order and Orderbook classes
'''
import zlib

class Order():
    '''
    Used in Orderbook class to maintain individual orders
    '''
    def __init__(self, price: float, size: float):
        self.price = price
        self.size = size

    def __str__(self):
        '''Print price and size'''
        return f"Price: {self.price}, Size: {self.size}"

    def loc_check_string(self):
        '''returns formatted strings for use in calculating checksum'''
        return str(self.price) + ':' + str(self.size) + ':'


# No need to split Bids and Asks
class Bid(Order):
    '''Extends Order (to be deleted once code is converted)'''
    def __init__(self, price, size) -> None:
        Order.__init__(self, price, size)


class Ask(Order):
    '''Extends Order (to be deleted once code is converted)'''
    def __init__(self, price, size) -> None:
        Order.__init__(self, price, size)


class OrderBook():
    '''
    Main class handling orderbook and orderbook updates.
    Uses Order class to maintain a list of orders
    Contains functions to update individual orders, sides, and complete book'''
    # TODO: Handle if orderbook gets off
    # No need for differentiation between Bid/Ask objects
    def __init__(self, parsed):  # snapshot comes from parsed in main
        '''
        Initializes orderbook from snapshot message (type 'partial')
        '''
        snapshot = parsed['data']
        self.checksum_src = snapshot['checksum']
        self.bids = []
        self.asks = []

        self.update_number = 0

        self.init_bids(snapshot)
        self.init_asks(snapshot)

        self.len_bids = len(self.bids)
        self.len_asks = len(self.asks)

        self.checksum_loc = self.checksum()

        print(f"test: {self.checksum_loc}")

        print(f"checksum: {self.checksum_src}\n")

        self.print_bids()
        self.print_asks()

    def init_bids(self, snapshot):
        '''initializes bids'''
        for this_bid in snapshot['bids']:
            self.bids.append(Bid(this_bid[0], this_bid[1]))

    def init_asks(self, snapshot):
        '''initializes asks'''
        for this_ask in snapshot['asks']:
            self.asks.append(Ask(this_ask[0], this_ask[1]))

    def print_bids(self):
        '''prints bids w/ formatting'''
        print("Bids:")
        for bid in self.bids:
            print(bid)

    def print_asks(self):
        '''prints asks w/ formatting'''
        print("Asks:")
        for ask in self.asks:
            print(ask)

    def checksum(self):
        '''calculates crc32 checksum'''
        check_string = ''

        max_len = max(len(self.bids), len(self.asks))

        for i in range(max_len):
            if i < len(self.bids):
                check_string = check_string + self.bids[i].loc_check_string()
            if i < len(self.asks):
                check_string = check_string + self.asks[i].loc_check_string()
        check_string = check_string[0:-1]  # Remove last colon
        return zlib.crc32(bytes(check_string, 'utf-8'))

    def find_by_size(self, size_to_match, order_list):
        '''
        Finds indexes by specified size
        Used to find orders with size 0 for deletion
        '''
        matches = []
        for count, order in enumerate(order_list):
            if order.size == size_to_match:
                matches.append(count)
        return matches

    def update_order(self, order, order_list):
        '''
        Updates an individual order
        '''
        order_exists = False
        # Faster search algorithms
        # If price exists,
        for old_order in order_list:
            if order.price == old_order.price:
                old_order.size = order.size
                order_exists = True
                break
        if order_exists is False:
            order_list.append(order)

    def update_side(self, side_update, order_list, reverse_bool):
        '''
        Updates an entire side (bids or asks)
        '''

        # side_update: either all bids or all asks in an update
        # reverse_bool is true for bids, false for asks
        for new_order in side_update:
            self.update_order(Bid(new_order[0], new_order[1]), order_list)

        # Search for empty orders
        to_del = self.find_by_size(0.0, order_list)
        offset = 0
        for idx in to_del:
            del order_list[idx - offset]
            offset += 1

        order_list.sort(key=lambda x: x.price, reverse=reverse_bool)
        order_list = order_list[0:100]

    def update_all(self, parsed):
        '''
        Updates all orders
        '''
        update = parsed['data']
        print(update)

        self.update_number += 1
        print(f"Update Number: {self.update_number}")

        self.update_side(update['bids'], self.bids, True)
        self.update_side(update['asks'], self.asks, False)

        # self.print_bids()
        # self.print_asks()

        if self.checksum() == update['checksum']:
            print("Groovy!")
        else:
            print("Gnarly!")
