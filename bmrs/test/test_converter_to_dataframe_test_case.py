import json
import pandas as pd

from django.test import TestCase
from bmrs.converters.converter_dict_to_dataframe import ConverterDictToDataFrame


class TestConverterToDataframeTestCase(TestCase):
    """Test cases for the ConverterDictToDataFrame."""
    
    
    def setUp(self):
        """Set up test case dependencies."""
        self.converter_dict_to_dataframe = ConverterDictToDataFrame()


    def test_converter_to_dataframe(self):
        """Test conversion of a dictionary to a pandas DataFrame."""
        # Define the filepath to the JSON file containing the test data.
        filepath = './bmrs/test/data/bmrs_data.json'

        # Read the JSON data into a dictionary.
        with open(filepath, "r") as f:
            bmrs_data = json.load(f)
        
        report_name = 'B1770'
        report_length = len(bmrs_data)
        expected_columns = ['imbalancePriceAmountGBP']

        # Convert the dictionary to a DataFrame using the conversion method.
        bbmrs_dataframe = \
                        self.converter_dict_to_dataframe.convert(report_name=report_name,
                                                                 report_output=bmrs_data
                                                                )

        self.assertIsNotNone(bbmrs_dataframe)
        self.assertIsInstance(bbmrs_dataframe, pd.DataFrame)
        self.assertEqual(len(bbmrs_dataframe), report_length)
        self.assertListEqual(list(bbmrs_dataframe.columns), expected_columns)