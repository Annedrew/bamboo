import pandas as pd
import numpy as np


class ForegroundImporter:
    def extend_matrix(self, extend_data: pd.DataFrame, emissions: list, fg_activities: list, bg_activities: list):
        """
        Concatenate foreground data to background data.
        
        Parameters:
            * extend_data: The user's input data include technosphere and biosphere data in dataframe format.
            * emissions: The list of emissions.
            * fg_activities: The list of foreground activities.
            * bg_activities: The list of background activities.
        """
        fgbg = np.zeros([len(fg_activities), len(bg_activities)])
        fgfg = np.zeros([len(fg_activities), len(fg_activities)])
        bgfg = np.zeros([len(bg_activities), len(fg_activities)])
        bifg = np.zeros([len(emissions), len(fg_activities)])

        for index, row in extend_data.iterrows():
            # check which column the exchange is in
            activity_name = row["Activity name"]
            column_count = fg_activities.index(activity_name)

            if row["Exchange type"] == "production":  # fgfg
                np.fill_diagonal(fgfg, 1)
                # TODO: add amount
            elif row["Exchange type"] == "technosphere": # bgfg
                row_count = bg_activities.index(row["Exchange name"])
                fgbg[row_count][column_count] = row["Exchange amount"]
            elif row["Exchange type"] == "biosphere": # bifg
                row_count = emissions.index(row["Exchnage name"])
                bifg[row_count][column_count] = row["Exchange amount"]

        return fgbg, fgfg, bgfg, bifg

    def concatenate_matrix(self, tech_matrix: pd.DataFrame, bio_matrix: pd.DataFrame, fgbg: np.ndarray, fgfg: np.ndarray, bgfg: np.ndarray, bifg: np.ndarray):
        tech_matrix = np.concatenate((np.concatenate((fgfg, fgbg), axis=0), np.concatenate((bgfg, tech_matrix), axis=0)), axis=1)
        bio_matrix = np.concatenate((bifg, bio_matrix), axis=1)

        return tech_matrix, bio_matrix
