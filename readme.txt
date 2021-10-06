Build a proccess in python which will pull exchange rates from the following url:
https://sdw-wsrest.ecb.europa.eu/help/

The proccess must meet the following conditions:
1. According to a parameter (or multiple), return all the conversion rates from every currency to all other currencies in the parameter. The parameters are:
from_currency_list
to_currency_list
from_date
to_date

Expected output: result of daily conversion rates for the requested currencies.

If the requested date does not return a conversion, return the conversion for the nearest date before the requested date.

The data should be outputted to any sort of text file with a unique identifier and a date. 
