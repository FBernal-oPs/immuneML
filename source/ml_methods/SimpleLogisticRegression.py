from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RandomizedSearchCV

from source.ml_methods.SklearnMethod import SklearnMethod


class SimpleLogisticRegression(SklearnMethod):
    """
    Logistic regression wrapper of the corresponding scikit-learn's method.

    For usage and specification, check SklearnMethod class.
    For valid parameters, see: https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html
    """

    default_parameters = {"max_iter": 1000, "solver": "saga"}

    def __init__(self, parameter_grid: dict = None, parameters: dict = None):
        super(SimpleLogisticRegression, self).__init__()

        self._parameters = {**self.default_parameters, **(parameters if parameters is not None else {})}

        if parameter_grid is not None:
            self._parameter_grid = parameter_grid
        else:
            self._parameter_grid = {"max_iter": [1000],
                                    "penalty": ["l1", "l2"],
                                    "C": [0.001, 0.01, 0.1, 10, 100, 1000],
                                    "class_weight": ["balanced"]}

    def _get_ml_model(self, cores_for_training: int = 2):
        self._parameters["n_jobs"] = cores_for_training
        return LogisticRegression(**self._parameters)

    def _can_predict_proba(self) -> bool:
        return True

    def get_params(self, label):
        params = self.models[label].estimator.get_params() if isinstance(self.models[label], RandomizedSearchCV) \
            else self.models[label].get_params()
        params["coefficients"] = self.models[label].coef_[0].tolist()
        params["intercept"] = self.models[label].intercept_.tolist()
        return params
