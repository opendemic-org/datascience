from datetime import datetime
from typing import Tuple

import numpy as np
import pandas as pd

from .core import AbstractRegionData

NAME2CODE = {
    'Italia': 0,
    'Abruzzo': 13,
    'Basilicata': 17,
    'Calabria': 18,
    'Campania': 15,
    'Emilia-Romagna': 8,
    'Friuli Venezia Giulia': 6,
    'Lazio': 12,
    'Liguria': 7,
    'Lombardia': 3,
    'Marche': 11,
    'Molise': 14,
    'P.A. Trento': 4,
    'Piemonte': 1,
    'Puglia': 16,
    'Sardegna': 20,
    'Sicilia': 19,
    'Toscana': 9,
    'Umbria': 10,
    'Valle d\'Aosta': 2,
    'Veneto': 5
}

REGIONS = list(NAME2CODE.keys())


def fetch_protezione_civile(region: str = 'Italia') -> Tuple[str, str,
                                                             np.ndarray,
                                                             np.ndarray]:
    """Fetch data from Protezione Civile.
    Source: https://github.com/pcm-dpc/COVID-19/

    Args:
        region: str
            Region name (e.g. 'Lombardia' or ' Emilia-Romagna'). If 'Italia'
            , data will be fetched for the whole Italy. The list of allowed
            regions can be inspected at `opendemic.data.italy.REGIONS`.
            (Default: Italia)
    Return:
        Tuple with the 4 elements that are necessary to instantiate RegionData
        in the right order.
    """
    if region.upper() not in [r.upper() for r in REGIONS]:
        raise ValueError(f"'{region}' is not an available region. See "
                         f"opendemic.data.italy.REGIONS for a list of allowed "
                         f"regions.")

    address = 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/' \
              'dati-regioni/dpc-covid19-ita-regioni.csv'
    df = pd.read_csv(address)

    if region != 'Italia':
        df = df[df['denominazione_regione'] == region]
    dates = np.unique(df['data'].to_numpy())
    cases = np.zeros(len(dates))
    for k, d in enumerate(dates):
        # aggregate the data of each state
        c = df[df['data'] == d]['totale_positivi'].to_numpy()
        c[np.isnan(c)] = 0
        cases[k] = np.sum(c)  # this accounts for multiple reports in the same day

    code = NAME2CODE.get(region)
    name = region

    # convert dates to python standard format
    dates = [datetime.strptime(str(d), '%Y-%m-%dT%H:%M:%S') for d in dates]
    dates = np.asarray(dates)

    return name, code, dates, cases


class RegionData(AbstractRegionData):
    @classmethod
    def fetch(cls, region: str = 'Italia'):
        """Fetch data from Protezione Civile.
        Source: https://github.com/pcm-dpc/COVID-19/

        Args:
            region: str
                Region name (e.g. 'Lombardia' or ' Emilia-Romagna'). If 'Italia'
                , data will be fetched for the whole Italy. The list of allowed
                regions can be inspected at `opendemic.data.italy.REGIONS`.
                (Default: Italia)
        Return:
          opendemic.data.italy.RegionData instantiated object.
        """
        return cls(*fetch_protezione_civile(region))
