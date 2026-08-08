import pdb

from tts_utilities.logger import create_logger

from tts_data_utils.invulnerable_data_manager.invulnerable_data_manager import InvulnerableDataManager
from tts_data_utils.invulnerable_data_manager.utilities import invulnerable, exec_invulnerable

from tts_data_utils.invulnerable_data_manager.batch import AllDataBatch, UntaggedBatch
from tts_dexter.core.data import DISPO_CHOICE
from tts_dexter.core.dispo import DISPO_FORMAT, SUGGESTED_DEFAULT_DISPO



logger = create_logger(__name__)

#================================================
# :: Constants
#------------------------------------------------
BATCH_ALL_NAME = '_dex_all_data'

class Dexter(InvulnerableDataManager):
    """
    The central management class for the Dexter automation framework.

    Inherits from InvulnerableDataManager to provide separate fault tolerance
    for each individual test.
    This class is responsible for orchestrating the workflow of loading data,
    initializing specific disposition logic (via Dispositioners), executing those
    dispositions, and finally stamping the results back onto the data containers.

    Attributes:
        DISPO_CHOICE (DISPO_CHOICE): The default strategy for selecting dispositions (e.g., ALL).
        DISPO_FORMAT (DISPO_FORMAT): The default format for outputting dispositions (e.g., HTML).
        DISPO_DEFAULT (Disposition): The default disposition to apply when no specific rule matches.
    """
    DISPO_CHOICE = DISPO_CHOICE.ALL
    DISPO_FORMAT = DISPO_FORMAT.HTML
    DISPO_DEFAULT = SUGGESTED_DEFAULT_DISPO

    def __init__(self):
        # Initialize default options
        self.dispo_choice = self.DISPO_CHOICE
        self.dispo_format = self.DISPO_FORMAT
        self._dispositioners = []
        super().__init__()

    def _impl_init_data(self, *args, **kwargs):
        """
        Implementation hook for initializing data containers.

        Ensures that a 'default_dispo' is provided in the keyword arguments
        before delegating to the parent class's data initialization logic.
        """
        if 'default_dispo' not in kwargs:
            kwargs['default_dispo'] = self.DISPO_DEFAULT

    def init_dispositioner(self, dispositioner_cls):
        """
        Instantiates and registers a new dispositioner.

        This method safely attempts to create an instance of the provided
        dispositioner class using `exec_invulnerable`. If successful, the
        instance is added to the internal list of active dispositioners.

        Args:
            dispositioner_cls (class): The class of the dispositioner to initialize.
                                       Must accept the Dexter instance as an argument.
        """
        new_dispositioner = exec_invulnerable(dispositioner_cls, self)
        if new_dispositioner is not None:
            self._dispositioners.append(new_dispositioner)
           
    def disposition_all(self):
        """
        Executes the disposition logic for all registered dispositioners.

        Iterates through the list of initialized dispositioners and calls their
        `do_dispositions` method to evaluate rules against the loaded data.
        """
        for dispositioner in self._dispositioners:
            dispositioner.do_dispositions()
    
    def stamp_all(self):
        """
        Applies the final dispositions to the data records.

        Iterates through all data containers managed by this Dexter instance and
        triggers their `stamp_all` method to format and attach the calculated
        dispositions (and severity statuses) to the individual data items.

        Stamps can be configured to show all disosition statuses, only the
        latest, only the first, or only the most severe.

        TO DO: Determine if we can remove this now that we've written stamp_all_to_outputs, which 
        added to enable a new strategy where we no longer edit inputs in place and instead
        make copies of them to be output. TBD whether some users will want to keep the old
        structure and others will take the new, but this might be retained for legacy reasons.
        """
        for container in self.all_input_data.data_map.values():
            container.stamp_all(self.dispo_choice, self.dispo_format)

    def stamp_all_to_outputs(self):
        """Copy-on-stamp variant of :meth:[stamp_all](cci:1://file:///Users/muszynsk/projects/tt_studio/dev/tts_core/tts_dexter/src/tts_dexter/core/dexter.py:82:4-94:69).

        For each input container/frame, this method:

        - creates a copy of the input data,
        - applies row-level stamping on the copy using the current
          ``dispo_choice`` and ``dispo_format``, and
        - registers the stamped copy in :attr:[all_output_data](cci:1://file:///Users/muszynsk/projects/tt_studio/dev/tts_core/tts_data_utils/src/tts_data_utils/invulnerable_data_manager/invulnerable_data_manager.py:95:4-98:36) under the
          same name.

        The original input containers/frames are left unmodified.
        """

        outputs = {}
        for name, container in self.all_input_data.data_map.items():
            # DataContainer has a custom _copy() that preserves history/metadata
            if hasattr(container, "_copy"):
                stamped = container._copy()
            else:
                # TtsDataFrame and other pandas-like types should implement copy()
                stamped = container.copy()

            stamped.stamp_all(self.dispo_choice, self.dispo_format)
            self.all_output_data.set_data_one(name, stamped)
            outputs[name] = stamped

        return outputs            