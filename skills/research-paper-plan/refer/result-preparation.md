# Audited Result Preparation

Read before preparing `research-paper-plan` evidence. This is analysis of completed experiments, not authorization to run missing experiments. Follow the skill's roots, review, bundle freeze, approval, and handoff contract. This reference specifies procedures, not a universal result parser: adapters must implement the actual observed project schemas.

## 1. Establish what exists and what was measured

Inspect the actual result files and enough implementation/evaluation/config code to explain their fields. Record:

- source path, exact byte SHA-256, schema/version if present, encoding, and precise row/key/line/byte-range locator;
- dataset/task/version/split and sample identities; exclusions/filtering/preprocessing; ground-truth availability;
- method/baseline role, original run/attempt/seed, code/config/checkpoint/proposal/experiment-plan bindings;
- metric definition/direction/unit, evaluation protocol and budget, checkpoint/threshold selection, number of evaluated examples, completion/error status;
- original selected populations and expected attempts from actual tracker/config evidence, separately from observed/valid results.

Read reports as context and reconcile them with machine-readable evidence. A report table without underlying result provenance cannot silently become audited measurement data. Keep literature-reported baselines distinct from reproduced/local baselines, with their original protocol limitations; do not pool them as repeated runs.

Do not infer missing seed, split, code hash, sample count, checkpoint, or budget from neighboring files. Unknown values are null with explanation; unknown fields relevant to comparability prevent pooling. Use actual attempt identity, not filenames alone, to find duplicates/retries. Multiple copies of one run are not independent evidence. Distinct attempted retries stay visible; any selected retry/checkpoint must follow the original justified rule, not post-hoc best performance.

### Original versus current code

Identify original immutable code/config snapshots or commit plus actual accessible file bindings if available. A commit label without inspected matching content is weaker provenance; state that limitation. Inspect relevant differences from current code. Method equations/diagrams must describe the applicable implementation, not a newer design assigned to older measurements. Keep original bindings unchanged and separately inventory current inspected source bytes. If original code is unavailable, state it and restrict claims; do not manufacture historical hashes. Material unresolved method/evaluation applicability blocks claims requiring that evidence.

### Growing logs

When a consumed source is still growing, copy a bounded observed window into `analysis/` without changing the original. Record original source identity, observed time/watermark, boundaries/line or byte ranges, length, snapshot digest, and how boundaries represent complete records. Detect/report truncation, reset, duplicate append records, or mismatched identities before using the snapshot. Inventory the immutable snapshot bytes and identify its live source separately; do not bind future content with a whole-log hash observed earlier. Never read an arbitrary last line as the completed run summary.

## 2. Implement complete, bounded analysis

Prefer a trustworthy existing analysis path after inspecting its entry point, imports, called scripts, writes and side effects. Reuse does not waive validation of metric semantics, selections or dependencies. If no suitable analysis exists, write complete project-specific adapters under `PLAN_DIR/analysis/`:

1. Parse the observed schemas, with exact field-to-normalized mapping and explicit selection/completion rules.
2. Produce stable unique record identities and original provenance, including visible failures/exclusions/missing values.
3. Normalize only documented units/transforms and validate comparability keys.
4. Compute justified statistics from declared independent units.
5. Produce normalized JSON, actual useful tables/plots and machine-readable trace mappings.
6. Emit actual execution records and fail honestly on unsupported formats or unavailable required data instead of manufacturing values.

These are required real behaviors whenever scripts are generated, not stub functions or promises. No placeholder CSV, fake curve, random fallback, hardcoded invented result, or silently successful empty export. Write outputs only within approved planning paths. No experiment source/config/tracker changes, inference, evaluation jobs, downloads, or automatic dependency installation. Recalculating a metric from existing predictions and actual matching labels is permitted; running a model to obtain missing predictions is not.

Specify the actual interpreter/executable, versions/dependencies, cwd, exact command and parameters, observed source schemas, required inputs, output paths and execution records. Use project-local existing tools/dependencies when available. If a dependency or execution/visual capability is absent, record the exact missing prerequisite and mark the corresponding gate incomplete. Do not claim an unexecuted script created results.

## 3. Normalize `RESULTS.json` (schema_version 1)

Root: `schema_version: 1`, `records: [...]`, `aggregates: [...]`. Additional project-specific fields are allowed when explained. JSON numbers must be finite; never emit NaN/Infinity tokens. Keep full numeric precision in normalized data; round only presentation outputs with recorded rules.

### Record contract

Every record has these semantics (use these field names):

| Field | Required content |
|---|---|
| `result_id` | Unique stable ID for one measured metric/unit/attempt identity; duplicate source copies cannot generate independent IDs |
| `run_id`, `attempt` | Original observed identifiers, or honest null with reason |
| `method`, `role` | Actual method and baseline/proposed/control/diagnostic role; distinguish literature-only baselines |
| `dataset`, `task`, `split`, `seed` | Observed identities; null and explain if unknown, never guessed |
| `metric`, `direction`, `unit` | Exact defined measure, higher/lower or appropriate direction, fraction/percent/ms/etc.; explain nonstandard definitions |
| `value` | Actual finite numeric value, or null for missing/failed/nonfinite measurements |
| `status`, `reason` | Actual valid/excluded/missing/failed status and reason; explain any null value, unknown binding or exclusion |
| `source` | `{path,sha256,locator}` of the actual immutable input/snapshot, with raw original value/token when parsing excluded nonfinite data |
| `original_bindings` | Actual original code/config/attempt/plan/proposal/checkpoint/data bindings, paths/digests or honest nulls plus limitations; never retroactive current hashes |
| `protocol` | Actual evaluation/split/budget/selection/preprocessing/version/denominator metadata needed to establish comparability |

An excluded but finite observation may retain its actual `value` with excluded status/reason and must not enter the primary aggregate. Failed/missing/nonfinite observations use null value. If no source row exists for an expected missing attempt, do not invent a metric-source locator: retain honest null metric-source binding and link the actual tracker/plan evidence establishing that expected attempt in `original_bindings`. Mark this an expected-not-observed record, not an observed measurement. These exceptions must be explicit in the report; actual measurements always require exact source bindings.

Preserve failed samples and runs. A partially completed evaluation may have finite per-sample values but is not automatically a comparable completed-run metric. Record coverage/denominator and whether failure is outcome-dependent; do not remove failed samples to improve success metrics. Missing records cannot become zero. A measured zero is valid only if it is genuinely recorded/computed by the correct metric.

Examples in writing references are rhetorical illustrations, never data sources. Only observed records populate this artifact.

## 4. Statistics and comparability

Define the scientific unit first: independent training seeds, matched subjects, independent datasets, or another justified unit. Number of log rows, batches, checkpoints, correlated frames, repeated copies, or individual predictions is not automatically the number of independent runs. State the estimand, grouping, selection rule and denominators before aggregation.

### Aggregate contract

Each aggregate has:

- unique `aggregate_id` and explicit `grouping` across method, dataset/task/version/split, metric/direction/unit, budget, evaluation protocol, preprocessing and applicable code/config family;
- `member_result_ids` for actual included observations; explicit excluded IDs/reasons, missing/failed counts, and observed/expected/valid denominators (expected null if unknown);
- valid independent `n`, `mean`, `sd`, `ddof: 1`, and `statistic_semantics` explaining unit, estimand, selection, grouping and any transformation.

When comparable independent finite scalar observations are appropriate, compute arithmetic mean over valid members. Sample SD is `sqrt(sum((x_i - mean)^2)/(n-1))`: null for n<2, never 0 to conceal one run. For n=0 mean and SD are null. n=1 gives the actual mean and no estimated between-run SD; any descriptive within-sample variance must be separately labeled, not substituted. Exact identical observations can legitimately yield SD=0 when n>=2, but verify duplicate identity has not inflated n.

For a justified non-mean statistic, keep required mean/sample-SD fields honest where meaningful and report median/quantiles/etc. as additional labeled statistics with method/data. Do not relabel median as mean or raw min/max as a confidence interval.

### Non-negotiable exclusions and disclosures

- Never pool incompatible datasets, test/validation splits, preprocessing, metrics/units, budgets, checkpoint selection rules or protocols. Unknown compatibility stays separate. A documented conversion (for example fraction to percent) retains original values, formula and source; it does not repair protocol mismatch.
- Do not count duplicate files, repeated summary rows, checkpoints or retried copies as extra seeds. Do not choose the best seed. Preserve genuine retries and exclusions with justified rules.
- Never average per-class or per-batch values to mimic a dataset metric unless that matches its actual definition/weights. Macro/micro/weighted F1, different accuracy denominators and censored latency are not interchangeable.
- Reconstruct expected/attempted/observed/valid counts only from evidence; unknown counts remain unknown. Report outcome-dependent failures and missingness. Do not present surviving-run success as unconditional performance.
- Do not derive significance from means/SD alone without the required data/design/assumptions. Paired comparisons require real matched independent units and must retain matching IDs and missing pairs. No artificial pairing by row order.
- Confidence intervals/tests require justified independent units, resampling level/design, confidence level/test statistic, assumptions and applicable multiplicity handling. Document bootstrap seeds only if a real justified bootstrap is executed; never invent intervals from one seed or imply training-seed uncertainty from resampling test examples.
- Label sample SD, standard error and confidence intervals distinctly. A population SD (`ddof=0`) is not between-run sample SD. Do not add error bars when their interpretation is unsupported.
- Distinguish absolute difference, percentage-point difference, relative percent change, ratio and speedup; retain formulas, direction and units. Do not divide by zero or hide nonfinite ratios.
- Correlation/ablation does not prove mechanism or causality. Null/negative findings should constrain the story rather than disappear.

## 5. Existing predictions and ground truth

Metric recomputation is allowed only from already saved predictions and actual labels/targets with verified sample-ID joins, split/version, label mapping, thresholds, masks, preprocessing and coverage. Audit missing/duplicate IDs, failed outputs, mismatched ordering and exclusions. Inspect the original evaluation implementation and explain differences. Do not use predictions as their own ground truth, invent labels, use validation-selected thresholds on test data without disclosure, or silently fill absent predictions. Retain original reported values and separately identify recomputed values/definitions, source IDs and discrepancies; neither replaces the other without explanation.

## 6. Real tables and figures

Choose assets that answer real claim/diagnostic questions. There is no figure quota; if no scientific plot is appropriate explain why, but prepare actual suitable tables/visualizations wherever the evidence calls for them. A conceptual diagram does not replace required measured results.

### Tables

Export actual consumed machine-readable tables (CSV and useful LaTeX). Label method, dataset/split, metric/direction/unit, n and uncertainty. Display absent/failed/incomparable results honestly (for example em dash with reason), never as zero. Preserve full-precision underlying data and record presentation rounding. Mark best results only within truly comparable groups; ties and uncertainty do not justify invented ranking or statistical significance. A table cell trace maps output path/row/column to record/aggregate IDs, source members, transforms/selection, exclusions and uncertainty.

### Plots

Create actual appropriate plots, such as comparable method estimates, measured learning curves already present in logs, failure/coverage analyses, or matched per-unit differences. No manufactured points, extrapolated unsupported curves, copied reference-paper numbers represented as local runs, or selective smoothing. For an inherited curve, record step alignment, seeds, censoring and available coverage. Any smoothing/interpolation is labeled with formula/window and raw data access; it cannot create new evidence or suppress inconvenient ranges.

Use clear units and axes, honest limits, readable labels at intended size, accessible colors plus markers/line styles, and uncluttered self-contained captions. Identify metric direction, split, n, uncertainty type and independent unit. Avoid misleading truncated bar axes; justify transformed/log axes. Do not connect incomparable categories or hide failed runs. Prefer suitable vector PDF/SVG and a viewable PNG when useful; raster source images remain raster and are not made vector by wrapping them.

A plot-series trace maps every series/point/band to result/aggregate IDs and full transformation/uncertainty/source provenance. Replotting from normalized results must not silently reselect seeds or change statistics. Every planned numeric caption/claim maps to these same IDs.

## 7. Execute and inspect, then report

Execute only inspected result-preparation commands. Record real command/cwd/interpreter/dependencies/parameters, exit code, stdout/stderr location, exact input/output inventories, and analysis script digests. A nonzero exit, missing output, unsupported format, empty input, or unavailable dependency is a blocker, not a plot-generation success. Preserve diagnostic failures and implement scoped fixes when possible; never delete evidence to make the run look clean.

Inspect actual normalized values against representative raw locators and investigate discrepancies. Check grouping and totals, source uniqueness, valid/excluded/missing/failure counts, n<2 handling, finite JSON values and transform formulas. Inspect actual table content and actually view the rendered figures for labels, clipping, overlap, axes/uncertainty semantics, and correspondence with normalized values. A file extension, file existence or plotting-library success does not prove numeric/visual correctness. If the host cannot view renders, explicitly record the missing visual inspection and keep its gate pending.

`RESULTS_REPORT.md` documents performed analysis and inspection, not future promises: observed input schemas and audit; code-method/claim mapping; historical applicability; metric/statistical procedures; exact commands/execution records; source-to-result/table/figure mappings; real key results and negative findings; failures/exclusions/denominators; comparability; missing experiments/data; and limitations. Keep interpretation separate from measurements. Supply these actual files to independent review before the final bundle and user gate.

## 8. Reproducibility and freeze boundary

The plan bundle inventories every consumed code/config/source snapshot, adapter, schema mapping, execution record, normalized dataset, table, figure and trace file by actual byte SHA-256. Avoid recursive unrelated-source ingestion. Documentation of expected runtime behavior is not an execution record. No analysis artifact embeds the eventual bundle digest if that artifact is in its inventory. Review reports bind inspected content files and do not depend on their own hash or the eventual bundle hash. State holds review/approval bindings after bundle freeze. Changed source/data/statistics/assets invalidate affected review and final approval; rerun preparation and return through planning gates rather than patching evidence during writing.
