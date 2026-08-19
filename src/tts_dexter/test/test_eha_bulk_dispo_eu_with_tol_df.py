import pytest
from pathlib import Path

from tts_data_utils.core.data_frame import TtsDataFrame
from tts_dexter.core.dexter import Dexter
from tts_dexter.dispositioners.eha import DfLadEhaDispositioner
from tts_dexter.test.df_test_helpers import TEST_FILE_DIR, make_lad_frame, rows_for

EHA_DIR = TEST_FILE_DIR / 'eha_bulk_dispo'
RULES_CSV = EHA_DIR / 'eha_autodispositions.csv'
CHANVALS_CSV = EHA_DIR / 'eu_chanvals_with_tolerance.csv'


class _EuWithTolDispositioner(DfLadEhaDispositioner):
    pass


class _EuWithTolDexter(Dexter):
    def __init__(self, frame):
        super().__init__()
        self.all_input_data.set_data_one('lad_frame', frame)
        self.init_dispositioner(_EuWithTolDispositioner)


@pytest.fixture(scope='module')
def dex_output():
    frame = make_lad_frame(RULES_CSV, CHANVALS_CSV, group_filter='EU With Tolerance')
    dex = _EuWithTolDexter(frame)
    dex.disposition_all()
    return dex.stamp_all_to_outputs()['lad_frame']


@pytest.mark.unreviewed_ai_generated_test
class TestBulkEhaDispoEuWithToleranceDf:

    def test_gt(self, dex_output):
        assert rows_for(dex_output, 'GT-004') == [
            ('-1.234567', -1.2347,    '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not greater than -1.234567 within 1e-6</p>'),
            ('-1.234567', -1.234569,  '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not greater than -1.234567 within 1e-6</p>'),
            ('-1.234567', -1.234568,  '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not greater than -1.234567 within 1e-6</p>'),
            ('-1.234567', -1.234567,  '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is greater than -1.234567 within 1e-6</p>'),
            ('-1.234567', -1.234566,  '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is greater than -1.234567 within 1e-6</p>'),
            ('-1.234567', -1.234567,  '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is greater than -1.234567 within 1e-6</p>'),
            ('-1.234567', -1.234568,  '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not greater than -1.234567 within 1e-6</p>'),
        ]

    def test_lt(self, dex_output):
        assert rows_for(dex_output, 'LT-004') == [
            ('1.234567', 1.234564, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is less than 1.234567 within 1e-6</p>'),
            ('1.234567', 1.234565, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is less than 1.234567 within 1e-6</p>'),
            ('1.234567', 1.234566, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is less than 1.234567 within 1e-6</p>'),
            ('1.234567', 1.234567, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is less than 1.234567 within 1e-6</p>'),
            ('1.234567', 1.234568, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not less than 1.234567 within 1e-6</p>'),
            ('1.234567', 1.234569, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not less than 1.234567 within 1e-6</p>'),
            ('1.234567', 1.23457,  '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not less than 1.234567 within 1e-6</p>'),
        ]

    def test_gte(self, dex_output):
        assert rows_for(dex_output, 'GTE-004') == [
            ('-1.234567', -1.2347,   '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not greater than or equal to -1.234567 within 1e-6</p>'),
            ('-1.234567', -1.234569, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not greater than or equal to -1.234567 within 1e-6</p>'),
            ('-1.234567', -1.234568, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is greater than or equal to -1.234567 within 1e-6</p>'),
            ('-1.234567', -1.234567, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is greater than or equal to -1.234567 within 1e-6</p>'),
            ('-1.234567', -1.234566, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is greater than or equal to -1.234567 within 1e-6</p>'),
            ('-1.234567', -1.234567, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is greater than or equal to -1.234567 within 1e-6</p>'),
            ('-1.234567', -1.234568, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is greater than or equal to -1.234567 within 1e-6</p>'),
        ]

    def test_lte(self, dex_output):
        assert rows_for(dex_output, 'LTE-004') == [
            ('1.234567', 1.234564, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is less than or equal to 1.234567 within 1e-6</p>'),
            ('1.234567', 1.234565, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is less than or equal to 1.234567 within 1e-6</p>'),
            ('1.234567', 1.234566, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is less than or equal to 1.234567 within 1e-6</p>'),
            ('1.234567', 1.234567, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is less than or equal to 1.234567 within 1e-6</p>'),
            ('1.234567', 1.234568, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is less than or equal to 1.234567 within 1e-6</p>'),
            ('1.234567', 1.234569, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not less than or equal to 1.234567 within 1e-6</p>'),
            ('1.234567', 1.23457,  '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not less than or equal to 1.234567 within 1e-6</p>'),
        ]

    def test_eq(self, dex_output):
        assert rows_for(dex_output, 'EQ-004') == [
            ('-1.234567', -1.2347,   '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not equal to -1.234567 within 1e-6</p>'),
            ('-1.234567', -1.234569, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not equal to -1.234567 within 1e-6</p>'),
            ('-1.234567', -1.234568, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is equal to -1.234567 within 1e-6</p>'),
            ('-1.234567', -1.234567, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is equal to -1.234567 within 1e-6</p>'),
            ('-1.234567', -1.234566, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is equal to -1.234567 within 1e-6</p>'),
            ('-1.234567', -1.234565, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not equal to -1.234567 within 1e-6</p>'),
            ('-1.234567', -1.234564, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not equal to -1.234567 within 1e-6</p>'),
        ]

    def test_ne(self, dex_output):
        assert rows_for(dex_output, 'NE-004') == [
            ('1.234567', 1.234564, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is not equal to 1.234567 within 1e-6</p>'),
            ('1.234567', 1.234565, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is not equal to 1.234567 within 1e-6</p>'),
            ('1.234567', 1.234566, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is equal to 1.234567 within 1e-6</p>'),
            ('1.234567', 1.234567, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is equal to 1.234567 within 1e-6</p>'),
            ('1.234567', 1.234568, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is equal to 1.234567 within 1e-6</p>'),
            ('1.234567', 1.234569, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is not equal to 1.234567 within 1e-6</p>'),
            ('1.234567', 1.23457,  '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is not equal to 1.234567 within 1e-6</p>'),
        ]

    def test_range_neither_inclusive(self, dex_output):
        assert rows_for(dex_output, 'RANGE-019') == [
            ('(-1.234567,1.234567)', -1.234569, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between -1.234567 and 1.234567  within 1e-6 (non-inclusive)</p>'),
            ('(-1.234567,1.234567)', -1.234568, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between -1.234567 and 1.234567  within 1e-6 (non-inclusive)</p>'),
            ('(-1.234567,1.234567)', -1.234567, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between -1.234567 and 1.234567  within 1e-6 (non-inclusive)</p>'),
            ('(-1.234567,1.234567)',  0.0,      '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between -1.234567 and 1.234567  within 1e-6 (non-inclusive)</p>'),
            ('(-1.234567,1.234567)',  1.234567, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between -1.234567 and 1.234567  within 1e-6 (non-inclusive)</p>'),
            ('(-1.234567,1.234567)',  1.234568, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between -1.234567 and 1.234567  within 1e-6 (non-inclusive)</p>'),
            ('(-1.234567,1.234567)',  1.234569, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between -1.234567 and 1.234567  within 1e-6 (non-inclusive)</p>'),
        ]

    def test_range_upper_only_exclusive(self, dex_output):
        assert rows_for(dex_output, 'RANGE-020') == [
            ('(-1.234567,1.234567]', -1.234569, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between -1.234567 and 1.234567  within 1e-6 (upper-only inclusive)</p>'),
            ('(-1.234567,1.234567]', -1.234568, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between -1.234567 and 1.234567  within 1e-6 (upper-only inclusive)</p>'),
            ('(-1.234567,1.234567]', -1.234567, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between -1.234567 and 1.234567  within 1e-6 (upper-only inclusive)</p>'),
            ('(-1.234567,1.234567]',  0.0,      '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between -1.234567 and 1.234567  within 1e-6 (upper-only inclusive)</p>'),
            ('(-1.234567,1.234567]',  1.234567, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between -1.234567 and 1.234567  within 1e-6 (upper-only inclusive)</p>'),
            ('(-1.234567,1.234567]',  1.234568, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between -1.234567 and 1.234567  within 1e-6 (upper-only inclusive)</p>'),
            ('(-1.234567,1.234567]',  1.234569, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between -1.234567 and 1.234567  within 1e-6 (upper-only inclusive)</p>'),
        ]

    def test_range_lower_only_exclusive(self, dex_output):
        assert rows_for(dex_output, 'RANGE-021') == [
            ('[-1.234567,1.234567)', -1.234569, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between -1.234567 and 1.234567  within 1e-6 (lower-only inclusive)</p>'),
            ('[-1.234567,1.234567)', -1.234568, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between -1.234567 and 1.234567  within 1e-6 (lower-only inclusive)</p>'),
            ('[-1.234567,1.234567)', -1.234567, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between -1.234567 and 1.234567  within 1e-6 (lower-only inclusive)</p>'),
            ('[-1.234567,1.234567)',  0.0,      '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between -1.234567 and 1.234567  within 1e-6 (lower-only inclusive)</p>'),
            ('[-1.234567,1.234567)',  1.234567, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between -1.234567 and 1.234567  within 1e-6 (lower-only inclusive)</p>'),
            ('[-1.234567,1.234567)',  1.234568, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between -1.234567 and 1.234567  within 1e-6 (lower-only inclusive)</p>'),
            ('[-1.234567,1.234567)',  1.234569, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between -1.234567 and 1.234567  within 1e-6 (lower-only inclusive)</p>'),
        ]

    def test_range_both_inclusive(self, dex_output):
        assert rows_for(dex_output, 'RANGE-022') == [
            ('[-1.234567,1.234567]', -1.234569, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between -1.234567 and 1.234567  within 1e-6 (inclusive)</p>'),
            ('[-1.234567,1.234567]', -1.234568, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between -1.234567 and 1.234567  within 1e-6 (inclusive)</p>'),
            ('[-1.234567,1.234567]', -1.234567, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between -1.234567 and 1.234567  within 1e-6 (inclusive)</p>'),
            ('[-1.234567,1.234567]',  0.0,      '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between -1.234567 and 1.234567  within 1e-6 (inclusive)</p>'),
            ('[-1.234567,1.234567]',  1.234567, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between -1.234567 and 1.234567  within 1e-6 (inclusive)</p>'),
            ('[-1.234567,1.234567]',  1.234568, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between -1.234567 and 1.234567  within 1e-6 (inclusive)</p>'),
            ('[-1.234567,1.234567]',  1.234569, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between -1.234567 and 1.234567  within 1e-6 (inclusive)</p>'),
        ]

    def test_range_same_value_inclusive(self, dex_output):
        assert rows_for(dex_output, 'RANGE-023') == [
            ('[1.234567,1.234567]', 1.234563, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between 1.234567 and 1.234567  within 1e-6 (inclusve). Equivalent to eq 1.234567</p>'),
            ('[1.234567,1.234567]', 1.234564, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between 1.234567 and 1.234567  within 1e-6 (inclusve). Equivalent to eq 1.234567</p>'),
            ('[1.234567,1.234567]', 1.234565, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between 1.234567 and 1.234567  within 1e-6 (inclusve). Equivalent to eq 1.234567</p>'),
            ('[1.234567,1.234567]', 1.234566, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between 1.234567 and 1.234567  within 1e-6 (inclusve). Equivalent to eq 1.234567</p>'),
            ('[1.234567,1.234567]', 1.234567, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between 1.234567 and 1.234567  within 1e-6 (inclusve). Equivalent to eq 1.234567</p>'),
            ('[1.234567,1.234567]', 1.234568, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between 1.234567 and 1.234567  within 1e-6 (inclusve). Equivalent to eq 1.234567</p>'),
            ('[1.234567,1.234567]', 1.234569, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between 1.234567 and 1.234567  within 1e-6 (inclusve). Equivalent to eq 1.234567</p>'),
        ]

    def test_range_same_non_value_inclusive(self, dex_output):
        assert rows_for(dex_output, 'RANGE-024') == [
            ('[1.234567,1.234567]', 1.234563, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between 1.234567 and 1.234567  within 1e-6 (non-inclusve).</p>'),
            ('(1.234567,1.234567)', 1.234564, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between 1.234567 and 1.234567  within 1e-6 (non-inclusve).</p>'),
            ('(1.234567,1.234567)', 1.234565, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between 1.234567 and 1.234567  within 1e-6 (non-inclusve).</p>'),
            ('(1.234567,1.234567)', 1.234566, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between 1.234567 and 1.234567  within 1e-6 (non-inclusve).</p>'),
            ('(1.234567,1.234567)', 1.234567, '<p><strong><span style="color:#68BC00">Expected</span></strong> - EU chanval is between 1.234567 and 1.234567  within 1e-6 (non-inclusve).</p>'),
            ('(1.234567,1.234567)', 1.234568, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between 1.234567 and 1.234567  within 1e-6 (non-inclusve).</p>'),
            ('(1.234567,1.234567)', 1.234569, '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - EU chanval is not between 1.234567 and 1.234567  within 1e-6 (non-inclusve).</p>'),
        ]
