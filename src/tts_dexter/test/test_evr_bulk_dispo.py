import hashlib
import json
import pytest
from pathlib import Path
import pandas as pd
import pdb


from tts_utilities.logger import create_logger
from tts_data_utils.multimission.evr import EvrContainer
from tts_dexter.core.dexter import Dexter
from tts_dexter.dispositioners.evrs import BulkEvrDispositioner

logger = create_logger(f'dexter.evr_bulk_dispo')
TEST_FILE_DIR = Path(__file__).parent.joinpath('test_files/evr_bulk_dispo')

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
    dex.disposition_all()
    dex.stamp_all()
    return dex

class TestBulkEvrDispo:
    def test_evr_exact_name_match(self, dex, evr_container):
        assert [(e['name'], e['message'], e['disposition']) for e in evr_container.isin('name', ['MATCH_BY_EXACT_EVR_NAME', 'DONT_MATCH_BY_EXACT_EVR_NAME'])] == [
            ('MATCH_BY_EXACT_EVR_NAME', "It doesn't matter what this message is", '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - This EVR\'s name has the exact name MATCH_BY_EXACT_EVR_NAME</p>'),
            ('DONT_MATCH_BY_EXACT_EVR_NAME', "It doesn't matter what this message is", '<p><strong><span style="color:#AD44AD">No Autodisposition</span></strong> - Manual Disposition Needed</p>')
            ]

    def test_evr_regex_name_match(self, dex, evr_container):
        assert [(e['name'], e['message'], e['disposition']) for e in evr_container.isin('name', ['MATCH_BY_EVR_NAME_REGEX_A', 'MATCH_BY_EVR_NAME_REGEX_B', 'MATCH_BY_EVR_NAME_REGEX_C', 'DONT_MATCH_BY_EVR_NAME_REGEX'])] == [
            ('MATCH_BY_EVR_NAME_REGEX_A', "It doesn't matter what this message is", '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - This EVR\'s name matches the regex MATCH_BY_EVR_NAME_REGEX_[A|B]</p>'),
            ('MATCH_BY_EVR_NAME_REGEX_B', "It doesn't matter what this message is", '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - This EVR\'s name matches the regex MATCH_BY_EVR_NAME_REGEX_[A|B]</p>'),
            ('MATCH_BY_EVR_NAME_REGEX_C', "It doesn't matter what this message is", '<p><strong><span style="color:#AD44AD">No Autodisposition</span></strong> - Manual Disposition Needed</p>'),
            ('DONT_MATCH_BY_EVR_NAME_REGEX', "It doesn't matter what this message is", '<p><strong><span style="color:#AD44AD">No Autodisposition</span></strong> - Manual Disposition Needed</p>')
            ]

    def test_evr_regex_message_match(self, dex, evr_container):
        assert [(e['name'], e['message'], e['disposition']) for e in evr_container.isin('name', ['MATCH_BY_EVR_NAME_WITH_MESSAGE_REGEX'])] == [
            ('MATCH_BY_EVR_NAME_WITH_MESSAGE_REGEX', 'Please _-_-_-_ match 0909090 this qwqwqwq message.', '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - This EVR\'s message matches the regex Please.*match.*this.*message\\.</p>'),
            ('MATCH_BY_EVR_NAME_WITH_MESSAGE_REGEX', "But don't match this one.", '<p><strong><span style="color:#AD44AD">No Autodisposition</span></strong> - Manual Disposition Needed</p>')            
            ]

    def test_evr_regex_message_and_regex_name_match(self, dex, evr_container):
        #The messages in this test get a little confusing. Note that we only expect the names ending in A and B to match
        #and only the messages with "Please match this message." baked into them
        #SO  here, we expect the first two to trigger the disposition and all the rest to fail.
        assert [(e['name'], e['message'], e['disposition']) for e in evr_container.isin('name', ['NAME_AND_REGEX_MATCH_A', 'NAME_AND_REGEX_MATCH_B', 'NAME_AND_REGEX_MATCH_C'])] == [
            ('NAME_AND_REGEX_MATCH_A', 'Please _-_-_-_ match 0909090 this qwqwqwq message.', '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - This EVR\'s name matches NAME_AND_REGEX_MATCH_[A|B] and its message matches the regex Please.*match.*this.*message\\.</p>'),
            ('NAME_AND_REGEX_MATCH_B', 'Please _-_-_-_ match 0909090 this qwqwqwq message.', '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - This EVR\'s name matches NAME_AND_REGEX_MATCH_[A|B] and its message matches the regex Please.*match.*this.*message\\.</p>'),
            ('NAME_AND_REGEX_MATCH_C', 'Please _-_-_-_ match 0909090 this qwqwqwq message.', '<p><strong><span style="color:#AD44AD">No Autodisposition</span></strong> - Manual Disposition Needed</p>'),
            ('NAME_AND_REGEX_MATCH_A', "But don't match this one.", '<p><strong><span style="color:#AD44AD">No Autodisposition</span></strong> - Manual Disposition Needed</p>'),
            ('NAME_AND_REGEX_MATCH_B', "But don't match this one.", '<p><strong><span style="color:#AD44AD">No Autodisposition</span></strong> - Manual Disposition Needed</p>'),
            ('NAME_AND_REGEX_MATCH_C', "But don't match this one.", '<p><strong><span style="color:#AD44AD">No Autodisposition</span></strong> - Manual Disposition Needed</p>'),
            ]





