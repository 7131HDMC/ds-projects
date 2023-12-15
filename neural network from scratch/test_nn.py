from nn import Neuron, Layer, Network
import random

def test_make_prediction_with_network():
    # Test making predictions with the network
    # Mock data is from https://machinelearningmastery.com/implement-backpropagation-algorithm-scratch-python/
    dataset = [
        [2.7810836, 2.550537003],
        [1.465489372, 2.362125076],
        [3.396561688, 4.400293529],
        [1.38807019, 1.850220317],
        [3.06407232, 3.005305973],
        [7.627531214, 2.759262235],
        [5.332441248, 2.088626775],
        [6.922596716, 1.77106367],
        [8.675418651, -0.242068655],
        [7.673756466, 3.508563011],
    ]
    expected = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1]
    n_inputs = len(dataset[0])
    n_outputs = len(set(expected))
    hidden_layers = [
        Layer(
            neurons=[
                Neuron(weights=[random() for _ in range(n_inputs)], bias=random()),
                Neuron(weights=[random() for _ in range(n_inputs)], bias=random()),
            ],
        )
    ]
    output_layer = Layer(
        neurons=[
            Neuron(weights=[random() for _ in range(n_outputs)], bias=random()),
            Neuron(weights=[random() for _ in range(n_outputs)], bias=random()),
        ],
    )
    network = Network(
        hidden_layers=hidden_layers, output_layer=output_layer, learning_rate=0.5
    )
    network.train(40, n_outputs, dataset, expected)
    print(f"Hidden layer: {network.layers[0].neurons}")
    print(f"Output layer: {network.layers[1].neurons}")
    
    # This is just for demonstration only
    for i in range(len(dataset)):
        prediction = network.predict(dataset[i])
        print("Expected=%d, Got=%d" % (expected[i], prediction))

        
if __name__ == "__main__":
    test_make_prediction_with_network()