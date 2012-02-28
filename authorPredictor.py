'''
Created on Feb 26, 2012
New
@author: Benjamin Jaeger
'''
from ngrams import *
import string

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
        #-14 found from cross validation - this case only occurs for email author
        # prediction and not if smooth bigram probabilities are used.
        return acc + (text_freq[bigram] * -14)
    product =  reduce (log_prob, text_freq, 0.0)
    if product == 0:
        return 0
    return (math.e ) ** (- product / text.get_num_tokens() )

        
#See textbook page 122
def email_prediction (train, validate, test, farmer_correction = False, remove_punctuation = False, use_singletons = False, kaggle= False):
        train_data = []
        with open(train) as fp:
                train_data = fp.readlines()
        #concatenate emails from same author
        author_texts = {}
        avg_length = {}
        author_numer = {}
        for line in train_data:
                #author is the first word, email is the rest
                author, email = line.split(' ',1)
                
                author = author[:-1]
                for c in string.punctuation:
                    if (not c in [".", "?", "!"]) and remove_punctuation:
                        email = email.replace(c," ")
                if author in author_texts:
                    author_numer[author] += 1
                    author_texts[author] += email
                else:
                    author_texts[author] = email
                    author_numer[author] = 1
        authors = list(author_texts.iterkeys())
        #generate unigram model for each author
        #unigram_probs = nested dict of author -> unigram -> probability
        author_unigram = {}
        for author in authors:
                author_unigram[author] = Unigram(text_string = author_texts[author])
                avg_length[author] = author_unigram[author].get_num_tokens() / float(author_numer[author])
        #read in validation or train emails
        validate_data = []
        with open(validate) as fp:
                validate_data = fp.readlines()
        test_data = []
        with open(test) as fp:
                test_data = fp.readlines()
        if kaggle:
            validate_data.extend(test_data)
        predicted_authors = []
        actual_authors = []
        for line in validate_data:
                actual_author, email = line.split(' ',1)
                actual_author = actual_author[:-1]
                for c in string.punctuation:
                    if (not c in [".", "?", "!"]) and remove_punctuation:
                        email = email.replace(c," ")
                actual_authors.append(actual_author)
                #generate unigram model on just that email and find words that occur only once (singletons)
                unigram = Unigram(text_string = email)
                frequencies = unigram.get_frequencies()
                #singletons = array of unigrams
                if use_singletons:
                    singletons = filter( lambda x : frequencies[x]==1, frequencies )
                else:
                    singletons = filter( lambda x : True, frequencies )
                singleton_unigram = Unigram(text_string = ' '.join(singletons))
                #for each author, compute perplexity of singletons
                #find author with max perplexity
                max_perplexity = 1000000000
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
                            if (author == "farmer-d") and farmer_correction:
                                perplex *= .95
                        
                        if (perplex < max_perplexity) :
                                max_perplexity = perplex
                                max_author = author
                predicted_authors.append(max_author)
        #compute average f_measure
        f_sum = 0.
        for author in authors:
            tp, fp, fn, tn = 0.,0.,0.,0.
            for i in range(len(actual_authors)):
                if actual_authors[i] == predicted_authors[i] and author == actual_authors[i]:
                    tp += 1
                elif predicted_authors[i] == author and actual_authors[i] != predicted_authors[i]:
                    fp +=1
                elif actual_authors[i] == author and author != actual_authors[i]:
                    fn +=1
                elif actual_authors[i] != author and author != actual_authors[i]:
                    tn +=1
            precision = tp / (tp + fp)
            recall = tp / (tp + fn)
            f_sum += 2 * precision * recall / (precision + recall)
        if not kaggle:
            print "f-measure = " + str(f_sum/len(authors))
            print "Accuracy = " + str (reduce( lambda acc, x: acc + (x[0] == x[1]), zip(actual_authors, predicted_authors), 0.0) / len(actual_authors))
        else:
            submission = open("submission.csv", 'w')
            for a in predicted_authors:
                submission.write(a + "\n")
        print "done"

if __name__ == '__main__':
    email_prediction("train.txt", "validation.txt", "test.txt")
    
        
    