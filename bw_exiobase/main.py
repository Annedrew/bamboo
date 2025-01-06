from constants import *
import pandas as pd
from bw_exiobase.utils import *


simu = SimulationScript()

def get_activities(region_column: pd.Series, sector_column: pd.Series) -> list:
    """
    Form activities by combing <country_name> and <sector_name>.
    """
    activities = (region_column + "-" + sector_column).to_list()

    return activities

def data_prepare(A_file, S_file):
    # technosphere matrix
    tech_df = pd.read_table(A_file, sep='\t', low_memory=False, header=None)
    raw_tech = tech_df.iloc[3:, 2:].astype('float').to_numpy()
    tech_matrix = simu.form_tech_matrix(raw_tech)

    # biosphere matrix
    bio_df = pd.read_csv(S_file, header=[0,1], index_col=[0], sep='\t', low_memory=False)
    bio_matrix = simu.form_bio_matrix(bio_df, GHG)
    if tech_matrix.shape[1] != bio_matrix.shape[1] or bio_matrix.shape[0] != len(GHG):
        print("The shape of matrices don't match!")

    # characterization factor matrix
    # emission_code = pd.read_csv("EXIOBASE-ecoinvent-bio-bw-GHG.csv", delimiter=",") 
    # simu.file_preprocessing("EXIOBASE-ecoinvent-bio-bw-GHG.csv", ",", ) # TODO: need to concatenate multiple columns as the name or save the code, better to follow the order of emissions because biosphere gives emissions.
    # cf_matrix = simu.form_cf_matrix(, METHOD)
    cf_matrix = np.diagflat(CFS)

    return tech_matrix, bio_matrix, cf_matrix

def data_prepare_addional_data(A_file, S_file, extend_file, activities):
    # technosphere matrix
    tech_df = pd.read_table(A_file, sep='\t', low_memory=False, header=None)
    raw_tech = tech_df.iloc[3:, 2:].astype('float').to_numpy()
    tech_matrix = simu.form_tech_matrix(raw_tech)

    extend_data = pd.read_csv(extend_file, delimiter=";").iloc[:, :2]
    tech_matrix_new = simu.extend_matrix(tech_matrix, extend_data, activities, is_technosphere=True)
    if not (tech_matrix_new.shape[0] == tech_matrix.shape[0]+1 and tech_matrix_new.shape[1] == tech_matrix.shape[1]+1):
        print("Add column and row to technosphere failed!")

    # biosphere matrix
    bio_df = pd.read_csv(S_file, header=[0,1], index_col=[0], sep='\t', low_memory=False)
    bio_matrix = simu.form_bio_matrix(bio_df, GHG)
    extend_data = pd.DataFrame([{"Exiobase_big_col (matrix B)": "N2O - combustion - air",
                                 "Amount": 5.62,
                                 "Exchange uncertainty type": 1,
                                 "Exchange loc": 1.7263316639056,
                                 "Exchange scale": 0,
                                 "Exchange negative": False}]).iloc[:, :2]
    bio_matrix_new = simu.extend_matrix(bio_matrix, extend_data, GHG, is_technosphere=False)
    if not (bio_matrix_new.shape[0] == bio_matrix.shape[0] and bio_matrix_new.shape[1] == bio_matrix.shape[1]+1):
        print("Add column and row to biosphere failed!")

    # characterization factor matrix
    # emission_code = pd.read_csv("EXIOBASE-ecoinvent-bio-bw-GHG.csv", delimiter=",") 
    # simu.file_preprocessing("EXIOBASE-ecoinvent-bio-bw-GHG.csv", ",", ) # TODO: need to concatenate multiple columns as the name or save the code, better to follow the order of emissions because biosphere gives emissions.
    # cf_matrix = simu.form_cf_matrix(, METHOD)
    cf_matrix = np.diagflat(CFS)

    return tech_matrix_new, bio_matrix_new, cf_matrix

def create_datapackages_pedigree(tech_matrix, bio_matrix, cf_matrix, activities, extra_column):
    datapackage_data = simu.prepare_bw_matrix(tech_matrix, bio_matrix, cf_matrix, extra_column + activities)
    tech_data, tech_indices, tech_flip = datapackage_data[0]
    bio_data, bio_indices = datapackage_data[1]

    # find and save pedigree undertainty
    country_region, sector_seccat, region_sector_dfs = simu.map_pedigree_uncertainty(COUNTRY_FILE, SECTOR_FILE, GSD_FILE)
    for i in range(len(simu.metadata)):
        if 0 in simu.metadata[i]: # skip extra column
            continue
        for index, act in simu.metadata[i].items():
            gsd = simu.find_pedigree_uncertainty(act, country_region, sector_seccat, region_sector_dfs)
            simu.metadata[i][index] = (act, gsd)

    # find and save specific uncertainty
    specific_uncertainty_df = simu.file_preprocessing("/Users/bp45th/Downloads/20241121_foreground_system_small.csv", ";", "Exiobase_small_col", activities)
    uncertainty_df = specific_uncertainty_df["u"]
    uncertainty_df = uncertainty_df.where(pd.notnull(uncertainty_df), 0)
    for i in range(len(simu.metadata)):
        if 0 in simu.metadata[i]:
            for key, value in simu.metadata[i].items():
                simu.metadata[i][key] = (value, uncertainty_df.to_list())

    # add pedigree and specific uncertainty
    tech_uncertainty = simu.add_uncertainty(tech_data, tech_indices, tech_flip)
    bio_uncertainty = simu.add_uncertainty(bio_data, bio_indices, None)
    datapackage = simu.prepare_datapackage(datapackage_data, uncertainty=[tech_uncertainty, bio_uncertainty, None])

    return datapackage

def create_datapackages(tech_matrix, bio_matrix, cf_matrix):
    datapackage_data = simu.prepare_bw_matrix(tech_matrix, bio_matrix, cf_matrix)
    datapackage = simu.prepare_datapackage(datapackage_data)
                       
    return datapackage

def run_experiments(chosen_act, datapackage):
    for act in chosen_act:
        lca_score = simu.perform_simulation(act[1], datapackage)
        print(f"Brightway calculated lca score: {lca_score}")

def check_additional_column_correct(A, B, C, chosen_act):
    A_ = -A
    np.fill_diagonal(A_, -A_.diagonal())
    for act in chosen_act:
        lca_score_manual = simu.manual_lca(A, B, C, A_, act[1])
        print(f"Manually calculated lca score: {lca_score_manual}")

if __name__ == "__main__":
    # # baseline, exiobase small
    # tech_matrix, bio_matrix, cf_matrix = data_prepare(SMALL_A_FILE, SMALL_S_FILE)
    # datapackage = create_datapackages(tech_matrix, bio_matrix, cf_matrix)
    # run_experiments(SMALL_CHOSEN_ACT, datapackage)

    # # additional column, exiobase small
    # tech_matrix, bio_matrix, cf_matrix = data_prepare_addional_data(SMALL_A_FILE, SMALL_S_FILE)
    # datapackage = create_datapackages(tech_matrix, bio_matrix, cf_matrix)
    # run_experiments(SMALL_CHOSEN_ACT, datapackage)
    # check_additional_column_correct(tech_matrix, bio_matrix, cf_matrix, SMALL_CHOSEN_ACT)

    # additional column with pedigree, exiobase small
    tech_df = pd.read_table(SMALL_A_FILE, sep='\t', low_memory=False, header=None)
    activities = get_activities(tech_df.iloc[3:, 0], tech_df.iloc[3:, 1])
    
    tech_matrix, bio_matrix, cf_matrix =  data_prepare_addional_data(SMALL_A_FILE, SMALL_S_FILE, SMALL_EXTEND, activities)
    datapackage = create_datapackages_pedigree(tech_matrix, bio_matrix, cf_matrix, activities, ["extra"])
    run_experiments(SMALL_CHOSEN_ACT, datapackage)
    check_additional_column_correct(tech_matrix, bio_matrix, cf_matrix, SMALL_CHOSEN_ACT)