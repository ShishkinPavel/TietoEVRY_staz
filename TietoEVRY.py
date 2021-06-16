from json import loads
from requests import get
from jmespath import search
from heapq import nsmallest, nlargest
from more_itertools import chunked

JSON_LINK = loads(get("https://json-stat.org/samples/oecd.json").text)
YEARS = list(search('dimension.year.category.index', JSON_LINK).keys())
COUNTRIES = search('dimension.area.category.label.*', JSON_LINK)

# The bottom line is that I have the count of chunk of values == number of years,
# and the count of values in the chunk == count of countries. Then I can use indexes for search
VALUES_CHUNKED_BY_YEARS = list(chunked(search('value', JSON_LINK), len(COUNTRIES)))


def best3_and_worth3_unemployment_rate_by_years():
    for i in VALUES_CHUNKED_BY_YEARS:
        print(YEARS[VALUES_CHUNKED_BY_YEARS.index(i)] + "\nLowest unemployment rate:")
        for value in nsmallest(3, i):
            print(COUNTRIES[i.index(value)] + ': ' + str(value) + '%')
        print("\nHighest unemployment rate:")
        for value in nlargest(3, i):
            print(COUNTRIES[i.index(value)] + ': ' + str(value) + '%')
        print('\n')


if __name__ == '__main__':
    best3_and_worth3_unemployment_rate_by_years()
