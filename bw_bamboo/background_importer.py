import pandas as pd
import numpy as np
import bw2data as bd
from .utils import *


class BackgroundImporter:
    def form_tech_matrix(self, raw_tech: np.ndarray):
        """
        Get technosphere matrix data:
            Calculate (I-A), then convert it into a totally positive matrix.

        Parameters:
            * raw_tech: Raw data in pandas dataframe format.
        """
        identity_matrix = np.identity(len(raw_tech))
        tech_matrix = - (identity_matrix - raw_tech)
        np.fill_diagonal(tech_matrix, -tech_matrix.diagonal())
        
        if (tech_matrix < 0).any().any():
            raise ValueError("Transformation failed, negative values remain.")

        return tech_matrix

    def form_bio_matrix(self, bio_df, emissions) -> np.ndarray:
        """
        Get biosphere matrix data:
            Extract the corresponding value by emission name.
        
        Parameters:
            * bio_df: The whole EXIOBASE emissions in dataframe format.
            * emissions: The list of emissions used for LCA calculation.
        """
        bio_matrix = bio_df.loc[emissions].to_numpy()

        return bio_matrix

    def form_cf_matrix(self, ecoinvent_name, method: tuple, emission_file: str, emission_list: list) -> np.ndarray:
        """
        Get characterization factor matrix data.

        Parameters:
            * emission_file: The path to the file that needs to be processed. The file includes emission name and emission code column.
            * method: The method used for LCA calculation.
            * emission_list: the list of emissions in foreground system
        """
        # create a df mapping name to code.
        emission_df = pd.read_csv(emission_file, delimiter=",")
        emission_df = file_preprocessing(emission_file, ",", "exiobase name", emission_list)  # sorting the column order align with the desired order.
        codes = emission_df.iloc[:, -1].copy()  # by default, the last column is the 'code' column
        bg_name = emission_df.iloc[:, 0].copy()  # by default, the first column is the 'background emission name' column
        name_code = pd.concat([codes, bg_name], axis=1, ignore_index=True)
        name_code.columns = ["code", "name"]

        bw_method = bd.Method(method)
        method_data = bw_method.load() # method_data is a list of tuple

        if isinstance(method_data[0][0], list): # for ecoinvent 3.9, the first element of the tuple is a two element list
            method_df = pd.DataFrame(method_data, columns=["database_code", "cf_value"])
            method_df[["database", "code"]] = method_df["database_code"].to_list()
            cf_selected = method_df[method_df["code"].isin(codes)][["code", "cf_value"]].copy()
            missing_codes = list(set(codes.unique()) - set(cf_selected["code"]))

            df_merged = name_code.merge(cf_selected, on="code", how="left", suffixes=("_old", "_new"))
            matrix_values = df_merged["cf_value"]
            if missing_codes is not None:
                print(f"Characterization factor data imcomplete, missing: {missing_codes}")
            else:
                cf_matrix = np.diagflat(matrix_values.to_list())
        elif isinstance(method_data[0][0], int): # for ecoinvent 3.11, the first element of the tuple is an int value
            method_df = pd.DataFrame(method_data, columns=["id", "cf_value"])
            emissions = {}
            for code in codes:
                emission = bd.Database(ecoinvent_name).get(code)
                emissions[emission.id] = code  # create the mapping from id to code
            ids = list(emissions.keys())
            cf_selected = method_df[method_df["id"].isin(ids)][["id", "cf_value"]]
            missing_ids = set(ids) - set(cf_selected["id"])
            missing_codes = [emissions[key] for key in missing_ids if key in emissions]

            emissions = pd.DataFrame(list(emissions.items()), columns=["id", "code"])
            name_code_id = name_code.merge(emissions, on="code", how="left", suffixes=("_old", "_new"))
            df_merged = name_code_id.merge(cf_selected, on="id", how="left", suffixes=("_old", "_new"))
            matrix_values = df_merged["cf_value"]
            if missing_codes is not None:
                print(f"Characterization factor data imcomplete, missing: {missing_codes}")
            else:
                cf_matrix = np.diagflat(matrix_values.to_list())

        return cf_matrix if matrix_values is None else matrix_values

    # TODO: if it's functional unit, then try to find it and set it to 1
    def find_functional_unit(self, emission_code, missing_codes, cf_dict, codes):
        cf_matrix = []
        if missing_codes: # try to find co2
            miss_dict = emission_code[["ecoinvent name", "brightway code"]].set_index("brightway code")["ecoinvent name"].to_dict()
            fixed_codes = []
            for code in missing_codes:
                name = miss_dict.get(code)
                if "Carbon dioxide" in name:
                    cf_dict[code] = 1.0
                    fixed_codes.append(code)
            if missing_codes == fixed_codes:
                for code in codes:
                    cf_matrix.append(cf_dict.get(code))

        cf_matrix = np.diagflat(cf_matrix)

        if len(cf_matrix) != len(emission_code):
            raise ValueError(f"Characterization factor data imcomplete, missing: {missing_codes}")
            
        return cf_matrix
