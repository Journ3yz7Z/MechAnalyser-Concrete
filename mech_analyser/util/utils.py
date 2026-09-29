import numpy as np

from numpy.typing import NDArray


def calculate_r2(data: list[float], regressed_data: list[float]) -> float:
    """
    Calculates the coefficient of determination (R^2) value for a given dataset.

    Args:
        data: The dataset of actual values.
        regressed_data: The dataset of values calculated using the regression
            model.

    Returns:
        The coefficient of determination (R^2) for the given dataset.
    """

    data_array: NDArray[np.float64] = np.array(data)
    regressed_data_array: NDArray[np.float64] = np.array(regressed_data)

    residuals: NDArray[np.float64] = data_array - regressed_data_array
    total_sum_of_squares: np.float64 = np.sum((data_array - np.mean(data_array)) ** 2)
    residual_sum_of_squares: np.float64 = np.sum(residuals**2)

    return 1 - residual_sum_of_squares / total_sum_of_squares
