import csv
from pathlib import Path
import re
import pdb

from tts_dexter.core.dispo import Dispositioner, Disposition, DISPO_SEVERITY, dispo_method

class BulkEvrDispositioner(Dispositioner):
    """
    A dispositioner that applies bulk disposition rules to Event Records (EVRs) defined in a CSV file.

    This class provides a mechanism to load rules from an external CSV source and evaluate them against
    a collection of EVRs. It supports various matching strategies including exact string matching and
    regular expressions for both EVR names and messages.

    Attributes:
        HANDLER_MAP (dict): A mapping for handlers (currently unused in this base implementation).
                            Allows the developer to map specific cases to other methods within this
                            class within their project adaptation layer in cases where these
                            out-of-the-box dispositions are not enough.
        CSV_FILEPATH (Path or None): The file path to the CSV containing the disposition rules. 
                                     Subclasses must define this path.
    """
    HANDLER_MAP = {}
    CSV_FILEPATH = None

    @dispo_method(['evrs'])
    def dispo_from_csv(self, evrs):
        """
        Reads rules from the configured CSV file and applies matching dispositions to the provided EVRs.

        The method iterates through each row in the CSV, interprets the rule based on the 'Condition' column,
        and applies the corresponding 'Headline' and 'Disposition Message' to matching records in the `evrs` container.

        Supported 'Condition' types:
        - 'nameMatch': Requires an exact match of the EVR 'name'.
        - 'nameRegex': Matches the EVR 'name' against a regular expression.
        - 'messageRegex': Requires an exact match of the EVR 'name', and validates the 'message' against a regex.
        - 'bothRegex': Validates both the EVR 'name' and 'message' against regular expressions.

        Args:
            evrs (DataContainer): A container of EVR data objects to be processed.

        Raises:
            Exception: If a rule in the CSV specifies a 'Condition' that is not recognized.
        """
        with open(self.CSV_FILEPATH, mode='r', newline='', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            # Convert the CSV data into a list of dictionaries
            ruledefs = list(reader)
        
        for ruledef in ruledefs:
            if ruledef['Condition'] == 'nameMatch':
                #Name is strict match, message can be anything
                for evr in evrs.eq('name', ruledef['Name']):
                    evr.new_dispo().custom(ruledef['Headline'], ruledef['Disposition Message'])
            elif ruledef['Condition'] == 'nameRegex':
                #Name is regex match, message can be anything
                for evr in evrs.matches('name', ruledef['Name']):
                    evr.new_dispo().custom(ruledef['Headline'], ruledef['Disposition Message'])
            elif ruledef['Condition'] == 'messageRegex':
                #Name must strictly match, but message is only regex match
                for evr in evrs.eq('name', ruledef['Name']):
                    if re.fullmatch(ruledef['Message Regex'], evr['message']):
                        evr.new_dispo().custom(ruledef['Headline'], ruledef['Disposition Message'])
            elif ruledef['Condition'] == 'bothRegex':
                #Name AND message are regex match
                for evr in evrs.matches('name', ruledef['Name']):
                    if re.match(ruledef['Message Regex'], evr['message']):
                        evr.new_dispo().custom(ruledef['Headline'], ruledef['Disposition Message'])                
            else:
                raise Exception(f"Condition \"{ruledef['Condition']}\" is not understood.")


class DfBulkEvrDispositioner(Dispositioner):
    """
    DataFrame-aware dispositioner for EVRs.

    Operates on a TtsDataFrame registered under the ``'evr_frame'`` data key.
    Reads rules from :attr:`CSV_FILEPATH` and applies matching dispositions by
    iterating all rows and checking each rule inline.  This avoids the
    parent-frame tracking issue that would arise from filtering the frame before
    iterating (rows from a filtered sub-frame point to the sub-frame, not the
    original).

    Supports the same ``Condition`` types as :class:`BulkEvrDispositioner`:
    ``nameMatch``, ``nameRegex``, ``messageRegex``, and ``bothRegex``.
    """
    HANDLER_MAP = {}
    CSV_FILEPATH = None

    @dispo_method(['evr_frame'])
    def dispo_from_frame(self, frame):
        with open(self.CSV_FILEPATH, mode='r', newline='', encoding='utf-8-sig') as f:
            ruledefs = list(csv.DictReader(f))

        for _, row in frame.iterrows():
            for ruledef in ruledefs:
                condition = ruledef['Condition']
                if condition == 'nameMatch':
                    if row['name'] == ruledef['Name']:
                        row.new_dispo().custom(ruledef['Headline'], ruledef['Disposition Message'])
                elif condition == 'nameRegex':
                    if re.fullmatch(ruledef['Name'], row['name']):
                        row.new_dispo().custom(ruledef['Headline'], ruledef['Disposition Message'])
                elif condition == 'messageRegex':
                    if row['name'] == ruledef['Name'] and re.fullmatch(ruledef['Message Regex'], row['message']):
                        row.new_dispo().custom(ruledef['Headline'], ruledef['Disposition Message'])
                elif condition == 'bothRegex':
                    if re.match(ruledef['Name'], row['name']) and re.match(ruledef['Message Regex'], row['message']):
                        row.new_dispo().custom(ruledef['Headline'], ruledef['Disposition Message'])
                else:
                    raise Exception(f"Condition \"{condition}\" is not understood.")

            if len(row.dispositions) == 0:
                row.add_dispo(
                    Disposition.from_definition(
                        'No Autodisposition', 'Manual Disposition Needed', DISPO_SEVERITY.UNKNOWN
                    )
                )