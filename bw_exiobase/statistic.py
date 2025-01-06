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


class Statistic:
    def sort_file(self, filename):
        """
        Sort files in a folder when file name has both string and number.
        """
        match = re.search(r'CASE_(\d+)_', filename)
        if match:
            return int(match.group(1))
        else:
            return float('inf')

    def concate_files(self, folder_path):
        """
        Merge all columns from all files in a folder(exis=0).
        """
        data = pd.DataFrame()
        sorted_files = sorted(os.listdir(folder_path), key=self.sort_file)
        for file in sorted_files:
            if "CASE" in file:
                file_path = os.path.join(folder_path, file)
                df = pd.read_csv(file_path)
                old_column_name = "kg CO2eq"
                df.rename(columns={old_column_name: os.path.splitext(file)[0]}, inplace=True)
                data = pd.concat([data, df], axis=1)
            data.to_csv(f"{folder_path}/all_results.csv", index=False)

    def collect_data(self, folder_path, database_type):
        """
        Merge all columns from all files in a folder(axis=1), ready for plot drawing.
        Note: This function is used when you have a folder hierarchy.
        """
        data = pd.DataFrame()
        sorted_folders = sorted(os.listdir(folder_path), key=self.sort_file)
        for folder in sorted_folders:
            if database_type in folder:
                path = os.path.join(folder_path, folder)
                sorted_files = sorted(os.listdir(path), key=self.sort_file)
                for file in sorted_files:
                    if file.endswith(".csv"):
                        file_path = os.path.join(path, file)
                        print(f"Reading file: {file}")
                        df = pd.read_csv(file_path)
                        df["case"] = "_".join(file.split("_")[2:4])
                        df["sector"] = file.split("_")[-1].split(".")[0]
                        data = pd.concat([data, df], ignore_index=True)

        print(f"Check cases: {data['case'].unique()}")
        print(f"Check row numbers: {len(data)}")
        print(f"Check column numbers: {len(data.columns)}")
        return data

    def collect_data_direct(self, folder_path):
        """
        Merge all columns from all files in a folder(axis=1), ready for plot drawing.
        Note: This function is used when you have all files in one folder.
        """
        data = pd.DataFrame()
        sorted_folders = sorted(os.listdir(folder_path), key=self.sort_file)
        for file in sorted_folders:
            if file.endswith(".csv"):
                file_path = os.path.join(folder_path, file)
                df = pd.read_csv(file_path)
                case_name = " ".join(file.split("_")[2:4])
                df["case"] = case_name if "static" not in case_name else "deterministic"
                match = re.search(r'simulations_(.*)\.csv', file)
                df["sector"] = match.group(1).replace("_", " ") if match else print("Sector name not founded.")
                data = pd.concat([data, df], ignore_index=True)

        print(f"Check cases: {data['case'].unique()}")
        print(f"Check row numbers: {len(data)}")
        print(f"Check column numbers: {len(data.columns)}")
        return data

    def draw_plot(self, data, compare_type, database_name, sector_names, save_path):
        font = {'size': 16}
        plt.rc('font', **font)
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        def scientific_format(x, pos):
            return f'{x:.2e}'
        formatter = FuncFormatter(scientific_format)

        if compare_type == "cases": # means one plot includes all uncertainty cases for one sector
            for sector in data["sector"].unique():
                filtered_data = data[data["sector"] == sector].copy()
                plt.figure(figsize=(16, 14))
                plt.xlabel("Cases", labelpad=20)
                plt.ylabel("kg CO\u2082eq", labelpad=20)
                sb.boxplot(x=filtered_data["case"], y=filtered_data["kg CO2eq"], data=filtered_data, order=sector_names, hue="case", palette="Set2")
                plt_title = " ".join([sector, database_name])
                plt.title(plt_title, labelpad=20)
                plt_name = f"MC_{plt_title}_{compare_type}.png"
                plt.gca().yaxis.set_major_formatter(formatter)
                plt.savefig(os.path.join(save_path, plt_name))
                plt.close() # always remember to free memory
        elif compare_type == "sectors": # means one plot includes all sectors
            for case in data["case"].unique():
                filtered_data = data[data["case"] == case].copy()
                plt.figure(figsize=(16, 14))
                plt.xlabel("Activities", labelpad=20)
                plt.ylabel("kg CO\u2082eq", labelpad=20)
                sb.boxplot(x=filtered_data["sector"], y=filtered_data["kg CO2eq"], data=filtered_data, order=sector_names, hue="sector", palette="Set2")
                plt_title = " ".join([case, database_name])
                plt.title(plt_title)
                plt.xticks(
                    ticks=range(len(sector_names)), 
                    labels=["\n".join(textwrap.wrap(label, width=21)) for label in sector_names],
                )
                plt_name = f"MC_{plt_title}_{compare_type}.png"
                plt.gca().yaxis.set_major_formatter(formatter)
                plt.savefig(os.path.join(save_path, plt_name))
                plt.close() # always remember to free memory