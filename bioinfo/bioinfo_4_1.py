seq_file=open("seq_file.txt","r")
list_seq=seq_file.readlines()
seq_x=" "+list_seq[0].strip()#" gaattc"
seq_y=" "+list_seq[1]#" gatta"
seq_file.close()

import bioinfo_4

i,j,s=bioinfo_4.alignment(seq_x,seq_y)

print("配列xの最適アラインメントは：",end="")
for p2 in reversed(range(len(j))):
        print(j[p2],end="")
print("\n")

print("配列yの最適アラインメントは：",end="")
for p1 in reversed(range(len(i))):
        print(i[p1],end="")
print("\n")

print("スコア(降順)は：",end="")

for p3 in range(len(s)):
    print(s[p3],end=" ")
    
print("\n")

    
