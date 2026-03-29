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
    
    # Test if you can add a limit buy and a limit sell that directly match, 
    # and if there is no remaining volume from either.
    def test_add_one_limit_buy_and_one_limit_sell_that_match(self):
        self.assert_command("limit buy 10 100", "Order Created: buy 100 @ 10 id_1")
        
        expected_output = "Order Created: sell 100 @ 10 id_2\nTrade, price: 10, qty: 100"
        self.assert_command("limit sell 10 100", expected_output)
        
        self.assert_command("print book", "Buy Orders:\nSell Orders:")

    # Test if you can add a limit sell and then a limit buy that directly match, 
    # and if there is no remaining volume from either.
    def test_add_one_limit_sell_and_one_limit_buy_that_match(self):
        self.assert_command("limit sell 10 100", "Order Created: sell 100 @ 10 id_1")
        
        expected_output = "Order Created: buy 100 @ 10 id_2\nTrade, price: 10, qty: 100"
        self.assert_command("limit buy 10 100", expected_output)
        
        self.assert_command("print book", "Buy Orders:\nSell Orders:")