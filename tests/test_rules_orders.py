# ============================================================
# test_rules_orders.py
# ------------------------------------------------------------
# orders クレンジングルール 単体テスト
#
# 【目的】
# ・業務ルールが仕様どおり動作することを保証する
# ・異常系を「仕様として固定」する
#
# 【注意】
# ・ログ出力はテスト対象外
# ・値そのものではなく「結果と理由」を確認する
# ============================================================

import pytest
from scripts.rules_orders import cleanse_order_row


# ------------------------------------------------------------
# 正常系：すべて正しいデータ
# ------------------------------------------------------------
def test_valid_order_row():
    row = {
        "order_date": "2024/01/15",
        "amount": "1000"
    }

    cleaned_row, warnings = cleanse_order_row(row)

    assert cleaned_row["order_date"] == "2024-01-15"
    assert cleaned_row["amount"] == 1000
    assert cleaned_row["error_flag"] == 0
    assert warnings == []


# ------------------------------------------------------------
# 異常系：order_date 欠損
# ------------------------------------------------------------
def test_missing_order_date():
    row = {
        "order_date": "",
        "amount": "1000"
    }

    cleaned_row, warnings = cleanse_order_row(row)

    assert cleaned_row["error_flag"] == 1
    assert len(warnings) == 1
    assert warnings[0]["column"] == "order_date"
    assert warnings[0]["reason"] == "missing_value"


# ------------------------------------------------------------
# 異常系：order_date 形式不正
# ------------------------------------------------------------
def test_invalid_order_date_format():
    row = {
        "order_date": "2024-01-15",
        "amount": "1000"
    }

    cleaned_row, warnings = cleanse_order_row(row)

    assert cleaned_row["error_flag"] == 1
    assert warnings[0]["column"] == "order_date"
    assert warnings[0]["reason"] == "invalid_format"


# ------------------------------------------------------------
# 異常系：amount 欠損
# ------------------------------------------------------------
def test_missing_amount():
    row = {
        "order_date": "2024/01/15",
        "amount": ""
    }

    cleaned_row, warnings = cleanse_order_row(row)

    assert cleaned_row["error_flag"] == 1
    assert warnings[0]["column"] == "amount"
    assert warnings[0]["reason"] == "missing_value"


# ------------------------------------------------------------
# 異常系：amount 形式不正
# ------------------------------------------------------------
def test_invalid_amount_format():
    row = {
        "order_date": "2024/01/15",
        "amount": "abc"
    }

    cleaned_row, warnings = cleanse_order_row(row)

    assert cleaned_row["error_flag"] == 1
    assert warnings[0]["column"] == "amount"
    assert warnings[0]["reason"] == "invalid_format"


# ------------------------------------------------------------
# 複合異常：order_date + amount 両方不正
# ------------------------------------------------------------
def test_multiple_errors():
    row = {
        "order_date": "",
        "amount": "abc"
    }

    cleaned_row, warnings = cleanse_order_row(row)

    assert cleaned_row["error_flag"] == 1
    assert len(warnings) == 2

    columns = {w["column"] for w in warnings}
    assert "order_date" in columns
    assert "amount" in columns
