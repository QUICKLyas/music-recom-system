import pandas as pd
import numpy as np


class TUPandas (object):
    def __init__(self, datas, tags, users) -> None:
        self.data = datas
        self.items = tags
        self.users = users
        self.df = pd.DataFrame(
            self.data, columns=self.users, index=self.items)
        pd.set_option('display.unicode.ambiguous_as_wide', True)
        pd.set_option('display.unicode.east_asian_width', True)
        pass

    def computeRateofTag(self):
        data = self.df
        # print(self.df[self.df.columns[0]].sum())
        data['rate'] = (self.df[self.df.columns[1]] /
                        self.df[self.df.columns[1]].sum())
        self.df = self.formatRateforTag(data=data)
        return

    def formatRateforTag(self, data):
        data = data.sort_values('rate', ascending=False, kind='mergesort')
        data['rate'] = data['rate'].apply(lambda x: format(x, '.2%'))
        return data
