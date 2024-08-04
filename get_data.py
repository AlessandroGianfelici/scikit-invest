import os
import pandas as pd
from invest.scoring import compute_score, get_indicators, main_fundamental_indicators
import os
import pandas as pd
from invest.utils import file_folder_exists, select_or_create
from invest import Stock


self = Stock('IT0001041000')
main_fundamental_indicators(self)
print("DONE")
