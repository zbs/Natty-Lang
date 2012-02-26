import nltk
import math
import random

filename = "../Proj1Data/test.txt"

"""
	Outstanding issues:
		- How to deal with punctuation, how to mark end of file (i.e. do we
		 	insert an end of sentence marker there?
		- Additionally, should we insert a beginning of sentence marker at the beginning
			of the file?
		- If we use markers, how do we differentiate between different types of punctuation?
"""
def add_sentence_markers(tokens):
		#Need to double-check
		tokens_with_punct = []
		for word in tokens:
			if len(word) > 1 and \
				(word[-1:] == "!"  or word[-1:] == "?" or word[-1:] == "."):
				tokens_with_punct.append(word[:-1])
				tokens_with_punct.append(word[-1:])
			else:
				tokens_with_punct.append(word)
		return tokens
	
class Unigram():
	def __init__(self, filename):
		#Reads in text of specified file
		with open(filename) as fp:
			self.file_text = fp.read()
		# self.tokens = add_sentence_markers()
		self.tokens = nltk.wordpunct_tokenize(self.file_text)
		self.num_words = float(len(self.tokens))
		
	def generate_probabilities(self):
		frequencies = dict()
		for word in self.tokens:
			if word in frequencies:
				frequencies[word] += 1.
			else:
				frequencies[word] = 1.
		self.unigrams = dict()
		for word in frequencies:
			self.unigrams[(word,)] = frequencies[word] / self.num_words
		
	def next_word(self):
		# Need to implement this using new structure
		pass
	"""
		num = random.randint(0,len(self.tokens)-1)
		next = self.tokens[num]
		return next
	"""
		
	def gen_sentence(self, sentence_length):
		pass
	"""
		sentence = ""
		for i in range(sentence_length):
			sentence += self.next_word(self)
	"""
	
class Bigram():
	def __init__(self, filename):
		with open(filename) as fp:
			self.file_text = fp.read()
		self.tokens = add_sentence_markers(nltk.wordpunct_tokenize(self.file_text))
		self.num_words = float(len(self.tokens))
		
	def generate_probabilities(self):
		# Still need to figure out beginning-of-sentence markers
		l = len(self.tokens)
		uni_frequencies = dict()
		bi_frequencies = dict()
		for i in range(l):
			unigram_token = (self.tokens[i],)
			#bigram frequencies
			if i != l-1:
				bigram_token = (self.tokens[i], self.tokens[i+1])
				if bigram_token in bi_frequencies:
					bi_frequencies[bigram_token] += 1.
				else:
					bi_frequencies[bigram_token] = 1.
					
			#unigram frequencies
			if unigram_token in uni_frequencies:
				uni_frequencies[unigram_token] += 1.
			else:
				uni_frequencies[unigram_token] = 1.
				
		self.bigrams = dict()
		for (first, second) in bi_frequencies:
			self.bigrams[(first, second)] = \
				bi_frequencies[(first,second)] / uni_frequencies[(first,)]

# OUTSTANDING ISSUE: You're supposed to compute the probability of an entire file,
# as opposed to just iterating over all the probabilities.
#compute ngram perplexity given dictionary of n-gram probabilities.
def perplexity(ngrams):
	product = reduce (lambda acc, ngram: acc + math.log( ngrams[ngram] ), ngrams.iterkeys(), 0.0)
	return math.pow(product, - math.e / len(ngrams) )
	
		