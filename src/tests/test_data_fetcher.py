import unittest
import pandas as pd
import numpy as np
import tempfile
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.fetcher import DataFetcher

class TestDataFetcher(unittest.TestCase):
    def test_basic_functionality(self):
        fetcher = DataFetcher(cache_enabled=False)
        self.assertIsNotNone(fetcher)
        
if __name__ == '__main__':
    unittest.main()
