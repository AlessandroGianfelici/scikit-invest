import numpy as np
import pandas as pd

from invest.utils import file_folder_exists, select_or_create
import logging

from yahooquery import Ticker
from invest.ratios import liquidity
import os
from invest.data_loader import euronext_milan

logger = logging.getLogger()

TOTAL_LIAB = "TotalLiabilitiesNetMinorityInterest"
OPERATING_CASHFLOW = 'OperatingCashFlow'#"Total Cash From Operating Activities"
FREE_CASHFLOW = 'FreeCashFlow'
CASH = 'Cash'
CASH_AND_EQ = 'CashAndCashEquivalents'
INTEREST_EXPENSE = 'InterestExpense'
TOT_EQUITY = "TotalStockholderEquity"
INTANGIBLE_ASSETS = "IntangibleAssets"

def load_scheda(isin):
    return pd.read_csv(os.path.join('invest', 
                                    'symbols', 
                                    'scheda', 
                                   f'{isin}.csv'))

def load_financials(isin):
    return pd.read_csv(os.path.join('invest', 
                                    'symbols', 
                                    'financials', 
                                   f'{isin}.csv')).set_index('Millenium').T.rename(columns={'Income from ordinary activities' : 'Proventi dalle attività ordinarie'})

class Stock:
    def __init__(self, isin : str):
        self.isin = isin

        self.scheda = load_scheda(isin)
        self.financials = load_financials(isin)

        self.code = self.scheda['Codice Alfanumerico'].item()
        self.yahoo_code = f"{self.code}.MI"
        self.ticker = Ticker(self.yahoo_code.upper())

        self.name = euronext_milan[isin]
        self.sector = self.get_super_sector()
        self.financial_coefficient = self.get_financial_coefficient()
        self._reference_price = None

        self._yearly_financials = None
        self._quarterly_financials = None
        
        self._yearly_balance_sheet = None
        self._quarterly_balance_sheet = None

        self._yearly_cashflow = None
        self._quarterly_cashflow = None
        
        self._yearly_income_statement = None
        self._quarterly_income_statement = None

        self._hist = None
        self._info = None
        self._n_shares = None
        self._quarterly_cashflow = None
        self._net_income = None
        self._last_financial_data = None
        self._total_assets = None
        self._total_liabilities = None
        self._intangible_assets = None
        self._revenue_and_earning = None
        
        self._pretax_income = None
        self._EBIT = None

    def get_financial_coefficient(self):
        udm_string = self.financials.head(1)['Valuta e unità di misura'].item()
        match udm_string:
            case 'EUR - unità': return 1
            case 'EUR - migliaia': return 1000
            case 'EUR - milioni': return 1000000
            case _ : raise ValueError

    def get_super_sector(self):
        try:
            return self.scheda['Super Sector'].item()
        except:
            return 'NA'


    @property
    def website(self):
        try:
            return self.ticker.summary_profile[self.yahoo_code]['website']
        except:
            return ''

    @property
    def business_summary(self):
        try:
            return self.ticker.summary_profile[self.yahoo_code]['longBusinessSummary']
        except:
            return ''
        
    def load_financials(self, frequency):
        new_yearly_financial = self.ticker.all_financial_data(frequency=frequency).reset_index()
        
        filepath = os.path.join(select_or_create(os.path.join('data', 'yahoo_fundamentals', self.isin)),
                                 f'{frequency}_financials.csv')
        if file_folder_exists(filepath):
            old_yearly_financial  = pd.read_csv(filepath)
        else:
            old_yearly_financial  = pd.DataFrame()
        yearly_financials = pd.concat([old_yearly_financial, new_yearly_financial])
        yearly_financials['asOfDate'] = pd.to_datetime(yearly_financials['asOfDate'], format='mixed')
        yearly_financials = yearly_financials.drop_duplicates(subset=['symbol', 'asOfDate', 'periodType'], keep='last')
        yearly_financials.to_csv(filepath, index=0)
        return yearly_financials

    @property
    def yearly_financials(self):
        if self._yearly_financials is None:
            self._yearly_financials = self.load_financials(frequency='a')
        return self._yearly_financials

    @property
    def quarterly_financials(self):
        if self._quarterly_financials is None:
            self._quarterly_financials = self.load_financials(frequency='q')
        return self._quarterly_financials

    def load_balance_sheet(self, frequency):
        new_yearly_financial = self.ticker.balance_sheet(frequency=frequency).reset_index()
        
        filepath = os.path.join(select_or_create(os.path.join('data', 'yahoo_fundamentals', self.isin)),
                                 f'{frequency}_balance_sheet.csv')
        if file_folder_exists(filepath):
            old_yearly_financial  = pd.read_csv(filepath)
        else:
            old_yearly_financial  = pd.DataFrame()

        yearly_financials = pd.concat([old_yearly_financial, new_yearly_financial])
        yearly_financials['asOfDate'] = pd.to_datetime(yearly_financials['asOfDate'], format='mixed')
        yearly_financials = yearly_financials.drop_duplicates(subset=['symbol', 'asOfDate', 'periodType'], keep='last')
        return yearly_financials

    @property
    def yearly_balance_sheet(self):
        if self._yearly_balance_sheet is None:
            self._yearly_balance_sheet = self.load_balance_sheet(frequency='a')
        return self._yearly_balance_sheet

    @property
    def quarterly_balance_sheet(self):
        if self._quarterly_balance_sheet is None:
            self._quarterly_balance_sheet = self.load_balance_sheet(frequency='q')
        return self._quarterly_balance_sheet
    
    def load_cashflow(self, frequency):
        new_yearly_financial = self.ticker.cash_flow(frequency=frequency).reset_index()
        
        filepath = os.path.join(select_or_create(os.path.join('data', 'yahoo_fundamentals', self.isin)),
                                 f'{frequency}_cashflow.csv')
        if file_folder_exists(filepath):
            old_yearly_financial  = pd.read_csv(filepath)
        else:
            old_yearly_financial  = pd.DataFrame()
        yearly_financials = pd.concat([old_yearly_financial, new_yearly_financial])
        yearly_financials['asOfDate'] = pd.to_datetime(yearly_financials['asOfDate'], format='mixed')
        yearly_financials = yearly_financials.drop_duplicates(subset=['symbol', 'asOfDate', 'periodType'], keep='last')
        return yearly_financials

    @property
    def yearly_cashflow(self):
        if self._yearly_cashflow is None:
            self._yearly_cashflow = self.load_cashflow(frequency='a')
        return self._yearly_cashflow

    @property
    def quarterly_cashflow(self):
        if self._quarterly_cashflow is None:
            self._quarterly_cashflow = self.load_cashflow(frequency='q')
        return self._quarterly_cashflow

    def load_income_statement(self, frequency):
        new_yearly_financial = self.ticker.income_statement(frequency=frequency).reset_index()
        
        filepath = os.path.join(select_or_create(os.path.join('data', 'yahoo_fundamentals', self.isin)),
                                 f'{frequency}_income_statement.csv')
        if file_folder_exists(filepath):
            old_yearly_financial  = pd.read_csv(filepath)
        else:
            old_yearly_financial  = pd.DataFrame()
        yearly_financials = pd.concat([old_yearly_financial, new_yearly_financial])
        yearly_financials['asOfDate'] = pd.to_datetime(yearly_financials['asOfDate'], format='mixed')
        yearly_financials = yearly_financials.drop_duplicates(subset=['symbol', 'asOfDate', 'periodType'], keep='last')
        return yearly_financials

    @property
    def yearly_income_statement(self):
        if self._yearly_income_statement is None:
            self._yearly_income_statement = self.load_income_statement(frequency='a')
        return self._yearly_income_statement

    @property
    def quarterly_income_statement(self):
        if self._quarterly_income_statement is None:
            self._quarterly_income_statement = self.load_income_statement(frequency='q')
        return self._quarterly_income_statement

    @property
    def revenue_and_earning(self):
        if self._revenue_and_earning is None:
            self._revenue_and_earning = self.ticker.earnings
        return self._revenue_and_earning

    @property
    def n_shares(self):
        if self._n_shares is None:
            if self.get_info('sharesOutstanding') is not None:
                self._n_shares = self.get_info('sharesOutstanding')
            else:
                try:
                    self._n_shares = (pd.concat([self.yearly_balance_sheet,
                                                self.quarterly_balance_sheet])
                                        .reset_index().sort_values(by='asOfDate')[['ShareIssued']]
                                        .dropna().tail(1).values.item())
                except:
                    self._n_shares = int(self.market_cap/self.reference_price)
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
            return  self.ticker.key_stats[self.yahoo_code][label]
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
            self._total_assets = (pd.concat([self.yearly_balance_sheet[['asOfDate','periodType', 'TotalAssets']],
            self.quarterly_balance_sheet[['asOfDate','periodType', 'TotalAssets']]])
                .reset_index().sort_values(by='asOfDate').dropna()
                .set_index('asOfDate').tail(1)['TotalAssets'].item())
        return self._total_assets

    @property
    def total_liabilities(self):
        if self._total_liabilities is None:
            self._total_liabilities = (pd.concat([self.yearly_balance_sheet[['asOfDate', 'TotalLiabilitiesNetMinorityInterest']],
                                                  self.quarterly_balance_sheet[['asOfDate', 'TotalLiabilitiesNetMinorityInterest']]])
                                         .reset_index(drop=1).sort_values(by='asOfDate').dropna()
                                         .set_index('asOfDate').tail(1)['TotalLiabilitiesNetMinorityInterest'].values.item())
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
            return (pd.concat([self.annualize_financials(self.quarterly_financials.set_index('asOfDate'), 'NetIncome'),
            self.yearly_financials.set_index('asOfDate')['NetIncome']])).dropna().tail(1)['NetIncome'].item()
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
            return (pd.concat([self.quarterly_financials[['CurrentLiabilities']],
                               self.yearly_financials['CurrentLiabilities']]).reset_index()
                      .sort_values(by='asOfDate')[['CurrentLiabilities']]
                      .dropna().tail(1).values.item())
        except:
            if self.sector == 'BANCHE':
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
        quarterly_longterm_debt = self.find_longterm_debt_columns(self.quarterly_balance_sheet.set_index('asOfDate'))
        yearly_longterm_debt = self.find_longterm_debt_columns(self.yearly_balance_sheet.set_index('asOfDate'))
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
            return  (pd.concat([self.yearly_financials.set_index('asOfDate')[label].reset_index(),
                                              self.annualize_financials(self.quarterly_financials.set_index('asOfDate'), 
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
            return (self.yearly_income_statement[['asOfDate', 
                                                 'periodType', 
                                                 'TotalRevenue']]
                                                 .dropna().tail(1)['TotalRevenue'].values.item())

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
    