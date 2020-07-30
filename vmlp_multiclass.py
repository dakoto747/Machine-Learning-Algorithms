import numpy
import math
'''
VMLP: Vectorised Multilayer Perceptron 
    a neuron is represented as a vector; 
    a the neural network is represented as an array of a matrix of vectors
    this helps making the training process faster;
    todo: use MinPy to leverage GPU support 
'''
class vmlp(object):
    # tensorflow or scikit learn?
    # you could also use clustering or k-means
    neurons = []
    layer_count = 2
    input_layer_neuron_count = 0
    layer_neuron_count = []
    data = []
    labels = []
    learning_rate = 0.1
    iterations = 1000
    layer_outputs = []
    layer_deltas = []
    weight_updates = []
    predicted_labels = []
    raw_labels = []
    error_rate = 1

    """docstring forvmlp."""
    # labels should be a matrix 
    def __init__(self, data, labels, hidden_layer_nodes_list_rep, learning_rate, iterations, weight_range, use_softmax=False):
        super(vmlp, self).__init__()
        self.input_layer_neuron_count = data.shape[1]
        self.data = data
        self.labels = labels
        self.predicted_labels = numpy.zeros(labels.shape[0])
        self.raw_labels = numpy.zeros(labels.shape[0])
        self.learning_rate = learning_rate
        self.iterations = iterations
        self.use_softmax = use_softmax
        self.logit_layer_node_count = labels.shape[1] 

        if sum(hidden_layer_nodes_list_rep) > 0:
            self.layer_count = len(hidden_layer_nodes_list_rep) + 1 # none for input layer and one for output layer
            self.layer_neuron_count = [self.input_layer_neuron_count] + hidden_layer_nodes_list_rep + [self.logit_layer_node_count ] #output logit
        else:
            self.layer_neuron_count = [self.input_layer_neuron_count] + [self.input_layer_neuron_count] +[self.logit_layer_node_count ]

        for layer in range(0, self.layer_count):
            # initializing weights of vectors/neurons
            layer_neurons = numpy.matrix( 
                numpy.random.random(
                    (self.layer_neuron_count[layer+1], # number of neurons in this layer
                    self.layer_neuron_count[layer]+1) # weights for the neurons in this layer: number of neurons in previous layer plus a bias 
                )
            )
            self.neurons.append(layer_neurons)
            self.weight_updates.append(layer_neurons)
      
    def feedForward(self, input_):
        self.layer_outputs = []
        self.layer_outputs.append(input_)

        for layer in range(0, self.layer_count):
            inp = numpy.c_[self.layer_outputs[layer], 1]
            self.layer_outputs.append(self.numpySigmoid(inp * self.neurons[layer].T))
        
    def feedForwardSoftmax(self, input_):
        self.layer_outputs = []
        self.layer_outputs.append(input_)

        for layer in range(0, self.layer_count):
            inp = numpy.c_[self.layer_outputs[layer], 1] # add a 1 to the input for the bias value
            if layer == layer_count: 
                self.layer_outputs.append(self.softmax(inp * self.neurons[layer].T))
            else:
                self.layer_outputs.append(self.numpySigmoid(inp * self.neurons[layer].T))
        

    def backpropInput(self, label):
        net_activation = self.layer_outputs[self.layer_count] # because it includes the input layer
        training_err = label - net_activation
        output_delta = training_err
        self.layer_deltas = []
        self.layer_deltas.append(output_delta)

        # still correct for multiclass 
        output_delta_w = self.learning_rate * output_delta * numpy.c_[self.layer_outputs[self.layer_count-1], 1]
        for i in range(self.layer_count, 1, -1):
           
            self.layer_deltas.insert(
                0, # input it in position 0 because we're iterating backwards in terms of layers 
                numpy.multiply(
                    self.numpySigDeriv(self.layer_outputs[i-1].T) , 
                    (
                        self.layer_deltas[0].T * self.neurons[i-1][:,0:self.layer_neuron_count[i-1]] # similar to Pytorch's grad fn 
                    ).T
                )
            ) # bias

            # in softmax, we don't multiply by input
            # delta_w = self.learning_rate * self.layer_deltas[0] * numpy.ones(self.layer_neuron_count[i-2]+1)#* numpy.c_[self.layer_outputs[i-2], 1]
            delta_w = self.learning_rate * self.layer_deltas[0] * numpy.c_[self.layer_outputs[i-2], 1]
            self.neurons[i-2] =  delta_w + self.neurons[i-2]

        self.neurons[self.layer_count-1] = self.neurons[self.layer_count-1] + output_delta_w

        

    def train(self):
        if self.use_softmax:
            for x in range(0, self.iterations):
                for y in range(0, self.data.shape[0]):
            
                    input_ = self.data[y, :]
                    self.feedForwardSoftmax(input_)
                    self.backpropInput(self.labels[y])
        else: 
            for x in range(0, self.iterations):
                for y in range(0, self.data.shape[0]):
            
                    input_ = self.data[y, :]
                    self.feedForward(input_)
                    self.backpropInput(self.labels[y])
        
        

    def numpySigDeriv(self, x):
        sigdevfunc = numpy.vectorize(self.sigmoidDerivative)
        return sigdevfunc(x)

        return x * (1 - x)

    def numpySigmoid(self, x):
        sigfunc = numpy.vectorize(self.sigmoid)
        return sigfunc(x)

    def sigmoid(self, x):
        # result = 1.0 / ( 1.0 + math.exp(-x/rho) );
        return 1.0 / ( 1.0 + math.exp(-x) )

    def crossEntropyLoss(self, logit_output, label_vector): 
        # https://peterroelants.github.io/posts/cross-entropy-logistic/
        # https://www.ics.uci.edu/~pjsadows/notes.pdf
        # -t log(x) - (1 - t) log(1 - x)
        # -label_vector log(logit_output) - (1 - label_vector) log(1 - logit_output)
        return - sum(
            (label_vector * numpy.log(logit_output)) + 
            ((1 - label_vector) * log(1-logit_output))
        )

    def crossEntropyLossMultiple(self, logit_output, label_vector): 
        # https://peterroelants.github.io/posts/cross-entropy-logistic/
        # https://www.ics.uci.edu/~pjsadows/notes.pdf
        # -t log(x) - (1 - t) log(1 - x)
        # -label_vector log(logit_output) - (1 - label_vector) log(1 - logit_output)
        return - sum((label_vector - numpy.log(logit_output)))

    def crossEntropyLossDerivative(self, logit_output, label_vector):
        return logit_output - label_vector

    def softmaxGradient(self, logit_output, label_vector): 
        return logit_output - label_vector

    def softmax(self, x):
        """Compute softmax values for each sets of scores in x."""
        '''
        Softmax turn logits (numeric output of the last linear layer of 
        a multi-class classification neural network) into probabilities 
        by taking the exponents of each output and then normalize each number 
        by the sum of those exponents so the entire output vector adds up to one — 
        all probabilities should add up to one. Cross entropy loss is 
        usually the loss function for such a multi-class classification problem.

        Why not just divide each logits by the sum of logits? Why do we need exponents? 
        Logits is the logarithm of odds (wikipedia https://en.wikipedia.org/wiki/Logit) 
        see the graph on the wiki page, it ranges from negative infinity to positive infinity. 
        When logits are negative, adding it together does not give us the correct normalization. 
        exponentiate logitsturn them them zero or positive!
        
        If you have a multi-label classification problem = there is more than one "right answer" = the outputs are NOT mutually exclusive, 
        then use a sigmoid function on each raw output independently. 
        The sigmoid will allow you to have high probability for all of your classes, some of them, or none of them. 
        Example: classifying diseases in a chest x-ray image. The image might contain pneumonia, emphysema, and/or cancer, or none of those findings.
       
        If you have a multi-class classification problem = there is only one "right answer" = the outputs are mutually exclusive, then use a softmax function. 
        The softmax will enforce that the sum of the probabilities of your output classes are equal to one, 
        so in order to increase the probability of a particular class, your model must correspondingly decrease the probability of at least one of the other classes. 
        Example: classifying images from the MNIST data set of handwritten digits.
        A single picture of a digit has only one true identity - the picture cannot be a 7 and an 8 at the same time.
            
        '''

        return numpy.exp(x) / numpy.sum(numpyp.exp(x), axis=0) 
     
    def predictedLabels(self):
        self.patregTest(self.data, self.labels)
        print(self.raw_labels)
           
    def predict(self, input_vector):
        if self.use_softmax:
            self.feedForwardSoftmax(input_vector)
        else: 
            self.feedForward(input_vector)
        return self.layer_outputs[self.layer_count][0,0]

    def faTest(self, data, labels):
        error=0
        for i in range(0, data.shape[0]):
            self.raw_labels[i] = self.predict(data[i,:])
            error = error + (labels[i] - self.raw_labels[i])**2
        result = math.sqrt(error/data.shape[0])
        self.error_rate=result
        return result

    def patregTest(self, data, labels):
        error=0
        for i in range(0, data.shape[0]):
            self.raw_labels[i]=self.predict(data[i,:])
            activation=numpy.argmax(self.raw_labels[i])

            self.predicted_labels[i]=activation
            
            if activation != numpy.argmax(labels[i]):
                error = error+1
            self.error_rate = error/data.shape[0]
        return error/data.shape[0]

#
# data = numpy.matrix([[0,0],[0,1],[1,0],[1,1]])
# labels = numpy.matrix([[0],[1],[1],[0]])
#
# # problem is the difference in sigmoid prediction
# neural_net = vmlp(data, labels, [2], 0.1, 4000)
# neural_net.train()
# neural_net.predictedLabels()
