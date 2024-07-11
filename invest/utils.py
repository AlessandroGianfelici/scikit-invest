import os
from functools import reduce
from sklearn.metrics import mean_squared_error
import numpy as np

import pandas as pd
import yaml



def file_folder_exists(path: str):
    """
    Return True if a file or folder exists.
    :param path: the full path to be checked
    :type path: str
    """
    try:
        os.stat(path)
        return True
    except:
        return False


def select_or_create(path: str):
    """
    Check if a folder exists. If it doesn't, it create the folder.
    :param path: path to be selected
    :type path: str
    """
    if not file_folder_exists(path):
        os.makedirs(path)
    return path

def load_yaml(filename: str) -> dict:
    """Utility function to load a yaml file into a pyhon dict

    Parameters
    ----------
    filename : str
        fullpath of the yaml file

    Returns
    -------
    dict
    """
    assert filename.endswith("yaml") or filename.endswith(
        "yml"
    ), "Not a yaml extention!"
    with open(filename, "r", encoding="utf-8") as handler:
        return yaml.load(handler, Loader=yaml.FullLoader)
    
def merge_dataframe(data_frames):
    return reduce(lambda left, right: pd.merge(left, right, how="outer"), data_frames)

def rmse(y_true, y_pred):
    return np.sqrt(mean_squared_error(y_true, y_pred))