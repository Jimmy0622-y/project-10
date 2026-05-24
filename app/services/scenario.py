import pandas as pd

class StockScenario:
    TRAIN_DAYS = 120  # 約 6 個月
    TEST_DAYS = 29  # 第 1 天是初始狀態，再往後 29 天完成 30 天模擬

    def __init__(self, df):
        self.df = df

    def rolling_windows(self, train_days=TRAIN_DAYS, test_days=TEST_DAYS, seed=None):
        import random

        df = self.df.reset_index(drop=True)

        max_start = len(df) - (train_days + test_days)
        if max_start <= 0:
            raise ValueError(f"資料長度不足：{len(df)}")

        # ✔ 改成可重現
        if seed is not None:
            random.seed(seed)

        start_idx = random.randint(0, max_start)

        train_df = df.iloc[start_idx : start_idx + train_days].copy()
        test_df = df.iloc[
            start_idx + train_days : start_idx + train_days + test_days
        ].copy()

        return RollingWindow(train_df, test_df)


class RollingWindow:
    def __init__(self, train_df, test_df):
        self.train_df = train_df.reset_index(drop=True)
        self.test_df = test_df.reset_index(drop=True)

        self.cursor = 0

        # ✔ 初始 state = train + test[0]
        self.history = self.train_df.copy()

    def current_state(self):
        return self.history

    def next(self):
        if self.cursor >= len(self.test_df):
            return None

        new_row = self.test_df.iloc[[self.cursor]]  # ⚠️ 重點：雙中括號

        self.history = pd.concat([self.history, new_row], ignore_index=True)

        self.cursor += 1
        return self.history
