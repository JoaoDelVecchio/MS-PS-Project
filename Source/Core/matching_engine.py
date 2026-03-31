# Core/matching_engine.py
from Core.limit_order_book import LimitOrderBook
from Core.entities import PeggedOrder
from Utils.id_generator import IdGenerator

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
            order.reduce_qty(order.qty - new_qty)
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
                resting_order = self.limit_order_book.get_best_resting_bid()
                if resting_order is None:
                    break

                if price > resting_order.price:
                    break

                traded_qty = min(remaining_qty, resting_order.qty)
                trade_price = resting_order.price

                remaining_qty -= traded_qty
                resting_order.reduce_qty(traded_qty)

                if resting_order.qty == 0:
                    self.limit_order_book.remove_order(resting_order.order_id)

                trades[trade_price] = trades.get(trade_price, 0) + traded_qty

        elif side.lower() == "buy":
            while remaining_qty > 0:
                resting_order = self.limit_order_book.get_best_resting_ask()
                if resting_order is None:
                    break

                if price < resting_order.price:
                    break

                traded_qty = min(remaining_qty, resting_order.qty)
                trade_price = resting_order.price

                remaining_qty -= traded_qty
                resting_order.reduce_qty(traded_qty)

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
                resting_order = self.limit_order_book.get_best_resting_bid()
                if resting_order is None:
                    break

                trade_price = resting_order.price
                traded_qty = min(remaining_qty, resting_order.qty)

                remaining_qty -= traded_qty
                resting_order.reduce_qty(traded_qty)

                if resting_order.qty == 0:
                    self.limit_order_book.remove_order(resting_order.order_id)

                trades[trade_price] = trades.get(trade_price, 0) + traded_qty

        elif side.lower() == "buy":
            while remaining_qty > 0:
                resting_order = self.limit_order_book.get_best_resting_ask()
                if resting_order is None:
                    break

                trade_price = resting_order.price
                traded_qty = min(remaining_qty, resting_order.qty)

                remaining_qty -= traded_qty
                resting_order.reduce_qty(traded_qty)

                if resting_order.qty == 0:
                    self.limit_order_book.remove_order(resting_order.order_id)

                trades[trade_price] = trades.get(trade_price, 0) + traded_qty

        for price, traded_qty in trades.items():
            print(f"Trade, price: {price:g}, qty: {traded_qty}")

        self._check_and_update_pegged(old_limit_bid, old_limit_ask)

    def proccess_pegged_order(self, peg_type, side, qty):
        if peg_type == "bid":
            best_price = self.limit_order_book.get_best_limit_bid_price()
        elif peg_type == "offer":
            best_price = self.limit_order_book.get_best_limit_ask_price()
        else:
            print("Error")
            return
                
        if best_price is None:
            print("Error")
            return

        order_id = self.id_generator.generate_id()
        print(f"Order Created: {side} {qty} @ pegged {order_id}")
        self.limit_order_book.add_pegged_order(order_id, side, peg_type, best_price, qty)
        