import math
import random

X = ['F', 'L'] #states

#いかさまカジノHMMモデル
dice = ['1','2','3','4','5','6']
w_state_F = [0.95,0.05]
w_state_L = [0.1,0.9]
w_L = [1,1,1,1,1,5]

st_list = ['F']

for i in range(1,10000):
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
             
sp = {'F': 0.5, 'L': 0.5} #初期確率:start_probability
 
tp = {
    'F' : {'F': 0.95, 'L': 0.05},
    'L' : {'F': 0.1, 'L': 0.9},
    }#遷移確率:transition_probability
 
ep = {
    'F' : {'1':1/6, '2':1/6, '3':1/6, '4':1/6 , '5':1/6 , '6':1/6},
    'L' : {'1':1/10, '2':1/10, '3':1/10, '4':1/10 , '5':1/10 , '6':1/2},
    }#出力確率:emission_probability

#最適パスの算出
def viterbi():

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

    for t in range(len(V) - 2, -1, -1):
        v_prob_list.insert(0, V[t + 1][past]["prob"])
        v_path.insert(0, V[t + 1][past]["past"])
        past = V[t + 1][past]["past"]
 
    return v_path

#最適パス
v_path = viterbi()

#スケーリング版前向きアルゴリズム
def forward_scaling():

    #初期化
    F = [{}]
    S = [1]
    for state in X:
        F[0][state] = sp[state] * ep[state][y[0]]

    #再帰
    for i in range(1 , len(y)):
        F.append({})
        s_i = 0
        for now_state in X:
            p_sum = 0
            for past_state in X:
                p = F[i-1][past_state] * tp[past_state][now_state]
                p_sum += p
                    
            f_prob = p_sum * ep[now_state][y[i]]
            s_i += f_prob
            F[i][now_state] = f_prob
        #スケーリング版前向き変数    
        for st,pr in F[i].items():
            f_prob = pr/s_i
            F[i][st] = f_prob
            
        S.append(s_i)
    
    #終了処理  
    p_fwd = 0
    for s_i in S:
        p_fwd *= s_i
    
    return F,S

#スケーリング係数
F,S = forward_scaling()

#スケーリング版後ろ向きアルゴリズム
def backward_scaling():
    
    #初期化
    B = [{}]
    for state in X:
        B[0][state] = 1

    #再帰
    for i in range(1,len(y)):
        B.append({})
        for now_state in X:
            p_sum = 0
            for next_state in X:
                p = ep[next_state][y[-i]] * tp[now_state][next_state] * B[i-1][next_state]
                p_sum += p
                 
            B[i][now_state] = p_sum
        #スケーリング版後ろ向き変数    
        for st,pr in B[i].items():
            b_prob = pr/S[-i]
            B[i][st] = b_prob

    return B

B = backward_scaling()

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
    
dec_path = decodling()

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
