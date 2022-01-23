## 用遗传算法求解TSP问题

### 遗传编码

#### 综述

​	对称TSP问题的遗传编码通常采用顺序编码，按照编码思路可以分成路径编码、次序编码、邻近编码。其中次序编码的随机生成思路最为简单，因为每一位都可单独生成，并且总保证编码的合法性；其他编码在生成的时候难以保证随机性、均匀性和合法性，需要进行合法性检验，比较困难；但是三种编码之间的相互转化是一一对应的，并且只有编码长度线性的时间复杂度。因此可以采用通用的随机生成思路（生成次序编码），通过函数处理成对应编码，保证初始群体的随机与合法。而后三种编码采用各自编码空间的带有修复策略的遗传算子，保证种群迭代过程中编码的合法性，直到群体收敛。



- 路径编码

  - 编码在GA中的分类属于整数顺序编码

  - 编码思路：直接罗列访问的城市顺序，编码思路非常直接而自然

  - 随机数生成思想：需要生成均匀合法的n-length圈置换，非常困难；采取的策略是：生成了次序编码，而后直接转换为路径编码

    ```python
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
    ```

    

  - 遗传算子：

    - 交叉算子：OX交叉修复策略

      ```python
          def crossover_operator(self, code1, code2):
              res = [[[[]for i in range(self.node_num)]for k in range(2)]for j in range(self.dim)]
              for j in range(self.dim):
                  bucket=[[]for k in range(2)]
                  bucket[0] = [0 for i in range(self.node_num+1)]
                  bucket[1] = [0 for i in range(self.node_num+1)]
                  co = [[]for k in range(2)]
      
                  pos1 = self.U_1_nth(self.node_num)
                  pos2 = self.U_except(pos1)
                  pos1 -= 1
                  pos2 -= 1
                  pos_f = min(pos1, pos2)
                  pos_b = max(pos1, pos2)
                  if pos_f == 0:
                      pos_f += 1
      
                  co[1] = code1[j][pos_b:]
                  co[1] += code1[j][0:pos_b]
      
                  co[0] = code2[j][pos_b:]
                  co[0] += code2[j][0:pos_b]
      
                  for i in range(pos_f,pos_b):
                      bucket[0][code1[j][i]] = 1
                      bucket[1][code2[j][i]] = 1
                      res[j][0][i] = code1[j][i]
                      res[j][1][i] = code2[j][i]
      
                  index = [0, 0]
                  for k in range(2):
                      for i in range(pos_b, self.node_num):
                          for m in range(index[k], self.node_num):
                              if bucket[k][co[k][m]] == 0:
                                  bucket[k][co[k][m]] = 1
                                  res[j][k][i] = co[k][m]
                                  index[k] = m
                                  break
                      for i in range(0, pos_f):
                          for m in range(index[k], self.node_num):
                              if bucket[k][co[k][m]] == 0:
                                  bucket[k][co[k][m]] = 1
                                  res[j][k][i] = co[k][m]
                                  index[k] = m
                                  break
              return res
      ```

      ​	首先确定两个交叉位点，在子代中保留它们，而后第二个交叉位点后开始，顺序写出另一个亲本的基因序列，划掉子代中出现的序列，依次填入子代从第二个位点后开始，直到第一个位点前。

    - 变异算子：倒位变异：选择两个位点，交换之，交换后的路径仍然是合法的，所以染色体也是合法的

- 次序编码

  - 编码在GA中的分类属于整数顺序编码

  - 编码思路：假设访问的城市序列已知，而城市仅可以路过一次，且城市编号一定在[1,n]中，将城市编号按顺序排列好，则每位编码为将要访问的城市在未访问城市的顺序表中的位置，每访问一个城市，未访问的城市表长度递减，从而每一位的合法取值为[1, n-i+1]，i为第i位。

  - 随机数生成思想：次序编码的每一位都是属于[1,n-i+1]的整数，因此只要生成的单一编码未符合上述要求，整个的n位长度编码就是均匀、随机、合法的编码

    ```python
        def get_code(self):
            res = []
            for i in range(self.code_length):
                a_num = self.U_CodeBit(i)
                res.append(a_num)
            ans = self.neighbor2code(res)
            return ans
        
        def U_CodeBit(self, codebit_pos): #[1, node_num - codebit_pos] integer
            a = self.U()
            i = self.node_num - codebit_pos
            res = int(a * i) +1
            if res > i:
                res = i
            return res
    	
    ```

    

  - 遗传算子：

    - 交叉算子：所有关于顺序编码的传统交叉算子均可使用，因为交叉只改变片段子序列的对应位置，而两个亲本的子序列的对应位置满足次序编码的位范围要求。直接选择单点交叉变异
    - 变异算子：这时候倒位变异可能会导致位于前面的位超过位范围要求从而导致编码不合法，因此需要使用单点突变，同时对于突变的某一位随机生成满足位范围要求的位编码。

- 邻近编码

  - 编码在GA中的分类属于整数顺序编码

  - 编码思路：对于一个已知的路径，环路一定有n条边，直接记录出边并且按照出发节点为1至n罗列这些边，省去1到n这些出发节点构成的n个入结点编号就是邻近编码

  - 随机数生成思想：随机生成的n长圈置换作为邻近编码，可能面临不合法，因为该邻近编码可能构成了一个长度更小的圈置换，需要合法性检查，并且非常麻烦；采取的策略是：生成了合法的次序编码，而后直接转换为邻近编码

    ```python
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
    ```

    

  - 遗传算子：

    - 交叉算子：采用启发式交叉，每次交叉操作仅产生一个染色体子代。

      算法思路：对于两个父代，首先选择一个起始城市，比较以起始城市为出结点的出边的权，选取权小的边，边的另一个结点为下一个起始城市。如果在某次比较选择操作中，出边通往的城市已经在路径之中，则从余下的未到达的城市任选一个作为目的地，连接出结点与该结点，加入路径；直到所有的结点均（唯一只有一次）出现在路径中。将路径转换为邻近编码；得到该交叉后的子代染色体。

      ```python
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
              
          def path2code(self, ans):
              result = [[]for i in range(self.node_num)]
              for i in range(self.node_num-1):
                  result[ans[i]-1] = ans[i + 1]
              result[ans[self.node_num-1]-1] = ans[0]
              return result
      ```

      

    - 变异算子：任何在邻近编码空间变异算子的直接尝试都会引入带环子路径（长度小于n的环），从而导致编码不合法；一个可行的思路是将邻近编码转到其他编码空间做变异操作，但是失去了在邻近编码空间引入变异的意义

#### 收敛准则

- 最大迭代次数收敛，需要手动调参
- 迭代收敛：群体经过若干次的遗传操作，大部分群体染色体趋于一致，当一致的染色体数大于群体的某个百分比后，认为该遗传算法的优化问题已经收敛。通常这个百分比是变异率、交叉率的函数（变异率越高，每轮迭代都会为种群引入新的基因，这些基因与种群的大多数不同；交叉操作又将每次迭代的以一定概率引入种群）
  - 本实验中，方便起见，采用群体相同染色体达到$1-mutationRate*30$作为收敛准则，其中变异率选取为$1\%$



## 结果

- 使用邻近编码的启发式搜索迭代收敛很快

- 使用次序编码效果不佳，离该问题的最优解差的较远，邻近编码和可以比较快（数秒内）地收敛到最优解差距10%附近。

- 一次try-out结果展示：

  - **pathCode**:

     result: f([[(12, 13), (13, 4), (4, 5), (5, 6), (6, 1), (1, 2), (2, 18), (18, 3), (3, 9), (9, 11), (11, 7), (7, 19), (19, 20), (20, 21), (21, 10), (10, 8), (8, 14), (14, 15), (15, 24), (24, 25), (25, 26), (26, 29), (29, 27), (27, 28), (28, 16), (16, 17), (17, 22), (22, 23), (23, 30), (30, 12)]] ) =  **424.9002540077531**

    run time:  **35.590447187423706 s**

  - **neighborCode:**

    result: f([[(1, 2), (2, 3), (3, 18), (4, 5), (5, 6), (6, 1), (7, 19), (8, 14), (9, 11), (10, 8), (11, 7), (12, 13), (13, 4), (14, 15), (15, 24), (16, 17), (17, 22), (18, 9), (19, 20), (20, 21), (21, 10), (22, 23), (23, 30), (24, 25), (25, 26), (26, 29), (27, 16), (28, 27), (29, 28), (30, 12)]] ) =  **427.89714014496684**
    run time:  **4.340854167938232 s**

  - **orderCode:**

    result: f([[(2, 3), (3, 19), (19, 10), (10, 14), (14, 8), (8, 25), (25, 15), (15, 26), (26, 28), (28, 27), (27, 24), (24, 18), (18, 11), (11, 9), (9, 16), (16, 17), (17, 22), (22, 23), (23, 30), (30, 12), (12, 13), (13, 29), (29, 7), (7, 21), (21, 20), (20, 1), (1, 6), (6, 5), (5, 4), (4, 2)]] ) =  **667.9873577231103**
    run time:  **112.34261083602905 s**

