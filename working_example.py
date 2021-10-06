from conversion_rates import get_conversion_rates_df

from_currency_list = ['USD', 'JPY']
to_currency_list = ['ILS', 'TRY']
startPeriod = '2005-03-26'
endPeriod = '2018-10-31'


if __name__ == "__main__":
    get_conversion_rates_df(from_currency_list, to_currency_list, startPeriod, endPeriod)

