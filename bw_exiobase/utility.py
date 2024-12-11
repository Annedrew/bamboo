import bw_processing as bwp
import bw2calc as bc
from scipy import sparse
import pandas as pd
import numpy as np
from random import sample
import os
import matplotlib.pyplot as plt
import seaborn as sb
from matplotlib.ticker import FuncFormatter
import textwrap
import re
import bw2data as bd
from typing import List, Tuple, Any


class SimulationScript:
    def __init__(self):
        """
        * self.metadata: save technosphere data, including column index and gsd
        """
        self.metadata = []

    def file_preprocessing(self, file_name: str, delimiter: str, column_name: str, expected_order: list) -> pd.DataFrame:
        """
        Preprocess a file and return a DataFrame with the desired order.

        Parameters:
            * file_name: The path to the file that needs to be processed.
            * delimiter: The delimiter used in the file, for example: ','.
            * column_name: The column name of unexpected order.
            * expected_order: A list specifying the desired order of the rows in the DataFrame.
        """
        df = pd.read_csv(file_name, delimiter=delimiter)
        df_sorted = df.set_index(column_name).reindex(expected_order).reset_index()

        return df_sorted

    def get_index(self, activities: list, activity_name: str) -> int:
        """
        Get corresponding index for an activity.

        Parameters:
            * activities: The list of all activities.
            * activity_name: The name of the activity to be queried.
        """
        index = activities.index(activity_name)
        return index
    
    def form_tech_matrix(self, raw_tech: pd.DataFrame):
        """
        Convert the raw data to brightway data matrix.

        Parameters:
            * raw_tech: Raw data in pandas dataframe format.
        """
        identity_matrix = np.identity(len(raw_tech))
        tech_matrix = - (identity_matrix - raw_tech)
        np.fill_diagonal(tech_matrix, -tech_matrix.diagonal())

        return tech_matrix

    def extend_matrix(self, original_matrix: np.ndarray, extend_data: pd.DataFrame, names: list, is_technosphere=True):
        """
        Concatenage additional column and line to the matrix.
        
        Parameters:
            * original_matrix: The pure EXIOBASE matrix, after convert to brightway matrix format.
            * extend_data: The user's input data in dataframe format.
            * names: The list of activities or emissions that user needs to assign values.
            * is_technosphere: The default is to extend technosphere matrix. If it is False, then it extend biosphere matrix.
        """
        if is_technosphere:
            row = np.zeros([original_matrix.shape[1]]).reshape(1, -1)
            column = np.zeros([original_matrix.shape[0]])
            # TODO: match activities by index and then assign the amount.
            for act, data in zip(extend_data.iloc[:, 0], extend_data.iloc[:, 1]):
                column[self.get_index(names, act)] = data
            column = np.nan_to_num(column, nan=0)
            column = np.insert(column, 0, 1)
            column = np.array([column]).T
            extended_matrix = np.concatenate((column, np.concatenate((row, original_matrix), axis=0)), axis=1)
        else:
            column = np.zeros([original_matrix.shape[0]]).reshape(1, -1).T
            # TODO: assign values to biosphere emissions from user's input.
            extended_matrix = np.concatenate((column, original_matrix), axis=1)

        # TODO: print size before and after extension.

        return extended_matrix
    
    def add_multifunctionality_flip(self, extend_data, flip_column, dp_flip, dp_indices):
        """
        Add flip sign for multifunctionality foreground system.
        """
        for flip, indices in zip(dp_flip, dp_indices):
            if indices[1] == 0:
                if extend_data[[flip_column]][indices[0]] == True:
                    dp_flip[indices[0]] = True

        return dp_flip
    
    def add_multifunctionality_negative(self, extend_data, negative_column, dp_uncertainty, dp_indices):
        """
        Add uncertainty negative for multifunctionality foreground system.
        """
        for uncertainty, indices in zip(dp_uncertainty, dp_indices):
            if indices[1] == 0:
                if extend_data[[negative_column]][indices[0]] == True:
                    dp_uncertainty[indices[0]][-1] = True

        return dp_uncertainty

    def form_bio_matrix(self, bio_df: pd.DataFrame, emissions: list) -> np.ndarray:
        """
        Get biosphere matrix data.
        
        Parameters:
            * bio_df: The whole EXIOBASE emissions in dataframe format.
            * emissions: The list of emissions used for LCA calculation.
        """
        bio_matrix = bio_df.loc[emissions].to_numpy()

        return bio_matrix
    
    # ATTENTION: have to make sure the file has the same order as biosphere emissions.
    def form_cf_matrix(self, emission_file: str, method: tuple) -> pd.DataFrame:
        """
        Get characterization factor matrix data.

        Parameters:
            * emission_file: The path to the file that needs to be processed.
            * method: The method used for LCA calculation.
        """
        emission_code = pd.read_csv(emission_file, delimiter=",") 
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
            if missing_codes != fixed_codes:
                print(f"CF data imcomplete, missing: {missing_codes}")
            else:
                for code in codes:
                    cf_matrix.append(cf_dict.get(code))

        cf_matrix = np.diagflat(cf_matrix)
            
        return cf_matrix

    def get_country_sector(self, activity: str):
        """
        Separate the country and sector.
        
        Parameters:
            * activity: The activity name that needs to be processed.
        """
        country, sector = activity.split("-", 1)

        return country, sector

    def map_pedigree_uncertainty(self, country_file: str, sector_file: str, region_sector_file: str):
        """
        Build dictionaries to mapping specific uncertainty.
        
        Parameters:
            * country_file: The file that group country to region.
            * sector_file: The file that group sector to aggregated sector.
            * region_sector_file: The mapping from aggregated region and sector to GSD. 
        """
        country_dfs = pd.read_csv(country_file, delimiter=";")
        sector_dfs = pd.read_csv(sector_file, delimiter=";")
        region_sector_dfs = pd.read_csv(region_sector_file, delimiter=";")

        country_region = country_dfs.set_index(country_dfs.columns[0])[country_dfs.columns[1]].to_dict()
        sector_seccat = sector_dfs.set_index(sector_dfs.columns[0])[sector_dfs.columns[1]].to_dict()

        return country_region, sector_seccat, region_sector_dfs

    def find_pedigree_uncertainty(self, activity: str, country_region: pd.DataFrame, sector_seccat: pd.DataFrame, region_sector_dfs: pd.DataFrame):
        """
        Search for uncertainty for specific activity or biosphere flow.
        """
        country, sector = self.get_country_sector(activity)
        region_category =  country_region.get(country, None)
        sector_category = sector_seccat.get(sector, None)

        if region_category !=  None and sector_category != None:
            gsd = float(region_sector_dfs[(region_sector_dfs.iloc[:, 0] == region_category) & (region_sector_dfs.iloc[:, 1] == sector_category)]["GSD"].iloc[0])
        else:
            # print("No GSD found.")
            gsd = None

        return gsd
    
    def calc_specific_uncertainty(self, data: float, uncertainty: float):
        loc = np.log(data)
        scale = np.log(uncertainty)

        return loc, scale
    
    # TODO: design for pedigree and one column uncertainty
    # TODO: False align with the one from csv file.
    def add_uncertainty(self, bw_data, bw_indices, bw_flip):
        """
        Add uncertainty to the needed matrix.
        """
        bw_uncertainties = []
        if bw_flip is not None: # technosphere
            k = 0
            for data, indices, flip in zip(bw_data, bw_indices, bw_flip):
                uncertainty = list(self.metadata[indices[1]].items())[0][1][1]
                if uncertainty is not None:
                    if indices[1] == 0:
                        uncertainty = uncertainty[k]
                        k += 1
                        if uncertainty == 0:
                            parameters_a = (0, data, np.NaN, np.NaN, np.NaN, np.NaN, False)
                        else:
                            loc = np.log(data)
                            scale = np.log(uncertainty)
                            if not flip:
                                parameters_a = (0, data, np.NaN, np.NaN, np.NaN, np.NaN, False)
                            else:
                                parameters_a = (2, loc, scale, np.NaN, np.NaN, np.NaN, False)
                    else:
                        loc = np.log(data)
                        scale = np.log(uncertainty)
                        if not flip:
                            parameters_a = (0, data, np.NaN, np.NaN, np.NaN, np.NaN, False)
                        else:
                            parameters_a = (2, loc, scale, np.NaN, np.NaN, np.NaN, False)
                else:
                    parameters_a = (0, data, np.NaN, np.NaN, np.NaN, np.NaN, False)
                bw_uncertainties.append(parameters_a)
        else:
            k = 0
            for data, indices in zip(bw_data, bw_indices):
                uncertainty = list(self.metadata[indices[1]].items())[0][1][1]
                if uncertainty is not None:
                    if indices[1] == 0:
                        uncertainty = uncertainty[k]
                        k += 1
                        if uncertainty == 0:
                            parameters_a = (0, data, np.NaN, np.NaN, np.NaN, np.NaN, False)
                        else:
                            loc = np.log(data)
                            scale = np.log(uncertainty)
                            parameters_a = (2, loc, scale, np.NaN, np.NaN, np.NaN, False)
                    else:
                        loc = np.log(data)
                        scale = np.log(uncertainty)
                        parameters_a = (2, loc, scale, np.NaN, np.NaN, np.NaN, False)
                else:
                    parameters_a = (0, data, np.NaN, np.NaN, np.NaN, np.NaN, False)
                bw_uncertainties.append(parameters_a)

        return np.array(bw_uncertainties, dtype=bwp.UNCERTAINTY_DTYPE)
    
    def prepare_bw_matrix(self, tech_matrix, bio_matrix, cf_matrix, activities):
        """
        Transform matrices data to bw matrices data, ready for the datapackages.
        """
        tech_sparse = sparse.coo_array(tech_matrix)
        tech_coors = np.column_stack(tech_sparse.nonzero())
        
        max_coor = tech_coors[np.argmax(np.sum(tech_coors, axis=1))]
        tech_data = tech_sparse.data
        tech_indices = np.array([tuple(coor) for coor in tech_coors], dtype=bwp.INDICES_DTYPE)
        tech_flip = np.array([False if i[0] == i[1] else True for i in tech_indices])

        bio_sparse = sparse.coo_array(bio_matrix)
        bio_coors = np.column_stack(bio_sparse.nonzero())
        bio_data = bio_sparse.data
        bio_indices = np.array([tuple([coord[0] + max_coor[0] + 1, coord[1]]) for coord in bio_coors], dtype=bwp.INDICES_DTYPE)
        
        cf_sparse = sparse.coo_array(cf_matrix)
        cf_coors = np.column_stack(cf_sparse.nonzero())
        cf_data =  cf_sparse.data
        cf_indices = np.array([tuple([coord[0] + max_coor[0] + 1, coord[1] + max_coor[1] + 1]) for coord in cf_coors], dtype=bwp.INDICES_DTYPE)

        tech_poss = list(set(coord[1] for coord in tech_indices))
        for act, tech_pos in zip(activities, tech_poss):
            self.metadata.append({tech_pos: act})

        return [
            (tech_data, tech_indices, tech_flip),
            (bio_data, bio_indices),
            (cf_data, cf_indices)
        ]

    # TODO: uncertainty is None currently
    def prepare_datapackage(self, datapackage_data: List[Tuple[Any, ...]], uncertainty=None):
        """
        Prepare datapackage for brightway LCA calculation.

        Parameters:
            * datapackage_data: A list of tuple includes all information to create a datapackage.
            * uncertainty: The uncertainty for all matrices.
        """
        tech_data, tech_indices, tech_flip = datapackage_data[0]
        bio_data, bio_indices = datapackage_data[1]
        cf_data, cf_indices = datapackage_data[2]
        tech_uncertainty, bio_uncertainty, cf_uncerainty = uncertainty[0], uncertainty[1], uncertainty[2]

        dp = bwp.create_datapackage()
        dp.add_persistent_vector(
            matrix='technosphere_matrix',
            indices_array=tech_indices,
            data_array=tech_data,
            flip_array=tech_flip,
            distributions_array=tech_uncertainty,
        )
        dp.add_persistent_vector(
            matrix='biosphere_matrix',
            indices_array=bio_indices,
            data_array=bio_data,
            distributions_array=bio_uncertainty,
        )
        dp.add_persistent_vector(
            matrix='characterization_matrix',
            indices_array=cf_indices,
            data_array=cf_data,
            distributions_array=cf_uncerainty,
        )

        return dp

    def perform_simulation(self, index, datapackage):
        """
        Calculate LCA score in brightway.

        Parameters:
            * index: The index of functional unit.
            * datapackage: The datapackage for brightway LCA calculation.
        """
        lca = bc.LCA(
            demand={index: 1},
            data_objs=[datapackage],
        )
        lca.lci()
        lca.lcia()

        return lca.score

    def manual_lca(self, A, B, C, index):
        """
        Calculate LCA score manually for comparison.

        Parameters:
            * A: Raw EXIOBASE matrix
            * B: Biosphere matrix
            * C: Characterization factor matrix
            * index: The index of functional unit.
        """
        f = np.zeros(len(A))
        f[index] = 1
        lca_score = np.sum(C.dot(B.dot((np.linalg.inv(np.identity(len(A))-A)).dot(f))))

        return lca_score