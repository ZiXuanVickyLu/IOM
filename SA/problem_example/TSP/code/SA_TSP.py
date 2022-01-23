import my_random as r
import math
import time
import matplotlib.pyplot as plt

class SA():

    def __init__(self, clength, inner_step, outer_step, inner_stop, outer_stop, T0, TMultiplier):
        self.global_random_list_index = 1
        self.random_list_length = 2 ** 20
        self.random_list = []
        self.start_time = time.time()
        self.end_time = self.start_time
        self.file_path = '/Users/birdpeople/classObject/'

        self.statistics = []
        self.node_num = clength
        self.code = []
        self.fitness = 0
        self.result = []
        self.max = 1e5
        self.history_min = 1e5
        self.history_min_code = []
        self.inner_step = inner_step
        self.outer_step = outer_step
        self.inner_stop_condition = inner_stop
        self.outer_stop_condition = outer_stop
        self.neighbors_score = [[]for i in range(self.node_num)]
        self.city =  \
                    [[1,    41, 94],
                     [2,    37, 84],
                     [3,    54, 67],
                     [4,    25, 62],
                     [5,    7,  64],
                     [6,    2,  99],
                     [7,    68, 58],
                     [8,    71, 44],
                     [9,    54, 62],
                     [10,   83, 69],
                     [11,   64, 60],
                     [12,   18, 54],
                     [13,   22, 60],
                     [14,   83, 46],
                     [15,   91, 38],
                     [16,   25, 38],
                     [17,   24, 42],
                     [18,   58, 69],
                     [19,   71, 71],
                     [20,   74, 78],
                     [21,   87, 76],
                     [22,   18, 40],
                     [23,   13, 40],
                     [24,   82, 7 ],
                     [25,   62, 32],
                     [26,   58, 35],
                     [27,   45, 21],
                     [28,   41, 26],
                     [29,   44, 35],
                     [30,   4,  50]]
        self.Weight = [[[] for i in range(self.node_num)] for j in range(self.node_num)]
        self.T = T0
        self.Temperature_Multipler = TMultiplier
        self.SA_init()

    def dist(self, i, j):
        return math.sqrt((self.city[i][1]-self.city[j][1])**2 + (self.city[i][2]-self.city[j][2])**2)

    def SA_init(self):
        self.random_list_update()
        a_code = self.get_code()
        self.code = a_code

        for i in range(self.node_num):
             for j in range(self.node_num):
                     self.Weight[i][j] = self.dist(i, j)

        edge = self.code2edge(self.code)
        self.history_min = self.fitness_function(edge)
        self.fitness = self.history_min
        self.history_min_code = a_code



    def fitness_function(self, edge_set):#[(i, j), (a, b),...]
        w = 0
        for ele in edge_set:
            w += self.Weight[ele[0]-1][ele[1]-1]
        return w

    def random_list_update(self):
        self.random_list = r.LCG(self.random_list_length, int(time.time())%(2**31))

    def U(self):
        if self.global_random_list_index % (self.random_list_length-1) == 0:
            self.random_list_update()
            self.global_random_list_index = 0

        self.global_random_list_index += 1
        return self.random_list[self.global_random_list_index]

    def U_CodeBit(self, codebit_pos): #[1, node_num - codebit_pos] integer
        a = self.U()
        i = self.node_num - codebit_pos
        res = int(a * i) +1
        if res > i:
            res = i
        return res

    def U_1_nth(self, nth): #[1, n], integer
        a = self.U()
        res = int(a * nth) + 1
        if res > nth:
            res = nth
        return res


    def get_code(self):
        res = []
        for i in range(self.node_num):
            a_num = self.U_CodeBit(i)
            res.append(a_num)
        ans = self.order2path(res)
        return ans


    def code2edge(self, code):
        edge = []
        for i in range(self.node_num-1):
            edge.append((code[i], code[i+1]))
        edge.append((code[self.node_num-1], code[0]))
        return edge

    def order2path(self, code):
        P = [0 for i in range(self.node_num)]
        ans = []
        for i in range(self.node_num):
            index = 0
            for j in range(self.node_num):
                if P[j] == 0: #active
                    index += 1
                if index == code[i]:
                    P[j] = 1 #inactiv
                    ans.append(j + 1)
                    break
        return ans

    def W(self, i,j):
        return self.Weight[i-1][j-1]


    def cross_score_change(self, pos1, pos2):
        pos1_ = self.code[pos1]
        from1_ = self.code[(pos1-1)%(self.node_num)]
        to1_ = self.code[(pos1+1)%(self.node_num)]

        pos2_ = self.code[pos2]
        from2_ = self.code[(pos2 - 1) % (self.node_num)]
        to2_ = self.code[(pos2 + 1) % (self.node_num)]

        if to2_ == pos1_:
            res = -self.W(pos1_, to1_) - self.W(pos2_, from2_)\
                 + self.W(pos2_, to1_) + self.W(pos1_, from2_)
            return res
        if to1_ == pos2_:
            res = -self.W(pos1_,from1_ ) - self.W(pos2_, to2_)\
                + self.W(pos2_,from1_) + self.W(pos1_, to2_)
            return res
        else:
            res = - self.W(pos1_,from1_) - self.W(pos1_, to1_)\
              - self.W(pos2_,from2_) - self.W(pos2_, to2_)\
              + self.W(pos1_,from2_) + self.W(pos1_, to2_)\
              + self.W(pos2_,from1_) + self.W(pos2_, to1_)
        return res

    def accept(self, gap):
        return self.U() <= math.exp(-gap/self.T)

    def get_one_neighbor_or_self(self):
        pos1_ = self.U_1_nth(self.node_num)
        pos2_ = self.U_1_nth(self.node_num)
        if pos1_ == pos2_:
            return (self.code.copy(), 0)
        pos1 = max(pos1_, pos2_) - 1
        pos2 = min(pos1_, pos2_) - 1

        gap = self.cross_score_change(pos1, pos2)
        gap_ = 0
        code_copy = self.code.copy()
        if self.accept(gap):
            gap_ = gap
            tmp = code_copy[pos1]
            code_copy[pos1] = code_copy[pos2]
            code_copy[pos2] = tmp

        return (code_copy, gap_)


    def inner_cyc(self):
        old_code = self.code.copy()
        if self.inner_stop_condition == 0:# use specific step stop condition
            for i in range(self.inner_step):
                code_gap = self.get_one_neighbor_or_self()
                self.code = code_gap[0]
                self.fitness += code_gap[1]
        else:
            index = 0
            for i in range(self.inner_step):
                code_gap = self.get_one_neighbor_or_self()
                print(code_gap)
                if self.code == code_gap[0]:
                    index += 1
                else:
                    self.code = code_gap[0]
                    self.fitness += code_gap[1]
                    index = 0

                if index == self.inner_stop_condition:
                    break

        if self.history_min > self.fitness:
            self.history_min = self.fitness
            self.history_min_code = self.code

        if old_code == self.code:
            return 1
        return 0

    def update_statistic(self):
        res = []
        res.append(self.code)
        res.append(self.fitness)
        res.append(self.history_min)
        res.append(self.history_min_code)
        res.append(self.T)
        self.statistics.append(res)


    def progress_bar(self, i):
        if self.outer_step >= 100:
            index = int(self.outer_step/100)
            if i%index == 0:
                print('-', end='')
        else:
            index = int(100/self.outer_step)
            for j in range(index):
                print('-', end='')

    def SA_main(self):
        print("start simulation: ", end='')
        if self.outer_stop_condition == 0:
            for i in range(self.outer_step):
                self.progress_bar(i)  # this is progress bar
                self.inner_cyc()
                self.update_statistic()
                self.T *= self.Temperature_Multipler
        else:
            index = 0
            for i in range(self.outer_step):
                self.progress_bar(i)  # this is progress bar
                index += self.inner_cyc()
                self.update_statistic()
                if index == self.outer_stop_condition:
                    break
                self.T *= self.Temperature_Multipler

        print(">!!")

        w = self.history_min
        print("result: f(",end='')
        print(self.code2edge(self.history_min_code), ") = ",w )
        self.end_time = time.time()
        print("run time: ", self.end_time-self.start_time,"s")

    def print_variance(self):
        x = []
        y = []

        for i in range(len(self.statistics)):
            x.append(i+1)
            y.append(self.statistics[i][1])

        plt.figure("path-length")
        plt.title("path-length:variance")
        plt.scatter(x, y, s = 1)
        name = self.file_path + 'variance.jpg'
        plt.savefig(name)
        plt.show()
        plt.close()

    def print_even(self):
        x = []
        y = []

        for i in range(len(self.statistics)):
            x.append(i+1)
            y.append(self.statistics[i][2])

        plt.figure("path-length-min")
        plt.title("path-length:history_min")
        plt.scatter(x, y, s = 1)
        name = self.file_path + 'history_min.jpg'
        plt.savefig(name)
        plt.show()
        plt.close()



# parameters describe:
# code length: 30
# SA max inner step: 100
# SA max outer step: 10000
# SA inner convergence condition: 0(do not use), [1, max_inner_step]
# SA outer convergence condition: 0(do not use), [1, max_outer_step]
# SA initial Temperature: T0
# SA Temperature Multiplier: T_k+1 = T_k * TMultiplier
#parameter list:
#clength, inner_step, outer_step, inner_stop, outer_stop, T0, TMultipiler

question1 = SA(30, 100, 10000, 0, 1000, 2000, 0.999)
question1.SA_main()
question1.print_even()
question1.print_variance()
#print(question1.statistics)


# result:

