"""Shared helpers for DataFrame-based Dexter test suites.

Provides :func:`make_lad_frame` which joins an EHA autodispositions CSV with
an actuals chanvals CSV into a single ``TtsDataFrame`` suitable for
:class:`~tts_dexter.dispositioners.eha.DfLadEhaDispositioner`.

Also provides :func:`rows_for` for concise per-channel assertion slicing.
"""
from pathlib import Path

import pandas as pd

from tts_data_utils.core.data_frame import TtsDataFrame

TEST_FILE_DIR = Path(__file__).parent.joinpath('test_files')


def make_lad_frame(rules_csv, actuals_csv, group_filter=None):
    """Build a merged TtsDataFrame from autodispositions rules + chanval actuals.

    Joins *rules_csv* (rows from the EHA autodispositions spreadsheet) to
    *actuals_csv* (raw chanvals) on ``Channel ID`` == ``channelId``, then
    fills the ``Actual Value`` column from the appropriate chanval column
    (``dn``, ``eu``, ``status``, or ``dnStr``) based on ``Data Type``.

    Parameters
    ----------
    rules_csv : Path or str
        Path to the autodispositions CSV (e.g. ``eha_autodispositions.csv``).
    actuals_csv : Path or str
        Path to the chanvals CSV (e.g. ``dn_chanvals_no_tolerance.csv``).
    group_filter : str or None
        If given, only rows where the ``Group`` column equals this value are
        kept from the rules CSV.

    Returns
    -------
    TtsDataFrame
        Merged frame ready to be registered on a Dexter instance and passed
        to :class:`~tts_dexter.dispositioners.eha.DfLadEhaDispositioner`.
    """
    rules = pd.read_csv(rules_csv, dtype=str, keep_default_na=False)
    actuals = pd.read_csv(actuals_csv)

    if group_filter is not None:
        rules = rules[rules['Group'] == group_filter].copy()

    merged = rules.merge(actuals, left_on='Channel ID', right_on='channelId', how='inner')

    def _resolve_actual(row):
        dtype = str(row['Data Type']).lower()
        if dtype == 'dn':
            return row.get('dn', None)
        if dtype == 'eu':
            return row.get('eu', None)
        if dtype == 'status':
            return row.get('status', None)
        if dtype == 'dnstr':
            return row.get('dnStr', None)
        return None

    merged['Actual Value'] = merged.apply(_resolve_actual, axis=1)
    return TtsDataFrame(merged, coerce=False, validate=False)


def make_evr_frame(evrs_csv):
    """Build a TtsDataFrame from a raw EVR chanvals CSV.

    Parameters
    ----------
    evrs_csv : Path or str
        Path to the EVR CSV (e.g. ``evrs.csv``).

    Returns
    -------
    TtsDataFrame
        Frame ready to be registered on a Dexter instance as ``'evr_frame'``
        and passed to
        :class:`~tts_dexter.dispositioners.evrs.DfBulkEvrDispositioner`.
    """
    data = pd.read_csv(evrs_csv, dtype=str, keep_default_na=False)
    return TtsDataFrame(data, coerce=False, validate=False)


def evr_rows_for(out_frame, names):
    """Return ``(name, message, disposition)`` tuples for EVRs with the given names.

    Parameters
    ----------
    out_frame : TtsDataFrame
        Stamped output frame from ``stamp_all_to_outputs()``.
    names : list of str
        EVR names to include, in the order they appear in the frame.

    Returns
    -------
    list of tuple
        Each tuple is ``(name, message, disposition)``.
    """
    sub = out_frame[out_frame['name'].isin(names)]
    return [
        (row['name'], row['message'], row['disposition'])
        for _, row in sub.iterrows()
    ]


def rows_for(out_frame, channel_prefix):
    """Return ``(Expected Value, Actual Value, disposition)`` tuples for matching rows.

    Filters *out_frame* to rows whose ``Channel ID`` contains *channel_prefix*
    as a literal substring (no regex), preserving row order.

    Parameters
    ----------
    out_frame : TtsDataFrame
        Stamped output frame from ``stamp_all_to_outputs()``.
    channel_prefix : str
        Substring to match against the ``Channel ID`` column.

    Returns
    -------
    list of tuple
        Each tuple is ``(expected_value, actual_value, disposition)``.
    """
    sub = out_frame[out_frame['Channel ID'].str.contains(channel_prefix, regex=False)]
    return [
        (row['Expected Value'], row['Actual Value'], row['disposition'])
        for _, row in sub.iterrows()
    ]
