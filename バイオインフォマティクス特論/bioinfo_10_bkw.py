import math

f = open('observed.txt', 'r')#観測列:observations

y = f.read()

f.close()

y = y.replace('\n','')

#y='315'
X = ['F', 'L'] #states

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
def viterbi(X,y,sp,tp,ep):

    V = [{}]
    for state in X:
        V[0][state] = {"prob": sp[state] + ep[state][y[0]], "past": None}

    for i in range(1,len(y)):
        V.append({})
        for now_state in X:
            p_max = V[i-1][X[0]]["prob"] + tp[X[0]][now_state]
            selected_state = X[0]
            for past_state in X:
                p = V[i-1][past_state]["prob"] + tp[past_state][now_state]
                if p > p_max:
                    p_max = p
                    selected_state = past_state
                    
            v_prob = p_max + math.log(ep[now_state][y[i]])
            V[i][now_state] = {"prob": v_prob, "past": selected_state}

    v_path = []
    v_prob_list = []
    p_max = -1000.0
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
v_path = viterbi(X,y,sp,tp,ep)

#対数変換版
def backward_log(X,y,sp,tp,ep,v_path):

    #初期化
    B = [{}]
    for state in X:
        B[0][state] = 0

    #再帰
    for i in range(1,len(y)):
        B.append({})
        for now_state in X:
            p_sum = 0
            for next_state in X:
                p = math.log(ep[next_state][y[-i]]) + math.log(tp[now_state][next_state]) + B[i-1][next_state]
                p_sum += math.exp(p)
                     
            B[i][now_state] = math.log(p_sum)
      
    b_prob_list = []
    for t in range(len(v_path) - 1, -1, -1):
        b_prob_list.insert(0, B[t][v_path[t]])

    #終了処理   
    p_bkw = 0
    for state in X:
        p = B[len(y)-1][state] + math.log(ep[state][y[0]]) + math.log(sp[state])
        p_bkw += math.exp(p)

    print("対数変換版","\n","p(x)=",math.log(p_bkw),"\n","観測列に対応する周辺化確率：","\n",b_prob_list)

#スケーリング係数の算出
def forward_scaling(X,y,sp,tp,ep,v_path):

    F = [{}]
    S = [1]
    for state in X:
        F[0][state] = sp[state] * ep[state][y[0]]

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

    f_prob_list = []
    for t in range(len(v_path) - 1, -1, -1):
        f_prob_list.insert(0, F[t][v_path[t]])
       
    p_fwd = 1
    for s_i in S:
        p_fwd *= s_i
    
    return S

#スケーリング係数
S = forward_scaling(X,y,sp,tp,ep,v_path)

#スケーリング版
def backward_scaling(X,y,sp,tp,ep,v_path):
    
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
      
    b_prob_list = []
    for t in range(len(v_path) - 1, -1, -1):
        b_prob_list.insert(0, B[t][v_path[t]])

    #終了処理    
    s_times = 1
    p_bkw = 0
    for s_i in S[1:]:
        s_times *= s_i
        
    for state in X:
        p = sp[state] * ep[state][y[0]] * B[len(y)-1][state] * s_times
        p_bkw += p
        
    print("スケーリング版","\n","p(x)=",math.log(p_bkw),"\n","観測列に対応する周辺化確率：","\n",b_prob_list)

#実行

backward_log(X,y,sp,tp,ep,v_path)
backward_scaling(X,y,sp,tp,ep,v_path)
