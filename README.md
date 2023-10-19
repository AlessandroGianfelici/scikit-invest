# scikit-invest
A collection of utilities for investors

## Usage
As the libraries relies on data downloaded by yahoo finance, it can be used to screen stocks on any market.
Hereafter a sample of use on the markets I usually operate:

### Screening Borsa Italiana's stocks
Example of use on Italian stocks:

```python
from invest.loader import load_borsa_italiana_stocks_symbols
from invest.fundamental_analysis import main_fundamental_indicators
from invest.technical_analysis import detect_trend
from invest.scoring import compute_score, get_indicators
from invest import Stock
import pandas as pd

# Loading symbols
symbols = load_borsa_italiana_stocks_symbols()

# Computing indicators
result = pd.DataFrame()

for symbol in symbols['SYMBOL']:
    try:
        mystock = Stock(symbol)
        result = pd.concat([result,
                        get_indicators(mystock)])
    except Exception as e:
        print(e, e.__doc__)
        pass

compute_score(result.reset_index(drop=1))

```

### Screening NASDAQ's stocks
Example of use on NASDAQ's stocks:
```python
from invest.loader import load_nasdaq_exchange_symbols
from invest.fundamental_analysis import main_fundamental_indicators
from invest.technical_analysis import detect_trend
from invest.scoring import compute_score, get_indicators
from invest import Stock
import pandas as pd

# Loading symbols
symbols = load_nasdaq_exchange_symbols()

# Computing indicators
result = pd.DataFrame()

for symbol, name in zip(symbols['Symbol'], symbols['Description']):
    try:
        mystock = Stock(symbol)
        result = pd.concat([result,
                        get_indicators(mystock)])
    except Exception as e:
        print(e, e.__doc__)
        pass

compute_score(result.reset_index(drop=1))

```

## Feedbacks

Any feedback, improvement/enhancement or issue is welcome in the [issue page](https://github.com/AlessandroGianfelici/hycom_downloader/issues) of the repo.

## Contributing

Feel free to fork this repository, modify the code and open any needed pull requests!

## Licence

This repository has a MIT License.

## Support
As I am a caffeine-fueled programmer, if you want to support my open source projects you can offer me a coffee ;) 
<p><a href="https://www.buymeacoffee.com/AleGianfelici"> <img align="left" src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" height="50" width="210" alt="AleGianfelici" /></a><a href="https://ko-fi.com/alessandrogianfelici"> <img align="left" src="https://cdn.ko-fi.com/cdn/kofi3.png?v=3" height="50" width="210" alt="alessandrogianfelici" /></a></p><br><br>

