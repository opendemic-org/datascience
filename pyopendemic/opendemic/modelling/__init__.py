import logging as _logging
from typing import Iterable as _Iterable
from typing import Tuple as _Tuple

import numpy as _np
from opendemic.data.core import AbstractRegionData as _RegionData
from opendemic.modelling.systrom import get_posteriors
from opendemic.modelling.systrom import high_density_interval
from opendemic.modelling.systrom import RT_RANGE


def compute_rt(new_cases: _np.ndarray, kwargsmodel: dict = dict(),
               kwargshdi: dict = dict()) -> _Tuple[_np.ndarray,
                                                        _np.ndarray,
                                                        _np.ndarray]:
    """
    Compute the time series of Rt with the corresponding credible interval.

    Args:
        new_cases: 1d np.ndarray
            Time series of the number of new cases for each day.
        kwargsmodel: dict
            **kwargs to pass to the employed model.
        kwargshdi: dict
            **kwargs to pass to the function that computes the high density
            interval.
    Returns:
        Tuple with 3 one-dimensional np.ndarray-s.:
        - time series of Rt;
        - time series of lower boundary of high intensity interval;
        - time series of higher boundary of high intensity interval.
    """
    post, _ = get_posteriors(new_cases, **kwargsmodel)
    rt = _np.asarray([RT_RANGE[i] for i in _np.argmax(post, axis=1)])
    low = _np.zeros(post.shape[0])
    high = _np.zeros_like(low)
    for i, pmf in enumerate(post):
        hdi = high_density_interval(pmf, **kwargshdi)
        low[i] = hdi[0]
        high[i] = hdi[1]
    return rt, low, high


def sigma_update(regions: _Iterable[_RegionData],
                 sigmagrid: _Iterable[float] = None) -> float:
    """
    Compute the value of `sigma` that maximizes the likelihood of the Systrom
    model. See documentation of `opendemic.modelling.systrom.get_posteriors`
    for details.

    The returned value will be the one showing maximal likelihood among the ones
    in `sigmagrid`.

    Args:
        regions: iterable of RegionData objects
            This is the sequence of RegionData objects that will be used for
            computing the optimal sigma.
        sigmagrid: iterable of floats
            Grid of values of sigma that will be tested.
            Default: linspace(0.05, 1, 20)
    Returns:
        float whose value is the optimal sigma.
    """
    if sigmagrid is None:
        sigmagrid = _np.linspace(.05, 1, 20)

    total_llhoods = _np.zeros_like(sigmagrid)
    for r in regions:
        for i, s in enumerate(sigmagrid):  # TODO: can be parallelized
            post, llhood = get_posteriors(r.new_cases)
            _logging.info(f'{r.name}\tsigma: {s} log-likelihood: {llhood}')
            total_llhoods[i] = llhood
    opt = sigmagrid[total_llhoods.argmax()]
    _logging.info(f'Optimal sigma: {opt}')
    return opt
