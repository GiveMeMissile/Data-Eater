from fastparquet import write
import pandas as pd
import constants as c

class DataManager:
    def __init__(self, data, name="Placeholder_0"):
        data_dict = {"Data": data}
        self.data = pd.DataFrame(data_dict)
        self.name = name

    def save_to_csv(self):
        self.data.to_csv(c.CSV + "/" + self.name + ".csv")

    def save_to_parquet(self):
        self.data.to_parquet(c.PARQUET + "/" + self.name + ".parq", engine="fastparquet")