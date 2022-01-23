import my_random as r
import math
import time
import matplotlib.pyplot as plt

class ACA():

    def __init__(self, clength, NC, m, max_content, rho, alpha, beta, Q):
        self.global_random_list_index = 1
        self.random_list_length = 2 ** 20
        self.random_list = []
        self.start_time = time.time()
        self.end_time = self.start_time
        self.file_path = '/Users/birdpeople/classObject/'

        self.m = m
        self.statistics = []
        self.node_num = clength
        self.max_content = max_content #max package content
        self.tabu = [[]for i in range(self.m)]
        self.tau = [[1 for i in range(self.m)]for j in range(self.m)]
        self.eta = [[[] for i in range(self.m)] for j in range(self.m)]
        self.tau_m = [[0 for i in range(self.m)]for j in range(self.m)]
        self.close_pos = [[]for i in range(self.m)]
        self.fitness = 0
        self.fitness_code = []
        self.result = []
        self.rho = rho
        self.alpha = alpha
        self.beta = beta
        self.Q = Q

        self.NC = NC
        self.NC_index = 0
        self.history_max = 0
        self.history_max_code = []
        self.weight = [95, 4, 60, 32, 23, 72, 80, 62, 65, 46]
        self.value = [55, 10, 47, 5, 4, 50, 8, 61, 85, 87]

        self.ACA_init()

    def ACA_init(self):
        self.random_list_update()

        for i in range(self.node_num):
            for j in range(self.node_num):
                self.eta[i][j] = self.value[i] / self.weight[j]

        for i in range(self.m):
            self.tabu[i].append(self.U_CodeBit()) #first pos



    def total_weight(self, tabu):
        res = 0
        for ele in tabu:
            res += self.weight[ele]
        return res

    def total_value(self, tabu):
        res = 0
        for ele in tabu:
            res += self.value[ele]
        return res

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
        i = self.node_num
        res = int(a * i) +1
        if res > i:
            res = i
        res -= 1
        return res

    def U_1_nth(self, nth): #[1, n], integer
        a = self.U()
        res = int(a * nth) + 1
        if res > nth:
            res = nth
        return res

    def clear_and_init(self):
        self.fitness = 0
        self.fitness_code = []
        self.tau_m = [[0 for i in range(self.m)]for j in range(self.m)]
        self.tabu = [[] for i in range(self.m)]
        for i in range(self.m):
            self.tabu[i].append(self.close_pos[i])

    def update_tau(self):
        for i in range(self.node_num):
            for j in range(self.node_num):
                self.tau[i][j] *= self.rho
                self.tau[i][j] += self.tau_m[i][j]

    def can_choose(self,k):
        res = []
        w = self.total_weight(self.tabu[k])
        for i in range(self.node_num):
            if i not in self.tabu[k] and (w+self.weight[i])<=self.max_content:
                res.append(i)
        return res

    def calu(self, i, j):
        res = (self.tau[i][j]**self.alpha) * (self.eta[i][j]**self.beta)
        return res

    def movement(self,k):
        can = self.can_choose(k).copy()
        while len(can)!= 0:
            PP = 0
            Pi = []
            for ele in can:
                Pi.append(self.calu(self.tabu[k][-1], ele))
                PP += Pi[-1]
            for ele in Pi:
                ele /= PP
            for i in range(1, len(Pi)):
                Pi[i] += Pi[i-1]

            ref = self.U()
            res = len(Pi) - 1
            for i in range(len(Pi)):
                if Pi[i] >= ref :
                    res = i
                    break
            self.tabu[k].append(can[res])
            can = self.can_choose(k).copy()


        Lk = self.total_value(self.tabu[k])
        for i in range(len(self.tabu[k])-1):
            self.tau_m[self.tabu[k][i]][self.tabu[k][i+1]] += self.Q/Lk


    def one_NC(self):
        if self.NC_index != 0:
            self.clear_and_init()
        for k in range(self.m):
            self.movement(k)
            if self.fitness < self.total_value(self.tabu[k]):
                self.fitness_code = self.tabu[k].copy()
                self.fitness = self.total_value(self.tabu[k])

        self.update_tau()
        for i in range(self.m):
            self.close_pos[i] = self.tabu[i][-1]
        self.NC_index += 1


    def update_statistic(self):
        res = []
        res.append(self.tabu)
        res.append(self.fitness)
        res.append(self.fitness_code)
        res.append(self.history_max)
        res.append(self.history_max_code)

        self.statistics.append(res)


    def progress_bar(self, i):
        if self.NC >= 100:
            index = int(self.NC/100)
            if i%index == 0:
                print('-', end='')
        else:
            index = int(100/self.NC)
            for j in range(index):
                print('-', end='')

    def ACA_main(self):
        print("start simulation: ", end='')
        for i in range(self.NC):
            self.progress_bar(i)  # this is progress bar
            self.one_NC()
            if self.fitness >= self.history_max:
                self.history_max_code = self.fitness_code
                self.history_max = self.fitness
            self.update_statistic()

        print(">!!")

        w = self.history_max
        p = [0 for i in range(self.node_num)]
        for ele in self.history_max_code:
            p[ele] = 1
        print("result: f(",end='')
        print(p, ") = ",w )
        self.end_time = time.time()
        print("run time: ", self.end_time-self.start_time,"s")

    def print_variance(self):
        x = []
        y = []

        for i in range(len(self.statistics)):
            x.append(i+1)
            y.append(self.statistics[i][1])

        plt.figure("KP")
        plt.title("KP:variance")
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
            y.append(self.statistics[i][3])

        plt.figure("KP-max")
        plt.title("KP:history_max")
        plt.scatter(x, y, s = 1)
        name = self.file_path + 'history_max.jpg'
        plt.savefig(name)
        plt.show()
        plt.close()



# parameters describe:
# code length: 10
# ACA NC: 1, 10, 50, 100, 150
# ACA ant number: 50
# ACA max package weight: 269
# ACA rho: (1-forget rate): 0.5
# ACA alpha: 1
# ACA beta: 0
# ACA Q: 1

#clength, NC, m, max_content, rho, alpha, beta, Q:
question1 = ACA(10, 10, 50, 269, 0.5, 0.5, 0.5, 1)
question1.ACA_main()
question1.print_even()
question1.print_variance()
#print(question1.statistics)


# result:

