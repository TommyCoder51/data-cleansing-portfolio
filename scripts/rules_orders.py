# ============================================================
# rules_orders.py
# ------------------------------------------------------------
# orders CSV 用 業務ルール定義
#
# 【役割】
# ・業務的な判断をすべてここに集約する
# ・cleanse.py は「流すだけ」
#
# 【原則】
# ・行は消さない
# ・補正できなければ error_flag
# ・WARN は「列名＋理由」のみ
# ============================================================

from datetime import datetime


def cleanse_order_row(row: dict) -> tuple[dict, list]:
    """
    orders データ 1 行分のクレンジング処理。

    Parameters
    ----------
    row : dict
        CSV から読み込んだ 1 行（列名 → 値）

    Returns
    -------
    cleaned_row : dict
        補正済みの行データ
    warnings : list
        WARN ログ用情報
    """

    cleaned_row = row.copy()
    warnings = []
    error_flag = 0

    # --------------------------------------------------------
    # order_date チェック
    # --------------------------------------------------------
    order_date = (row.get("order_date") or "").strip()

    if not order_date:
        error_flag = 1
        warnings.append({
            "column": "order_date",
            "reason": "missing_value"
        })
    else:
        try:
            dt = datetime.strptime(order_date, "%Y/%m/%d")
            cleaned_row["order_date"] = dt.strftime("%Y-%m-%d")
        except Exception:
            error_flag = 1
            warnings.append({
                "column": "order_date",
                "reason": "invalid_format"
            })

    # --------------------------------------------------------
    # amount チェック
    # --------------------------------------------------------
    amount = (row.get("amount") or "").strip()

    if not amount:
        error_flag = 1
        warnings.append({
            "column": "amount",
            "reason": "missing_value"
        })
    else:
        try:
            cleaned_row["amount"] = int(amount)
        except Exception:
            error_flag = 1
            warnings.append({
                "column": "amount",
                "reason": "invalid_format"
            })

    # --------------------------------------------------------
    # error_flag 反映
    # --------------------------------------------------------
    cleaned_row["error_flag"] = error_flag

    return cleaned_row, warnings
