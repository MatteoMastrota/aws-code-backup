import sys
import os
import time
import numpy as np
import matplotlib.pyplot as plt
from random import randrange, getrandbits
import random
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


global pub_key
global priv_key
# 2048-bit group of order q based on Z_p^* with p=2*q+1, p,q primes
# p, q, g as recommended in RFC 7919 for Diffie-Hellman key exchange
random.seed(30)
pDH = 0xFFFFFFFFFFFFFFFFADF85458A2BB4A9AAFDC5620273D3CF1D8B9C583CE2D3695A9E13641146433FBCC939DCE249B3EF97D2FE363630C75D8F681B202AEC4617AD3DF1ED5D5FD65612433F51F5F066ED0856365553DED1AF3B557135E7F57C935984F0C70E0E68B77E2A689DAF3EFE8721DF158A136ADE73530ACCA4F483A797ABC0AB182B324FB61D108A94BB2C8E3FBB96ADAB760D7F4681D4F42A3DE394DF4AE56EDE76372BB190B07A7C8EE0A6D709E02FCE1CDF7E2ECC03404CD28342F619172FE9CE98583FF8E4F1232EEF28183C3FE3B1B4C6FAD733BB5FCBC2EC22005C58EF1837D1683B2C6F34A26C1B2EFFA886B423861285C97FFFFFFFFFFFFFFFF

# generator of the subgroup of Z_p^* of order q
gDH = 2

qDH = 0x7FFFFFFFFFFFFFFFD6FC2A2C515DA54D57EE2B10139E9E78EC5CE2C1E7169B4AD4F09B208A3219FDE649CEE7124D9F7CBE97F1B1B1863AEC7B40D901576230BD69EF8F6AEAFEB2B09219FA8FAF83376842B1B2AA9EF68D79DAAB89AF3FABE49ACC278638707345BBF15344ED79F7F4390EF8AC509B56F39A98566527A41D3CBD5E0558C159927DB0E88454A5D96471FDDCB56D5BB06BFA340EA7A151EF1CA6FA572B76F3B1B95D8C8583D3E4770536B84F017E70E6FBF176601A0266941A17B0C8B97F4E74C2C1FFC7278919777940C1E1FF1D8DA637D6B99DDAFE5E17611002E2C778C1BE8B41D96379A51360D977FD4435A11C30942E4BFFFFFFFFFFFFFFFF

RSAKEY = []
RSAENCR = []
RSADEC= []
def encryptAESCTR(key, plaintext):
    """Encrypts plaintext using AES-CTR mode with given key
       key:       bytes-like object, should be 16, 24, or 32 bytes long
       plaintext: bytes-like object
       return iv, ciphertext as bytes-like objects
    """
    # 128-bit iv, securely generated
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CTR(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()
    return (iv, ciphertext)
    
    
def decryptAESCTR(key, iv, ciphertext):
    """Decrypts ciphertext encrypted using AES-CTR mode with given key and iv
       key:        bytes-like object, should be 16, 24, or 32 bytes long
       iv:         bytes-like object, should be 16 bytes long
       ciphertext: bytes-like object
       return plaintext as bytes-like object
    """
    cipher = Cipher(algorithms.AES(key), modes.CTR(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    return decryptor.update(ciphertext) + decryptor.finalize()
   
def millerTest(n, k=128):
    """ Test if a number is prime
        Args:
            n -- int -- the number to test
            k -- int -- the number of tests to do
        return True if n is prime
    """
    # Test if n is not even.
    # But care, 2 is prime !
    if n == 2 or n == 3:
        return True
    if n <= 1 or n % 2 == 0:
        return False
    
    # find r and s
    s = 0
    r = n - 1
    while r & 1 == 0:
        s += 1
        r //= 2
    
    # do k tests
    for _ in range(k):
        a = randrange(2, n - 1)
        x = pow(a, r, n)
        
        if x == 1 and x == n - 1:
            return True
            
        while r != n - 1:
            x = pow(x,2,n)
            r *= 2;

            if x == 1:
                return False
            if x == n - 1:
                return True
        return False
    return True    
    
def GCD(a,b):
    if a==0:
        return(b,0,1)
    else:
        g, x, y = GCD(b%a, a)
        return(g, y-(b//a)*x, x)
    
def generate_prime_candidate(length):
    """ Generate an odd integer via secure random generator
        Args:
            length -- int -- the length of the number to generate, in bits
        return an odd integer in range(sqrt(2)*2^(length-1), 2^length)
    """
    mask = (1 << length) - 1
    offs = 1.4142135623731 * (1 << (length-1))
    p = 0
    while p < offs:
        # generate big integer from random bytes
        p = int.from_bytes(os.urandom((length+7)//8), byteorder='little')
        # apply a mask to limit to length bits
        p &= mask
    # apply a mask to set LSB to 1
    p |=  1
    return p
    
    
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
    bytelen = (bitlen // 8) - 1
    mbytes = bytearray()
    for x in m:
        mbytes += x.to_bytes(bytelen, byteorder='little')
    return mbytes.rstrip(b'\x00').decode('utf-8')

def main():
    global pub_key
    global priv_key
    keylen = 1024
    start_time = time.time()  
    p = generate_prime_candidate(keylen//2)
    while not millerTest(p):
        p = generate_prime_candidate(keylen//2)
    q = generate_prime_candidate(keylen//2)
    while not millerTest(q):
        q = generate_prime_candidate(keylen//2)
    # this is not a valid RSA modulo, p and q should be tested for primality!
    N = p*q
    phiN=(p-1)*(q-1)
    
    e=random.SystemRandom().randint(2,pow(2,16)+1)
    #print(e)
    #print(e <= pow(2,16)+1)
    (g,x,y)=GCD(e,phiN)
    while g!=1:
        e=random.SystemRandom().randint(2,pow(2,16)+1)
        (g,x,y)=GCD(e,phiN)
    d=x%phiN
    pub_key=(N, e)
    priv_key=(N, d)
    #print('public key:', pub_key)
    try:
        assert N.bit_length() == keylen
    except AssertionError:
        print('N generation error:')
        print('size of N is', N.bit_length(), 'bits instead of', keylen)
        sys.exit(1)
        
    # print('p:', p)
    # print('q:', q)
    # print('N:', N)
    elapsed_time = time.time() - start_time
    print('RSA key generation time :', elapsed_time)  
    RSAKEY.append(elapsed_time)
    
    with open('text.txt') as text:
         s = text.read()
    start_time = time.time()
    m = encodeText(s, keylen)

    d = 48281073392151686696880286611050055754781823486508621672278736309419493243952837929368519109761119495593750924068187533364641091082129039222352826724430038507516706581793170258607852200229092197151964218494732036513026677586753302304617820185909532030511753128286099022598252122459216612640009076991810772229
    N = 115324745379267849984316535372748136470986963561643979992109831680584278827254991248526807755142611712985999391373451416953659000081447303953205244957966580876979815219049625719864722210654890031948259527434390360039167738839596248481302181538849741935378061316333074691527256644754225228461541509608008609333
    e = 53653    
    # print(m)
    c = []
    for x in m:
        elem = pow(x,e,N)
        c.append(elem)
    elapsed_time = time.time()-start_time
    print("RSA Encryption: ", elapsed_time)
    RSAENCR.append(elapsed_time)
    
    start_time = time.time()
    m2 = []
    for x in c:
        elem = pow(x,d,N)
        m2.append(elem)
    mex = decodeText(m, 1024)
    elapsed_time = time.time()-start_time
    print("RSA Decryption: ", elapsed_time)
    RSADEC.append(elapsed_time)
    
    # print(mex)
    #integers in m can be safely encrypted using a RSA key on keylen bits
    
    # s2 = decodeText([m], keylen)
    # print('decoded m:', s2)
    # try:
    #     assert s == s2
    # except AssertionError:
    #     print('message decoding error:')
    #     print('message is:')
    #     print(s)
    #     print('decoded message is:')
    #     print(s2)
    #     sys.exit(1)
    
    #-------------Diffie-Helmann Exchange ------------------------------------
    
    pkDH = 231496621204370508895931748857755688773955557370722566546524279241681783924615459222281328781846958709671178933550268979137824811356380142723458582689238338881602937866599482596517635627201490862987705580528580122030574292913825460656414418530301010266004326589419172467364887958500892750202983947301330827393531207626744229962720413918512823808690023548441036635272327523845223428985955360366428904878223170012768633135103661638106507748637163377957664799771569021118234716556142527020139132381453117289393367071863842364636961374713484929024198420198291374856545022707013121483896955505081060905509151197548949686
    
    #key generation
    start_time = time.time()
    x=random.SystemRandom().randint(1,qDH-1)
    # print('x: ',x)
    x = 6096599277580491408062914942366142971484245555637671382602995067619428850894894067749612145265374675031056961368306196765946783956887398130668060559966772236995969774659068547612213332179850547191704876271427295491785502137425604096296418454892350946499518961055585996348662055455531174461951111173860378709212138585212640753268991525730150836855727959142390098212816880465750083475388252585435640918758867768124048961499895880962060187562336122527614249821517483435094307334341452865913524246541061141944006282345992972839982224681072924580169208534872782708991829069676587602490905787016526963212497611809731487100
    pk = pow(gDH,x,pDH) #public key
    #print("public DH:", pk)
    elapsed_time = time.time()-start_time
    print("AES key generation", elapsed_time)
    # k = pow(pkDH,x,pDH)
    # key = (k & ((1 << 128) - 1)).to_bytes(16, byteorder='little')
    
    pkAndrea = 27075675337076813308695682812844785817571016300793864901235397796862568276861041170291345168803980172251660451734053885876162244651318851913251320447905609245942690191725812307616330237471232860337162376782693053086847524401537978807401552392300493516495747420039581073269162174055543010259750505496882108419682280603562197605904244816851467289673466753563636436632082880363296597576562511199308944973596803634935403005249885138792956547312871324214652398171391233179366580198382642252436599526372426449828907000733491248090318914485214763054514186680097719566790785823091452337869033804745673626531504390090519980107
    
    start_time = time.time()
    k = pow(pkAndrea,x,pDH)
    key = (k & ((1 << 128) - 1)).to_bytes(16, byteorder='little')
    elapsed_time = time.time()-start_time
    print("AES shared key generation", elapsed_time)
    # print("key shared: ",key)
    key_sharedAndrea = b'%\xf3B\xb5\xd4t\xaaQ\x84\xd4\x99\xa5\x0c|\x8a\xc4'
    # print("shared key: ",key == key_sharedAndrea)
    
    # s = "Somebody once told me the world is gonna roll me I aint the sharpest tool in the shed She was looking kind of dumb with her finger and her thumb In the shape of an L on her forehead Well the years start coming and they dont stop coming Fed to the rules and I hit the ground running Didnt make sense not to live for funYour brain gets smart but your head gets dumb So much to do so much to see So whats wrong with taking the back streets Youll never know if you dont go Youll never shine if you dont glow Hey now youre an allstar get your game on go play Hey now youre a rock star get the show on, get paid And all that glitters is gold Only shooting stars break the mold"
    #key = os.urandom(16)
    with open('text.txt') as text:
         s = text.read()
    plaintext = s.encode('utf-8')
    
    # first call may take longer to execute due to crypto library initializations
    start_time = time.time()
    (iv, ciphertext) = encryptAESCTR(key, plaintext)
    elapsed_time = time.time() - start_time
    print('AES encryption time (first call):', elapsed_time)
    
    start_time = time.time()
    plaintext = decryptAESCTR(key, iv, ciphertext)
    elapsed_time = time.time() - start_time
    print('AES decryption time:', elapsed_time)
    
    plaintext = s.encode('utf-8')
    # this call should be much faster
    start_time = time.time()
    (iv, ciphertext) = encryptAESCTR(key, plaintext)
    elapsed_time = time.time() - start_time
    print('AES encryption time (second call):', elapsed_time)
    
    start_time = time.time()
    plaintext = decryptAESCTR(key, iv, ciphertext)
    elapsed_time = time.time() - start_time
    print('AES decryption time:', elapsed_time)
    
    try:
        assert s == plaintext.decode('utf-8')
    except AssertionError:
        print('AES error:')
        print('message is:')
        print(s)
        print('decrypted message is:')
        print(plaintext.decode('utf-8'))
        sys.exit(1)  
    
    # first_string = base64.b64encode(iv).decode("utf-8")
    # print("first string: ", first_string)
    # second_string = base64.b64encode(ciphertext).decode("utf-8")
    # print("second string: ", second_string)

    # iv = base64.b64decode(first_string)
    # ciphertext = base64.b64decode(second_string)
    
if __name__ == '__main__':
    for i in range(1,100):
        main()
    #print("pub_key: ", pub_key)
    
    print("\n")
    #print("priv_key: ", priv_key)
#nostra public:
#    Npb = 122074716073587229414484367493460064924449453137468538631579983873163874511649689099279212539183486563700405749352012545027272667821469353810661250361220765423702433116321469136838098194259412104050769900382985540640787704393950428871605209319309283947331099429317371179427605916925970794695024623572370948133
#    e = 57833
#    Npb = pub_key[0]
#    e = pub_key[1]
#nostra private:
#    Nprv = priv_key[0]
#    d = priv_key[1]
    m = 112484326657792877299325619902141851299808698248350328288857685955127251736616710103538079067638585258859458250995929927569621534134955512954806824092892969170868518226613958028136747184917144994981403218389576978783275290248243460986990156980997596877314711888137938659883346748037779183745257038299216487825
    d = 48281073392151686696880286611050055754781823486508621672278736309419493243952837929368519109761119495593750924068187533364641091082129039222352826724430038507516706581793170258607852200229092197151964218494732036513026677586753302304617820185909532030511753128286099022598252122459216612640009076991810772229
    N = 115324745379267849984316535372748136470986963561643979992109831680584278827254991248526807755142611712985999391373451416953659000081447303953205244957966580876979815219049625719864722210654890031948259527434390360039167738839596248481302181538849741935378061316333074691527256644754225228461541509608008609333
    e = 53653
    
#    start_time = time.time()
    c = pow(m, d, N)
    mex = decodeText([c], 1024)
#    elapsed_time = time.time() - start_time
#    print('RSA decryption time :', elapsed_time)
    #print(mex)
    
#prof public key:
#N=84679728665601623534964724907925515929006540043189517481604602443064696359792213876789134073333039587280256381629121330309212710075084136072434602842735932397920567074126295940793758270599694063151970957022891161811181118800418280560581409959172714364916927401331291518944188508877716559336163266657183044021
#    e=65537

    # c = 112484326657792877299325619902141851299808698248350328288857685955127251736616710103538079067638585258859458250995929927569621534134955512954806824092892969170868518226613958028136747184917144994981403218389576978783275290248243460986990156980997596877314711888137938659883346748037779183745257038299216487825
    
    # d = 48281073392151686696880286611050055754781823486508621672278736309419493243952837929368519109761119495593750924068187533364641091082129039222352826724430038507516706581793170258607852200229092197151964218494732036513026677586753302304617820185909532030511753128286099022598252122459216612640009076991810772229
    # Npr = 115324745379267849984316535372748136470986963561643979992109831680584278827254991248526807755142611712985999391373451416953659000081447303953205244957966580876979815219049625719864722210654890031948259527434390360039167738839596248481302181538849741935378061316333074691527256644754225228461541509608008609333
    # m = pow(c,d,Nprv)
    # print(len(str(m)))
    # decryptMex = decodeText([m],1024)
    # print("decryptMex", decryptMex)
        # c = []
    # print(len(m))
    # for i in m:
    #     c.append(pow(i,e,Npb))
    # cm = int("".join(map(str, c))) 

    # with open('text.txt') as text:
    #     s = text.read()
    # #s = "Nel mezzo del cammin di nostra vita mi ritrovai per una selva oscura la cui diritta via era smarrita"
    # m = encodeText(s,1024)
    # print(len(m))
    # #if len(m)== 1:
    # #    c = pow(m,e,N)
    # # else:
    # #     c = []
    # #     for element in m:
    # #         c.append(pow(element,e,Npb))
    # #decryptMessage = decodeText([pow(c,d,N)],1024)
    # c = []
    # for x in m:
    #     elem = pow(x,e,N)
    #     c.append(elem)

    # m2 = []
    # for x in c:
    #     elem = pow(x,d,N)
    #     m2.append(elem)

    # s2 = decodeText(m2,1024) #da lista di integers a stringa
    # print("s2:", s2)
    # print(s==s2)
    # print(s2)
    
#--------- Diffie-Hellman-------------------------------------------
    # x=random.SystemRandom().randint(1,qDH-1)
    # #prof pk for DH exchange:
    # pkDH =  231496621204370508895931748857755688773955557370722566546524279241681783924615459222281328781846958709671178933550268979137824811356380142723458582689238338881602937866599482596517635627201490862987705580528580122030574292913825460656414418530301010266004326589419172467364887958500892750202983947301330827393531207626744229962720413918512823808690023548441036635272327523845223428985955360366428904878223170012768633135103661638106507748637163377957664799771569021118234716556142527020139132381453117289393367071863842364636961374713484929024198420198291374856545022707013121483896955505081060905509151197548949686
    
    # pk = pow(gDH,x,pDH)
    # k = pow(pkDH,x,pDH)
    # key = (k & ((1 << 128) - 1)).to_bytes(16, byteorder='little')
    
    plt.hist(RSAKEY,30,density=True)
    plt.xlabel('Time')
    plt.title("RSAKEY")
    plt.show()
    
    plt.hist(RSAENCR,30,density=True)
    plt.xlabel('Time')
    plt.title("RSAENCR")
    plt.show()
    
    plt.hist(RSADEC,30,density=True)
    plt.xlabel('Time')
    plt.title("RSADEC")
    plt.show()
