import random
import time
import numpy as np
import pygame.display
from TetrisBattle.envs.tetris_env import *
from funcionplus import *
env = TetrisSingleEnv(mode="suzeu", obs_type="grid")
env.reset()
# ls = [4, 4, 4, 6, 6, 6, 6, 2]
# i = 0
# while i < len(ls):
#     env.step(ls[i])
#     pygame.display.update()
#     time.sleep(1)
#     i += 1
tetris_shapes = [
    [[6, 6, 6, 6]],
    [[7, 7],
     [7, 7]],
    [[4, 0, 0],
     [4, 4, 4]],
    [[0, 0, 5],
     [5, 5, 5]],
    [[3, 3, 0],
     [0, 3, 3]],
    [[0, 2, 2],
     [2, 2, 0]],
    [[0, 1, 0],
     [1, 1, 1]],
]
DIC_PIECE = {
    ((0, 1, 0),
     (1, 1, 1)): 6,
    ((0, 1, 1),
     (1, 1, 0)): 5,
    ((1, 1, 0),
     (0, 1, 1)): 4,
    ((1, 0, 0),
     (1, 1, 1)): 2,
    ((0, 0, 1),
     (1, 1, 1)): 3,
    ((1, 1, 1, 1),): 0,
    ((1, 1),
     (1, 1)): 1
}
for i in range(3):
    ob, _, _, _ = env.step(5)
    print(get_grid(ob))
    print(get_piece(ob)[0])
    print(tetris_shapes[DIC_PIECE[get_piece(ob)[0]]])
    print(tetris_shapes[get_next_piece(ob)])
    print(get_7(ob))
time.sleep(100)
# def rotate_clockwise(shape):
#     return [ [ shape[y][x]
#             for y in range(len(shape)) ]
#         for x in range(len(shape[0]) - 1, -1, -1) ]
# print(np.array(rotate_clockwise(tetris_shapes[2])))