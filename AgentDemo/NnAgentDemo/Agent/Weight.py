import numpy as np

class Weight(object):
    def __init__(self, weight: np.array):
        self.weight = weight

    def setWeight(self, weight):
        self.weight = weight

    def getWeight(self):
        return self.weight

    def getWidth(self):
        self.weight.shape[1]

    def getHeight(self):
        self.weight.shape[0]

    def getShape(self):
        return self.weight.shape
