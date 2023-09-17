import copy
import time

import numpy as np
# variable const_____________________________________________________________________
TETRIS_SHAPES = [
    [[0, 1, 0],
     [1, 1, 1]],

    [[0, 2, 2],
     [2, 2, 0]],

    [[3, 3, 0],
     [0, 3, 3]],

    [[4, 0, 0],
     [4, 4, 4]],

    [[0, 0, 5],
     [5, 5, 5]],

    [[6, 6, 6, 6]],

    [[7, 7],
     [7, 7]]
]
DIC_PIECE = {
    ((0, 1, 0),
     (1, 1, 1)): 0,
    ((0, 1, 1),
     (1, 1, 0)): 1,
    ((1, 1, 0),
     (0, 1, 1)): 2,
    ((1, 0, 0),
     (1, 1, 1)): 3,
    ((0, 0, 1),
     (1, 1, 1)): 4,
    ((1, 1, 1, 1),): 5,
    ((1, 1),
     (1, 1)): 6
}
#____________________________________________________________________________________

# Function Plus______________________________________________________________________
def rotate_clockwise(shape):
    return [ [ shape[y][x]
            for y in range(len(shape)) ]
        for x in range(len(shape[0]) - 1, -1, -1) ]
#____________________________________________________________________________________

# class______________________________________________________________________________
class Field(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.field = [[0]*self.width]*self.height

    def size(self):
        return self.width, self.height

    def updateField(self, field):
        self.field = field

    @staticmethod
    def check_collision(field, shape, offset):
        off_x, off_y = offset
        for cy, row in enumerate(shape):
            for cx, cell in enumerate(row):
                try:
                    if cell and field[ cy + off_y ][ cx + off_x ]:
                        return True
                except IndexError:
                    return True
        return False

    def projectPieceDown(self, piece, offsetX, workingPieceIndex):
        if offsetX+len(piece[0]) > self.width or offsetX < 0:
            return None
        #result = copy.deepcopy(self)
        offsetY = self.height
        for y in range(0, self.height):
            if Field.check_collision(self.field, piece, (offsetX, y)):
                offsetY = y
                break
        for x in range(0, len(piece[0])):
            for y in range(0, len(piece)):
                value = piece[y][x]
                if value > 0:
                    self.field[offsetY-1+y][offsetX+x] = -workingPieceIndex
        return self

    def undo(self, workingPieceIndex):
        self.field = [[0 if el == -workingPieceIndex else el for el in row] for row in self.field]

    def heightForColumn(self, column):
        width, height = self.size()
        for i in range(0, height):
            if self.field[i][column] != 0:
                return height-i
        return 0

    def heights(self):
        result = []
        width, height = self.size()
        for i in range(0, width):
            result.append(self.heightForColumn(i))
        return result

    def numberOfHoleInColumn(self, column):
        result = 0
        maxHeight = self.heightForColumn(column)
        for height, line in enumerate(reversed(self.field)):
            if height > maxHeight: break
            if line[column] == 0 and height < maxHeight:
                result+=1
        return result

    def numberOfHoleInRow(self, line):
        result = 0
        for index, value in enumerate(self.field[self.height-1-line]):
            if value == 0 and self.heightForColumn(index) > line:
                result += 1
        return result

    ################################################
    #                   HEURISTICS                 #
    ################################################

    def heuristics(self):
        heights = self.heights()
        maxColumn = self.maxHeightColumns(heights)
        return heights + [self.aggregateHeight(heights)] + self.numberOfHoles(heights) + self.bumpinesses(heights) + [self.completLine(), self.maxPitDepth(heights), self.maxHeightColumns(heights), self.minHeightColumns(heights)]

    def aggregateHeight(self, heights):
        result = sum(heights)
        return result

    def completLine(self):
        result = 0
        width, height = self.size()
        for i in range (0, height) :
            if 0 not in self.field[i]:
                result+=1
        return result

    def bumpinesses(self, heights):
        result = []
        for i in range(0, len(heights)-1):
            result.append(abs(heights[i]-heights[i+1]))
        return result

    def numberOfHoles(self, heights):
        results = []
        width, height = self.size()
        for j in range(0, width) :
            result = 0
            for i in range (0, height) :
                if self.field[i][j] == 0 and height-i < heights[j]:
                    result+=1
            results.append(result)
        return results

    def maxHeightColumns(self, heights):
        return max(heights)

    def minHeightColumns(self, heights):
        return min(heights)

    def maximumHoleHeight(self, heights):
        if self.numberOfHole(heights) == 0:
            return 0
        else:
            maxHeight = 0
            for height, line in enumerate(reversed(self.field)):
                if sum(line) == 0: break
                if self.numberOfHoleInRow(height) > 0:
                    maxHeight = height
            return maxHeight

    def rowsWithHoles(self, maxColumn):
        result = 0
        for line in range(0, maxColumn):
            if self.numberOfHoleInRow(line) > 0:
                result += 1
        return result

    def maxPitDepth(self, heights):
        return max(heights)-min(heights)



    @staticmethod
    def __offsetPiece(piecePositions, offset):
        piece = copy.deepcopy(piecePositions)
        for pos in piece:
            pos[0] += offset[0]
            pos[1] += offset[1]

        return piece

    def __checkIfPieceFits(self, piecePositions):
        for x,y in piecePositions:
            if 0 <= x < self.width and 0 <= y < self.height:
                if self.field[y][x] >= 1:
                    return False
            else:
                return False
        return True

    def fitPiece(self, piecePositions, offset=None):
        if offset:
            piece = self.__offsetPiece(piecePositions, offset)
        else:
            piece = piecePositions

        field = copy.deepcopy(self.field)
        if self.__checkIfPieceFits(piece):
            for x,y in piece:
                field[y][x] = 1

            return field
        else:
            return None
class GetBest(object):

    @staticmethod
    def best(field, workingPieces, workingPieceIndex, weights, level):
        bestRotation = None
        bestOffset = None
        bestScore = None
        workingPieceIndex = copy.deepcopy(workingPieceIndex)
        workingPiece = workingPieces[workingPieceIndex]
        shapes_rotation = { 4 : 4, 8 : 2, 12 : 2, 16 : 4, 20 : 4, 24 : 2, 28 : 1 }
        try:
            flat_piece = [val for sublist in workingPiece for val in sublist]
        except:
            print(workingPiece)
        hashedPiece = sum(flat_piece)

        for rotation in range(0, shapes_rotation[hashedPiece]):
            for offset in range(0, field.width):
                result = field.projectPieceDown(workingPiece, offset, level)
                if not result is None:
                    score = None
                    if workingPieceIndex == len(workingPieces)-1 :
                        heuristics = field.heuristics()
                        score = sum([a*b for a,b in zip(heuristics, weights)])
                    else:
                        _, _, score = GetBest.best(field, workingPieces, workingPieceIndex + 1, weights, 2)

                    if (bestScore is None) or (score > bestScore):
                        bestScore = score
                        bestOffset = offset
                        bestRotation = rotation
                field.undo(level)
            workingPiece = rotate_clockwise(workingPiece)

        return bestOffset, bestRotation, bestScore

    @staticmethod
    def choose(initialField, piece, next_piece, offsetX, weights, parent):
        print(len(initialField[0]), len(initialField))
        field = Field(len(initialField[0]), len(initialField))
        field.updateField(copy.deepcopy(initialField))

        offset, rotation, _ = GetBest.best(field, [piece, next_piece], 0, weights, 1)
        moves = []

        offset = offset - offsetX
        for _ in range(0, rotation):
            moves.append(3)
        for _ in range(0, abs(offset)):
            if offset > 0:
                moves.append(5)
            else:
                moves.append(6)
        #moves.append('RETURN')
        moves.append(2)
        parent.list_action.extend(moves)
        print(offsetX, parent.list_action)
#____________________________________________________________________________________

# Main_______________________________________________________________________________

class Agent(object):
    def __init__(self, turn):
        # root = os.path.abspath(os.path.dirname(__file__))
        # model_file_path = os.path.join(root, "model.h5")
        # self.model = keras.models.load_model(model_file_path)
        self.list_action = []
        self.weight = [0.39357083734159515, -1.8961941343266449, -5.107694873375318, -3.6314963941589093,
                       -2.9262681134021786, -2.146136640641482, -7.204192964669836, -3.476853402227247,
                       -6.813002842291903, 4.152001386170861, -21.131715861293525, -10.181622180279133,
                       -5.351108175564556, -2.6888972099986956, -2.684925769670947, -4.504495386829769,
                       -7.4527302422826, -6.3489634714511505, -4.701455626343827, -10.502314845278828,
                       0.6969259450910086, -4.483319180395864, -2.471375907554622, -6.245643268054767,
                       -1.899364785170105, -5.3416512085013395, -4.072687054171711, -5.936652569831475,
                       -2.3140398163110643, -4.842883337741306, 17.677262456993276, -4.42668539845469,
                       -6.8954976464473585, 4.481308299774875]

    def get_piece_current(self, ob):
        grid = np.array(np.array(ob).squeeze()[:20, :10], dtype="float32")
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
        gr = np.array(cvt_TF[y1:y2, x1:x2], dtype="int32")
        piece = tuple([tuple([x for x in rows]) for rows in gr])
        try:
            return TETRIS_SHAPES[DIC_PIECE[piece]], x1, y1
        except:
            return TETRIS_SHAPES[0], 3, 0


    def get_next_piece(self, ob):
        return TETRIS_SHAPES[np.array(np.array(ob).squeeze()[:20, 10:17], dtype="float16")[1].argmax()]

    def get_grid(self, ob):
        return np.array(np.array(ob).squeeze()[:20, :10], dtype="int16")

    def choose_action(self, observation):
        if len(self.list_action) != 0:
            action = self.list_action[0]
            self.list_action.pop(0)
            print(self.list_action)
            return action
        else:
            crr_piece, x, _ = self.get_piece_current(observation)
            next_piece = self.get_next_piece(observation)
            board = self.get_grid(observation)
            GetBest.choose(board, crr_piece, next_piece, x, self.weight, self)
            self.choose_action(observation)

if __name__ == "__main__":
    pass

