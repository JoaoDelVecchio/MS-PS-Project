# Core/entities.py

class Order:
    def __init__(self, order_id, side, price, qty):
        self._order_id = order_id
        self._seq_id = 0
        self._side = side
        
        self.price = price
        self.qty = qty
        self.prev = None
        self.next = None

    @property
    def order_id(self):
        return self._order_id

    @property
    def seq_id(self):
        return self._seq_id
    
    @property
    def side(self):
        return self._side

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


