word = input()

n = len(word)

if n % 2 == 0:  
    mid = word[n//2 - 1 : n//2 + 1]
else:           
    mid = word[n//2]

print(mid)