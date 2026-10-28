# ILIAS QC — Manual Test Suite

Generate ILIAS-uploadable quiz pools from sample question files for manual testing.

## Setup

```bash
conda activate iliasqc
```

## Run

```bash
python manual_test.py
```

## Output

All ZIP files land in `manual_test/output/`, organised into titled subfolders:

```
output/
├── Single Choice Questions/
├── Multiple Choice Questions/
├── Gap Fill Questions/
├── Mixed Question Pool/
├── Override Test/
├── Points Filter (1 pt)/
└── combine_results/
    ├── quiz_combinations.csv
    ├── 3873883666__1600__qpl_6599701.zip
    └── 2395833667__1600__qpl_6599702.zip
```

Each ZIP uses the ILIAS-prescribed filename (`<timestamp>__1600__qpl_<id>.zip`) so it imports correctly. Upload individual ZIPs into ILIAS question pools to verify.

## What's tested

- **Convert** — single/multiple choice, gap-fill, mixed pools
- **--title / --description overrides**
- **--points filter**
- **combine** — quiz combination generation with CSV export

## Prerequisites

- Python ≥ 3.12 (conda env `iliasqc`)
- iliasqc installed in that env: `pip install -e .` (from project root)