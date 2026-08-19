import pytest
from pathlib import Path

from tts_data_utils.core.data_frame import TtsDataFrame
from tts_dexter.core.dexter import Dexter
from tts_dexter.dispositioners.evrs import DfBulkEvrDispositioner
from tts_dexter.test.df_test_helpers import TEST_FILE_DIR, make_evr_frame, evr_rows_for

EVR_DIR = TEST_FILE_DIR / 'evr_bulk_dispo'
RULES_CSV = EVR_DIR / 'evr_autodispositions.csv'
EVRS_CSV = EVR_DIR / 'evrs.csv'


class _TestBulkEvrDispositioner(DfBulkEvrDispositioner):
    CSV_FILEPATH = RULES_CSV


class _EvrBulkDispoDexter(Dexter):
    def __init__(self, frame):
        super().__init__()
        self.all_input_data.set_data_one('evr_frame', frame)
        self.init_dispositioner(_TestBulkEvrDispositioner)


@pytest.fixture(scope='module')
def dex_output():
    frame = make_evr_frame(EVRS_CSV)
    dex = _EvrBulkDispoDexter(frame)
    dex.disposition_all()
    return dex.stamp_all_to_outputs()['evr_frame']


@pytest.mark.unreviewed_ai_generated_test
class TestBulkEvrDispo:

    def test_evr_exact_name_match(self, dex_output):
        assert evr_rows_for(dex_output, ['MATCH_BY_EXACT_EVR_NAME', 'DONT_MATCH_BY_EXACT_EVR_NAME']) == [
            ('MATCH_BY_EXACT_EVR_NAME',      "It doesn't matter what this message is", '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - This EVR\'s name has the exact name MATCH_BY_EXACT_EVR_NAME</p>'),
            ('DONT_MATCH_BY_EXACT_EVR_NAME', "It doesn't matter what this message is", '<p><strong><span style="color:#AD44AD">No Autodisposition</span></strong> - Manual Disposition Needed</p>'),
        ]

    def test_evr_regex_name_match(self, dex_output):
        assert evr_rows_for(dex_output, ['MATCH_BY_EVR_NAME_REGEX_A', 'MATCH_BY_EVR_NAME_REGEX_B', 'MATCH_BY_EVR_NAME_REGEX_C', 'DONT_MATCH_BY_EVR_NAME_REGEX']) == [
            ('MATCH_BY_EVR_NAME_REGEX_A',   "It doesn't matter what this message is", '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - This EVR\'s name matches the regex MATCH_BY_EVR_NAME_REGEX_[A|B]</p>'),
            ('MATCH_BY_EVR_NAME_REGEX_B',   "It doesn't matter what this message is", '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - This EVR\'s name matches the regex MATCH_BY_EVR_NAME_REGEX_[A|B]</p>'),
            ('MATCH_BY_EVR_NAME_REGEX_C',   "It doesn't matter what this message is", '<p><strong><span style="color:#AD44AD">No Autodisposition</span></strong> - Manual Disposition Needed</p>'),
            ('DONT_MATCH_BY_EVR_NAME_REGEX', "It doesn't matter what this message is", '<p><strong><span style="color:#AD44AD">No Autodisposition</span></strong> - Manual Disposition Needed</p>'),
        ]

    def test_evr_regex_message_match(self, dex_output):
        assert evr_rows_for(dex_output, ['MATCH_BY_EVR_NAME_WITH_MESSAGE_REGEX']) == [
            ('MATCH_BY_EVR_NAME_WITH_MESSAGE_REGEX', 'Please _-_-_-_ match 0909090 this qwqwqwq message.', '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - This EVR\'s message matches the regex Please.*match.*this.*message\\.</p>'),
            ('MATCH_BY_EVR_NAME_WITH_MESSAGE_REGEX', "But don't match this one.",                         '<p><strong><span style="color:#AD44AD">No Autodisposition</span></strong> - Manual Disposition Needed</p>'),
        ]

    def test_evr_regex_message_and_regex_name_match(self, dex_output):
        assert evr_rows_for(dex_output, ['NAME_AND_REGEX_MATCH_A', 'NAME_AND_REGEX_MATCH_B', 'NAME_AND_REGEX_MATCH_C']) == [
            ('NAME_AND_REGEX_MATCH_A', 'Please _-_-_-_ match 0909090 this qwqwqwq message.', '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - This EVR\'s name matches NAME_AND_REGEX_MATCH_[A|B] and its message matches the regex Please.*match.*this.*message\\.</p>'),
            ('NAME_AND_REGEX_MATCH_B', 'Please _-_-_-_ match 0909090 this qwqwqwq message.', '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - This EVR\'s name matches NAME_AND_REGEX_MATCH_[A|B] and its message matches the regex Please.*match.*this.*message\\.</p>'),
            ('NAME_AND_REGEX_MATCH_C', 'Please _-_-_-_ match 0909090 this qwqwqwq message.', '<p><strong><span style="color:#AD44AD">No Autodisposition</span></strong> - Manual Disposition Needed</p>'),
            ('NAME_AND_REGEX_MATCH_A', "But don't match this one.",                          '<p><strong><span style="color:#AD44AD">No Autodisposition</span></strong> - Manual Disposition Needed</p>'),
            ('NAME_AND_REGEX_MATCH_B', "But don't match this one.",                          '<p><strong><span style="color:#AD44AD">No Autodisposition</span></strong> - Manual Disposition Needed</p>'),
            ('NAME_AND_REGEX_MATCH_C', "But don't match this one.",                          '<p><strong><span style="color:#AD44AD">No Autodisposition</span></strong> - Manual Disposition Needed</p>'),
        ]
