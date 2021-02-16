def mod2dec(n):
    k = n
    s=0
    r=1
    while(k%2==0):
        s+=1
        k=k/2
    r = k    
    return s,r
    
def millerRabin(n,k):
    s,r = mod2dec(n-1)
    print(n)
    
millerRabin(100,5)