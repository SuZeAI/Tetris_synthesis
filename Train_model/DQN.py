import random
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Flatten, Layer
from keras.optimizers import Adam
from collections import deque

class Agent(object):
    def __init__(self, state_size, discount=0.98, replay_mem_size=20000,
                 minibatch_size=512, epsilon=1,
                 epsilon_stop_epsisode=1500, epsilon_min=1e-3,
                 learning_rate=1e-3, loss="mse",
                 optimizer=Adam, hidden_dims=[64, 64],
                 activations=['relu', 'relu', 'linear']):

        if len(activations) != len(hidden_dims) + 1:
                raise Exception("Error activations should greater hidden_dims")

        self.state_size = state_size
        self.discount = discount
        self.replay_mem_size = deque(maxlen=replay_mem_size)
        self.minibatch_size = minibatch_size
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = (self.epsilon - self.epsilon_min)/epsilon_stop_epsisode
        self.learning_rate = learning_rate
        self.loss = loss
        self.optimizer = optimizer
        self.hidden_dims = hidden_dims
        self.activations = activations

        self.model = self.initModel()

    def initModel(self):

        model = Sequential()
        model.add(Flatten(input_dim=self.state_size))
        model.add(Dense(units=self.hidden_dims[0], activation=self.activations[0]))
        model.add(Dense(units=self.hidden_dims[1], activation=self.activations[1]))
        model.add(Dense(units=1, activation=self.activations[-1]))
        model.compile(self.optimizer(lr=self.learning_rate, name="Adam"), loss=self.loss)
        print("{:^50}".format("create model successful"))
        print(model.summary())
        print("{:^50}".format("end init"))
        return model

    def update_mem_replay(self, current_state, action, next_state, reward, done):
        self.replay_mem_size.append([current_state, action, next_state, reward, done])

    def get_qs(self, state):
        return self.model.predict(state)[0]

    def get_best_state(self, states):
        max_value = None
        best_state = None

        if random.random() <= self.epsilon:
            return random.choice(list(states))
        else:
            for state in states:
                value = self.get_qs(np.reshape(state, (1, self.state_size)))
                if not max_value or max_value <= value:
                    max_value = value
                    best_state = state

        return best_state

    def trainModel(self, epochs):
        if len(self.replay_mem_size) < self.minibatch_size:
            return

        minibatch = random.sample(self.replay_mem_size, self.minibatch_size)

        next_states = np.array([transition[2] for transition in minibatch])
        next_qs = [x[0] for x in self.model.predict(next_states)]

        X = []
        Y = []
        print(minibatch[0])
        for i, (current_state, action, _, reward, done) in enumerate(minibatch):
            if not done:
                new_q = reward + self.discount * np.max(next_qs)
            else:
                new_q = reward

            X.append(current_state)
            Y.append(new_q)

        self.model.fit(np.array(X), np.array(Y), batch_size=self.minibatch_size, verbose=0, epochs=epochs)









