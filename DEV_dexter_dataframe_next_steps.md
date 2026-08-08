---
description: Next steps after implementing stamp_all_to_outputs and TtsRowSeries dispositions
---

# Dexter DataFrame Migration – Next Steps

This note builds on the main plan in `DEV_dexter_dataframe_migration.md`. It captures what to do next **after** implementing:

- `Dexter.stamp_all_to_outputs` (copy-on-stamp API)
- `TtsRowSeries` + `TtsDataFrame` dispositions (`_row_dispositions`, `DexterRowMixin` wiring)
- Initial tests for both containers and DataFrames

Use this as a checklist when you re-enable auto-editing.

---

## 1. Clean up and harden the new Dexter API

- **Fix the failing test in `test_dex.py`:**
  - Current failure: `AllDataBatch` has no `get_inventory()` method.
  - Action: in `test_dex_stamp_to_outputs`, replace:
    - `assert dex_basic_dispositionable.all_output_data.get_inventory()`
  - With a simpler check that does not rely on a non-existent API, for example:
    - `assert dex_basic_dispositionable.all_output_data.data_map` or
    - `assert dex_basic_dispositionable.get_output_data("test_data")`.

- **Double-check `stamp_all_to_outputs` behavior:**
  - Confirm `DataContainer` has `_copy()` and that it preserves history/metadata.
  - Confirm `TtsDataFrame` has `.copy()` and that it respects our `_metadata` list.
  - Optional: add a short docstring note in `Dexter.stamp_all` indicating that
    `stamp_all_to_outputs` is the preferred API for new code, while `stamp_all`
    is retained for legacy callers.

- **Possible small refactor (optional for now):**
  - Extract the copy logic into a small helper on `InvulnerableDataManager` or
    `Dexter`, e.g. `_copy_for_stamping(obj)` that encapsulates the `_copy` vs
    `copy()` decision. This is purely for clarity and testability.

---

## 2. Strengthen DataFrame-side tests and behavior

We already added tests in `test_data_frame.py` that:

- Validate `lad_value` returns a scalar.
- Validate that `TtsRowSeries` + `DexterRowMixin` can:
  - `new_dispo()` + `expected("OK")`
  - `choose_and_stamp(DISPO_CHOICE.ALL, DISPO_FORMAT.HTML)`
  - Populate a `disposition` column on the frame.
- Validate that `_row_dispositions` are pruned on filter (using index-based
  pruning in `TtsDataFrame.__finalize__`).

**Follow-ups to consider:**

- Add one more test that exercises `.iloc` and `.xs` row access explicitly:
  - Use `.iloc[0]` and ensure `_frame` is attached and dispositions work.
  - Use `.xs(..., axis=0)` and verify the same.
- Add a test that sorts by time and ensures `_row_dispositions` follow the
  surviving rows but do not cause any errors.

---

## 3. Explore using TtsDataFrame directly in Dexter tests (future step)

Right now, all Dexter tests in `src/tts_dexter/test` use `DataContainer` /
`DataItem`:

- `DataItem_Test`
- `DataContainer_Test`

Once the new APIs are stable, we can add **parallel tests** that:

- Build a `MockFrame` (from `test_data_frame.py`) instead of a container.
- Feed that into a small Dexter-like flow (possibly via a thin adapter):
  - Either by wrapping the frame in a temporary `DataContainer` that exposes
    rows as `TtsRowSeries`, or
  - By teaching Dexter to accept frames directly in `init_data` in a new test
    fixture.
- Run the same `_Dispositioner` logic and assert that `disposition` columns
  are stamped as expected on the frame.

This is aligned with Step 5 of the main migration doc (adapters between
containers and frames) but can be introduced gradually and guarded by tests.

---

## 4. Future work items (captured from the main plan)

When ready to move beyond copy-on-stamp and initial frame support:

1. **Adapters container↔frame** (Step 5 in the main doc):
   - Implement `container_to_df(container, frame_cls=TtsDataFrame)`.
   - Implement `df_to_container(df, container_cls)`.
   - Start using these in one or two mission-specific flows.

2. **Mission-specific Dexter façades (multi-LAD)** (Step 6):
   - For each procedure (e.g., OCO-2 realtime), create a small Dexter subclass
     that wires:
     - The relevant EHA/Expected LAD data (containers or frames).
     - The appropriate dispositioner (possibly subclassed per procedure).

3. **Deprecation path for `Dexter.stamp_all`:**
   - Once enough callers have migrated to `stamp_all_to_outputs`, consider:
     - Adding a deprecation warning in `stamp_all`.
     - Updating documentation to steer new code toward the copy-on-stamp API.

This file is intentionally high-level so that, when you re-enable editing, we
can apply these changes directly without revisiting the entire design.
