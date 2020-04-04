import unittest

from main import create_transaction

class TestStringMethods(unittest.TestCase):

    def test_create_transaction(self):
        self.assertEqual(create_transaction("1.0"), "  - !Transaction\n    Fee: 1.0")

    
if __name__ == '__main__':
    unittest.main()
