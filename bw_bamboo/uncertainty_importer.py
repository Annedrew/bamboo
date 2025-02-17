# TODO: 这个是多个列的
import pandas as pd
from .metadata_manager import * # TODO: 为什么不是这个？


class UncertaintyImporter:
    """
    The metadata updated in this class will be stored in metadata_manager
    """
    def __init__(self, file_path, delimiter):
        self.metadata = metadata_manager.get_metadata()
        self.file_path = file_path
        self.delimiter = delimiter
        self.df = None

    def _load_df(self):
        if self.df is None:
            self.df = pd.read_csv(self.file_path, delimiter=self.delimiter)

    def update_metadata_uncertainty(self, activities, strategy):  # TODO: What if they have the same name?
        self.update_metadata_activities(activities)

        self._load_df()
        column_names = self.df["Activity name"].unique()  # the column names of foreground system
        for col_name in column_names:
            self.update_metadata_column_uncertainty(col_name, self.df, activities, strategy)

    def update_metadata_activities(self, activities):
        """
        Import all foreground activity names, if foreground system has 2 columns, it will have 2 keys.
        """
        if not any("Activity name" in value for value in self.metadata.values()):
            for i in range(len(activities)):
                metadata_manager.update_metadata(i, {"Activity name": activities[i]})

    def update_metadata_column_uncertainty(self, act_name, df, activities, strategy):
        """
        Update metadata by "Activity name"
        """
        selected_df = df.loc[df["Activity name"] == act_name, ["Exchange name", "Exchange uncertainty type", "GSD", "Exchange negative"]]
        selected_dict = selected_df.set_index("Exchange name")[["Exchange uncertainty type", "GSD", "Exchange negative"]].to_dict(orient="index")

        if strategy == "itemwise":
            selected_df = selected_df.set_index("Exchange name")[["Exchange uncertainty type", "GSD", "Exchange negative"]]
            selected_df = selected_df.reindex(activities, fill_value=0)
            gsd_list = selected_df["GSD"].fillna(0).tolist()

            for key, value in self.metadata.items():
                activity_name = value["Activity name"]
                if activity_name in selected_dict:
                    self.metadata[key].update(selected_dict.get(activity_name, {}))
                    self.metadata[key]["specific"] = gsd_list
        elif strategy == "columnwise":
            for key, value in self.metadata.items():
                activity_name = value["Activity name"]
                if activity_name in selected_dict:
                    self.metadata[key].update(selected_dict.get(activity_name, {}))