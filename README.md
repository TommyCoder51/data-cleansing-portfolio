# CSVデータクレンジングツール

> 「Excelのデータに空欄や形式ミスがあって困っている」  
> そんな現場のお悩みを、Pythonで自動チェック・修正するツールです。

---

## こんな方に使っていただけます

- 売上・注文データの整備を手作業でやっていて大変な方
- ECサイトの受注CSVに不正データが混入して困っている方
- 経理・事務担当者で、Excelの集計前にデータをきれいにしたい方
- システム開発会社で、データ取り込み前処理の実装例を探している方

---

## このツールでできること

- CSVの**空欄・形式ミス**を自動検出
- 日付形式を自動統一（例：`2024/01/15` → `2024-01-15`）
- 問題のある行を**削除せず**、`error_flag`でマーキング（元データ保全）
- 処理結果をログファイルに記録（列名・理由のみ。実データは出力しない）

---

## 動作イメージ

```
【入力】orders_raw.csv（日付ミス・金額空欄あり）
        ↓ python scripts/cleanse.py で実行
【出力】cleaned/orders_raw.csv（補正済み＋error_flagつき）
【ログ】logs/cleanse_20240115.log（問題箇所の記録）
```

---

## ディレクトリ構成

```
data-cleansing-portfolio/
├─ sample_data/
│  ├─ raw/        # 元データ（このフォルダは絶対に上書きしません）
│  └─ cleaned/    # クレンジング後データ
├─ scripts/
│  ├─ cleanse.py        # メイン処理（入出力・ログ制御）
│  └─ rules_orders.py   # 業務ルール定義（チェック・補正ロジック）
├─ logs/          # 実行ログ
├─ tests/         # テストコード
├─ requirements.txt
└─ README.md
```

---

## 使い方

```bash
# 依存ライブラリのインストール
pip install -r requirements.txt

# クレンジング実行
python scripts/cleanse.py sample_data/raw/orders_raw.csv
```

出力ファイルは `sample_data/cleaned/` に生成されます。

---

## テスト実行

```bash
cd data-cleansing-portfolio
pytest
```

---

## データの取り扱い方針

| 方針 | 内容 |
|------|------|
| 元データ保全 | `raw/` フォルダのデータは一切上書きしません |
| 削除しない | 不正・欠損データは行削除せず、`error_flag=1` で管理します |
| ログの安全性 | ログには列名と理由のみ記録。実データの値は一切出力しません |

---

## 技術スタック

- Python 3.x
- 標準ライブラリのみ使用（`csv` / `logging` / `datetime`）
- 外部ライブラリ不要

---

## カスタマイズについて

`rules_orders.py` に業務ルールを集約しているため、  
チェック項目の追加・変更が容易です。  
「自社のCSVに合わせたい」などのご要望もお気軽にご相談ください。

---
