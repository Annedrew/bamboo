import os

# ---------- PARAMETERS FOR SIMULATION ---------- 
# EXIOBASE AGGREGATED FILE PATH
EXIOBASE_AGGREGATED_INPUT = os.path.join(os.getcwd(), "exiobase_aggregated")
EXIOBASE_AGGREGATED_OUTPUT = os.path.join(os.getcwd(), "small_output")
EXIOBASE_AGGREGATED_A_FILE = os.path.join(os.getcwd(), "data/", "A.txt")
EXIOBASE_AGGREGATED_S_FILE = os.path.join(os.getcwd(), "data/", "S.txt")
EMISSION_CODE_FILE = os.path.join(os.getcwd(), "data", "EXIOBASE-ecoinvent-bio-bw-GHG.csv")
FG_FILE_1COL = os.path.join(os.getcwd(), "data", "fg_exiobase_aggregated_1col.csv")
FG_FILE_2COL = os.path.join(os.getcwd(), "data", "fg_exiobase_aggregated_2col.csv")

# UNCERTAINTY
DIST_TYPE = ["static", "uniform", "log-normal", "pedigree"] # Define the types of distribution
U_UNIFORM = [0.1, 0.2, 0.3] # Define the uncertainty for uniform distribution
U_LOG = [1.106, 1.225, 1.363] # Define the uncertainty for log-normal distribution

# ---------- CONSTANTS FOR CASE STUDY ----------
METHOD = ('IPCC 2013', 'climate change', 'global warming potential (GWP100)')
GHG = ["CO2 - combustion - air",
        "CO2 - non combustion - Cement production - air",
        "CO2 - non combustion - Lime production - air",
        "CO2 - waste - biogenic - air", 
        "CO2 - waste - fossil - air",
        "CO2 - agriculture - peat decay - air", 
        "CH4 - agriculture - air",
        "CH4 - waste - air",
        "CH4 - combustion - air",
        "CH4 - non combustion - Extraction/production of (natural) gas - air",
        "CH4 - non combustion - Extraction/production of crude oil - air",
        "CH4 - non combustion - Mining of antracite - air",
        "CH4 - non combustion - Mining of bituminous coal - air",
        "CH4 - non combustion - Mining of coking coal - air",
        "CH4 - non combustion - Mining of lignite (brown coal) - air",
        "CH4 - non combustion - Mining of sub-bituminous coal - air",
        "CH4 - non combustion - Oil refinery - air",
        "N2O - combustion - air",
        "N2O - agriculture - air",
        "SF6 - air"]

COUNTRY_FILE = "../gsd_data/Grouping_reg.csv"
SECTOR_FILE = "../gsd_data/Grouping_sec.csv"
GSD_FILE = "../gsd_data/GSD_sec_reg.csv"
GSD_SMALL_FILE = "../gsd_data/GSD_background_pedigree_exiobase_small.csv"
