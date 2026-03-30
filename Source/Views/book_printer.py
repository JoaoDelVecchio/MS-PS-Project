# Views/book_printer.py

class BookPrinter:
    @staticmethod
    def print_book(limit_order_book):
        positions = limit_order_book.get_all_positions()

        print("Buy Orders:")
        for qty, price, order_id in positions["buy"]:
            print(f"{qty} @ {price:g} ({order_id})")

        print("Sell Orders:")
        for qty, price, order_id in positions["sell"]:
            print(f"{qty} @ {price:g} ({order_id})")
