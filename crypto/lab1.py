import numpy as np
import string
import random
import base64

def substitute_encrypt(message, key):
    """Encrypt message using character substitution. Key is a random permutation of the 26 letters"""
    # map message to numerical array in range(0,26)
    plain = [x - ord('a') for x in map(ord,message)]
    # apply substitution according to key
    cipher = [key[x] for x in plain]
    # rewrite numerical array in uppercase letters
    cryptogram = [chr(x+ord('A')) for x in cipher]
    return ''.join(cryptogram)
    
def substitute_decrypt(cryptogram, key):
    """Decrypt cryptogram using character substitution. Key is a random permutation of the 26 letters"""
    # map cryptogram to numerical array in range(0,26)
    cipher = [x - ord('A') for x in map(ord,cryptogram)]
    # compute inverse permutation
    rev_key = np.argsort(key)
    # apply inverse substitution according to key
    plain = [rev_key[x] for x in cipher]
    # rewrite numerical array in lowercase letters
    message = [chr(x+ord('a')) for x in plain]
    return ''.join(message)


def Vigenere_encrypt(message, key):
    """Encrypt message using Vigenere algorithm. Key is a password."""
    # map message to numerical array in range(0,26)
    plain = [x - ord('a') for x in map(ord,message)]
    # map key (password) to numerical array in range(0,26)
    keynum = [x - ord('a') for x in map(ord,key)]
    # allocate empty array
    cipher = [0] * len(plain)
    i = 0
    klen = len(key)
    for k in keynum:
        # substistute one character every klen characters according to key[i]
        cipher[i::klen] = [(x + k) % 26 for x in plain[i::klen] ]
        i = i + 1
    # rewrite numerical array in uppercase letters
    cryptogram = [chr(x+ord('A')) for x in cipher]
    return ''.join(cryptogram)
    
def Vigenere_decrypt(cryptogram, key):
    """Encrypt message using Vigenere algorithm. Key is a password."""
    # map cryptogram to numerical array in range(0,26)
    cipher = [x - ord('A') for x in map(ord,cryptogram)]
    # map key (password) to numerical array in range(0,26)
    keynum = [x - ord('a') for x in map(ord,key)]
    # allocate empty array
    plain = [0] * len(cipher)
    i = 0
    klen = len(key)
    for k in keynum:
        # substistute one character every klen characters according to key[i]
        plain[i::klen] = [(x - k) % 26 for x in cipher[i::klen] ]
        i = i + 1
    # rewrite numerical array in lowercase letters
    message = [chr(x+ord('a')) for x in plain]
    return ''.join(message)
    



def monogram_ranking(cryptogram, topn=None):
    """Returns the topn most frequent monograms (letters) in cryptogram"""
    # map letters to numerical values in range(0,26)
    cipher = [x - ord('A') for x in map(ord,cryptogram)]
    # compute histogram of letter values
    freq = np.histogram(cipher, 26, (-0.5, 25.5))
    # get sorted letters in decreasing order of their frequency
    sorted_monograms = [(chr(x+ord('A')), freq[0][x]) for x in np.argsort(-freq[0])]
    return sorted_monograms[0:topn]


def digram_to_number(t, i):
    return 26*(ord(t[i]) - ord('A')) + ord(t[i+1]) - ord('A')
    
def number_to_digram(x):
    return ''.join([chr(x // 26 + ord('A')), chr(x % 26 + ord('A'))])


def digram_ranking(cryptogram, topn=None):
    """Returns the topn most frequent digrams (letter pairs) in cryptogram"""
    # map digrams to numerical values in range(0,26*26)
    digrams = [digram_to_number(cryptogram, i) for i in range(0,len(cryptogram)-1)]
    # compute histogram of digram values
    freq = np.histogram(digrams, 26*26, (-0.5, 26*26-0.5))
    # get sorted digrams in decreasing order of their frequency
    sorted_digrams = [(number_to_digram(x), freq[0][x]) for x in np.argsort(-freq[0])]
    return sorted_digrams[0:topn]
    
    
def trigram_to_number(t, i):
    return 26*26*(ord(t[i]) - ord('A')) + 26*(ord(t[i+1]) - ord('A')) + ord(t[i+2]) - ord('A')
        
def number_to_trigram(x):
    return ''.join([chr(x // (26*26) + ord('A')), chr((x % (26*26) // 26) + ord('A')), chr(x % 26 + ord('A'))])

def trigram_ranking(cryptogram, topn=None):
    """Returns the topn most frequent trigrams (letter triplets) in cryptogram"""
    # map trigrams to numerical values in range(0,26*26*26)
    trigrams = [trigram_to_number(cryptogram, i) for i in range(0,len(cryptogram)-2)]
    # compute histogram of trigram values
    freq = np.histogram(trigrams, 26*26*26, (-0.5, 26*26*26-0.5))
    # get sorted trigrams in decreasing order of their frequency
    sorted_trigrams = [(number_to_trigram(x), freq[0][x]) for x in np.argsort(-freq[0])]
    return sorted_trigrams[0:topn]
    

def crypto_freq(cryptogram):
    """Returns the relative frequencies of characters in  cryptogram"""
    # map letters to numerical values in range(0,26)
    cipher = [x - ord('A') for x in map(ord,cryptogram)]
    # compute histogram of letter values
    freq = np.histogram(cipher, 26, (-0.5, 25.5))
    # return relative frequency
    return freq[0] / len(cipher)
    
    
    
def periodic_corr(x, y):
    """Periodic correlation, implemented using the FFT. x and y must be real sequences with the same length."""
    return np.fft.ifft(np.fft.fft(x) * np.fft.fft(y).conj()).real
    
def key_len(cryptogram,length):
    subsequence = cryptogram[0::length]
    Q = crypto_freq(subsequence)
    score = sum(np.square(Q))
    return np.abs(score-0.065)<0.01
    
def crack_key (cryptogram,keylen,P):
    s=[]
    key = []
    for i in range(keylen):
        s = []
        n = 0
        # Slice the cyphertext
        s = cryptogram[i:len(cryptogram):keylen]
        # Calculate the frequence of letters
        Q = crypto_freq(s)
        
        # Select the key that fit the best with english language distribution
        key.append(np.argmax(periodic_corr(Q,P)))

    return key    
    
def main():
    # frequency of English letters in alphabetical order
    english_letter_freqs = [0.085516907,
    0.016047959,
    0.031644354,
    0.038711837,
    0.120965225,
    0.021815104,
    0.020863354,
    0.049557073,
    0.073251186,
    0.002197789,
    0.008086975,
    0.042064643,
    0.025263217,
    0.071721849,
    0.074672654,
    0.020661661,
    0.001040245,
    0.063327101,
    0.067282031,
    0.089381269,
    0.026815809,
    0.010593463,
    0.018253619,
    0.001913505,
    0.017213606,
    0.001137563]
    
    Dict_digram={'TH' : 2.71, 'EN' : 1.13, 'NG' : 0.89,
    'HE' : 2.33, 'AT' : 1.12, 'AL' : 0.88,
    'IN' : 2.03, 'ED' : 1.08, 'IT' : 0.88,
    'ER' : 1.78, 'ND' : 1.07, 'AS' : 0.87,
    'AN' : 1.61, 'TO' : 1.07, 'IS' : 0.86,
    'RE' : 1.41, 'OR' : 1.06, 'HA' : 0.83,
    'ES' : 1.32, 'EA' : 1.00, 'ET' : 0.76,
    'ON' : 1.32, 'TI' : 0.99, 'SE' : 0.73,
    'ST' : 1.25, 'AR' : 0.98, 'OU' : 0.72,
    'NT' : 1.17, 'TE' : 0.98, 'OF' : 0.71}

    Dict_trigram={'THE' : 1.81, 'ERE' : 0.31, 'HES' : 0.24,
    'AND' : 0.73, 'TIO' : 0.31, 'VER' : 0.24,
    'ING' : 0.72, 'TER' : 0.30, 'HIS' : 0.24,
    'ENT' : 0.42, 'EST' : 0.28, 'OFT' : 0.22,
    'ION' : 0.42, 'ERS' : 0.28, 'ITH' : 0.21,
    'HER' : 0.36, 'ATI' : 0.26, 'FTH' : 0.21,
    'FOR' : 0.34, 'HAT' : 0.26, 'STH' : 0.21,
    'THA' : 0.33, 'ATE' : 0.25, 'OTH' : 0.21,
    'NTH' : 0.33, 'ALL' : 0.25, 'RES' : 0.21,
    'INT' : 0.32, 'ETH' : 0.24, 'ONT' : 0.20}

#-----------------------------ES1------------------------------------------------------------    
    with open("cryptogram01.txt","r") as text_file:
        cryptogram = text_file.read()
    with open("cryptogram02.txt","r") as text_file:
        cryptogram2 = text_file.read()
    with open("cryptogram03.txt","r") as text_file:
        cryptogram3 = text_file.read()
    print(cryptogram)
    print(monogram_ranking(cryptogram, 5))
    print(digram_ranking(cryptogram, 3))
    print(trigram_ranking(cryptogram, 3))
    
    # you can write here your code for the lab and test it with "python3 AISC_01.py
    
    # Sort monograms
    
    # monograms=monogram_ranking(cryptogram, 3)
    guess01 = cryptogram
    # ind =np.argpartition(english_letter_freqs,-3)[-3:]
    # res = sorted(range(len(english_letter_freqs)), key = lambda sub: english_letter_freqs[sub], reverse=False)[-3:]
    # Dict={}
    # i=0
    # for x in reversed(res):
    #     Dict[ord(monograms[i][0])] = chr(x+ord('A'))
    #     i+=1
    # guess01 = cryptogram.translate(Dict)
    # print(cryptogram)
    # print(guess01)
    
    # Sort 
    #supponiamo che BYX sia THE
    guess01 = cryptogram.replace('BYX', 'the')
    guess01 = guess01.replace('BY', 'th')
    guess01=guess01.replace('YX','he')
    guess01 = guess01.replace('Y', 'h')
    guess01=guess01.replace('X', 'e')
    guess01=guess01.replace('B', 't')
    
    guess01=guess01.replace('T', 'a')
    
    #la consonoante più probabile era la n
    guess01=guess01.replace('J', 'n')
    
    #abbiamo beccato Ahen quindi la W ci stava bene come A
    guess01=guess01.replace('A', 'w')
    
    #abbiamo beccato weaOth quindi la O ci stava bene come L
    guess01=guess01.replace('O', 'l')
    
    # whateZeW
    guess01=guess01.replace('Z', 'v').replace('W', 'r')
    
    guess01=guess01.replace('V', 's')
    
    guess01=guess01.replace('G', 'p')
    guess01=guess01.replace('R', 'o')
    guess01=guess01.replace('D', 'u')
    guess01=guess01.replace('H', 'y')
    guess01=guess01.replace('F','d')
    guess01=guess01.replace('L','f')
    guess01=guess01.replace('U', 'b')
    guess01=guess01.replace('N', 'i')
    guess01=guess01.replace('I', 'c')
    guess01=guess01.replace('M', 'g')
    guess01=guess01.replace('S', 'm')
    guess01=guess01.replace('P', 'k')
    guess01=guess01.replace('E', 'x')

    print(guess01)
    '''
    
    '''
#-----------------Es2--------------------------------------------------
    length=1
    while (not key_len(cryptogram2,length) and length < 25 ):
        length +=1
    print(length)
    key_vig=crack_key(cryptogram2,length,english_letter_freqs)
    
    k=[]
    for x in key_vig:
        k.append(chr(x+ord('a')))
    
    print(k)
    
    listToStr = ''.join([str(elem) for elem in k])
    print(listToStr)

    print(Vigenere_decrypt(cryptogram2,listToStr.lower()))
    
# -------------------- --------------------
    length=1
    while (not key_len(cryptogram3,length) and length < 25 ):
        length +=1
    print(length)
    
    key_vig=crack_key(cryptogram3,length,english_letter_freqs)
    
    k=[]
    for x in key_vig:
        k.append(chr(x+ord('a')))
    
    print(k)
    
    listToStr = ''.join([str(elem) for elem in k])
    print(listToStr)

    #print(Vigenere_decrypt(cryptogram3,listToStr.lower()))
    res = Vigenere_decrypt(cryptogram3,listToStr.lower())
    print(res)
    
    
if __name__ == '__main__':
    main()
