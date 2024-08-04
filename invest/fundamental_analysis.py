import pandas as pd
from invest.ratios import liquidity, efficiency, solvency, valuation
from sklearn.linear_model import LinearRegression
import numpy as np

def main_fundamental_indicators(stock):
    score = pd.DataFrame()
    score["name"] = [stock.name]
    score["isin"] = [stock.isin]
    score["code"] = [stock.code]
    #score["LastPriceDate"] = [stock.quot_date]

    score["Reference Price"] = [stock.reference_price]
    score["Graham Price"] = [stock.graham_price]



    #DIVIDEND
    score["Dividend yeld"] = [stock.dividend_yeld]
    score["Payout Ratio"] = [stock.payout_ratio]
    #try:
    #    N = 2023 - stock.annual_dividends['Year'][0] + 1
    #    score["Number of Years of Dividends"] = [N]
    #    if N != 0:
    #        score["Dividend Consistency"] = [len(stock.annual_dividends)/N]
    #    else:
    #        score["Dividend Consistency"] = [0]
    #except:
    #    score["Number of Years of Dividends"] = [0]
    #    score["Dividend Consistency"] = [0]

    #LIQUIDITY
    score["Quick Ratio"] = [liquidity.get_quick_ratio(stock.cash_and_equivalents,
                                                      stock.accounts_receivable,
                                                      stock.marketable_securities,
                                                      stock.current_liabilities)]

    score["Cash Ratio"] = [liquidity.get_cash_ratio(stock.cash_and_equivalents,
                                                    stock.marketable_securities,
                                                    stock.current_liabilities)]

    score["Current Ratio"] = [stock.current_ratio]

    #score["Operating Cash Flow Ratio"] = [liquidity.get_operating_cash_flow_ratio(stock.operating_cash_flow,
    #                                                                              stock.current_liabilities)]
    #score["Operating Cash Flow Sales Ratio"] = [liquidity.get_operating_cash_flow_sales_ratio(stock.operating_cash_flow,
    #                                                                                          stock.revenue)]
    #score["Short Term Coverage Ratio"] = [liquidity.get_short_term_coverage_ratio(stock.operating_cash_flow,
    #                                                                              stock.accounts_receivable,
    #                                                                              stock.inventory,
    #                                                                              stock.accounts_payable)]
    #score['Working capital over market cap'] = [liquidity.get_working_capital(stock.current_assets,
    #                                                                          stock.current_liabilities)/
    #                                                                          stock.market_cap]
    #EFFICIENCY
    #score["Asset Turnover Ratio"] = [efficiency.get_asset_turnover_ratio(stock.sales,
    #                                                                     stock.total_assets_begin,
    #                                                                     stock.total_assets_end )]
    #SOLVENCY
    #score["Debt to Assets Ratio"] = [solvency.get_debt_to_assets_ratio(stock.total_debt,
    #                                                                   stock.total_assets)]
    #score["Debt to Equity Ratio"] = [solvency.get_debt_to_equity_ratio(stock.total_debt,
    #                                                                   stock.total_equity)]
    #score["Interest Coverage Ratio"] = [solvency.get_interest_coverage_ratio(stock.operating_income,
    #                                                                         stock.depreciation_and_amortization,
    #                                                                         stock.interest_expense)]
    #score["Debt Service Coverage Ratio"] = [solvency.get_debt_service_coverage_ratio(stock.operating_income,
    #                                                                                 stock.current_liabilities)]
    #score["Free Cash Flow Yield"] = solvency.get_free_cash_flow_yield(stock.free_cash_flow,
    #                                                                  stock.market_cap)


    #VALUATION
    score["price_over_graham"] = [stock.reference_price/stock.graham_price]
    score["Net current asset per share over price"] = [stock.net_current_assets/stock.market_cap]

    score['EPS over price'] = [stock.EPS/stock.reference_price]
    score['Revenue per Share'] = [valuation.get_revenue_per_share(stock.revenue,
                                                                  stock.n_shares)]

    score["PE"] = [stock.PE]
    score["ROE"] = [stock.ROE]
    score["PB"] = [stock.PB]
    #score["PS"] = [stock.PS]
    #score['Book Value per Share'] = [valuation.get_book_value_per_share(stock.stockholder_equity,
    #                                                                    0,
    #                                                                    stock.n_shares)]
    score["Price to cash flow"] = [stock.price_to_cash_flow]
    score["Price to free cash flow"] = [stock.price_to_free_cash_flow]
    score['Net cash over market cap'] = [stock.net_cash_per_share/stock.reference_price]
    score['ROCE'] = [stock.ROCE]
    score['Net income per employee'] = [stock.net_income_per_employee]
    score['Revenue per employee'] = [stock.revenue_per_employee]
    score['Fulltime employee'] = [stock.full_time_employees]
    score['market_cap'] = [stock.market_cap]
    score["Return on Assets"] = [stock.ROA]

    #try:
    #    score['NetIncome derivative'] = compute_slope(stock.yearly_financials.NetIncome)
    #except:
    #    score['NetIncome derivative'] = 0
#
    #try:
    #    score['Revenue derivative'] = compute_slope(stock.yearly_financials.TotalRevenue)
    #except:
    #    score['Revenue derivative'] = 0
#
    #try:
    #    score['OperatingRevenue derivative'] = compute_slope(stock.yearly_financials.OperatingRevenue)
    #except:
    #    score['OperatingRevenue derivative'] = 0
#
    #try:
    #    score['TotalAssets derivative'] = compute_slope(stock.yearly_financials.TotalAssets)
    #except:
    #    score['TotalAssets derivative'] = 0
#
    #try:
    #    score['TotalAssets derivative'] = compute_slope(stock.yearly_financials.TotalAssets)
    #except:
    #    score['TotalAssets derivative'] = 0
    #try:
    #    score['FreeCashFlow derivative'] = compute_slope(stock.yearly_financials.FreeCashFlow)
    #except:
    #    score['FreeCashFlow derivative'] = 0
    #try:
    #    score['TangibleBookValue derivative'] = compute_slope(stock.yearly_financials.TangibleBookValue)
    #except:
    #    score['TangibleBookValue derivative'] = 0

        
    #score['volatility'] = volatility(stock)
    score['BUYBACK_SCORE'] = score_buyback(stock)
   
    return score


def compute_slope(y):
    X = np.array(range(len(y))).reshape(-1, 1)
    reg = LinearRegression().fit(X, y)
    return reg.coef_.item()

def score_buyback(stock):
    if stock.n_shares < np.mean(stock.yearly_balance_sheet['ShareIssued'].values):
        return 5
    elif stock.n_shares == np.mean(stock.yearly_balance_sheet['ShareIssued'].values):
        return 3
    else:
        return 0

def volatility(stock):
    TRADING_DAYS = 252
    returns = np.log(stock.hist['Close']/stock.hist['Close'].shift(1))
    returns.fillna(0, inplace=True)
    volatility = returns.rolling(window=TRADING_DAYS).std()*np.sqrt(TRADING_DAYS)
    return volatility.tail(1).item()
