import json
import requests
from typing import Dict, List, Union, Optional

json_link = json.loads(requests.get("https://json-stat.org/samples/oecd.json").text)
ADType = Dict[str, Dict[str, List[str]]]
DBYType = Dict[str, List[str]]


# I made the information of the best and worst countries for all years,
# but you can uncomment a couple of lines at the very bottom and get
# a version working through the console with the choice of the year
# for which you need to get information.


# function for getting data for the selected year
def with_inp(my_json: Dict, year: str) -> str:
    ready_data: ADType = main(my_json)
    result: str = year + ":\n" + part_of_string(ready_data[year])
    return result


# function for getting data for the all years
def without_inp(my_json: Dict) -> str:
    ready_data: ADType = main(my_json)
    result: str = all_data_to_text(ready_data)
    return result


# I made it into a separate function to make it easier to test
def all_data_to_text(all_data: ADType) -> str:
    result: str = ""
    for every_i in all_data.keys():
        result += every_i + ":\n" + part_of_string(all_data[every_i])
    return result


# this part is the same when getting information for all
# years and for one separate one, so I put it in a separate function
def part_of_string(dict_by_year: DBYType) -> str:
    result: str = ""
    for i in dict_by_year.keys():
        result += "   " + i + ":" + "\n"

        count: int = 0
        prev: Optional[float] = None
        for j in dict_by_year[i]:
            # a sequence number is awarded to each unique element,
            # so I compare with the previous one and
            # increment it by 1 if it is different
            if j[1] != prev:
                prev = float(j[1])
                count += 1

            result += "         " + str(count) + \
                      ". " + j[0] + ": " + \
                      str(round(float(j[1]), 2)) + "%" + "\n"

    return result


def main(my_json: Dict) -> ADType:
    len_year: int = my_json["size"][2]
    len_country: int = my_json["size"][1]
    countries: List[str] = list(my_json["dimension"]["area"]["category"]["label"].values())
    values: List[float] = list(my_json["value"])
    years: List[str] = list(my_json["dimension"]["year"]["category"]["index"])

    # I decided to create a dictionary where the keys will be the years
    # and the values will be the country and rating,
    # so that it will be easier to work with the values further
    dict_by_years: DBYType = create_dict_by_years(len_year,
                                                  len_country,
                                                  countries,
                                                  values,
                                                  years)

    result: ADType = min_max(dict_by_years)
    return result


def create_dict_by_years(len_year: int,
                         len_country: int,
                         countries: List[str],
                         values: List[float],
                         years: List[str]) -> Dict[str, List[str]]:
    # i need index for working with an array of rating values
    index: int = 0
    result: Dict = dict()

    for i in range(0, len_year):
        upd: List[List[Union[str, float]]] = []

        for j in range(0, len_country):
            upd.append([countries[j], values[index]])
            index += 1

        result[years[i]] = upd

    return result


def min_max(dict_by_years: DBYType) -> \
        ADType:
    result: ADType = dict()

    for i in dict_by_years.keys():
        actual_dict: DBYType = dict()

        actual_dict["3 countries with the lowest unemployment rate"] = minimum(dict_by_years[i])
        actual_dict["3 countries with the highest unemployment rate"] = maximum(dict_by_years[i])

        # dictionary structure: {year:[[3 lowest values], [3 highest values]]}
        result[i] = actual_dict

    return result


# It was possible not to do it in separate functions,
# but I have a habit after Java, so...
def minimum(data_by_year: List[str]) -> List[str]:
    county_data: List[str] = sorted(data_by_year, key=lambda x: x[1])
    result: List[str] = top3_creator(county_data)
    return result


def maximum(data_by_year: List[str]) -> List[str]:
    county_data: List[str] = sorted(data_by_year, key=lambda x: x[1], reverse=True)
    result: List[str] = top3_creator(county_data)
    return result


def top3_creator(county_data: List[str]) -> List[str]:
    result: List[str] = []
    # I need "count" because if several countries
    # have the same values, all of them are added
    count: int = 1
    prev: str = county_data[0][1]

    # I will add all the countries
    for i in county_data:
        # but if count is 3 i'll exit cycle
        if count == 3:
            break

        # I'm not sure, but it is unlikely that total and EU
        # should be included in the list of " top 3 countries"
        if i[0] != "total" and i[0] != "Euro area (15 countries)":
            result.append(i)
            if i[1] != prev:
                count += 1
    return result


#
# simple tests
#


def correct_json():
    len_year: int = json_link["size"][2]
    len_country: int = json_link["size"][1]
    countries = list(json_link["dimension"]["area"]["category"]["label"].values())
    values = list(json_link["value"])
    years = list(json_link["dimension"]["year"]["category"]["index"])

    assert len_year == len(years)
    assert len_country == len(countries)
    assert len(values) == len_year * len_country


def test_repeated_rate():
    test_len_year = 1
    test_len_country: int = 5
    test_countries = ['Australia', 'Austria', 'Belgium', 'Canada', 'Chile']
    test_values = [5.943826289, 5.943826289, 5.943826289, 5.943826289, 5.943826289]
    test_years = ['2003']
    test_dict_by_years = create_dict_by_years(test_len_year,
                                              test_len_country,
                                              test_countries,
                                              test_values,
                                              test_years)
    x = all_data_to_text(min_max(test_dict_by_years)).split()

    assert x.count('5.94%') == 5 * 2
    assert x.count('1.') == 5 * 2
    for i in test_countries:
        assert x.count(i + ':') == 2


def americans_test():
    # also check for less than 3 countries in the list
    test_len_year = 1
    test_len_country: int = 2
    test_countries = ['Australia', 'Austria']
    test_values = [5.3, 5.943826289]
    test_years = ['2003']
    test_dict_by_years = create_dict_by_years(test_len_year,
                                              test_len_country,
                                              test_countries,
                                              test_values,
                                              test_years)
    x = all_data_to_text(min_max(test_dict_by_years)).split()

    assert x[0] == '2003:'
    index_australia_low = x.index("Australia:")
    index_australia_high = x.index("Australia:", index_australia_low + 1)
    index_austria_low = x.index("Austria:")
    index_austria_high = x.index("Austria:", index_austria_low + 1)
    assert index_australia_low < index_austria_low
    assert index_australia_high > index_austria_high


def positive_rate():
    test_len_year = 1
    test_len_country: int = 2
    test_countries = ['Australia', 'Austria']
    test_values = [-2, -5.943826289]
    test_years = ['2003']
    test_dict_by_years = create_dict_by_years(test_len_year,
                                              test_len_country,
                                              test_countries,
                                              test_values,
                                              test_years)

    x = all_data_to_text(min_max(test_dict_by_years)).split("\n")
    austria = float(x[2].split('. ')[1].split(': ')[1].split('%')[0])
    australia = float(x[3].split('. ')[1].split(': ')[1].split('%')[0])
    assert austria < australia


#
# extra feature
#

def menu() -> None:
    years_list: List[str] = list(json_link["dimension"]["year"]["category"]["index"])
    print("Do you want to see all data by years or only for a specific year")
    first_step: str = ""
    second_step: str = ""
    while first_step != '1' and first_step != '2':
        first_step = input("input '1' for all data\ninput '2' for selecting a specific year:\n")
        if first_step != '1' and first_step != '2':
            print("Input correct number!\n")
    if first_step == '1':
        print(without_inp(json_link))

    elif first_step == '2':
        while second_step not in years_list:
            second_step = input("Choose a year from 2003 to 2014:\n")
            if second_step not in years_list:
                print("Input correct year!\n")
        print(with_inp(json_link, second_step))

    menu_looper()


def menu_looper() -> None:
    loop: str = ""
    while (loop != "Y" or loop != 'y') and \
            (loop != 'n' or loop != 'N'):
        loop = input("Do you want to see another statistics?\nY/N:\n")
        if loop == "Y" or loop == 'y':
            menu()
            break
        elif loop == 'n' or loop == 'N':
            break
        else:
            print("input correct symbol")


if __name__ == '__main__':
    # tests
    correct_json()
    test_repeated_rate()
    americans_test()
    positive_rate()

    # # program
    data_selector = False
    # # uncomment to use "data selector"
    # data_selector = check = True

    if data_selector is False:
        print(without_inp(json_link))
    else:
        menu()
