from typing import Tuple as _Tuple

import numpy as _np


def compute_rt(dates: _np.ndarray, new_cases: _np.ndarray) -> _Tuple[
    _np.ndarray, _np.ndarray, _np.ndarray]:
    """
    Compute the time series of Rt with the corresponding credible interval.

    Args:
        dates: 1d np.ndarray
            Time series of the dates in python datetime format.
        new_cases: 1d np.ndarray
            Time series of the number of new cases for each day.
    Returns:
        Tuple with 3 one-dimensional np.ndarray-s.:
        - time series of Rt;
        - time series of lower boundary of high intensity interval;
        - time series of higher boundary of high intensity interval.
    """
    raise NotImplementedError('Sorry... computing Rt is not available yet.')
