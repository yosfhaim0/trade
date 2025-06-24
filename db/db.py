import os
import csv
import pandas as pd
from typing import List, Dict, Optional



DATA_DIR=r'C:\Users\hoday\PyCharmMiscProject\db\data'
COllETIONS=['stocks_with_options','nasdaq_stocks']
class SimpleCSVDatabase:
    def __init__(self, data_dir: str, collections: Optional[List[str]] = None):
        self.data_dir = data_dir
        self.collections = collections or []
        self.db = {}  # {collection_name: DataFrame}

        self._load_all_collections()




    def _load_all_collections(self):
        for name in self.collections:
            path = os.path.join(self.data_dir, f"{name}.csv")
            if os.path.exists(path):
                self.db[name] = pd.read_csv(path)
            else:
                self.db[name] = pd.DataFrame()

    def get(self, collection_name: str) -> pd.DataFrame:
        if collection_name not in self.db:
            raise ValueError(f"Collection '{collection_name}' not found.")
        return self.db[collection_name]

    def update(self, collection_name: str, data: List[Dict]):
        df = pd.DataFrame(data)
        self.db[collection_name] = df
        self._save(collection_name)

    def append(self, collection_name: str, row: Dict):
        if collection_name not in self.db:
            self.db[collection_name] = pd.DataFrame([row])
        else:
            self.db[collection_name] = pd.concat(
                [self.db[collection_name], pd.DataFrame([row])],
                ignore_index=True
            )
        self._save(collection_name)

    def _save(self, collection_name: str):
        path = os.path.join(self.data_dir, f"{collection_name}.csv")
        self.db[collection_name].to_csv(path, index=False)

    def list_collections(self) -> List[str]:
        return list(self.db.keys())

    def refresh(self):
        self._load_all_collections()
db=SimpleCSVDatabase(DATA_DIR,COllETIONS)
stocks_with_options=db.get('stocks_with_options')
stocks_with_options=stocks_with_options['Symbol'].dropna().unique().tolist()
pass