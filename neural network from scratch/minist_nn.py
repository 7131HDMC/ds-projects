import numpy as np
import pandas as pd
from activation_functions import ActivationFunctions as F

class MnistNetwork:
    """
        
    """
    def __init__(self, X, Y, shape):
        W1 = np.random.randn(10,784) - 0.5
        b1 = np.random.randn(10,1) - 0.5
        W2 = np.random.randn(10,10) - 0.5
        b2 = np.random.randn(10,1) - 0.5
        self.m, self.n = shape
        self.Y = Y
        self.X = X
        return W1, b1, W2, b2
        
    def forward_prop(self, W1, b1, W2, b2, X):
        Z1 = W1.dot(X) + b1 
        A1 = F.relu(Z1)    
        Z2 = W2.dot(A1) + b2
        A2 = F.softmax(Z2)
        return Z1, A1, Z2, A2

    def one_hot(self, Y):
        one_hot_Y = np.zeros((Y.size, Y.max() + 1))
        one_hot_Y[np.arange(Y.size), Y] = 1
        one_hot_Y = one_hot_Y.T
        return one_hot_Y

    def deriv_ReLU(Z):
        return Z > 0
        

    def back_prop(self, Z1, A1, Z2, A2, W1, W2, X,Y):
    #     m = Y.size
        one_hot_Y = self.one_hot(Y)
        dZ2 =  A2 - one_hot_Y
        dW2 = 1/self.m * dZ2.dot(A1.T)
        db2 = 1/self.m * np.sum(dZ2)
        dZ1 = W2.T.dot(dZ2) * self.deriv_ReLU(Z1)
        dW1 = 1/self.m * dZ1.dot(X.T)
        db1 = 1/self.m * np.sum(dZ1)
        return dW1, db1, dW2, db2

    def update_params(self, W1, b1, W2, b2,dW1, db1, dW2, db2, alpha):
        W1 = W1 - alpha * dW1
        b1 = b1 - alpha * db1
        W2 = W2 - alpha * dW2
        b2 = b2 - alpha * db2
        return W1, b1, W2, b2 

    def get_predictions(A2):
        return np.argmax(A2, 0)

    def get_accuracy(predictions, Y):
        print(predictions, Y)
        return np.sum(predictions == Y) / Y.size

    def gradient_descent(self, iterations, alpha):
        for i in range(iterations):
            Z1, A1, Z2, A2 = self.forward_prop(self.W1, self.b1, self.W2, self.b2, self.X)
            dW1, db1, dW2, db2 = self.back_prop(Z1, A1, Z2, A2, self.W1, self.W2, self.X, self.Y)
            self.W1, self.b1, self.W2, self.b2 = self.update_params(self.W1, self.b1, self.W2, self.b2, dW1, db1, dW2, db2, alpha)
            
            if i % 10 == 0:
                print("Iteraction: ", i)
                print("Accuracy: ", self.get_accuracy(self.get_predictions(A2), Y))
        
        return self.W1, self.b1, self.W2, self.b2  