import talib

# Inputs
length = 10
multiplier = 3.0

# Pivot Points
pp = (high + low + close) / 3
r1 = 2 * pp - low
s1 = 2 * pp - high

# Supertrend
basis = (high + low) / 2
atr = talib.ATR(high, low, close, length)
upper = basis + (multiplier * atr)
lower = basis - (multiplier * atr)
uptrend = max(upper, high.shift(1))
dntrend = min(lower, low.shift(1))
trend = uptrend
trend.fillna(method='ffill', inplace=True)
trend = trend.shift(1).where(trend.shift(1) == uptrend, dntrend).where(close < trend.shift(1), dntrend)
