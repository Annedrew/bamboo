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

    def form_cf_matrix(self, emission_file: str, method: tuple, emission_list: list) -> np.ndarray:
        """
        Get characterization factor matrix data.

        Parameters:
            * emission_file: The path to the file that needs to be processed. The file includes emission name and emission code column.
            * method: The method used for LCA calculation.
        """
        emission_code = pd.read_csv(emission_file, delimiter=",")
        emission_code = file_preprocessing(emission_file, ",", "exiobase name", emission_list)  # sorting the column order align with the desired order.

        codes = emission_code.iloc[:, -1]
        bw_method = bd.Method(method)
        method_df = pd.DataFrame(bw_method.load(), columns=["database_code", "cf_number"])
        method_df[["database", "code"]] = method_df["database_code"].to_list()
        cf_selected = method_df[method_df["code"].isin(codes)][["code", "cf_number"]]
        cf_dict = cf_selected.set_index("code")["cf_number"].to_dict()
        missing_codes = list(set(codes.unique()) - set(cf_selected["code"]))
        
        cf_matrix = []
        if not missing_codes:
            for code in codes:
                cf_matrix.append(cf_dict.get(code))
        else:
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
