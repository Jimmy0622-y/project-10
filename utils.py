def generate_advice(stats):
    total = stats["total"]
    win_rate = stats["win_rate"]
    profit_ratio = stats["profit_ratio"]

    if total == 0:
        return "尚未有交易資料"

    if win_rate > 60 and profit_ratio != float('inf') and profit_ratio > 1.5:
        return "策略良好（MA多頭策略有效），可以考慮實際投資"
    elif win_rate > 50:
        return "策略普通，建議調整MA參數（例如5/20改10/30）"
    else:
        return "策略風險高，建議不要使用此MA策略"