import my_random as r
import math
import time


class GA():

    def __init__(self, clength, np, mR, cR, dim, is_max, generation = 0):
        self.start_time = time.time()
        self.end_time = self.start_time
        self.calu_start = self.start_time
        self.calu_end = self.start_time
        self.cross_start = self.start_time
        self.cross_end = self.start_time
        self.global_random_list_index = 1
        self.random_list_length = 2 ** 20
        self.random_list = []

        self.max_generation = generation
        self.statistics = []

        self.dim = dim

        self.code_length = clength
        self.edge_num = clength
        self.node_num = clength

        self.NP = np
        self.mutation_rate = mR
        self.crossover_rate = cR
        self.mutation_number = max(0, int(self.NP * self.mutation_rate))
        self.crossover_pair_number = int(self.NP * self.crossover_rate )
        self.staying_number = self.NP - self.mutation_number - self.crossover_pair_number
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
        self.sample_not = 1
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
        self.Weight = [[[] for i in range(self.code_length)] for j in range(self.code_length)]
        self.GA_init()

    def dist(self, i, j):
        return math.sqrt((self.city[i][1]-self.city[j][1])**2 + (self.city[i][2]-self.city[j][2])**2)

    def GA_init(self):
        self.random_list_update()
        for j in range(self.dim):
            for i in range(self.NP):
                a_code = self.get_code()
                self.chromosome_father[j][i] = a_code
                self.chromosome_son[j][i] = a_code
                self.fitness[i] = 0
                self.PP[i] = 0

        for i in range(self.code_length):
             for j in range(self.code_length):
                     self.Weight[i][j] = self.dist(i, j)


    def fitness_function(self, coordinate):
        w = 0
        for ele in coordinate[0]:
            w += self.Weight[ele[0]-1][ele[1]-1]
        return 1000/(w-400)

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

    def U_except(self, num): #[1, node_num] except num, integer
        res = self.U_1_nth(self.node_num)
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
            a_num = self.U_CodeBit(i)
            res.append(a_num)
        ans = self.order2code(res)
        return ans


    def code2solution(self, code, j):
        edge = []
        for i in range(self.node_num):
            edge.append((i+1, code[i]))
        return edge

    def order2code(self, code):
        P = [0 for i in range(self.node_num)]
        ans = []
        result = [[]for i in range(self.node_num)]
        for i in range(self.node_num):
            index = 0
            for j in range(self.node_num):
                if P[j] == 0: #active
                    index += 1
                if index == code[i]:
                    P[j] = 1 #inactive
                    ans.append(j + 1)
                    break

        for i in range(self.node_num-1):
            result[ans[i]-1] = ans[i + 1]
        result[ans[self.node_num-1]-1] = ans[0]
        return result

    def path2code(self, ans):
        result = [[]for i in range(self.node_num)]
        for i in range(self.node_num-1):
            result[ans[i]-1] = ans[i + 1]
        result[ans[self.node_num-1]-1] = ans[0]
        return result

    def gather_roulette_wheel(self):
        for i in range(self.NP):
            self.PP[i] = self.fitness[i]

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
        res = [[[]for i in range(self.node_num)]for j in range(self.dim)]
        for j in range(self.dim):
            bucket = [0 for i in range(self.node_num)]
            path = [[] for i in range(self.node_num)]
            start = self.U_1_nth(self.node_num)
            path[0] = start
            bucket[start-1] = 1
            for i in range(1, self.node_num):
                if self.Weight[code1[j][start-1]-1][start-1] > self.Weight[code2[j][start-1]-1][start-1]:
                    if bucket[code2[j][start-1]-1] == 0:
                        path[i] = code2[j][start-1]
                        bucket[path[i]-1] = 1
                    else:
                        path[i] = self.bucket_choose(bucket)
                        bucket[path[i]-1] = 1
                else:
                    if bucket[code1[j][start-1]-1] == 0:
                        path[i] = code1[j][start-1]
                        bucket[path[i]-1] = 1
                    else:
                        path[i] = self.bucket_choose(bucket)
                        bucket[path[i] - 1] = 1
                start = path[i]
            res[j] = self.path2code(path)
        return res

    def bucket_choose(self,bucket):
        start = self.U_code()
        while bucket[start] == 1:
            start += 1
            start = start % self.node_num
        return start + 1

    def mutation_operator(self, code):
        res = code.copy()
        which_bit1 = [[] for j in range(self.dim)]
        which_bit2 = [[] for j in range(self.dim)]
        for j in range(self.dim):
            which_bit1[j] = self.U_1_nth(self.node_num)
            which_bit2[j] = self.U_except(which_bit1[j])
            which_bit1[j] -= 1
            which_bit2[j] -= 1
            while which_bit1[j]+1 == res[j][which_bit2[j]] or which_bit2[j]+1 == res[j][which_bit1[j]]:
                which_bit1[j] = self.U_1_nth(self.node_num)
                which_bit2[j] = self.U_except(which_bit1[j])
                which_bit1[j] -= 1
                which_bit2[j] -= 1
            res[j][which_bit1[j]],res[j][which_bit2[j]] = res[j][which_bit2[j]],res[j][which_bit1[j]]

        return res


    def deep_copy(self, list_dest, list_template):
        for j in range(self.dim):
            for i in range(self.NP):
                list_dest[j][i] = list_template[j][i]
        return 1

    def calculate_fitness(self):
        self.calu_start = time.time()
        coordinate = [[]for j in range(self.dim)]
        for i in range(self.NP):
            for j in range(self.dim):
                coordinate[j] = self.code2solution(self.chromosome_father[j][i], j)
                self.solution[j][i] = coordinate[j]

            self.fitness[i] = self.fitness_function(coordinate)

        self.calu_end = time.time()

        self.max = max(self.fitness)
        self.min = min(self.fitness)
        self.sum = sum(self.fitness)
        self.sample_not = self.sample()


    def sample(self):
        num = self.NP * 1
        index = 0
        for i in range(self.NP):
            if self.fitness[i] == self.max:
                index += 1
        return int(index < num)

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

        self.cross_start = time.time()
        for i in range(left, self.NP):
            chromosome = self.crossover_operator(self.selection_operator(),self.selection_operator())
            for j in range(self.dim):
                self.chromosome_son[j][i] = chromosome[j].copy()

        self.cross_end = time.time()
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
        if self.max_generation != 0:
            for i in range(self.max_generation):
                self.progress_bar(i)  # this is progress bar
                self.calculate_fitness()
                self.get_new_generation()
                self.update_statistic()
        else:
            index = 0
            last = 0
            now = 1e5
            while abs(last - now) > 1e-4 or self.sample_not:
                index += 1
                #print("")
                #print("generation",index,": gap = ", self.max - self.sum/self.NP)
                self.calculate_fitness()
                self.get_new_generation()
                self.update_statistic()
                last = now
                now = self.max

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
        print("cross time", self.cross_end - self.cross_start, "s")
        print("calu time", self.calu_end - self.calu_start, "s")

    def print_Graph(self):
        print("draw Graph: ")
        for i in range(self.node_num):
            print(i+1)
        for i in range(self.edge_num):
            node1 = self.result[0][i][0]
            node2 = self.result[0][i][1]
            print(node1, node2, self.Weight[node1-1][node2-1])


# parameters describe:
# gene code length: 30
# max generation: 0 (not use max generation)
# NP: 1000
# mutation rate: 0.0
# crossover rate: 0.3
# dimension: 1 that is:(x)
# is maximize optimization problem? 1 (True)
#
# GA utility:


question1 = GA(30, 1000, 0, 0.3, 1, 1)
question1.GA_main()
question1.print_Graph()

# result:

