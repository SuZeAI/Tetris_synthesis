import numpy as np
from Env.setting import *
class Oservation(object):
    def __init__(self, ob):
        self.ob = ob
    def getPieceAtId(self, id):
        return TETRIS_SHAPE[np.array(np.array(self.ob).squeeze()[:20, 10:17], dtype="float32")[id].argmax()]

    def getIdPiece(self, id):
        return np.array(np.array(self.ob).squeeze()[:20, 10:17], dtype="float32")[id].argmax()

    def getGrid(self):
        return np.array(np.array(self.ob).squeeze()[:20, :10], dtype="int32")

    def maxHeight(self, board):
        return np.argmin(np.sum(board, axis=1)[::-1])

    def get7(self):
        return np.array(np.array(self.ob).squeeze()[:20, 10:17], dtype="float32")