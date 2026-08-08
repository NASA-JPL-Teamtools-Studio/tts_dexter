import csv
from pathlib import Path
import re
import pdb
from decimal import Decimal
import decimal

import pandas as pd

from tts_data_utils.core.data_frame import TtsDataFrame
from tts_dexter.core.dispo import Dispositioner, dispo_method

ALLOWABLE_TYPES_BY_CONDITION = {
    'gt':    ['dn', 'eu'                   ],
    'lt':    ['dn', 'eu'                   ],
    'gte':   ['dn', 'eu'                   ],
    'lte':   ['dn', 'eu'                   ],
    'eq':    ['dn', 'eu', 'status', 'dnStr'],
    'ne':    ['dn', 'eu', 'status', 'dnStr'],
    'range': ['dn', 'eu'                   ],
    'isin':  [            'status', 'dnStr'],
    'notin': [            'status', 'dnStr']
    }

COMPARITORS = {
    'gt':    lambda x, y, t: x + t > y or x - t > y, #the or captures where x is pos or neg
    'lt':    lambda x, y, t: x + t < y or x - t < y, #the or captures where x is pos or neg
    'gte':   lambda x, y, t: x + t >= y or x - t >= y, #the or captures where x is pos or neg
    'lte':   lambda x, y, t: x + t <= y or x - t <= y, #the or captures where x is pos or neg
    'eq':    lambda x, y, t: x - t <= y and x + t >= y,
    'str_eq':    lambda x, y: x == y and x == y,
    'str_ne':    lambda x, y: x == y and x == y,
    'ne':    lambda x, y, t: not (x - t <= y and x + t >= y),
    'range': lambda x, y, t, bounds='[]': (
        ((x + t > y[0] or x - t > y[0]) if bounds[0] == '(' else (x + t >= y[0] or x - t >= y[0])) and
        ((x + t < y[1] or x - t < y[1]) if bounds[1] == ')' else (x + t <= y[1] or x - t <= y[1]))
    ),
    'isin':  lambda x, y, t: x in y,
    'notin': lambda x, y, t: x not in y,
}

class LadEhaDispositioner(Dispositioner):
    """
    Dispositioner for Latest Available Data (LAD) for EHA.

    This class loads disposition rules from a CSV file and evaluates them against
    EHA channel values. It supports various comparison operations including
    numerical thresholds (with tolerance) and status matching.

    It does not check all values like alarms, but only the latest state.
    """
    HANDLER_MAP = {}

    @dispo_method(['Expected LAD'])
    def dispo_from_csv(self, chanvals):
        for chanval in chanvals:

            if chanval['Tolerance'] == '' or chanval['Tolerance'] is None:
                tolerance = Decimal(0)
            else:
                tolerance = Decimal(str(chanval['Tolerance']))

            if chanval['Condition'] not in ALLOWABLE_TYPES_BY_CONDITION.keys():
                raise Exception(f"Condition type \"{chanval['Condition']}\" not understood.")
            if chanval['Data Type'] not in  ALLOWABLE_TYPES_BY_CONDITION[chanval['Condition']]:
                raise Exception(f"Data type \"{chanval['Condition']}\" not allowed for condition \"{chanval['Condition']}\".")

            if chanval['Actual Value'] == 'Not Present':
                chanval.new_dispo().custom('Ops Check', 'Chanval Not Present')
                continue

            #TO DO: Improve this type handing
            try:
                actual_value = Decimal(str(chanval['Actual Value']))
            except decimal.InvalidOperation:
                actual_value = chanval['Actual Value']

            try:
                expected_value = Decimal(chanval['Expected Value'])
            except decimal.InvalidOperation:
                expected_value = chanval['Expected Value']

            if chanval['Condition'] == 'range':
                bounds = expected_value[0] + expected_value[-1]
                expected_value = [Decimal(x) for x in expected_value[1:-1].split(',')]
                comparison = COMPARITORS[chanval['Condition']](actual_value, expected_value, tolerance, bounds)
            elif chanval['Condition'] == 'eq' and chanval['Data Type'].lower() in ['status', 'dnstr']:
                comparison = COMPARITORS['str_eq'](actual_value, expected_value)
            elif chanval['Condition'] == 'ne' and chanval['Data Type'].lower() in ['status', 'dnstr']:
                comparison = COMPARITORS['str_ne'](actual_value, expected_value)
            else:
                comparison = COMPARITORS[chanval['Condition']](actual_value, expected_value, tolerance)

            if comparison:
                chanval.new_dispo().custom(chanval['Headline (True)'], chanval['Disposition Message (True)'])
            else:
                chanval.new_dispo().custom(chanval['Headline (False)'], chanval['Disposition Message (False)'])


class DfLadEhaDispositioner(Dispositioner):
    """
    DataFrame-aware dispositioner for Latest Available Data (LAD) EHA.

    Operates on a TtsDataFrame registered under the ``'lad_frame'`` data key.
    Each row must already contain merged autodisposition rules and actual chanval
    data (see :func:`make_lad_frame` in the test helpers).

    Applies the same comparison logic as :class:`LadEhaDispositioner` but
    iterates via ``TtsRowSeries`` rows so ``new_dispo()`` writes back to the
    parent frame through the standard ``DexterRowMixin`` contract.
    """
    HANDLER_MAP = {}

    @dispo_method(['lad_frame'])
    def dispo_from_frame(self, frame):
        for _, row in frame.iterrows():
            tol_raw = row['Tolerance']
            if pd.isna(tol_raw) or tol_raw == '':
                tolerance = Decimal(0)
            else:
                tolerance = Decimal(str(tol_raw))

            condition = row['Condition']
            data_type = row['Data Type']

            if condition not in ALLOWABLE_TYPES_BY_CONDITION:
                raise Exception(f"Condition type \"{condition}\" not understood.")
            if data_type not in ALLOWABLE_TYPES_BY_CONDITION[condition]:
                raise Exception(f"Data type \"{data_type}\" not allowed for condition \"{condition}\".")

            actual_raw = row['Actual Value']
            if actual_raw == 'Not Present':
                row.new_dispo().custom('Ops Check', 'Chanval Not Present')
                continue

            try:
                actual_value = Decimal(str(actual_raw))
            except decimal.InvalidOperation:
                actual_value = actual_raw

            expected_raw = row['Expected Value']
            try:
                expected_value = Decimal(str(expected_raw))
            except decimal.InvalidOperation:
                expected_value = expected_raw

            if condition == 'range':
                bounds = expected_value[0] + expected_value[-1]
                expected_value = [Decimal(x) for x in expected_value[1:-1].split(',')]
                comparison = COMPARITORS[condition](actual_value, expected_value, tolerance, bounds)
            elif condition == 'eq' and data_type.lower() in ['status', 'dnstr']:
                comparison = COMPARITORS['str_eq'](actual_value, expected_value)
            elif condition == 'ne' and data_type.lower() in ['status', 'dnstr']:
                comparison = COMPARITORS['str_ne'](actual_value, expected_value)
            else:
                comparison = COMPARITORS[condition](actual_value, expected_value, tolerance)

            if comparison:
                row.new_dispo().custom(row['Headline (True)'], row['Disposition Message (True)'])
            else:
                row.new_dispo().custom(row['Headline (False)'], row['Disposition Message (False)'])


class DfCsvLadEhaDispositioner(DfLadEhaDispositioner):
    """
    Extension of DfLadEhaDispositioner that knows how to build its own merged
    frame from a rules CSV and a raw actuals frame.

    Subclasses may override ``NAME_COL``, ``EU_COL``, and ``DN_COL`` to match
    the column names used by their telemetry query layer.

    Usage::

        frame = MyDispositioner.build_frame(snapshot_csv, lad_chanvals)
        dex.all_input_data.set_data_one('lad_frame', frame)
    """
    NAME_COL = 'name'
    EU_COL   = 'value'
    DN_COL   = 'raw_value'

    @classmethod
    def build_frame(cls, snapshot_csv, actuals_frame):
        """Merge a rules CSV with actual chanvals into a disposition-ready TtsDataFrame.

        Parameters
        ----------
        snapshot_csv : str or Path
            Procedure step CSV defining expected-value rules.  Must contain
            columns ``Channel ID``, ``Data Type``, ``Condition``,
            ``Expected Value``, ``Tolerance``, ``Headline (True)``,
            ``Disposition Message (True)``, ``Headline (False)``,
            ``Disposition Message (False)``.
        actuals_frame : DataFrame-like
            Telemetry frame whose column names match ``cls.NAME_COL``,
            ``cls.EU_COL``, and ``cls.DN_COL``.  One row per channel
            (LAD query result).

        Returns
        -------
        TtsDataFrame
            Merged frame ready to be registered on a Dexter instance as
            ``'lad_frame'`` and passed to this dispositioner.
        """
        rules = pd.read_csv(snapshot_csv, dtype=str, keep_default_na=False)
        actuals = pd.DataFrame({
            '_name': list(actuals_frame[cls.NAME_COL]),
            '_eu':   list(actuals_frame[cls.EU_COL]),
            '_dn':   list(actuals_frame[cls.DN_COL]),
        })
        merged = rules.merge(actuals, left_on='Channel ID', right_on='_name', how='left')

        def _resolve(row):
            if pd.isna(row.get('_name')):
                return 'Not Present'
            dtype = str(row.get('Data Type', '')).lower()
            v = row.get('_dn') if dtype == 'dn' else row.get('_eu')
            if v is None or (not isinstance(v, str) and pd.isna(v)):
                return 'Not Present'
            return v

        merged['Actual Value'] = merged.apply(_resolve, axis=1)
        return TtsDataFrame(merged, coerce=False, validate=False)

