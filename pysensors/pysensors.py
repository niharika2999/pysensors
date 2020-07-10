"""
SensorSelector object definition.
"""
from numpy import dot
from scipy.linalg import lstsq
from scipy.linalg import solve
from sklearn.base import BaseEstimator
from sklearn.utils.validation import check_is_fitted

from pysensors.basis import Identity
from pysensors.optimizers import QR
from pysensors.utils import validate_input


class SensorSelector(BaseEstimator):
    """TODO: write docstring

    <Description>

    Parameters
    ----------
    basis: basis object, optional
        Basis in which to represent the data. Default is the identity basis
        (i.e. raw features).

    optimizer: optimizer object, optional
        Optimization method used to identify sparse sensors.

    n_sensors: int, optional (default n_input_features)
        Number of sensors to select. Note that
        ``s = SensorSelector(n_sensors=10); s.fit(x)``
        is equivalent to
        ``s = SensorSelector(); s.fit(x); s.set_number_of_sensors(10)``.

    Attributes
    ----------

    Examples
    --------
    """

    def __init__(self, basis=None, optimizer=None, n_sensors=None):
        if basis is None:
            basis = Identity()
        self.basis = basis
        if optimizer is None:
            optimizer = QR()
        self.optimizer = optimizer
        if n_sensors is None:
            self.n_sensors = None
        elif isinstance(n_sensors, int) and n_sensors > 0:
            self.n_sensors = n_sensors
        else:
            raise ValueError("n_sensors must be a positive integer.")

    def fit(self, x, **optimizer_kws):
        """
        Fit the SensorSelector model, determining which sensors are relevant.

        Parameters
        ----------
        x: array-like, shape (n_samples, n_input_features)
            Training data.

        optimizer_kws: dict
            Keyword arguments to be passed to the `get_sensors` method of the optimizer.
        """

        # TODO: some kind of preprocessing / quality control on x
        x = validate_input(x)

        # Fit basis functions to data (sometimes unnecessary, e.g FFT)
        self.basis.fit(x)

        # Get matrix representation of basis
        self.basis_matrix_ = self.basis.matrix_representation()

        # Maximum number of sensors (= dimension of basis vectors)
        max_sensors = self.basis_matrix_.shape[0]
        if self.n_sensors is None:
            self.n_sensors = max_sensors
        elif self.n_sensors > max_sensors:
            raise ValueError(
                "n_sensors cannot exceed number of available sensors: {}".format(
                    max_sensors
                )
            )

        # Find sparse sensor locations
        self.selected_sensors_ = self.optimizer.get_sensors(
            self.basis_matrix_, **optimizer_kws
        )

    def predict(self, x, **solve_kws):
        """
        TODO: docstring

        If x is a column vector, should behave fine.
        If x is a 2D array with rows corresponding to examples we'll need
        to transpose it before multiplying it with the basis matrix.
        """
        check_is_fitted(self, "selected_sensors_")
        x = validate_input(x, self.selected_sensors_[: self.n_sensors]).T

        # For efficiency we may want to factor
        # self.basis_matrix_[self.selected_sensors_, :]
        # in case predict is called multiple times

        # Square matrix
        if len(self.selected_sensors_[: self.n_sensors]) == self.basis_matrix_.shape[1]:
            return dot(
                self.basis_matrix_,
                solve(
                    self.basis_matrix_[self.selected_sensors_[: self.n_sensors], :],
                    x,
                    **solve_kws
                ),
            )
        # Rectangular matrix
        else:
            return dot(
                self.basis_matrix_,
                lstsq(
                    self.basis_matrix_[self.selected_sensors_[: self.n_sensors], :],
                    x,
                    **solve_kws
                )[0],
            )

    def get_selected_sensors(self):
        check_is_fitted(self, "selected_sensors_")
        return self.selected_sensors_[: self.n_sensors]

    def get_all_sensors(self):
        check_is_fitted(self, "selected_sensors_")
        return self.selected_sensors_

    # TODO: functionality for selecting how many sensors to use
    def set_number_of_sensors(self, n_sensors):
        check_is_fitted(self, "selected_sensors_")

        if not isinstance(n_sensors, int):
            raise ValueError("n_sensors must be a positive integer")
        elif n_sensors <= 0:
            raise ValueError("n_sensors must be a positive integer")
        elif n_sensors > len(self.selected_sensors_):
            raise ValueError(
                "n_sensors cannot exceed number of available sensors: "
                "{}".format(len(self.selected_sensors_))
            )
        else:
            self.n_sensors = n_sensors
