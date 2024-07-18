import numpy as np
import pandas as pd

from datetime import datetime
import logging

from yahooquery import Ticker
from invest.ratios import liquidity
import os

logger = logging.getLogger()

TOTAL_LIAB = "TotalLiabilitiesNetMinorityInterest"
OPERATING_CASHFLOW = 'OperatingCashFlow'#"Total Cash From Operating Activities"
FREE_CASHFLOW = 'FreeCashFlow'
CASH = 'Cash'
CASH_AND_EQ = 'CashAndCashEquivalents'
INTEREST_EXPENSE = 'InterestExpense'
TOT_EQUITY = "TotalStockholderEquity"
INTANGIBLE_ASSETS = "IntangibleAssets"

class Stock:
    def __init__(self, isin : str):
        self.isin = isin

        self.scheda = pd.read_csv(os.path.join('symbols', 'isin_transcode', f'{isin}.csv'))
        self.yahoo_code = f"{self.scheda['Codice Alfanumerico'].item()}.MI"

        self._name = None
        self.ticker = Ticker(self.yahoo_code.upper())
        self._sector = None
        self._reference_price = None
        self._hist = None
        self._info = None
        self._financials = None
        self._yearly_financials = None
        self._quarterly_financials = None
        self._balance_sheet = None
        self._cashflow = None
        self._revenue_and_earning = None
        self._quarterly_balance_sheet = None
        self._n_shares = None
        self._quarterly_cashflow = None
        self._net_income = None
        self.quot_date =  datetime.now()
        self._last_financial_data = None
        self._total_assets = None
        self._total_liabilities = None
        self._intangible_assets = None
        
        self._pretax_income = None
        self._EBIT = None

    def name_option(self, key):
        if key in self.business_summary:
            option = self.business_summary.split(' '+ key)[0] + ' ' + key
        else:
            option = self.business_summary
        return option

    @property
    def business_summary(self):
        return self.ticker.summary_profile[self.yahoo_code]['longBusinessSummary']


    @property
    def name(self):
        if self._name is None:
            self._name = self.get_name()
        return self._name

    @property
    def last_financial_data(self):
        if self._last_financial_data is None:
            self._last_financial_data = self.ticker.financial_data[self.yahoo_code]
        return self._last_financial_data
    
    @staticmethod
    def company_suffixes():
        suff_list = ['S.p.A',
                     'SpA',
                     'Spa',
                     'S.P.A.',
                     'Sa',
                     'S.p.A.',
                     'N.V.',
                     'S.A.',
                     'S.I.M.p.A.',
                     'SA',
                     'Corp.',
                     'società per azioni',
                     'Société anonyme']
        return list(map(lambda x : x + ',', suff_list)) +  list(map(lambda x : x + ' ', suff_list))

    def get_name(self):
        try:
            options = list(map(self.name_option, self.company_suffixes()))
            name = min(options, key=len)
            if name == self.business_summary:
                return self.business_summary.split(",")[0]
            else:
                return name[:-1]
        except:
            return self.yahoo_code

    @property
    def info(self):
        if self._info is None:
            self._info = (self.ticker.summary_detail[self.yahoo_code] |
                          self.ticker.financial_data[self.yahoo_code] |
                          self.ticker.asset_profile[self.yahoo_code])
        return self._info

    @property
    def sector(self):
        if self._sector is None:
            self._sector = self.get_info('sector')
        return self._sector
        
    @property
    def yearly_financials(self):
        if self._yearly_financials is None:
            self._yearly_financials = self.ticker.all_financial_data(frequency='a').set_index('asOfDate')
        return self._yearly_financials

    @property
    def quarterly_financials(self):
        if self._quarterly_financials is None:
            self._quarterly_financials = self.ticker.all_financial_data(frequency='q').set_index('asOfDate')
        return self._quarterly_financials

    @property
    def yearly_balance_sheet(self):
        if self._balance_sheet is None:
            self._balance_sheet = self.ticker.balance_sheet(frequency='a').set_index('asOfDate')
        return self._balance_sheet

    @property
    def quarterly_balance_sheet(self):
        if self._quarterly_balance_sheet is None:
            self._quarterly_balance_sheet = self.ticker.balance_sheet(frequency='q').set_index('asOfDate')
        return self._quarterly_balance_sheet

    @property
    def yearly_cashflow(self):
        if self._cashflow is None:
            self._cashflow = self.ticker.cash_flow(frequency="a").set_index('asOfDate')
        return self._cashflow

    @property
    def quarterly_cashflow(self):
        if self._quarterly_cashflow is None:
            self._quarterly_cashflow = self.ticker.cash_flow(frequency="q").set_index('asOfDate')
        return self._quarterly_cashflow

    @property
    def revenue_and_earning(self):
        if self._revenue_and_earning is None:
            self._revenue_and_earning = self.ticker.earnings
        return self._revenue_and_earning

    @property
    def n_shares(self):
        if self._n_shares is None:
            self._n_shares = (pd.concat([self.yearly_balance_sheet['ShareIssued'],
                                        self.quarterly_balance_sheet['ShareIssued']])
                                .reset_index().sort_values(by='asOfDate').dropna()
                                .tail(1)['ShareIssued'].item())
        return self._n_shares

    @property
    def hist(self):
        if self._hist is None:
            self._hist = self.ticker.history(period="max").reset_index().drop(columns='symbol')
            self._hist.columns = [col.capitalize() for col in self._hist.columns]
            try:
                self._hist['Date'] = self._hist['Date'].dt.tz_localize(None)
            except: pass
            self._hist = self._hist.set_index('Date')
        return self._hist

    @property
    def dividends(self):
        try:
            return self.hist["Dividends"].replace({0: None}).dropna()
        except:
            return pd.DataFrame()

    @property
    def annual_dividends(self):
        try:
            dividends = self.dividends.reset_index()
            dividends["Year"] = pd.to_datetime(dividends["Date"]).dt.year
            return pd.pivot_table(dividends,
                                  index="Year",
                                  values="Dividends",
                                  aggfunc="sum").reset_index()
        except:
            return pd.DataFrame()

    def get_info(self, label):
        try:
            return  self.info[label]
        except:
            return None

    @property
    def reference_price(self):
        if self._reference_price is None:
           self._reference_price = self.hist.tail(1)['Close'].item()
        return self._reference_price

    @property
    def sales(self):
        return self.market_cap/self.PS

    @property
    def PS(self):
        return self.get_info('priceToSalesTrailing12Months') or np.nan

    @property
    def PB(self):
        try:
            return self.ticker.key_stats[self.yahoo_code]['priceToBook']
        except Exception as e:
            print(e, e.__doc__)
            return self.reference_price/ self.book_value

    @property
    def market_cap(self):
        if (self.get_info("marketCap") is not None):
            return float(self.get_info("marketCap"))
        else:
            return self.reference_price * self.n_shares

    @property
    def price_to_tangible_book(self):
        return (self.total_assets - self.total_liabilities - self.intangible_assets)/self.market_cap

    @property
    def PTBV(self):
        return self.price_to_tangible_book


    @property
    def intangible_assets(self):
        if self._intangible_assets is None:
            try:
                self._intangible_assets = (pd.concat([self.yearly_balance_sheet['IntangibleAssets'],
                                                      self.quarterly_balance_sheet['IntangibleAssets']])
                                             .reset_index().sort_values(by='asOfDate').dropna()
                                             .set_index('asOfDate').tail(1)['IntangibleAssets'].item())
            except:
                self._intangible_assets = 0
        return self._intangible_assets

    @property
    def stockholder_equity(self):
        return self.total_assets - self.total_liabilities

    @property
    def total_assets(self):
        if self._total_assets is None:
            self._total_assets = (pd.concat([self.yearly_balance_sheet['TotalAssets'],
                                             self.quarterly_balance_sheet['TotalAssets']])
                                    .reset_index().sort_values(by='asOfDate').dropna()
                                    .set_index('asOfDate').tail(1)['TotalAssets'].item())
        return self._total_assets

    @property
    def total_liabilities(self):
        if self._total_liabilities is None:
            self._total_liabilities = (pd.concat([self.yearly_balance_sheet['TotalLiabilitiesNetMinorityInterest'],
                                                  self.quarterly_balance_sheet['TotalLiabilitiesNetMinorityInterest']])
                                         .reset_index().sort_values(by='asOfDate').dropna()
                                         .set_index('asOfDate').tail(1)['TotalLiabilitiesNetMinorityInterest'].item())
        return self._total_liabilities
    
    @property
    def earning_per_share(self):
        return self.net_income/self.market_cap

    @property
    def PE(self):
        if (self.get_info("trailingPE") is not None) and not isinstance(self.get_info("trailingPE"), dict):
            return float(self.get_info("trailingPE"))
        else:
            return self.market_cap/self.net_income

    @property
    def revenue_per_share(self):
        return self.revenue/self.n_shares

    @property
    def current_ratio(self):
        try:
            return self.last_financial_data['currentRatio']
        except:
            return liquidity.get_current_ratio(self.current_assets,
                                               self.current_liabilities)

    def _set_net_income(self):
        if (self.get_info("netIncomeToCommon") is not None) and not isinstance(self.get_info("netIncomeToCommon"), dict):
            return self.get_info("netIncomeToCommon")
        elif 'NetIncome' in self.yearly_financials:
            return (pd.concat([self.annualize_financials(self.quarterly_financials, 'NetIncome'),
                                  self.yearly_financials['NetIncome'].reset_index()])
                             .sort_values(by='asOfDate').dropna().tail(1)['NetIncome'].item())
        else:
            try:
                return self.net_income_from_pe()
            except:
                return self.net_income_from_roe()

    @property
    def net_income(self):
        if self._net_income is None:
            self._net_income = self._set_net_income()
        return self._net_income


    def net_income_from_pe(self):
        return self.market_cap/float(self.get_info("trailingPE"))

    def net_income_from_roe(self):
        return float(self.get_info("returnOnEquity"))*self.market_cap

    @property
    def graham_price(self):
        squared_graham = 22.5 * self.book_value * self.earning_per_share
        if squared_graham > 0:
            return (squared_graham) ** (1 / 2)
        else:
            return np.nan

    @property
    def ROA(self):
        if   (self.get_info("returnOnAssets") is not None):
            return float(self.get_info("returnOnAssets"))
        else:
            return self.net_income/self.total_assets

    @property
    def book_value(self):    
        try:
            return float(self.get_info("bookValue"))
        except Exception as e:
            print(f"{e}: {e.__doc__}")
            try:
                return self.ticker.key_stats[self.yahoo_code]['bookValue']
            except:
                return self.stockholder_equity/self.n_shares
    
    @property
    def ROE(self):
        return self.return_on_equity

    @property
    def price_to_book(self):
        return self.PB

    @property
    def full_time_employees(self):
        if self.get_info('fullTimeEmployees') is not None:
            return float(self.get_info('fullTimeEmployees'))
        else:
            return np.nan

    @property
    def return_on_equity(self):
        try:
           return float(self.get_info("returnOnEquity"))
        except Exception as e:
            logger.warn(f'{e} : {e.__doc__}')
            return self.net_income/self.stockholder_equity
    
    @property
    def inventory_begin(self):
        try:
            return self.financials['InventoryBeginning']
        except Exception as e:
            print(f"{e}: {e.__doc__}")
            return np.nan

    @property
    def inventory_end(self):
        return self.inventory

    @property
    def accounts_receivable(self):
        try:
            return (pd.concat([self.quarterly_financials['AccountsReceivable'],
                               self.yearly_financials['AccountsReceivable']]).reset_index()
                      .sort_values(by='asOfDate').dropna().tail(1)['AccountsReceivable'].item())
        except Exception as e:
            print(f"{e}: {e.__doc__}")
            return 0

    @property
    def accounts_payable(self):
        try:
            return (pd.concat([self.quarterly_financials['AccountsPayable'],
                               self.yearly_financials['AccountsPayable']]).reset_index()
                      .sort_values(by='asOfDate').dropna().tail(1)['AccountsPayable'].item())
        except Exception as e:
            print(f"{e}: {e.__doc__}")
            return 0

    @property
    def total_equity(self):
        try:
            return (pd.concat([self.quarterly_financials['TotalEquityGrossMinorityInterest'],
                               self.yearly_financials['TotalEquityGrossMinorityInterest']]).reset_index()
                     .sort_values(by='asOfDate').dropna().tail(1)['TotalEquityGrossMinorityInterest'].item())
        except Exception as e:
            print(f"{e}: {e.__doc__}")
            return np.nan


    @property
    def cash_and_equivalents(self):
        try:
            return (pd.concat([self.quarterly_financials['CashAndCashEquivalents'],
                               self.yearly_financials['CashAndCashEquivalents']]).reset_index()
                      .sort_values(by='asOfDate').dropna().tail(1)['CashAndCashEquivalents'].item())
        except Exception as e:
            print(f"{e}: {e.__doc__}")
            return np.nan


    @property
    def operating_income(self):
        try:
            return (pd.concat([self.yearly_financials['OperatingIncome'].reset_index(),
                                              self.annualize_financials(self.quarterly_financials, 
                                                                        'OperatingIncome')])
                                         .reset_index().sort_values(by='asOfDate').dropna()
                                         .set_index('asOfDate').tail(1)['OperatingIncome'].item())
        except Exception as e:
            print(f"{e}: {e.__doc__}")
            return np.nan

    @property
    def depreciation_and_amortization(self):
        try:
            if 'DepreciationAndAmortization' in self.yearly_financials.columns:
                label = 'DepreciationAndAmortization'
            else:
                label = 'DepreciationAmortizationDepletion'
            return (pd.concat([self.yearly_financials[label].reset_index(),
                                              self.annualize_financials(self.quarterly_financials, 
                                                                        label)])
                                         .reset_index().sort_values(by='asOfDate').dropna()
                                         .set_index('asOfDate').tail(1)[label].item())
        except Exception as e:
            print(f"{e}: {e.__doc__}")
            return np.nan

    @property
    def marketable_securities(self):
        try:
            return (pd.concat([self.quarterly_financials['AvailableForSaleSecurities'],
                               self.yearly_financials['AvailableForSaleSecurities']]).reset_index()
                      .sort_values(by='asOfDate').dropna().tail(1)['AvailableForSaleSecurities'].item())
        except Exception as e:
            print(f"{e}: {e.__doc__}")
            return 0

    @property
    def current_assets(self):
        try:
            return (pd.concat([self.quarterly_financials['CurrentAssets'],
                               self.yearly_financials['CurrentAssets']]).reset_index()
                      .sort_values(by='asOfDate').dropna().tail(1)['CurrentAssets'].item())
        except Exception as e:
            print(f"{e}: {e.__doc__}")
            if self.sector == 'Financial Services':
                return self.total_assets
            else:
                return np.nan

    @property
    def net_current_assets(self):
        return self.current_assets - self.current_liabilities

    @property
    def inventory(self):
        try:
            return (pd.concat([self.quarterly_financials['Inventory'],
                               self.yearly_financials['Inventory']]).reset_index()
                      .sort_values(by='asOfDate').dropna().tail(1)['Inventory'].item())
        except Exception as e:
            print(f"{e}: {e.__doc__}")
            return 0 #Insurance and banks do not have inventory

    @property
    def working_capital_per_share(self):
        return liquidity.get_working_capital(self.current_assets - self.current_liabilities) / self.n_shares

    @property
    def current_liabilities(self):
        try:
            return (pd.concat([self.quarterly_financials['CurrentLiabilities'],
                               self.yearly_financials['CurrentLiabilities']]).reset_index()
                      .sort_values(by='asOfDate').dropna().tail(1)['CurrentLiabilities'].item())
        except:
            if self.sector == 'Financial Services':
                return self.total_liabilities
            else:
                return np.nan

    @property
    def total_debt(self):
        if   (self.get_info("totalDebt") is not None) and not isinstance(self.get_info("totalDebt"), dict):
            return self.get_info("totalDebt")
        else:
            return self.long_term_debt + self.current_liabilities

    def find_longterm_debt_columns(self, df):
        if ('LongTermDebt' in df.columns):
            return df['LongTermDebt']
        else:
            result = df.filter(like='LongTermDebt')
            if len(result.columns):
                col = result.columns[0]
                return result.rename(columns={col : 'LongTermDebt'}).dropna()
            else:
                return pd.DataFrame()
            
        
    @property
    def long_term_debt(self):
        quarterly_longterm_debt = self.find_longterm_debt_columns(self.quarterly_financials)
        yearly_longterm_debt = self.find_longterm_debt_columns(self.yearly_financials)
        return (pd.concat([quarterly_longterm_debt,
                           yearly_longterm_debt]).reset_index()
                  .sort_values(by='asOfDate').dropna().tail(1)['LongTermDebt'].item())

    @property
    def net_cash_per_share(self):
        return (self.cash - self.total_debt) / self.n_shares

    @property
    def cash(self):
        if   (self.get_info("totalCash") is not None):
            return self.get_info("totalCash")
        else:
            if 'Cash' in self.yearly_financials.columns:
                label = 'Cash'
            elif 'CashAndCashEquivalents' in self.yearly_financials.columns:
                label = 'CashAndCashEquivalents'
            else: return np.nan
            return  (pd.concat([self.yearly_financials[label].reset_index(),
                                              self.annualize_financials(self.quarterly_financials, 
                                                                        label)])
                                         .reset_index().sort_values(by='asOfDate').dropna()
                                         .set_index('asOfDate').tail(1)[label].item())

    @property
    def payout_ratio(self):
        try:
            return  self.last_dividend / self.EPS #TODO yahooquery already provides this quantity, no need to calculate it
        except:
            return np.nan

    @property
    def last_dividend(self):
        if   (self.get_info("dividendRate") is not None) and not (isinstance(self.get_info("dividendRate"), dict)):
            return  self.get_info("dividendRate")
        elif len(self.annual_dividends):
            return self.annual_dividends.tail(1)['Dividends'].item()
        else:
            return 0


    @property
    def dividend_yeld(self):
        return  self.last_dividend/self.reference_price

    @property
    def operating_cash_flow(self):
        if   (self.get_info("operatingCashflow") is not None) and not isinstance(self.get_info("operatingCashflow"), dict):
            return float(self.get_info("operatingCashflow"))
        else:
            try:
                return (pd.concat([self.yearly_financials['OperatingCashFlow'].reset_index(),
                                              self.annualize_financials(self.quarterly_financials, 
                                                                        'OperatingCashFlow')])
                                         .reset_index().sort_values(by='asOfDate').dropna()
                                         .set_index('asOfDate').tail(1)['OperatingCashFlow'].item())
            except:
                return np.nan

    @property
    def price_to_cash_flow(self):
        try:
            return self.market_cap/ self.operating_cash_flow
        except:
            return np.nan

    @property
    def price_to_free_cash_flow(self):
        return self.market_cap / self.free_cash_flow

    @property
    def free_cash_flow(self):
        try:
            return float(self.get_info("freeCashflow"))
        except:
            try:
                return (pd.concat([self.yearly_financials['FreeCashFlow'].reset_index(),
                                              self.annualize_financials(self.quarterly_financials, 
                                                                        'FreeCashFlow')])
                                         .reset_index().sort_values(by='asOfDate').dropna()
                                         .set_index('asOfDate').tail(1)['FreeCashFlow'].item())
            except:
                try:
                    return self.operating_cash_flow - self.capital_expenditures
                except:
                    return np.nan

    @property
    def capital_expenditures(self):
        return self.tail(1).cashflow["CapitalExpenditures"]

    @property
    def revenue(self):
        if   (self.get_info("totalRevenue") is not None) and not isinstance(self.get_info("totalRevenue"), dict):
            return self.get_info("totalRevenue")
        else:
            return (pd.concat([self.yearly_financials['TotalRevenue'].reset_index(),
                                              self.annualize_financials(self.quarterly_financials, 
                                                                        'TotalRevenue')])
                                         .reset_index().sort_values(by='asOfDate').dropna()
                                         .set_index('asOfDate').tail(1)['TotalRevenue'].item())

    @property
    def net_income_per_employee(self):
        return self.net_income/self.full_time_employees

    @property
    def revenue_per_employee(self):
        return  self.revenue/self.full_time_employees
    
    @property
    def earning_per_share(self):
        try:
            return self.reference_price/self.PE
        except:
            return  self.net_income/self.n_shares

    @property
    def EPS(self):
        return self.earning_per_share

    @property
    def ROCE(self):
        return self.EBIT/(self.total_assets - self.current_liabilities)

    @property
    def EBIT(self):
        if self._EBIT is None:
            try:
                self._EBIT = (pd.concat([self.annualize_financials(self.quarterly_financials, 'EBIT'),
                                         self.yearly_financials['EBIT'].reset_index()])
                                .sort_values(by='asOfDate').dropna().tail(1)['EBIT'].item())
            except:
                logger.warning('EBIT column not found, recomputing from other quantities')
                self._EBIT = self.pretax_income + self.interest_expense
        return self._EBIT

    @property
    def pretax_income(self):
        if self._pretax_income is None:
            self._pretax_income = (pd.concat([self.yearly_financials['PretaxIncome'].reset_index(),
                                              self.annualize_financials(self.quarterly_financials, 
                                                                        'PretaxIncome')])
                                         .reset_index().sort_values(by='asOfDate').dropna()
                                         .set_index('asOfDate').tail(1)['PretaxIncome'].item())
        return self._pretax_income

    @property
    def interest_expense(self):
        try:
            return self.yearly_financials.tail(1)[INTEREST_EXPENSE].item()
        except Exception as e:
            print(f"{e}: {e.__doc__}")
            return 0

    def annualize_financials(self, financials : pd.DataFrame, label : str):
        try:
            period = int(financials['periodType'].unique().item().replace('M', ''))
            variable = financials[label].dropna()
            if len(variable) >= int(12/period):
                results = variable.reset_index().tail(1)
                results[label] = variable.tail(int(12/period)).sum()
                return results
            else:
                return pd.DataFrame()
        except KeyError:
            logger.warn("Quarterly data not found! Using yearly")
            return self.yearly_financials[label].reset_index().tail(1)
    