# This is a numpy/scipy reimplementation of
# https://github.com/k-sys/covid-19/blob/master/Realtime%20R0.ipynb
# and is still an alpha version
import numpy as np
import scipy.stats as sps

# The gamma parameter is defined as the reciprocal of the serial interval and
# is required to define the likelihood
_GAMMA = 1 / 7

_RT_MAX = 12
_RT_RANGE = np.linspace(0, _RT_MAX, _RT_MAX * 100 + 1)


def get_posteriors(ts, sigma=0.25):
    # TODO: write docstring
    lam = ts[:-1] * np.exp(_GAMMA * (_RT_RANGE - 1))

    likelihood = sps.poisson.pmd(ts[1:], lam)

    # Determine the update of the prior P(R(t) | R(t-1))
    transition = sps.norm(loc=_RT_RANGE, scale=sigma).pdf(_RT_RANGE[:, None])
    transition /= transition.sum(axis=0)

    # Initial prior
    prior0 = np.ones_like(_RT_RANGE)
    prior0 /= len(prior0)
    prior0 /= prior0.sum()

    # Compute posterior and log likelihood
    posteriors = np.zeros((prior0.size, ts.size))
    posteriors[0] = prior0

    llhood = 0.0

    for i in range(1, ts.size - 1):
        # one step of the brownian motion that defines the prior
        prior = transition @ posteriors[i - 1]

        # compute P(k|R_t) P(R_t) for each R_t (numerator of posterior)
        posterior_num = likelihood[i] * prior

        # compute P(k) with total probability law (denominator of posterior)
        posterior_den = posterior_num.sum()

        # one step forward
        posteriors[i] = posterior_num / posterior_den

        # update log likelihood
        llhood += np.log(posterior_den)

    return posteriors, llhood


def compute_credible_region(pmf, p=0.9):
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

    low = pmf[lows[best]]
    high = pmf[highs[best]]

    return low, high
