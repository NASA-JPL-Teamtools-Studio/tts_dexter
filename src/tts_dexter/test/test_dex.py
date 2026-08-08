import pytest

from jpl_time import Time, Duration

from tts_data_utils.invulnerable_data_manager.utilities import set_global_invulnerable, clear_global_invulnerable, cached_property, exec_invulnerable

from tts_data_utils.core.data_item import DataItem
from tts_data_utils.core.data_container import DataContainer
from tts_data_utils.core.data_frame import TtsDataFrame

from tts_dexter.core.dexter import Dexter
from tts_dexter.core.dispo import Dispositioner, Disposition, dispo_method
from tts_data_utils.invulnerable_data_manager.batch import Batch, Batcher
    
#TO DO: We should move this to a new tts-spice library
#No plans to do a lot that's not already in spiceypy
#but if we want to eventually, that's a place to put
#common transforms and extensions. But for now it's
#just a place to put some kind of
#tts_spice.furnish() method that can do this for us
#in a common way. It will also give us a single place
#to do soemthign like update a kernel for everyone
#without having to go edit every TTS library...
#but for not we're just going to do it local
import spiceypy
from pathlib import Path
spiceypy.furnsh(str(Path(__file__).parent.joinpath('naif0012.tls')))

clear_global_invulnerable()

class DataItem_Test(DataItem):
    DICT_VALID_KEYS = []

    @cached_property
    def time(self):
        return Time('2000-001T12:00:00') + Duration('01:00:00')*self.data_value
    
    @property
    def data_value(self):
        return self.source['data']
    
    @property
    def valid(self):
        return True
    
    def stamp(self, dispo_value):
        self.source['disposition'] = dispo_value

class DataContainer_Test(DataContainer):
    NAME = 'test_data'
    DATA_ITEM_CLS = DataItem_Test
    
@pytest.fixture
def dex_empty():
    return Dexter()

@pytest.fixture
def dex_basic_dispositionable():

    class _Dispositioner(Dispositioner):
        @dispo_method(['test_data'])
        def dispo_various_statuses(self, data_test):
            data_test.records[0].new_dispo().expected('EXPECTED')
            data_test.records[1].new_dispo().unexpected('UNEXPECTED')
            ops_check_dispo = Disposition(); ops_check_dispo.ops_check('OPS_CHECK')
            data_test.records[2].add_dispo(ops_check_dispo)
            

    class _Dexter(Dexter):
        def __init__(self):
            super().__init__()
            self.init_data(DataContainer_Test, [{'data': i} for i in range(3)])
            self.init_dispositioner(_Dispositioner)
            
    return _Dexter()

@pytest.fixture
def dex_batched():        

    class ZeroBatcher(Batcher):
        NAME = 'zero_batch'
        
        def _make_batches(self):
            zero_batch = Batch('zeroes', tag_data=True)
            zero_data = self.source_batch.subdivide_on_condition(lambda x: x.source['data'] == 0)
            zero_batch.set_data(**zero_data)
            self._add_batch(zero_batch)
            
    class TimeRangeBatcher(Batcher):
        NAME = 'time_batch'
        
        def _make_batches(self):
            both_batch = Batch('both_range', tag_data=True)
            both_data = self.source_batch.subdivide_on_time(
                start_time=Time('2000-001T12:30:00'),
                end_time=Time('2000-001T13:30:00')
            )
            both_batch.set_data(**both_data)
            self._add_batch(both_batch)
            
            start_batch = Batch('start_range', tag_data=True)
            start_data = self.source_batch.subdivide_on_time(
                start_time=Time('2000-001T13:30:00')
            )
            start_batch.set_data(**start_data)
            self._add_batch(start_batch)
            
            end_batch = Batch('end_range', tag_data=True)
            end_data = self.source_batch.subdivide_on_time(
                end_time=Time('2000-001T13:30:00')
            )
            end_batch.set_data(**end_data)
            self._add_batch(end_batch)

    class _Dexter(Dexter):
        def __init__(self):
            super().__init__()
            self.init_data(DataContainer_Test, [{'data': i} for i in range(4)])
            self.init_batcher(ZeroBatcher)

            self.init_batcher(TimeRangeBatcher)
            
    return _Dexter()

def test_dex_creation(dex_empty):
    assert dex_empty
    
def test_dex_dispo(dex_basic_dispositionable):
    dex_basic_dispositionable.disposition_all()
    assert True
    
def test_dex_stamp(dex_basic_dispositionable):
    dex_basic_dispositionable.stamp_all()
    assert True
    
def test_dex_batched(dex_batched):
    batch_data = dex_batched.get_batcher('zero_batch').batches[0].get_data('test_data')
    assert(len(batch_data.source)) == 1
    batch_data = dex_batched.get_batcher('time_batch').batches[0].get_data('test_data')
    assert(len(batch_data.source)) == 1
    batch_data = dex_batched.get_batcher('time_batch').batches[1].get_data('test_data')
    assert(len(batch_data.source)) == 2
    batch_data = dex_batched.get_batcher('time_batch').batches[2].get_data('test_data')
    assert(len(batch_data.source)) == 2
    
def test_invulnerable():
    def die():
        raise Exception
    
    set_global_invulnerable()
    exec_invulnerable(die)
    clear_global_invulnerable()
    assert True

def test_dex_stamp_to_outputs(dex_basic_dispositionable):
    # Run dispositions first so stamp_all has something to stamp
    dex_basic_dispositionable.disposition_all()

    outputs = dex_basic_dispositionable.stamp_all_to_outputs()

    # Outputs should be populated
    assert outputs
    # all_output_data is an AllDataBatch; ensure its internal map is non-empty
    assert dex_basic_dispositionable.all_output_data.data_map

    # Original inputs still exist and are distinct objects
    input_container = dex_basic_dispositionable.get_input_data("test_data")
    output_container = dex_basic_dispositionable.get_output_data("test_data")
    assert input_container is not output_container

    # Output container should have dispositions stamped
    # We don't assert specific string formatting here, just presence
    assert any("disposition" in r.source for r in output_container.records)


@pytest.mark.unreviewed_ai_generated_test
def test_dex_with_tts_dataframe_rows():
    """Dexter can operate on a TtsDataFrame input via stamp_all_to_outputs.

    Builds a small frame, registers it on Dexter's all_input_data, runs a
    dispositioner that uses TtsRowSeries/DexterRowMixin row methods, then
    verifies stamp_all_to_outputs produces a separate stamped frame.
    """
    class FrameForDex(TtsDataFrame):
        pass

    times = [Time('2000-001T12:00:00') + Duration(f'00:00:0{i}') for i in range(3)]
    data = [
        {"time": times[0], "label": "a", "value": 1.0},
        {"time": times[1], "label": "a", "value": 2.0},
        {"time": times[2], "label": "b", "value": 3.0},
    ]
    frame = FrameForDex(data, coerce=False, validate=False)

    dex = Dexter()
    input_name = "frame_data"
    dex.all_input_data.set_data_one(input_name, frame)

    class _FrameDispositioner(Dispositioner):
        @dispo_method([input_name])
        def mark_all_ok(self, df):
            for _, row in df.iterrows():
                row.new_dispo().expected("OK")

    dex.init_dispositioner(_FrameDispositioner)
    dex.disposition_all()

    outputs = dex.stamp_all_to_outputs()

    assert input_name in outputs
    out_frame = outputs[input_name]

    # Input and output must be distinct objects
    assert out_frame is not frame

    # Disposition column should exist and be populated for all rows
    assert "disposition" in out_frame.columns
    assert out_frame["disposition"].notna().all()