#入力配列seq_x,seq_yの最適アラインメントとそのスコアを出力する
def alignment(seq_x,seq_y):
    import itertools

    #dp行列
    list_dp = [[[] for dp_j in range(len(seq_x))]for dp_i in range(len(seq_y))]
    #トレースバック行列
    list_trace = [[[] for trace_j in range(len(seq_x))]for trace_i in range(len(seq_y))]
    #アラインメントスコア
    s=0
    d1=-2
    d2=-2
    i=0
    j=0

    for i in range(len(seq_y)):
        for j in range(len(seq_x)):
            if i==0:
                list_dp[i][j] = -2*j
            elif j==0:
                list_dp[i][j] = -2*i
            else:
                base_j=seq_x[j]
                base_i=seq_y[i]
                """
                base_j=index[seq_x[j]]
                base_i=index[seq_y[i]]
            
                s = list_dp[i-1][j-1]+int(matrix_score_1[base_i][base_j]
                """
                if base_i==base_j:
                    s=list_dp[i-1][j-1]+2#int(matrix_score_1[base_i][base_j])

                else:
                    s=list_dp[i-1][j-1]-1#
                    
                d1=list_dp[i][j-1]-2#8
                d2=list_dp[i-1][j]-2#8
                max_ij=max ([s,d1,d2])
                list_dp[i][j]=max_ij
                
            if list_dp[i][j]==s:
                list_trace[i][j]="s"
            elif list_dp[i][j]==d1:
                list_trace[i][j]="d1"
            elif list_dp[i][j]==d2:
                list_trace[i][j]="d2"
            else:
                list_trace[0][j]="d1"
                list_trace[i][0]="d2"
                list_trace[0][0]="s"
                
    m1=m2=m3=len(seq_y)-1
    n1=n2=n3=len(seq_x)-1
    p1,p2=len(seq_y),len(seq_x)
    test = [[] for i in range(len(seq_x)+1)]

    align_i = [[]]
    align_j = [[]]
    list_score = [[]]

    #配列yの最適アラインメント
    for u in itertools.count():
        if list_trace[m1][n1] == "s":
            test[p1]="s"
            align_i[u]=seq_y[m1]
            p1 -= 1
            m1 -= 1
            n1 -= 1
        elif list_trace[m1][n1] == "d1":
            test[p1]="d1"
            align_i[u]="-"
            m1 = m1
            n1 -= 1
        elif list_trace[m1][n1] == "d2":
            test[p1]="d2"
            align_i[u] = seq_y[m1]
            p1 -= 1
            m1 -= 1
            n1 = n1
        align_i.append([])

        if p1<=0:
            align_i.remove([])
            break
                
    #配列xの最適アラインメント
    for v in itertools.count():
        if list_trace[m2][n2] == "s":
            test[p2]="s"
            align_j[v] = seq_x[n2]
            p2 -= 1
            m2 -= 1
            n2 -= 1

        elif list_trace[m2][n2] == "d2":
            test[p2]="d2"
            align_j[v] = "-"
            m2 -= 1
            n2 = n2
            
        elif list_trace[m2][n2] == "d1":
            test[p2]="d1"
            align_j[v] = seq_x[n2]
            p2 -= 1
            m2 = m2
            n2 -= 1
        align_j.append([])
        if p2<=0:
            align_j.remove([])
            break

    #スコア
    p3=len(align_i)-1
    list_score = [[] for k in range(len(align_i))]
    while p3 >= 0:
        if list_trace[m3][n3] == "s":
            list_score[-p3]=list_dp[m3][n3]
            m3-=1
            n3-=1 
        elif list_trace[m3][n3] == "d1":
            list_score[-p3]=list_dp[m3][n3]
            m3 = m3
            n3 -= 1
        elif list_trace[m3][n3] == "d2":
            list_score[-p3]=list_dp[m3][n3]
            m3 -= 1
            n3 = n3  
        list_score.append([])
        p3 -= 1

    new_score = [s for s in list_score if s!=[]]
    new_score.remove(0)
    return align_i,align_j,new_score
