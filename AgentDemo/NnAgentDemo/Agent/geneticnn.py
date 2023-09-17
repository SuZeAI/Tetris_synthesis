from tqdm import tqdm
from functools import cmp_to_key
from copy import deepcopy
import numpy as np
import random

INPUT_SHAPE = 4, 1
EPSILON = 0.6
NBESTPPOPULATION = 2
ROUNDS = 4
LIMITPIECE = 200
RANDOM_NWEIGHT = 3

def cmp(a, b):
    if a[1] < b[1]: return 1
    else: return -1

class Geneticnn(object):
    def __init__(self, population, epochs, limit_piece, epsilon):
        self.epochs = epochs
        self.limit_piece = limit_piece
        self.epsilon = epsilon
        self.population = population

    def genIndv(self):
        return AgentNN(input_shape=INPUT_SHAPE)

    def genPopulations(self):
        weight_population = []
        for i in range(self.population):
            weight_population.append(self.genIndv())
        return weight_population

    def getFitness(self,indv):
        """
        play -> score
        :return: score of Agent: int
        """
        score = 0
        for round in range(ROUNDS):
            score += TetrisApp(playWithUI=False, seed=np.random.randint(1, 100000), Ai=indv).run(LIMITPIECE)
        return score

    def getBestNPopulation(self, listAgent):
        """
        :param listAgent: list[(AgentNN, score)]
        :return: list[AgentNN]
        """
        return list(zip(*(sorted(listAgent, key=cmp_to_key(mycmp=cmp))[:NBESTPPOPULATION])))[0]

    def excuteCross(self,indv1: AgentNN, indv2: AgentNN) -> list[AgentNN]:
        weight1 = indv1.getWeight()
        weight2 = indv2.getWeight()

        for i in range(np.random.randint(RANDOM_NWEIGHT)):
            if np.random.rand() > 0.3:
                idx = np.random.randint(len(weight1))
                weight1, weight2 = weight1[:idx] + weight2[idx:], weight2[:idx] + weight1[idx:]

        return [AgentNN(INPUT_SHAPE).update_weight(weight1), AgentNN(INPUT_SHAPE).update_weight(weight2)]

    def crossGen(self, indv1, indv2):
        if np.random.rand() > 0.4:
            return self.excuteCross(indv1, indv2)
        else:
            return [self.genIndv(), self.genIndv()]

    def excuteMutate(self, indv: AgentNN):
        """
        :param indv:
        :return: AgentNN
        """
        agent = AgentNN(input_shape=INPUT_SHAPE)
        weight = indv.getWeight()
        for i in range(np.random.randint(RANDOM_NWEIGHT)):
            if np.random.rand() > 0.3:
                idx = np.random.randint(len(weight))
                array = weight[idx].copy()
                if idx % 2 == 0 and len(array.shape) == 2:
                    print(array)
                    colUP, colDown = sorted(list(random.choices(np.arange(len(array)), k=2)))
                    rowLeft, rowRight = sorted(list(random.choices(np.arange(len(array[0])), k=2)))
                    sample = np.random.rand(rowRight - rowLeft + 1, colDown - colUP + 1)
                    array[rowRight - rowLeft + 1, colDown - colUP + 1] = sample
                else:
                    pass
            else:
                idx = np.random.randint(len(weight))
                if len(weight[idx].shape) == 2:
                    sample = np.random.rand(len(weight[idx][0]), len(weight[idx]))
                    weight[idx] = sample
        print(weight)
        agent.update_weight(weight)

        return agent

    def mutateGen(self, indv):
        if np.random.rand() > 0.5:
            return self.excuteMutate(indv)
        else:
            return self.genIndv()

    def normalGen(self):
        pass

    def genRemain(self, nremain, nbestgen):
        remainGen = []
        for gen in range(nremain):
            if np.random.rand() > 0.4:
                remainGen.append(self.mutateGen(random.choice(nbestgen)))
            else:
                remainGen.extend(self.crossGen(*random.choices(nbestgen, k=2)))
        return remainGen

    def trainGeneticNN(self):
        gen = self.genPopulations()
        for epoch in tqdm(range(self.epochs)):
            print()
            listAgnt: list[tuple[AgentNN, int]] = []
            for idx, idiv in enumerate(gen):
                print(f"indv: {idx}/{len(gen)}")
                score = self.getFitness(idiv)
                listAgnt.append((idiv, score))
                # print(listAgnt[-1][1], np.array(listAgnt[-1][0].getWeight()).flatten())
                print(listAgnt[-1][1])

            bestPop = list(self.getBestNPopulation(listAgnt))
            print(bestPop)
            gen = deepcopy(bestPop)
            gen.extend(self.genRemain(self.population - NBESTPPOPULATION, bestPop))


DG = Geneticnn(population=5, epochs=5 , limit_piece=200, epsilon=0.5)
DG.trainGeneticNN()