from sklearn.ensemble import RandomForestClassifier
import joblib


class RandomForest:

    def __init__(self,n_estimators:int = 200, random_state: int = 42, **kwargs):

        self.model = RandomForestClassifier(n_estimators=n_estimators, random_state=random_state)

    def fit(self, x_train, y_train):
        self.model.fit(x_train, y_train)

    def predict(self, x):
        return self.model.predict(x)

    def predict_proba(self, x):
        return self.model.predict_proba(x)

    def save(self, path):
        joblib.dump(self.model, path)

    def load(self, path):
        self.model = joblib.load(path)