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
    eha_container = EhaContainer(csv_path = TEST_FILE_DIR.joinpath('dn_chanvals_no_tolerance.csv'),cast_fields=True)
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

class TestBulkEhaDispoDnNoTolerance:
    def test_gt(self, dante):
        # eha_container.eq('channelId', 'GT-002').table(['channelId', 'dn', 'dnString', 'eu', 'status', 'disposition'])
        
        assert  [(e['Expected Value'], e['Actual Value'], e['disposition']) for e in dante.get_output_data('lad_chanvals.lad_chanvals').contains('Channel ID', 'GT-001')] == [
            ('-1', -2, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not greater than -1</p>'),
            ('-1', -1, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not greater than -1</p>'),
            ('-1', 1, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is greater than -1</p>')
            ]

    def test_lt(self, dante):

        assert [(e['Expected Value'], e['Actual Value'], e['disposition']) for e in dante.get_output_data('lad_chanvals.lad_chanvals').contains('Channel ID', 'LT-001')] == [
            ('1', 0, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is less than 1</p>'), 
            ('1', 1, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not less than 1</p>'), 
            ('1', 2, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not less than 1</p>')
            ]

    def test_gte(self, dante):

        assert [(e['Expected Value'], e['Actual Value'], e['disposition']) for e in dante.get_output_data('lad_chanvals.lad_chanvals').contains('Channel ID', 'GTE-001')] == [
            ('-1', -2, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not greater than or equal to -1</p>'), 
            ('-1', -1, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is greater than or equal to -1</p>'), 
            ('-1', 1, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is greater than or equal to -1</p>')
            ]

    def test_lte(self, dante):
        assert [(e['Expected Value'], e['Actual Value'], e['disposition']) for e in dante.get_output_data('lad_chanvals.lad_chanvals').contains('Channel ID', 'LTE-001')] == [
            ('1', 0, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is less than or equal to 1</p>'), 
            ('1', 1, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is less than or equal to 1</p>'), 
            ('1', 2, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not less than or equal to 1</p>')
            ]

    def test_eq(self, dante):
        assert [(e['Expected Value'], e['Actual Value'], e['disposition']) for e in dante.get_output_data('lad_chanvals.lad_chanvals').contains('Channel ID', 'EQ-001')] == [
            ('1', 1, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is equal to 1</p>'), 
            ('1', 2, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not equal to 1</p>')
            ]

    def test_ne(self, dante):
        assert [(e['Expected Value'], e['Actual Value'], e['disposition']) for e in dante.get_output_data('lad_chanvals.lad_chanvals').contains('Channel ID', 'NE-001')] == [
            ('1', 1, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is equal to 1</p>'), 
            ('1', 2, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is not equal to 1</p>')
            ]

    def test_range_neither_inclusive(self, dante):
        assert [(e['Expected Value'], e['Actual Value'], e['disposition']) for e in dante.get_output_data('lad_chanvals.lad_chanvals').contains('Channel ID', 'RANGE-001')] == [
            ('(-1,1)', -2, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between -1 and 1 (non-inclusive)</p>'),
            ('(-1,1)', -1, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between -1 and 1 (non-inclusive)</p>'),
            ('(-1,1)', 0, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between -1 and 1 (non-inclusive)</p>'),
            ('(-1,1)', 1, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between -1 and 1 (non-inclusive)</p>'),
            ('(-1,1)', 2, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between -1 and 1 (non-inclusive)</p>')
        ]

    def test_range_upper_only_exclusive(self, dante):
        assert [(e['Expected Value'], e['Actual Value'], e['disposition']) for e in dante.get_output_data('lad_chanvals.lad_chanvals').contains('Channel ID', 'RANGE-002')] == [
            ('(-1,1]', -2, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between 1 and 1 (upper-only inclusive)</p>'),
            ('(-1,1]', -1, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between 1 and 1 (upper-only inclusive)</p>'),
            ('(-1,1]', 0, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between 1 and 1 (upper-only inclusive)</p>'),
            ('(-1,1]', 1, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between 1 and 1 (upper-only inclusive)</p>'),
            ('(-1,1]', 2, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between 1 and 1 (upper-only inclusive)</p>')
        ]

    def test_range_lower_only_exclusive(self, dante):
        assert [(e['Expected Value'], e['Actual Value'], e['disposition']) for e in dante.get_output_data('lad_chanvals.lad_chanvals').contains('Channel ID', 'RANGE-003')] == [
            ('[-1,1)', -2, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between -1 and 1 (lower-only inclusive)</p>'),
            ('[-1,1)', -1, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between -1 and 1 (lower-only inclusive)</p>'),
            ('[-1,1)', 0, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between -1 and 1 (lower-only inclusive)</p>'),
            ('[-1,1)', 1, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between -1 and 1 (lower-only inclusive)</p>'),
            ('[-1,1)', 2, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between -1 and 1 (lower-only inclusive)</p>')
        ]

    def test_range_both_inclusive(self, dante):
        assert [(e['Expected Value'], e['Actual Value'], e['disposition']) for e in dante.get_output_data('lad_chanvals.lad_chanvals').contains('Channel ID', 'RANGE-004')] == [
            ('[-10,10]', -11, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between -10 and 10 (inclusive)</p>'),
            ('[-10,10]', -10, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between -10 and 10 (inclusive)</p>'),
            ('[-10,10]', 0, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between -10 and 10 (inclusive)</p>'),
            ('[-10,10]', 10, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between -10 and 10 (inclusive)</p>'),
            ('[-10,10]', 11, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between -10 and 10 (inclusive)</p>')
        ]

    def test_range_same_value_inclusive(self, dante):
        assert [(e['Expected Value'], e['Actual Value'], e['disposition']) for e in dante.get_output_data('lad_chanvals.lad_chanvals').contains('Channel ID', 'RANGE-005')] == [
            ('[5,5]', 4, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between 5 and 5 (inclusve). Equivalent to eq 5</p>'),
            ('[5,5]', 5, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between 5 and 5 (inclusve). Equivalent to eq 5</p>'),
            ('[5,5]', 6, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between 5 and 5 (inclusve). Equivalent to eq 5</p>')
        ]

    def test_range_same_non_value_inclusive(self, dante):
        assert [(e['Expected Value'], e['Actual Value'], e['disposition']) for e in dante.get_output_data('lad_chanvals.lad_chanvals').contains('Channel ID', 'RANGE-006')] == [
            ('(5,5)', 4, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between 5 and 5 (non-inclusve). Should never be true</p>'),
            ('(5,5)', 5, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between 5 and 5 (non-inclusve). Should never be true</p>'),
            ('(5,5)', 6, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between 5 and 5 (non-inclusve). Should never be true</p>')
        ]

