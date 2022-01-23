import my_random as r
import math
import time
import matplotlib.pyplot as plt

class PSO():

    def __init__(self, iteg, quanta, car, station, w, c1, c2):
        self.global_random_list_index = 1
        self.random_list_length = 2 ** 20
        self.random_list = []
        self.start_time = time.time()
        self.end_time = self.start_time
        self.file_path = './'

        self.car = car
        self.station = station
        self.statistics = []
        self.node_num = station
        self.iteg = iteg
        self.w = w
        self.c2 = c2
        self.c1 = c1
        self.quanta = quanta
        self.result = []
        self.NC_index = 0
        self.path = []

        self.vv = [[[]for j in range(self.station)]for i in range(quanta)]
        self.vr = [[[]for j in range(self.station)]for i in range(quanta)]
        self.xv = [[[]for j in range(self.station)]for i in range(quanta)]
        self.xr = [[[]for j in range(self.station)]for i in range(quanta)]
        self.piv = [[[]for j in range(self.station)]for i in range(quanta)]
        self.pir = [[[]for j in range(self.station)]for i in range(quanta)]
        self.optimizer = [1e8 for i in range(quanta)]
        self.even_optimizer = 1e7
        self.global_optimizer = 1e10
        self.pgv = []
        self.pgr = []


        self.position = \
            [
                [18, 54],
                [22, 60],
                [58, 69],
                [71, 71],
                [83, 46],
                [91, 38],
                [24, 42],
                [18, 40]
            ]
        self.gi = [0, 0.89, 0.14, 0.28, 0.33, 0.21, 0.41, 0.57]
        self.car_max = 1
        self.dis = [[[]for i in range(self.station+1)]for j in range(self.station + 1)]

        self.PSO_init()
    
    def PSO_init(self):
        self.random_list_update()
        for i in range(self.station + 1):
            for j in range(self.station + 1):
                self.dis[i][j] = self.dist(i,j)
        # update the Xv
        for i in range(self.quanta):
            for j in range(self.station):
                self.xv[i][j] = self.U_1_nth(self.car) #integer
                self.piv[i][j] = self.xv[i][j]
        # update the Xr
        for i in range(self.quanta):
            for j in range(self.station):
                self.xr[i][j] = self.U_usigned_R(self.station)
                self.pir[i][j] = self.xr[i][j]

        # update the Vv
        for i in range(self.quanta):
            for j in range(self.station):
                self.vv[i][j] = round(self.U_signed_R(self.car-1)) #integer

        #update the Vr
        for i in range(self.quanta):
            for j in range(self.station):
                self.vr[i][j] = self.U_signed_R(self.station-1)
    
    def dist(self,i ,j):
        return math.sqrt((self.position[i][0]-self.position[j][0])**2
                         + (self.position[i][1] - self.position[j][1])**2)
        

    def random_list_update(self):
        self.random_list = r.LCG(self.random_list_length, int(time.time())%(2**31))

    def U(self):
        if self.global_random_list_index % (self.random_list_length-1) == 0:
            self.random_list_update()
            self.global_random_list_index = 0

        self.global_random_list_index += 1
        return self.random_list[self.global_random_list_index]

    def U_usigned_R(self, K): #[1,K] num
        a = self.U()
        i = a * (K-1)
        i += 1
        return i

    def U_signed_R(self,K): #[-K,K] num
        a = self.U_usigned_R(K)
        if self.U() > 0.5:
            a *= -1
        return a


    def U_1_nth(self, nth): #[1, n], integer
        a = self.U()
        res = int(a * nth) + 1
        if res > nth:
            res = nth
        return res


    def verifiy_xv(self, one_xv):
        for i in range(self.station):
            one_xv[i] = round(one_xv[i])
            if one_xv[i] > self.car:
                one_xv[i] = 1+self.U_1_nth(self.car-1)
            if one_xv[i] < 1:
                one_xv[i] = self.car - self.U_1_nth(self.car-1)

    def pos(self, li, ele):
        for i in range(len(li)):
            if ele == li[i]:
                return i+1
        return 1e5

    def verifiy_xr(self, one_xv, one_xr):
        car_task = [[]for i in range(self.car)]
        car_num = [[]for i in range(self.car)]
        car_rank = [[]for i in range(self.car)]
        car_order = [[] for i in range(self.car)]
        car_path = [[]for i in range(self.car)]
        for i in range(self.station):
            car_task[one_xv[i]-1].append(one_xr[i])
            car_num[one_xv[i]-1].append(i+1)

        for i in range(self.car):
            car_path[i] = [0 for i in range(len(car_task[i])+1)]
            car_rank[i] = sorted(car_task[i])
        for i in range(self.car):
            for j in range(len(car_task[i])):
                car_order[i].append(self.pos(car_task[i], car_rank[i][j]))

        for i in range(self.car):
            for j in range(len(car_task[i])):
                car_path[i][car_order[i][j]] = car_num[i][j]
            car_path[i].append(0)
        #print(car_task)
        #print(car_num)
        #print(car_rank)
        #print(car_order)
        #print(car_path)
        return car_path

    def eval(self, car_path):
        res = 0
        for i in range(self.car):
            weight = 0
            res_in = 0
            for j in range(len(car_path[i])-1):
                weight += self.gi[car_path[i][j]]
                res_in += self.dis[car_path[i][j]][car_path[i][j+1]]
                res += self.dis[car_path[i][j]][car_path[i][j+1]]

            if weight >= self.car_max:
                res += (math.ceil(weight)-1) * res_in

        return res

    def test(self,car_path):
        print( self.eval(car_path))

    def listAdd(self,v,pi,pg,x):
        res = []
        for i in range(len(list1)):
            res.append( self.w*v[i] + self.c1*0.5*(1-self.w)*(pi[i]-x[i]) + self.c2*0.5*(1-self.w)*(pg[i]-x[i]) )
        return res

    def update_v(self):
        for i in range(self.quanta):
            self.vr[i] = self.listAdd(self.vr[i], self.pir[i],self.pgr,self.xr[i])
            self.vv[i] = self.listAdd(self.vv[i], self.piv[i],self.pgv,self.xv[i])
            for j in range(self.station):
                if self.vr[i][j] > self.station -1:
                    self.vr[i][j] = self.station -1
                if self.vr[i][j] < -self.station + 1:
                    self.vr[i][j] = -self.station+1
                if self.vv[i][j] > self.car -1:
                    self.vr[i][j] = self.car -1
                if self.vv[i][j] < -self.car +1:
                    self.vr[i][j] = -self.car +1

    def update_x(self):
        for i in range(self.quanta):
            for j in range(self.station):
                self.xr[i][j] += self.vr[i][j]
                self.xv[i][j] += self.vv[i][j]
                self.verifiy_xv(self.xv[i])

    def eval_update_pi(self):
        res = 0
        for i in range(self.quanta):
            car_path = self.verifiy_xr(self.xv[i], self.xr[i])
            mark = self.eval(car_path)
            if mark <= self.optimizer[i]:
                self.optimizer[i] = mark
                self.pir[i] = self.xr[i].copy()
                self.piv[i] = self.xv[i].copy()
            res += self.optimizer[i]
        self.even_optimizer = res / self.quanta

    def one_iteg(self):
        if self.NC_index != 0:
            self.update_v()
        self.update_x()
        self.eval_update_pi()


    def update_statistic(self):
        res = []
        res.append(self.pgr)
        res.append(self.pgv)
        res.append(self.optimizer)
        res.append(self.even_optimizer)
        res.append(self.global_optimizer)

        self.statistics.append(res)


    def progress_bar(self, i):
        if self.iteg >= 100:
            index = int(self.iteg/100)
            if i%index == 0:
                print('-', end='')
        else:
            index = int(100/self.iteg)
            for j in range(index):
                print('-', end='')

    def PSO_main(self):
        print("start simulation: ", end='')
        for i in range(self.iteg):
            self.progress_bar(i)  # this is progress bar
            self.one_iteg()
            for i in range(self.quanta):
                if self.global_optimizer > self.optimizer[i]:
                    self.pgv = self.piv[i]
                    self.pgr = self.pir[i]
                    self.global_optimizer = self.optimizer[i]
            self.update_statistic()

        print(">!!")

        w = self.global_optimizer
        p = self.verifiy_xr(self.pgv,self.pgr)
        self.path = p
        print("result: f(",end='')
        print(p, ") = ",w )
        self.end_time = time.time()
        print("run time: ", self.end_time-self.start_time,"s")

    def print_variance(self):
        x = []
        y = []

        for i in range(len(self.statistics)):
            x.append(i+1)
            y.append(self.statistics[i][3])

        plt.figure("VRP")
        plt.title("VRP:variance")
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
            y.append(self.statistics[i][4])

        plt.figure("VRP-min")
        plt.title("VRP:history_min")
        plt.scatter(x, y, s = 1)
        name = self.file_path + 'history_min.jpg'
        plt.savefig(name)
        plt.show()
        plt.close()

    def print_path(self):
        plt.figure("VRP-path")
        plt.title("VRP:path")
        color = ['red', 'green','blue']

        for i in range(self.car):
            for j in range(len(self.path[i])-1):
                plt.scatter(self.position[self.path[i][j]][0],self.position[self.path[i][j]][1], color = color[i], s = 3)
                plt.plot([self.position[self.path[i][j]][0],self.position[self.path[i][j+1]][0]],\
                         [self.position[self.path[i][j]][1],self.position[self.path[i][j+1]][1]],\
                         color = color[i])
        plt.scatter(self.position[0][0], self.position[0][1], color='black', s=3)
        name = self.file_path + 'path.jpg'
        plt.savefig(name)
        plt.show()
        plt.close()



# parameters describe:
#iteg: time to loop
#quanta: quanta number for a group (we use one group for this ting problem)
#car: car number
#station: number of station (except the delivery point)
#w : velocity update parameter, indicate the inertance
#c1: velocity update parameter, indicate the migration to quanta_i's history optima
#c2 : velocity update parameter, indicate the migration to global optima

#iteg, quanta, car, station, w, c1, c2):
question1 = PSO(60, 100, 3, 7, 0.8, 0.5, 1.5)
question1.PSO_main()
question1.print_path()
question1.print_even()
question1.print_variance()
#print(question1.statistics)

# result:

