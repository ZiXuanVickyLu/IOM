import SA_ as sa
import sys

#load the file
def load_file():
    filename = []
    if __name__=='__main__':
        if len(sys.argv)>=2:
             filename = sys.argv[1]
        else:
            exit(1) #argv error, no file exist.

    file_obj = open(filename)
    file_context = file_obj.read().splitlines()
    file_obj.close()
    num = int(file_context[0])
    people_name = [[]for i in range(num)]
    for i in range(num):
        tmp = file_context[i+1].split(',')
        people_name[i] = tmp[1]
    match_weight = []
    for i in range(1 + num + 1,len(file_context)):
        tmp = file_context[i].split(',')
        for j in range(3):
            tmp[j] = int(tmp[j])
        match_weight.append(tmp)

    return (num,people_name, match_weight)


# SA parameters describe:
# code length: number of participants in file '.wmg'
# SA max inner step TL: 200 (control annealing)
# SA max outer step: 5000 (control Temperature dropping)
# SA inner convergence condition: 0(do not use), others, range: [1, max_inner_step]
# SA outer convergence condition: 0(do not use), others, range: [1, max_outer_step]
# (accelerating tech explain):
# if max_step times of iteration remains the result, which means a convergence, then there is no need to go on.
# SA initial Temperature: T0 = 5000
# SA Temperature Multiplier: T_k+1 = T_k * TMultiplier
# So the T = TMultiplier **(outer_step(really ran)) * T0

#parameter list of the SA class:
#clength, inner_step, outer_step, inner_stop, outer_stop, T0, TMultipiler
data = load_file()
question1 = sa.SA(data[0], 200, 5000, 0, 700, 5000, 0.995)

for i in range(len(data[1])):
    question1.set_name(i, data[1][i])

for i in range(len(data[2])):
    question1.set_weight(data[2][i][1]-1, data[2][i][2]-1, data[2][i][0])

question1.SA_main()
question1.print_even()
question1.print_variance()

#debug:
#print(question1.statistics)
