# This is a numpy/scipy reimplementation of
# https://github.com/k-sys/covid-19/blob/master/Realtime%20R0.ipynb
# and is still an alpha version
from typing import Tuple

import numpy as np
import scipy.stats as sps

# The gamma parameter is defined as the reciprocal of the serial interval and
# is required in order to define the likelihood
_GAMMA = 1 / 7

_RT_MAX = 12
RT_RANGE = np.linspace(0, _RT_MAX, _RT_MAX * 100 + 1)


def get_posteriors(ts: np.ndarray, sigma: float = 0.25) -> Tuple[np.ndarray,
                                                                 float]:
    """
    Get the posterior probability for each time step and the log-likelihood of
    the representation.

    Args:
        ts : np.ndarray
            One dimensional array representation of the time series of the
            number of new cases in each time point.
        sigma : float
            Scale parameter of the gaussian update of the prior distribution.
    Returns:
        tuple of length 2 with:
            * 2d numpy array with one row per time point and one column per
                tested Rt. Each row of the matrix encodes the posterior
                probability distribution at a specific timepoint. The array of
                the tested Rt-s is defined as
                `opendemic.modelling.systrom.RT_RANGE`.
            * float with the log-likelihood of the model.
    Raises:
        ValueError : if the passed time series is not one-dimensional.
    """
    ts = np.squeeze(ts)
    if ts.ndim != 1:
        raise ValueError('The time series must be a 1d array.')

    sigma = float(sigma)

    lam = ts[:-1] * np.exp(_GAMMA * (RT_RANGE[:, None] - 1))

    likelihood = sps.poisson.pmf(ts[1:], lam)
    likelihood /= np.sum(likelihood, axis=0)

    # Determine the update of the prior P(R(t) | R(t-1))
    transition = sps.norm(loc=RT_RANGE, scale=sigma).pdf(RT_RANGE[:, None])
    transition /= transition.sum(axis=0)

    # Initial prior
    prior0 = np.ones_like(RT_RANGE)
    prior0 /= len(prior0)
    prior0 /= prior0.sum()

    # Compute posterior and log likelihood
    posteriors = np.zeros((ts.size, prior0.size))
    posteriors[0] = prior0

    llhood = 0.0

    for i in range(1, ts.size):
        # one step of the brownian motion that defines the prior
        prior = transition @ posteriors[i - 1]

        # compute P(k|R_t) P(R_t) for each R_t (numerator of posterior)
        posterior_num = likelihood[:, i - 1] * prior

        # compute P(k) with total probability law (denominator of posterior)
        posterior_den = posterior_num.sum()

        # one step forward
        posteriors[i] = posterior_num / posterior_den

        # update log likelihood
        llhood += np.log(posterior_den)

    return posteriors, llhood


def high_density_interval(pmf, p=0.9):
    # TODO: write docstring
    pmf = np.squeeze(pmf)
    if pmf.ndim != 1:
        raise ValueError('Credible region can be computed only for 1d'
                         'probability mass vectors.')
    cumsum = np.cumsum(pmf)

    # total probability mass for each low, high
    total_p = cumsum - cumsum[:, None]

    # find where the total mass is higher than the wanted probability
    lows, highs = (total_p > p).nonzero()

    # find range with highest density (hence smallest range)
    best = (highs - lows).argmin()

    low = RT_RANGE[lows[best]]
    high = RT_RANGE[highs[best]]

    return low, high
