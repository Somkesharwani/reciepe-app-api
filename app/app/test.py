"""
Sample test
"""

from django.test import SimpleTestCase

from app import calc

class CalcTests(SimpleTestCase):
    """Test the calc Module"""
    def test_add_number(self):
        res=calc.add(4,5)
        self.assertEqual(res,9)

    def test_subtract_number(self):
        """Test Subtract functions"""
        res=calc.subtract(10,8)
        self.assertEqual(res,2)