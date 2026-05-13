# 產生6個月+1個月題目
class StockScenario:
    TRAIN_DAYS = 120  # 約 6 個月
    TEST_DAYS = 20  # 約 1 個月

    def __init__(self, df):
        self.df = df

        self.start_idx = None
        self.train = None
        self.test = None

    def split(self):
        import random

        max_start = len(self.df) - (self.TRAIN_DAYS + self.TEST_DAYS)

        self.start_idx = random.randint(0, max_start)

        self.train = self.df[self.start_idx : self.start_idx + self.TRAIN_DAYS]

        self.test = self.df[
            self.start_idx
            + self.TRAIN_DAYS : self.start_idx
            + self.TRAIN_DAYS
            + self.TEST_DAYS
        ]

        return self
