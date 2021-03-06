import paddle
import paddle.nn as nn
import numpy as np
from paddle import Tensor
from paddle.nn.initializer import Assign

class GaussianVariational(nn.Layer):

    """Gaussian Variational Weight Sampler.

    Section 3.2 of the 'Weight Uncertainty in Neural Networks' paper
    proposes the use of a Gaussian posterior in order to sample weights
    from the network for use in variational inference.
    """

    def __init__(self, mu: Tensor, rho: Tensor) -> None:

        """Gaussian Variational Weight Sampler.

        Parameters
        ----------
        mu : Tensor
            Mu used to shift the samples drawn from a unit Gaussian.
        rho : Tensor
            Rho used to generate the pointwise parameterisation of the
            standard deviation - used to scale the samples drawn a unit
            Gaussian.
        """

        super().__init__()

        self.mu = self.create_parameter(shape=mu.shape,default_initializer=Assign(mu))
        self.rho = self.create_parameter(shape=rho.shape,default_initializer=Assign(rho))
        self.w = None
        self.sigma = None
        self.normal = paddle.distribution.Normal(0, 1)

    def sample(self) -> Tensor:

        """Draws a sample from the posterior distribution.

        Samples a weight using:
            w = mu + log(1 + exp(rho)) * epsilon
                where epsilon ~ N(0, 1)

        Returns
        -------
        Tensor
            Sampled weight from the posterior distribution.
        """

        epsilon = self.normal.sample(self.mu.shape)
        self.sigma = paddle.log(1 + paddle.exp(self.rho))
        self.w = self.mu + self.sigma * epsilon

        return self.w

    def log_posterior(self) -> Tensor: # 计算高斯的对数似然logq(w|θ)

        """Log Likelihood for each weight sampled from the distribution.

        Calculates the Gaussian log likelihood of the sampled weight
        given the the current mean, mu, and standard deviation, sigma:

            LL = -log((2pi * sigma^2)^0.5) - 0.5(w - mu)^2 / sigma^2

        Returns
        -------
        Tensor
            Gaussian log likelihood for the weights sampled.
        """

        if self.w is None:
            raise ValueError('self.w must have a value.')

        log_const = np.log(np.sqrt(2 * np.pi))
        log_exp = ((self.w - self.mu) ** 2) / (2 * self.sigma ** 2)
        log_posterior = -log_const - paddle.log(self.sigma) - log_exp

        return log_posterior.sum()
