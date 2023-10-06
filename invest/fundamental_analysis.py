import pandas as pd
from invest.ratios import liquidity, efficiency, solvency, valuation

def main_fundamental_indicators(stock):
    score = pd.DataFrame()
    score["code"] = [stock.code]
    score["name"] = [stock.name]
    score["Date"] = [stock.quot_date]

    score["Reference Price"] = [stock.reference_price]
    score["Graham Price"] = [stock.graham_price]



    #DIVIDEND
    score["Dividend yeld"] = [stock.dividend_yeld]
    score["Payout Ratio"] = [stock.payout_ratio]
    try:
        N = 2023 - stock.annual_dividends['Year'][0] + 1
        score["Number of Years of Dividends"] = [N]
        score["Dividend Consistency"] = [len(stock.annual_dividends)/N]
    except:
        score["Number of Years of Dividends"] = [0]
        score["Dividend Consistency"] = [0]

    #LIQUIDITY
    score["Quick Ratio"] = [liquidity.get_quick_ratio(stock.cash_and_equivalents,
                                                      stock.accounts_receivable,
                                                      stock.marketable_securities,
                                                      stock.current_liabilities)]

    score["Cash Ratio"] = [liquidity.get_cash_ratio(stock.cash_and_equivalents,
                                                    stock.marketable_securities,
                                                    stock.current_liabilities)]

    score["Current Ratio"] = [liquidity.get_current_ratio(stock.current_assets,
                                                          stock.current_liabilities)]

    score["Operating Cash Flow Ratio"] = [liquidity.get_operating_cash_flow_ratio(stock.operating_cash_flow,
                                                                                  stock.current_liabilities)]

    score["Operating Cash Flow Sales Ratio"] = [liquidity.get_operating_cash_flow_sales_ratio(stock.operating_cash_flow,
                                                                                              stock.revenue)]

    score["Short Term Coverage Ratio"] = [liquidity.get_short_term_coverage_ratio(stock.operating_cash_flow,
                                                                                  stock.accounts_receivable,
                                                                                  stock.inventory,
                                                                                  stock.accounts_payable)]

    score['Working capital over market cap'] = [liquidity.get_working_capital(stock.current_assets,
                                                                              stock.current_liabilities)/
                                                                              stock.market_cap]

    #EFFICIENCY
    score["Asset Turnover Ratio"] = [efficiency.get_asset_turnover_ratio(stock.sales,
                                                                         stock.total_assets_begin,
                                                                         stock.total_assets_end )]

    #SOLVENCY
    score["Debt to Assets Ratio"] = [solvency.get_debt_to_assets_ratio(stock.total_debt,
                                                                       stock.total_assets)]
    score["Debt to Equity Ratio"] = [solvency.get_debt_to_equity_ratio(stock.total_debt,
                                                                       stock.total_equity)]

    score["Interest Coverage Ratio"] = [solvency.get_interest_coverage_ratio(stock.operating_income,
                                                                             stock.depreciation_and_amortization,
                                                                             stock.interest_expense)]
    score["Debt Service Coverage Ratio"] = [solvency.get_debt_service_coverage_ratio(stock.operating_income,
                                                                                     stock.current_liabilities)]
    score["Equity Multiplier"] = [solvency.get_equity_multiplier(stock.total_assets_begin,
                                                                 stock.total_assets_end,
                                                                 stock.total_equity_begin,
                                                                 stock.total_equity_end)]
    score["Free Cash Flow Yield"] = solvency.get_free_cash_flow_yield(stock.free_cash_flow,
                                                                      stock.market_cap)


    #VALUATION
    score["price_over_graham"] = [stock.reference_price/stock.graham_price]
    score["Net current asset per share over price"] = [stock.net_current_assets/stock.market_cap]

    score['EPS over price'] = [stock.EPS/stock.reference_price]
    score['Revenue per Share'] = [valuation.get_revenue_per_share(stock.revenue,
                                                                  stock.n_shares)]

    score["PE"] = [stock.PE]
    score["ROE"] = [stock.ROE]
    score["PB"] = [stock.PB]
    score["PS"] = [stock.PS]
    score['Book Value per Share'] = [valuation.get_book_value_per_share(stock.stockholder_equity,
                                                                        0,
                                                                        stock.n_shares)]
    score["Price to cash flow"] = [stock.price_to_cash_flow]
    score["Price to free cash flow"] = [stock.price_to_free_cash_flow]
    score['Net cash over market cap'] = [stock.net_cash_per_share/stock.reference_price]
    score['ROCE'] = [stock.ROCE]
    score['Net income per employee'] = [stock.net_income_per_employee]
    score['Revenue per employee'] = [stock.revenue_per_employee]
    score['Fulltime employee'] = [stock.full_time_employees]
    score['market_cap'] = [stock.market_cap]
    score["Return on Assets"] = [stock.ROA]

    #score['full_object'] = [stock]
    return score
