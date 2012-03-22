#!/usr/bin/python -o

from __future__ import division  # Make the divisions floating point ops
import os                        # For reading directories
import re                        # For regex


# Pattern to tokenize the emails
pattern = re.compile('[^a-zA-Z0-9_\-\'!$\.]+')
# Pattern to remove attachments
patternAttachment = re.compile('Content-Disposition: attachment;.*------=_NextPart', re.DOTALL)

##
# Read the sample files and put the tokens into the word array
# index 0 for ham, 1 for spam
def read(path, words, msgCount, index):
    msgCount[index] += len(os.listdir(path))
    for filename in os.listdir(path):
        f = open(os.path.join(path, filename), 'r')
        contents = f.read()
        contents = re.sub(patternAttachment, '', contents)
        for word in re.split(pattern, contents):
            try:
                words[word][index] += 1
            except KeyError:
                # It's not set. Set it and proceed
                words[word] = [0,0]
                words[word][index] += 1

##
# The bayesian probabilities
def calculateProb(words, prob, msgCount):
    for k,v in words.items():
        # 2x weighting on good because Paul Graham suggested that               
        g, b = (v[0]*2, v[1])
        # Avoid cases that are too small
        if (g+b >= 3):
            # Note divisions are floating point due to the import
            pg = min( 1, (g/msgCount[0]))
            pb = min( 1, (b/msgCount[1]))
            prob[k] = max( .01, min( .99, pb/(pg+pb)))

##
# Test mail. Check against expected value. 
# Returns True if it got it right, False if wrong            
def testSingleMail(filename, prob, expect):

    f = open(filename, 'r')
    contents = f.read()
    contents = re.sub(patternAttachment, '', contents)
    # Dedup the tokens
    contents = set(re.split(pattern, contents))

    # Find the probabilties for all the tokens
    p = [0.5 if word not in prob else prob[word] for word in contents]

    # Sorts the tokens and takes the 15 most important tokens
    l = sorted(p, key=lambda x: abs(x-0.5), reverse=True)[:15]

    #  Probability Formula: P(a)*P(b)...P(n) / [ P(a)*P(b)..P(n) + (1-P(a))(1-P(b))...(1-P(n)) ]
    prod = reduce( lambda x, y: x*y, l, 1)
    notProd = reduce( lambda x, y: x * (1-y), l, 1)
    result = prod/(prod + notProd)

    tolerance = 0.1
    out = ((expect == 'spam' and result >= tolerance) or (expect == 'ham' and result < tolerance))
    
    # Verbose Output
    '''
    if (out == False):
        debug = [(word, prob.setdefault(word, 0.5)) for word in contents]
        for word, p in sorted(sorted(debug, key=lambda x: abs(x[1] - 0.5), reverse=True)[:15], key=lambda x: x[1]):
            print word.ljust(20) + str(p)
        print result
        print filename
        print "----"
    '''
    return out
    
# Test an entire folder; returns (wrong, total#)
def testMail(path, prob, expect):
    count = len(os.listdir(path))
    right = sum([testSingleMail(os.path.join(path, filename), prob, expect) for filename in os.listdir(path)])
    return (count-right, count)

def main():
    words = {}
    prob = {}
    msgCount = [0,0]

    print "Building index"
    read('ham', words, msgCount, 0)
    read('spam', words, msgCount, 1)

    print "Calculating Probabilities"
    calculateProb(words, prob, msgCount)

    print "Testing Mail"
    falsePos = testMail('test_ham', prob, 'ham')
    slipThrough = testMail('test_spam', prob, 'spam')
    # Lower numbers better
    print "False Positive", falsePos, (falsePos[0]/falsePos[1])*100, "%"
    # Lower numbers better BUT...
    # I reversed the percentage so higher percentage is better
    # Since it's a tradeoff between False Positives and your spam aggressiveness
    # it seemed right to optimize one and decrease the other...
    print "Slip Through/Effectiveness", slipThrough, (1-slipThrough[0]/slipThrough[1])*100, "%"

if __name__ == '__main__':
    main()
