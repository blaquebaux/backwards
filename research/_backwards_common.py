#!/usr/bin/python3
# =============================================================================
# _backwards_common.py — shared helpers for Blaque Baux BACKWARDS (risk-managed / vol-scaled momentum).
# Alpaca SIP daily bars (adjustment=all → total return); reads ALPACA_KEY_ID / ALPACA_SECRET_KEY. Read-only.
#
# BACKWARDS is a REVERSE TEST, not a hunt for a new signal. The corpus already carries momentum (boom, beyond) and
# has marked momentum's CRASH risk red. The literature (Barroso–Santa-Clara, Daniel–Moskowitz) claims a specific
# cure: scale the momentum book by the inverse of its own recent volatility — because momentum's vol SPIKES right
# before it crashes (the short leg behaves like a short call). The sharp, falsifiable part of the claim is that
# this helps MOMENTUM SPECIFICALLY and has no systematic benefit for non-momentum strategies. So we build a clean
# cross-sectional multi-asset momentum factor, vol-scale it, AND vol-scale non-momentum controls (the market, a
# short-term reversal book) the same way — and see whether the skew/drawdown repair is momentum-specific or generic.
# HONEST LIMIT: Alpaca starts 2016, so the canonical 2009 momentum crash is OUT of sample; the in-window stress is
# the 2020-21 value rotations and the Jan-2021 squeeze. The measured crash (and thus the cure) is milder than history.
# =============================================================================
import os, json, urllib.request, math
import numpy as np

H = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"], "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET_KEY"]}
START, END = "2016-01-01", "2026-08-01"
_cache = {}

def bars(s):
    if s in _cache: return _cache[s]
    u = (f"https://data.alpaca.markets/v2/stocks/bars?symbols={s}&timeframe=1Day"
         f"&start={START}&end={END}&adjustment=all&feed=sip&limit=10000")
    try:
        d = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=40))
        _cache[s] = {b["t"][:10]: b["c"] for b in d.get("bars", {}).get(s, [])}
    except Exception:
        _cache[s] = {}
    return _cache[s]

def panel(syms):
    D = {s: bars(s) for s in syms}; D = {s: v for s, v in D.items() if len(v) > 250}
    if not D: return {}, []
    u = list(D); dates = sorted(set.intersection(*[set(D[s]) for s in u]))
    return {s: np.array([D[s][d] for d in dates], float) for s in u}, dates

def rets(px): return px[1:] / px[:-1] - 1

def stats(r):
    r = np.asarray(r, float); r = r[np.isfinite(r)]
    if len(r) < 30 or r.std() == 0: return dict(sh=float('nan'), cagr=float('nan'), dd=float('nan'), vol=float('nan'))
    cum = np.cumprod(1 + r)
    return dict(sh=r.mean()/r.std()*math.sqrt(252), cagr=cum[-1]**(252/len(r))-1,
                dd=(cum/np.maximum.accumulate(cum)-1).min(), vol=r.std()*math.sqrt(252))

def skew_of(r):
    r = np.asarray(r, float); r = r[np.isfinite(r)]
    if len(r) < 30 or r.std() == 0: return float('nan')
    z = (r - r.mean())/r.std(); return float(np.mean(z**3))

def vol_scale(r, target=0.10, win=126, cap=3.0):
    """Barroso-style risk management: lever each day by target/ (trailing realized vol), capped. CAUSAL — the
    leverage at t uses only returns strictly before t. Returns the scaled daily series (aligned to r[win:])."""
    r = np.asarray(r, float); out = []
    for t in range(win, len(r)):
        rv = r[t-win:t].std() * math.sqrt(252)
        lev = min(cap, target / rv) if rv > 0 else 0.0
        out.append(lev * r[t])
    return np.array(out)

def to_vol(r, target=0.10):
    """Constant rescale to a common ex-post annualized vol, so maxDD / CAGR compare at an equal risk budget
    (Sharpe and skew are already scale-free; this only makes the drawdown columns apples-to-apples)."""
    r = np.asarray(r, float); v = r.std() * math.sqrt(252)
    return r * (target / v) if v > 0 else r
