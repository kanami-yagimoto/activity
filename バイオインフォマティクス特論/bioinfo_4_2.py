import time
keika_jikan_1 = [[] for t in range(10)]
keika_jikan_2 = [[] for t in range(10)]
keika_jikan = [[] for t in range(10)]
n=int(input("配列xの塩基数をnとすると、n="))+1
m=int(input("配列yの塩基数をmとすると、m="))+1

for p in range(10):
    keika_jikan_1[p]=time.time()
    import random,bioinfo_4
    seq_x = [[] for i in range(n)]
    seq_y = [[] for i in range(m)]

    seq_x[0]=seq_y[0]=" "

    genome_code={0:"A",1:"T",2:"C",3:"G"}


    for q in range(1,n):
        seq_x[q]=genome_code[random.randint(0,3)]
    for r in range(1,m):
        seq_y[r]=genome_code[random.randint(0,3)]

    bioinfo_4.alignment(seq_x,seq_y)

    keika_jikan_2[p]=time.time()
    keika_jikan[p] = keika_jikan_2[p]-keika_jikan_1[p]
    
keika_ave = sum(keika_jikan)/len(keika_jikan)
    
print(f"経過時間平均：{keika_ave}")

