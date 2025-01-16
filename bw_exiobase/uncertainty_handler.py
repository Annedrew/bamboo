import bw_processing as bwp
import pandas as pd
import numpy as np


class UncertaintyHandler:
    def __init__(self):
        """
        self.metadata: save technosphere data, including column index and gsd

        metadata:
        [{index: (act, [specific1, specific2, specific3, ...]])}, {index: (act, gsd)}, {index: (act, gsd)}]
        """
        self.metadata = []
        
    def get_country_sector(self, activity):
        """
        Separate the country and sector.
        
        Parameters:
            * activity: The activity name that needs to be processed.
        """
        country, sector = activity.split("-", 1)

        return country, sector

    def map_pedigree_uncertainty(self, country_file, sector_file, region_sector_file):
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

    def find_pedigree_uncertainty(self, activity, country_region, sector_seccat, region_sector_dfs):
        """
        Search for uncertainty for specific activity or biosphere flow.
        """
        country, sector = self.get_country_sector(activity)
        region_category =  country_region.get(country, None)
        sector_category = sector_seccat.get(sector, None)

        if region_category !=  None and sector_category != None:
            gsd = float(region_sector_dfs[(region_sector_dfs.iloc[:, 0] == region_category) & (region_sector_dfs.iloc[:, 1] == sector_category)]["GSD"].iloc[0])
        else:
            print("No GSD found.")
            gsd = None

        return gsd

    def calc_specific_uncertainty(self, data, uncertainty):
        loc = np.log(data)
        scale = np.log(uncertainty)

        return loc, scale

    # TODO: design for pedigree and specific uncertainty
    def add_uncertainty(self, bw_data, bw_indices, bw_flip):
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