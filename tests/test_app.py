#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for 5G Signal Visualization Dashboard
================================================
Test suite for the core functions in utils.py.

Run tests with:
    python -m pytest tests/test_app.py -v
    or
    python tests/test_app.py

Coverage:
    - Data loading functionality
    - RSRP color mapping
    - RSRP category classification
    - Map data preparation
"""

import unittest
import sys
import os
import pandas as pd
import numpy as np

# Add parent directory to path for importing utils module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    load_data,
    get_rsrp_color,
    get_rsrp_category,
    prepare_map_data
)


class TestDataLoading(unittest.TestCase):
    """Test cases for data loading functionality."""

    def setUp(self):
        """Create a temporary test CSV file."""
        self.test_data_path = "/tmp/test_signal_data.csv"
        test_data = pd.DataFrame({
            'Latitude': [31.209143, 31.214219, 31.249965],
            'Longitude': [121.482867, 121.484829, 121.453557],
            'CellID': [1926, 1457, 1941],
            'Band': ['n28', 'n78', 'n28'],
            'RSRP_dBm': [-94.94, -105.47, -82.27],
            'SINR_dB': [5.44, 20.67, 18.28],
            'TerminalType': ['Smartphone', 'CPE', 'Smartphone'],
            'Download_Mbps': [138.21, 837.84, 36.23]
        })
        test_data.to_csv(self.test_data_path, index=False)

    def tearDown(self):
        """Clean up temporary test file."""
        if os.path.exists(self.test_data_path):
            os.remove(self.test_data_path)

    def test_load_data_success(self):
        """Test successful data loading from CSV."""
        df = load_data(self.test_data_path)
        self.assertEqual(len(df), 3)
        self.assertIn('Band', df.columns)
        self.assertIn('RSRP_dBm', df.columns)

    def test_load_data_file_not_found(self):
        """Test that FileNotFoundError is raised for non-existent file."""
        with self.assertRaises(FileNotFoundError):
            load_data("nonexistent_file.csv")

    def test_load_data_missing_columns(self):
        """Test that ValueError is raised for missing expected columns."""
        bad_data = pd.DataFrame({
            'Latitude': [31.0],
            'Longitude': [121.0]
        })
        bad_path = "/tmp/bad_data.csv"
        bad_data.to_csv(bad_path, index=False)
        with self.assertRaises(ValueError):
            load_data(bad_path)
        os.remove(bad_path)


class TestRSRPColorMapping(unittest.TestCase):
    """Test cases for RSRP to color mapping functionality."""

    def test_excellent_signal_green(self):
        """Test that RSRP > -90 returns green color."""
        color = get_rsrp_color(-85)
        self.assertEqual(color, [0, 200, 0])

    def test_good_signal_yellow_green(self):
        """Test that -100 < RSRP <= -90 returns yellow-green."""
        color = get_rsrp_color(-95)
        self.assertEqual(color, [128, 200, 0])

    def test_fair_signal_orange(self):
        """Test that -110 < RSRP <= -100 returns orange."""
        color = get_rsrp_color(-105)
        self.assertEqual(color, [255, 165, 0])

    def test_poor_signal_red(self):
        """Test that RSRP <= -110 returns red."""
        color = get_rsrp_color(-115)
        self.assertEqual(color, [255, 0, 0])

    def test_boundary_values(self):
        """Test boundary values of each range."""
        # Boundary at -90
        self.assertEqual(get_rsrp_color(-89), [0, 200, 0])
        self.assertEqual(get_rsrp_color(-90), [128, 200, 0])

        # Boundary at -100
        self.assertEqual(get_rsrp_color(-99), [128, 200, 0])
        self.assertEqual(get_rsrp_color(-100), [255, 165, 0])

        # Boundary at -110
        self.assertEqual(get_rsrp_color(-109), [255, 165, 0])
        self.assertEqual(get_rsrp_color(-110), [255, 0, 0])


class TestRSRPCategory(unittest.TestCase):
    """Test cases for RSRP category classification."""

    def test_excellent_category(self):
        """Test excellent signal category."""
        self.assertEqual(get_rsrp_category(-85), "Excellent (>-90dBm)")

    def test_good_category(self):
        """Test good signal category."""
        self.assertEqual(get_rsrp_category(-95), "Good (-100 to -90dBm)")

    def test_fair_category(self):
        """Test fair signal category."""
        self.assertEqual(get_rsrp_category(-105), "Fair (-110 to -100dBm)")

    def test_poor_category(self):
        """Test poor signal category."""
        self.assertEqual(get_rsrp_category(-115), "Poor (<=-110dBm)")


class TestPrepareMapData(unittest.TestCase):
    """Test cases for data preparation function."""

    def setUp(self):
        """Create test DataFrame."""
        self.df = pd.DataFrame({
            'Latitude': [31.209143, 31.214219],
            'Longitude': [121.482867, 121.484829],
            'CellID': [1926, 1457],
            'Band': ['n28', 'n78'],
            'RSRP_dBm': [-94.94, -105.47],
            'SINR_dB': [5.44, 20.67],
            'TerminalType': ['Smartphone', 'CPE'],
            'Download_Mbps': [138.21, 837.84]
        })

    def test_color_column_added(self):
        """Test that color column is added."""
        result = prepare_map_data(self.df)
        self.assertIn('color', result.columns)

    def test_category_column_added(self):
        """Test that rsrp_category column is added."""
        result = prepare_map_data(self.df)
        self.assertIn('rsrp_category', result.columns)

    def test_color_values_are_lists(self):
        """Test that color values are RGB lists."""
        result = prepare_map_data(self.df)
        for color in result['color']:
            self.assertIsInstance(color, list)
            self.assertEqual(len(color), 3)

    def test_original_dataframe_unchanged(self):
        """Test that original DataFrame is not modified."""
        original_cols = list(self.df.columns)
        prepare_map_data(self.df)
        self.assertEqual(list(self.df.columns), original_cols)


class TestIntegration(unittest.TestCase):
    """Integration tests combining multiple functions."""

    def test_end_to_end_data_flow(self):
        """Test complete data processing pipeline."""
        # Create test data
        test_data = pd.DataFrame({
            'Latitude': np.random.uniform(31.18, 31.28, 10),
            'Longitude': np.random.uniform(121.42, 121.52, 10),
            'CellID': range(1000, 1010),
            'Band': np.random.choice(['n28', 'n41', 'n78'], 10),
            'RSRP_dBm': np.random.uniform(-120, -70, 10),
            'SINR_dB': np.random.uniform(-5, 30, 10),
            'TerminalType': np.random.choice(['Smartphone', 'CPE', 'IoT'], 10),
            'Download_Mbps': np.random.uniform(10, 1000, 10)
        })

        # Process data
        processed = prepare_map_data(test_data)

        # Verify all expected columns exist
        self.assertIn('color', processed.columns)
        self.assertIn('rsrp_category', processed.columns)

        # Verify all rows have valid colors
        for _, row in processed.iterrows():
            color = row['color']
            self.assertIsInstance(color, list)
            self.assertEqual(len(color), 3)
            for c in color:
                self.assertIsInstance(c, int)
                self.assertTrue(0 <= c <= 255)

        # Verify all rows have valid categories
        valid_categories = [
            "Excellent (>-90dBm)",
            "Good (-100 to -90dBm)",
            "Fair (-110 to -100dBm)",
            "Poor (<=-110dBm)"
        ]
        for _, row in processed.iterrows():
            self.assertIn(row['rsrp_category'], valid_categories)


def run_tests():
    """Run all unit tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDataLoading))
    suite.addTests(loader.loadTestsFromTestCase(TestRSRPColorMapping))
    suite.addTests(loader.loadTestsFromTestCase(TestRSRPCategory))
    suite.addTests(loader.loadTestsFromTestCase(TestPrepareMapData))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
