from sklearn.ensemble import RandomForestClassifier
import joblib
from src.core.logger import logger


class RandomForest:

    def __init__(self,n_estimators:int = 200, random_state: int = 42, **kwargs):

        self.model = RandomForestClassifier(n_estimators=n_estimators, random_state=random_state)

        logger.info(f"Initialized RandomForestClassifier  (n_estimators={n_estimators}, random_state={random_state}).")

    def fit(self, x_train, y_train):
        logger.info('Random Forest Training Started.')

        self.model.fit(x_train, y_train)

        logger.info('Random Forest Training Completed.')

    def predict(self, x):
        return self.model.predict(x)

    def predict_proba(self, x):
        return self.model.predict_proba(x)

    def save(self, path):
        logger.info(f"Saving Random Forest Model to path: {path}")
        joblib.dump(self.model, path)

    def load(self, path):
        logger.info(f"Loading Random Forest Model from path: {path}")
        self.model = joblib.load(path)