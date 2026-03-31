import matplotlib.pyplot as plt
from collections import defaultdict

class VolumeProfilePrinter:
    @staticmethod
    def print_profile(limit_order_book):
        positions = limit_order_book.get_all_positions()

        bid_vols = defaultdict(int)
        for qty, price, _ in positions["buy"]:
            bid_vols[price] += qty
            
        ask_vols = defaultdict(int)
        for qty, price, _ in positions["sell"]:
            ask_vols[price] += qty

        if not bid_vols and not ask_vols:
            print("O Order Book está vazio. Não há dados para plotar.")
            return

        bid_prices = list(bid_vols.keys())
        bid_quantities = list(bid_vols.values())
        
        ask_prices = list(ask_vols.keys())
        ask_quantities = list(ask_vols.values())

        plt.figure(figsize=(10, 6))
        
        plt.bar(bid_prices, bid_quantities, color='green', alpha=0.7, label='Bids (Demand)', width=0.4)
        plt.bar(ask_prices, ask_quantities, color='red', alpha=0.7, label='Asks (Supply)', width=0.4)
        
        plt.title('Volume Profile - LOB Liquidity Distribution', fontsize=14, fontweight='bold')
        plt.xlabel('Price ($p$)', fontsize=12)
        plt.ylabel('Volume ($V(p)$)', fontsize=12)
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.5)
        
        plt.show()