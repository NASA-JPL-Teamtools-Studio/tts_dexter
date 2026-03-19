import pytest

from jpl_time import Time, Duration

from tts_data_utils.invulnerable_data_manager.utilities import set_global_invulnerable, clear_global_invulnerable, cached_property, exec_invulnerable

from tts_data_utils.core.data_item import DataItem
from tts_data_utils.core.data_container import DataContainer

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

