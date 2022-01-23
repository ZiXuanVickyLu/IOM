import my_random as r
import math
import time
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

class GA():
    def __init__(self, clength, generation, np, mR, cR, dim, is_max, solution_range, is_generate_mp4 = 0):
        self.global_random_list_index = 1
        self.random_list_length = 2 ** 20
        self.random_list = []
        self.file_path = '/Users/birdpeople/classObject/jpg1/'
        self.generate_mp4 = is_generate_mp4

        self.max_generation = generation
        self.statistics = []

        self.dim = dim

        self.code_length = clength
        self.NP = np
        self.mutation_rate = mR
        self.crossover_rate = cR
        self.mutation_number = max(1, int(self.NP * self.mutation_rate))
        self.crossover_pair_number = int(self.NP * self.crossover_rate * 0.5)
        self.staying_number = self.NP - self.mutation_number - self.crossover_pair_number * 2
        self.is_max = bool(is_max)

        self.chromosome_father = [[[]for i in range(self.NP)]for j in range(dim)]
        self.chromosome_son = [[[]for i in range(self.NP)]for j in range(dim)]
        self.chromosome_buffer = [[[]for i in range(self.NP)]for j in range(dim)]
        self.solution = [[[]for i in range(self.NP)]for j in range(dim)]
        self.fitness = [[] for i in range(self.NP) ]
        self.PP = [[]for i in range(self.NP)]
        self.result = [[]for j in range(self.dim)]
        self.max = 1e5
        self.min = -1e5
        self.sum = 0
        self.solution_range = solution_range
        self.GA_init()

    def GA_init(self):
        self.random_list_update()
        for j in range(self.dim):
            for i in range(self.NP):
                a_code = self.get_code()
                self.chromosome_father[j][i] = a_code
                self.chromosome_buffer[j][i] = a_code
                self.chromosome_son[j][i] = a_code
                self.fitness[i] = 0
                self.PP[i] = 0

    def fitness_function(self, coordinate):
        x = coordinate[0]
        y = coordinate[1]
        return math.e - 20*math.exp(-0.2*math.sqrt((x**2+y**2)/2))-\
               math.exp(0.5*(math.cos(2*math.pi*x)+math.cos(2*math.pi*y)))

    # def fitness_function(self,coordinate):
    #     x = coordinate[0]
    #     return x**3 - 60 * x**2 + 900 * x +100

    def random_list_update(self):
        self.random_list = r.LCG(self.random_list_length, int(time.time())%(2**31))

    def U(self):
        if self.global_random_list_index % (self.random_list_length-1) == 0:
            self.random_list_update()
            self.global_random_list_index = 0

        self.global_random_list_index += 1
        return self.random_list[self.global_random_list_index]

    def U0_1(self):
        return int(self.U() > 0.5)

    def U_NP(self):
        a = self.U()
        integer_part = int (a * self.NP)
        fraction_part =int( (a * self.NP - integer_part) >= 0.5 )
        res = integer_part + fraction_part
        if res >= self.NP:
            res = self.NP - 1
        return res

    def U_code(self):
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
            a_bit = self.U0_1()
            if a_bit == 0:
                res.append(0)
            else:
                res.append(1)
        return res


    def code2solution(self, code, j):
        ans = 0
        length = self.solution_range[j][1] - self.solution_range[j][0]
        for i in range(self.code_length):
            if code[i] == 1:
                ans += 2**i
        return length/(2**self.code_length) * ans + self.solution_range[j][0]

    def gather_roulette_wheel(self):
        for i in range(self.NP):
            self.PP[i] = self.fitness[i]
        if self.is_max == 1:
            for i in range(self.NP):
                self.PP[i] -= self.min
        else:
            for i in range(self.NP):
                self.PP[i] *= -1
                self.PP[i] += self.max

        for i in range(1,self.NP):
            self.PP[i] += self.PP[i-1]

        for i in range(self.NP):
            self.PP[i] /= self.PP[self.NP-1]


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
            if code[j][which_bit[j]] == 0:
                res[j][which_bit[j]] = 1
            else:
                res[j][which_bit[j]] = 0
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
            if self.generate_mp4 == 1:
                self.save_fig3D(i)

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

        print("result: f(",end='')
        print(self.result, ") = ",end='')
        if self.is_max == 1:
            print(self.max)
        else:
            print(self.min)

    def print_variance(self):
        x = []
        y = []

        for i in range(self.max_generation):
            x.append(i+1)
            if self.is_max == 1:
                y.append(self.statistics[i][self.dim])
            else:
                y.append(self.statistics[i][self.dim+1])

        plt.figure("fitness")
        plt.title("fitness")
        plt.scatter(x, y, s = 1)
        name = self.file_path + 'fitness.jpg'
        plt.savefig(name)
        plt.show()

    def print_even(self):
        x = []
        y = []

        for i in range(self.max_generation):
            x.append(i+1)

            y.append(self.statistics[i][self.dim+2]/self.NP)

        plt.figure("even-fitness")
        plt.title("even-fitness")
        plt.scatter(x, y, s = 1)
        name = self.file_path + 'even-fitness.jpg'
        plt.savefig(name)
        plt.show()


    def save_fig3D(self, i):
        n = 1000
        x, y = np.meshgrid(np.linspace(self.solution_range[0][0],self.solution_range[0][1]),
                           np.linspace(self.solution_range[1][0],self.solution_range[1][1]))
        z = np.e - 20*np.exp(-0.2*np.sqrt((x**2+y**2)/2))-\
               np.exp(0.5*(np.cos(2*np.pi*x)+np.cos(2*np.pi*y)))

        fig = plt.figure("Surface")
        plt.title("Surface")
        ax3d = Axes3D(fig)

        ax3d.plot_surface(x,y,z,cmap='jet',alpha=0.2)
        ax3d.scatter(self.statistics[i][0],
                     self.statistics[i][1], self.fitness,color='r')
        name = self.file_path + 'fig'+str(i) + '.jpg'
        plt.savefig(name)
        plt.close(fig)

## parameters describe:
# gene code length: 10
# max generation: 100
# NP: 100
# mutation rate: 0.01
# crossover rate: 0.3
# dimension: 2 that is:(x, y)
# is maximize optimization problem? 0 (false)
# solution space range: [[-5, 5],[5, 5]]: x in (-5,5); y in (-5, 5)
# need video, that is a sequence of jpgs? yes!

# question1 = GA( 10, 100, 100, 0.01, 0.3, 2, 0, [[-5,5],[-5,5]])
# question1.GA_main()
#
# # GA utility:
# question1.print_variance()
# question1.print_even()

question1 = GA( 5, 100, 100, 0.01, 0.3, 1, 1, [[0,30]])
question1.GA_main()

# GA utility:
question1.print_variance()
question1.print_even()

