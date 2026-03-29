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
        self.id_generator = IdGenerator()
        self.orders_map = {}
        self.bids_dict = {}
        self.asks_dict = {}
        self.bids_prices = []
        self.asks_prices = []

    def add_limit_order(self, side, price, qty):
        order_id = self.id_generator.generate_id()

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
        

class MatchingEngine:
    def __init__(self):
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
        order_id = self.limit_order_book.add_limit_order(side, price, qty)
        print(f"Order Created: {side} {qty} @ {price} {order_id}")

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