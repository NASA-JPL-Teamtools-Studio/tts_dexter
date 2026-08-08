# DataFrame Test Parity Plan

Goal: for every existing DataContainer-based Dexter test class, create a parallel
`TtsDataFrame`-based test class that exercises the same disposition logic via
`TtsRowSeries` / `DexterRowMixin` and `stamp_all_to_outputs`.

---

## Context: how the existing tests work

```
chanvals CSV ──────┐
                   ├─► Dante.derive_all() ──► ExpectedLadContainer (merged rows) ──► Dexter ──► stamped DataContainer
autodispositions   ┘
CSV
```

Each row in the final `ExpectedLadContainer` has:
- `Channel ID`, `Data Type`, `Condition`, `Tolerance`
- `Expected Value` (from autodispositions CSV)
- `Actual Value`  (from chanvals CSV, filled in by the Dante deriver)
- `Headline (True/False)`, `Disposition Message (True/False)`

`LadEhaDispositioner.dispo_from_csv` iterates those rows, calls `COMPARITORS[condition]`,
then calls `chanval.new_dispo().custom(headline, message)`.

For `BulkEvrDispositioner`, the EVR rows come directly from the EVR CSV; matching rules
come from `evr_autodispositions.csv`, and the dispositioner does name/regex matching
to find which EVR rows each rule applies to.

---

## Approach for DataFrame equivalents

Skip Dante entirely.  Instead, build the merged frame directly in the fixture:

```python
import pandas as pd
from tts_data_utils.core.data_frame import TtsDataFrame

rules = pd.read_csv('eha_autodispositions.csv')
actuals = pd.read_csv('dn_chanvals_no_tolerance.csv')

# Join on Channel ID
merged = rules.merge(actuals, left_on='Channel ID', right_on='channelId', how='inner')

# Fill Actual Value from the correct column based on Data Type
def resolve_actual(row):
    dtype = row['Data Type'].lower()
    if dtype == 'dn':    return row['dn']
    if dtype == 'eu':    return row['eu']
    if dtype == 'status': return row['status']
    if dtype == 'dnstr': return row['dnStr']

merged['Actual Value'] = merged.apply(resolve_actual, axis=1)

frame = MyLadFrame(merged, coerce=False, validate=False)
```

The `DfLadEhaDispositioner` (new class) will iterate `frame.iterrows()` and call the
same `COMPARITORS` logic from `eha.py`, but `row` is a `TtsRowSeries` so
`row.new_dispo().custom(...)` just works via `DexterRowMixin`.

Then `stamp_all_to_outputs()` copies the frame, calls `frame.stamp_all(...)`, and
writes the `disposition` column.

Assertions check `out_frame.loc[out_frame['Channel ID'] == 'GT-001', 'disposition'].tolist()`.

---

## Shared infrastructure to build first  (Step 0)

### 0a. `DfLadEhaDispositioner`

New class in `tts_dexter/dispositioners/eha_df.py` (or a second class in `eha.py`).
Reuses `COMPARITORS` from `eha.py`.  Only difference: operates on a `TtsDataFrame`
registered under a configurable data-key (default `'lad_frame'`).

```python
class DfLadEhaDispositioner(Dispositioner):
    DATA_KEY = 'lad_frame'

    @dispo_method(['lad_frame'])
    def dispo_from_frame(self, frame):
        for _, row in frame.iterrows():
            # same logic as LadEhaDispositioner.dispo_from_csv
            # row['Tolerance'], row['Condition'], row['Actual Value'], ...
            # row.new_dispo().custom(row['Headline (True)'], row['Disposition Message (True)'])
```

### 0b. `DfBulkEvrDispositioner`

New class in `tts_dexter/dispositioners/evrs_df.py` (or second class in `evrs.py`).
Reuses the `nameMatch` / `nameRegex` / `messageRegex` / `bothRegex` logic.
DataFrame version iterates `evr_frame.iterrows()` instead of
`evrs.eq('name', ...)` / `evrs.matches('name', ...)`.

### 0c. Shared fixture helper `make_lad_frame(rules_csv, actuals_csv, frame_class)`

A utility function (in `conftest.py` or a local helper) that:
1. Reads both CSVs
2. Merges on `channelId` == `Channel ID`
3. Fills `Actual Value` from the correct column
4. Returns an instance of `frame_class`

### 0d. `conftest.py` additions

Module-scoped `lad_frame` fixture (parametrised per test file) and a
`dex_from_frame` fixture that:
1. Calls `DfLadEhaDispositioner` on the frame
2. Returns `stamp_all_to_outputs()` output
3. Provides the output frame to each test via a fixture

---

## Per-suite plan

### Suite 1 — EHA DN No Tolerance
- **Existing file**: `test_eha_bulk_dispo_dn_no_tol.py`  →  `TestBulkEhaDispoDnNoTolerance`
- **New file**: `test_eha_bulk_dispo_dn_no_tol_df.py`  →  `TestBulkEhaDispoDnNoToleranceDf`
- **Chanvals CSV**: `dn_chanvals_no_tolerance.csv`
- **Rules CSV**: `eha_autodispositions.csv` (filter `Group == 'DN No Tolerance'`)
- **Tests** (12 methods → 12 DF equivalents):
  `test_gt`, `test_lt`, `test_gte`, `test_lte`, `test_eq`, `test_ne`,
  `test_range_neither_inclusive`, `test_range_upper_only_exclusive`,
  `test_range_lower_only_exclusive`, `test_range_both_inclusive`,
  `test_range_same_value_inclusive`, `test_range_same_non_value_inclusive`
- **Assertion pattern** (translating from container iteration):
  ```python
  # Old:
  [(e['Expected Value'], e['Actual Value'], e['disposition'])
   for e in container.contains('Channel ID', 'GT-001')]
  # New:
  sub = out_frame[out_frame['Channel ID'].str.startswith('GT-001')]
  list(zip(sub['Expected Value'], sub['Actual Value'], sub['disposition']))
  ```
  Note: existing tests use `GT-001`, `LT-001`, etc. (3-digit suffix).
  The DF tests will use the same Channel IDs from the merged frame.

### Suite 2 — EHA DN With Tolerance
- **Existing file**: `test_eha_bulk_dispo_dn_with_tol.py`
- **New file**: `test_eha_bulk_dispo_dn_with_tol_df.py`  →  `TestBulkEhaDispoDnWithToleranceDf`
- **Chanvals CSV**: `dn_chanvals_with_tolerance.csv`
- **Rules CSV**: `eha_autodispositions.csv` (filter `Group == 'DN With Tolerance'`)
- **Tests** (11 methods → 11 DF equivalents):
  `test_gt`, `test_lt`, `test_gte`, `test_lte`, `test_eq`, `test_ne`,
  `test_range_neither_none_clusive`, `test_range_upper_only_inclusive`,
  `test_range_lower_only_inclusive`, `test_range_both_inclusive`,
  `test_range_same_value_inclusive`, `test_range_same_value_non_inclusive`

### Suite 3 — EHA EU No Tolerance
- **Existing file**: `test_eha_bulk_dispo_eu_no_tol.py`
- **New file**: `test_eha_bulk_dispo_eu_no_tol_df.py`  →  `TestBulkEhaDispoEuNoToleranceDf`
- **Chanvals CSV**: `eu_chanvals_no_tolerance.csv`
- **Rules CSV**: `eha_autodispositions.csv` (filter `Group == 'EU No Tolerance'`)
- **Tests** (12 methods → 12 DF equivalents): same operator list as Suite 1

### Suite 4 — EHA EU With Tolerance
- **Existing file**: `test_eha_bulk_dispo_eu_with_tol.py`
- **New file**: `test_eha_bulk_dispo_eu_with_tol_df.py`  →  `TestBulkEhaDispoEuWithToleranceDf`
- **Chanvals CSV**: `eu_chanvals_with_tolerance.csv`
- **Rules CSV**: `eha_autodispositions.csv` (filter `Group == 'EU With Tolerance'`)
- **Tests** (12 methods → 12 DF equivalents)

### Suite 5 — EHA Status + DN String
- **Existing file**: `test_eha_bulk_dispo_stats_and_dn_str.py`
  →  `TestBulkEhaDispoStatus` (4 tests) + `TestBulkEhaDispoDnString` (4 tests)
- **New file**: `test_eha_bulk_dispo_stats_and_dn_str_df.py`
  →  `TestBulkEhaDispoStatusDf` + `TestBulkEhaDispoDnStringDf`
- **Chanvals CSV**: `status_and_dnString_chanvals.csv`
- **Rules CSV**: `eha_autodispositions.csv` (filter `Group` for STATUS/DNSTR rows)
- **Tests** (8 total → 8 DF equivalents):
  For each class: `test_eq`, `test_ne`, `test_isin`, `test_notin`

### Suite 6 — EVR Bulk Dispo
- **Existing file**: `test_evr_bulk_dispo.py`  →  `TestBulkEvrDispo`
- **New file**: `test_evr_bulk_dispo_df.py`  →  `TestBulkEvrDispoDf`
- **Data CSV**: `evrs.csv` → loaded into `EvrFrame(TtsDataFrame)`
- **Rules CSV**: `evr_autodispositions.csv` → read in `DfBulkEvrDispositioner`
- **Key challenge**: The EVR dispositioner uses `evrs.eq()` / `evrs.matches()` which
  are DataContainer methods.  The DF version must replace these with pandas boolean
  indexing and `re.fullmatch`.  Because the dispositioner iterates RULES (not rows),
  each matching row in the frame gets `row.new_dispo().custom(...)` called on it.
  Rows with no matching rule get a "No Autodisposition" dispo from a fallback
  `disposition_all` pass.
- **Tests** (4 methods → 4 DF equivalents):
  `test_evr_exact_name_match`, `test_evr_regex_name_match`,
  `test_evr_regex_message_match`, `test_evr_regex_message_and_regex_name_match`
- **No-autodispo handling**: In the container world, `DataItem.__init__` seeds a
  "No Autodisposition" dispo by default.  In the DF world, we need to seed it
  ourselves — either in the dispositioner as a post-pass, or by initialising the
  `disposition` column to the no-autodispo HTML before `stamp_all_to_outputs`.

### Suite 7 — Stamp and Format
- **Existing file**: `test_stamp_and_format.py`  →  `TestDispoFormatting`
- **New file**: `test_stamp_and_format_df.py`  →  `TestDispoFormattingDf`
- **Tests** (3 methods → 3 DF equivalents, 1 xfail):
  `test_format_html`, `test_format_text`, `test_format_excel` (xfail)
- **Key point**: This suite tests `DISPO_FORMAT.HTML` / `TEXT` / `EXCEL` output.
  The DF `stamp_all` already accepts `dispo_format`.  We just need to verify that
  the `disposition` column gets the correct format string.

---

## Open questions / decisions needed

1. **Where does `DfLadEhaDispositioner` live?**
   - Option A: new file `dispositioners/eha_df.py`
   - Option B: second class at the bottom of `dispositioners/eha.py`
   - Recommendation: Option B to keep related logic together.

2. **No-autodispo seeding for EVR DF tests**
   - The DataContainer seeds "No Autodisposition" automatically per `DataItem`.
   - For the DF, we need to decide: does the `DfBulkEvrDispositioner` do a
     post-pass adding a no-autodispo dispo to any row that has none, OR do we
     pre-seed the `disposition` column?
   - Recommendation: post-pass in the dispositioner — after rule matching, iterate
     all rows; any row with `len(row.dispositions) == 0` gets a no-autodispo dispo.

3. **Channel ID filtering in assertions**
   - Container tests use `container.contains('Channel ID', 'GT-001')`.
   - DF tests use `out_frame[out_frame['Channel ID'] == 'GT-001']` (exact) or
     `out_frame[out_frame['Channel ID'].str.contains('GT-001')]` (partial).
   - The autodispositions CSV uses IDs like `GT-0010`, `GT-0011`, etc.
     The existing tests (which filter for `GT-001`) rely on `contains()` doing
     a substring match.  DF tests should use `.str.startswith('GT-001')`.

4. **Test file marking**
   - All new DF test classes should be marked `@pytest.mark.unreviewed_ai_generated_test`
     (existing convention, see `test_dex.py`).

---

## Suggested implementation order

| Step | Deliverable | Notes |
|------|-------------|-------|
| 0a | `DfLadEhaDispositioner` in `eha.py` | Reuses COMPARITORS |
| 0b | `DfBulkEvrDispositioner` in `evrs.py` | Includes no-autodispo post-pass |
| 0c | `make_lad_frame` helper in test `conftest.py` | Shared CSV-merge utility |
| 1 | `test_eha_bulk_dispo_dn_no_tol_df.py` | Simplest case, no tolerance |
| 2 | `test_eha_bulk_dispo_dn_with_tol_df.py` | Adds tolerance logic |
| 3 | `test_eha_bulk_dispo_eu_no_tol_df.py` | Float values |
| 4 | `test_eha_bulk_dispo_eu_with_tol_df.py` | Float + tolerance |
| 5 | `test_eha_bulk_dispo_stats_and_dn_str_df.py` | String types |
| 6 | `test_evr_bulk_dispo_df.py` | EVR regex logic |
| 7 | `test_stamp_and_format_df.py` | Format variants |

Run `pytest -v` after each step to confirm no regressions.
