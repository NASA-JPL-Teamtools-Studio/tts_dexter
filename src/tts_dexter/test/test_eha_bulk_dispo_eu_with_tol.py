import hashlib
import json
import pytest
from pathlib import Path
import pandas as pd
import pdb

from tts_utilities.logger import create_logger
from tts_data_utils.multimission.eha import EhaContainer
from tts_data_utils.multimission.expected_lad import ExpectedLadContainer
from tts_dexter.core.dexter import Dexter
from tts_dexter.dispositioners.eha import LadEhaDispositioner

from demosat_dante.derivers.eha import DemoSatLadChanvalDeriver
from tts_dante.core.dante import Dante
from tts_dante.derivers.eha import LadChanvalDeriver

logger = create_logger(f'dexter.eha_bulk_dispo')
TEST_FILE_DIR = Path(__file__).parent.joinpath('test_files/eha_bulk_dispo')


class LadBulkEhaDispositionerNoTolerance(LadEhaDispositioner):
    CSV_FILEPATH = TEST_FILE_DIR.joinpath('eha_autodispositions.csv')

class EhaBulkDispoTestDante(Dante):
    def __init__(self, chanvals=None, expected_lad=None):
        super().__init__()
        self.init_data(EhaContainer, chanvals)
        self.init_data(ExpectedLadContainer, expected_lad, "expected eha lad")
        self.init_deriver(DemoSatLadChanvalDeriver)

class EhaBulkDispoTestDexter(Dexter):
    def __init__(self, expected_lad=None):
        super().__init__()
        self.init_data(ExpectedLadContainer, expected_lad, "Expected LAD")
        self.init_dispositioner(LadBulkEhaDispositionerNoTolerance)

@pytest.fixture(scope="module")
def eha_container():
    eha_container = EhaContainer(csv_path = TEST_FILE_DIR.joinpath('eu_chanvals_with_tolerance.csv'),cast_fields=True)
    return eha_container

@pytest.fixture(scope="module")
def expected_lad():
    expected_lad = ExpectedLadContainer(csv_path=TEST_FILE_DIR.joinpath('eha_autodispositions.csv'), cast_fields=True)
    return expected_lad

@pytest.fixture(scope="module")
def dante(eha_container, expected_lad):

    dante = EhaBulkDispoTestDante(chanvals=eha_container, expected_lad=expected_lad)
    dante.derive_all()  # This populates the expected_lad with actual values from eha_data

    dex = EhaBulkDispoTestDexter(expected_lad=dante.get_output_data('lad_chanvals.lad_chanvals'))
    dex.disposition_all()
    dex.stamp_all()

    return dante

class TestBulkEhaDispoDnWithTolerance:
    def test_gt(self, dante):
        assert [(e['Expected Value'], e['Actual Value'], e['disposition']) for e in dante.get_output_data('lad_chanvals.lad_chanvals').contains('Channel ID', 'GT-004')] == [
            ('-1.234567', -1.2347, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not greater than -1.234567 within 1e-6</p>'),
            ('-1.234567', -1.234569, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not greater than -1.234567 within 1e-6</p>'),
            ('-1.234567', -1.234568, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not greater than -1.234567 within 1e-6</p>'),
            ('-1.234567', -1.234567, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is greater than -1.234567 within 1e-6</p>'),
            ('-1.234567', -1.234566, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is greater than -1.234567 within 1e-6</p>'),
            ('-1.234567', -1.234567, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is greater than -1.234567 within 1e-6</p>'),
            ('-1.234567', -1.234568, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not greater than -1.234567 within 1e-6</p>')
        ]

    def test_lt(self, dante):
        assert [(e['Expected Value'], e['Actual Value'], e['disposition']) for e in dante.get_output_data('lad_chanvals.lad_chanvals').contains('Channel ID', 'LT-004')] == [
            ('1.234567', 1.234564, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is less than 1.234567 within 1e-6</p>'),
            ('1.234567', 1.234565, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is less than 1.234567 within 1e-6</p>'),
            ('1.234567', 1.234566, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is less than 1.234567 within 1e-6</p>'),
            ('1.234567', 1.234567, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is less than 1.234567 within 1e-6</p>'),
            ('1.234567', 1.234568, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not less than 1.234567 within 1e-6</p>'),
            ('1.234567', 1.234569, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not less than 1.234567 within 1e-6</p>'),
            ('1.234567', 1.23457, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not less than 1.234567 within 1e-6</p>')
        ]

    def test_gte(self, dante):
        assert [(e['Expected Value'], e['Actual Value'], e['disposition']) for e in dante.get_output_data('lad_chanvals.lad_chanvals').contains('Channel ID', 'GTE-004')] == [
            ('-1.234567', -1.2347, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not greater than or equal to -1.234567 within 1e-6</p>'),
            ('-1.234567', -1.234569, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not greater than or equal to -1.234567 within 1e-6</p>'),
            ('-1.234567', -1.234568, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is greater than or equal to -1.234567 within 1e-6</p>'),
            ('-1.234567', -1.234567, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is greater than or equal to -1.234567 within 1e-6</p>'),
            ('-1.234567', -1.234566, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is greater than or equal to -1.234567 within 1e-6</p>'),
            ('-1.234567', -1.234567, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is greater than or equal to -1.234567 within 1e-6</p>'),
            ('-1.234567', -1.234568, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is greater than or equal to -1.234567 within 1e-6</p>')
        ]

    def test_lte(self, dante):
        assert [(e['Expected Value'], e['Actual Value'], e['disposition']) for e in dante.get_output_data('lad_chanvals.lad_chanvals').contains('Channel ID', 'LTE-004')] == [
            ('1.234567', 1.234564, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is less than or equal to 1.234567 within 1e-6</p>'),
            ('1.234567', 1.234565, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is less than or equal to 1.234567 within 1e-6</p>'),
            ('1.234567', 1.234566, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is less than or equal to 1.234567 within 1e-6</p>'),
            ('1.234567', 1.234567, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is less than or equal to 1.234567 within 1e-6</p>'),
            ('1.234567', 1.234568, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is less than or equal to 1.234567 within 1e-6</p>'),
            ('1.234567', 1.234569, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not less than or equal to 1.234567 within 1e-6</p>'),
            ('1.234567', 1.23457, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not less than or equal to 1.234567 within 1e-6</p>')
        ]

    def test_eq(self, dante):
        assert [(e['Expected Value'], e['Actual Value'], e['disposition']) for e in dante.get_output_data('lad_chanvals.lad_chanvals').contains('Channel ID', 'EQ-004')] == [
            ('-1.234567', -1.2347, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not equal to -1.234567 within 1e-6</p>'),
            ('-1.234567', -1.234569, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not equal to -1.234567 within 1e-6</p>'),
            ('-1.234567', -1.234568, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is equal to -1.234567 within 1e-6</p>'),
            ('-1.234567', -1.234567, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is equal to -1.234567 within 1e-6</p>'),
            ('-1.234567', -1.234566, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is equal to -1.234567 within 1e-6</p>'),
            ('-1.234567', -1.234565,  '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not equal to -1.234567 within 1e-6</p>'),
            ('-1.234567', -1.234564,  '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not equal to -1.234567 within 1e-6</p>')
        ]

    def test_ne(self, dante):
        assert [(e['Expected Value'], e['Actual Value'], e['disposition']) for e in dante.get_output_data('lad_chanvals.lad_chanvals').contains('Channel ID', 'NE-004')] == [
            ('1.234567', 1.234564, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is not equal to 1.234567 within 1e-6</p>'),
            ('1.234567', 1.234565, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is not equal to 1.234567 within 1e-6</p>'),
            ('1.234567', 1.234566, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is equal to 1.234567 within 1e-6</p>'),
            ('1.234567', 1.234567, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is equal to 1.234567 within 1e-6</p>'),
            ('1.234567', 1.234568, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is equal to 1.234567 within 1e-6</p>'),
            ('1.234567', 1.234569, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is not equal to 1.234567 within 1e-6</p>'),
            ('1.234567', 1.23457, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is not equal to 1.234567 within 1e-6</p>')
        ]

    def test_range_neither_inclusive(self, dante):
        assert [(e['Expected Value'], e['Actual Value'], e['disposition']) for e in dante.get_output_data('lad_chanvals.lad_chanvals').contains('Channel ID', 'RANGE-019')] == [
            ('(-1.234567,1.234567)', -1.234569, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between -1.234567 and 1.234567  within 1e-6 (non-inclusive)</p>'),
            ('(-1.234567,1.234567)', -1.234568, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between -1.234567 and 1.234567  within 1e-6 (non-inclusive)</p>'),
            ('(-1.234567,1.234567)', -1.234567, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between -1.234567 and 1.234567  within 1e-6 (non-inclusive)</p>'),
            ('(-1.234567,1.234567)', 0.0, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between -1.234567 and 1.234567  within 1e-6 (non-inclusive)</p>'),
            ('(-1.234567,1.234567)', 1.234567, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between -1.234567 and 1.234567  within 1e-6 (non-inclusive)</p>'),
            ('(-1.234567,1.234567)', 1.234568, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between -1.234567 and 1.234567  within 1e-6 (non-inclusive)</p>'),
            ('(-1.234567,1.234567)', 1.234569, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between -1.234567 and 1.234567  within 1e-6 (non-inclusive)</p>')
        ]

    def test_range_upper_only_exclusive(self, dante):
        assert [(e['Expected Value'], e['Actual Value'], e['disposition']) for e in dante.get_output_data('lad_chanvals.lad_chanvals').contains('Channel ID', 'RANGE-020')] == [
            ('(-1.234567,1.234567]', -1.234569, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between -1.234567 and 1.234567  within 1e-6 (upper-only inclusive)</p>'),
            ('(-1.234567,1.234567]', -1.234568, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between -1.234567 and 1.234567  within 1e-6 (upper-only inclusive)</p>'),
            ('(-1.234567,1.234567]', -1.234567, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between -1.234567 and 1.234567  within 1e-6 (upper-only inclusive)</p>'),
            ('(-1.234567,1.234567]', 0.0, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between -1.234567 and 1.234567  within 1e-6 (upper-only inclusive)</p>'),
            ('(-1.234567,1.234567]', 1.234567, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between -1.234567 and 1.234567  within 1e-6 (upper-only inclusive)</p>'),
            ('(-1.234567,1.234567]', 1.234568, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between -1.234567 and 1.234567  within 1e-6 (upper-only inclusive)</p>'),
            ('(-1.234567,1.234567]', 1.234569, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between -1.234567 and 1.234567  within 1e-6 (upper-only inclusive)</p>')
        ]

    def test_range_lower_only_exclusive(self, dante):
        assert [(e['Expected Value'], e['Actual Value'], e['disposition']) for e in dante.get_output_data('lad_chanvals.lad_chanvals').contains('Channel ID', 'RANGE-021')] == [
            ('[-1.234567,1.234567)', -1.234569, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between -1.234567 and 1.234567  within 1e-6 (lower-only inclusive)</p>'),
            ('[-1.234567,1.234567)', -1.234568, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between -1.234567 and 1.234567  within 1e-6 (lower-only inclusive)</p>'),
            ('[-1.234567,1.234567)', -1.234567, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between -1.234567 and 1.234567  within 1e-6 (lower-only inclusive)</p>'),
            ('[-1.234567,1.234567)', 0.0, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between -1.234567 and 1.234567  within 1e-6 (lower-only inclusive)</p>'),
            ('[-1.234567,1.234567)', 1.234567, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between -1.234567 and 1.234567  within 1e-6 (lower-only inclusive)</p>'),
            ('[-1.234567,1.234567)', 1.234568, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between -1.234567 and 1.234567  within 1e-6 (lower-only inclusive)</p>'),
            ('[-1.234567,1.234567)', 1.234569, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between -1.234567 and 1.234567  within 1e-6 (lower-only inclusive)</p>')
        ]

    def test_range_both_inclusive(self, dante):
        assert [(e['Expected Value'], e['Actual Value'], e['disposition']) for e in dante.get_output_data('lad_chanvals.lad_chanvals').contains('Channel ID', 'RANGE-022')] == [
            ('[-1.234567,1.234567]', -1.234569, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between -1.234567 and 1.234567  within 1e-6 (inclusive)</p>'),
            ('[-1.234567,1.234567]', -1.234568, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between -1.234567 and 1.234567  within 1e-6 (inclusive)</p>'),
            ('[-1.234567,1.234567]', -1.234567, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between -1.234567 and 1.234567  within 1e-6 (inclusive)</p>'),
            ('[-1.234567,1.234567]', 0.0, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between -1.234567 and 1.234567  within 1e-6 (inclusive)</p>'),
            ('[-1.234567,1.234567]', 1.234567, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between -1.234567 and 1.234567  within 1e-6 (inclusive)</p>'),
            ('[-1.234567,1.234567]', 1.234568, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between -1.234567 and 1.234567  within 1e-6 (inclusive)</p>'),
            ('[-1.234567,1.234567]', 1.234569, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between -1.234567 and 1.234567  within 1e-6 (inclusive)</p>')
        ]

    def test_range_same_value_inclusive(self, dante):
        assert [(e['Expected Value'], e['Actual Value'], e['disposition']) for e in dante.get_output_data('lad_chanvals.lad_chanvals').contains('Channel ID', 'RANGE-023')] == [
            ('[1.234567,1.234567]', 1.234563, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between 1.234567 and 1.234567  within 1e-6 (inclusve). Equivalent to eq 1.234567</p>'),
            ('[1.234567,1.234567]', 1.234564, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between 1.234567 and 1.234567  within 1e-6 (inclusve). Equivalent to eq 1.234567</p>'),
            ('[1.234567,1.234567]', 1.234565, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between 1.234567 and 1.234567  within 1e-6 (inclusve). Equivalent to eq 1.234567</p>'),
            ('[1.234567,1.234567]', 1.234566, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between 1.234567 and 1.234567  within 1e-6 (inclusve). Equivalent to eq 1.234567</p>'),
            ('[1.234567,1.234567]', 1.234567, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between 1.234567 and 1.234567  within 1e-6 (inclusve). Equivalent to eq 1.234567</p>'),
            ('[1.234567,1.234567]', 1.234568, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between 1.234567 and 1.234567  within 1e-6 (inclusve). Equivalent to eq 1.234567</p>'),
            ('[1.234567,1.234567]', 1.234569, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between 1.234567 and 1.234567  within 1e-6 (inclusve). Equivalent to eq 1.234567</p>')
        ]

    def test_range_same_non_value_inclusive(self, dante):
        assert [(e['Expected Value'], e['Actual Value'], e['disposition']) for e in dante.get_output_data('lad_chanvals.lad_chanvals').contains('Channel ID', 'RANGE-024')] == [
            ('[1.234567,1.234567]', 1.234563, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between 1.234567 and 1.234567  within 1e-6 (non-inclusve).</p>'),
            ('(1.234567,1.234567)', 1.234564, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between 1.234567 and 1.234567  within 1e-6 (non-inclusve).</p>'),
            ('(1.234567,1.234567)', 1.234565, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between 1.234567 and 1.234567  within 1e-6 (non-inclusve).</p>'),
            ('(1.234567,1.234567)', 1.234566, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between 1.234567 and 1.234567  within 1e-6 (non-inclusve).</p>'),
            ('(1.234567,1.234567)', 1.234567, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between 1.234567 and 1.234567  within 1e-6 (non-inclusve).</p>'),
            ('(1.234567,1.234567)', 1.234568, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between 1.234567 and 1.234567  within 1e-6 (non-inclusve).</p>'),
            ('(1.234567,1.234567)', 1.234569, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between 1.234567 and 1.234567  within 1e-6 (non-inclusve).</p>')
        ]