import csv
from pathlib import Path
import re
import pdb
from decimal import Decimal
import decimal

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

