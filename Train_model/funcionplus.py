import copy
import time

import numpy as np

def bumpiness(board):
    board = np.array(board)
    mask = board != 0
    inv_heights = np.where(mask.any(axis=0),
                           np.argmax(mask, axis=0),
                           20)
    heights = 20 - inv_heights
    currs = heights[:-1]
    nexts = heights[1:]
    diffs = np.abs(currs - nexts)

    total_bumpiness = np.sum(diffs)
    max_bumpiness = np.max(diffs)
    return total_bumpiness, max_bumpiness

def count_holes(board):
    num_holes = 0
    for col in zip(*board):
        row = 0
        while row < 20 and col[row] == 0:
            row += 1
        num_holes += len([x for x in col[row + 1:] if x == 0])
    return num_holes

def remove_row(board, indices):
    for i in indices[::-1]:
        del board[i]
        board = [[0 for _ in range(10)]] + board
    return board

def check_cleared_rows(board):
    to_delete = []
    for i, row in enumerate(board[::-1]):
        if 0 not in row:
            to_delete.append(len(board) - 1 - i)
    if len(to_delete) > 0:
        board = remove_row(copy.deepcopy(board), to_delete)
    return len(to_delete), board

def compute_height(board):
    board = np.array(board)
    mask = board != 0

    # Get the inverted heights
    inv_heights = np.where(mask.any(axis=0),
                           np.argmax(mask, axis=0),
                           20)
    # Get the correct heights
    heights = 20 - inv_heights

    sum_height = np.sum(heights)
    max_height = np.max(heights)
    min_height = np.min(heights)

    return sum_height, max_height, min_height

def get_state_props(board):
    lines_cleared, board = check_cleared_rows(copy.deepcopy(board))
    holes = count_holes(board)
    total_bumpiness, max_bumpiness = bumpiness(board)
    sum_height, max_height, min_height = compute_height(board)

    return [lines_cleared, holes, total_bumpiness, sum_height]


def store(piece, pos, board):
    for y in range(len(piece)):
        for x in range(len(piece[y])):
            if piece[y][x] and not board[y + pos['y']][x + pos['x']]:
                board[y + pos['y']][x + pos['x']] = piece[y][x]
    return board

def check_collision(piece, pos, board):
    future_y = pos['y'] + 1
    result = False
    for y in range(len(piece)):
        for x in range(len(piece[y])):
            if future_y + y > 20-1 or board[future_y + y][pos['x'] + x] and piece[y][x]:
                return True
    return False

def rotate_CW(piece):
    num_rows_orig = num_cols_new = len(piece)
    num_cols_orig = num_rows_new = len(piece[0])
    rotated_array = []

    for i in range(num_rows_new):
        new_row = [0] * num_cols_new
        for j in range(num_cols_new):
            new_row[j] = piece[(num_rows_orig-1)-j][i]
        rotated_array.append(new_row)
    return rotated_array

def get_next_states(grid, piece):
    states = {}
    grid = list(grid)
    curr_piece = [row[:] for row in piece]
    num_rotations = 4
    for i in range(num_rotations):
        # Loop over all possible x values the upper left corner of the
        # piece can take
        valid_xs = 10 - len(curr_piece[0])
        for x in range(valid_xs + 1):
            piece = [row[:] for row in curr_piece]
            pos = {'x': x,
                   'y': 0}
            # Drop the piece
            while not check_collision(piece, pos, grid):
                pos['y'] += 1
            board = store(piece, pos, grid)
            states[(x, i)] = get_state_props(board)
        curr_piece = rotate_CW(curr_piece)
    return states


def get_piece(ob):
    grid = np.array(np.array(ob).squeeze()[:20, :10], dtype="float16")
    cvt_TF = grid == 0.3
    cols_sum = cvt_TF.sum(axis=0)
    rows_sum = cvt_TF.sum(axis=1)
    if sum(cols_sum) == 0:
        return False, False, False
    x = list(cols_sum > 0)
    y = list(rows_sum > 0)
    x1, x2 = x.index(1), x.index(1) + sum(x)
    y1, y2 = y.index(1), y.index(1) + sum(y)
    # position start top - left: x1, y1
    gr = np.array(grid[y1:y2, x1:x2] + 0.7, dtype="int16")
    piece = tuple([tuple([x for x in rows]) for rows in gr])
    return piece, x1, y1
def get_grid(ob):
    return np.array(np.array(ob).squeeze()[:20, :10], dtype="float16")
def get_next_piece(ob):
    return np.array(np.array(ob).squeeze()[:20, 10:17], dtype="float16")[1].argmax()
def get_7(ob):
    return np.array(np.array(ob).squeeze()[:20, 10:17], dtype="float16")