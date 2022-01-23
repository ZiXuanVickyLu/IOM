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
        self.file_path = './'

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
        self.name = [[]for i in range(self.node_num)]
        self.neighbors_score = [[]for i in range(self.node_num)]
        self.Weight = [[ 0 for i in range(self.node_num)] for j in range(self.node_num)]
        self.T = T0
        self.T0 = T0
        self.Temperature_Multipler = TMultiplier


    def set_name(self, i, name):
        self.name[i] = name

    def set_weight(self, i, j, w):
        self.Weight[i][j] = w

    def print_name_weight(self):
        print(self.name)
        print(self.Weight)

    def SA_init(self):
        self.random_list_update()
        self.code = [(i) for i in range(self.node_num)]
        self.history_min = self.fitness_function(self.code)
        self.fitness = self.fitness_function(self.code)
        self.history_min_code = self.code


    def fitness_function(self, code):
        w = 0
        for i in range(self.node_num):
            for j in range(self.node_num):
                w += int(code[i] > code[j]) * self.Weight[i][j]
        return w

    def random_list_update(self):
        self.random_list = r.LCG(self.random_list_length, int(time.time())%(2**31))

    def U(self):
        if self.global_random_list_index % (self.random_list_length-1) == 0:
            self.random_list_update()
            self.global_random_list_index = 0

        self.global_random_list_index += 1
        return self.random_list[self.global_random_list_index]


    def U_1_nth(self, nth): #[1, n], integer
        a = self.U()
        res = int(a * nth) + 1
        if res > nth:
            res = nth
        return res


    def punish(self, winner, loser, rank_list):
        return int(rank_list[winner] > rank_list[loser]) * self.Weight[winner][loser]

    def cross_score_change(self, pos1, pos2):
        res = 0
        test_code = self.code.copy()
        tmp = test_code[pos2]
        test_code[pos2] = test_code[pos1]
        test_code[pos1] = tmp

        for i in range(self.node_num):
            if i != pos1 and i != pos2:
                res += self.punish(pos1, i, test_code)
                res += self.punish(pos2, i, test_code)
                res += self.punish(i, pos1, test_code)
                res += self.punish(i, pos2, test_code)

                res -= self.punish(pos2, i, self.code)
                res -= self.punish(pos1, i, self.code)
                res -= self.punish(i, pos1, self.code)
                res -= self.punish(i, pos2, self.code)
        res += self.punish(pos1, pos2, test_code) + self.punish(pos2, pos1, test_code)
        res -= (self.punish(pos1, pos2, self.code) + self.punish(pos2, pos1, self.code))
        # debug:
        # print("is ==: ", res == self.fitness_function(test_code) - self.fitness_function(self.code))
        return res


    def accept(self, gap):
        return self.U() <= math.exp(-gap/self.T)


    def get_one_neighbor_or_self(self):
        pos1_ = self.U_1_nth(self.node_num)
        pos2_ = self.U_1_nth(self.node_num)

        if pos1_ == pos2_:
            return (self.code.copy(), 0)

        pos1 = pos1_ - 1
        pos2 = pos2_ - 1

        gap = self.cross_score_change(pos1, pos2)
        gap_ = 0
        code_copy = self.code.copy()
        if self.accept(gap):
            gap_ = gap
            tmp = code_copy[pos1]
            code_copy[pos1] = code_copy[pos2]
            code_copy[pos2] = tmp

        return (code_copy, gap_)


    def inner_cyc(self): # This is the inner cycle of anealing.
        old_fitness = self.fitness
        if self.inner_stop_condition == 0:# use specific step stop condition
            for i in range(self.inner_step):
                code_gap = self.get_one_neighbor_or_self()
                self.code = code_gap[0].copy()
                self.fitness += code_gap[1]
                # debug:
                # print("fitness:", self.fitness)
                # print("ground_truth:", self.fitness_function(self.code))
        else:
            index = 0
            for i in range(self.inner_step):
                code_gap = self.get_one_neighbor_or_self()
                if code_gap[1] == 0:
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

        if old_fitness == self.fitness:
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

    # This is the main outer cycle for dropping temperature and (the total simulation).
    def SA_main(self):
        print("Simulation start: ", end='')
        self.SA_init()
        step = self.outer_step
        if self.outer_stop_condition == 0:
            for i in range(self.outer_step):
                self.progress_bar(i)  # this is for progress bar
                self.inner_cyc()
                self.update_statistic()
                self.T *= self.Temperature_Multipler
        else:
            index = 0
            step = 0
            for i in range(self.outer_step):
                step += 1
                self.progress_bar(i)  # this is  for progress bar
                ind = self.inner_cyc()
                if ind:
                    index += ind
                else:
                    index = 0
                self.update_statistic()
                if index == self.outer_stop_condition:
                    break
                self.T *= self.Temperature_Multipler
        print(">!!")


        w = self.history_min
        print("result: ")
        for i in range(20):
            print("==", end='')
        print('')
        self.dump_result()
        for i in range(20):
            print("==",end='')
        print('')

        print("The Kemeny score of this best ranking is: ", w)
        self.end_time = time.time()
        print("run time: ", (self.end_time-self.start_time) * 1000, "ms")
        print("TI = ", self.T0, ", T now = ", self.T, ", alpha = ", self.Temperature_Multipler,\
              ", TL = ",self.inner_step ,", with outer step: ",step)

    def progress_bar(self, i):
        if self.outer_step >= 100:
            index = int(self.outer_step/100)
            if i%index == 0:
                print('-', end='',flush = True)
        else:
            index = int(100/self.outer_step)
            for j in range(index):
                print('-', end='', flush = True)


    # print the necessary figure set, helping debug :-)
    def dump_result(self):
        print("\trank\t\tparticipant's name")
        index = 1
        for i in range(20):
            print("--",end='')
        print('')
        rank_list = [[]for i in range(self.node_num)]
        for i in range(self.node_num):
            rank_list[self.history_min_code[i]] = self.name[i]

        for ele in rank_list:
            if index < 10:
                print("\t ",index, "\t|\t", ele)
            else:
                print("\t",index, "\t|\t", ele)
            index += 1


    # Variance result show the Kemeny score of each iteration,
    # as the SA allow a temporary solution optimality-drop to against local optimality.
    def print_variance(self):
        x = []
        y = []

        for i in range(len(self.statistics)):
            x.append(i+1)
            y.append(self.statistics[i][1])

        plt.figure("Kemeny score")
        plt.title("Kemeny score:variance")
        plt.scatter(x, y, s = 1)
        name = self.file_path + 'variance.jpg'
        plt.savefig(name)
        plt.show()
        plt.close()

    # Even show the record of the history best fitness, beacuse the temperature drop is not quite static (finite time step),
    # and the annealing is not quite slow (finite annealing step), then we have to 'record' the history optimal solution,
    # though it is theoretically proved that SA will converge to global optimal solution :-).

    def print_even(self):
        x = []
        y = []

        for i in range(len(self.statistics)):
            x.append(i+1)
            y.append(self.statistics[i][2])

        plt.figure("Kemeny score-min")
        plt.title("Kemeny score: history_min")
        plt.scatter(x, y, s = 1)
        name = self.file_path + 'history_min.jpg'
        plt.savefig(name)
        plt.show()
        plt.close()


