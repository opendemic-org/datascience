import logging
from abc import ABC
from typing import Iterable, Sized, Union

import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter1d

ArrayType = Union[Iterable, Sized]  # Intersection does not yet exist


class AbstractRegionData(ABC):
    def __init__(self, name: str, code: str, dates: ArrayType,
                 cases: ArrayType):
        """Initiate a RegionData """
        self._name = str(name)
        self._code = str(code)

        if len(dates) != np.unique(dates).size:
            raise ValueError('Values of `dates` are not unique.')
        if len(dates) != len(cases):
            raise ValueError('`dates` and `cases` must have the same length.')

        cases = np.asarray(cases, dtype=np.float32)

        # discard all the data until non-zero new cases are consistently
        # reported
        diffcases = np.diff(cases)
        idx_start = 0
        for i, v in enumerate(diffcases):
            if v == 0:
                idx_start = i + 1
            else:
                break

        # If more than 20% of the data points are discarded, start at day
        # 20% + 1
        # TODO: do we really want to decide the biggest chunk we can cut?
        portion = 0.2  # if you change this, change also the comment above
        tolerable_crop = np.ceil(portion * cases.size)
        if idx_start > tolerable_crop:
            idx_start = int(np.ceil(tolerable_crop))
        logging.debug(f'Ignoring the first {idx_start} data points as they\'re '
                      f'zero-report days.')

        self._cases = cases[idx_start:]

        new_cases = gaussian_filter1d(np.diff(self._cases), 3)
        self._smoothed_new_cases = np.insert(new_cases, 0, self._cases[0])

        dates = np.asarray(dates)
        self._dates = dates[idx_start:]

    @property
    def asdf(self) -> pd.DataFrame:
        """Return data AS a pandas DataFrame object.

        It creates a new DataFrame with copied data every time this is called.

        Index: dates
        Columns:
            'cases': number of total cases at that day.
            'new_cases': smoothed number of new cases in that day. See
                ``RegionData.new_cases`` documentation for details about the
                smoothing procedure.

        """
        frame = {'cases': self.cases, 'new_cases': self.new_cases}
        return pd.DataFrame(frame, index=list(self.dates), copy=True)

    @property
    def cases(self) -> np.ndarray:
        """Time series of the number of cases in the region."""
        return self._cases

    @property
    def code(self) -> Union[str, int]:
        """Identification code of the region."""
        return self._code

    @property
    def dates(self) -> np.ndarray:
        """Dates at which the cases are reported."""
        return self._dates

    @property
    def name(self) -> str:
        """Name of the region."""
        return self._name

    @property
    def new_cases(self) -> np.ndarray:
        """New cases in each time point.

        The returned array is obtained via Gaussian filtering of the time series
        of the daily increment of the number of cases.

        To get the raw increment of the number of cases one can compute
        ``np.diff(RegionData.cases)``.

        Returns:
            np.ndarray of dimension 1
        """
        return self._smoothed_new_cases

    @property
    def npoints(self) -> int:
        """Number of data points."""
        return self.cases.size

    @classmethod
    def fetch(cls, **kwargs):
        """"Fetch data from a local or remote location."""
        pass

    def __repr__(self) -> str:
        s = (
                f'Region: {self.name}, {self.code}.\n' +
                f'N. data points: {len(self.dates)}.\n' +
                f'Dates from {self.dates[0]} to {self.dates[-1]}.\n' +
                f'Cases at {self.dates[-1]}: {self.cases[-1]}.'
        )
        return s
