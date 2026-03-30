# Controlers/command_parser.py
from Core.matching_engine import MatchingEngine
from Views.book_printer import BookPrinter

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
        BookPrinter.print_book(self.matching_engine.limit_order_book)

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
