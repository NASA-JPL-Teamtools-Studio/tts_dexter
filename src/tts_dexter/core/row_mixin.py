"""Shared row-level disposition behavior for Dexter-compatible data rows.

This mixin defines the minimal "Dexter row" contract used by dispositioners
and Dexter itself. Any row object that:

- exposes a mutable ``dispositions`` list,
- defines a ``default_dispo`` attribute (or sets it to None), and
- provides a ``DICT_STAMP_KEY`` attribute pointing at the target stamp column,

can inherit from :class:`DexterRowMixin` to gain ``new_dispo``,
``add_dispo``, ``choose_dispo``, ``choose_and_stamp``, and ``stamp``.

Current consumers include:

- ``tts_data_utils.core.data_item.DataItem`` (via integration to be
  added in later steps), and
- future ``TtsRowSeries`` implementations for ``TtsDataFrame`` rows.
"""

from tts_dexter.core.dispo import (
    Disposition,
    DISPO_FORMAT,
    get_dispo_joiner,
)
from tts_dexter.core.data import DISPO_CHOICE


class DexterRowMixin:
    """Mixin implementing the core Dexter disposition operations for a row.

    This is a direct extraction of the existing behavior on
    ``DataItem`` so that it can be shared with other row types
    (e.g., ``TtsRowSeries``) without duplicating logic.
    """

    # NOTE: The host class is expected to define:
    # - self.dispositions: list[Disposition]
    # - self.default_dispo: Disposition | None
    # - self.DICT_STAMP_KEY: str (name of the stamp column)

    def add_dispo(self, disposition: Disposition):
        """Append an existing :class:`Disposition` to this row's list.

        Parameters
        ----------
        disposition : Disposition
            Disposition for whatever has happened to this row.
        """
        self.dispositions.append(disposition)

    def new_dispo(self) -> Disposition:
        """Create, register, and return a new empty :class:`Disposition`.

        This mirrors the historical ``DataItem.new_dispo`` behavior.
        """
        new_dispo = Disposition()
        self.dispositions.append(new_dispo)
        return new_dispo

    def choose_dispo(self, dispo_choice: DISPO_CHOICE):
        """Select which disposition(s) to present for this row.

        Parameters
        ----------
        dispo_choice : DISPO_CHOICE
            How to roll up multiple dispositions. Currently supports
            FIRST, LAST, and ALL, matching existing ``DataItem``
            semantics. Other values will raise ``ValueError``.
        """
        all_dispositions = [_ for _ in self.dispositions if _.populated]
        if len(all_dispositions) == 0:
            if getattr(self, "default_dispo", None) is None:
                return
            return [self.default_dispo]

        if dispo_choice == DISPO_CHOICE.FIRST:
            return [all_dispositions[0]]
        elif dispo_choice == DISPO_CHOICE.LAST:
            return [all_dispositions[-1]]
        elif dispo_choice == DISPO_CHOICE.ALL:
            return all_dispositions
        else:
            raise ValueError(f"Unhandled dispo choice value: {dispo_choice}")

    def choose_and_stamp(self, dispo_choice: DISPO_CHOICE, dispo_format: DISPO_FORMAT):
        """Choose dispositions and stamp this row with a formatted value.

        This is the shared implementation of ``DataItem.choose_and_stamp``.
        It calls :meth:`choose_dispo`, formats the selected dispositions,
        joins them appropriately for the target format, and delegates to
        :meth:`stamp` to write the result onto the row.
        """
        dispos = self.choose_dispo(dispo_choice)
        if not dispos:
            return
        dispo_values = [_.format(dispo_format) for _ in dispos]
        if dispo_format == DISPO_FORMAT.EXCEL:
            # For Excel, this will be done in papertrail; keep as a list.
            dispo_full = dispo_values
        else:
            dispo_full = get_dispo_joiner(dispo_format).join(dispo_values)
        self.stamp(dispo_full)

    def stamp(self, dispo_value):
        """Write the disposition value into the host's source/stamp field.

        The host class is expected to implement the actual storage
        mechanism. For ``DataItem`` this means writing into
        ``self.source[self.DICT_STAMP_KEY]``. For frame-backed rows
        (e.g., ``TtsRowSeries``), this could write into the underlying
        DataFrame column indicated by ``DICT_STAMP_KEY``.
        """
        # Default implementation matches DataItem semantics. Host
        # classes relying on a different storage model can override
        # this method.
        self.source[self.DICT_STAMP_KEY] = dispo_value
