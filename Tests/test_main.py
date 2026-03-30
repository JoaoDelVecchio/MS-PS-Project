import unittest
from unittest.mock import patch
import io

from Source.main import CommandParser

class Test_Book_Foundations(unittest.TestCase):
    def setUp(self):
        self.parser = CommandParser()
        
        self.patcher = patch('sys.stdout', new_callable=io.StringIO)
        self.mock_stdout = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def assert_command(self, command: str, expected_output: str):
        self.parser.process(command)
        output = self.mock_stdout.getvalue().strip()

        self.assertEqual(output, expected_output)
        
        self.mock_stdout.seek(0)
        self.mock_stdout.truncate(0)

    def test_add_one_limit_buy(self):
        self.assert_command("limit buy 10 100", "Order Created: buy 100 @ 10 id_1")
        self.assert_command("print book", "Buy Orders:\n100 @ 10 (id_1)\nSell Orders:")

    def test_add_one_limit_sell(self):
        self.assert_command("limit sell 20 50", "Order Created: sell 50 @ 20 id_1")
        self.assert_command("print book", "Buy Orders:\nSell Orders:\n50 @ 20 (id_1)")

    def test_add_one_limit_buy_and_one_limit_sell(self):
        self.assert_command("limit buy 10 100", "Order Created: buy 100 @ 10 id_1")
        self.assert_command("limit sell 20 50", "Order Created: sell 50 @ 20 id_2")
        self.assert_command("print book", "Buy Orders:\n100 @ 10 (id_1)\nSell Orders:\n50 @ 20 (id_2)")
    
    def test_add_two_limit_buys_with_different_prices(self):
        self.assert_command("limit buy 10 100", "Order Created: buy 100 @ 10 id_1")
        self.assert_command("limit buy 20 50", "Order Created: buy 50 @ 20 id_2")
        self.assert_command("print book", "Buy Orders:\n50 @ 20 (id_2)\n100 @ 10 (id_1)\nSell Orders:")

    def test_add_two_limit_sells_with_different_prices(self):
        self.assert_command("limit sell 10 100", "Order Created: sell 100 @ 10 id_1")
        self.assert_command("limit sell 20 50", "Order Created: sell 50 @ 20 id_2")
        self.assert_command("print book", "Buy Orders:\nSell Orders:\n100 @ 10 (id_1)\n50 @ 20 (id_2)")

    def test_add_two_limit_buys_with_same_price(self):
        self.assert_command("limit buy 10 100", "Order Created: buy 100 @ 10 id_1")
        self.assert_command("limit buy 10 50", "Order Created: buy 50 @ 10 id_2")
        self.assert_command("print book", "Buy Orders:\n100 @ 10 (id_1)\n50 @ 10 (id_2)\nSell Orders:")

    def test_add_two_limit_sells_with_same_price(self):
        self.assert_command("limit sell 10 100", "Order Created: sell 100 @ 10 id_1")
        self.assert_command("limit sell 10 50", "Order Created: sell 50 @ 10 id_2")
        self.assert_command("print book", "Buy Orders:\nSell Orders:\n100 @ 10 (id_1)\n50 @ 10 (id_2)")

class Test_MatchingEngine_Market_and_Limit_Orders(unittest.TestCase):
    def setUp(self):
        self.parser = CommandParser()
        
        self.patcher = patch('sys.stdout', new_callable=io.StringIO)
        self.mock_stdout = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def assert_command(self, command: str, expected_output: str):
        self.parser.process(command)
        output = self.mock_stdout.getvalue().strip()

        self.assertEqual(output, expected_output)
        
        self.mock_stdout.seek(0)
        self.mock_stdout.truncate(0)

    def test_add_one_limit_buy_and_one_limit_sell_that_match(self):
        self.assert_command("limit buy 10 100", "Order Created: buy 100 @ 10 id_1")
        
        expected_output = "Order Created: sell 100 @ 10 id_2\nTrade, price: 10, qty: 100"
        self.assert_command("limit sell 10 100", expected_output)
        
        self.assert_command("print book", "Buy Orders:\nSell Orders:")

    def test_add_one_limit_sell_and_one_limit_buy_that_match(self):
        self.assert_command("limit sell 10 100", "Order Created: sell 100 @ 10 id_1")
        
        expected_output = "Order Created: buy 100 @ 10 id_2\nTrade, price: 10, qty: 100"
        self.assert_command("limit buy 10 100", expected_output)
        
        self.assert_command("print book", "Buy Orders:\nSell Orders:")

    def test_add_one_limit_sell_and_one_market_buy_that_match(self):
        self.assert_command("limit sell 10 100", "Order Created: sell 100 @ 10 id_1")
        
        expected_output = "Order Created: buy 50 @ market id_2\nTrade, price: 10, qty: 50"
        self.assert_command("market buy 50", expected_output)
        
        self.assert_command("print book", "Buy Orders:\nSell Orders:\n50 @ 10 (id_1)")
    
    def test_add_one_limit_buy_and_one_market_sell_that_match(self):
        self.assert_command("limit buy 10 100", "Order Created: buy 100 @ 10 id_1")
        
        expected_output = "Order Created: sell 50 @ market id_2\nTrade, price: 10, qty: 50"
        self.assert_command("market sell 50", expected_output)
        
        self.assert_command("print book", "Buy Orders:\n50 @ 10 (id_1)\nSell Orders:")

    def test_add_one_limit_sell_and_one_market_buy_that_match_with_partial_limit(self):
        self.assert_command("limit sell 10 100", "Order Created: sell 100 @ 10 id_1")
        
        expected_output = "Order Created: buy 150 @ market id_2\nTrade, price: 10, qty: 100"
        self.assert_command("market buy 150", expected_output)
        
        self.assert_command("print book", "Buy Orders:\nSell Orders:")
    
    def test_add_one_limit_sell_and_one_market_buy_that_match_with_partial_market(self):
        self.assert_command("limit sell 10 100", "Order Created: sell 100 @ 10 id_1")
        
        expected_output = "Order Created: buy 50 @ market id_2\nTrade, price: 10, qty: 50"
        self.assert_command("market buy 50", expected_output)
        
        self.assert_command("print book", "Buy Orders:\nSell Orders:\n50 @ 10 (id_1)")
    
    def test_add_one_limit_buy_and_one_market_sell_that_match_with_partial_limit(self):
        self.assert_command("limit buy 10 100", "Order Created: buy 100 @ 10 id_1")
        
        expected_output = "Order Created: sell 150 @ market id_2\nTrade, price: 10, qty: 100"
        self.assert_command("market sell 150", expected_output)
        
        self.assert_command("print book", "Buy Orders:\nSell Orders:")

    def test_add_one_limit_buy_and_one_market_sell_that_match_with_partial_market(self):
        self.assert_command("limit buy 10 100", "Order Created: buy 100 @ 10 id_1")
        
        expected_output = "Order Created: sell 50 @ market id_2\nTrade, price: 10, qty: 50"
        self.assert_command("market sell 50", expected_output)
        
        self.assert_command("print book", "Buy Orders:\n50 @ 10 (id_1)\nSell Orders:")
    
    def test_add_limit_sells_and_one_market_buy_that_consume_one_level(self):
        self.assert_command("limit sell 10 100", "Order Created: sell 100 @ 10 id_1")
        self.assert_command("limit sell 20 80", "Order Created: sell 80 @ 20 id_2")
        
        expected_output = "Order Created: buy 150 @ market id_3\nTrade, price: 10, qty: 100\nTrade, price: 20, qty: 50"
        self.assert_command("market buy 150", expected_output)
        
        self.assert_command("print book", "Buy Orders:\nSell Orders:\n30 @ 20 (id_2)")
    
    def test_add_limit_sells_and_one_market_buy_that_partially_consume_three_levels(self):
        self.assert_command("limit sell 20 20", "Order Created: sell 20 @ 20 id_1")
        self.assert_command("limit sell 25 20", "Order Created: sell 20 @ 25 id_2")
        self.assert_command("limit sell 15 80", "Order Created: sell 80 @ 15 id_3")
        
        expected_output = "Order Created: buy 110 @ market id_4\nTrade, price: 15, qty: 80\nTrade, price: 20, qty: 20\nTrade, price: 25, qty: 10"
        self.assert_command("market buy 110", expected_output)
        
        self.assert_command("print book", "Buy Orders:\nSell Orders:\n10 @ 25 (id_2)")
    
    def test_add_limit_sells_and_one_market_buy_that_consume_two_levels(self):
        self.assert_command("limit sell 20 20", "Order Created: sell 20 @ 20 id_1")
        self.assert_command("limit sell 25 20", "Order Created: sell 20 @ 25 id_2")
        
        expected_output = "Order Created: buy 60 @ market id_3\nTrade, price: 20, qty: 20\nTrade, price: 25, qty: 20"
        self.assert_command("market buy 60", expected_output)
        
        self.assert_command("print book", "Buy Orders:\nSell Orders:")

    def test_add_limit_buys_and_one_market_sell_that_consume_one_level(self):
        self.assert_command("limit buy 10 100", "Order Created: buy 100 @ 10 id_1")
        self.assert_command("limit buy 20 80", "Order Created: buy 80 @ 20 id_2")
        
        expected_output = "Order Created: sell 150 @ market id_3\nTrade, price: 20, qty: 80\nTrade, price: 10, qty: 70"
        self.assert_command("market sell 150", expected_output)
        
        self.assert_command("print book", "Buy Orders:\n30 @ 10 (id_1)\nSell Orders:")
    
    def test_add_limit_buys_and_one_market_sell_that_consume_two_levels(self):
        self.assert_command("limit buy 20 20", "Order Created: buy 20 @ 20 id_1")
        self.assert_command("limit buy 25 20", "Order Created: buy 20 @ 25 id_2")
        
        expected_output = "Order Created: sell 60 @ market id_3\nTrade, price: 25, qty: 20\nTrade, price: 20, qty: 20"
        self.assert_command("market sell 60", expected_output)
        
        self.assert_command("print book", "Buy Orders:\nSell Orders:")
    
    def test_add_limit_buys_and_one_market_sell_that_partially_consume_three_levels(self):
        self.assert_command("limit buy 20 20", "Order Created: buy 20 @ 20 id_1")
        self.assert_command("limit buy 25 20", "Order Created: buy 20 @ 25 id_2")
        self.assert_command("limit buy 15 80", "Order Created: buy 80 @ 15 id_3")
        
        expected_output = "Order Created: sell 110 @ market id_4\nTrade, price: 25, qty: 20\nTrade, price: 20, qty: 20\nTrade, price: 15, qty: 70"
        self.assert_command("market sell 110", expected_output)
        
        self.assert_command("print book", "Buy Orders:\n10 @ 15 (id_3)\nSell Orders:")
    
    def test_add_limit_buys_and_one_market_sell_that_partially_consume_one_level(self):
        self.assert_command("limit buy 20 20", "Order Created: buy 20 @ 20 id_1")
        self.assert_command("limit buy 25 20", "Order Created: buy 20 @ 25 id_2")
        self.assert_command("limit buy 15 80", "Order Created: buy 80 @ 15 id_3")
        
        expected_output = "Order Created: sell 10 @ market id_4\nTrade, price: 25, qty: 10"
        self.assert_command("market sell 10", expected_output)
        
        self.assert_command("print book", "Buy Orders:\n10 @ 25 (id_2)\n20 @ 20 (id_1)\n80 @ 15 (id_3)\nSell Orders:")
    
    def test_add_limit_sells_and_one_market_buy_that_partially_consume_one_level(self):
        self.assert_command("limit sell 20 20", "Order Created: sell 20 @ 20 id_1")
        self.assert_command("limit sell 25 20", "Order Created: sell 20 @ 25 id_2")
        self.assert_command("limit sell 15 80", "Order Created: sell 80 @ 15 id_3")
        
        expected_output = "Order Created: buy 10 @ market id_4\nTrade, price: 15, qty: 10"
        self.assert_command("market buy 10", expected_output)
        
        self.assert_command("print book", "Buy Orders:\nSell Orders:\n70 @ 15 (id_3)\n20 @ 20 (id_1)\n20 @ 25 (id_2)")
    
    def test_add_limit_buys_and_one_market_sell_that_partially_consume_two_levels_with_time_priority(self):
        self.assert_command("limit buy 10 50", "Order Created: buy 50 @ 10 id_1")
        self.assert_command("limit buy 10 50", "Order Created: buy 50 @ 10 id_2")
        self.assert_command("limit buy 10 50", "Order Created: buy 50 @ 10 id_3")
        
        expected_output = "Order Created: sell 70 @ market id_4\nTrade, price: 10, qty: 70"
        self.assert_command("market sell 70", expected_output)
        
        self.assert_command("print book", "Buy Orders:\n30 @ 10 (id_2)\n50 @ 10 (id_3)\nSell Orders:")
    
    def test_add_limit_sells_and_one_market_buy_that_partially_consume_two_levels_with_time_priority(self):
        self.assert_command("limit sell 10 50", "Order Created: sell 50 @ 10 id_1")
        self.assert_command("limit sell 10 50", "Order Created: sell 50 @ 10 id_2")
        self.assert_command("limit sell 10 50", "Order Created: sell 50 @ 10 id_3")
        
        expected_output = "Order Created: buy 70 @ market id_4\nTrade, price: 10, qty: 70"
        self.assert_command("market buy 70", expected_output)
        
        self.assert_command("print book", "Buy Orders:\nSell Orders:\n30 @ 10 (id_2)\n50 @ 10 (id_3)")
    
    def test_limit_order_buy_that_consumes_two_limit_sells_at_same_level_with_time_priority(self):
        self.assert_command("limit sell 10 50", "Order Created: sell 50 @ 10 id_1")
        self.assert_command("limit sell 10 50", "Order Created: sell 50 @ 10 id_2")
        
        expected_output = "Order Created: buy 90 @ 40 id_3\nTrade, price: 10, qty: 90"
        self.assert_command("limit buy 40 90", expected_output)
        
        self.assert_command("print book", "Buy Orders:\nSell Orders:\n10 @ 10 (id_2)")
    
    def test_the_sequence_of_the_statement(self):
        self.assert_command("limit buy 10 100", "Order Created: buy 100 @ 10 id_1")
        self.assert_command("limit sell 20 100", "Order Created: sell 100 @ 20 id_2")
        self.assert_command("limit sell 20 200", "Order Created: sell 200 @ 20 id_3")
        
        expected_output = "Order Created: buy 150 @ market id_4\nTrade, price: 20, qty: 150"
        self.assert_command("market buy 150", expected_output)
        
        expected_output = "Order Created: buy 200 @ market id_5\nTrade, price: 20, qty: 150"
        self.assert_command("market buy 200", expected_output)
        
        expected_output = "Order Created: sell 200 @ market id_6\nTrade, price: 10, qty: 100"
        self.assert_command("market sell 200", expected_output)
        
        self.assert_command("print book", "Buy Orders:\nSell Orders:")
    
class test_MatchingEngine_Cancel_and_Modify(unittest.TestCase):
    def setUp(self):
        self.parser = CommandParser()
        
        self.patcher = patch('sys.stdout', new_callable=io.StringIO)
        self.mock_stdout = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def assert_command(self, command: str, expected_output: str):
        self.parser.process(command)
        output = self.mock_stdout.getvalue().strip()

        self.assertEqual(output, expected_output)
        
        self.mock_stdout.seek(0)
        self.mock_stdout.truncate(0)
    
    def test_add_one_limit_buy_and_cancel_it(self):
        self.assert_command("limit buy 10 100", "Order Created: buy 100 @ 10 id_1")
        self.assert_command("cancel id_1", "Order Cancelled: id_1")
        self.assert_command("print book", "Buy Orders:\nSell Orders:")
    
    def test_add_one_limit_sell_and_cancel_it(self):
        self.assert_command("limit sell 10 100", "Order Created: sell 100 @ 10 id_1")
        self.assert_command("cancel id_1", "Order Cancelled: id_1")
        self.assert_command("print book", "Buy Orders:\nSell Orders:")

    def test_add_two_limit_buy_and_cancel_one(self):
        self.assert_command("limit buy 10 100", "Order Created: buy 100 @ 10 id_1")
        self.assert_command("limit buy 10 50", "Order Created: buy 50 @ 10 id_2")
        self.assert_command("cancel id_1", "Order Cancelled: id_1")
        self.assert_command("print book", "Buy Orders:\n50 @ 10 (id_2)\nSell Orders:")
    
    def test_add_two_limit_sell_and_cancel_one(self):
        self.assert_command("limit sell 10 100", "Order Created: sell 100 @ 10 id_1")
        self.assert_command("limit sell 10 50", "Order Created: sell 50 @ 10 id_2")
        self.assert_command("cancel id_1", "Order Cancelled: id_1")
        self.assert_command("print book", "Buy Orders:\nSell Orders:\n50 @ 10 (id_2)")
     
    def test_partially_consumed_order(self):
        self.assert_command("limit buy 10 100", "Order Created: buy 100 @ 10 id_1")
        
        expected_output = "Order Created: sell 40 @ market id_2\nTrade, price: 10, qty: 40"
        self.assert_command("market sell 40", expected_output)
        
        self.assert_command("cancel id_1", "Order Cancelled: id_1")
        self.assert_command("print book", "Buy Orders:\nSell Orders:")

    def test_cancel_non_existent_order(self):
        self.assert_command("cancel id_999", "Error: Order id_999 not found")

    def test_modify_buy_order_reduce_qty(self):
        self.assert_command("limit buy 10 100", "Order Created: buy 100 @ 10 id_1")
        self.assert_command("modify id_1 qty 50", "Order Modified")
        self.assert_command("print book", "Buy Orders:\n50 @ 10 (id_1)\nSell Orders:")
    
    def test_modify_buy_order_reduce_qty_and_market_sell(self):
        self.assert_command("limit buy 10 100", "Order Created: buy 100 @ 10 id_1")
        self.assert_command("limit buy 10 50", "Order Created: buy 50 @ 10 id_2")
        self.assert_command("modify id_1 qty 50", "Order Modified")
        
        expected_output = "Order Created: sell 60 @ market id_3\nTrade, price: 10, qty: 60"
        self.assert_command("market sell 60", expected_output)
        
        self.assert_command("print book", "Buy Orders:\n40 @ 10 (id_2)\nSell Orders:")
    
    def test_modify_sell_order_reduce_qty(self):
        self.assert_command("limit sell 10 100", "Order Created: sell 100 @ 10 id_1")
        self.assert_command("modify id_1 qty 50", "Order Modified")
        self.assert_command("print book", "Buy Orders:\nSell Orders:\n50 @ 10 (id_1)")
    
    def test_modify_sell_order_reduce_qty_and_market_buy(self):
        self.assert_command("limit sell 10 100", "Order Created: sell 100 @ 10 id_1")
        self.assert_command("limit sell 10 50", "Order Created: sell 50 @ 10 id_2")
        self.assert_command("modify id_1 qty 50", "Order Modified")
        
        expected_output = "Order Created: buy 60 @ market id_3\nTrade, price: 10, qty: 60"
        self.assert_command("market buy 60", expected_output)
        
        self.assert_command("print book", "Buy Orders:\nSell Orders:\n40 @ 10 (id_2)")
    
    def test_modify_buy_order_increase_qty(self):
        self.assert_command("limit buy 10 100", "Order Created: buy 100 @ 10 id_1")
        self.assert_command("modify id_1 qty 150", "Order Modified")
        self.assert_command("print book", "Buy Orders:\n150 @ 10 (id_1)\nSell Orders:")
    
    def test_modify_sell_order_increase_qty(self):
        self.assert_command("limit sell 10 100", "Order Created: sell 100 @ 10 id_1")
        self.assert_command("modify id_1 qty 150", "Order Modified")
        self.assert_command("print book", "Buy Orders:\nSell Orders:\n150 @ 10 (id_1)")
    
    def test_modify_buy_order_increase_price(self):
        self.assert_command("limit buy 10 100", "Order Created: buy 100 @ 10 id_1")
        self.assert_command("modify id_1 price 20", "Order Modified")
        self.assert_command("print book", "Buy Orders:\n100 @ 20 (id_1)\nSell Orders:")
    
    def test_modify_sell_order_increase_price(self):
        self.assert_command("limit sell 10 100", "Order Created: sell 100 @ 10 id_1")
        self.assert_command("modify id_1 price 20", "Order Modified")
        self.assert_command("print book", "Buy Orders:\nSell Orders:\n100 @ 20 (id_1)")

    def test_modify_buy_order_reduce_price(self):
        self.assert_command("limit buy 10 100", "Order Created: buy 100 @ 10 id_1")
        self.assert_command("modify id_1 price 5", "Order Modified")
        self.assert_command("print book", "Buy Orders:\n100 @ 5 (id_1)\nSell Orders:")
    
    def test_modify_sell_order_reduce_price(self):
        self.assert_command("limit sell 10 100", "Order Created: sell 100 @ 10 id_1")
        self.assert_command("modify id_1 price 5", "Order Modified")
        self.assert_command("print book", "Buy Orders:\nSell Orders:\n100 @ 5 (id_1)")
    
    def test_modify_price_and_qty_of_buy_order(self):
        self.assert_command("limit buy 10 100", "Order Created: buy 100 @ 10 id_1")
        self.assert_command("modify id_1 price 20 qty 150", "Order Modified")
        self.assert_command("print book", "Buy Orders:\n150 @ 20 (id_1)\nSell Orders:")
    
    def test_modify_price_and_qty_of_sell_order(self):
        self.assert_command("limit sell 10 100", "Order Created: sell 100 @ 10 id_1")
        self.assert_command("modify id_1 price 20 qty 150", "Order Modified")
        self.assert_command("print book", "Buy Orders:\nSell Orders:\n150 @ 20 (id_1)")
    
    def test_modify_non_existent_order(self):
        self.assert_command("modify id_999 price 20 qty 150", "Error")
    
    def test_modify_buy_order_increase_price_to_same_as_other_buy(self):
        self.assert_command("limit buy 10 50", "Order Created: buy 50 @ 10 id_1")
        self.assert_command("limit buy 20 50", "Order Created: buy 50 @ 20 id_2")
        
        expected_output = "Order Modified"
        self.assert_command("modify id_1 price 20", expected_output)

        self.assert_command("print book", "Buy Orders:\n50 @ 20 (id_2)\n50 @ 20 (id_1)\nSell Orders:")
    
    def test_modify_sell_order_reduce_price_to_same_as_other_sell(self):
        self.assert_command("limit sell 20 50", "Order Created: sell 50 @ 20 id_1")
        self.assert_command("limit sell 10 50", "Order Created: sell 50 @ 10 id_2")
        
        expected_output = "Order Modified"
        self.assert_command("modify id_1 price 10", expected_output)

        self.assert_command("print book", "Buy Orders:\nSell Orders:\n50 @ 10 (id_2)\n50 @ 10 (id_1)")
    
    def test_modify_sell_order_increase_price_to_same_as_other_sell(self):
        self.assert_command("limit sell 20 50", "Order Created: sell 50 @ 20 id_1")
        self.assert_command("limit sell 10 50", "Order Created: sell 50 @ 10 id_2")
        
        expected_output = "Order Modified"
        self.assert_command("modify id_2 price 20", expected_output)

        self.assert_command("print book", "Buy Orders:\nSell Orders:\n50 @ 20 (id_1)\n50 @ 20 (id_2)")
    
    def test_modify_buy_order_reduce_price_to_same_as_other_buy(self):
        self.assert_command("limit buy 10 50", "Order Created: buy 50 @ 10 id_1")
        self.assert_command("limit buy 20 50", "Order Created: buy 50 @ 20 id_2")
        
        expected_output = "Order Modified"
        self.assert_command("modify id_2 price 10", expected_output)

        self.assert_command("print book", "Buy Orders:\n50 @ 10 (id_1)\n50 @ 10 (id_2)\nSell Orders:")