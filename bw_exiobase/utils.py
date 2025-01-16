import pandas as pd

def get_activities(a_file_path: str, delimiter: str) -> list:
    """
    Get all activities by combing <country_name> and <sector_name>. 
    
    Parameters:
        * a_file_path: The path to the file that needs to be processed.
        * delimiter: The separator of the file.
    """
    df = pd.read_csv(a_file_path, delimiter=delimiter, header=None, low_memory=False)
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
