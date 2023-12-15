from dataclasses import dataclass
from typing import List, Optional
from activation_functions.ActivationFunctions import sigmoid, sigmoid_derivative 

@dataclass
class Neuron:
    weights: List[float]
    bias: float
    delta: Optional[float] = .0
    output: Optional[float] = .0

    def _set_output(self, output: float) -> None:
        self.output = output

    def set_delta(self, error: float) -> None:
        self.delta = error*sigmoid_derivative(self.output)
    
    def weighted_sum(self, inputs: List[float]) -> float:
        """
        Usually results in a big number, but we tend to use a value [0, 1] for activation
        Hence, after calculating this, we use the sigmoid function to normalize the result
        """
        ws = self.bias
        for i in range(len(self.weights)):
            ws += self.weights[i] * inputs[i]
        return ws
    
    def activate(self, inputs: List[float]) -> float:
        """
        Calculates the output of the neuron using a non-linear activation function
        In this case we use the sigmoid function
        """
        output = sigmoid(self.weighted_sum(inputs))
        self._set_output(output)
        return output
    
@dataclass
class Layer:
    neurons: List[Neuron]

    @property
    def all_outputs(self) -> List[float]:
        return [neuron.output for neuron in self.neurons]
    
    def activate_neurons(self, inputs: List[float]) -> List[float]:
        return [neuron.activate(inputs) for neuron in self.neurons]
    
    def total_delta(self, previous_layer_neuron_idx: int) -> float:
        return sum(
            neuron.weights[previous_layer_neuron_idx]*neuron.delta
            for neuron in self.neurons
        )


@dataclass
class Network:
    hidden_layers: List[Layer]
    output_layer: Layer
    learning_rate: float

    @property
    def layers(self) -> List[Layer]:
        return self.hidden_layers+[self.output_layer]
    
    def feed_forward(self, inputs: List[float]) -> List[float]:
        for layer in self.hidden_layers:
            inputs = layer.activate_neurons(inputs)
        return self.output_layer.activate_neurons(inputs)
    
    def derivative_error_to_output(
            self, actual: List[float], expected: List[float]
    ) -> List[float]:
        """
        Derivative of error function with respect to the output
        """
        return [actual[i] - expected[i] for i in range(len(actual))]
    

    def back_propagate(self, inputs: List[float], errors: List[float]) -> None:
        """
        Compute the gradient and then update the weights
        """
        for index, neuron in enumerate(self.output_layer.neurons):
            neuron.set_delta(errors[index])

        for layer_idx in reversed(range(len(self.hidden_layers))):
            layer = self.hidden_layers[layer_idx]
            next_layer = (
                self.output_layer
                if layer_idx == len(self.hidden_layers) - 1
                else self.hidden_layers[layer_idx+1]
            )
            for neuron_idx, neuron in enumerate(layer.neurons):
                error_fromo_next_layer = next_layer.total_delta(neuron_idx)
                neuron.set_delta(error_fromo_next_layer)

        self.update_weights_for_all(inputs)
    
    def update_weights_for_all_layers(self, inputs: List[float]):
        """
        Update weights for all layers
        """
        for layer_idx in range(len(self.hidden_layers)):
            layer = self.hidden_layers[layer_idx]
            previous_layer_outputs: List[float] = (
                inputs
                if layer_idx == 0
                else self.hidden_layers[layer_idx - 1].all_outputs
            )
            for neuron in layer.neurons:
                self.update_weights_in_a_layer(previous_layer_outputs, neuron)

        for index, neuron in enumerate(self.output_layer.neurons):
            self.update_weights_in_a_layer(self.hidden_layers[-1].all_outputs, neuron)

    def update_weights_in_a_layer(
        self, previous_layer_outputs: List[float], neuron: Neuron
    ) -> None:
        """
        Update weights in all neurons in a layer
        """
        for idx in range(len(previous_layer_outputs)):
            neuron.weights[idx] -= (
                self.learning_rate * neuron.delta * previous_layer_outputs[idx]
            )
            neuron.bias -= self.learning_rate * neuron.delta

    def train(
        self,
        num_epoch: int,
        num_outputs: int,
        training_set: List[List[float]],
        training_output: List[float],
    ) -> None:
        for epoch in range(num_epoch):
            sum_error = 0.0
            for idx, row in enumerate(training_set):
                expected = [0 for _ in range(num_outputs)]
                expected[training_output[idx]] = 1  # one-hot encoding
                actual = self.feed_forward(row)
                errors = self.derivative_error_to_output(actual, expected)
                self.back_propagate(row, errors)
                sum_error += self.mse(actual, training_output)
            print(f"Mean squared error: {sum_error}")
            print(f"epoch={epoch}")

    def predict(self, inputs: List[float]) -> int:
        outputs = self.feed_forward(inputs)
        return outputs.index(max(outputs))

    def mse(self, actual: List[float], expected: List[float]) -> float:
        """
        Mean Squared Error formula
        """
        return sum((actual[i] - expected[i]) ** 2 for i in range(len(actual))) / len(
            actual
        )