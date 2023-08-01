import numpy as np

class ActivationFunctions:
    
    def step(self, sum):
        return int(sum>=1)
    
    def relu(self, sum):
        return sum if sum>=0 else 0

    def sigmoid(self, sum):
        return 1 / ( 1 - np.exp(-sum))

    def hiperbolicTangent(self, sum):
        return (np.exp(sum) - np.exp(-sum)) / (np.exp(sum) + np.exp(-sum)) 

    def softmax(self, x):
        exp = np.exp(x)
        return exp / exp.sum()

    def softplus(self, x):
        return np.log(np.exp(x) + 1)
    
    def softsign(self, x):
        return 1 / (np.abs(x)+1)
    
