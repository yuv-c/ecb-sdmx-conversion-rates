import logging
import pandasdmx as sdmx
import itertools
import csv
import datetime
import uuid
import holidays

logging.basicConfig(level=logging.INFO)

WSDL_ADDR_STR = "https://sdw-wsrest.ecb.europa.eu/service/"
RESOURCE = "data"
FLOWREF = "EXR"  # Data flow key for exchange rates (FlowRef)

"""
key explanation by ECB: https://sdw-wsrest.ecb.europa.eu/help/
the frequency at which they are measured (e.g.: on a daily basis - code D),
the currency being measured (e.g.: US dollar - code USD),
the currency against which a currency is being measured (e.g.: Euro - code EUR),
the type of exchange rates (Foreign exchange reference rates - code SP00) and
the series variation (such as average or standardised measure for given frequency, code A).
"""


class CurrencyCodes(object):
    @classmethod
    def currency_code_dict(cls) -> dict:
        currency_code_dict = {}  # Create a dict of all currency codes to assert user input
        with open("currency_codes.csv", "r") as f:
            reader = csv.reader(f)
            for row in reader:
                currency_code_dict[row[2]] = True
        return currency_code_dict.copy()  # Return a copy to avoid modifying it


def assert_input_is_valid(from_currency_list: list, to_currency_list: list, from_date: str, to_date: str) -> bool:
    date_format = "%Y-%m-%d"

    try:
        for currency in from_currency_list + to_currency_list:
            assert CurrencyCodes.currency_code_dict().get(currency) is not None
    except AssertionError:
        raise ValueError("Currency %s supplied by user does not exist" % currency)

    try:
        from_date_obj = datetime.datetime.strptime(from_date,
                                                   date_format)  # Will raise Value Error if date format is not correct
        to_date_obj = datetime.datetime.strptime(to_date, date_format)
        assert from_date_obj <= to_date_obj
    except AssertionError:
        raise ValueError("from_date %s is greater than to_date %s" % from_date, to_date)

    try:
        assert from_currency_list != to_currency_list
    except AssertionError:
        raise ValueError("from_currency_list is equal to to_currency_list. Please select different currencies.")


def get_nearest_workday(from_date: str) -> str:
    ecb_holidays = holidays.CountryHoliday('ECB')  # Get the holidays of Euro central bank
    date_format = "%Y-%m-%d"

    try:
        assert from_date in ecb_holidays
    except AssertionError:
        from_date_object = datetime.datetime.strptime(from_date, date_format).date()
        logging.info("from_date %s is not an ECB workday. Selecting nearest earlier date", from_date)
        for i in range(1, 10):
            if from_date_object - datetime.timedelta(days=i) in ecb_holidays:
                nearest_date = str(from_date_object - datetime.timedelta(days=i))
                logging.info("Nearest date found: %s", nearest_date)
                return nearest_date


def get_conversion_rates_df(
        from_currency_list: list = ["EUR"],
        to_currency_list: list = ["USD"],
        from_date: str = str(datetime.date.today()),
        to_date: str = str(datetime.date.today())
) -> None:
    assert_input_is_valid(from_currency_list, to_currency_list, from_date, to_date)
    from_date = get_nearest_workday(from_date)
    list_of_currencies_to_compare = itertools.product(from_currency_list, to_currency_list)

    key = dict(CURRENCY=from_currency_list + to_currency_list, FREQ='D', CURRENCY_DENOM='EUR')
    ecb = sdmx.Request('ECB')
    parameters = {
        'startPeriod': from_date,  # Start date of the time series
        'endPeriod': to_date  # End of the time series
    }
    data_msg = ecb.data('EXR', key=key, params=parameters)
    df = sdmx.to_pandas(data_msg.data[0], datetime='TIME_PERIOD')
    for conversion_pair in list_of_currencies_to_compare:
        df["EXR: " + conversion_pair[0] + "/" + conversion_pair[1]] = df.D[conversion_pair[0]] / df.D[
            conversion_pair[1]]
    filename = str(datetime.date.today()) + str(uuid.uuid4())[0:8]
    df.to_excel(filename + ".xlsx")
