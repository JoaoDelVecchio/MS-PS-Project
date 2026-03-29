# Source/main.py
import bisect

class OrderDoubleLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

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
        self.side = side
        self.qty = qty

# Create class Limit order that inherit Order and has price as attribute
class LimitOrder(Order):
    def __init__(self, order_id, side, price, qty):
        super().__init__(order_id, side, qty)
        self.price = price
        self.prev = None
        self.next = None

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

    def add_limit_order(self, order_id, side, price, qty):
        order = LimitOrder(order_id, side, price, qty)
        self.orders_map[order_id] = order

        if side.lower() == "buy":
            if price not in self.bids_dict:
                self.bids_dict[price] = OrderDoubleLinkedList()
                bisect.insort(self.bids_prices, price)

            self.bids_dict[price].append(order)
        else:
            if price not in self.asks_dict:
                self.asks_dict[price] = OrderDoubleLinkedList()
                bisect.insort(self.asks_prices, price)

            self.asks_dict[price].append(order)
        
        return order_id
    
    def remove_order(self, order_id):
        if order_id not in self.orders_map:
            return
        
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

class MatchingEngine:
    def __init__(self):
        self.id_generator = IdGenerator()
        self.limit_order_book = LimitOrderBook()

    def print_book(self):
        All_positions = self.limit_order_book.get_all_positions()

        print("Buy Orders:")
        for qty, price, order_id in All_positions["buy"]:
            print(f"{qty} @ {price} ({order_id})")

        print("Sell Orders:")
        for qty, price, order_id in All_positions["sell"]:
            print(f"{qty} @ {price} ({order_id})")

    def proccess_limit_order(self, side, price, qty):
        order_id = self.id_generator.generate_id()
        print(f"Order Created: {side} {qty} @ {price} {order_id}")

        remaining_qty = qty

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

                print(f"Trade, price: {trade_price}, qty: {traded_qty}")   
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

                print(f"Trade, price: {trade_price}, qty: {traded_qty}")

        if remaining_qty > 0:
            self.limit_order_book.add_limit_order(order_id, side, price, remaining_qty)

class CommandParser():
    def __init__(self):
        self.matching_engine = MatchingEngine()

    def process(self, command):
        command = command.lower()

        if command == "print book":
            self.matching_engine.print_book()

        if command.startswith("limit"):
            _, side, price, qty = command.split()
            self.matching_engine.proccess_limit_order(side, int(price), int(qty))

            

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