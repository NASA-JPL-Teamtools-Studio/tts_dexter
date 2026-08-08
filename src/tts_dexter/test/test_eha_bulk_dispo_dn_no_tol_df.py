import pytest
from pathlib import Path

from tts_data_utils.core.data_frame import TtsDataFrame
from tts_dexter.core.dexter import Dexter
from tts_dexter.dispositioners.eha import DfLadEhaDispositioner
from tts_dexter.test.df_test_helpers import TEST_FILE_DIR, make_lad_frame, rows_for

EHA_DIR = TEST_FILE_DIR / 'eha_bulk_dispo'
RULES_CSV = EHA_DIR / 'eha_autodispositions.csv'
CHANVALS_CSV = EHA_DIR / 'dn_chanvals_no_tolerance.csv'


class _DnNoTolDispositioner(DfLadEhaDispositioner):
    pass


class _DnNoTolDexter(Dexter):
    def __init__(self, frame):
        super().__init__()
        self.all_input_data.set_data_one('lad_frame', frame)
        self.init_dispositioner(_DnNoTolDispositioner)


@pytest.fixture(scope='module')
def dex_output():
    frame = make_lad_frame(RULES_CSV, CHANVALS_CSV, group_filter='DN No Tolerance')
    dex = _DnNoTolDexter(frame)
    dex.disposition_all()
    return dex.stamp_all_to_outputs()['lad_frame']


@pytest.mark.unreviewed_ai_generated_test
class TestBulkEhaDispoDnNoToleranceDf:

    def test_gt(self, dex_output):
        assert rows_for(dex_output, 'GT-001') == [
            ('-1', -2, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not greater than -1</p>'),
            ('-1', -1, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not greater than -1</p>'),
            ('-1',  1, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is greater than -1</p>'),
        ]

    def test_lt(self, dex_output):
        assert rows_for(dex_output, 'LT-001') == [
            ('1', 0, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is less than 1</p>'),
            ('1', 1, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not less than 1</p>'),
            ('1', 2, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not less than 1</p>'),
        ]

    def test_gte(self, dex_output):
        assert rows_for(dex_output, 'GTE-001') == [
            ('-1', -2, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not greater than or equal to -1</p>'),
            ('-1', -1, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is greater than or equal to -1</p>'),
            ('-1',  1, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is greater than or equal to -1</p>'),
        ]

    def test_lte(self, dex_output):
        assert rows_for(dex_output, 'LTE-001') == [
            ('1', 0, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is less than or equal to 1</p>'),
            ('1', 1, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is less than or equal to 1</p>'),
            ('1', 2, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not less than or equal to 1</p>'),
        ]

    def test_eq(self, dex_output):
        assert rows_for(dex_output, 'EQ-001') == [
            ('1', 1, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is equal to 1</p>'),
            ('1', 2, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not equal to 1</p>'),
        ]

    def test_ne(self, dex_output):
        assert rows_for(dex_output, 'NE-001') == [
            ('1', 1, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is equal to 1</p>'),
            ('1', 2, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is not equal to 1</p>'),
        ]

    def test_range_neither_inclusive(self, dex_output):
        assert rows_for(dex_output, 'RANGE-001') == [
            ('(-1,1)', -2, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between -1 and 1 (non-inclusive)</p>'),
            ('(-1,1)', -1, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between -1 and 1 (non-inclusive)</p>'),
            ('(-1,1)',  0, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between -1 and 1 (non-inclusive)</p>'),
            ('(-1,1)',  1, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between -1 and 1 (non-inclusive)</p>'),
            ('(-1,1)',  2, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between -1 and 1 (non-inclusive)</p>'),
        ]

    def test_range_upper_only_exclusive(self, dex_output):
        assert rows_for(dex_output, 'RANGE-002') == [
            ('(-1,1]', -2, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between 1 and 1 (upper-only inclusive)</p>'),
            ('(-1,1]', -1, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between 1 and 1 (upper-only inclusive)</p>'),
            ('(-1,1]',  0, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between 1 and 1 (upper-only inclusive)</p>'),
            ('(-1,1]',  1, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between 1 and 1 (upper-only inclusive)</p>'),
            ('(-1,1]',  2, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between 1 and 1 (upper-only inclusive)</p>'),
        ]

    def test_range_lower_only_exclusive(self, dex_output):
        assert rows_for(dex_output, 'RANGE-003') == [
            ('[-1,1)', -2, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between -1 and 1 (lower-only inclusive)</p>'),
            ('[-1,1)', -1, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between -1 and 1 (lower-only inclusive)</p>'),
            ('[-1,1)',  0, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between -1 and 1 (lower-only inclusive)</p>'),
            ('[-1,1)',  1, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between -1 and 1 (lower-only inclusive)</p>'),
            ('[-1,1)',  2, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between -1 and 1 (lower-only inclusive)</p>'),
        ]

    def test_range_both_inclusive(self, dex_output):
        assert rows_for(dex_output, 'RANGE-004') == [
            ('[-10,10]', -11, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between -10 and 10 (inclusive)</p>'),
            ('[-10,10]', -10, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between -10 and 10 (inclusive)</p>'),
            ('[-10,10]',   0, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between -10 and 10 (inclusive)</p>'),
            ('[-10,10]',  10, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between -10 and 10 (inclusive)</p>'),
            ('[-10,10]',  11, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between -10 and 10 (inclusive)</p>'),
        ]

    def test_range_same_value_inclusive(self, dex_output):
        assert rows_for(dex_output, 'RANGE-005') == [
            ('[5,5]', 4, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between 5 and 5 (inclusve). Equivalent to eq 5</p>'),
            ('[5,5]', 5, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between 5 and 5 (inclusve). Equivalent to eq 5</p>'),
            ('[5,5]', 6, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between 5 and 5 (inclusve). Equivalent to eq 5</p>'),
        ]

    def test_range_same_non_value_inclusive(self, dex_output):
        assert rows_for(dex_output, 'RANGE-006') == [
            ('(5,5)', 4, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between 5 and 5 (non-inclusve). Should never be true</p>'),
            ('(5,5)', 5, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between 5 and 5 (non-inclusve). Should never be true</p>'),
            ('(5,5)', 6, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between 5 and 5 (non-inclusve). Should never be true</p>'),
        ]
