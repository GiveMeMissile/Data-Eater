import pandas as pd
import constants as c
import sqlite3

class DataManager:
    def __init__(self, data, name="None"):
        data_dict = {"Data": data}
        self.data = pd.DataFrame(data_dict)
        self.name = name

    def save_to_csv(self):
        self.data.to_csv(c.CSV + "/" + self.name + ".csv")

    def save_to_parquet(self):
        self.data.to_parquet(c.PARQUET + "/" + self.name + ".parq", engine="fastparquet")

    def save_to_sqlite(self):
        conn = sqlite3.connect(c.SQLITE + "/" + self.name + ".db")
        self.data.to_sql(self.name, conn, index=False)
        conn.close()

    def save_to_jsonl(self):
        self.data.to_json(c.JSONL + "/" + self.name + ".jsonl", orient="records", lines=True)

    def save_data(self, type):
        if type.lower() == "csv":
            self.save_to_csv()
            return
        elif type.lower() == "parquet":
            self.save_to_parquet()
            return
        elif type.lower() == "sqlite":
            self.save_to_sqlite()
            return
        elif type.lower() == "jsonl":
            self.save_to_jsonl()
            return 
        else:
            print("Invalid file type, make sure to return a valid file type")