import pandas as pd
import numpy as np


class ForegroundImporter:
    # only for adding one column.
    def extend_matrix(self, original_matrix, extend_data: pd.DataFrame, names: list, is_technosphere=True):
        """
        Concatenage additional column and line to the matrix.
        
        Parameters:
            * original_matrix: The pure EXIOBASE matrix, after convert to brightway matrix format.
            * extend_data: The user's input data in dataframe format.
            * names: The list of activities or emissions that user needs to assign values.
            * is_technosphere: The default is to extend technosphere matrix. If it is False, then it extend biosphere matrix.
        """
        if is_technosphere:
            row = np.zeros([original_matrix.shape[1]]).reshape(1, -1)  # this has the same amont of activities as exiobase
            column = np.zeros([len(names)])  # this has the total amount of the whole foreground system
            for act, data in zip(extend_data.iloc[:, 0], extend_data.iloc[:, 1]):
                column[names.index(act)] = data
            column[0] = 1
            column = np.nan_to_num(column, nan=0)
            column = np.array([column]).T  # swap the rows and columns of an array.
            extended_matrix = np.concatenate((column, np.concatenate((row, original_matrix), axis=0)), axis=1)
        else:
            column = np.zeros([len(names)])
            for act, data in zip(extend_data.iloc[:, 0], extend_data.iloc[:, 1]):
                column[names.index(act)] = data
            column = np.nan_to_num(column, nan=0)
            column = np.array([column]).T
            extended_matrix = np.concatenate((column, original_matrix), axis=1)
        
        return extended_matrix
    
    # for adding more columns in a long format
    def extend_matrix(self, extend_data: pd.DataFrame, emissions: list, fg_activities: list, bg_activities: list):
        """
        Concatenage additional column and line to the matrix.
        
        Parameters:
            * extend_data: The user's input data include technosphere and biosphere data in dataframe format.
            * emissions: The list of emissions.
            * fg_activities: The list of foreground activities.
            * bg_activities: The list of background activities.
        """
        #INFO:  the names include the foreground activities

        # 1. background's foreground
        bgfg = np.zeros([len(fg_activities), len(bg_activities)])

        # 2. foredround's foreground
        fgfg = np.zeros([len(fg_activities), len(fg_activities)])

        # 3. foreground's background
        fgbg = np.zeros([len(bg_activities), len(fg_activities)])

        # 4. foreground's biosphere
        fgbi = np.zeros([len(emissions), len(fg_activities)])

        for index, row in extend_data.iterrows():
            # check which column the exchange is in
            activity_name = row["Activity name"]
            column_count = fg_activities.index(activity_name)

            if row["Exchange type"] == "production":  # fgfg
                np.fill_diagonal(fgfg, 1)
            elif row["Exchange type"] == "technosphere": # fgbg
                row_count = bg_activities.index(row["Exchange name"]) # I don't need to make the index the same as datapackage here, it will be handled this in the prepare datapackage process.
                fgbg[row_count][column_count] = row["Amount"]
            elif row["Exchange type"] == "biosphere": # fgbi
                row_count = emissions.index(row["Exchnage name"])
                fgbi[row_count][column_count] = row["Amount"]

        return bgfg, fgfg, fgbg, fgbi

    def concatenate_matrix(self, tech_matrix: pd.DataFrame, bio_matrix: pd.DataFrame, bgfg: np.ndarray, fgfg: np.ndarray, fgbg: np.ndarray, fgbi: np.ndarray):
        tech_matrix = np.concatenate((np.concatenate((fgfg, fgbg), axis=0), np.concatenate((bgfg, tech_matrix), axis=0)), axis=1)
        bio_matrix = np.concatenate((bio_matrix, tech_matrix), axis=1)

        return tech_matrix, bio_matrix
