import pytest
from pathlib import Path

from tts_data_utils.core.data_frame import TtsDataFrame
from tts_dexter.core.dexter import Dexter
from tts_dexter.dispositioners.eha import DfLadEhaDispositioner
from tts_dexter.test.df_test_helpers import TEST_FILE_DIR, make_lad_frame, rows_for

EHA_DIR = TEST_FILE_DIR / 'eha_bulk_dispo'
RULES_CSV = EHA_DIR / 'eha_autodispositions.csv'
CHANVALS_CSV = EHA_DIR / 'status_and_dnString_chanvals.csv'


class _StatusDnStrDispositioner(DfLadEhaDispositioner):
    pass


class _StatusDnStrDexter(Dexter):
    def __init__(self, frame):
        super().__init__()
        self.all_input_data.set_data_one('lad_frame', frame)
        self.init_dispositioner(_StatusDnStrDispositioner)


@pytest.fixture(scope='module')
def dex_output():
    frame = make_lad_frame(RULES_CSV, CHANVALS_CSV, group_filter=None)
    dex = _StatusDnStrDexter(frame)
    dex.disposition_all()
    return dex.stamp_all_to_outputs()['lad_frame']


@pytest.mark.unreviewed_ai_generated_test
class TestBulkEhaDispoStatusDf:

    def test_eq(self, dex_output):
        assert rows_for(dex_output, 'STATUS-001') == [
            ('OPTION_1', 'OPTION_1', '<p><strong><span style="color:#68BC00">Expected</span></strong> - Status chanval is equal to OPTION_1</p>'),
            ('OPTION_1', 'OPTION_2', '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - Status chanval is not equal to OPTION_1</p>'),
        ]

    def test_ne(self, dex_output):
        assert rows_for(dex_output, 'STATUS-002') == [
            ('OPTION_1', 'OPTION_1', '<p><strong><span style="color:#68BC00">Expected</span></strong> - Status chanval is not equal to OPTION_2</p>'),
            ('OPTION_1', 'OPTION_2', '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - Status chanval is equal to OPTION_2</p>'),
        ]

    def test_isin(self, dex_output):
        assert rows_for(dex_output, 'STATUS-003') == [
            ('OPTION_1, OPTION_2', 'OPTION_1', '<p><strong><span style="color:#68BC00">Expected</span></strong> - Status chanval is either OPTION_1 or OPTION_2</p>'),
            ('OPTION_1, OPTION_2', 'OPTION_2', '<p><strong><span style="color:#68BC00">Expected</span></strong> - Status chanval is either OPTION_1 or OPTION_2</p>'),
        ]

    def test_notin(self, dex_output):
        assert rows_for(dex_output, 'STATUS-004') == [
            ('OPTION_1, OPTION_2', 'OPTION_1', '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - Status chanval is not neither OPTION_1 nor OPTION_2</p>'),
            ('OPTION_1, OPTION_2', 'OPTION_2', '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - Status chanval is not neither OPTION_1 nor OPTION_2</p>'),
        ]


@pytest.mark.unreviewed_ai_generated_test
class TestBulkEhaDispoDnStringDf:

    def test_eq(self, dex_output):
        assert rows_for(dex_output, 'DNSTR-001') == [
            ('StringValue1', 'StringValue1', '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN String chanval is equal to StringValue1</p>'),
            ('StringValue1', 'StringValue2', '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN String chanval is not equal to StringValue1</p>'),
        ]

    def test_ne(self, dex_output):
        assert rows_for(dex_output, 'DNSTR-002') == [
            ('StringValue1', 'StringValue1', '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN String chanval is not equal to StringValue1</p>'),
            ('StringValue1', 'StringValue2', '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN String chanval is equal to StringValue1</p>'),
        ]

    def test_isin(self, dex_output):
        assert rows_for(dex_output, 'DNSTR-003') == [
            ('StringValue1,StringValue2', 'StringValue1', '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN String chanval is equal to StringValue1</p>'),
            ('StringValue1,StringValue2', 'StringValue2', '<p><strong><span style="color:#68BC00">Expected</span></strong> - DN String chanval is equal to StringValue1</p>'),
        ]

    def test_notin(self, dex_output):
        assert rows_for(dex_output, 'DNSTR-004') == [
            ('StringValue1,StringValue2', 'StringValue1', '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN String chanval is equal to StringValue1</p>'),
            ('StringValue1,StringValue2', 'StringValue2', '<p><strong><span style="color:#FF6347">Unexpected</span></strong> - DN String chanval is equal to StringValue1</p>'),
        ]
