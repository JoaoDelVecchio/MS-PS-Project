import unittest
from unittest.mock import patch
import io

from Source.main import CommandParser

class Test_Book_Foundations(unittest.TestCase):
    def setUp(self):
        self.parser = CommandParser()

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_add_one_limit_buy(self, mock_stdout):
        input_cmd = "limit buy 10 100"
        expected_output = "Order Created: buy 100 @ 10 id_1"

        self.parser.process(input_cmd)
        output = mock_stdout.getvalue().strip()

        self.assertEqual(output, expected_output)

        mock_stdout.seek(0)
        mock_stdout.truncate(0)

        input_cmd = "print book"
        expected_output = "Buy Orders:\n100 @ 10 (id_1)\nSell Orders:"

        self.parser.process(input_cmd)
        output = mock_stdout.getvalue().strip()

        self.assertEqual(output, expected_output)