import pytest
from pathlib import Path

from tts_data_utils.core.data_frame import TtsDataFrame
from tts_dexter.core.dexter import Dexter
from tts_dexter.dispositioners.eha import DfLadEhaDispositioner
from tts_dexter.test.df_test_helpers import TEST_FILE_DIR, make_lad_frame, rows_for

EHA_DIR = TEST_FILE_DIR / 'eha_bulk_dispo'
RULES_CSV = EHA_DIR / 'eha_autodispositions.csv'
CHANVALS_CSV = EHA_DIR / 'dn_chanvals_with_tolerance.csv'


class _DnWithTolDispositioner(DfLadEhaDispositioner):
    pass


class _DnWithTolDexter(Dexter):
    def __init__(self, frame):
        super().__init__()
        self.all_input_data.set_data_one('lad_frame', frame)
        self.init_dispositioner(_DnWithTolDispositioner)


@pytest.fixture(scope='module')
def dex_output():
    frame = make_lad_frame(RULES_CSV, CHANVALS_CSV, group_filter='DN With Tolerance')
    dex = _DnWithTolDexter(frame)
    dex.disposition_all()
    return dex.stamp_all_to_outputs()['lad_frame']


@pytest.mark.unreviewed_ai_generated_test
class TestBulkEhaDispoDnWithToleranceDf:

    def test_gt(self, dex_output):
        assert rows_for(dex_output, 'GT-002') == [
            ('-1', -1.01,  '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not greater than -1 within 1e-3</p>'),
            ('-1', -1.001, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not greater than -1 within 1e-3</p>'),
            ('-1', -1.0,   '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is greater than -1 within 1e-3</p>'),
            ('-1', -0.999, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is greater than -1 within 1e-3</p>'),
            ('-1', -0.99,  '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is greater than -1 within 1e-3</p>'),
        ]

    def test_lt(self, dex_output):
        assert rows_for(dex_output, 'LT-002') == [
            ('1', 0.99,  '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is less than 1 within 1e-3</p>'),
            ('1', 0.999, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is less than 1 within 1e-3</p>'),
            ('1', 1.0,   '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is less than 1 within 1e-3</p>'),
            ('1', 1.001, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not less than 1 within 1e-3</p>'),
            ('1', 1.01,  '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not less than 1 within 1e-3</p>'),
        ]

    def test_gte(self, dex_output):
        assert rows_for(dex_output, 'GTE-002') == [
            ('-1', -1.01,  '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not greater than or equal to -1 within 1e-3</p>'),
            ('-1', -1.001, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is greater than or equal to -1 within 1e-3</p>'),
            ('-1', -1.0,   '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is greater than or equal to -1 within 1e-3</p>'),
            ('-1', -0.999, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is greater than or equal to -1 within 1e-3</p>'),
            ('-1', -0.99,  '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is greater than or equal to -1 within 1e-3</p>'),
        ]

    def test_lte(self, dex_output):
        assert rows_for(dex_output, 'LTE-002') == [
            ('1', 0.99,  '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is less than or equal to 1 within 1e-3</p>'),
            ('1', 0.999, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is less than or equal to 1 within 1e-3</p>'),
            ('1', 1.0,   '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is less than or equal to 1 within 1e-3</p>'),
            ('1', 1.001, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is less than or equal to 1 within 1e-3</p>'),
            ('1', 1.01,  '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not less than or equal to 1 within 1e-3</p>'),
        ]

    def test_eq(self, dex_output):
        assert rows_for(dex_output, 'EQ-002') == [
            ('2', 1.998, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not equal to 1 within 1e-3</p>'),
            ('2', 1.999, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is equal to 1 within 1e-3</p>'),
            ('2', 2.0,   '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is equal to 1 within 1e-3</p>'),
            ('2', 2.001, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is equal to 1 within 1e-3</p>'),
            ('2', 2.002, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not equal to 1 within 1e-3</p>'),
        ]

    def test_ne(self, dex_output):
        assert rows_for(dex_output, 'NE-002') == [
            ('2', 1.998, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is not equal to 1 within 1e-3</p>'),
            ('2', 1.999, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is equal to 1 within 1e-3</p>'),
            ('2', 2.0,   '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is equal to 1 within 1e-3</p>'),
            ('2', 2.001, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is equal to 1 within 1e-3</p>'),
            ('2', 2.002, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is not equal to 1 within 1e-3</p>'),
        ]

    def test_range_neither_inclusive(self, dex_output):
        assert rows_for(dex_output, 'RANGE-007') == [
            ('(-1,1)', -1.002, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between -1 and 1  within 1e-3 (non-inclusive)</p>'),
            ('(-1,1)', -1.001, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between -1 and 1  within 1e-3 (non-inclusive)</p>'),
            ('(-1,1)', -1.0,   '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between -1 and 1  within 1e-3 (non-inclusive)</p>'),
            ('(-1,1)',  0.0,   '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between -1 and 1  within 1e-3 (non-inclusive)</p>'),
            ('(-1,1)',  1.0,   '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between -1 and 1  within 1e-3 (non-inclusive)</p>'),
            ('(-1,1)',  1.001, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between -1 and 1  within 1e-3 (non-inclusive)</p>'),
            ('(-1,1)',  1.002, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between -1 and 1  within 1e-3 (non-inclusive)</p>'),
        ]

    def test_range_upper_only_inclusive(self, dex_output):
        assert rows_for(dex_output, 'RANGE-008') == [
            ('(-1,1]', -1.002, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between -1 and 1  within 1e-3 (upper-only inclusive)</p>'),
            ('(-1,1]', -1.001, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between -1 and 1  within 1e-3 (upper-only inclusive)</p>'),
            ('(-1,1]', -1.0,   '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between -1 and 1  within 1e-3 (upper-only inclusive)</p>'),
            ('(-1,1]',  0.0,   '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between -1 and 1  within 1e-3 (upper-only inclusive)</p>'),
            ('(-1,1]',  1.0,   '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between -1 and 1  within 1e-3 (upper-only inclusive)</p>'),
            ('(-1,1]',  1.001, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between -1 and 1  within 1e-3 (upper-only inclusive)</p>'),
            ('(-1,1]',  1.002, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between -1 and 1  within 1e-3 (upper-only inclusive)</p>'),
        ]

    def test_range_lower_only_inclusive(self, dex_output):
        assert rows_for(dex_output, 'RANGE-009') == [
            ('[-1,1)', -1.002, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between -1 and 1  within 1e-3 (lower-only inclusive)</p>'),
            ('[-1,1)', -1.001, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between -1 and 1  within 1e-3 (lower-only inclusive)</p>'),
            ('[-1,1)', -1.0,   '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between -1 and 1  within 1e-3 (lower-only inclusive)</p>'),
            ('[-1,1)',  0.0,   '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between -1 and 1  within 1e-3 (lower-only inclusive)</p>'),
            ('[-1,1)',  1.0,   '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between -1 and 1  within 1e-3 (lower-only inclusive)</p>'),
            ('[-1,1)',  1.001, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between -1 and 1  within 1e-3 (lower-only inclusive)</p>'),
            ('[-1,1)',  1.002, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between -1 and 1  within 1e-3 (lower-only inclusive)</p>'),
        ]

    def test_range_both_inclusive(self, dex_output):
        assert rows_for(dex_output, 'RANGE-010') == [
            ('[-1,1]', -1.002, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between -1 and 1  within 1e-3 (inclusive)</p>'),
            ('[-1,1]', -1.001, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between -1 and 1  within 1e-3 (inclusive)</p>'),
            ('[-1,1]', -1.0,   '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between -1 and 1  within 1e-3 (inclusive)</p>'),
            ('[-1,1]',  0.0,   '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between -1 and 1  within 1e-3 (inclusive)</p>'),
            ('[-1,1]',  1.0,   '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between -1 and 1  within 1e-3 (inclusive)</p>'),
            ('[-1,1]',  1.001, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between -1 and 1  within 1e-3 (inclusive)</p>'),
            ('[-1,1]',  1.002, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between -1 and 1  within 1e-3 (inclusive)</p>'),
        ]

    def test_range_same_value_inclusive(self, dex_output):
        assert rows_for(dex_output, 'RANGE-011') == [
            ('[1,1]', -1.002, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between 1 and 1  within 1e-3 (inclusve). Equivalent to eq 1</p>'),
            ('[1,1]', -1.001, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between 1 and 1  within 1e-3 (inclusve). Equivalent to eq 1</p>'),
            ('[1,1]', -1.0,   '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between 1 and 1  within 1e-3 (inclusve). Equivalent to eq 1</p>'),
            ('[1,1]',  0.0,   '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between 1 and 1  within 1e-3 (inclusve). Equivalent to eq 1</p>'),
            ('[1,1]',  1.0,   '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between 11 and 1  within 1e-3 (inclusve). Equivalent to eq 1</p>'),
            ('[1,1]',  1.001, '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between 11 and 1  within 1e-3 (inclusve). Equivalent to eq 1</p>'),
            ('[1,1]',  1.002, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between 1 and 1  within 1e-3 (inclusve). Equivalent to eq 1</p>'),
        ]

    def test_range_same_value_non_inclusive(self, dex_output):
        assert rows_for(dex_output, 'RANGE-012') == [
            ('(1,1)', -1.002, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between 1 and 1  within 1e-3 (non-inclusve).</p>'),
            ('(1,1)', -1.001, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between 1 and 1  within 1e-3 (non-inclusve).</p>'),
            ('(1,1)', -1.0,   '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between 1 and 1  within 1e-3 (non-inclusve).</p>'),
            ('(1,1)',  0.0,   '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between 1 and 1  within 1e-3 (non-inclusve).</p>'),
            ('(1,1)',  1.0,   '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN chanval is between 1 and 1  within 1e-3 (non-inclusve).</p>'),
            ('(1,1)',  1.001, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between 1 and 1  within 1e-3 (non-inclusve).</p>'),
            ('(1,1)',  1.002, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN chanval is not between 1 and 1  within 1e-3 (non-inclusve).</p>'),
        ]
