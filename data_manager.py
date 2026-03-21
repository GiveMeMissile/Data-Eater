from fastparquet import write
import pandas as pd
import constants as c

class DataManager:
    def __init__(self, data, name="Placeholder_1"):
        data_dict = {"Data": data}
        self.data = pd.DataFrame(data_dict)
        self.name = name

    def save_to_csv(self):
        self.data.to_csv(c.CSV + "/" + self.name + ".csv")

    def save_to_parquet(self):
        self.data.to_parquet(c.PARQUET + "/" + self.name + ".parq", engine="fastparquet")

    def save_data(self, type):
        if type.lower() == "csv":
            self.save_to_csv()
            return
        elif type.lower() == "parquet":
            self.save_to_parquet()
            return
        else:
            print("Invalid file type, make sure to return a valid file type")