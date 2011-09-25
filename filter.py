#!/usr/bin/python -o
from __future__ import division
import os
import re

words = {}
rootWords = {}
prob = {}
rootProb = {}
msgCount = [0,0]

pattern = '[^a-zA-Z0-9_\-\'!$\.]+'

def read(path, dest, index):
    for filename in os.listdir(path):
        msgCount[index] += 1
        f = open(os.path.join(path, filename), 'r')
        for word in re.split(pattern, f.read()):
            try:
                dest[word][index] += 1
            except:
                dest[word] = [0,0]
                dest[word][index] += 1
                
def calculateProb():
    for k,v in words.items():
        g, b = (v[0]*2, v[1])
        if (g+b >= 3):
            pg = min( 1, (g/msgCount[0]))
            pb = min( 1, (b/msgCount[1]))
            prob[k] = max( .01, min( .99, pb/(pg+pb)))

def testSingleMail(filename, prob, expect):

    f = open(filename, 'r')
    contents = set(re.split(pattern, f.read()))

    p = [prob.setdefault(word, 0.5) for word in contents]

    l = sorted(p, key=lambda x: abs(x-0.5), reverse=True)[:15]
    prod = reduce( lambda x, y: x*y, l, 1)
    notProd = reduce( lambda x, y: x * (1-y), l, 1)
    result = prod/(prod + notProd)
    tolerance = 0.9

    if (expect == 'spam' and result < tolerance) or (expect == 
'ham' and result >= tolerance):
        '''
        debug = [(word, prob.setdefault(word, 0.5)) for word in contents]
        for word, p in sorted(sorted(debug, key=lambda x: abs(x[1] - 0.5), reverse=True)[:15], key=lambda x: x[1]):
            print word.ljust(20) + str(p)
        print result
        print filename
        print "----"
        '''
        return False
    else:
        return True
        
def testMail(path, prob, expect):
    count = len(os.listdir(path))
    right = sum([testSingleMail(os.path.join(path, filename), prob, expect) for filename in os.listdir(path)])
    wrong = count - right
    return (wrong, count)


read('ham', words, 0)
read('spam', words, 1)
calculateProb()

falsePos = testMail('test_ham', prob, 'ham')
slipThrough = testMail('test_spam', prob, 'spam')

print "False Positive", falsePos, (falsePos[0]/falsePos[1])*100, "%"
print "Slip Through", slipThrough, (1-slipThrough[0]/slipThrough[1])*100, "%"

