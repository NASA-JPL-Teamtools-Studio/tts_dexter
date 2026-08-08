---
description: Dexter migration from DataContainer to TtsDataFrame
---
 
# Dexter DataFrame Migration Plan
 
This document describes a staged plan to:
 
- Evolve Dexter away from `DataContainer` / `DataItem` as the **only** data model.
- Introduce `TtsDataFrame`/`TtsRowSeries` as a first-class target for Dexter.
- Avoid duplicating every construct in both container and DataFrame form.
- Stop mutating input data in-place and start producing explicit output objects.
- Support multiple Expected LAD sets per procedure (e.g., OCO-2) in a clean way.
 
The goal is to make this migration incremental and safe. We do **not** need to do everything in one PR.
 
---
 
## High-Level Strategy
 
1. **Define a minimal "Dexter row" contract** that is shared between `DataItem` and `TtsRowSeries`.
2. **Extract Dexter-specific behavior** out of generic data-utils classes into small, explicit mixins.
3. **Teach `TtsRowSeries` to implement the Dexter row contract**, storing dispositions on the frame.
4. **Add a copy-on-stamp output path to Dexter** (use `all_output_data` instead of mutating inputs).
5. **Introduce adapters between `DataContainer` and `TtsDataFrame`** for gradual migration.
6. **Create procedure-specific Dexter entrypoints** for multi-LAD Expected LAD use cases.
 
Each step can land independently as long as we respect backward compatibility at the public API boundary.
 
---
 
## Step 1 – Define the Dexter Row Contract
 
**Goal:** Specify the minimum API that any "row" must support for Dexter/dispositioners to work.
 
From current code, Dexter and the stock dispositioners only rely on a small subset of `DataItem`:
 
- Dict-like access:
  - `row['field']` – already satisfied by `DataItem` and `TtsRowSeries`.
- Disposition lifecycle:
  - `row.dispositions` → list of `Disposition` objects.
  - `row.new_dispo()` → create a new `Disposition`, append, and return it.
  - `row.add_dispo(disposition)` → append an existing `Disposition`.
  - `row.choose_dispo(dispo_choice)` → select which dispositions to present.
  - `row.choose_and_stamp(dispo_choice, dispo_format)` → format and stamp the row.
  - `row.stamp(value)` → write a disposition string/list into a well-known field.
 
**Action items:**
 
- Define a `DexterRowMixin` that implements the methods above, parametrized only by:
  - access to a `dispositions` list,
  - knowledge of where to stamp (column name / DICT_STAMP_KEY), and
  - access to `DISPO_CHOICE`, `DISPO_FORMAT`, and `get_dispo_joiner`.
 
This mixin should live in a Dexter-specific module (e.g., `tts_dexter.core.row_mixin`) to avoid polluting generic data-utils.
 
---
 
## Step 2 – Move Dexter Row Logic into the Mixin (while keeping DataItem working)
 
**Goal:** Stop baking Dexter behavior directly into `DataItem`, but keep behavior unchanged for existing code.
 
**Concrete changes:**
 
- Implement `DexterRowMixin` with methods:
  - `add_dispo`, `new_dispo`, `choose_dispo`, `choose_and_stamp`, `stamp`.
- Refactor `DataItem` so that it:
  - Inherits from `DexterRowMixin`, or
  - Composes it (e.g., delegates to functions defined in the mixin module).
- Ensure `DataItem` continues to initialize `self.dispositions` and `self.default_dispo` as today.
 
**Success criteria:**
 
- All existing Dexter tests continue to pass.
- No change to public behavior of `DataItem` and `DataContainer`.
 
At this point, we have isolated the Dexter row mechanics into a reusable component.
 
---
 
## Step 3 – Add Dexter Row Behavior to `TtsRowSeries`
 
**Goal:** Make `TtsRowSeries` satisfy the same Dexter row contract as `DataItem`, so dispositioners can run on `TtsDataFrame`.
 
### 3.1 – Where to store dispositions
 
We cannot rely on storing persistent state on the row Series itself; rows are often views, copied, or re-created.
 
Instead:
 
- Add a private attribute to `TtsDataFrame`:
  - `_row_dispositions: dict[row_key, list[Disposition]]`.
- Optionally, support a frame-level default disposition, if needed.
 
Each `TtsRowSeries` needs to know:
 
- Its parent frame: `row._parent`.
- Its key: `row._row_key` (typically the index value).
 
With that, the mixin can implement:
 
- `dispositions` by looking up `self._parent._row_dispositions[self._row_key]`.
- `stamp` by writing into `self[...]` (e.g., `self['disposition'] = value`).
 
### 3.2 – Wiring `TtsRowSeries` to the parent frame
 
Update `TtsDataFrame` so that whenever we create a row Series, we attach parent and key:
 
- In `iterrows`:
  - For each `(idx, row)` yielded, set:
    - `row.__class__ = self.ROW_SERIES_CLASS`.
    - `row._parent = self`.
    - `row._row_key = idx`.
- In `loc` / `xs`:
  - When returning a row (Series), do the same.
 
Ensure `TtsRowSeries` either inherits from `DexterRowMixin` or uses its functions.
 
### 3.3 – Behavior for frames without a disposition column
 
Decide on one of these patterns:
 
- Require a disposition column name (e.g., `'disposition'`) and document it.
- Or let `TtsDataFrame` subclasses specify `DICT_STAMP_KEY` (defaulting to `'disposition'`).
 
**Success criteria:**
 
- A simple test case where we:
  - Build a `TtsDataFrame` with label/time/value columns.
  - Iterate rows, call `row.new_dispo().custom(...)`, then `row.choose_and_stamp(...)`.
  - Check that a disposition column is populated as expected.
 
Now Dexter-style dispositioners can operate on frames as easily as they do on containers.
 
---
 
## Step 4 – Copy-on-Stamp Outputs in Dexter
 
**Goal:** Stop mutating input data in place when stamping dispositions; instead, produce explicit “output” data.
 
The `InvulnerableDataManager` already has:
 
- `_all_input_data` (an `AllDataBatch`) and
- `_all_output_data` (also an `AllDataBatch`).
 
Currently, `Dexter.stamp_all()` calls `DataContainer.stamp_all()`, which mutates the input containers.
 
**Proposed extension:**
 
- Add a new method on `Dexter`, e.g.:
 
  - `stamp_all_to_outputs(self, dispo_choice, dispo_format) -> dict[str, Any]`
 
  Behavior:
 
  - For each entry in `self.all_input_data.data_map`:
    - If it is a `DataContainer`: use `container._copy()` to make a copy.
    - If it is a `TtsDataFrame`: use `frame.copy()`.
    - Call `stamp_all` or equivalent row logic on the copy.
    - Store the copy in `self.all_output_data.set_data_one(name, copy)`.
  - Return a `{name: copy}` mapping for convenience.
 
- Keep the existing `stamp_all()` semantics unchanged for backward compatibility.
 
**Success criteria:**
 
- Existing callers that use `stamp_all()` see no change.
- New code can call `stamp_all_to_outputs()` and then operate only on the copies, leaving inputs pristine.
 
This is also the natural hook point for DataFrame-based users: call Dexter, then immediately convert output containers/frames into whatever final format you need.
 
---
 
## Step 5 – Adapters Between `DataContainer` and `TtsDataFrame`
 
**Goal:** Allow gradual migration from containers to frames without duplicating data models for every mission.
 
**Helpers to add (location flexible; could live in data-utils or in a project-specific layer):**
 
- `container_to_df(container, frame_cls=TtsDataFrame)`:
  - One row per `DataItem.values`.
  - Copies metadata and name onto the frame.
  - Optionally preserves history as metadata.
- `df_to_container(df, container_cls)`:
  - Creates `container_cls(raw_data=df.to_dict('records'), cast_fields=..., validate=...)`.
 
**Usage pattern for migration:**
 
- Existing missions:
  - Continue using container-based Dexter directly.
 
- New missions or new features (e.g., OCO-2 tooling):
  - Start from `TtsDataFrame` as the primary data representation.
  - Convert to containers right at the Dexter boundary if needed, or
  - Once frame rows fully implement the Dexter row contract, allow Dexter to operate directly on frames.
 
The adapters let you shift particular flows to frames incrementally without having to redesign everything at once.
 
---
 
## Step 6 – Multi-LAD / Multi-Procedure Wiring
 
**Goal:** Support multiple Expected LAD sets and procedures (e.g., different OCO-2 realtime procedures) without hard-coding everything into one monolithic dispositioner.
 
We already have:
 
- `ExpectedLadContainer` in `tts_data_utils.multimission.expected_lad`.
- `LadChanvalDeriver` in `tts_dante.derivers.eha` to build expected-vs-actual LAD containers.
- `LadEhaDispositioner` in `tts_dexter.dispositioners.eha` to apply dispositions from CSV rules.
 
**Recommended pattern:**
 
- For each realtime procedure, define a small Dexter façade class in the mission-specific project (e.g., `oco2_dexter`):
 
  - `class Oco2ProcX_LadDexter(Dexter):`
    - In `__init__`, load:
      - An EHA data set (container or frame).
      - An `ExpectedLadContainer` restricted to that procedure’s LAD spec (per-file or via a `Procedure` column filter).
    - Call `self.init_data(...)` to register those containers.
    - Call `self.init_dispositioner(LadEhaDispositioner)` or a subclass with mission/procedure-specific configuration.
 
- If you need different disposition behavior per procedure, subclass `LadEhaDispositioner` into:
 
  - `Oco2ProcX_LadDispositioner(LadEhaDispositioner)`
 
  and wire that into the appropriate Dexter façade.
 
**How this interacts with frames:**
 
- Upstream systems can work entirely in `TtsDataFrame`.
- Right before Dexter, convert to containers or pass frames directly (once frame rows implement the Dexter row contract).
- After calling `stamp_all_to_outputs()`, convert the Expected LAD outputs into DataFrames for reporting.
 
---
 
## Suggested Implementation Order
 
To keep risk low, here’s a concrete sequence of work items:
 
1. **Extract Dexter row logic into a mixin and wire it into `DataItem`.**
   - No behavior changes, just relocation and cleanup.
2. **Add disposition storage and Dexter row behavior to `TtsRowSeries` / `TtsDataFrame`.**
   - Introduce `_row_dispositions` and `DexterRowMixin` on the frame side.
3. **Add `stamp_all_to_outputs()` to `Dexter` using `all_output_data`.**
   - Keep current `stamp_all()` intact.
4. **Implement container↔frame adapters.**
   - Start using them in one or two well-scoped call sites.
5. **Introduce a single mission-specific Dexter façade that uses frames end-to-end.**
   - For example, an OCO-2 procedure that uses `TtsDataFrame` for EHA and Expected LAD.
6. **Gradually migrate remaining flows to frames where beneficial.**
   - Prefer new code that starts with `TtsDataFrame` + Dexter row behavior.
   - Treat `DataContainer` as a compatibility + history layer rather than the primary abstraction.
 
Each step can be developed and tested independently, and rolled back if needed without impacting other missions.
