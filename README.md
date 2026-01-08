## Directory Structure

```
data-cleansing-portfolio/
├─ sample_data/
│  ├─ raw/        # 元データ（加工禁止）
│  └─ cleaned/    # クレンジング後データ
├─ scripts/       # 処理スクリプト
├─ logs/          # 実行ログ
├─ tests/         # テストコード
├─ tools/         # ツール
├─ requirements.txt
└─ README.md
```

## Data Policy

- raw データは一切上書きしません
- cleaned データは正規化済みの理想形として出力します
- 不正・欠損データは削除せず、フラグで管理します



## Overview

This project is a sample implementation of CSV data cleansing using Python.
It focuses on safe data handling, logging, and testable rule-based cleansing.


## Usage

```bash
python scripts/cleanse.py sample_data/raw/orders_raw.csv


## Test

This project uses pytest.

```bash
cd data-cleansing-portfolio
pytest
```