import bioinfo_5
import argparse
#blosum50のテキストファイルを開き二次元配列にする
matrix_score_00 = bioinfo_5.file_open("blosum50.txt")
matrix_score_0 = matrix_score_00[1:]
matrix_score_1 = [[]]
for row in matrix_score_0:
        matrix_score_1[len(matrix_score_1)-1] = row[1:]
        matrix_score_1.append([])
list_num = list(range(-1,len(matrix_score_00[0])-1))
index = dict(zip(matrix_score_00[0],list_num))

#アミノ酸配列のテキストファイル を読み込み
seq_file=open("amn_file.txt","r")
list_seq=seq_file.readlines()
seq_x=" "+list_seq[0].strip()#" HEAGAWGHEE"
seq_y=" "+list_seq[1]#" PAWHEAE"
seq_file.close()

#コマンドライン引数-localの有無での場合分け
parser = argparse.ArgumentParser()
parser.add_argument('-local', action='store_true')
args = parser.parse_args()
if args.local:
        i,j,n=bioinfo_5.local_alignment(seq_x,seq_y,index,matrix_score_1)
else:
        i,j,n=bioinfo_5.global_alignment(seq_x,seq_y,index,matrix_score_1)

#結果
print("配列xの最適アラインメントは：",end="")
for p2 in reversed(range(len(j))):
        print(j[p2],end="")
print("\n")

print("配列yの最適アラインメントは：",end="")
for p1 in reversed(range(len(i))):
        print(i[p1],end="")
print("\n")

print("スコア(降順)は：",end="")

for p3 in range(len(n)):
    print(n[p3],end=" ")
    
print("\n")

    

