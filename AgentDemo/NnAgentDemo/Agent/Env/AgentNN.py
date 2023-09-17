import os
from keras.models import Sequential
from keras.layers import Dense, Flatten
from keras.optimizers import Adam
import tensorflow as tf
# import numpy as np
# import copy
from field import *
def rotate_clockwise(shape):
    return [[shape[y][x]
             for y in range(len(shape))]
            for x in range(len(shape[0]) - 1, -1, -1)]


class AgentNN(object):
    def __init__(self, input_shape, optimizer=Adam, loss="mse",
                 learning_rate=0.1, activation=("relu", "relu", "linear"), dimenson=(64, 64)):
        self.input_shape = input_shape
        self.optimizer = optimizer
        self.loss = loss
        self.learning_rate = learning_rate
        self.activation = activation
        self.dimenson = dimenson

        self.model = self.createModel()

    def createModel(self):
        tf.random.set_seed(42)
        model = Sequential()
        model.add(Flatten(input_shape=self.input_shape))
        model.add(Dense(units=self.dimenson[0], activation=self.activation[0]))
        model.add(Dense(units=self.dimenson[1], activation=self.activation[1]))
        model.add(Dense(units=1, activation=self.activation[2]))

        model.compile(loss=self.loss, optimizer=self.optimizer(learning_rate=self.learning_rate, name="Adam"))
        # print(model.summary())
        return model

    def getWeight(self):
        """
        :return: list[array()]
        """
        return self.model.get_weights()

    def update_weight(self, weight):
        """
        :param weight: list[np.array()]
        :return: None
        """
        self.model.set_weights(weight)

    def save_model(self):
        ROOT = os.path.abspath(os.path.dirname(__file__))
        self.model.save("model.h5")

    def get_predict(self, data):
        """
        :param data: input: list have dim (1, 4)
        :return: predict int
        """
        return self.model.predict(np.array(data).reshape(1, 4), verbose=0)[0]

    def get_best(self, piece, field, id, idPiece):
        """
        :param self: AgentNN
        :param piece: list[list[]]
        :param field: grid
        :return: int, int
        """
        rotate_nb = {4: 4, 8: 2, 12: 2, 16: 4, 20: 4, 24: 2, 28: 1}
        offetX = None
        rotate_rt = None
        score_max = None
        piece_crr = piece[idPiece]
        for rotate in range(rotate_nb[np.sum(piece_crr)]):
            for offset in range(field.width):
                result = field.projectPieceDown(piece_crr, offset, id)
                if result is not None:
                    if len(piece) - 1 == idPiece:
                        heuristics = field.heuristics()
                        score = self.get_predict(heuristics)[0]
                    else:
                        _, _, score = self.get_best(piece, field, id + 1, idPiece + 1)

                    if score_max is None or score > score_max:
                        # print("check", offset)
                        score_max = score
                        offetX = offset
                        rotate_rt = rotate
                field.undo(id)
            piece_crr = rotate_clockwise(copy.deepcopy(piece_crr))

        return offetX, rotate_rt, score_max

    def choose(self, grid, piece, nextPiece, offsetX, parent):
        field = Field(len(grid[0]), len(grid))
        field.updateField(grid)
        print("check")
        offset, rotation, _ = self.get_best([piece, nextPiece], field, 1, 0)

        moves = []

        print("offfset: ", offset)
        offset = offset - offsetX
        for _ in range(0, rotation):
            moves.append("UP")
        for _ in range(0, abs(offset)):
            if offset > 0:
                moves.append("RIGHT")
            else:
                moves.append("LEFT")
        # moves.append('RETURN')
        print(moves)
        parent.executes_moves(moves)