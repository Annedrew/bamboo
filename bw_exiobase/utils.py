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

def get_activities(self, a_file_path: str, delimiter: str) -> list:
    """
    Get all activities by combing <country_name> and <sector_name>.
    """
    df = pd.read_csv(a_file_path, delimiter=delimiter, header=None, low_memory=False)
    countries = df.iloc[3:, 0].unique().tolist()
    sectors = df.iloc[3:, 1].unique().tolist()
    activities = [ x + '-' + y for x in countries for y in sectors]

    return activities

def file_preprocessing(self, file_name, delimiter: str, column_name: str, expacted_order: list):
    """
    Preprocess a file and return a DataFrame with the desired order.
    """
    df = pd.read_csv(file_name, delimiter=delimiter)
    df_sorted = df.set_index(column_name).reindex(expacted_order).reset_index()

    return df_sorted
