## 粒子群优化算法

### PSO产生的背景：

#### 1. 复杂适应系统（CAS）

​	我们把系统中的成员称为具有适应性的主体(Adaptive Agent)，简称为主体。所谓具有适应性，就是指它能够与环境以及其它主体进行交流，在这种交流的过程中“学习”或“积累经验”，并且根据学到的经验改变自身的结构和行为方式。整个系统的演变或进化，包括新层次的产生，分化和多样性的出现，新的、聚合
而成的、更大的主体的出现等等，都是在这个基础上出现的。

- 主体是主动的、活的实体
- 个体与环境的相互影响，相互作用，是系统演变和进化的主要动力
- 并不直接联系宏观和微观
- 引入了随机因素，因此具有更强的描述和表达能力

#### 2.人工生命

人工生命“是来研究具有某些生命基本特征的人工系统。人工生命包括两方面的内容:

- 研究如何利用计算技术研究生物现象;
-  研究如何利用生物技术研究计算问题(Nature Computation)

​    现在已经有很多源于生物现象的计算技巧，例如, 人工神经网络是简化的大脑模型；遗传算法是模拟基因进化过程的。

​	讨论另一种生物系统：社会系统，更确切地说，是由简单个体组成的群落与环境以及个体之间的互动行为，也可称做"群智能"。

### PSO的基本思想

模仿鸟群的飞行，觅食行为的特征

1. 保持惯性
2. 按照自身的最优修正方向
3. 按群体的最优修正方向

### PSO基本迭代公式

​	对于每一代粒子，其速度

$V_i = \{V_{i1},V_{i2},\cdots,V_{id},\cdots,V_{iD}\}$

$V_{id}^{k+1}=\omega V_{id}^k(\text{ inertance})+c_1\xi_1(P_{id}-X_{id})(\text{self optimal direction})+c_2\xi_2(P_{gd}-X_{id})(\text{group optimal direction})$，其中$\xi_1,\xi_2\in \bigcup(0,1)$，$\omega,c_1,c_2$是常数

$X_{id}^{k+1} = X_{id}^k+V_{id}$

其中$p_i$是粒子i的历史最优解

$p_{id}$是$p_i$的第$d$个分量

$p_g$是群体的历史最优解

### PSO的算法

1. 初始化粒子群$i =1,2,\cdots,m$，给予随机的位置和速度$x_i,v_i$
2. 评估每个粒子的适应值$f(x),F(x_i)$，其中$i=1,2,\cdots,m$ （目标函数值）
3. 对每个粒子，更新粒子最优位置$p_i$
4. 对群体粒子更新历史最优解$p_g$
5.  对所有粒子计算$x_i,v_i$
6. 若达到最大迭代数则停止，否则转step 2
