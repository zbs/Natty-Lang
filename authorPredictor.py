'''
Created on Feb 26, 2012
New
@author: Benjamin
'''
from ngrams import *

def perplexity(text, model):
    text_freq = None
    if isinstance(text, Bigram):
        _, text_freq = text.get_frequencies()
        model.smooth()
    else:
        text_freq = text.get_frequencies()
    def log_prob(acc, bigram):
        prob = model.get_probability(bigram)
        if (prob != 0):
            return acc + text_freq[bigram] * math.log( prob )
        return acc
    product =  reduce (log_prob, text_freq, 0.0)
    if product == 0:
        return 0
    return (math.e ) ** (- product / text.get_num_tokens() )

        
#See textbook page 122
def email_prediction(train, validate, test):
        train_data = []
        with open(train) as fp:
                train_data = fp.readlines()
        #concatenate emails from same author
        author_texts = {}
        for line in train_data:
                #author is the first word, email is the rest
                author, email = line.split(' ',1)
                author = author[:-1]
                if author in author_texts:
                        author_texts[author] += email
                else:
                        author_texts[author] = email
        authors = list(author_texts.iterkeys())
        #generate unigram model for each author
        #unigram_probs = nested dict of author -> unigram -> probability
        author_unigram = {}
        for author in authors:
                author_unigram[author] = Unigram(text_string = author_texts[author])

        #read in validation or train emails
        validate_data = []
        with open(validate) as fp:
                validate_data = fp.readlines()
        test_data = []
        with open(test) as fp:
                test_data = fp.readlines()
        validate_data.extend(test_data)
        predicted_authors = []
        actual_authors = []
        print len(validate_data)
        for line in validate_data:
                actual_author, email = line.split(' ',1)
                actual_author = actual_author[:-1]
                actual_authors.append(actual_author)
                #generate unigram model on just that email and find words that occur only once (singletons)
                unigram = Unigram(text_string = email)
                frequencies = unigram.get_frequencies()
                #singletons = array of unigrams
                singletons = filter( lambda x : frequencies[x]==1, frequencies )
                singleton_unigram = Unigram(text_string = ' '.join(singletons))
                #for each author, compute perplexity of singletons
                #find author with max perplexity
                max_perplexity = -1
                max_author = None
                if unigram.get_num_tokens() == 0:
                    max_author = random.choice(authors)
                    predicted_authors.append(max_author)
                    continue
                for author in authors:
                        perplex = 0
                        if singleton_unigram.get_num_tokens() == 0:
                            perplex =  perplexity( unigram, author_unigram[author])
                        else:
                            perplex =  perplexity( singleton_unigram, author_unigram[author])
                        if (perplex > max_perplexity) :
                                max_perplexity = perplex
                                max_author = author
                predicted_authors.append(max_author)
        return actual_authors, predicted_authors




if __name__ == '__main__':
    '''
    model = Bigram(text_string = "one one one two two three.")
    text = Bigram(text_string = "one one one.")
    print perplexity(text, model)
    '''
    actual, predicted = email_prediction("train.txt", "validation.txt", "test.txt")
    submission = open("submission.csv", 'w')
    for a in predicted:
        submission.write(a + "\n")
    print "done"
    #print predicted
    #print actual
    #print reduce( lambda acc, x: acc + (x[0] == x[1]), zip(actual, predicted), 0.0) / len(actual)
    