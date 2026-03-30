# Core/entities.py

class Order:
    def __init__(self, order_id, side, price, qty):
        self.order_id = order_id
        self.seq_id = 0
        self.side = side
        self.price = price
        self.qty = qty
        self.prev = None
        self.next = None

    def reduce_qty(self, amount):
        if amount > self.qty:
            raise ValueError("Amount exceeds current quantity")
        self.qty -= amount

class LimitOrder(Order):
    def __init__(self, order_id, side, price, qty):
        super().__init__(order_id, side, price, qty)

class PeggedOrder(Order):
    def __init__(self, order_id, side, peg_type, price, qty):
        super().__init__(order_id, side, price, qty)
        self.peg_type = peg_type


