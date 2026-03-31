import unittest
from unittest.mock import patch
import io

from Controllers.command_parser import CommandParser

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
    
    def test_add_one_limit_buy_and_one_limit_sell_that_partially_match(self):
        self.assert_command("limit buy 10 100", "Order Created: buy 100 @ 10 id_1")
        
        expected_output = "Order Created: sell 10 @ 10 id_2\nTrade, price: 10, qty: 10"
        self.assert_command("limit sell 10 10", expected_output)
        
        self.assert_command("print book", "Buy Orders:\n90 @ 10 (id_1)\nSell Orders:")

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
    
class Test_MatchingEngine_Cancel_and_Modify(unittest.TestCase):
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

        self.assert_command("modify id_1 price 20", expected_output)
    
    def test_modify_buy_order_increase_price_to_cross_spread(self):
        self.assert_command("limit sell 20 50", "Order Created: sell 50 @ 20 id_1")
        self.assert_command("limit buy 10 50", "Order Created: buy 50 @ 10 id_2")
        
        expected_output = "Order Modified\nTrade, price: 20, qty: 50"
        self.assert_command("modify id_2 price 25", expected_output)

        self.assert_command("print book", "Buy Orders:\nSell Orders:")
    
    def test_modify_sell_order_reduce_price_to_cross_spread(self):
        self.assert_command("limit buy 10 50", "Order Created: buy 50 @ 10 id_1")
        self.assert_command("limit sell 20 50", "Order Created: sell 50 @ 20 id_2")
        
        expected_output = "Order Modified\nTrade, price: 10, qty: 50"
        self.assert_command("modify id_2 price 5", expected_output)

        self.assert_command("print book", "Buy Orders:\nSell Orders:")
    
    def test_modify_buy_order_increase_price_to_cross_spread_and_partially_execute(self):
        self.assert_command("limit sell 20 50", "Order Created: sell 50 @ 20 id_1")
        self.assert_command("limit buy 10 150", "Order Created: buy 150 @ 10 id_2")
        
        expected_output = "Order Modified\nTrade, price: 20, qty: 50"
        self.assert_command("modify id_2 price 25", expected_output)

        self.assert_command("print book", "Buy Orders:\n100 @ 25 (id_2)\nSell Orders:")
    
    def test_modify_sell_order_reduce_price_to_cross_spread_and_partially_execute(self):
        self.assert_command("limit buy 10 50", "Order Created: buy 50 @ 10 id_1")
        self.assert_command("limit sell 20 150", "Order Created: sell 150 @ 20 id_2")
        
        expected_output = "Order Modified\nTrade, price: 10, qty: 50"
        self.assert_command("modify id_2 price 5", expected_output)

        self.assert_command("print book", "Buy Orders:\nSell Orders:\n100 @ 5 (id_2)")
    
    def test_modify_buy_order_increase_price_to_cross_spread_and_consume_multiple_levels(self):
        self.assert_command("limit sell 20 50", "Order Created: sell 50 @ 20 id_1")
        self.assert_command("limit sell 25 50", "Order Created: sell 50 @ 25 id_2")
        self.assert_command("limit buy 10 150", "Order Created: buy 150 @ 10 id_3")
        
        expected_output = "Order Modified\nTrade, price: 20, qty: 50\nTrade, price: 25, qty: 50"
        self.assert_command("modify id_3 price 30", expected_output)

        self.assert_command("print book", "Buy Orders:\n50 @ 30 (id_3)\nSell Orders:")
    
    def test_modify_sell_order_reduce_price_to_cross_spread_and_consume_multiple_levels(self):
        self.assert_command("limit buy 20 50", "Order Created: buy 50 @ 20 id_1")
        self.assert_command("limit buy 25 50", "Order Created: buy 50 @ 25 id_2")
        self.assert_command("limit sell 30 150", "Order Created: sell 150 @ 30 id_3")
        
        expected_output = "Order Modified\nTrade, price: 25, qty: 50\nTrade, price: 20, qty: 50"
        self.assert_command("modify id_3 price 15", expected_output)

        self.assert_command("print book", "Buy Orders:\nSell Orders:\n50 @ 15 (id_3)")
    
    def test_modify_sell_order_to_cross_spread_and_being_tottaly_consumed(self):
        self.assert_command("limit buy 20 50", "Order Created: buy 50 @ 20 id_1")
        self.assert_command("limit buy 25 50", "Order Created: buy 50 @ 25 id_2")
        self.assert_command("limit sell 30 150", "Order Created: sell 150 @ 30 id_3")
        self.assert_command("limit buy 25 50", "Order Created: buy 50 @ 25 id_4")
        
        expected_output = "Order Modified\nTrade, price: 25, qty: 100\nTrade, price: 20, qty: 20"
        self.assert_command("modify id_3 price 15 qty 120", expected_output)

        self.assert_command("print book", "Buy Orders:\n30 @ 20 (id_1)\nSell Orders:")
    
    def test_modify_from_statement(self):
        self.assert_command("limit buy 10 200", "Order Created: buy 200 @ 10 id_1")
        self.assert_command("limit buy 9.99 100", "Order Created: buy 100 @ 9.99 id_2")
        self.assert_command("limit sell 10.5 100", "Order Created: sell 100 @ 10.5 id_3")


        self.assert_command("modify id_1 price 9.98", "Order Modified")
        self.assert_command("print book", "Buy Orders:\n100 @ 9.99 (id_2)\n200 @ 9.98 (id_1)\nSell Orders:\n100 @ 10.5 (id_3)")
    
    def test_pegged_with_limit_behind_it_in_the_queue(self):
        self.assert_command("limit buy 10 100", "Order Created: buy 100 @ 10 id_1")
        self.assert_command("peg bid buy 50", "Order Created: buy 50 @ pegged id_2")
        self.assert_command("limit buy 10 100", "Order Created: buy 100 @ 10 id_3")
        
        self.assert_command("cancel id_1", "Order Cancelled: id_1")
        
        self.assert_command("peg bid buy 20", "Order Created: buy 20 @ pegged id_4")
    
    def test_pegged_order_with_only_pegged_in_book_returns_error(self):
        self.assert_command("peg bid buy 10", "Error")

        self.assert_command("limit buy 10 100", "Order Created: buy 100 @ 10 id_1")
        self.assert_command("peg bid buy 20", "Order Created: buy 20 @ pegged id_2")

        self.assert_command("cancel id_1", "Order Cancelled: id_1")

        expected_book_1 = "Buy Orders:\n20 @ 10 (id_2)\nSell Orders:"
        self.assert_command("print book", expected_book_1)

        self.assert_command("peg bid buy 20", "Error")

        self.assert_command("limit buy 8 100", "Order Created: buy 100 @ 8 id_3")
        
        expected_book_2 = "Buy Orders:\n20 @ 8 (id_2)\n100 @ 8 (id_3)\nSell Orders:"
        self.assert_command("print book", expected_book_2)

class Test_MatchingEngine_Pegged_Orders(unittest.TestCase):
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

    def test_add_pegged_buy_order(self):
        self.assert_command("limit buy 10 200", "Order Created: buy 200 @ 10 id_1")
        self.assert_command("limit buy 9.99 100", "Order Created: buy 100 @ 9.99 id_2")
        self.assert_command("limit sell 10.5 100", "Order Created: sell 100 @ 10.5 id_3")
        
        expected_output = "Order Created: buy 150 @ pegged id_4"
        self.assert_command("peg bid buy 150", expected_output)

        expected_output= "Buy Orders:\n200 @ 10 (id_1)\n150 @ 10 (id_4)\n100 @ 9.99 (id_2)\nSell Orders:\n100 @ 10.5 (id_3)"
        self.assert_command("print book", expected_output)

    def test_add_pegged_sell_order(self):
        self.assert_command("limit buy 10 100", "Order Created: buy 100 @ 10 id_1")
        self.assert_command("limit sell 10.5 200", "Order Created: sell 200 @ 10.5 id_2")
        self.assert_command("limit sell 10.6 100", "Order Created: sell 100 @ 10.6 id_3")
        
        expected_output = "Order Created: sell 150 @ pegged id_4"
        self.assert_command("peg offer sell 150", expected_output)

        expected_output= "Buy Orders:\n100 @ 10 (id_1)\nSell Orders:\n200 @ 10.5 (id_2)\n150 @ 10.5 (id_4)\n100 @ 10.6 (id_3)"
        self.assert_command("print book", expected_output)
    
    def test_pegged_buy_order_update_to_better_price(self):
        self.assert_command("limit sell 20 100", "Order Created: sell 100 @ 20 id_1")
        self.assert_command("peg offer sell 50", "Order Created: sell 50 @ pegged id_2")
        
        expected_output = "Order Created: sell 100 @ 10 id_3"
        self.assert_command("limit sell 10 100", expected_output)

        expected_output= "Buy Orders:\nSell Orders:\n50 @ 10 (id_2)\n100 @ 10 (id_3)\n100 @ 20 (id_1)"
        self.assert_command("print book", expected_output)
    
    def test_pegged_temporal_priority_fallback(self):
        self.assert_command("limit buy 10 100", "Order Created: buy 100 @ 10 id_1")
        self.assert_command("limit buy 20 50", "Order Created: buy 50 @ 20 id_2")
        self.assert_command("peg bid buy 50", "Order Created: buy 50 @ pegged id_3")
        self.assert_command("limit buy 10 80", "Order Created: buy 80 @ 10 id_4")
        self.assert_command("peg bid buy 18", "Order Created: buy 18 @ pegged id_5")
        
        self.assert_command("market sell 60", "Order Created: sell 60 @ market id_6\nTrade, price: 20, qty: 60")

        expected_book = "Buy Orders:\n100 @ 10 (id_1)\n40 @ 10 (id_3)\n80 @ 10 (id_4)\n18 @ 10 (id_5)\nSell Orders:"
        self.assert_command("print book", expected_book)

    def test_market_sell_consumes_limit_and_pegged_at_same_price(self):
        self.assert_command("limit buy 10 100", "Order Created: buy 100 @ 10 id_1")
        self.assert_command("peg bid buy 40", "Order Created: buy 40 @ pegged id_2")
        
        self.assert_command("market sell 140", "Order Created: sell 140 @ market id_3\nTrade, price: 10, qty: 140")
        
        expected_book = "Buy Orders:\nSell Orders:"
        self.assert_command("print book", expected_book)

    def test_limit_crosses_spread_updates_pegs_and_maintains_priority(self):
        self.assert_command("limit buy 20 150", "Order Created: buy 150 @ 20 id_1")
        self.assert_command("peg bid buy 30", "Order Created: buy 30 @ pegged id_2")
        self.assert_command("peg bid buy 20", "Order Created: buy 20 @ pegged id_3")
        self.assert_command("limit sell 30 100", "Order Created: sell 100 @ 30 id_4")
        
        self.assert_command("limit buy 35 110", "Order Created: buy 110 @ 35 id_5\nTrade, price: 30, qty: 100")
        
        expected_book = "Buy Orders:\n30 @ 35 (id_2)\n20 @ 35 (id_3)\n10 @ 35 (id_5)\n150 @ 20 (id_1)\nSell Orders:"
        self.assert_command("print book", expected_book)
    
    def test_limit_crosses_spread_updates_pegs_to_offer(self):
        self.assert_command("limit sell 15 100", "Order Created: sell 100 @ 15 id_1")
        self.assert_command("limit sell 20 100", "Order Created: sell 100 @ 20 id_2")
        self.assert_command("peg offer sell 50", "Order Created: sell 50 @ pegged id_3")

        expected_output = "Order Created: buy 120 @ market id_4\nTrade, price: 15, qty: 120"
        self.assert_command("market buy 120", expected_output)
        
        expected_book = "Buy Orders:\nSell Orders:\n100 @ 20 (id_2)\n30 @ 20 (id_3)"
        self.assert_command("print book", expected_book)
    
    def test_cancel_pegged_order(self):
        self.assert_command("limit sell 15 100", "Order Created: sell 100 @ 15 id_1")
        self.assert_command("peg offer sell 50", "Order Created: sell 50 @ pegged id_2")
        
        self.assert_command("cancel id_2", "Order Cancelled: id_2")

        expected_book = "Buy Orders:\nSell Orders:\n100 @ 15 (id_1)"
        self.assert_command("print book", expected_book)

    def test_modify_pegged_order_decrease_qty(self):
        self.assert_command("limit sell 15 100", "Order Created: sell 100 @ 15 id_1")
        self.assert_command("peg offer sell 50", "Order Created: sell 50 @ pegged id_2")
        self.assert_command("limit sell 15 120", "Order Created: sell 120 @ 15 id_3")
        
        self.assert_command("modify id_2 qty 30", "Order Modified")

        expected_book = "Buy Orders:\nSell Orders:\n100 @ 15 (id_1)\n30 @ 15 (id_2)\n120 @ 15 (id_3)"
        self.assert_command("print book", expected_book)

    def test_modify_pegged_order_increase_qty(self):
        self.assert_command("limit sell 15 100", "Order Created: sell 100 @ 15 id_1")
        self.assert_command("peg offer sell 50", "Order Created: sell 50 @ pegged id_2")
        self.assert_command("limit sell 15 120", "Order Created: sell 120 @ 15 id_3")

        self.assert_command("modify id_2 qty 70", "Order Modified")

        expected_book = "Buy Orders:\nSell Orders:\n100 @ 15 (id_1)\n120 @ 15 (id_3)\n70 @ 15 (id_2)"
        self.assert_command("print book", expected_book)
    
    def test_modify_pegged_buy_order_increase_qty_and_lose_priority_between_pegs(self):
        self.assert_command("limit buy 10 100", "Order Created: buy 100 @ 10 id_1")
        self.assert_command("peg bid buy 30", "Order Created: buy 30 @ pegged id_2")
        self.assert_command("peg bid buy 20", "Order Created: buy 20 @ pegged id_3")
        self.assert_command("limit buy 10 80", "Order Created: buy 80 @ 10 id_4")
        self.assert_command("peg bid buy 18", "Order Created: buy 18 @ pegged id_5")

        self.assert_command("modify id_2 qty 50", "Order Modified")

        expected_book = "Buy Orders:\n100 @ 10 (id_1)\n20 @ 10 (id_3)\n80 @ 10 (id_4)\n18 @ 10 (id_5)\n50 @ 10 (id_2)\nSell Orders:"
        self.assert_command("print book", expected_book)
    

    def test_time_priority_pegged_buy_order_when_bid_is_lowered(self):
        self.assert_command("limit buy 10 100", "Order Created: buy 100 @ 10 id_1")
        self.assert_command("peg bid buy 30", "Order Created: buy 30 @ pegged id_2")
        self.assert_command("peg bid buy 20", "Order Created: buy 20 @ pegged id_3")
        self.assert_command("limit buy 10 80", "Order Created: buy 80 @ 10 id_4")
        self.assert_command("peg bid buy 25", "Order Created: buy 25 @ pegged id_5")

        expected_output = "Order Created: sell 110 @ market id_6\nTrade, price: 10, qty: 110"
        self.assert_command("market sell 110", expected_output)

        self.assert_command("modify id_4 price 9.99", "Order Modified")

        expected_book = "Buy Orders:\n20 @ 9.99 (id_2)\n20 @ 9.99 (id_3)\n25 @ 9.99 (id_5)\n80 @ 9.99 (id_4)\nSell Orders:"
        self.assert_command("print book", expected_book)
    
    def test_modify_pegged_sell_order_when_offer_is_raised(self):
        self.assert_command("limit sell 20 100", "Order Created: sell 100 @ 20 id_1")
        self.assert_command("limit sell 25 100", "Order Created: sell 100 @ 25 id_2")
        self.assert_command("peg offer sell 50", "Order Created: sell 50 @ pegged id_3")

        self.assert_command("modify id_1 price 30", "Order Modified")

        expected_book = "Buy Orders:\nSell Orders:\n100 @ 25 (id_2)\n50 @ 25 (id_3)\n100 @ 30 (id_1)"
        self.assert_command("print book", expected_book)
    
    def test_modify_pegged_sell_order_when_offer_is_lowered(self):
        self.assert_command("limit sell 20 100", "Order Created: sell 100 @ 20 id_1")
        self.assert_command("limit sell 25 100", "Order Created: sell 100 @ 25 id_2")
        self.assert_command("peg offer sell 50", "Order Created: sell 50 @ pegged id_3")

        self.assert_command("modify id_2 price 15", "Order Modified")

        expected_book = "Buy Orders:\nSell Orders:\n50 @ 15 (id_3)\n100 @ 15 (id_2)\n100 @ 20 (id_1)"
        self.assert_command("print book", expected_book)
    
    def test_market_sell_consumes_limit_and_pegged_at_same_price(self):
        self.assert_command("limit buy 10 100", "Order Created: buy 100 @ 10 id_1")
        self.assert_command("peg bid buy 40", "Order Created: buy 40 @ pegged id_2")
        
        self.assert_command("market sell 180", "Order Created: sell 180 @ market id_3\nTrade, price: 10, qty: 140")
        
        expected_book = "Buy Orders:\nSell Orders:"
        self.assert_command("print book", expected_book)
    
    def test_sweep_with_pegged_orders(self):
        self.assert_command("limit sell 20 100", "Order Created: sell 100 @ 20 id_1")
        self.assert_command("limit sell 25 100", "Order Created: sell 100 @ 25 id_2")
        self.assert_command("peg offer sell 50", "Order Created: sell 50 @ pegged id_3")
        self.assert_command("limit sell 30 100", "Order Created: sell 100 @ 30 id_4")
        
        expected_output = "Order Created: buy 300 @ 35 id_5\nTrade, price: 20, qty: 150\nTrade, price: 25, qty: 100\nTrade, price: 30, qty: 50"
        self.assert_command("limit buy 35 300", expected_output)

        expected_book = "Buy Orders:\nSell Orders:\n50 @ 30 (id_4)"
        self.assert_command("print book", expected_book)

    def test_cancel_reference_order_for_pegged_bid(self):
        self.assert_command("limit buy 10 100", "Order Created: buy 100 @ 10 id_1")
        self.assert_command("peg bid buy 50", "Order Created: buy 50 @ pegged id_2")
        self.assert_command("limit buy 8 100", "Order Created: buy 100 @ 8 id_3")
        
        self.assert_command("cancel id_1", "Order Cancelled: id_1")

        expected_book = "Buy Orders:\n50 @ 8 (id_2)\n100 @ 8 (id_3)\nSell Orders:"
        self.assert_command("print book", expected_book)
    
    def test_cancel_reference_order_for_pegged_offer(self):
        self.assert_command("limit sell 20 100", "Order Created: sell 100 @ 20 id_1")
        self.assert_command("peg offer sell 50", "Order Created: sell 50 @ pegged id_2")
        self.assert_command("limit sell 25 100", "Order Created: sell 100 @ 25 id_3")
        
        self.assert_command("cancel id_1", "Order Cancelled: id_1")

        expected_book = "Buy Orders:\nSell Orders:\n50 @ 25 (id_2)\n100 @ 25 (id_3)"
        self.assert_command("print book", expected_book)
    
    def test_modify_price_of_pegged_order(self):
        self.assert_command("limit sell 20 100", "Order Created: sell 100 @ 20 id_1")
        self.assert_command("peg offer sell 50", "Order Created: sell 50 @ pegged id_2")

        self.assert_command("modify id_2 price 25", "Error: Cannot modify price of a pegged order")
    
    

class Test_MatchingEngine_Edge_Cases(unittest.TestCase):
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
    
    def test_invalid_command(self):
        self.assert_command("lmit buy 10 100", "Error: Invalid command")
        self.assert_command("invalid command", "Error: Invalid command")
        self.assert_command("print book extra", "Error: Invalid command")

        self.assert_command("limit buy 10", "Error: Invalid command")
        self.assert_command("limit buy 10 100 extra", "Error: Invalid command")
        self.assert_command("market sell", "Error: Invalid command")
        self.assert_command("market sell 10 extra", "Error: Invalid command")
        self.assert_command("peg bid buy", "Error: Invalid command")
        self.assert_command("peg bid buy 100 extra", "Error: Invalid command")
        self.assert_command("cancel", "Error: Invalid command")
        self.assert_command("cancel id_1 extra", "Error: Invalid command")
        self.assert_command("modify", "Error: Invalid command")
        self.assert_command("modify id_1", "Error: Invalid command")
        self.assert_command("modify id_1 qty", "Error: Invalid command")

        self.assert_command("limit hold 10 100", "Error: Invalid command")
        self.assert_command("market middle 100", "Error: Invalid command")
        self.assert_command("peg middle buy 100", "Error: Invalid command")
        self.assert_command("peg bid hold 100", "Error: Invalid command")
        self.assert_command("modify id_1 volume 100", "Error: Invalid command")

        self.assert_command("limit buy -10 100", "Error: Quantity and price must be positive")
        self.assert_command("limit buy 10 -100", "Error: Quantity and price must be positive")
        self.assert_command("limit buy -10 -100", "Error: Quantity and price must be positive")
        self.assert_command("limit buy 0 100", "Error: Quantity and price must be positive")
        self.assert_command("limit buy 10 0", "Error: Quantity and price must be positive")
        self.assert_command("market sell 0", "Error: Quantity and price must be positive")
        self.assert_command("market sell -50", "Error: Quantity and price must be positive")
        self.assert_command("peg bid buy 0", "Error: Quantity and price must be positive")
        self.assert_command("peg bid buy -10", "Error: Quantity and price must be positive")
        self.assert_command("modify id_1 price 0", "Error: Quantity and price must be positive")
        self.assert_command("modify id_1 price -10", "Error: Quantity and price must be positive")
        self.assert_command("modify id_1 qty 0", "Error: Quantity and price must be positive")
        self.assert_command("modify id_1 qty -10", "Error: Quantity and price must be positive")

        self.assert_command("limit buy 10 14.2", "Error: Quantity must be integer")
        self.assert_command("market sell 12.4", "Error: Quantity must be integer")
        self.assert_command("peg bid buy 10.5", "Error: Quantity must be integer")
        self.assert_command("modify id_1 qty 14.2", "Error: Quantity must be integer")

        self.assert_command("limit buy abc def", "Error: Invalid command")
        self.assert_command("limit buy 10 def", "Error: Invalid command")
        self.assert_command("market sell def", "Error: Invalid command")
        self.assert_command("peg bid buy def", "Error: Invalid command")
        self.assert_command("modify id_1 qty abc", "Error: Invalid command")
        self.assert_command("modify id_1 price abc", "Error: Invalid command")

    