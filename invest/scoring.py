import pandas as pd
from invest.fundamental_analysis import main_fundamental_indicators
from invest.technical_analysis import detect_trend
import piecewise_regression
from sklearn.preprocessing import MinMaxScaler
import numpy as np

def compute_score(indicatori : pd.DataFrame):

    #DIVIDEND
    indicatori['score_dividend_YELD'] = score_YELD(indicatori['Dividend yeld'])
    indicatori['score_dividend_PAYOUT'] = score_PAYOUT(indicatori['Payout Ratio'])
    indicatori['score_dividend_HISTORY'] = score_DIVHIST(indicatori['Number of Years of Dividends'])
    indicatori['score_dividend_CONSISTENCY'] = score_DIVCONSISTENCY(indicatori['Dividend Consistency'])

    #LIQUIDITY
    indicatori['score_liquidity_QR'] = score_QR(indicatori['Quick Ratio'])
    indicatori['score_liquidity_CASHR'] = score_CashRatio(indicatori['Cash Ratio'])
    indicatori['score_liquidity_CUR'] = score_CurrentRatio(indicatori['Current Ratio'])
    indicatori['score_liquidity_OCFR'] = score_OCFR(indicatori['Operating Cash Flow Ratio'])
    indicatori['score_liquidity_OCFSR'] = score_quantile(indicatori['Operating Cash Flow Sales Ratio'],  nan_score=np.nan)
    indicatori['score_liquidity_STCFR'] = score_quantile(indicatori['Short Term Coverage Ratio'],  nan_score=np.nan)
    indicatori['score_liquidity_WCOMC'] = score_quantile(indicatori['Working capital over market cap'],  nan_score=np.nan)

    #EFFICIENCY
    indicatori['score_efficiency_ATR'] = score_efficiency_ATR(indicatori.copy())
    indicatori['score_efficiency_NIPE'] = score_NIPE(indicatori['Net income per employee'])

    #SOLVENCY
    indicatori['score_solvency_DAR'] = score_quantile(1 - indicatori['Debt to Assets Ratio'],  nan_score=np.nan)
    indicatori['score_solvency_DER'] = score_quantile(1 - indicatori['Debt to Equity Ratio'],  nan_score=np.nan)
    indicatori['score_solvency_ICR'] = score_quantile(indicatori['Interest Coverage Ratio'],  nan_score=np.nan)
    indicatori['score_solvency_DSCR'] = score_quantile(indicatori['Debt Service Coverage Ratio'],  nan_score=np.nan)
    indicatori['score_solvency_EM'] = score_quantile(1 - indicatori['Equity Multiplier'],  nan_score=np.nan)
    indicatori['score_solvency_FCFY'] = score_quantile(indicatori['Free Cash Flow Yield'],  nan_score=np.nan)

    #VALUE
    indicatori['score_value_PE'] = score_PE(indicatori['PE'])
    indicatori['score_value_PB'] = score_PB(indicatori['PB'])
    indicatori['score_value_ROA'] = score_ROA(indicatori['Return on Assets'])
    indicatori['score_value_ROE'] = score_ROE(indicatori['ROE'])
    indicatori['score_value_NCAPSOP'] = score_NCAPSOP(indicatori['Net current asset per share over price'])
    indicatori['score_value_ROCE'] = score_ROCE(indicatori['ROCE'])
    indicatori['score_value_EPS'] = score_EPS(indicatori['EPS over price'])
    indicatori['score_value_BVS'] = score_quantile(indicatori['Book Value per Share'])
    indicatori['score_value_PFC'] = score_quantile(indicatori['Price to free cash flow']**-1, nan_score = np.nan)
    indicatori['score_value_graham'] = score_graham(indicatori['price_over_graham'])

    #TECHNICAL
    indicatori['score_technical_TM'] = score_TREND(indicatori['trend_magnitude'])
    #indicatori['score_technical_POT'] = score_quantile(indicatori['price_over_trend'])

    indicatori['DIVIDEND_SCORE']       = indicatori.filter(like='score_dividend_').mean(axis=1)
    indicatori['LIQUIDITY_SCORE']      = indicatori.filter(like='score_liquidity').mean(axis=1)
    indicatori['EFFICIENCY_SCORE']     = indicatori.filter(like='score_efficiency').mean(axis=1)
    indicatori['SOLVENCY_SCORE']       = indicatori.filter(like='score_solvency_').mean(axis=1)
    indicatori['VALUE_SCORE']          = indicatori.filter(like='score_value_').mean(axis=1)
    indicatori['TECHNICAL_SCORE']      = indicatori.filter(like='score_technical_').mean(axis=1)

    indicatori['OVERALL_SCORE'] =  indicatori.filter(like='_SCORE').mean(axis=1)

    return indicatori.sort_values(by='OVERALL_SCORE', ascending=False)


def get_indicators(stock):
    trend_magnitude, last_value_trendline = detect_trend(stock.hist.reset_index(),
                                                         verbose=0)
    tmp = main_fundamental_indicators(stock)
    tmp['trendline'] = last_value_trendline
    tmp['trend_magnitude'] = trend_magnitude
    tmp['price_over_trend'] = (tmp['Reference Price'])/last_value_trendline
    tmp['sector'] = stock.get_info('sector')
    tmp['description'] = stock.get_info('longBusinessSummary')
    #tmp['#div_past20y'] = years_of_dividend_payments(stock)
    tmp['score_dividend_DIVTREND'] = score_DIVTREND(stock)
    return tmp

def score_efficiency_ATR(result):
    sectors = result['sector'].unique()
    result['score_efficiency_ATR'] = np.nan
    try:
        for sector in sectors:
            filtered = result.loc[result['sector'] == sector]['Asset Turnover Ratio']
            result.loc[result['sector'] == sector, 'score_efficiency_ATR'] = 5* MinMaxScaler().fit_transform(filtered.values.reshape(-1, 1))
    except:
        pass
    return result['score_efficiency_ATR']

def score_OCFR(value):
    df = pd.DataFrame()
    df['Operating Cash Flow Ratio'] = value
    df.loc[df['Operating Cash Flow Ratio'] < 1, 'score_liquidity_OCFR'] = 2
    df.loc[df['Operating Cash Flow Ratio'] < 0.8, 'score_liquidity_OCFR'] = 1    
    df.loc[df['Operating Cash Flow Ratio'] < 0, 'score_liquidity_OCFR'] = 0
    
    df.loc[df['Operating Cash Flow Ratio'] > 1, 'score_liquidity_OCFR'] = 3
    df.loc[df['Operating Cash Flow Ratio'] > 1.2, 'score_liquidity_OCFR'] = 4
    df.loc[df['Operating Cash Flow Ratio'] > 2, 'score_liquidity_OCFR'] = 5
    return df['score_liquidity_OCFR']

def score_DIVHIST(years_of_payments):
    tmp = pd.DataFrame()
    tmp['score_dividend_HISTORY'] = years_of_payments.apply(lambda x : min(x, 20))/4
    return tmp['score_dividend_HISTORY']

def score_DIVCONSISTENCY(fraction_of_payments):
    tmp = pd.DataFrame()
    tmp['score_dividend_CONSISTENCY'] = 5*fraction_of_payments.apply(lambda x : min(x, 1))
    return tmp['score_dividend_CONSISTENCY']

def score_quantile(value, nan_score=0):
    tmp = pd.DataFrame()
    tmp['value'] = value
    soglia_5 = tmp['value'].quantile(0.9)
    tmp['score'] = None
    tmp.loc[tmp['value'].isna(), 'score'] = nan_score
    tmp.loc[(tmp['value'] < 0), 'score'] = 0
    tmp.loc[(tmp['value'] > soglia_5), 'score'] = 5
    tmp.loc[((tmp['value'] >= 0) &
             (tmp['value'] <= soglia_5)), 'score'] = 5*tmp['value']/soglia_5
    return tmp['score']

def score_ROCE(roce):
    tmp = pd.DataFrame()
    tmp['ROCE'] = roce
    soglia_5 = tmp['ROCE'].quantile(0.9)
    tmp['score_ROCE'] = None
    tmp.loc[(tmp['ROCE'].isna() |
            (tmp['ROCE'] < 0)), 'score_ROCE'] = 0
    tmp.loc[(tmp['ROCE'] > soglia_5), 'score_ROCE'] = 5
    tmp.loc[((tmp['ROCE'] >= 0) &
             (tmp['ROCE'] <= soglia_5)), 'score_ROCE'] = 5*tmp['ROCE']/soglia_5
    return tmp['score_ROCE']

def score_OPENJOBS(roce):
    tmp = pd.DataFrame()
    tmp['OPENJOBS'] = roce
    soglia_5 = tmp['OPENJOBS'].quantile(0.9)
    tmp['score_OPENJOBS'] = None
    tmp.loc[(tmp['OPENJOBS'].isna() |
            (tmp['OPENJOBS'] < 0)), 'score_OPENJOBS'] = 0
    tmp.loc[(tmp['OPENJOBS'] > soglia_5), 'score_OPENJOBS'] = 5
    tmp.loc[((tmp['OPENJOBS'] >= 0) &
             (tmp['OPENJOBS'] <= soglia_5)), 'score_OPENJOBS'] = 5*tmp['OPENJOBS']/soglia_5
    return tmp['score_OPENJOBS']

def score_FOLLOWERS(roce):
    tmp = pd.DataFrame()
    tmp['FOLLOWERS'] = roce
    soglia_5 = tmp['FOLLOWERS'].quantile(0.9)
    tmp['score_FOLLOWERS'] = None
    tmp.loc[(tmp['FOLLOWERS'].isna() |
            (tmp['FOLLOWERS'] < 0)), 'score_FOLLOWERS'] = 0
    tmp.loc[(tmp['FOLLOWERS'] > soglia_5), 'score_FOLLOWERS'] = 5
    tmp.loc[((tmp['FOLLOWERS'] >= 0) &
             (tmp['FOLLOWERS'] <= soglia_5)), 'score_FOLLOWERS'] = 5*tmp['FOLLOWERS']/soglia_5
    return tmp['score_FOLLOWERS']

def score_YELD(div_yeld):
    tmp_df = pd.DataFrame()
    tmp_df['Dividend yeld'] = div_yeld
    tmp_df['score_YELD'] =  (5*tmp_df['Dividend yeld']/tmp_df['Dividend yeld'].quantile(0.9)).map(lambda x : min(5, x))
    return tmp_df['score_YELD']

def score_PAYOUT(payout):
    tmp_df = pd.DataFrame()
    tmp_df['payout'] = 1 - payout
    tmp_df['score_PAYOUT'] = None
    tmp_df.loc[(tmp_df['payout'] <= 0)  |
               (tmp_df['payout'] >= 1), 'score_PAYOUT'] = 0
    tmp_df.loc[(tmp_df['payout'] > 0) &
               (tmp_df['payout'] < 1) , 'score_PAYOUT'] = 5*tmp_df['payout']
    return tmp_df['score_PAYOUT']

def years_of_dividend_payments(mystock):
    tmp_div_df = pd.DataFrame()
    mydate = mystock.quot_date
    tmp_div_df['Year'] = list(range(mydate.year-20, mydate.year))
    try:
        dividends_df = mystock.annual_dividends.copy().merge(tmp_div_df)
        return len(dividends_df)
    except:
        return 0

def score_PE(PE):
    tmp_df = pd.DataFrame()
    tmp_df['PE'] = PE
    tmp_df['score_PE'] = 1
    tmp_df.loc[tmp_df['PE'].isna(), 'score_PE'] = 0
    tmp_df.loc[tmp_df['PE'] < 17.5, 'score_PE'] = 2
    tmp_df.loc[tmp_df['PE'] < 15, 'score_PE'] = 3
    tmp_df.loc[tmp_df['PE'] < 12, 'score_PE'] = 4
    tmp_df.loc[tmp_df['PE'] < 10, 'score_PE'] = 5
    return tmp_df['score_PE']

def score_QR(qr):
    tmp_df = pd.DataFrame()
    tmp_df['QR'] = qr
    tmp_df['score_QR'] = 0
    tmp_df.loc[tmp_df['QR'].isna(), 'score_QR'] = np.nan
    tmp_df.loc[(tmp_df['QR'] < 1.0) &
               (tmp_df['QR'] > 0.0) , 'score_QR'] =  5*(tmp_df['QR'])
    tmp_df.loc[tmp_df['QR'] >= 1.0, 'score_QR'] = 5.0
    return tmp_df['score_QR']

def score_CashRatio(qr):
    tmp_df = pd.DataFrame()
    tmp_df['CR'] = qr
    tmp_df['score_CR'] = np.nan
    tmp_df.loc[tmp_df['CR'] <= 0.5, 'score_CR'] = 0.0
    tmp_df.loc[(tmp_df['CR'] <= 1.0) &
               (tmp_df['CR'] > 0.5) , 'score_CR'] = 10*(tmp_df['CR'] - 0.5)
    tmp_df.loc[tmp_df['CR'] > 1.0, 'score_CR'] = 5.0
    return tmp_df['score_CR']

def score_CurrentRatio(qr):
    tmp_df = pd.DataFrame()
    tmp_df['CR'] = qr
    tmp_df['score_CR'] = 0.0
    tmp_df.loc[tmp_df['CR'].isna(), 'score_CR'] = np.nan
    tmp_df.loc[(tmp_df['CR'] < 3.0) &
               (tmp_df['CR'] > 1.0) , 'score_CR'] =  2.5*(tmp_df['CR']-1.0)
    tmp_df.loc[tmp_df['CR'] >= 3.0, 'score_CR'] = 5.0
    return tmp_df['score_CR']

def score_PB(PB):
    tmp_df = pd.DataFrame()
    tmp_df['PB'] = PB
    tmp_df['score_PB'] = 0
    tmp_df.loc[tmp_df['PB'].isna() | (tmp_df['PB'] < 0), 'score_PB'] = 0
    tmp_df.loc[(tmp_df['PB'] > 3), 'score_PB'] = 1
    tmp_df.loc[((tmp_df['PB'] < 3) & (tmp_df['PB'] > 2)), 'score_PB'] = 2
    tmp_df.loc[(tmp_df['PB'] < 2) & (tmp_df['PB'] > 1), 'score_PB'] = 4
    tmp_df.loc[(tmp_df['PB'] < 1)& (tmp_df['PB'] > 0), 'score_PB'] = 5
    return tmp_df['score_PB']

def score_TREND(trend):
    tmp_df = pd.DataFrame()
    tmp_df['TREND'] = trend
    tmp_df['score_TREND'] = 0
    tmp_df.loc[(tmp_df['TREND'] > 0), 'score_TREND'] = 5
    return tmp_df['score_TREND']


def score_NIPE(IPE):
    tmp_df = pd.DataFrame()
    tmp_df['IPE'] = IPE

    best_decile = tmp_df['IPE'].quantile(0.90)

    tmp_df['score_NIPE'] = None
    tmp_df.loc[tmp_df['IPE'].isna() | (tmp_df['IPE'] < 0), 'score_NIPE'] = 0

    tmp_df.loc[(tmp_df['IPE'] > 0) &
               (tmp_df['IPE'] < best_decile), 'score_NIPE'] = 5*tmp_df['IPE']/best_decile

    tmp_df.loc[(tmp_df['IPE'] >= best_decile), 'score_NIPE'] = 5

    return tmp_df['score_NIPE']

def score_EPS(ROE):
    tmp_df = pd.DataFrame()
    tmp_df['EPS'] = ROE
    tmp_df['score_EPS'] = None
    best_decile = tmp_df.loc[tmp_df['EPS'] > 0]['EPS'].quantile(0.85)
    tmp_df.loc[tmp_df['EPS'].isna() |
              (tmp_df['EPS'] < 0), 'score_EPS'] = 0
    tmp_df.loc[tmp_df['EPS'] > 0 &
              (tmp_df['EPS'] < best_decile), 'score_EPS'] = 5*tmp_df['EPS']/best_decile
    tmp_df.loc[((tmp_df['EPS'] >= best_decile)), 'score_EPS'] = 5
    return tmp_df['score_EPS']


def score_graham(price_over_graham):
    tmp_df = pd.DataFrame()
    tmp_df['graham'] = price_over_graham
    tmp_df['score_GRAHAM'] = None
    tmp_df.loc[tmp_df['graham'].isna(), 'score_GRAHAM'] = 0
    tmp_df.loc[(tmp_df['graham'] > 2) , 'score_GRAHAM'] = 1
    tmp_df.loc[((tmp_df['graham'] > 1.5) &
                (tmp_df['graham'] < 2)) , 'score_GRAHAM'] = 2
    tmp_df.loc[((tmp_df['graham'] > 1.1) &
                (tmp_df['graham'] < 1.5)) , 'score_GRAHAM'] = 3
    tmp_df.loc[((tmp_df['graham'] > 1) &
                (tmp_df['graham'] < 1.1)) , 'score_GRAHAM'] = 4
    tmp_df.loc[tmp_df['graham'] < 1, 'score_GRAHAM'] = 5
    return tmp_df['score_GRAHAM']

def score_ROA(ROA):
    tmp_df = pd.DataFrame()
    tmp_df['ROA'] = ROA
    tmp_df['score_ROA'] = None
    tmp_df.loc[tmp_df['ROA'].isna() |
              (tmp_df['ROA'] < 0), 'score_ROA'] = 0
    tmp_df.loc[tmp_df['ROA'] > 0 &
              (tmp_df['ROA'] < 0.1), 'score_ROA'] = 5*tmp_df['ROA']/0.1
    tmp_df.loc[((tmp_df['ROA'] >= 0.1)), 'score_ROA'] = 5
    return tmp_df['score_ROA']


def score_ROE(ROE):
    tmp_df = pd.DataFrame()
    tmp_df['ROE'] = ROE
    tmp_df['score_ROE'] = None
    tmp_df.loc[tmp_df['ROE'].isna() |
              (tmp_df['ROE'] < 0), 'score_ROE'] = 0
    tmp_df.loc[tmp_df['ROE'] > 0 &
              (tmp_df['ROE'] < 0.2), 'score_ROE'] = 5*tmp_df['ROE']/0.2
    tmp_df.loc[((tmp_df['ROE'] >= 0.2)), 'score_ROE'] = 5
    return tmp_df['score_ROE']



def score_NCAPSOP(NCAPSOP):
    tmp_df = pd.DataFrame()
    tmp_df['NCAPSOP'] = NCAPSOP
    tmp_df['score_NCAPSOP'] = None
    tmp_df.loc[tmp_df['NCAPSOP'].isna(), 'score_NCAPSOP'] = 3
    tmp_df.loc[tmp_df['NCAPSOP'] < -10, 'score_NCAPSOP'] = 1
    tmp_df.loc[((tmp_df['NCAPSOP'] > -10) &
                (tmp_df['NCAPSOP'] < -5)), 'score_NCAPSOP'] = 2
    tmp_df.loc[((tmp_df['NCAPSOP'] > -5) &
                (tmp_df['NCAPSOP'] < -1)), 'score_NCAPSOP'] = 3
    tmp_df.loc[((tmp_df['NCAPSOP'] > -1) &
                (tmp_df['NCAPSOP'] < 0)), 'score_NCAPSOP'] = 4
    tmp_df.loc[((tmp_df['NCAPSOP'] > 0)), 'score_NCAPSOP'] = 5
    return tmp_df['score_NCAPSOP']



def score_DIVTREND(stock):
    try:
        annual_dividends = stock.annual_dividends.loc[stock.annual_dividends['Year']>=2002]
        ms = piecewise_regression.ModelSelection(annual_dividends['Year'].astype(float).values,
                                             annual_dividends['Dividends'].astype(float).values,
                                             max_breakpoints=3)
    except:
        return 0
    model_selector = pd.DataFrame()

    model_selector['bic'] = [ms.model_summaries[0]['bic'],
                             ms.model_summaries[1]['bic'],
                             ms.model_summaries[2]['bic'],
                             ms.model_summaries[3]['bic']]
    model_selector = model_selector.dropna()
    n_breakpoints = model_selector.loc[model_selector['bic'] == min(model_selector['bic'])].index.item()

    try:
        pw_fit = piecewise_regression.Fit(annual_dividends['Year'].values,
                                          annual_dividends['Dividends'].values,
                                          n_breakpoints=n_breakpoints)

        result = pw_fit.get_results()
        alpha = result['estimates'][f'alpha{1+n_breakpoints}']
        min_alpha = alpha['confidence_interval'][0]
        max_alpha = alpha['confidence_interval'][1]
        if min_alpha > 0:
            return 5
        elif (min_alpha < 0) and (max_alpha > 0):
            return 3
        elif max_alpha < 0:
            return 0
    except:
        return 3