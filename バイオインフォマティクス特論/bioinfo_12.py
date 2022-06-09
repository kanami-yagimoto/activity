import math
import random

X = ['F', 'L'] #states
dice = ['1','2','3','4','5','6']

def casino(length):
    #いかさまカジノHMMモデル
    w_state_F = [0.95,0.05]
    w_state_L = [0.1,0.9]
    w_L = [1,1,1,1,1,5]

    st_list = ['F']

    for i in range(1 , length):
        if st_list[i-1] == 'F':
            st_list += random.choices(X, weights = w_state_F)
           
        if st_list[i-1] == 'L':
            st_list += random.choices(X, weights = w_state_L)
                
    y = []
    for i in range(len(st_list)):
        if st_list[i] == 'F':
            y += random.choices(dice)
        if st_list[i] == 'L':
            y += random.choices(dice, weights = w_L)

    return y,st_list
       
sp = {'F': 0.5, 'L': 0.5} #初期確率:start_probability
 


#最適パスの算出
def viterbi(tp,ep):

    V = [{}]
    for state in X:
        V[0][state] = {"prob": math.log(sp[state]) +math.log(ep[state][y[0]]), "past": None}
        
    for i in range(1,len(y)):
        V.append({})
        for now_state in X:
            p_max = V[i-1][X[0]]["prob"] + math.log(tp[X[0]][now_state])
            selected_state = X[0]
            for past_state in X:
                p = V[i-1][past_state]["prob"] + math.log(tp[past_state][now_state])
                if p > p_max:
                    p_max = p
                    selected_state = past_state
                    
            v_prob = p_max + math.log(ep[now_state][y[i]])
            V[i][now_state] = {"prob": v_prob, "past": selected_state}

    v_path = []
    v_prob_list = []
    p_max = -100000.0
    best_state = None

    for state,data in V[-1].items():
        if data["prob"] > p_max:
            p_max = data["prob"]
            best_state = state
    v_prob_list.append(p_max)
    v_path.append(best_state)
    past = best_state

    for t in range(len(V)-2, -1, -1):
        v_prob_list.insert(0, V[t + 1][past]["prob"])
        v_path.insert(0, V[t + 1][past]["past"])
        past = V[t + 1][past]["past"]

    return v_path

tp = {
    'F' : {'F': 0.95, 'L': 0.05},
    'L' : {'F': 0.1, 'L': 0.9},
    }#遷移確率:transition_probability
 
ep = {
    'F' : {'1':1/6, '2':1/6, '3':1/6, '4':1/6 , '5':1/6 , '6':1/6},
    'L' : {'1':1/10, '2':1/10, '3':1/10, '4':1/10 , '5':1/10 , '6':1/2},
    }#出力確率:emission_probability


#スケーリング版前向きアルゴリズム

#初期化
F = [{}]
S = [1]

def forward_scaling(i,y):
    
    for state in X:
        F[0][state] = sp[state] * ep[state][y]
    
    s_i = 0
    F.append({})
    for now_state in X:
        p_sum = 0
        for past_state in X:
            p = F[i-1][past_state] * tp[past_state][now_state]
            p_sum += p
                
        f_prob = p_sum * ep[now_state][y]
        s_i += f_prob
        F[i][now_state] = f_prob

    S.append(s_i)
        
    #スケーリング版前向き変数    
    for st,pr in F[i].items():
        f_prob = pr/s_i
        F[i][st] = f_prob
    
    #終了処理  
    p_fwd = 1
    L = 0
    for s_i in S:
         L += math.log(s_i)
        
    return F,L

#スケーリング係数
#F,p,S = forward_scaling()

#初期化
B = [{}]

#スケーリング版後ろ向きアルゴリズム
def backward_scaling(i,y):
    
    for state in X:
        B[0][state] = 1
        
    #再帰
    B.append({})
    for now_state in X:
        p_sum = 0
        for next_state in X:
            p = ep[next_state][y] * tp[now_state][next_state] * B[i-1][next_state]
            p_sum += p     
        B[i][now_state] = p_sum
    #スケーリング版後ろ向き変数    
    for st,pr in B[i].items():
        b_prob = pr/S[-i]
        B[i][st] = b_prob
            
    return B


def BW_algorithm():
    E = 0
    E_sum_i = {}
    E_sum_b = {}
    A_sum_i = [{}]
    A_sum_l = {}
    L_list = [1]
    
    #パラメタ更新
    #出力確率

    for i in range(1 , len(y)):
        for b in dice:
            F_b,L_b = forward_scaling(i,b)
            
            B = backward_scaling(i,b)
  
    for now_state in X:
        E_sum_i[now_state] = {}
        for b in dice:
            E_sum_i[now_state][b] = 0
            E_sum_b[now_state] = 0
            for i in range(1 , len(y)):
                #print(B[-i-1][now_state])
                E = F[i][now_state] * B[-i-1][now_state]
                E_sum_i[now_state][b] += E

    for now_state in X:
        for b in dice:
            E_sum_b[now_state] += E_sum_i[now_state][b]

    ep = {}
    for state in X:
        ep[state] = {}
        for b in dice:
            ep[state][b] = E_sum_i[state][b]/E_sum_b[state]

    #遷移確率            
    for now_state in X:
        A_sum_l[now_state] = 0
        for next_state in X:
            A_sum_i[now_state][next_state] = 0
            for i in range(1,len(y)):
                A = F[i][state] * tp[now_state][next_state] * ep[next_state][y[i+1]] * B[-i-2][next_state]/S[i+1]
                A_sum_i[now_state][next_state] += A
            A_sum_l[now_state] += A_sum_i[now_state][next_state]

    tp = {}
    for now_state in X:
        tp[now_state] = {}
        for next_state in X:
            tp[now_state][next_state] = A_sum_i[now_state][next_state]/A_sum_l[now_state]

    return tp,ep
    
y,st_list = casino(300)

#事後デコーディング
def decodling():

    dec_st = ['F']
    for i in range(1,len(y)):
        p_post_max = -100000
        for state in X:
            p_post =  F[i][state] * B[-i-1][state]
            if p_post > p_post_max:
                p_post_max = p_post
                best_state = state
        dec_st.append(best_state)

    return dec_st

tp = {
    'F' : {'F': 0.95, 'L': 0.05},
    'L' : {'F': 0.1, 'L': 0.9},
    }#遷移確率:transition_probability
 
ep = {
    'F' : {'1':1/6, '2':1/6, '3':1/6, '4':1/6 , '5':1/6 , '6':1/6},
    'L' : {'1':1/10, '2':1/10, '3':1/10, '4':1/10 , '5':1/10 , '6':1/2},
    }#出力確率:emission_probability

v_path = viterbi(tp,ep)
dec_st = decodling()

j = 1
L_list = [1]
while True:
    tp,ep = BW_algorithm()
    v_path = viterbi(tp,ep)
    dec_path = decodling()
    L_list[j] = L
    j += 1

    if L_list[j]-L_list[j-1] < 1e-3:
        break

#精度チェック
def accuracy():

    correct = 0
    for i in range(len(y)):
        if st_list[i] == dec_path[i]:
            correct += 1
    acc_dec = correct*100/len(y)

    correct = 0
    for i in range(len(y)):
        if st_list[i] == v_path[i]:
            correct += 1
    acc_v = correct*100/len(y)

    print('accuracy of decoding',acc_dec,'%','\n','accuracy of viterbi',acc_v,'%')

         
accuracy()  
