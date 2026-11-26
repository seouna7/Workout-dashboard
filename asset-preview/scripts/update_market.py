#!/usr/bin/env python3
"""data/market.json 갱신 스크립트.

지수·환율·관심 ETF의 최신가, 전일 대비 등락률, 52주 고점 대비 위치, 최근 30거래일 종가를
yfinance로 받아 data/market.json 에 저장한다.

사용:
    python scripts/update_market.py
"""
from __future__ import annotations

import json
import math
import os
import sys
from datetime import datetime, timezone, timedelta

try:
    import yfinance as yf
except Exception as exc:  # pragma: no cover
    print("yfinance import 실패: %r" % (exc,), file=sys.stderr)
    sys.exit(1)

KST = timezone(timedelta(hours=9))

# (심볼, 표시 이름, 통화, 소수 자릿수, 분류)
SYMBOLS = [
    ("^GSPC", "S&P 500", "USD", 2, "index"),
    ("^NDX", "나스닥 100", "USD", 2, "index"),
    ("^KS11", "코스피", "KRW", 2, "index"),
    ("KRW=X", "원/달러 환율", "KRW", 2, "fx"),
    ("BTC-USD", "비트코인", "USD", 0, "crypto"),
    ("VOO", "VOO", "USD", 2, "stock"),
    ("QLD", "QLD", "USD", 2, "stock"),
    ("SOXL", "SOXL", "USD", 2, "stock"),
]


def clean(v):
    if v is None:
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    if math.isnan(f) or math.isinf(f):
        return None
    return f


def quote(symbol: str):
    t = yf.Ticker(symbol)
    hist = t.history(period="1y", interval="1d", auto_adjust=False)
    if hist is None or len(hist) == 0:
        raise RuntimeError("no history for %s" % symbol)
    closes = [clean(c) for c in list(hist["Close"].values)]
    closes = [c for c in closes if c is not None]
    if not closes:
        raise RuntimeError("no close prices for %s" % symbol)
    last = closes[-1]
    prev = closes[-2] if len(closes) >= 2 else last
    # 52주 고점: 최근 1년 종가·고가 중 큰 값
    highs = [clean(h) for h in list(hist["High"].values)] if "High" in hist else []
    highs = [h for h in highs if h is not None]
    high52 = max(highs + closes) if highs else max(closes)
    return {
        "price": last,
        "prevClose": prev,
        "changePct": ((last - prev) / prev * 100.0) if prev else 0.0,
        "high52": high52,
        "fromHighPct": ((last - high52) / high52 * 100.0) if high52 else 0.0,
        "spark": [round(c, 4) for c in closes[-30:]],
        "lastDate": str(hist.index[-1].date()),
    }


def main() -> int:
    out_items = []
    errors = []
    for symbol, name, cur, digits, kind in SYMBOLS:
        try:
            q = quote(symbol)
        except Exception as exc:
            errors.append("%s: %r" % (symbol, exc))
            print("실패 %s: %r" % (symbol, exc), file=sys.stderr)
            continue
        out_items.append(
            {
                "symbol": symbol,
                "name": name,
                "currency": cur,
                "digits": digits,
                "kind": kind,
                "price": round(q["price"], 4),
                "prevClose": round(q["prevClose"], 4),
                "changePct": round(q["changePct"], 3),
                "high52": round(q["high52"], 4),
                "fromHighPct": round(q["fromHighPct"], 3),
                "spark": q["spark"],
                "lastDate": q["lastDate"],
            }
        )

    if not out_items:
        print("모든 심볼 조회 실패 — market.json 을 덮어쓰지 않습니다.", file=sys.stderr)
        return 1

    now = datetime.now(timezone.utc)
    payload = {
        "updated": now.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "updatedKst": now.astimezone(KST).strftime("%Y-%m-%d %H:%M KST"),
        "source": "yfinance (Yahoo Finance)",
        "errors": errors,
        "items": out_items,
    }

    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "market.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("wrote %s (%d items, %d errors)" % (path, len(out_items), len(errors)))
    return 0 if len(out_items) == len(SYMBOLS) else 0


if __name__ == "__main__":
    raise SystemExit(main())
