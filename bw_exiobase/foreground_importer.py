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


class ForegroundImporter:
    # only for adding one column.
    def extend_matrix(self, original_matrix, extend_data: pd.DataFrame, names: list, is_technosphere=True):
        """
        Concatenage additional column and line to the matrix.
        * names: 
            - For technosphere, this is the list of activities which include all activities for the whole foreground system.
            - For biosphere, this is the list of emissions.
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