d = 48281073392151686696880286611050055754781823486508621672278736309419493243952837929368519109761119495593750924068187533364641091082129039222352826724430038507516706581793170258607852200229092197151964218494732036513026677586753302304617820185909532030511753128286099022598252122459216612640009076991810772229
N = 115324745379267849984316535372748136470986963561643979992109831680584278827254991248526807755142611712985999391373451416953659000081447303953205244957966580876979815219049625719864722210654890031948259527434390360039167738839596248481302181538849741935378061316333074691527256644754225228461541509608008609333
Nprv = 115324745379267849984316535372748136470986963561643979992109831680584278827254991248526807755142611712985999391373451416953659000081447303953205244957966580876979815219049625719864722210654890031948259527434390360039167738839596248481302181538849741935378061316333074691527256644754225228461541509608008609333
e = 53653


    
def encodeText(s, bitlen):
    """Encode string s in a list of positive integers each representable with bitlen-8 bits (bitlen // 8 - 1 bytes)"""
    sbytes = bytearray(s.encode('utf-8'))
    # do not use most significant byte
    bytelen = (bitlen // 8) - 1
    m = []
    while len(sbytes) > bytelen:
        m.append(int.from_bytes(sbytes[:bytelen], byteorder='little'))
        sbytes[:bytelen] = []
    m.append(int.from_bytes(sbytes, byteorder='little'))
    return m
    
    
def decodeText(m, bitlen):
    """Decode a list of positive integers each representable with bitlen-8 bits (bitlen // 8 - 1 bytes) into a string s.
        Ensures decodeText(encodeText(s, bitlen), bitlen) == s"""
    # do not use most significant byte
    bytelen = (bitlen // 8)-1
    mbytes = bytearray()
    for x in m:
        print(bytelen)
        mbytes += x.to_bytes(bytelen, byteorder='little')
    return mbytes.rstrip(b'\x00').decode('utf-8')
prof = 50236244617004765431134295697677724733072421259838833190405206094290537025879502333248277221612844908634768889518130997419940771939187626137829111374689882653047812701948130932353054681965709035931750073611203987229361677571565082216770080333201030736628747149477725228669927608193869043153406762396572806945

s = "supercalifragilistichespidalidososupercalifragilistichespidalidososupercalifragilistichespidalidososupercalifragilistichespidalidososupercalifragilistichespidalidososupercalifragilistichespidalidososupercalifragilistichespidalidososupercalifragilistichespidalidoso"
m = encodeText(s,1024) #da stringa a lista di integers
print("m", len(m))
c = []
for x in m:
    print("bit: ", x.bit_length())
    c.append(pow(x,e,N))
    print("POST pow encr: ",pow(x,e,N).bit_length())

m2 = []
for x in c:
    m2.append(pow(x,d,N))
    print("Post pow per decifrare: ",pow(x,d,N).bit_length())

s2 = decodeText(m2,1024) #da lista di integers a stringa
print("m2", s2)
print(s==s2)




# print(pow(prof,d,N).bit_length())
# # b = int(string[1015:])
# a = prof%1000
# print(a.bit_length())
ma = pow(prof,d,N)
# # mb = pow(b,d,N)
# print(ma.bit_length())
m = [ma]#,mb]

print(decodeText(m,1024))







# string = str(prof)
# flag = False
# i = 0
m = []
# while flag != True:
#     i+=1
#     print(int(string[0:i]))
#     if i == 10:
#         print(int(string[0:i]).bit_length())
#         o=1/0
#     try:
#         if int(string[0:i]).bit_length() == 1015:
#             m.append(pow(int(string[0:i]),d,N))
#             string = string[i:]
#     except IndexError:
#         s = decodeText(m,1024)
#         print(s)