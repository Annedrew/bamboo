import pandas as pd
import numpy as np
import bw2data as bd
from .utils import *


class BackgroundImporter:
    def build_tech_matrix(self, raw_tech: np.ndarray):
        """
        Get technosphere matrix data:
            Calculate (I-A), then convert it into a totally positive matrix.

        Parameters:
            * raw_tech: Raw data in pandas dataframe format.

        Returns: 
            * np.ndarray: Return the numpy matrix format technosphere.
        """
        identity_matrix = np.identity(len(raw_tech))
        tech_matrix = - (identity_matrix - raw_tech)
        np.fill_diagonal(tech_matrix, -tech_matrix.diagonal())

        return tech_matrix

    def build_bio_matrix(self, bio_df, emissions) -> np.ndarray:
        """
        Get biosphere matrix data:
            Extract the corresponding value by emission name.
        
        Parameters:
            * bio_df: The whole EXIOBASE emissions in dataframe format.
            * emissions: The list of emissions used for LCA calculation.

        Returns: 
            * np.ndarray: Return the numpy matrix format biosphere.
        """
        bio_matrix = bio_df.loc[emissions].to_numpy()

        return bio_matrix

    def get_from_cfs(self, emission_df):
        """
        Get the characterization factor values (type: list) from characterization factor file in dataframe format.

        Parameters:
            * emission_df: The dataframe format of characterization factor file, provide characterization factor matrix raw data.
            
        Returns:
            * list: Return the cf values as a list.
        """
        column_name = "cf value"
        if column_name not in emission_df.columns:
            print("The file doesn't have a 'cf values' column. Please add your characterization factor values to the 'cf values' column.")
        else:
            cf_df = emission_df[column_name]
            if not cf_df.isnull().any():
                print("All characterization factors have been found.")
                return cf_df.to_list()
            else:
                emission_names = emission_df["exiobase name"].to_list()
                emission_values = emission_df[column_name].to_list()
                cf_missing = emission_df[emission_df[column_name].isnull()]["exiobase name"].to_list()
                
                print(f"{cf_missing} emission(s) don't have characterization factor values. Please complete your 'cf values' column.")
                # print the founded cf values
                # print(f"Emissions: \n{emission_names}")
                # print(f"Characteriation factor values: \n{emission_values}")

        return None

    def get_from_code(self, emission_df, method, ecoinvent_name):
        """
        Get the characterization factor values (type: list) through brightway by code.

        Parameters:
            * emission_df: The dataframe format of characterization factor file, provide characterization factor matrix raw data.
            * method: The selected method used for LCA calculation.
            * ecoinvent_name: The name of the ecoinvent database on user's device.

        Returns:
            * list | None: A list of characterization factor (cf) values if found, otherwise None.
        """

        emission_codes = emission_df["brightway code"].copy()  # TODO: should I call it code, or brightway code, it's not from brightway in the new ecoinvent version.
        emission_names = emission_df["exiobase name"].copy()  # TODO: how can we do that, should we define the name or the position of the name.
        code_name = pd.concat([emission_codes, emission_names], axis=1, ignore_index=True)
        code_name.columns = ["code", "name"]

        bw_method = bd.Method(method)
        method_data = bw_method.load() # method_data is a list of tuple

        if isinstance(method_data[0][0], list): # for ecoinvent 3.9, the first element of the tuple is a two element list
            method_df = pd.DataFrame(method_data, columns=["database_code", "cf_value"])
            method_df[["database", "code"]] = method_df["database_code"].to_list()
            cf_selected = method_df[method_df["code"].isin(emission_codes)][["code", "cf_value"]].copy()
            missing_codes = list(set(emission_codes.unique()) - set(cf_selected["code"]))

            code_name_cf_value = code_name.merge(cf_selected, on="code", how="left", suffixes=("_old", "_new"))
            cf_values = code_name_cf_value["cf_value"]
            if missing_codes:
                emission_names = []
                for missing_code in missing_codes:
                    emission_names.append(emission_df[emission_df["brightway code"] == missing_code]["exiobase name"].to_list()[0])
                print(f"Characterization factor data incomplete, missing: {list(zip(emission_names, missing_codes))}")
            else:
                print("All characterization factors have been found.")
                return cf_values.to_list()
        elif isinstance(method_data[0][0], int): # for ecoinvent 3.11, the first element of the tuple is an int value
            method_df = pd.DataFrame(method_data, columns=["id", "cf_value"])
            emissions = {}
            for code in emission_codes:
                emission = bd.Database(ecoinvent_name).get(code)
                emissions[emission.id] = code  # create the mapping from id to code
            ids = list(emissions.keys())
            cf_selected = method_df[method_df["id"].isin(ids)][["id", "cf_value"]]
            missing_ids = set(ids) - set(cf_selected["id"].to_list())
            missing_codes = [emissions[key] for key in missing_ids if key in emissions]
            emissions = pd.DataFrame(list(emissions.items()), columns=["id", "code"])

            name_code_id = code_name.merge(emissions, how="left", on="code", suffixes=("_old", "_new"))
            df_merged = name_code_id.merge(cf_selected, how="left", on="id", suffixes=("_old", "_new"))
            matrix_values = df_merged["cf_value"]
            if missing_codes:
                emission_names = []
                for missing_code in missing_codes:
                    emission_names.append(emission_df[emission_df["brightway code"] == missing_code]["exiobase name"].to_list()[0])
                print(f"Characterization factor data incomplete, missing: {list(zip(emission_names, missing_codes))}")
            else:
                print("All characterization factors have been found.")
                return matrix_values.to_list()
        
        return None

    def build_cf_matrix(self, emission_file: str, emission_list: list, ecoinvent_name: str = None, method: tuple = None, source="cf") -> np.ndarray: # TODO: should here called ecoinvent_name or database_name? I wonder is there any other database.
        """
        Get characterization factor matrix data.

        Parameters: 
            * emission_file: The path to the file that needs to be processed. The file includes emission name and emission code column.
            * emission_list: the list of emissions in foreground system
            * ecoinvent_name: The name of the ecoinvent biosphere database on user's device.
            * method: The method used for LCA calculation.
            * source: define the data source, two options: "cf" or "code". Set to "cf", the function extract cf values from "cf value" column of the file, set to "code", the function extract cf values from "brightway code" column of the file.

        Returns: 
            * np.ndarray | None: Return the numpy matrix format of characterization factor (cf) values if found, otherwise None.
        """
        emission_df = pd.read_csv(emission_file, delimiter=",")
        emission_df = file_preprocessing(emission_file, ",", "exiobase name", emission_list)  # sorting the column order align with the desired order.
        
        if source == "cf":
            cf_values = self.get_from_cfs(emission_df)
            if cf_values:
                cf_matrix = np.diagflat(cf_values)
                return cf_matrix
            else:
                print("Failed to build matrix, there are cf values not found.")
        elif source == "code":
            cf_values = self.get_from_code(emission_df, method, ecoinvent_name)
            if cf_values:
                cf_matrix = np.diagflat(cf_values)
                return cf_matrix
            else:
                print("Failed to build matrix, there are cf values not found.")
        else:
            print('Please set the source to either "cf" or "code".')
            
        return None
    
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
            raise ValueError(f"Characterization factor data incomplete, missing: {missing_codes}")
            
        return cf_matrix