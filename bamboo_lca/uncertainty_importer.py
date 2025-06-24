import pandas as pd
from .metadata_manager import *


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
        """
        Parameters:
            * strategy: "itemwise" or "columnwise"
        """
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
            selected_df_2 = selected_df.set_index("Exchange name")[["Exchange uncertainty type", "GSD", "Exchange negative"]]
            selected_df_2 = selected_df_2.reindex(activities, fill_value=0)
            gsd_list = selected_df_2["GSD"].astype(float).fillna(0).tolist()
            negative_list = selected_df_2["Exchange negative"].replace(0, False).astype(bool).fillna(False).tolist()
            for key, value in self.metadata.items():
                activity_name = value["Activity name"]
                if activity_name in selected_dict:
                    index = activities.index(act_name)
                    uncertainty_type = selected_df[selected_df["Exchange name"] == act_name]["Exchange uncertainty type"].to_list()[0]
                    self.metadata[index]["Activity uncertainty type"] = uncertainty_type
                    self.metadata[index]["Exchange uncertainty amount"] = gsd_list
                    self.metadata[index]["Exchange negative"] = negative_list
        elif strategy == "columnwise":
            for key, value in self.metadata.items():
                activity_name = value["Activity name"]
                if activity_name in selected_dict:
                    index = activities.index(act_name)
                    uncertainty_type = selected_df[selected_df["Exchange name"] == act_name]["Exchange uncertainty type"].to_list()[0]
                    self.metadata[index]["Activity uncertainty type"] = uncertainty_type
                    self.metadata[index]["Exchange uncertainty amount"] = selected_df[selected_df["Exchange name"] == act_name]["GSD"].to_list()[0]
                    self.metadata[index]["Exchange negative"] = selected_df[selected_df["Exchange name"] == act_name]["Exchange negative"].to_list()[0]
        else:
            print(F"Strategy {strategy} is not supported, you should either choose 'columnwise' or 'itemwise'")