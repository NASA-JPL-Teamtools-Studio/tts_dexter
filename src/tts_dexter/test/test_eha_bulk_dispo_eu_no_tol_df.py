import pytest
from pathlib import Path

from tts_data_utils.core.data_frame import TtsDataFrame
from tts_dexter.core.dexter import Dexter
from tts_dexter.dispositioners.eha import DfLadEhaDispositioner
from tts_dexter.test.df_test_helpers import TEST_FILE_DIR, make_lad_frame, rows_for

EHA_DIR = TEST_FILE_DIR / 'eha_bulk_dispo'
RULES_CSV = EHA_DIR / 'eha_autodispositions.csv'
CHANVALS_CSV = EHA_DIR / 'eu_chanvals_no_tolerance.csv'


class _EuNoTolDispositioner(DfLadEhaDispositioner):
    pass


class _EuNoTolDexter(Dexter):
    def __init__(self, frame):
        super().__init__()
        self.all_input_data.set_data_one('lad_frame', frame)
        self.init_dispositioner(_EuNoTolDispositioner)


@pytest.fixture(scope='module')
def dex_output():
    frame = make_lad_frame(RULES_CSV, CHANVALS_CSV, group_filter='EU No Tolerance')
    dex = _EuNoTolDexter(frame)
    dex.disposition_all()
    return dex.stamp_all_to_outputs()['lad_frame']


@pytest.mark.unreviewed_ai_generated_test
class TestBulkEhaDispoEuNoToleranceDf:

    def test_gt(self, dex_output):
        assert rows_for(dex_output, 'GT-003') == [
            ('-1.234567', -1.234568, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not greater than -1.234567</p>'),
            ('-1.234567', -1.234567, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not greater than -1.234567</p>'),
            ('-1.234567', -1.234566, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is greater than -1.234567</p>'),
        ]

    def test_lt(self, dex_output):
        assert rows_for(dex_output, 'LT-003') == [
            ('1.234567', 1.234566, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is less than 1.234567</p>'),
            ('1.234567', 1.234567, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not less than 1.234567</p>'),
            ('1.234567', 1.234568, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not less than 1.234567</p>'),
        ]

    def test_gte(self, dex_output):
        assert rows_for(dex_output, 'GTE-003') == [
            ('-1.234567', -1.234568, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not greater than or equal to -1.234567</p>'),
            ('-1.234567', -1.234567, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is greater than or equal to -1.234567</p>'),
            ('-1.234567', -1.234566, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is greater than or equal to -1.234567</p>'),
        ]

    def test_lte(self, dex_output):
        assert rows_for(dex_output, 'LTE-003') == [
            ('1.234567', 1.234566, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is less than or equal to 1.234567</p>'),
            ('1.234567', 1.234567, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is less than or equal to 1.234567</p>'),
            ('1.234567', 1.234568, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not less than or equal to 1.234567</p>'),
        ]

    def test_eq(self, dex_output):
        assert rows_for(dex_output, 'EQ-003') == [
            ('1.234567', 1.234566, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not equal to 1.234567</p>'),
            ('1.234567', 1.234567, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is equal to 1.234567</p>'),
            ('1.234567', 1.234568, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not equal to 1.234567</p>'),
        ]

    def test_ne(self, dex_output):
        assert rows_for(dex_output, 'NE-003') == [
            ('1.234567', 1.234566, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is not equal to 1.234567</p>'),
            ('1.234567', 1.234567, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is equal to 1.234567</p>'),
            ('1.234567', 1.234568, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is not equal to 1.234567</p>'),
        ]

    def test_range_neither_inclusive(self, dex_output):
        assert rows_for(dex_output, 'RANGE-013') == [
            ('(-1.234567,1.234567)', -1.234568, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between -1.234567 and 1.234567 (non-inclusive)</p>'),
            ('(-1.234567,1.234567)', -1.234567, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between -1.234567 and 1.234567 (non-inclusive)</p>'),
            ('(-1.234567,1.234567)',  0.0,      '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between -1.234567 and 1.234567 (non-inclusive)</p>'),
            ('(-1.234567,1.234567)',  1.234567, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between -1.234567 and 1.234567 (non-inclusive)</p>'),
            ('(-1.234567,1.234567)',  1.234568, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between -1.234567 and 1.234567 (non-inclusive)</p>'),
        ]

    def test_range_upper_only_exclusive(self, dex_output):
        assert rows_for(dex_output, 'RANGE-014') == [
            ('(-1.234567,1.234567]', -1.234568, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between 1.234567 and 1.234567 (upper-only inclusive)</p>'),
            ('(-1.234567,1.234567]', -1.234567, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between 1.234567 and 1.234567 (upper-only inclusive)</p>'),
            ('(-1.234567,1.234567]',  0.0,      '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between 1.234567 and 1.234567 (upper-only inclusive)</p>'),
            ('(-1.234567,1.234567]',  1.234567, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between 1.234567 and 1.234567 (upper-only inclusive)</p>'),
            ('(-1.234567,1.234567]',  1.234568, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between 1.234567 and 1.234567 (upper-only inclusive)</p>'),
        ]

    def test_range_lower_only_exclusive(self, dex_output):
        assert rows_for(dex_output, 'RANGE-015') == [
            ('[-1.234567,1.234567)', -1.234568, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between -1.234567 and 1.234567 (lower-only inclusive)</p>'),
            ('[-1.234567,1.234567)', -1.234567, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between -1.234567 and 1.234567 (lower-only inclusive)</p>'),
            ('[-1.234567,1.234567)',  0.0,      '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between -1.234567 and 1.234567 (lower-only inclusive)</p>'),
            ('[-1.234567,1.234567)',  1.234567, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between -1.234567 and 1.234567 (lower-only inclusive)</p>'),
            ('[-1.234567,1.234567)',  1.234568, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between -1.234567 and 1.234567 (lower-only inclusive)</p>'),
        ]

    def test_range_both_inclusive(self, dex_output):
        assert rows_for(dex_output, 'RANGE-016') == [
            ('[-1.234567,1.234567]', -1.234568, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between -1.234567 and 1.234567 (inclusive)</p>'),
            ('[-1.234567,1.234567]', -1.234567, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between -1.234567 and 1.234567 (inclusive)</p>'),
            ('[-1.234567,1.234567]',  0.0,      '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between -1.234567 and 1.234567 (inclusive)</p>'),
            ('[-1.234567,1.234567]',  1.234567, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between -1.234567 and 1.234567 (inclusive)</p>'),
            ('[-1.234567,1.234567]',  1.234568, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between -1.234567 and 1.234567 (inclusive)</p>'),
        ]

    def test_range_same_value_inclusive(self, dex_output):
        assert rows_for(dex_output, 'RANGE-017') == [
            ('[-1.234567,-1.234567]', -1.234568, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between -1.234567 and -1.234567 (inclusve). Equivalent to eq -1.234567</p>'),
            ('[-1.234567,-1.234567]', -1.234567, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between -1.234567 and -1.234567 (inclusve). Equivalent to eq -1.234567</p>'),
            ('[-1.234567,-1.234567]',  0.0,      '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between -1.234567 and -1.234567 (inclusve). Equivalent to eq -1.234567</p>'),
            ('[-1.234567,-1.234567]',  1.234567, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between -1.234567 and -1.234567 (inclusve). Equivalent to eq -1.234567</p>'),
            ('[-1.234567,-1.234567]',  1.234568, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between -1.234567 and -1.234567 (inclusve). Equivalent to eq -1.234567</p>'),
        ]

    def test_range_same_non_value_inclusive(self, dex_output):
        assert rows_for(dex_output, 'RANGE-018') == [
            ('(-1.234567,-1.234567)', -1.234568, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between -1.234567 and -1.234567 (non-inclusve). Should always trigger</p>'),
            ('(-1.234567,-1.234567)', -1.234567, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between -1.234567 and -1.234567 (non-inclusve). Should always trigger</p>'),
            ('(-1.234567,-1.234567)',  0.0,      '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between -1.234567 and -1.234567 (non-inclusve). Should always trigger</p>'),
            ('(-1.234567,-1.234567)',  1.234567, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between -1.234567 and -1.234567 (non-inclusve). Should always trigger</p>'),
            ('(-1.234567,-1.234567)',  1.234568, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between -1.234567 and -1.234567 (non-inclusve). Should always trigger</p>'),
        ]
