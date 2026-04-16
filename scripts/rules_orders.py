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

import re
from datetime import datetime
WAREKI_SHOWA = "昭和"
WAREKI_HEISEI = "平成"
WAREKI_REIWA = "令和"
WAREKI = {WAREKI_SHOWA: 1925, WAREKI_HEISEI: 1988, WAREKI_REIWA: 2018}


# ============================================================
# 日付パース関数
# ============================================================

def _try_parse_date(value: str):
    """
    各種日付表記を datetime に変換する。
    変換できない場合は None を返す。

    対応形式：
    ・2024/01/05  2024/1/5  （スラッシュ 全角／半角 ゼロサプレス対応）
    ・2024-01-06  2024-1-6  （ハイフン ゼロサプレス対応）
    ・2024年1月7日           （年月日）
    ・20240108               （区切りなし8桁）
    ・14年1月7日 / 14/1/7 / 14-1-7  （2桁年>=10 → 2000年代）
    ・1年1月7日 / 1/1/7 / 1-1-7     （1桁年<=9 → 令和）
    ・昭和63年1月7日 / 平成6年1月7日 / 令和6年1月7日  （和暦）
    """

    # 全角スラッシュ → 半角スラッシュ
    value = value.replace("／", "/")

    # -------- 8桁区切りなし --------
    m = re.fullmatch(r"(\d{4})(\d{2})(\d{2})", value)
    if m:
        try:
            return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            pass

    # -------- 4桁年 + スラッシュ or ハイフン --------
    m = re.fullmatch(r"(\d{4})[/\-](\d{1,2})[/\-](\d{1,2})", value)
    if m:
        try:
            return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            pass

    # -------- 年月日（漢字） 4桁年 --------
    m = re.fullmatch(r"(\d{4})年(\d{1,2})月(\d{1,2})日?", value)
    if m:
        try:
            return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            pass

    # -------- 2桁年（>=10） or 1-2桁年（<=9 → 令和） + スラッシュ or ハイフン --------
    m = re.fullmatch(r"(\d{1,2})[/\-](\d{1,2})[/\-](\d{1,2})", value)
    if m:
        yy = int(m.group(1))
        if yy >= 10:
            try:
                return datetime(2000 + yy, int(m.group(2)), int(m.group(3)))
            except ValueError:
                pass
        elif yy <= 9:
            seireki = 2018 + yy
            if seireki <= datetime.now().year:
                try:
                    return datetime(seireki, int(m.group(2)), int(m.group(3)))
                except ValueError:
                    pass

    # -------- 2桁年（>=10） or 1-2桁年（<=9 → 令和） + 年月日（漢字） --------
    m = re.fullmatch(r"(\d{1,2})年(\d{1,2})月(\d{1,2})日?", value)
    if m:
        yy = int(m.group(1))
        if yy >= 10:
            try:
                return datetime(2000 + yy, int(m.group(2)), int(m.group(3)))
            except ValueError:
                pass
        elif yy <= 9:
            seireki = 2018 + yy
            if seireki <= datetime.now().year:
                try:
                    return datetime(seireki, int(m.group(2)), int(m.group(3)))
                except ValueError:
                    pass

# -------- 和暦（昭和・平成・令和）+ 年月日（漢字） --------
    m = re.fullmatch(
        rf"({WAREKI_SHOWA}|{WAREKI_HEISEI}|{WAREKI_REIWA})(\d{{1,2}})年(\d{{1,2}})月(\d{{1,2}})日?", value)
    if m:
        gengou = m.group(1)
        base = WAREKI[gengou]
        seireki = base + int(m.group(2))
        if gengou == WAREKI_REIWA and seireki > datetime.now().year:
            pass
        else:
            try:
                return datetime(seireki, int(m.group(3)), int(m.group(4)))
            except ValueError:
                pass

    return None


# ============================================================
# メインクレンジング関数
# ============================================================

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
        dt = _try_parse_date(order_date)
        if dt:
            cleaned_row["order_date"] = dt.strftime("%Y-%m-%d")
        else:
            error_flag = 1
            print(f"")
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
            cleaned_row["amount"] = int(amount.replace(",", "").replace(
                "，", "").replace("¥", "").replace("￥", ""))
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
