import hashlib
import os
import secrets
import random


     
aU = int.from_bytes(b"it is the constant a", byteorder='little')
bU = int.from_bytes(b"it is the constant b", byteorder='big')


# sample DSA parameters for 1024-bit key from RFC 6979

pDSA = 0x86F5CA03DCFEB225063FF830A0C769B9DD9D6153AD91D7CE27F787C43278B447E6533B86B18BED6E8A48B784A14C252C5BE0DBF60B86D6385BD2F12FB763ED8873ABFD3F5BA2E0A8C0A59082EAC056935E529DAF7C610467899C77ADEDFC846C881870B7B19B2B58F9BE0521A17002E3BDD6B86685EE90B3D9A1B02B782B1779

qDSA = 0x996F967F6C8E388D9E28D01E205FBA957A5698B1

gDSA = 0x07B0F92546150B62514BB771E2A0C0CE387F03BDA6C56B505209FF25FD3C133D89BBCD97E904E09114D9A7DEFDEADFC9078EA544D2E401AEECC40BB9FBBF78FD87995A10A1C27CB7789B594BA7EFB5C4326A9FE59A070E136DB77175464ADCA417BE5DCE2F40D10A46A3A3943F26AB7FD9C0398FF8C76EE0A56826A8A88F1DBD



def egcd(a, b):
    """computes g, x, y such that g = GCD(a, b) and x*a + y*b = g"""
    if a == 0:
        return (b, 0, 1)
    else:
        g, x, y = egcd(b % a, a)
        return (g, y - (b // a) * x, x)

def modinv(a, m):
    """computes a^(-1) mod m"""
    g, x, y = egcd(a % m, m)
    if g != 1:
        raise Exception('modular inverse does not exist')
    else:
        return x % m

def hashDigest(message,nBytes=32):
    # if type(message) != bytes:
    #     message = message.to_bytes(32,'big')
    m = hashlib.sha256()
    m.update(message)
    hash = m.digest()
    return hash[:nBytes]
    
def collisionDetect(H,nBits=32*8,outLength=2):
    size = int(nBits/8+1)
    x0 = bytearray(random.getrandbits(8) for _ in range(size))
    
    outputLength = outLength
    C1 = 0
    C2 = 0
    x1 = H(x0,outputLength)
    x2 = H(x1,outputLength)
    while x1!=x2:
        C1+=1
        x1 = H(x1,outputLength)
        x2 = H(H(x2,outputLength),outputLength)
    print('C1: ',C1)
    x1 = x0
    while H(x1,outputLength) != H(x2,outputLength):
        C2 +=1
        x1 = H(x1,outputLength)
        x2 = H(x2,outputLength)
    
    print('C2: ',C2)
    return x1, x2

def univHash(message,nBytes=20):
    # print(message)
    m = int.from_bytes(message, byteorder='big')
    # print('m', m)
    h = (aU*m+bU) %qDSA
    #print('h',h)
    hash = h.to_bytes(20, byteorder='big')
    #print('hash', hash)
    uhash = hash[:nBytes] #solo 20 bytes in uscita
    #print('r',r)
    return uhash

def reverseHash(hashMessage):
    n=0
    h = int.from_bytes(hashMessage,byteorder='big')
    somma = pow(h%qDSA,1,qDSA)
    print("h :", h==somma)
    s = pow(somma-bU,1,qDSA)
    m=pow(s*modinv(aU,qDSA),1,qDSA)
    print("Byte length of m: ",(m.bit_length()+7)//8)
    m = m.to_bytes(20,byteorder='big')
    print("Hash message reversed successfully: ",hashMessage == univHash(m,20))
    #x = aU* int.from_bytes(m, byteorder='big')
    #m2=0
    #while univHash(m2.to_bytes(20,byteorder='big'),20) != univHash(m,20):
    #    m2 = (x+n*qDSA)//aU
    #    n+=1
    #print("m1: ",m)
    #print("m2: ",m2.to_bytes(20,byteorder='big'))
    #print("Collision detected: ",univHash(m2.to_bytes(20,byteorder='big'),20) == univHash(m,20)
    return m


def SchnorrSignature(message,privKey):
    k=0
    while k==0:
        k = secrets.randbelow(qDSA)
    I = pow(gDSA,k,pDSA)
    
    nbytes = (pDSA.bit_length()+7)//8
    I_bytes = I.to_bytes(nbytes,byteorder='big')
    # message = message.
    r = int.from_bytes(hashDigest(I_bytes+message),byteorder='big')%qDSA
    s = (k-r*privKey)%qDSA
    #print('r: ',r, 's',s)
    return r,s
    
def verifySignature(r,s,pubKey,message):
    g_s = pow(gDSA,s,pDSA)

    y_r = pow(pubKey,r,pDSA)
    # print(g_s*y_r)
    nbytes = (pDSA.bit_length()+7)//8
    I = pow(g_s*y_r,1,pDSA).to_bytes(nbytes,byteorder='big')
    # I = (g^s*pubKey^r)%p
    r1 = int.from_bytes(hashDigest(I+message),byteorder='big')%qDSA
    return r1==r

def SchnorrSignatureDummy(message,privKey):
    k=0
    while k==0:
        k = secrets.randbelow(qDSA)
    I = pow(gDSA,k,pDSA)
    
    nbytes = (pDSA.bit_length()+7)//8
    I_bytes = I.to_bytes(nbytes,byteorder='big')
    # message = message.
    r = int.from_bytes(univHash(I_bytes+message),byteorder='big')%qDSA
    s = (k-r*privKey)%qDSA
    # print('r: ',r, 's',s)
    return r,s
    
def verifySignatureDummy(r,s,pubKey,message):
    g_s = pow(gDSA,s,pDSA)
    y_r = pow(pubKey,r,pDSA)

    nbytes = (pDSA.bit_length()+7)//8
    I = pow(g_s*y_r,1,pDSA).to_bytes(nbytes,byteorder='big')

    r1 = int.from_bytes(univHash(I+message),byteorder='big')%qDSA
    return r1==r

def forgePrivate(m0,r0,s0,m1,r1,s1,y_prof):
    S = s1 - s0
    R = r0 - r1

    for K in range(1,101):
        somma=pow(S%qDSA,1,qDSA)
        # print(somma==S)
        s=pow(somma-K,1,qDSA)
        x=pow(s*modinv(R,qDSA),1,qDSA)
        y = pow(gDSA,x,pDSA)
        # if y==y_prof:
        #     print("TROVATA ",K)
        #     return
        r, s = SchnorrSignature(m1,x)
        if verifySignature(r,s,y_prof,m1):
            print("Trovata")
            return x

    
def main():
    # First message
    m0 =  b'first message'
    r0 = 299969984114895304388954029424480730263471439206
    s0 = 192417049713099740312922361446986628497439105550
    # Second message
    m1 =  b'second message'
    r1 = 719970963765961216949252326232207427282652913363
    s1 = 107425968460827725118970802806887322358870342520
    # Instructor public key
    y_prof = 42276637486569720268071647368550139276503521977640661888834825275517477780979914414339836061961635727800848465170706694019279805873893995587354694642526839889426158621140802827015533730771103146644607587713359225607432856473853326971226628964711099095487586928079612107255097386799478803704960241864601625828
   
    print('(p-1) mod q:', (pDSA - 1) % qDSA)
    nBytes = 32
    nBits = nBytes *8
    
    message = b"SHA-256 is a cryptographic hash function"
    
    hash = hashDigest(message,nBytes)
    uhash = univHash(message,20)
    print('universal hash - 20bytes: ', uhash)
    print('message', message)
    print('reversed', reverseHash(uhash))
    print("Collision detected: ", message != reverseHash(uhash))
    
    x1,x2 = collisionDetect(hashDigest)
    ux1, ux2 = collisionDetect(univHash,20*8,2)
    
    print(x1)
    print(x2)
    print('hash of', message, 'is:', hash)
    print('32 bit hash is:', hash[:4])
    print('64 bit hash is:', hash[:8])
    reverseHash(uhash)
   
    # privateKey
    x=0
    while x==0:
        x = secrets.randbelow(qDSA)
    #public key
    print("\nprivate key: ",x)
    y = pow(gDSA,x,pDSA)
    hashMessage = hashDigest(message)
    r,s = SchnorrSignature(message,x)
    print("Original message signature: ",verifySignature(r,s,y,message))
    message = b"SHA-256 is a cryptographic bash function"
    print("Slight change in message, signature: ",verifySignature(r,s,y,message))
    
    forgePrivate(m0,r0,s0,m1,r1,s1,y_prof)
    
if __name__ == '__main__':
    public=  94683834070487246567469448609658000375412355454305732010462889580989237198722554944255217769536274250905031065519993633546824538850209524983278322734472822232653926625690366824794113874951493149500261555684874246547781989696634463241262825940578919405600327759130262007849420359540154167460684980441338039574
    r= 54993604217615568840085873112253490730062845672
    s=  559584078731918110127823077111182523368642773078
    message= b"Hello, we are the group number 2"   

    print("Autentico? ",verifySignature(r,s,public,message))
    main()
# First message
m0 =  b'first message'
r0 = 299969984114895304388954029424480730263471439206
s0 = 192417049713099740312922361446986628497439105550
# Second message
m1 =  b'second message'
r1 = 719970963765961216949252326232207427282652913363
s1 = 107425968460827725118970802806887322358870342520
# Instructor public key
y = 42276637486569720268071647368550139276503521977640661888834825275517477780979914414339836061961635727800848465170706694019279805873893995587354694642526839889426158621140802827015533730771103146644607587713359225607432856473853326971226628964711099095487586928079612107255097386799478803704960241864601625828

# def conquere_world(s1_prof, s2_prof, r1_prof, r2_prof, message1_prof, public_key_prof):
#     S = s2_prof - s1_prof
#     R = r1_prof - r2_prof

#     for K in range(1,101):
#         somma=pow(S%qDSA,1,qDSA)
#         s=pow(somma-K,1,qDSA)
#         x=pow(s*modinv(R,qDSA),1,qDSA)
#         r, s = schnorr_sign(x, message1_prof)
#         if schnorr_sign_verify(public_key_prof,message1_prof,r, s):
#             return x