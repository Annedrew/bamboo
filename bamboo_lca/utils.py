import bw_processing as bwp
import pandas as pd
import numpy as np


def get_country_sector(activity):
    """
    Design for EXIOBASE: Separate the country and sector.
    
    Parameters:
        * activity: The activity name that needs to be processed.
    """
    country, sector = activity.split("-", 1)

    return country, sector

def get_fg_activities(fg_file_path: str, delimiter: str) -> list:
    """
    Get all activities of foreground system.

    Parameters:
        * fg_file_path: The path to the file that needs to be processed.
        * delimiter: The separator of the file.
    """
    df = pd.read_csv(fg_file_path, decimal=delimiter)
    fg_activities = df["Activity name"].unique().tolist()

    return fg_activities

def get_bg_activities(a_file_path: str, delimiter: str) -> list:
    """
    Get all activities of EXIOBASE by combing <country_name> and <sector_name>.

    Parameters:
        * a_file_path: The path to the file that needs to be processed.
        * delimiter: The separator of the file.
    """
    df = pd.read_csv(a_file_path, delimiter=delimiter, header=None)
    countries = df.iloc[3:, 0].unique().tolist()
    sectors = df.iloc[3:, 1].unique().tolist()
    activities = [ x + '-' + y for x in countries for y in sectors]

    return activities

def file_preprocessing(file_name, delimiter: str, column_name: str, expacted_order: list):
    """
    Preprocess a file and return a DataFrame with the desired order.

    Parameters:
        * file_name: The path to the file that needs to be processed.
        * delimiter: The delimiter used in the file, for example: ','.
        * column_name: The column name of unexpected order.
        * expected_order: A list specifying the desired order of the rows in the DataFrame.
    """
    df = pd.read_csv(file_name, delimiter=delimiter)
    df_sorted = df.set_index(column_name).reindex(expacted_order).reset_index()

    return df_sorted

def map_pedigree_uncertainty(country_file, sector_file, region_sector_file):
    """
    Design for case study: Build dictionaries to mapping specific uncertainty.
    
    Parameters:
        * country_file: The file that group country to region.
        * sector_file: The file that group sector to aggregated sector.
        * region_sector_file: The mapping from aggregated region and sector to GSD. 
    """
    country_data = pd.read_csv(country_file, delimiter=";").fillna("").to_numpy()
    sector_data = pd.read_csv(sector_file, delimiter=";").fillna("").to_numpy()
    region_sector_data = pd.read_csv(region_sector_file, delimiter=";").fillna("").to_numpy()

    country_region = {row[0]: row[1] for row in country_data}
    sector_seccat = {row[0]: row[1] for row in sector_data}

    return country_region, sector_seccat, region_sector_data

def find_pedigree_uncertainty(activity, country_region, sector_seccat, region_sector_dfs):
    """
    Design for case study: Search for pedigree uncertainty for specific activity or biosphere flow.
    """
    country, sector = get_country_sector(activity)
    region_category =  country_region.get(country, None)
    sector_category = sector_seccat.get(sector, None)

    if region_category !=  None and sector_category != None:
        gsd = float(region_sector_dfs[(region_sector_dfs.iloc[:, 0] == region_category) & (region_sector_dfs.iloc[:, 1] == sector_category)]["GSD"].iloc[0])
    else:
        print("No GSD found.")
        gsd = None

    return gsd

def add_uncertainty(self, bw_data, bw_indices, bw_flip):
    """
    Design for case study: Add pedigree and specific uncertainty
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
                    if uncertainty == 0 or data == 0:
                        parameters_a = (0, data, np.NaN, np.NaN, np.NaN, np.NaN, False)
                    else:
                        loc = np.log(abs(data))
                        scale = np.log(uncertainty)
                        if not flip:
                            parameters_a = (0, data, np.NaN, np.NaN, np.NaN, np.NaN, False)
                        else:
                            parameters_a = (2, loc, scale, np.NaN, np.NaN, np.NaN, False)
                else:
                    if data == 0:
                        parameters_a = (0, data, np.NaN, np.NaN, np.NaN, np.NaN, False)
                    else:
                        loc = np.log(abs(data))
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
                    if uncertainty == 0 or data == 0:
                        parameters_a = (0, data, np.NaN, np.NaN, np.NaN, np.NaN, False)
                    else:
                        loc = np.log(abs(data))
                        scale = np.log(uncertainty)
                        parameters_a = (2, loc, scale, np.NaN, np.NaN, np.NaN, False)
                else:
                    if data == 0:
                        parameters_a = (0, data, np.NaN, np.NaN, np.NaN, np.NaN, False)
                    else:
                        loc = np.log(abs(data))
                        scale = np.log(uncertainty)
                        parameters_a = (2, loc, scale, np.NaN, np.NaN, np.NaN, False)
            else:
                parameters_a = (0, data, np.NaN, np.NaN, np.NaN, np.NaN, False)
            bw_uncertainties.append(parameters_a)

    return np.array(bw_uncertainties, dtype=bwp.UNCERTAINTY_DTYPE)