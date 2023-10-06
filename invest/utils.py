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


def merge_dataframe(data_frames):
    return reduce(lambda left, right: pd.merge(left, right, how="outer"), data_frames)

def rmse(y_true, y_pred):
    return np.sqrt(mean_squared_error(y_true, y_pred))