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
            activity_name = row["Activity name"]
            column_num = fg_activities.index(activity_name)

            if row["Exchange type"] == "production":  # fgfg
                row_num = fg_activities.index(row["Exchange name"])
                fgfg[row_num][column_num] = row["Exchange amount"]
            elif row["Exchange type"] == "technosphere": # bgfg
                row_num = bg_activities.index(row["Exchange name"])
                bgfg[row_num][column_num] = row["Exchange amount"]
            elif row["Exchange type"] == "biosphere": # bifg
                row_num = emissions.index(row["Exchange name"])
                bifg[row_num][column_num] = row["Exchange amount"]

        fgfg = np.nan_to_num(fgfg, nan=0)
        bgfg = np.nan_to_num(bgfg, nan=0)
        bifg = np.nan_to_num(bifg, nan=0)

        return fgbg, fgfg, bgfg, bifg

    def concatenate_matrix(self, tech_matrix: pd.DataFrame, bio_matrix: pd.DataFrame, fgbg: np.ndarray, fgfg: np.ndarray, bgfg: np.ndarray, bifg: np.ndarray):
        tech_matrix = np.concatenate((np.concatenate((fgfg, bgfg), axis=0), np.concatenate((fgbg, tech_matrix), axis=0)), axis=1)
        bio_matrix = np.concatenate((bifg, bio_matrix), axis=1)

        return tech_matrix, bio_matrix
