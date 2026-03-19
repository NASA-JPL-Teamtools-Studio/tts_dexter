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


class LadBulkEhaDispositionerStatusDnStr(LadEhaDispositioner):
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
        self.init_dispositioner(LadBulkEhaDispositionerStatusDnStr)

@pytest.fixture(scope="module")
def eha_container():
    eha_container = EhaContainer(csv_path = TEST_FILE_DIR.joinpath('status_and_dnString_chanvals.csv'),cast_fields=True)
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

class TestBulkEhaDispoStatus:
    def test_eq(self, dante):
        assert [(e['Expected Value'], e['Actual Value'], e['disposition']) for e in dante.get_output_data('lad_chanvals.lad_chanvals').contains('Channel ID', 'STATUS-001')] == [
            ('OPTION_1', 'OPTION_1', '<p><strong><span style="color:#68BC00">Expected</span></strong> - Status chanval is equal to OPTION_1</p>'),
            ('OPTION_1', 'OPTION_2', '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - Status chanval is not equal to OPTION_1</p>')
        ]

    def test_ne(self, dante):
        assert [(e['Expected Value'], e['Actual Value'], e['disposition']) for e in dante.get_output_data('lad_chanvals.lad_chanvals').contains('Channel ID', 'STATUS-002')] == [
            ('OPTION_1', 'OPTION_1', '<p><strong><span style="color:#68BC00">Expected</span></strong> - Status chanval is not equal to OPTION_2</p>'),
            ('OPTION_1', 'OPTION_2', '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - Status chanval is equal to OPTION_2</p>')
        ]

    def test_isin(self, dante):
        assert [(e['Expected Value'], e['Actual Value'], e['disposition']) for e in dante.get_output_data('lad_chanvals.lad_chanvals').contains('Channel ID', 'STATUS-003')] == [
            ('OPTION_1, OPTION_2', 'OPTION_1', '<p><strong><span style="color:#68BC00">Expected</span></strong> - Status chanval is either OPTION_1 or OPTION_2</p>'),
            ('OPTION_1, OPTION_2', 'OPTION_2', '<p><strong><span style="color:#68BC00">Expected</span></strong> - Status chanval is either OPTION_1 or OPTION_2</p>')
        ]

    def test_notin(self, dante):
        assert [(e['Expected Value'], e['Actual Value'], e['disposition']) for e in dante.get_output_data('lad_chanvals.lad_chanvals').contains('Channel ID', 'STATUS-004')] == [
            ('OPTION_1, OPTION_2', 'OPTION_1', '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - Status chanval is not neither OPTION_1 nor OPTION_2</p>'),
            ('OPTION_1, OPTION_2', 'OPTION_2', '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - Status chanval is not neither OPTION_1 nor OPTION_2</p>')
        ]

class TestBulkEhaDispoDnString:
    def test_eq(self, dante):
        assert [(e['Expected Value'], e['Actual Value'], e['disposition']) for e in dante.get_output_data('lad_chanvals.lad_chanvals').contains('Channel ID', 'DNSTR-001')] == [
            ('StringValue1', 'StringValue1', '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN String chanval is equal to StringValue1</p>'),
            ('StringValue1', 'StringValue2', '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN String chanval is not equal to StringValue1</p>')
        ]

    def test_ne(self, dante):
        assert [(e['Expected Value'], e['Actual Value'], e['disposition']) for e in dante.get_output_data('lad_chanvals.lad_chanvals').contains('Channel ID', 'DNSTR-002')] == [
            ('StringValue1', 'StringValue1', '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN String chanval is not equal to StringValue1</p>'),
            ('StringValue1', 'StringValue2', '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN String chanval is equal to StringValue1</p>')
        ]

    def test_isin(self, dante):
        assert [(e['Expected Value'], e['Actual Value'], e['disposition']) for e in dante.get_output_data('lad_chanvals.lad_chanvals').contains('Channel ID', 'DNSTR-003')] == [
            ('StringValue1,StringValue2', 'StringValue1', '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN String chanval is equal to StringValue1</p>'), 
            ('StringValue1,StringValue2', 'StringValue2', '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN String chanval is equal to StringValue1</p>')
            ]

    def test_notin(self, dante):
        assert [(e['Expected Value'], e['Actual Value'], e['disposition']) for e in dante.get_output_data('lad_chanvals.lad_chanvals').contains('Channel ID', 'DNSTR-004')] == [
            ('StringValue1,StringValue2', 'StringValue1', '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN String chanval is equal to StringValue1</p>'), 
            ('StringValue1,StringValue2', 'StringValue2', '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN String chanval is equal to StringValue1</p>')
            ]




