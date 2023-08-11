# This is a DTW classifier 
# from dtaidistance import dtw_ndim
from tslearn.metrics import dtw_path
import numpy as np
import itertools

"""A temporal Dynamic Time Warping Classifier. 

Parameters
-----------
std: int (optional), default=3 
    The number of standard deviations away from the mean of templates. This value is used for thresholding each new sample. 
"""
class DTWClassifier:
    def __init__(self, std=3):
        # DATA:
        self.templates = None
        self.labels = None
        self.distances = None
        self.std = std
        self.threshold = None

    def fit(self, features):
        self.templates = features
        distances = []
        for t1, t2 in itertools.combinations(self.templates, 2):
            _, dist = dtw_path(t1, t2)
            distances.append(dist)
        self.distances = distances
        self.update_threshold(self.std)
    
    def update_threshold(self, std):
        self.std = std
        self.threshold = np.mean(self.distances) + self.std * np.std(self.distances)

    def predict(self, samples): 
        predictions = []
        for s in samples:
            scores = []
            for t in self.templates:
                _, dist = dtw_path(t, s)
                scores.append(dist)

            if np.mean(scores) < self.threshold:
                print("Threshold: " + str(self.threshold) + " Val: " + str(np.mean(scores)))
                predictions.append(1)
            else:
                predictions.append(-1)
            
        return np.array(predictions)
