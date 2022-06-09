#blosum50のテキストファイルを開き二次元配列にするメソッド
def file_open(file):
    import sys
    data = []
    try:
        f = open(file, 'r')
    except Exception:
        print("open error. not found file:", int(file))
        sys.exit(1)
       
    for line in f:
        line = line.strip() #前後空白削除
        line = line.replace('\n','')#末尾の\nの削除
        #line = line.removeprefix('')
        line = line.split() #分割
        data.append(line)
    return data

#ローカルアラインメントの計算
#seq_x,seq_yはDNA配列x,yと対応する文字列
def local_alignment(seq_x,seq_y,index,matrix_score_1):
    import itertools
    #スコア配列list_dpの宣言
    list_dp = [[[] for dp_j in range(len(seq_x))]for dp_i in range(len(seq_y))]
    #再帰の種類を表す配列list_traceの宣言
    list_trace = [[[] for trace_j in range(len(seq_x))]for trace_i in range(len(seq_y))]

    s=0
    d1=-2
    d2=-2
    i=0
    j=0

    for i in range(len(seq_y)):
        for j in range(len(seq_x)):
            #初期化
            if i==0:
                list_dp[i][j] = 0
            elif j==0:
                list_dp[i][j] = 0
            else:
                #再帰
                #アミノ酸に番号をつけた辞書型データindexから、使用するアミノ酸(key)と対応する値を呼び出す   
                base_j=index[seq_x[j]]
                base_i=index[seq_y[i]]
                #整列スコアs
                s = list_dp[i-1][j-1]+int(matrix_score_1[base_i][base_j])
                #ギャップスコア
                d1=list_dp[i][j-1]-8
                d2=list_dp[i-1][j]-8
                #最大スコアの決定
                max_ij=max ([0,s,d1,d2])
                list_dp[i][j]=max_ij
            #list_trace配列の設定
            #xjとyiが整列した場合はs,yi がギャップに対応している場合にはd1,xjがギャップに対応している場合はd2を入れる   
            if list_dp[i][j]==s:
                list_trace[i][j]="s"
            elif list_dp[i][j]==d1:
                list_trace[i][j]="d1"
            elif list_dp[i][j]==d2:
                list_trace[i][j]="d2"
            elif list_dp[i][j]==0:
                list_trace[i][j]="0"
            else:
                list_trace[0][j]="0"
                list_trace[i][0]="0"
                list_trace[0][0]="0"
    #SWアルゴリズムで決定したアラインメントスコア中の最大値を決定         
    max_score = max(list(map(lambda x: max(x), list_dp)))
    #最大値に対応する配列は何番めか
    for y, row in enumerate(list_dp):
        try:
            index_score = (y, row.index(max_score))
            break
        except ValueError:
            pass
    
    m1=m2=m3=index_score[0]
    n1=n2=n3=index_score[1]
    #カウンターとしての変数p1,p2
    #p1,p2が0になるとトレースバックが終わる
    p1,p2=index_score[0]+1,index_score[1]+1
    #最適アラインメント配列align_i,align_j(seq_y,seq_xに対応)の宣言
    align_i = [[]]
    align_j = [[]]
    #トレースバックしたスコアの配列list_scoreの宣言
    list_score = [[]]
    
    #トレースバック：配列y
    for u in itertools.count():
        if list_trace[m1][n1] == "s":
            align_i[u]=seq_y[m1]
            p1 -= 1
            m1 -= 1
            n1 -= 1
        elif list_trace[m1][n1] == "d1":
            align_i[u]="-"
            m1 = m1
            n1 -= 1
        elif list_trace[m1][n1] == "d2":
            align_i[u] = seq_y[m1]
            p1 -= 1
            m1 -= 1
            n1 = n1
        align_i.append([])
        
        if list_dp[m1][n1]==0:
            align_i.remove([])
            break
                
    #トレースバック：配列x
    for v in itertools.count():
        if list_trace[m2][n2] == "s":
            align_j[v] = seq_x[n2]
            p2 -= 1
            m2 -= 1
            n2 -= 1

        elif list_trace[m2][n2] == "d2":
            align_j[v] = "-"
            m2 -= 1
            n2 = n2
            
        elif list_trace[m2][n2] == "d1":
            align_j[v] = seq_x[n2]
            p2 -= 1
            m2 = m2
            n2 -= 1
        align_j.append([])
        
        if list_dp[m2][n2]==0:
            align_j.remove([])
            break

    #トレースバックの際のスコア配列list_scoreの設定
    list_score = [[] for k in range(len(align_i))]
    for w in itertools.count():
        if list_trace[m3][n3] == "s":
            list_score[w]=list_dp[m3][n3]
            m3-=1
            n3-=1 
        elif list_trace[m3][n3] == "d1":
            list_score[w]=list_dp[m3][n3]
            m3 = m3
            n3 -= 1
        elif list_trace[m3][n3] == "d2":
            list_score[w]=list_dp[m3][n3]
            m3 -= 1
            n3 = n3  
        if w > len(list_score):
            break
    return align_i,align_j,list_score

#グローバルアラインメントを行う関数の宣言
#seq_x,seq_yはDNA配列x,yと対応する文字列
def global_alignment(seq_x,seq_y,index,matrix_score_1):
    import itertools
    
    #スコア配列list_dpの宣言
    list_dp = [[[] for dp_j in range(len(seq_x))]for dp_i in range(len(seq_y))]
    #再帰の種類を表す配列list_traceの宣言
    list_trace = [[[] for trace_j in range(len(seq_x))]for trace_i in range(len(seq_y))]

    s=0
    d1=-2
    d2=-2
    i=0
    j=0

    for i in range(len(seq_y)):
        for j in range(len(seq_x)):
            if i==0:
                #初期化
                list_dp[i][j] = -2*j
            elif j==0:
                list_dp[i][j] = -2*i
            else:
                #再帰
                base_j=index[seq_x[j]]
                base_i=index[seq_y[i]]
            
                s = list_dp[i-1][j-1]+int(matrix_score_1[base_i][base_j])
                d1=list_dp[i][j-1]-8
                d2=list_dp[i-1][j]-8
                max_ij=max ([s,d1,d2])
                list_dp[i][j]=max_ij
            #list_trace配列の設定
            #xjとyiが整列した場合はs,yi がギャップに対応している場合にはd1,xjがギャップに対応している場合はd2を入れる   
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
    #カウンターとしての変数p1,p2
    #p1,p2が0になるとトレースバックが終わる
    p1,p2=len(seq_y),len(seq_x)
    #最適アラインメント配列align_i,align_j(seq_y,seq_xに対応)の宣言
    align_i = [[]]
    align_j = [[]]
    #トレースバックしたスコアの配列list_scoreの宣言
    list_score = [[]]

    #トレースバック：配列y
    for u in itertools.count():
        if list_trace[m1][n1] == "s":
            align_i[u]=seq_y[m1]
            p1 -= 1
            m1 -= 1
            n1 -= 1
        elif list_trace[m1][n1] == "d1":
            align_i[u]="-"
            m1 = m1
            n1 -= 1
        elif list_trace[m1][n1] == "d2":
            align_i[u] = seq_y[m1]
            p1 -= 1
            m1 -= 1
            n1 = n1
        align_i.append([])

        if p1<=0:
            align_i.remove([])
            break
                
    #トレースバック：配列x
    for v in itertools.count():
        if list_trace[m2][n2] == "s":
            align_j[v] = seq_x[n2]
            p2 -= 1
            m2 -= 1
            n2 -= 1

        elif list_trace[m2][n2] == "d2":
            align_j[v] = "-"
            m2 -= 1
            n2 = n2
            
        elif list_trace[m2][n2] == "d1":
            align_j[v] = seq_x[n2]
            p2 -= 1
            m2 = m2
            n2 -= 1
        align_j.append([])
        if p2<=0:
            align_j.remove([])
            break

    #トレースバックの際のスコア配列list_scoreの設定
    list_score = [[] for k in range(len(align_i))]
    for w in itertools.count():
        if list_trace[m3][n3] == "s":
            list_score[w]=list_dp[m3][n3]
            m3-=1
            n3-=1 
        elif list_trace[m3][n3] == "d1":
            list_score[w]=list_dp[m3][n3]
            m3 = m3
            n3 -= 1
        elif list_trace[m3][n3] == "d2":
            list_score[w]=list_dp[m3][n3]
            m3 -= 1
            n3 = n3  
        if w >= len(list_score)-1:
            break
    return align_i,align_j,list_score
    


