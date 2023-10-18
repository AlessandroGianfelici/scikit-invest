import numpy as np
import pandas as pd

from datetime import datetime
import logging

from yahooquery import Ticker
from invest.ratios import efficiency, liquidity, profitability, solvency, valuation


logger = logging.getLogger()

EBIT = 'EBIT'
ASSETS = "TotalAssets"
TOTAL_LIAB = "TotalLiabilitiesNetMinorityInterest"
OPERATING_CASHFLOW = 'OperatingCashFlow'#"Total Cash From Operating Activities"
FREE_CASHFLOW = 'FreeCashFlow'
CASH = 'Cash'
CASH_AND_EQ = 'CashAndCashEquivalents'
INTEREST_EXPENSE = 'InterestExpense'
TOT_EQUITY = "TotalStockholderEquity"
INTANGIBLE_ASSETS = "IntangibleAssets"

class Stock:
    def __init__(self, code: str, name: str = None, quot_date=None, granularity='q'):
        self.code = code
        self._name = name
        self.ticker = Ticker(code)
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
        self.is_last = (quot_date is None)
        self.granularity =granularity
        self.quot_date = quot_date or datetime.now()

    def name_option(self, key):
        if key in self.business_summary:
            option = self.business_summary.split(' '+ key)[0] + ' ' + key
        else:
            option = self.business_summary
        return option

    @property
    def business_summary(self):
        return self.ticker.summary_profile[self.code]['longBusinessSummary']


    @property
    def name(self):
        if self._name is None:
            self._name = self.get_name()
        return self._name

    def get_name(self):
        try:
            options = list(map(self.name_option, ['S.p.A.',
                                                  'SpA',
                                                  'Spa',
                                                  'S.P.A.',
                                                  'Sa',
                                                  'S.p.A.',
                                                  'N.V.',
                                                  'S.A.',
                                                  'S.I.M.p.A.',
                                                  'società per azioni',
                                                  'Société anonyme']))
            name = min(options, key=len)
            if name == self.business_summary:
                return self.business_summary.split(",")[0]
            else:
                return name
        except:
            return self.code

    @property
    def info(self):
        if self._info is None:
            self._info = (self.ticker.summary_detail[self.code] |
                          self.ticker.financial_data[self.code] |
                          self.ticker.asset_profile[self.code])
        return self._info

    @property
    def financials(self):
        if self._financials is None:
            self._financials = self.ticker.all_financial_data(frequency=self.granularity).set_index('asOfDate')
            if (self.granularity == 'q') and (len(self._financials) == 0):
                logger.warn("WARNING: no quarterly data found! Using yearly financials")
                self._financials = self.ticker.all_financial_data(frequency='a').set_index('asOfDate')
            self._financials['TotalAssetsBeginning'] = self._financials['TotalAssets'].shift()
            try:
                self._financials['InventoryBeginning'] = self._financials['Inventory'].shift()
            except: pass
            self._financials['AccountsReceivableBeginning'] = self._financials['AccountsReceivable'].shift()
        return self._financials.fillna(method='ffill')

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
    def balance_sheet(self):
        if self._balance_sheet is None:
            self._balance_sheet = self.ticker.balance_sheet(frequency='a').set_index('asOfDate')
        return self._balance_sheet

    @property
    def quarterly_balance_sheet(self):
        if self._quarterly_balance_sheet is None:
            self._quarterly_balance_sheet = self.ticker.balance_sheet(frequency='q').set_index('asOfDate')
        return self._quarterly_balance_sheet

    @property
    def cashflow(self):
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
            self._n_shares = self.balance_sheet['ShareIssued'].tail(1).item()
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
            try:
                self._hist = self._hist.loc[pd.to_datetime(self._hist.index) <= pd.to_datetime(self.quot_date)]
            except:
                pass
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
                                  aggfunc=sum).reset_index()
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
        return self.info['priceToSalesTrailing12Months']

    @property
    def PB(self):
        return self.reference_price/ self.book_value

    @property
    def market_cap(self):
        if self.is_last and (self.get_info("marketCap") is not None):
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
        try:
            return self.last_before_quot_date(self.balance_sheet.index)[INTANGIBLE_ASSETS]
        except:
            return 0

    @property
    def stockholder_equity(self):
        try:
            return self.last_before_quot_date(self.financials)[TOT_EQUITY]
        except:
            return self.total_assets - self.total_liabilities

    @property
    def total_assets(self):
        try:
            return self.last_before_quot_date(self.financials['TotalAssets'])
        except Exception as e:
            print(f"{e}: {e.__doc__}")
            return np.nan

    @property
    def total_liabilities(self):
        try:
            return self.last_before_quot_date(self.financials[TOTAL_LIAB])
        except Exception as e:
            print(f"{e}: {e.__doc__}")
            return np.nan

    @property
    def earning_per_share(self):
        return self.net_income/self.market_cap

    @property
    def PE(self):
        if self.is_last and (self.get_info("trailingPE") is not None) and not isinstance(self.get_info("trailingPE"), dict):
            return float(self.get_info("trailingPE"))
        else:
            return self.market_cap/self.net_income

    def _set_net_income(self):
        if self.is_last and (self.get_info("netIncomeToCommon") is not None) and not isinstance(self.get_info("netIncomeToCommon"), dict):
            return self.get_info("netIncomeToCommon")
        elif self.is_last and self.granularity == 'q':
            try:
                return self.financials.reset_index()[['NetIncome']].tail(4).sum().values.item()
            except:
                if self.is_last and (self.get_info("trailingPE") is not None) and not isinstance(self.get_info("trailingPE"), dict):
                    return self.net_income_from_pe()
                elif self.is_last and (self.get_info("returnOnEquity") is not None) and not isinstance(self.get_info("returnOnEquity"), dict):
                    return self.net_income_from_roe()
                else:
                    return np.nan
        else:
            try:
                return self.last_before_quot_date(self.yearly_financials)['NetIncome']
            except:
                return self.net_income_from_pe()

    @property
    def net_income(self):
        if self._net_income is None:
            self._net_income = self._set_net_income()
        return self._net_income


    def net_income_from_pe(self):
        return self.market_cap/self.PE

    def net_income_from_roe(self):
        return self.ROE*self.market_cap

    @property
    def graham_price(self):
        squared_graham = 22.5 * self.book_value * self.earning_per_share
        if squared_graham > 0:
            return (squared_graham) ** (1 / 2)
        else:
            return np.nan

    @property
    def ROA(self):
        if self.is_last and (self.get_info("returnOnAssets") is not None):
            return float(self.get_info("returnOnAssets"))
        else:
            return self.net_income/self.total_assets

    @property
    def book_value(self):
        if self.is_last:
            try:
                return float(self.get_info("bookValue"))
            except Exception as e:
                print(f"{e}: {e.__doc__}")
                return self.stockholder_equity/self.n_shares
        else:
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
        if self.is_last:
            try:
                return float(self.get_info("returnOnEquity"))
            except Exception as e:
                logger.warn(f'{e} : {e.__doc__}')
                return self.net_income/self.stockholder_equity
        else:
            return self.net_income/self.stockholder_equity

    @property
    def inventory_begin(self):
        try:
            return self.last_before_quot_date(self.financials)['InventoryBeginning']
        except Exception as e:
            print(f"{e}: {e.__doc__}")
            return np.nan

    @property
    def inventory_end(self):
        return self.inventory

    @property
    def accounts_receivable(self):
        try:
            return self.last_before_quot_date(self.financials)['AccountsReceivable']
        except Exception as e:
            print(f"{e}: {e.__doc__}")
            return np.nan

    @property
    def accounts_receivable_begin(self):
        try:
            return self.last_before_quot_date(self.financials)['AccountsReceivableBeginning']
        except Exception as e:
            print(f"{e}: {e.__doc__}")
            return np.nan

    @property
    def accounts_receivable_end(self):
        return self.accounts_receivable

    @property
    def accounts_payable(self):
        try:
            return self.last_before_quot_date(self.financials)['AccountsPayable']
        except Exception as e:
            print(f"{e}: {e.__doc__}")
            return np.nan

    @property
    def total_equity(self):
        try:
            return self.last_before_quot_date(self.financials)['TotalEquityGrossMinorityInterest']
        except Exception as e:
            print(f"{e}: {e.__doc__}")
            return np.nan

    @property
    def total_equity_begin(self):
        try:
            return self.last_before_quot_date(self.financials.shift())['TotalEquityGrossMinorityInterest']
        except Exception as e:
            print(f"{e}: {e.__doc__}")
            return np.nan

    @property
    def total_equity_end(self):
        return self.total_equity

    @property
    def cash_and_equivalents(self):
        try:
            return self.last_before_quot_date(self.financials)['CashAndCashEquivalents']
        except Exception as e:
            print(f"{e}: {e.__doc__}")
            return np.nan


    @property
    def operating_income(self):
        try:
            if self.is_last and (self.granularity == 'q'):
                try:
                    return self.quarterly_financials[['OperatingIncome']].tail(4).sum().values.item()
                except:
                    self.last_before_quot_date(self.yearly_financials)['OperatingIncome']
            else:
                return self.last_before_quot_date(self.yearly_financials)['OperatingIncome']
        except Exception as e:
            print(f"{e}: {e.__doc__}")
            return np.nan

    @property
    def depreciation_and_amortization(self):
        try:
            if 'DepreciationAndAmortization' in self.financials.columns:
                return self.last_before_quot_date(self.financials)['DepreciationAndAmortization']
            else:
                return self.last_before_quot_date(self.financials)['DepreciationAmortizationDepletion']
        except Exception as e:
            print(f"{e}: {e.__doc__}")
            return np.nan

    @property
    def marketable_securities(self):
        try:
            return self.last_before_quot_date(self.financials)['AvailableForSaleSecurities']
        except Exception as e:
            print(f"{e}: {e.__doc__}")
            return 0

    @property
    def total_assets_begin(self):
        try:
            return self.last_before_quot_date(self.financials)['TotalAssetsBeginning']
        except Exception as e:
            print(f"{e}: {e.__doc__}")
            return np.nan

    @property
    def total_assets_end(self):
        return self.total_assets

    @property
    def current_assets(self):
        try:
            return self.last_before_quot_date(self.financials)['CurrentAssets']
        except Exception as e:
            print(f"{e}: {e.__doc__}")
            return np.nan

    @property
    def net_current_assets(self):
        return self.current_assets - self.current_liabilities

    @property
    def inventory(self):
        try:
            return self.last_before_quot_date(self.financials)["Inventory"]
        except Exception as e:
            print(f"{e}: {e.__doc__}")
            return 0 #Insurance and banks do not have inventory

    @property
    def working_capital_per_share(self):
        return liquidity.get_working_capital(self.current_assets - self.current_liabilities) / self.n_shares

    @property
    def current_liabilities(self):
        try:
            return self.last_before_quot_date(self.financials['CurrentLiabilities'])
        except:
            return np.nan

    @property
    def total_debt(self):
        if self.is_last and (self.get_info("totalDebt") is not None) and not isinstance(self.get_info("totalDebt"), dict):
            return self.get_info("totalDebt")
        else:
            return self.last_before_quot_date(self.yearly_financials)[['LongTermDebt', 'CurrentLiabilities']].sum()

    @property
    def net_cash_per_share(self):
        return (self.cash - self.total_debt) / self.n_shares

    @property
    def cash(self):
        if self.is_last and (self.get_info("totalCash") is not None):
            return self.get_info("totalCash")
        else:
            try:
                return self.last_before_quot_date(self.financials)[CASH]
            except:
                return self.last_before_quot_date(self.financials)[CASH_AND_EQ]

    @property
    def payout_ratio(self):
        try:
            return  self.last_dividend / self.EPS #TODO yahooquery already provides this quantity, no need to calculate it
        except:
            return np.nan

    @property
    def last_dividend(self):
        if self.is_last and (self.get_info("dividendRate") is not None) and not (isinstance(self.get_info("dividendRate"), dict)):
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
        if self.is_last and (self.get_info("operatingCashflow") is not None) and not isinstance(self.get_info("operatingCashflow"), dict):
            return float(self.get_info("operatingCashflow"))
        else:
            return float( self.last_before_quot_date(self.cashflow)[OPERATING_CASHFLOW])

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
            if self.is_last:
                return float(self.get_info("freeCashflow"))
            else:
                raise TypeError
        except:
            try:
                return self.last_before_quot_date(self.financials)[FREE_CASHFLOW]
            except:
                try:
                    return self.operating_cash_flow - self.capital_expenditures
                except:
                    return np.nan

    @property
    def capital_expenditures(self):
        return self.last_before_quot_date(self.cashflow)["CapitalExpenditures"]

    @property
    def revenue(self):
        if self.is_last and (self.get_info("totalRevenue") is not None) and not isinstance(self.get_info("totalRevenue"), dict):
            return self.get_info("totalRevenue")
        else:
            return self.last_before_quot_date(self.yearly_financials)["TotalRevenue"]

    @property
    def net_income_per_employee(self):
        return self.net_income/self.full_time_employees

    @property
    def revenue_per_employee(self):
        return  self.revenue/self.full_time_employees
    @property
    def earning_per_share(self):
        try:
            if self.is_last:
                return self.reference_price/self.PE
            else:
                raise ValueError
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
        try:
            return self.last_before_quot_date(self.quarterly_financials)[EBIT]
        except:
            if self.is_last and (EBIT in self.financials.columns):
                return self.last_before_quot_date(self.financials)[EBIT]
            else:
                return self.pretax_income + self.interest_expense

    @property
    def pretax_income(self):
        try:
            return self.last_before_quot_date(self.yearly_financials)['PretaxIncome']
        except Exception as e:
            print(f"{e}: {e.__doc__}")
            return np.nan

    @property
    def interest_expense(self):
        try:
            return self.last_before_quot_date(self.yearly_financials)[INTEREST_EXPENSE]
        except Exception as e:
            print(f"{e}: {e.__doc__}")
            return 0

    @staticmethod
    def last_before(df, date):
        return df.loc[pd.to_datetime(df.index) < date].iloc[-1]

    def last_before_quot_date(self, df):
        return self.last_before(df, self.quot_date)
