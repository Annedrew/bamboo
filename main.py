from bw_exiobase.background_importer import *
from bw_exiobase.foreground_importer import *
from bw_exiobase.datapackage_builder import *
from bw_exiobase.uncertainty_handler import *
from bw_exiobase.exiobase_lca import *
from constants import *

bg_importer = BackgroundImporter()

"""
Prepare background database
"""
# get technosphere matrix
tech_df = pd.read_table(EXIOBASE_AGGREGATED_A_FILE, sep='\t', header=None, low_memory=False)
raw_tech = tech_df.iloc[3:, 2:].astype('float').to_numpy()
tech_matrix = bg_importer.form_tech_matrix(raw_tech)

# get biosphere matrix
bio_df = pd.read_csv(EXIOBASE_AGGREGATED_S_FILE, header=[0,1], index_col=[0], sep='\t', low_memory=False)
bio_matrix = bg_importer.form_bio_matrix(bio_df, GHG)

# get characterization factor matrix
cf_matrix = bg_importer.form_cf_matrix(EMISSION_CODE_FILE, METHOD, GHG)

"""
Prepare foreground database
"""
# use tech data as an example
activities = get_activities(EXIOBASE_AGGREGATED_A_FILE, "\t")
fore_df = pd.read_csv("ALIGNED-LCI-biobased-product-dummy.csv")

fg_importer = ForegroundImporter()
fg_importer.extend_matrix(tech_matrix, fore_df, activities)

# build datapackage
# dp_builder = DatapackageBuilder()
# datapackage_data = dp_builder.prepare_bw_matrix(tech_matrix, bio_matrix, cf_matrix)
# datapackage = dp_builder.prepare_datapackage(datapackage_data)

# lca_runner = ExiobaseLCA()
# lca_runner.perform_static(68, datapackage, EXIOBASE_AGGREGATED_OUTPUT, 0, "static", "RoW-Services")