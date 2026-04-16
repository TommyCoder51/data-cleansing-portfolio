# ============================================================
# cleanse.py
# ------------------------------------------------------------
# データクレンジング メイン処理
#
# 【責務】
# ・入出力制御
# ・ログ制御
# ・CSV 読み書き
# ・業務ルール呼び出し
#
# 【重要方針】
# ・raw データは絶対に変更しない
# ・削除は行わず、必ずフラグ管理
# ・ログは「貼って説明できる」粒度で残す
# ============================================================

import csv
import logging
import os
import sys
from datetime import datetime

from rules_orders import cleanse_order_row


def setup_logger(log_dir: str) -> logging.Logger:
    """
    ログ出力用 logger を初期化する。

    【設計意図】
    ・ログは「実装者のため」ではなく「説明のため」に残す
    ・後工程、非エンジニア、顧客にそのまま貼れる形式を想定
    ・DEBUG は内部調査用、INFO/WARN/ERROR は説明用

    【ログ仕様】
    ・出力先：logs/cleanse_YYYYMMDD.log
    ・文字コード：UTF-8
    ・実データ値は出力しない（列名・理由のみ）
    """

    # ログディレクトリ作成
    os.makedirs(log_dir, exist_ok=True)

    # 日付単位のログファイル名
    log_filename = f"cleanse_{datetime.now().strftime('%Y%m%d')}.log"
    log_path = os.path.join(log_dir, log_filename)

    # logger 取得（固定名）
    logger = logging.getLogger("cleanse_logger")
    logger.setLevel(logging.DEBUG)

    # フォーマット（時刻必須）
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s"
    )

    # ファイルハンドラ
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)

    # ハンドラ重複防止
    if not logger.handlers:
        logger.addHandler(file_handler)

    return logger


def main():
    """
    メイン処理。

    処理の流れ：
    1. 引数チェック
    2. パス解決
    3. CSV 読み込み（DictReader）
    4. 行単位クレンジング
    5. cleaned CSV 出力
    """

    # ========================================================
    # 1. 引数チェック
    # ========================================================
    if len(sys.argv) != 2:
        print("Usage: python cleanse.py <input_csv_path>")
        sys.exit(1)

    input_path = sys.argv[1]

    # ========================================================
    # 2. パス解決
    # ========================================================
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    log_dir = os.path.join(base_dir, "logs")
    cleaned_dir = os.path.join(base_dir, "sample_data", "cleaned")

    os.makedirs(cleaned_dir, exist_ok=True)

    # ========================================================
    # 3. ロガー初期化
    # ========================================================
    logger = setup_logger(log_dir)

    logger.info("Process started")
    logger.debug(f"base_dir={base_dir}")
    logger.debug(f"input_path={input_path}")
    logger.debug(f"cleaned_dir={cleaned_dir}")

    # ========================================================
    # 4. 入力ファイル存在確認
    # ========================================================
    if not os.path.isfile(input_path):
        logger.error(f"Input file not found")
        sys.exit(1)

    input_filename = os.path.basename(input_path)
    output_path = os.path.join(cleaned_dir, input_filename)

    logger.debug(f"input_filename={input_filename}")
    logger.debug(f"output_path={output_path}")

    # ========================================================
    # 5. CSV 読み込み
    # ========================================================
    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            rows = list(reader)
    except Exception:
        logger.error("CSV parse failed")
        sys.exit(1)

    # ヘッダチェック
    if not fieldnames:
        logger.error("CSV header missing")
        sys.exit(1)

    # データ行チェック
    if len(rows) == 0:
        logger.error("CSV has no data rows")
        sys.exit(1)

    logger.info(f"Input loaded: rows={len(rows)}")
    logger.debug(f"fieldnames(before)={fieldnames}")

    # ========================================================
    # 6. 出力列定義
    # ========================================================
    if "error_flag" not in fieldnames:
        fieldnames = list(fieldnames)
        fieldnames.append("error_flag")
        logger.debug("error_flag column appended")

    logger.debug(f"fieldnames(after)={fieldnames}")

    # ========================================================
    # 7. 行単位クレンジング
    # ========================================================
    cleaned_rows = []

    for csv_row_no, row in enumerate(rows, start=2):
        logger.debug(f"row_start row={csv_row_no}")

        cleaned_row, warnings = cleanse_order_row(row)

        # WARN ログ出力
        for w in warnings:
            logger.warning(
                f"row={csv_row_no} column={w['column']} reason={w['reason']}"
            )

        logger.debug(
            f"row_end row={csv_row_no} error_flag={cleaned_row.get('error_flag')}"
        )

        cleaned_rows.append(cleaned_row)

    logger.debug(f"cleaned_rows_count={len(cleaned_rows)}")

    # ========================================================
    # 8. cleaned CSV 出力
    # ========================================================
    try:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(cleaned_rows)
    except Exception:
        logger.error("Failed to write cleaned CSV")
        sys.exit(1)

    logger.info(f"Output written: {input_filename}")
    logger.info("Process completed")
    print("クレンジング処理が完了しました。")


if __name__ == "__main__":
    main()
