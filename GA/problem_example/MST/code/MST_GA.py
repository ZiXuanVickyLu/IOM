import my_random as r
import math
import time
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

class GA():

    def __init__(self, clength, generation, np, mR, cR, dim, is_max, constrain = 0):
        self.start_time = time.time()
        self.end_time = self.start_time
        self.global_random_list_index = 1
        self.random_list_length = 2 ** 20
        self.random_list = []

        self.max_generation = generation
        self.statistics = []

        self.dim = dim

        self.degree_constraint = constrain
        self.code_length = clength
        self.edge_num = clength + 1
        self.node_num = clength + 2

        self.NP = np
        self.mutation_rate = mR
        self.crossover_rate = cR
        self.mutation_number = max(1, int(self.NP * self.mutation_rate))
        self.crossover_pair_number = int(self.NP * self.crossover_rate * 0.5)
        self.staying_number = self.NP - self.mutation_number - self.crossover_pair_number * 2
        self.is_max = bool(is_max)

        self.chromosome_father = [[[]for i in range(self.NP)]for j in range(dim)]
        self.chromosome_son = [[[]for i in range(self.NP)]for j in range(dim)]
        self.solution = [[[]for i in range(self.NP)]for j in range(dim)]
        self.fitness = [[] for i in range(self.NP) ]
        self.PP = [[]for i in range(self.NP)]
        self.result = [[]for j in range(self.dim)]
        self.max = 1e5
        self.min = -1e5
        self.sum = 0
        self.Weight = [ [0,  224, 224, 361, 671, 300, 539, 800, 943],
                        [224, 0,  200, 200, 447, 283, 400, 728, 762],
                        [224, 200, 0,   400, 566, 447, 600, 922, 949],
                        [361, 200, 400, 0,  400, 200, 200, 539, 583],
                        [671, 447, 566, 400, 0,  600, 447, 781, 510],
                        [300, 283, 447, 200, 600, 0,   283, 500, 707],
                        [539, 400, 600, 200, 447, 283, 0,   361, 424],
                        [800, 728, 922, 539, 781, 500, 361, 0,   500],
                        [943, 762, 949, 583, 510, 707, 424, 500,    0]]

        self.GA_init()

    def GA_init(self):
        self.random_list_update()
        for j in range(self.dim):
            for i in range(self.NP):
                a_code = self.get_code()
                self.repair(a_code)
                self.chromosome_father[j][i] = a_code
                self.chromosome_son[j][i] = a_code
                self.fitness[i] = 0
                self.PP[i] = 0

    def fitness_function(self, coordinate):
        w = 0
        for ele in coordinate[0]:
            w += self.Weight[ele[0]-1][ele[1]-1]
        return 100000/w

    def random_list_update(self):
        self.random_list = r.LCG(self.random_list_length, int(time.time())%(2**31))

    def U(self):
        if self.global_random_list_index % (self.random_list_length-1) == 0:
            self.random_list_update()
            self.global_random_list_index = 0

        self.global_random_list_index += 1
        return self.random_list[self.global_random_list_index]

    def U_CodeBit(self): #[1, node_num] integer
        a = self.U()
        res = int(a * self.node_num) +1
        if res > self.node_num:
            res = self.node_num
        return res

    def U_1_nth(self, nth): #[1, n], integer
        a = self.U()
        res = int(a * nth) + 1
        if res > nth:
            res = nth
        return res

    def U_except(self, num): #[1, node_num] except num, integer
        res = self.U_CodeBit()
        if res != num:
            return res
        else:
            return self.U_except(num)

    def U_NP(self): #[0,NP), integer
        a = self.U()
        integer_part = int (a * self.NP)
        fraction_part =int( (a * self.NP - integer_part) >= 0.5 )
        res = integer_part + fraction_part
        if res >= self.NP:
            res = self.NP - 1
        return res

    def U_code(self): #[0, code_length), integer
        a = self.U()
        integer_part = int(a * self.code_length)
        fraction_part = int((a * self.code_length - integer_part) >= 0.5)
        res = integer_part + fraction_part
        if res >= self.code_length:
            res = self.code_length - 1
        return res

    def get_code(self):
        res = []
        for i in range(self.code_length):
            a_num = self.U_CodeBit()
            res.append(a_num)
        return res


    def code2solution(self, code, j):
        P_nor = []
        P = [0 for i in range(self.node_num+1)]
        ans = []
        for i in range(self.node_num):
            if (i+1) not in code:
                P_nor.append(i+1)
        for i in range(self.code_length):
            P[code[i]] += 1


        index = 0
        for i in range(self.code_length):
            ans.append((P_nor[index], code[i]))
            index += 1
            P[code[i]] -= 1
            if P[code[i]] == 0:
                l = len(P_nor)
                for k in range(index, l):
                    if code[i] < P_nor[k]:
                        P_nor.insert( k, code[i])
                        break
                if l == len(P_nor):
                    P_nor.append(code[i])

        ans.append((P_nor[index],P_nor[index+1]))

        return ans





    def gather_roulette_wheel(self):
        for i in range(self.NP):
            self.PP[i] = self.fitness[i]

        for i in range(1,self.NP):
            self.PP[i] += self.PP[i-1]

        for i in range(self.NP):
            self.PP[i] /= self.PP[self.NP-1]


    def repair(self, target):
        if self.degree_constraint == 0:
            return
        box = [0 for i in range(self.node_num)]
        for i in range(self.code_length):
            box[target[i] -1] += 1

        change_flag = 0

        for i in range(self.node_num):
            if box[i] >= self.degree_constraint:
                changeto = self.change(target, i+1, box[i])
                box[changeto-1] += 1
                box[i] -= 1
                change_flag = 1

        if change_flag == 0:
            return

        return self.repair(target)

    def change(self, targetlist, repairNum, max_pos):
        change_pos = self.U_1_nth(max_pos)
        changeto = self.U_except(repairNum)
        index = 0
        for i in range(self.code_length):
            if targetlist[i] == repairNum:
                index += 1
            if index == change_pos:
                targetlist[i] = changeto
        return changeto


    def selection_operator(self):
        choose_index = self.U()
        res = []
        for i in range(self.NP):
            if self.PP[i] >= choose_index:
                for j in range(self.dim):
                    res.append(self.chromosome_father[j][i].copy())
                return res

        for j in range(self.dim):
            res.append(self.chromosome_father[j][self.NP-1].copy())
        return res


    def crossover_operator(self, code1, code2):
        index = [[]for j in range(self.dim)]
        res = [[]for j in range(self.dim)]
        for j in range(self.dim):
            index[j] = self.U_code()
            res[j].append(code1[j].copy())
            res[j].append(code2[j].copy())
            for i in range(0, index[j]):
                res[j][0][i] = code2[j][i]
                res[j][1][i] = code1[j][i]
        return res

    def mutation_operator(self, code):
        res = code.copy()
        which_bit = [[] for j in range(self.dim)]
        for j in range(self.dim):
            which_bit[j]= self.U_code()
            res[j][which_bit[j]] = self.U_CodeBit()
        return res


    def deep_copy(self, list_dest, list_template):
        for j in range(self.dim):
            for i in range(self.NP):
                list_dest[j][i] = list_template[j][i]
        return 1

    def calculate_fitness(self):
        coordinate = [[]for j in range(self.dim)]
        for i in range(self.NP):
            for j in range(self.dim):
                coordinate[j] = self.code2solution(self.chromosome_father[j][i], j)
                self.solution[j][i] = coordinate[j]


            self.fitness[i] = self.fitness_function(coordinate)

        self.max = max(self.fitness)
        self.min = min(self.fitness)
        self.sum = sum(self.fitness)


    def get_new_generation(self):
        self.gather_roulette_wheel()

        for i in range(self.staying_number):
            tmp = self.selection_operator()
            for j in range(self.dim):
                self.chromosome_son[j][i] = tmp[j].copy()

        left = self.staying_number
        right = self.staying_number + self.mutation_number

        for i in range(left, right):
            tmp = self.mutation_operator(self.selection_operator())
            for j in range(self.dim):
                self.chromosome_son[j][i] = tmp[j].copy()

        left = self.staying_number + self.mutation_number

        for i in range(left, self.NP, 2):
            chromosome = self.crossover_operator(self.selection_operator(),self.selection_operator())
            for j in range(self.dim):
                self.chromosome_son[j][i] = chromosome[j][0]
                self.chromosome_son[j][i+1] = chromosome[j][1]
        for i in range(self.NP):
            for j in range(self.dim):
                self.repair(self.chromosome_son[j][i])
        self.deep_copy(self.chromosome_father, self.chromosome_son)


    def update_statistic(self):
        res = []
        for j in range(self.dim):
            res.append(self.solution[j].copy())
        res.append(self.max)
        res.append(self.min)
        res.append(self.sum)
        self.statistics.append(res)

    def progress_bar(self, i):
        if self.max_generation >= 100:
            index = int(self.max_generation/100)
            if i%index == 0:
                print('-', end='')
        else:
            index = int(100/self.max_generation)
            for j in range(index):
                print('-', end='')

    def GA_main(self):
        print("start simulation: ", end='')
        for i in range(self.max_generation):
            self.progress_bar(i)  # this is progress bar
            self.calculate_fitness()
            self.get_new_generation()
            self.update_statistic()

        print(">!!")
        for i in range(self.NP):
            if self.is_max == 1:
                if self.fitness[i] == self.max:
                    for j in range(self.dim):
                        self.result[j] = self.solution[j][i]
                    break
            else:
                if self.fitness[i] == self.max:
                    for j in range(self.dim):
                        self.result[j] = self.solution[j][i]
                    break

        w = 0
        for ele in self.result[0]:
            w += self.Weight[ele[0] - 1][ele[1] - 1]

        print("result: f(",end='')
        print(self.result, ") = ",w )
        self.end_time = time.time()
        print("run time: ", self.end_time-self.start_time,"s")

    def print_Graph(self):
        print("draw Graph: ")
        print("ref: https://csacademy.com/app/graph_editor/")
        for i in range(self.node_num):
            print(i+1)
        for i in range(self.edge_num):
            node1 = self.result[0][i][0]
            node2 = self.result[0][i][1]
            print(node1, node2, self.Weight[node1-1][node2-1])


## parameters describe:
# gene code length: 7
# max generation: 100
# NP: 500
# mutation rate: 0.01
# crossover rate: 0.3
# dimension: 1 that is:(x)
# is maximize optimization problem? 1 (True)
# constraints: max_degree: 3
#
# GA utility:


question1 = GA( 7, 100, 1000 , 0.05, 0.4, 1, 1, 3)
question1.GA_main()
question1.print_Graph()


