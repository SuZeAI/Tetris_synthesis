import copy
import time

import numpy as np

################################################
#                  CONST VALUE                 #
################################################
TETRIS_SHAPES = [
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


################################################
#                   FUNCTION                   #
################################################
def rotate_clockwise(shape):
    return [[shape[y][x]
             for y in range(len(shape))]
            for x in range(len(shape[0]) - 1, -1, -1)]


################################################
#                      CLass                   #
################################################
class Field(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.field = [[0] * self.width] * self.height

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
                    if cell and field[cy + off_y][cx + off_x]:
                        return True
                except IndexError:
                    return True
        return False

    def projectPieceDown(self, piece, offsetX, workingPieceIndex):
        if offsetX + len(piece[0]) > self.width or offsetX < 0:
            return None
        offsetY = self.height
        for y in range(0, self.height):
            if Field.check_collision(self.field, piece, (offsetX, y)):
                offsetY = y
                break
        for x in range(0, len(piece[0])):
            for y in range(0, len(piece)):
                value = piece[y][x]
                if value > 0:
                    self.field[offsetY - 1 + y][offsetX + x] = -workingPieceIndex
        return self

    def undo(self, workingPieceIndex):
        self.field = [[0 if el == -workingPieceIndex else el for el in row] for row in self.field]

    def heightForColumn(self, column):
        width, height = self.size()
        for i in range(0, height):
            if self.field[i][column] != 0:
                return height - i
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
                result += 1
        return result

    def numberOfHoleInRow(self, line):
        result = 0
        for index, value in enumerate(self.field[self.height - 1 - line]):
            if value == 0 and self.heightForColumn(index) > line:
                result += 1
        return result

    # |----------------------------------------------|
    #                   HEURISTICS                   #
    # |----------------------------------------------|

    def heuristics(self):
        heights = self.heights()
        maxColumn = self.maxHeightColumns(heights)
        return heights + [self.aggregateHeight(heights)] + self.numberOfHoles(heights) + self.bumpinesses(heights) + [
            self.completLine(), self.maxPitDepth(heights), self.maxHeightColumns(heights),
            self.minHeightColumns(heights)]

    def aggregateHeight(self, heights):
        result = sum(heights)
        return result

    def completLine(self):
        result = 0
        width, height = self.size()
        for i in range(0, height):
            if 0 not in self.field[i]:
                result += 1
        #######################################################
        # if result == 0: return 0
        # elif result == 1: return 0
        # elif result == 2: return 100
        # elif result == 3: return 200

        return result
        ########################################################

    def bumpinesses(self, heights):
        result = []
        for i in range(0, len(heights) - 1):
            result.append(abs(heights[i] - heights[i + 1]))
        return result

    def numberOfHoles(self, heights):
        results = []
        width, height = self.size()
        for j in range(0, width):
            result = 0
            for i in range(0, height):
                if self.field[i][j] == 0 and height - i < heights[j]:
                    result += 1
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
        return max(heights) - min(heights)

    @staticmethod
    def __offsetPiece(piecePositions, offset):
        piece = copy.deepcopy(piecePositions)
        for pos in piece:
            pos[0] += offset[0]
            pos[1] += offset[1]

        return piece

    def __checkIfPieceFits(self, piecePositions):
        for x, y in piecePositions:
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
            for x, y in piece:
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
        shapes_rotation = {4: 4, 8: 2, 12: 2, 16: 4, 20: 4, 24: 2, 28: 1}
        flat_piece = [val for sublist in workingPiece for val in sublist]
        hashedPiece = sum(flat_piece)

        for rotation in range(0, shapes_rotation[hashedPiece]):
            for offset in range(0, field.width):
                result = field.projectPieceDown(workingPiece, offset, level)
                if not result is None:
                    score = None
                    if workingPieceIndex == len(workingPieces) - 1:
                        heuristics = field.heuristics()
                        score = sum([a * b for a, b in zip(heuristics, weights)])
                    else:
                        _, _, score = GetBest.best(field, workingPieces, workingPieceIndex + 1, weights, level + 1)

                    if (bestScore is None) or (score > bestScore):
                        bestScore = score
                        bestOffset = offset
                        bestRotation = rotation
                field.undo(level)
            workingPiece = rotate_clockwise(workingPiece)

        return bestOffset, bestRotation, bestScore

    @staticmethod
    def choose(initialField, piece, next_piece, offsetX, weights, parent, id):
        field = Field(len(initialField[0]), len(initialField))
        field.updateField(copy.deepcopy(initialField))
        offset, rotation, _ = GetBest.best(field, [piece, next_piece], 0, weights, 1)
        moves = []
        if id == 7: offsetX += 1
        if rotation == 3:
            offsetX += 1
        elif rotation == 1 and id == 6:
            offsetX += 1

        print("offsetX:", offsetX)
        print("offset:", offset)
        offset = offset - offsetX
        for _ in range(0, rotation):
            moves.append(4)
        for _ in range(0, abs(offset)):
            if offset > 0:
                moves.append(5)
            else:
                moves.append(6)
        moves.append(2)
        parent.list_action.extend(moves)


################################################
#                     Agent                    #
################################################

class Agent(object):
    def __init__(self, turn):
        # root = os.path.abspath(os.path.dirname(__file__))
        # model_file_path = os.path.join(root, "model.h5")
        # self.model = keras.models.load_model(model_file_path)
        self.list_action = []
        # self.weight = [0.39357083734159515, -1.8961941343266449, -5.107694873375318, -3.6314963941589093, -2.9262681134021786, -2.146136640641482, -7.204192964669836, -3.476853402227247, -6.813002842291903, 4.152001386170861, -21.131715861293525, -10.181622180279133, -5.351108175564556, -2.6888972099986956, -2.684925769670947, -4.504495386829769, -7.4527302422826, -6.3489634714511505, -4.701455626343827, -10.502314845278828, 0.6969259450910086, -4.483319180395864, -2.471375907554622, -6.245643268054767, -1.899364785170105, -5.3416512085013395, -4.072687054171711, -5.936652569831475, -2.3140398163110643, -4.842883337741306, 17.677262456993276, -4.42668539845469, -6.8954976464473585, 4.481308299774875]
        self.weight = [-2.503203450528113, -6.232148141856897, -4.889022639678535, -5.483191625315361,
                       -5.621116241119032, -7.167988262189014, -3.787280013510496, -7.1433724740204925,
                       -6.820522834607067, 4.156362964813036, -23.764795034066324, -17.36836019094467,
                       -6.6518818320983035, 2.7040604325130286, -19.764237133686873, -6.405123768951559,
                       -6.258423157239519, -9.104965785418177, -3.9580234761128787, -1.9310935590686635,
                       -13.801667307038553, -4.762971682982187, 0.839292713552033, -2.9922313458582694,
                       -6.75452824882575, -6.900109485346231, -3.3173538574836168, -3.86242852312692,
                       -7.3743581151540045, -2.0437270423997727, 9.836725060604877, -8.114889750599733,
                       -8.895551330060245, 3.256322916796323]
        # self.weight = [-2.092101985761462, -6.157692009243851, -4.69504075247928, -5.868865261933104, -4.174932167471736, -7.147570297901506, -3.835620207373367, -7.121686462485371, -6.840400473239583, 4.117417796467243, -23.085011574460424, -17.378401587571293, -6.68749926766231, 2.973035166696902, -6.378320361628544, -4.3122332705732696, -7.013615566263364, -9.278902518666833, -4.2376588055776425, -2.349944930164783, -13.601612635375794, -4.6976044398402825, 1.0517161646901183, -3.134307763425047, -5.814828804626929, -6.811567694792287, -3.3423493976208123, -3.9744409098946454, -7.48014274200137, -1.819651656550658, 9.84027193933466, -8.116736094413634, -8.875281365529787, 3.0928063442630584]
        # self.weight = [-2.3535715221199114, -6.184306985732168, -2.5088213333078917, -5.1728131327905285, -5.179067579492058, -7.114493946641594, -3.8538394411680414, -7.133284920575231, -6.83624706619042, 4.348518667351807, -23.390773643260697, -17.49190148992391, -6.695116733363868, 3.5181891582490565, -20.62167460167828, -4.808217227230028, -6.284489437680635, -9.195683939227523, -4.941290610406047, -2.250570723879471, -13.52900384009877, -4.717034995372051, 1.2216006318764911, -3.840648218296267, -6.422283018078107, -6.232331134679149, -3.412272636306671, -4.278083421550721, -7.3869057543192564, -1.6741752098036946, 9.862898599735047, -8.18920477962554, -8.96538085037683, 3.2096129377255656]
        # self.weight = [-2.477107258177053, -6.382596371387953, -5.061015047528198, -5.275772467883689, -4.197970370468587, -7.157973968078759, -3.622049169510937, -6.910711119222375, -6.83498084652584, 4.00137623233897, -22.511266954724935, -17.446782961895718, -6.6439686576935895, 2.496440341941779, -14.593959096207318, -6.098996358789119, -6.2046579590900555, -9.152750717725258, -4.823294510540408, -2.6087695948224865, -13.898044397841359, -4.88092509519146, 1.9488473063767524, -3.314648601476849, -6.86357827364368, -6.485315318629907, -3.1696739105592413, -4.252523866289832, -7.3775250227271805, -2.1846016412888694, 9.837784113484332, -8.104878177622028, -8.884314130035564, 3.106728061523182]
        # self.weight = [-2.114409315958902, -6.600353417095967, -4.4838597971780585, -5.442277399896397, -7.427331047406691, -7.108042302510307, -3.6705911459811347, -7.4691729807476195, -6.820845969123389, 4.181035746730205, -22.745566224619438, -17.433438138751956, -6.705426810078855, 2.8768385748481364, -14.089870111045625, -5.1729794844718615, -5.681750995178749, -9.11144709261052, -4.435806133026812, -2.11007806547817, -13.773004771179925, -4.533017386932546, 1.113556394587005, -3.2911296067414457, -6.267529586529296, -7.547385118351671, -3.2918227409036405, -3.864498517677048, -7.368650548706378, -2.102567995363515, 9.860304080529003, -8.023671465703787, -9.223487885249229, 3.127318988573003]
        # self.weight = [-2.288377460517875, -6.426867472412552, -2.6676753558339046, -4.904800928701944, -6.654776582364347, -7.2494738303370285, -3.7814621420779093, -6.625602678836543, -6.851516641462909, 4.26082136286486, -22.705276139120116, -17.47270934926082, -6.837412478350752, 3.4406804539695255, -12.054260756128006, -4.548971255899007, -6.380582883899651, -8.992206953177792, -4.540584796382033, -2.1238428737671713, -13.352657197693985, -4.57690246117096, 1.0425812028737798, -2.948201261372145, -6.130581380460365, -6.889581112942637, -3.534175127525335, -4.351486961320134, -7.314959727220688, -1.6526954488942005, 9.830718133147535, -8.246422633591889, -9.14034708605627, 3.1195208020062557]

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
        # position start cell top - left: x1, y1
        gr = np.array(cvt_TF[y1:y2, x1:x2], dtype="int32")
        piece = tuple([tuple([x for x in rows]) for rows in gr])
        # return TETRIS_SHAPES[DIC_PIECE[piece]], x1, y1

    def get_next_piece(self, ob, id):
        return TETRIS_SHAPES[np.array(np.array(ob).squeeze()[:20, 10:17], dtype="float32")[id].argmax()]

    def get_grid(self, ob):
        return np.array(np.array(ob).squeeze()[:20, :10], dtype="int32")

    def max_height(self, board):
        return np.argmin(np.sum(board, axis=1)[::-1])

    def get_7(self, ob):
        return np.array(np.array(ob).squeeze()[:20, 10:17], dtype="float32")

    def choose_action(self, observation):
        if len(self.list_action) != 0:
            action = self.list_action[0]
            self.list_action.pop(0)
            return action
        else:
            board = self.get_grid(copy.deepcopy(observation))
            print(
                "state:___________________________________________________________________________________________________________________________")
            print(np.array(np.array(observation).squeeze()[:20, :10], dtype="float16"))
            # print(board, self.max_height(board))
            # print(self.get_7(observation))
            # if self.max_height(board) <= 17:
            # _, x, _ = self.get_piece_current(copy.deepcopy(observation))
            x = 4
            crr_piece = self.get_next_piece(copy.deepcopy(observation), 6)
            next_piece = self.get_next_piece(copy.deepcopy(observation), 1)
            GetBest.choose(board, crr_piece, next_piece, x, self.weight, self, crr_piece[0][0])
            print(self.list_action)
            return self.choose_action(observation)

