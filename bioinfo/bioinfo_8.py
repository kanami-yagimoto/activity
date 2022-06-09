import math
f = open('observed.txt', 'r')#観測列:observations

y = f.read()

f.close()

y = y.replace('\n','')

X = ['F', 'L'] #states
 
sp = {'F': math.log(0.5), 'L': math.log(0.5)} #初期確率:start_probability
 
tp = {
    'F' : {'F': math.log(0.95), 'L': math.log(0.05)},
    'L' : {'F': math.log(0.1), 'L': math.log(0.9)},
    }#遷移確率:transition_probability
 
ep = {
    'F' : {'1':1/6, '2':1/6, '3':1/6, '4':1/6 , '5':1/6 , '6':1/6},
    'L' : {'1':1/10, '2':1/10, '3':1/10, '4':1/10 , '5':1/10 , '6':1/2},
    }#出力確率:emission_probability

V = [{}]
for state in X:
    V[0][state] = {"prob": sp[state] + math.log(ep[state][y[0]]), "past": None}

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

print("最適パス:",v_path,"\n同時確率(log):",v_prob_list)
