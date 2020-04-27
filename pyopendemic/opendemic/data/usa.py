from datetime import date
from datetime import datetime
from typing import Tuple, Union

import numpy as np
import pandas as pd

from .core import AbstractRegionData

_CODE2NAME = {
    'US': 'United States of America',
    'AK': 'Alaska',
    'AL': 'Alabama',
    'AR': 'Arkansas',
    'AS': 'American Samoa',
    'AZ': 'Arizona',
    'CA': 'California',
    'CO': 'Colorado',
    'CT': 'Connecticut',
    'DC': 'District Of Columbia',
    'DE': 'Delaware',
    'FL': 'Florida',
    'GA': 'Georgia',
    'GU': 'Guam',
    'HI': 'Hawaii',
    'IA': 'Iowa',
    'ID': 'Idaho',
    'IL': 'Illinois',
    'IN': 'Indiana',
    'KS': 'Kansas',
    'KY': 'Kentucky',
    'LA': 'Louisiana',
    'MA': 'Massachusetts',
    'MD': 'Maryland',
    'ME': 'Maine',
    'MI': 'Michigan',
    'MN': 'Minnesota',
    'MO': 'Missouri',
    'MP': 'Northern Mariana Islands',
    'MS': 'Mississippi',
    'MT': 'Montana',
    'NC': 'North Carolina',
    'ND': 'North Dakota',
    'NE': 'Nebraska',
    'NH': 'New Hampshire',
    'NJ': 'New Jersey',
    'NM': 'New Mexico',
    'NV': 'Nevada',
    'NY': 'New York',
    'OH': 'Ohio',
    'OK': 'Oklahoma',
    'OR': 'Oregon',
    'PA': 'Pennsylvania',
    'PR': 'Puerto Rico',
    'RI': 'Rhode Island',
    'SC': 'South Carolina',
    'SD': 'South Dakota',
    'TN': 'Tennessee',
    'TX': 'Texas',
    'UT': 'Utah',
    'VA': 'Virginia',
    'VI': 'US Virgin Islands',
    'VT': 'Vermont',
    'WA': 'Washington',
    'WI': 'Wisconsin',
    'WV': 'West Virginia',
    'WY': 'Wyoming'
}
REGIONS = list(_CODE2NAME.keys())


def fips2name(fips: Union[str, int, float]) -> str:
    # TODO: we've got to upload this csv to our server in order to make sure it
    #       does not magically disappear
    df_fips = pd.read_csv('https://raw.githubusercontent.com/kjhealy/'
                          'fips-codes/master/state_and_county_fips_master.csv')
    myfips = df_fips[df_fips['fips'] == int(fips)]
    return f"{myfips['name'].values[0]}, {myfips['state'].values[0]}"


def fetch_covid_tracking_project(state: str = 'US') -> Tuple[str, str,
                                                             np.ndarray,
                                                             np.ndarray]:
    """Fetch data from Covid Tracking Project

    Args:
        state: str
            State code (e.g. `NY` or `AK`). If `US`, data will be fetched
            for the whole USA. The list of allowed regions can be inspected
            at `opendemic.data.usa.REGIONS`. (Default: US)
    Return:
        Tuple with the 4 elements that are necessary to instantiate RegionData
        in the right order.
    """
    if state.upper() not in _CODE2NAME.keys():
        raise ValueError(f"'{state}' is not an available region. See "
                         f"opendemic.data.usa.REGIONS for a list of allowed "
                         f"regions.")

    df = pd.read_json('https://covidtracking.com/api/v1/states/daily.json')

    state = state.upper()
    if state != 'US':
        df = df[df['state'] == state]

    dates = np.unique(df['date'].to_numpy())  # ensures chronological order

    cases = np.zeros(len(dates))
    for k, d in enumerate(dates):
        # aggregate the data of each date
        c = df[df['date'] == d]['positive'].to_numpy()
        c[np.isnan(c)] = 0
        cases[k] = np.sum(c)  # accounts for multiple reports in the same day

    code = state
    name = _CODE2NAME.get(code)

    # convert dates to python standard format
    dates = np.asarray([datetime.strptime(str(d), '%Y%m%d') for d in dates])

    return name, code, dates, cases


def fetch_nyt(fips: Union[int, float, str]) -> Tuple[str, str, np.ndarray,
                                                     np.ndarray]:
    df = pd.read_csv(
        'https://raw.githubusercontent.com/nytimes/covid-19-data/master/'
        'us-counties.csv')

    fipscast = int(fips)
    fips_mask = df['fips'] == fipscast
    if np.count_nonzero(fips_mask) == 0:
        raise ValueError(f'No data available for county fips {fipscast}.')

    # select only data for the county
    df = df[fips_mask]

    dates = np.unique(df['date'])  # ensures chronological order

    cases = np.zeros(len(dates))
    for k, d in enumerate(dates):
        # aggregate the data of each date
        c = df[df['date'] == d]['cases'].to_numpy()
        c[np.isnan(c)] = 0
        cases[k] = np.sum(c)  # accounts for multiple reports in the same day

    # The NYT updates the database many times during a day. We want to rely
    # only on complete daily data, therefore we discard any data uploaded in the
    # same day of the query.
    n_today = np.count_nonzero(dates == date.today())

    dates = dates[: dates.size - n_today]
    cases = cases[: cases.size - n_today]

    dates = np.asarray([datetime.strptime(str(d), '%Y-%m-%d') for d in dates])

    name = fips2name(fips)

    return name, str(fipscast).zfill(5), dates, cases


class RegionData(AbstractRegionData):
    @classmethod
    def fetch(cls, state: str = 'US', county: Union[str, int, float] = None):
        """Fetch data from Covid Tracking Project

        If a county is specified, it fetches data from the NYT database,
        otherwise the COVID tracking project databases is employed.

        Args:
            state: str
                State code (e.g. `NY` or `AK`). If `US`, data will be fetched
                for the whole USA. The list of allowed regions can be inspected
                at `opendemic.data.usa.REGIONS`. (Default: US)
            county: str or int or float
                County fips (e.g. 01001). If specified, it fetches data for the
                given county and ignores the value of `state`. (Default: None)
        Return:
          opendemic.data.usa.RegionData instantiated object.
        """
        if county is not None:
            return cls(*fetch_nyt(county))
        else:
            return cls(*fetch_covid_tracking_project(state))
