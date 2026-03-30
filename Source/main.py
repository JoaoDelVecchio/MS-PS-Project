# Source/main.py
import bisect

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

class Order:
    def __init__(self, order_id, side, qty):
        self.order_id = order_id
        self.seq_id = 0
        self.side = side
        self.qty = qty
        self.prev = None
        self.next = None

class LimitOrder(Order):
    def __init__(self, order_id, side, price, qty):
        super().__init__(order_id, side, qty)
        self.price = price
        self.prev = None
        self.next = None

class PeggedOrder(Order):
    def __init__(self, order_id, side, peg_type, price, qty):
        super().__init__(order_id, side, qty)
        self.price = price
        self.peg_type = peg_type 

class IdGenerator:
    def __init__(self):
        self.current_id = 0

    def generate_id(self):
        self.current_id += 1
        return f"id_{self.current_id}"

class LimitOrderBook:
    def __init__(self):
        self.orders_map = {}
        self.bids_dict = {}
        self.asks_dict = {}
        self.bids_prices = []
        self.asks_prices = []
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
    
class MatchingEngine:
    def __init__(self):
        self.id_generator = IdGenerator()
        self.limit_order_book = LimitOrderBook()

    def _check_and_update_pegged(self, old_limit_bid, old_limit_ask):
        new_limit_bid = self.limit_order_book.get_best_limit_bid_price()
        new_limit_ask = self.limit_order_book.get_best_limit_ask_price()

        if new_limit_bid is not None and new_limit_bid != old_limit_bid:
            self.limit_order_book.update_pegged_orders('bid', new_limit_bid)
            
        if new_limit_ask is not None and new_limit_ask != old_limit_ask:
            self.limit_order_book.update_pegged_orders('offer', new_limit_ask)

    def print_book(self):
        All_positions = self.limit_order_book.get_all_positions()

        print("Buy Orders:")
        for qty, price, order_id in All_positions["buy"]:
            print(f"{qty} @ {price:g} ({order_id})")

        print("Sell Orders:")
        for qty, price, order_id in All_positions["sell"]:
            print(f"{qty} @ {price:g} ({order_id})")

    def proccess_modify_order(self, order_id, new_price=None, new_qty=None):
        old_limit_bid = self.limit_order_book.get_best_limit_bid_price()
        old_limit_ask = self.limit_order_book.get_best_limit_ask_price()

        order = self.limit_order_book.get_order(order_id)
        if not order:
            print("Error") 
            return
        
        if isinstance(order, PeggedOrder) and new_price is not None:
            print("Error: Cannot modify price of a pegged order")
            return
        
        if new_qty is not None and new_qty <= 0:
            print("Error")
            return

        price_changed = (new_price is not None and new_price != order.price)
        qty_decreased = (new_qty is not None and new_qty < order.qty)
        qty_increased = (new_qty is not None and new_qty > order.qty)

        if not price_changed and not qty_increased and qty_decreased:
            order.qty = new_qty
            print("Order Modified")
            return

        side = order.side
        final_price = new_price if new_price is not None else order.price
        final_qty = new_qty if new_qty is not None else order.qty

        print("Order Modified")
        self.limit_order_book.remove_order(order_id)
        self.proccess_limit_order(side, final_price, final_qty, order_id=order_id)

        self._check_and_update_pegged(old_limit_bid, old_limit_ask)
    
    def proccess_cancel_order(self, order_id):
        old_limit_bid = self.limit_order_book.get_best_limit_bid_price()
        old_limit_ask = self.limit_order_book.get_best_limit_ask_price()
        try:
            self.limit_order_book.remove_order(order_id)
            print(f"Order Cancelled: {order_id}")
            self._check_and_update_pegged(old_limit_bid, old_limit_ask)
        except ValueError:
            print(f"Error: Order {order_id} not found")
    
    def proccess_limit_order(self, side, price, qty, order_id=None):
        old_limit_bid = self.limit_order_book.get_best_limit_bid_price()
        old_limit_ask = self.limit_order_book.get_best_limit_ask_price()

        if order_id is None:
            order_id = self.id_generator.generate_id()
            print(f"Order Created: {side} {qty} @ {price:g} {order_id}")    

        remaining_qty = qty
        trades = {}

        if side.lower() == "sell":
            while remaining_qty > 0:
                best_bid_list = self.limit_order_book.get_best_bid()
                if best_bid_list is None or best_bid_list.head is None:
                    break

                resting_order = best_bid_list.head
                if price > resting_order.price:
                    break

                traded_qty = min(remaining_qty, resting_order.qty)
                trade_price = resting_order.price

                remaining_qty -= traded_qty
                resting_order.qty -= traded_qty

                if resting_order.qty == 0:
                    self.limit_order_book.remove_order(resting_order.order_id)

                trades[trade_price] = trades.get(trade_price, 0) + traded_qty
        elif side.lower() == "buy":
            while remaining_qty > 0:
                best_ask_list = self.limit_order_book.get_best_ask()
                if best_ask_list is None or best_ask_list.head is None:
                    break

                resting_order = best_ask_list.head
                if price < resting_order.price:
                    break

                traded_qty = min(remaining_qty, resting_order.qty)
                trade_price = resting_order.price

                remaining_qty -= traded_qty
                resting_order.qty -= traded_qty

                if resting_order.qty == 0:
                    self.limit_order_book.remove_order(resting_order.order_id)

                trades[trade_price] = trades.get(trade_price, 0) + traded_qty

        if remaining_qty > 0:
            self.limit_order_book.add_limit_order(order_id, side, price, remaining_qty)
        
        for price, traded_qty in trades.items():
            print(f"Trade, price: {price:g}, qty: {traded_qty}")

        self._check_and_update_pegged(old_limit_bid, old_limit_ask)

    def proccess_market_order(self, side, qty):
        old_limit_bid = self.limit_order_book.get_best_limit_bid_price()
        old_limit_ask = self.limit_order_book.get_best_limit_ask_price()

        order_id = self.id_generator.generate_id()
        print(f"Order Created: {side} {qty} @ market {order_id}")

        remaining_qty = qty
        trades = {}

        if side.lower() == "sell":
            while remaining_qty > 0:
                best_bid_list = self.limit_order_book.get_best_bid()
                if best_bid_list is None or best_bid_list.head is None:
                    break

                resting_order = best_bid_list.head
                trade_price = resting_order.price
                traded_qty = min(remaining_qty, resting_order.qty)

                remaining_qty -= traded_qty
                resting_order.qty -= traded_qty

                if resting_order.qty == 0:
                    self.limit_order_book.remove_order(resting_order.order_id)

                trades[trade_price] = trades.get(trade_price, 0) + traded_qty

        elif side.lower() == "buy":
            while remaining_qty > 0:
                best_ask_list = self.limit_order_book.get_best_ask()
                if best_ask_list is None or best_ask_list.head is None:
                    break

                resting_order = best_ask_list.head
                trade_price = resting_order.price
                traded_qty = min(remaining_qty, resting_order.qty)

                remaining_qty -= traded_qty
                resting_order.qty -= traded_qty

                if resting_order.qty == 0:
                    self.limit_order_book.remove_order(resting_order.order_id)

                trades[trade_price] = trades.get(trade_price, 0) + traded_qty

        for price, traded_qty in trades.items():
            print(f"Trade, price: {price:g}, qty: {traded_qty}")

        self._check_and_update_pegged(old_limit_bid, old_limit_ask)

    def proccess_pegged_order(self, peg_type, side, qty):
        old_limit_bid = self.limit_order_book.get_best_limit_bid_price()
        old_limit_ask = self.limit_order_book.get_best_limit_ask_price()
        
        price = old_limit_bid if peg_type == "bid" else old_limit_ask
            
        if price is None:
            print("Error")
            return

        order_id = self.id_generator.generate_id()
        print(f"Order Created: {side} {qty} @ pegged {order_id}")
        self.limit_order_book.add_pegged_order(order_id, side, peg_type, price, qty)
        
class CommandParser:
    def __init__(self):
        self.matching_engine = MatchingEngine()

    def process(self, command):
        command = command.strip().lower()
        if not command:
            return

        parts = command.split()
        main_command = parts[0]

        if command == "print book":
            self._parse_print_book()
        elif main_command == "limit":
            self._parse_limit(parts)
        elif main_command == "market":
            self._parse_market(parts)
        elif main_command == "peg":
            self._parse_peg(parts)
        elif main_command == "cancel":
            self._parse_cancel(parts)
        elif main_command == "modify":
            self._parse_modify(parts)
        else:
            print("Error: Invalid command")

    def _parse_print_book(self):
        self.matching_engine.print_book()

    def _parse_limit(self, parts):
        if len(parts) != 4:
            print("Error: Invalid command")
            return
        
        _, side, price_str, qty_str = parts
        
        if side not in ["buy", "sell"]:
            print("Error: Invalid command")
            return

        if '.' in qty_str:
            print("Error: Quantity must be integer")
            return
        
        try:
            qty = int(qty_str)
            price = float(price_str)
        except ValueError:
            print("Error: Invalid command")
            return

        if qty <= 0 or price <= 0:
            print("Error: Quantity and price must be positive")
            return

        self.matching_engine.proccess_limit_order(side, price, qty)

    def _parse_market(self, parts):
        if len(parts) != 3:
            print("Error: Invalid command")
            return
        
        _, side, qty_str = parts
        if side not in ["buy", "sell"]:
            print("Error: Invalid command")
            return

        if '.' in qty_str:
            print("Error: Quantity must be integer")
            return
        
        try:
            qty = int(qty_str)
        except ValueError:
            print("Error: Invalid command")
            return

        if qty <= 0:
            print("Error: Quantity and price must be positive")
            return

        self.matching_engine.proccess_market_order(side, qty)

    def _parse_peg(self, parts):
        if len(parts) != 4:
            print("Error: Invalid command")
            return
        
        _, peg_type, side, qty_str = parts
        if side not in ["buy", "sell"] or peg_type not in ["bid", "offer"]:
            print("Error: Invalid command")
            return

        if '.' in qty_str:
            print("Error: Quantity must be integer")
            return
        
        try:
            qty = int(qty_str)
        except ValueError:
            print("Error: Invalid command")
            return

        if qty <= 0:
            print("Error: Quantity and price must be positive")
            return

        self.matching_engine.proccess_pegged_order(peg_type, side, qty)

    def _parse_cancel(self, parts):
        if len(parts) != 2:
            print("Error: Invalid command")
            return
        
        _, order_id = parts
        self.matching_engine.proccess_cancel_order(order_id)

    def _parse_modify(self, parts):
        if len(parts) < 4 or len(parts) % 2 != 0:
            print("Error: Invalid command")
            return

        order_id = parts[1]
        new_qty = None
        new_price = None
        
        for i in range(2, len(parts), 2):
            key = parts[i]
            value_str = parts[i+1]

            if key == "qty":
                if '.' in value_str:
                    print("Error: Quantity must be integer")
                    return
                try:
                    new_qty = int(value_str)
                except ValueError:
                    print("Error: Invalid command")
                    return
                
                if new_qty <= 0:
                    print("Error: Quantity and price must be positive")
                    return
                    
            elif key == "price":
                try:
                    new_price = float(value_str)
                except ValueError:
                    print("Error: Invalid command")
                    return
                
                if new_price <= 0:
                    print("Error: Quantity and price must be positive")
                    return
            else:
                print("Error: Invalid command")
                return
            
        self.matching_engine.proccess_modify_order(order_id, new_price, new_qty)

def main():
    print("Matching Engine started. Type 'exit' or 'quit' to stop.")
    
    command_parser = CommandParser()

    while True:
        try:
            comando = input(">>> ").strip()
            
            if comando.lower() in ['exit', 'quit']:
                break
                
            if not comando:
                continue
            command_parser.process(comando)
            
        except KeyboardInterrupt:
            print("\nSaindo...")
            break
        except Exception as e:
            print(f"Erro: {e}")

if __name__ == "__main__":
    main()