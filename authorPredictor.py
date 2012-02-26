'''
Created on Feb 26, 2012

@author: Benjamin
'''
import math, ngrams

def perplexity(ngrams_text, ngrams_model):
    product = reduce (lambda acc, ngram: acc + ngrams_text[ngram] * math.log( ngrams_model[ngram] ), ngrams_text.iterkeys(), 0.0)
    return math.pow(product, - math.e / len(ngrams) )
    
    
#See textbook page 122
def email_prediction(filename):
        train_data = []
        with open(filename) as fp:
                train_data = file.readlines()
        #concatenate emails from same author
        author_texts = {}
        for line in train_data:
                #author is the first word, email is the rest
                author, email = line.split(' ',1)
                if author in author_texts:
                        author_texts[author] += email
                else:
                        author_texts[author] = email
        #generate unigram model for each author
        #unigram_probs = nested dict of author -> unigram -> probability
        unigrams_probs = {}
        for author in author_texts.iterkeys():
                unigrams = Unigram(author_texts[author])
                unigrams_probs[author] = unigrams.getProb()

        #read in validation or train emails
        validate_data = []
        with open(filename) as fp:
                validate_data = file.readlines()

        predicted_author = []
        for line in validate_data:
                _, email = line.split(' ',1)
                #generate unigram model on just that email and find words that occur only once (singletons)
                unigrams = Unigram(email)
                #singletons = array of unigrams
                singletons = filter( lambda x : unigrams[x]==1, unigrams.getFreq() )
                #for each author, compute perplexity of singletons
                #find author with max perplexity
                max_perplexity = 0
                max_author = None
                for author in author_texts.iterkeys():
                        #find the probabilities (in the known author text) of the singletons (in the unknown text)
                        singleton_probs = {}
                        for singleton in singletons:
                                singleton_probs[singleton] = unigrams_probs[author][singleton];
                        perplexity =  perplexity(singleton_probs)
                        if (perplexity > max_perplexity) :
                                max_perplexity = perplexity
                                max_author = author
                predicted_author.append(max_author)
        return predicted_author




if __name__ == '__main__':
    pass