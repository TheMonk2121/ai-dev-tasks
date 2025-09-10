#!/usr/bin/env python3
"""
Test file that should be quarantined - low signal, redundant.
"""

import pytest


def test_redundant_functionality():
    """This test is redundant and should be quarantined"""
    assert 1 + 1 == 2


def test_duplicate_logic():
    """Duplicate of other tests"""
    assert True


def test_low_value():
    """Low value test"""
    assert False is False
