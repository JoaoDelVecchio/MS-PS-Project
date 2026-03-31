# Core/limit_order_book.py
import bisect
from Core.entities import LimitOrder, PeggedOrder

class OrderDoubleLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def insert_sorted(self, order):
        if not self.head:
            self.head = order
            self.tail = order
        else:
            current = self.tail
            while current is not None and current.seq_id > order.seq_id:
                current = current.prev
            
            if current is None:
                order.next = self.head
                self.head.prev = order
                self.head = order
            else:
                order.next = current.next
                order.prev = current
                if current.next:
                    current.next.prev = order
                else:
                    self.tail = order
                current.next = order

    def append(self, order):
        if not self.head:
            self.head = order
            self.tail = order
        else:
            self.tail.next = order
            order.prev = self.tail
            self.tail = order
    
    def remove(self, order):
        if order.prev:
            order.prev.next = order.next
        else:
            self.head = order.next

        if order.next:
            order.next.prev = order.prev
        else:
            self.tail = order.prev


class LimitOrderBook:
    def __init__(self):
        # orders_map maps order_id to Order objects for O(1) access.
        self.orders_map = {}
        # bids_dict and asks_dict map price levels to doubly linked lists of Orders with same price.
        self.bids_dict = {}
        self.asks_dict = {}
        # bids_prices and asks_prices maintain sorted lists of price levels for quick access to best prices.
        self.bids_prices = []
        self.asks_prices = []
        # pegged_bids and pegged_asks track pegged orders for quick updates when best limit prices change.
        self.pegged_bids = {}
        self.pegged_asks = {}
        self.time_counter = 0

    def _insert_into_price_list(self, order):
        if order.side.lower() == "buy":
            if order.price not in self.bids_dict:
                self.bids_dict[order.price] = OrderDoubleLinkedList()
                bisect.insort(self.bids_prices, order.price)

            self.bids_dict[order.price].insert_sorted(order)
        else:
            if order.price not in self.asks_dict:
                self.asks_dict[order.price] = OrderDoubleLinkedList()
                bisect.insort(self.asks_prices, order.price)

            self.asks_dict[order.price].insert_sorted(order)

    def update_pegged_orders(self, peg_type, new_price):
        pegged_dict = self.pegged_bids if peg_type == 'bid' else self.pegged_asks
        
        for order in list(pegged_dict.values()):
            if order.price != new_price:
                if order.side.lower() == 'buy':
                    price_list = self.bids_dict[order.price]
                    price_list.remove(order)
                    if price_list.head is None:
                        del self.bids_dict[order.price]
                        self.bids_prices.remove(order.price)
                else:
                    price_list = self.asks_dict[order.price]
                    price_list.remove(order)
                    if price_list.head is None:
                        del self.asks_dict[order.price]
                        self.asks_prices.remove(order.price)
                
                order.price = new_price
                self._insert_into_price_list(order)
    
    def add_limit_order(self, order_id, side, price, qty):
        order = LimitOrder(order_id, side, price, qty)

        self.time_counter += 1
        order.seq_id = self.time_counter

        self.orders_map[order_id] = order
        self._insert_into_price_list(order)
    
    def add_pegged_order(self, order_id, side, peg_type, price, qty):
        order = PeggedOrder(order_id, side, peg_type, price, qty)

        self.time_counter += 1
        order.seq_id = self.time_counter

        self.orders_map[order_id] = order
        if peg_type == "bid":
            self.pegged_bids[order_id] = order
        else:
            self.pegged_asks[order_id] = order
        self._insert_into_price_list(order)

    def remove_order(self, order_id):
        if order_id not in self.orders_map:
            raise ValueError("Order not found")
                
        order = self.orders_map[order_id]
        if order.side == 'buy':
            price_list = self.bids_dict[order.price]
            price_list.remove(order)

            if price_list.head is None:
                del self.bids_dict[order.price]
                self.bids_prices.remove(order.price) 
        elif order.side == 'sell':
            price_list = self.asks_dict[order.price]
            price_list.remove(order)

            if price_list.head is None:
                del self.asks_dict[order.price]
                self.asks_prices.remove(order.price)

        del self.orders_map[order_id]
        self.pegged_bids.pop(order_id, None)
        self.pegged_asks.pop(order_id, None)

    def get_order(self, order_id):
        return self.orders_map.get(order_id)
    
    def get_all_positions(self):
        positions = {"buy": [], "sell": []}

        for price in self.bids_prices[::-1]:
            order_list = self.bids_dict[price]
            current_order = order_list.head
            while current_order:
                positions["buy"].append((current_order.qty, current_order.price, current_order.order_id))
                current_order = current_order.next

        for price in self.asks_prices:
            order_list = self.asks_dict[price]
            current_order = order_list.head
            while current_order:
                positions["sell"].append((current_order.qty, current_order.price, current_order.order_id))
                current_order = current_order.next

        return positions

    def get_best_ask(self):
        if not self.asks_prices:
            return None
        return self.asks_dict[self.asks_prices[0]]
    
    def get_best_bid(self):
        if not self.bids_prices:
            return None
        return self.bids_dict[self.bids_prices[-1]]

    def get_best_limit_bid_price(self):
        for price in reversed(self.bids_prices):
            current = self.bids_dict[price].head
            while current:
                if isinstance(current, LimitOrder):
                    return price
                current = current.next
        return None

    def get_best_limit_ask_price(self):
        for price in self.asks_prices:
            current = self.asks_dict[price].head
            while current:
                if isinstance(current, LimitOrder):
                    return price
                current = current.next
        return None

    def get_best_resting_bid(self):
        best_list = self.get_best_bid()
        return best_list.head if best_list else None

    def get_best_resting_ask(self):
        best_list = self.get_best_ask()
        return best_list.head if best_list else None
    