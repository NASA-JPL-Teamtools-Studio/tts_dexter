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
    eha_container = EhaContainer(csv_path = TEST_FILE_DIR.joinpath('dn_chanvals_with_tolerance.csv'),cast_fields=True)
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
        assert  [(e['Expected Value'], e['Actual Value'], e['disposition']) for e in dante.get_output_data('lad_chanvals.lad_chanvals').contains('Channel ID', 'GT-002')] == [
            ('-1', -1.01, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not greater than -1 within 1e-3</p>'),
            ('-1', -1.001, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not greater than -1 within 1e-3</p>'),
            ('-1', -1.0, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is greater than -1 within 1e-3</p>'),
            ('-1', -0.999, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is greater than -1 within 1e-3</p>'),
            ('-1', -0.99, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is greater than -1 within 1e-3</p>'),
            ]

    def test_lt(self, dante):
        assert [(e['Expected Value'], e['Actual Value'], e['disposition']) for e in dante.get_output_data('lad_chanvals.lad_chanvals').contains('Channel ID', 'LT-002')] == [
            ('1', 0.99, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is less than 1 within 1e-3</p>'),
            ('1', 0.999, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is less than 1 within 1e-3</p>'),
            ('1', 1.0, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is less than 1 within 1e-3</p>'),
            ('1', 1.001, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not less than 1 within 1e-3</p>'),
            ('1', 1.01, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not less than 1 within 1e-3</p>'),
            ]

    def test_gte(self, dante):
        assert [(e['Expected Value'], e['Actual Value'], e['disposition']) for e in dante.get_output_data('lad_chanvals.lad_chanvals').contains('Channel ID', 'GTE-002')] == [
            ('-1', -1.01, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not greater than or equal to -1 within 1e-3</p>'),
            ('-1', -1.001, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is greater than or equal to -1 within 1e-3</p>'),
            ('-1', -1.0, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is greater than or equal to -1 within 1e-3</p>'),
            ('-1', -0.999, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is greater than or equal to -1 within 1e-3</p>'),
            ('-1', -0.99, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is greater than or equal to -1 within 1e-3</p>'),
            ]

    def test_lte(self, dante):
        assert [(e['Expected Value'], e['Actual Value'], e['disposition']) for e in dante.get_output_data('lad_chanvals.lad_chanvals').contains('Channel ID', 'LTE-002')] == [
            ('1', 0.99, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is less than or equal to 1 within 1e-3</p>'),
            ('1', 0.999, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is less than or equal to 1 within 1e-3</p>'),
            ('1', 1.0, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is less than or equal to 1 within 1e-3</p>'),
            ('1', 1.001, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is less than or equal to 1 within 1e-3</p>'),
            ('1', 1.01, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not less than or equal to 1 within 1e-3</p>'),
            ]
    def test_eq(self, dante):
        assert [(e['Expected Value'], e['Actual Value'], e['disposition']) for e in dante.get_output_data('lad_chanvals.lad_chanvals').contains('Channel ID', 'EQ-002')] == [
            ('2', 1.998, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not equal to 1 within 1e-3</p>'),
            ('2', 1.999, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is equal to 1 within 1e-3</p>'),
            ('2', 2.0, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is equal to 1 within 1e-3</p>'),
            ('2', 2.001, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is equal to 1 within 1e-3</p>'),
            ('2', 2.002, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not equal to 1 within 1e-3</p>'),
        ]

    def test_ne(self, dante):
            assert [(e['Expected Value'], e['Actual Value'], e['disposition']) for e in dante.get_output_data('lad_chanvals.lad_chanvals').contains('Channel ID', 'NE-002')] == [
            ('2', 1.998, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is not equal to 1 within 1e-3</p>'),
            ('2', 1.999, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is equal to 1 within 1e-3</p>'),
            ('2', 2.0, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is equal to 1 within 1e-3</p>'),
            ('2', 2.001, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is equal to 1 within 1e-3</p>'),
            ('2', 2.002, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is not equal to 1 within 1e-3</p>'),
            ]

    def test_range_neither_none_clusive(self, dante):
        assert [(e['Expected Value'], e['Actual Value'], e['disposition']) for e in dante.get_output_data('lad_chanvals.lad_chanvals').contains('Channel ID', 'RANGE-007')] == [
            ('(-1,1)', -1.002, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between -1 and 1  within 1e-3 (non-inclusive)</p>'),
            ('(-1,1)', -1.001, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between -1 and 1  within 1e-3 (non-inclusive)</p>'),
            ('(-1,1)', -1.0, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between -1 and 1  within 1e-3 (non-inclusive)</p>'),
            ('(-1,1)', 0.0, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between -1 and 1  within 1e-3 (non-inclusive)</p>'),
            ('(-1,1)', 1.0, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between -1 and 1  within 1e-3 (non-inclusive)</p>'),
            ('(-1,1)', 1.001, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between -1 and 1  within 1e-3 (non-inclusive)</p>'),
            ('(-1,1)', 1.002, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between -1 and 1  within 1e-3 (non-inclusive)</p>')
        ]

    def test_range_upper_only_inclusive(self, dante):
        assert [(e['Expected Value'], e['Actual Value'], e['disposition']) for e in dante.get_output_data('lad_chanvals.lad_chanvals').contains('Channel ID', 'RANGE-008')] == [
            ('(-1,1]', -1.002, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between -1 and 1  within 1e-3 (upper-only inclusive)</p>'),
            ('(-1,1]', -1.001, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between -1 and 1  within 1e-3 (upper-only inclusive)</p>'),
            ('(-1,1]', -1.0, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between -1 and 1  within 1e-3 (upper-only inclusive)</p>'),
            ('(-1,1]', 0.0, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between -1 and 1  within 1e-3 (upper-only inclusive)</p>'),
            ('(-1,1]', 1.0, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between -1 and 1  within 1e-3 (upper-only inclusive)</p>'),
            ('(-1,1]', 1.001, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between -1 and 1  within 1e-3 (upper-only inclusive)</p>'),
            ('(-1,1]', 1.002, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between -1 and 1  within 1e-3 (upper-only inclusive)</p>')
        ]

    def test_range_lower_only_inclusive(self, dante):
        assert [(e['Expected Value'], e['Actual Value'], e['disposition']) for e in dante.get_output_data('lad_chanvals.lad_chanvals').contains('Channel ID', 'RANGE-009')] == [
            ('[-1,1)', -1.002, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between -1 and 1  within 1e-3 (lower-only inclusive)</p>'),
            ('[-1,1)', -1.001, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between -1 and 1  within 1e-3 (lower-only inclusive)</p>'),
            ('[-1,1)', -1.0, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between -1 and 1  within 1e-3 (lower-only inclusive)</p>'),
            ('[-1,1)', 0.0, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between -1 and 1  within 1e-3 (lower-only inclusive)</p>'),
            ('[-1,1)', 1.0, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between -1 and 1  within 1e-3 (lower-only inclusive)</p>'),
            ('[-1,1)', 1.001, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between -1 and 1  within 1e-3 (lower-only inclusive)</p>'),
            ('[-1,1)', 1.002, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between -1 and 1  within 1e-3 (lower-only inclusive)</p>')
        ]

    def test_range_both_inclusive(self, dante):
        assert [(e['Expected Value'], e['Actual Value'], e['disposition']) for e in dante.get_output_data('lad_chanvals.lad_chanvals').contains('Channel ID', 'RANGE-010')] == [
            ('[-1,1]', -1.002, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between -1 and 1  within 1e-3 (inclusive)</p>'),
            ('[-1,1]', -1.001, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between -1 and 1  within 1e-3 (inclusive)</p>'),
            ('[-1,1]', -1.0, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between -1 and 1  within 1e-3 (inclusive)</p>'),
            ('[-1,1]', 0.0, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between -1 and 1  within 1e-3 (inclusive)</p>'),
            ('[-1,1]', 1.0, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between -1 and 1  within 1e-3 (inclusive)</p>'),
            ('[-1,1]', 1.001, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between -1 and 1  within 1e-3 (inclusive)</p>'),
            ('[-1,1]', 1.002, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between -1 and 1  within 1e-3 (inclusive)</p>')
        ]

    def test_range_same_value_inclusive(self, dante):
        assert [(e['Expected Value'], e['Actual Value'], e['disposition']) for e in dante.get_output_data('lad_chanvals.lad_chanvals').contains('Channel ID', 'RANGE-011')] == [
            ('[1,1]', -1.002, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between 1 and 1  within 1e-3 (inclusve). Equivalent to eq 1</p>'),
            ('[1,1]', -1.001, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between 1 and 1  within 1e-3 (inclusve). Equivalent to eq 1</p>'),
            ('[1,1]', -1.0, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between 1 and 1  within 1e-3 (inclusve). Equivalent to eq 1</p>'),
            ('[1,1]', 0.0, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between 1 and 1  within 1e-3 (inclusve). Equivalent to eq 1</p>'),
            ('[1,1]', 1.0, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between 11 and 1  within 1e-3 (inclusve). Equivalent to eq 1</p>'),
            ('[1,1]', 1.001, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between 11 and 1  within 1e-3 (inclusve). Equivalent to eq 1</p>'),
            ('[1,1]', 1.002, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between 1 and 1  within 1e-3 (inclusve). Equivalent to eq 1</p>')
        ]

    def test_range_same_value_non_inclusive(self, dante):
        assert [(e['Expected Value'], e['Actual Value'], e['disposition']) for e in dante.get_output_data('lad_chanvals.lad_chanvals').contains('Channel ID', 'RANGE-012')] == [
            ('(1,1)', -1.002, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between 1 and 1  within 1e-3 (non-inclusve).</p>'),
            ('(1,1)', -1.001, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between 1 and 1  within 1e-3 (non-inclusve).</p>'),
            ('(1,1)', -1.0, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between 1 and 1  within 1e-3 (non-inclusve).</p>'),
            ('(1,1)', 0.0, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between 1 and 1  within 1e-3 (non-inclusve).</p>'),
            ('(1,1)', 1.0, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between 1 and 1  within 1e-3 (non-inclusve).</p>'),
            ('(1,1)', 1.001, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between 1 and 1  within 1e-3 (non-inclusve).</p>'),
            ('(1,1)', 1.002, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between 1 and 1  within 1e-3 (non-inclusve).</p>'),
        ]

