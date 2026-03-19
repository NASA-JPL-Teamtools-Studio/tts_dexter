import hashlib
import json
import pytest
from pathlib import Path
import pdb

from tts_utilities.logger import create_logger
from tts_data_utils.multimission.evr import EvrContainer
from tts_dexter.core.dexter import Dexter
from tts_dexter.dispositioners.evrs import BulkEvrDispositioner
from tts_dexter.core.dispo import DISPO_FORMAT #TO DO: Clean this up... this is vestigal because it became data_utils

logger = create_logger(f'dexter.stamp_and_format')
TEST_FILE_DIR = Path(__file__).parent.joinpath('test_files/stamp_and_format')

class TestBulkEvrDispositioner(BulkEvrDispositioner):
    CSV_FILEPATH = TEST_FILE_DIR.joinpath('evr_autodispositions.csv')

class EvrBulkDispoTestDexter(Dexter):
    def __init__(self, evrs=None):
        super().__init__()        
        self.init_data(EvrContainer, evrs)
        self.init_dispositioner(TestBulkEvrDispositioner)

@pytest.fixture(scope="module")
def evr_container():
    return EvrContainer(
        csv_path=TEST_FILE_DIR.joinpath('evrs.csv'), 
        cast_fields=True
        )    

@pytest.fixture(scope="module")
def dex(evr_container):
    dex = EvrBulkDispoTestDexter(evr_container)
    return dex

class TestDispoFormatting:
    @pytest.mark.xfail #TO DO: Refactor this test with the new way we're handling papertrail
    def test_format_excel(self, dex, evr_container):
        dex.dispo_format = DISPO_FORMAT.EXCEL
        dex.disposition_all()
        dex.stamp_all()
        assert [e['disposition'][0].parts for e in evr_container] == [
            [{'bold': True, 'font_color': '#FF6347'}, 'Unexpected', ' - ', "This EVR's name has the exact name MATCH_BY_EXACT_EVR_NAME"],
            [{'bold': True, 'font_color': '#AD44AD'}, 'No Autodisposition', ' - ', 'Manual Disposition Needed'],
            [{'bold': True, 'font_color': '#FF6347'}, 'Unexpected', ' - ', "This EVR's name matches the regex MATCH_BY_EVR_NAME_REGEX_[A|B]"],
            [{'bold': True, 'font_color': '#FF6347'}, 'Unexpected', ' - ', "This EVR's name matches the regex MATCH_BY_EVR_NAME_REGEX_[A|B]"],
            [{'bold': True, 'font_color': '#AD44AD'}, 'No Autodisposition', ' - ', 'Manual Disposition Needed'],
            [{'bold': True, 'font_color': '#AD44AD'}, 'No Autodisposition', ' - ', 'Manual Disposition Needed'],
            [{'bold': True, 'font_color': '#FF6347'}, r'Unexpected', ' - ', "This EVR's message matches the regex Please.*match.*this.*message\\."],
            [{'bold': True, 'font_color': '#AD44AD'}, 'No Autodisposition', ' - ', 'Manual Disposition Needed'],
            [{'bold': True, 'font_color': '#FF6347'}, 'Unexpected', ' - ', "This EVR's name matches NAME_AND_REGEX_MATCH_[A|B] and its message matches the regex Please.*match.*this.*message\\."],
            [{'bold': True, 'font_color': '#FF6347'}, 'Unexpected', ' - ', "This EVR's name matches NAME_AND_REGEX_MATCH_[A|B] and its message matches the regex Please.*match.*this.*message\\."],
            [{'bold': True, 'font_color': '#AD44AD'}, 'No Autodisposition', ' - ', 'Manual Disposition Needed'],
            [{'bold': True, 'font_color': '#AD44AD'}, 'No Autodisposition', ' - ', 'Manual Disposition Needed'],
            [{'bold': True, 'font_color': '#AD44AD'}, 'No Autodisposition', ' - ', 'Manual Disposition Needed'],
            [{'bold': True, 'font_color': '#AD44AD'}, 'No Autodisposition', ' - ', 'Manual Disposition Needed'],
            ]

    def test_format_html(self, dex, evr_container):
        dex.dispo_format = DISPO_FORMAT.HTML
        dex.disposition_all()
        dex.stamp_all()
        assert [e['disposition'] for e in evr_container] == [
            '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - This EVR\'s name has the exact name MATCH_BY_EXACT_EVR_NAME</p><br><p><strong><span style="color:#FF6347">Unexpected</span></strong> - This EVR\'s name has the exact name MATCH_BY_EXACT_EVR_NAME</p>',
            '<p><strong><span style="color:#AD44AD">No Autodisposition</span></strong> - Manual Disposition Needed</p>',
            '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - This EVR\'s name matches the regex MATCH_BY_EVR_NAME_REGEX_[A|B]</p><br><p><strong><span style="color:#FF6347">Unexpected</span></strong> - This EVR\'s name matches the regex MATCH_BY_EVR_NAME_REGEX_[A|B]</p>',
            '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - This EVR\'s name matches the regex MATCH_BY_EVR_NAME_REGEX_[A|B]</p><br><p><strong><span style="color:#FF6347">Unexpected</span></strong> - This EVR\'s name matches the regex MATCH_BY_EVR_NAME_REGEX_[A|B]</p>',
            '<p><strong><span style="color:#AD44AD">No Autodisposition</span></strong> - Manual Disposition Needed</p>',
            '<p><strong><span style="color:#AD44AD">No Autodisposition</span></strong> - Manual Disposition Needed</p>',
            '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - This EVR\'s message matches the regex Please.*match.*this.*message\\.</p><br><p><strong><span style="color:#FF6347">Unexpected</span></strong> - This EVR\'s message matches the regex Please.*match.*this.*message\\.</p>',
            '<p><strong><span style="color:#AD44AD">No Autodisposition</span></strong> - Manual Disposition Needed</p>',
            '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - This EVR\'s name matches NAME_AND_REGEX_MATCH_[A|B] and its message matches the regex Please.*match.*this.*message\\.</p><br><p><strong><span style="color:#FF6347">Unexpected</span></strong> - This EVR\'s name matches NAME_AND_REGEX_MATCH_[A|B] and its message matches the regex Please.*match.*this.*message\\.</p>',
            '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - This EVR\'s name matches NAME_AND_REGEX_MATCH_[A|B] and its message matches the regex Please.*match.*this.*message\\.</p><br><p><strong><span style="color:#FF6347">Unexpected</span></strong> - This EVR\'s name matches NAME_AND_REGEX_MATCH_[A|B] and its message matches the regex Please.*match.*this.*message\\.</p>',
            '<p><strong><span style="color:#AD44AD">No Autodisposition</span></strong> - Manual Disposition Needed</p>',
            '<p><strong><span style="color:#AD44AD">No Autodisposition</span></strong> - Manual Disposition Needed</p>',
            '<p><strong><span style="color:#AD44AD">No Autodisposition</span></strong> - Manual Disposition Needed</p>',
            '<p><strong><span style="color:#AD44AD">No Autodisposition</span></strong> - Manual Disposition Needed</p>',
            ]

    def test_format_text(self, dex, evr_container):
        dex.dispo_format = DISPO_FORMAT.TEXT
        dex.disposition_all()
        dex.stamp_all()
        assert [e['disposition'] for e in evr_container] == [
            "Unexpected - This EVR's name has the exact name MATCH_BY_EXACT_EVR_NAME\nUnexpected - This EVR's name has the exact name MATCH_BY_EXACT_EVR_NAME\nUnexpected - This EVR's name has the exact name MATCH_BY_EXACT_EVR_NAME",
            'No Autodisposition - Manual Disposition Needed',
            "Unexpected - This EVR's name matches the regex MATCH_BY_EVR_NAME_REGEX_[A|B]\nUnexpected - This EVR's name matches the regex MATCH_BY_EVR_NAME_REGEX_[A|B]\nUnexpected - This EVR's name matches the regex MATCH_BY_EVR_NAME_REGEX_[A|B]",
            "Unexpected - This EVR's name matches the regex MATCH_BY_EVR_NAME_REGEX_[A|B]\nUnexpected - This EVR's name matches the regex MATCH_BY_EVR_NAME_REGEX_[A|B]\nUnexpected - This EVR's name matches the regex MATCH_BY_EVR_NAME_REGEX_[A|B]",
            'No Autodisposition - Manual Disposition Needed',
            'No Autodisposition - Manual Disposition Needed',
            "Unexpected - This EVR's message matches the regex Please.*match.*this.*message\\.\nUnexpected - This EVR's message matches the regex Please.*match.*this.*message\\.\nUnexpected - This EVR's message matches the regex Please.*match.*this.*message\\.",
            'No Autodisposition - Manual Disposition Needed',
            "Unexpected - This EVR's name matches NAME_AND_REGEX_MATCH_[A|B] and its message matches the regex Please.*match.*this.*message\\.\nUnexpected - This EVR's name matches NAME_AND_REGEX_MATCH_[A|B] and its message matches the regex Please.*match.*this.*message\\.\nUnexpected - This EVR's name matches NAME_AND_REGEX_MATCH_[A|B] and its message matches the regex Please.*match.*this.*message\\.",
            "Unexpected - This EVR's name matches NAME_AND_REGEX_MATCH_[A|B] and its message matches the regex Please.*match.*this.*message\\.\nUnexpected - This EVR's name matches NAME_AND_REGEX_MATCH_[A|B] and its message matches the regex Please.*match.*this.*message\\.\nUnexpected - This EVR's name matches NAME_AND_REGEX_MATCH_[A|B] and its message matches the regex Please.*match.*this.*message\\.",
            'No Autodisposition - Manual Disposition Needed',
            'No Autodisposition - Manual Disposition Needed',
            'No Autodisposition - Manual Disposition Needed',
            'No Autodisposition - Manual Disposition Needed',
            ]



