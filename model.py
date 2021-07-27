import pandas as pd
import numpy as np
import math

class Model():
    def __init__(self, weights=None):
        """When class is created, it is either created with previous weights, or randomly initiated

        -Input size is 49 (of data points)
        -Output size is 3 (shoot, x and y)
        -Model has a 10% chance to mutate each weight
        """
        self.input_size = 50
        self.output_size = 3
        self.mutation_rate = 0.1  # 10% chance to mutate

        if weights is None:
            self.weights = np.random.uniform(-1, 1, (self.output_size, self.input_size))
        else:
            self.weights = weights

    def sigmoid(self, x):
        return 1 / (1 + math.exp(-x))

    def feed_forward(self, inputs):
        return [self.sigmoid(i) for i in (inputs * self.weights).sum(axis=1)]

    def mutate(self):
        """When mutating, there is a 10% chance per weight to reinitialize (randomize) its value.
        """
        self.weights = pd.DataFrame(self.weights).apply(
            lambda ser: ser.apply(lambda x: np.random.uniform(-1, 1) if np.random.random() <= 0.1 else x)).values

    def save(self, file_name):
        np.save(file_name, self.weights)