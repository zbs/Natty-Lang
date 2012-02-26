import random, math, nltk

filename = "../Proj1Data/test.txt"

def add_sentence_markers(tokens):
		for i in range(len(tokens)):
			#Need to implement cuz zach is stupid and cant remember this
			pass

class Unigram():
	def __init__(self, filename):
		with open(filename) as fp:
			self.file_text = fp.read()
		self.tokens = nltk.wordpunct_tokenize(self.file_text)
	
	def next_word(self):
		num = random.randint(0,len(self.tokens)-1)
		next = tokens[num]
		return next
		
	def gen_sentence(self, sentence_length):
		sentence = ""
		for i in range(sentence_length):
			sentence += next_word(self)
	
class Bigram():
	def __init__(self, filename):
		with open(filename) as fp:
			self.file_text = fp.read()
		self.tokens = add_sentence_markers(nltk.wordpunct_tokenize(self.file_text))
			
	def generate_frequencies(self):
		# Still need to figure out beginning-of-sentence markers
		l = len(self.tokens)
		unigrams = dict()
		bigrams = dict()
		for i in range(l):
			unigram_token = (self.tokens[i],)
			#bigram generation
			if i != l-1:
				bigram_token = (self.tokens[i],self.tokens[i+1])
				if bigrams[bigram_token]:
					bigrams[bigram_token] += 1
				else:
					bigrams[bigram_token] = 0
					
			#unigram generation
			if unigrams[unigram_token]:
				unigrams[unigram_token] += 1
			else:
				unigrams[unigram_token] = 0
				
		self.unigrams = unigrams
		self.bigrams = bigrams

	def generate_table(self):
		pass
	
def perplexity(ngrams):
	product = reduce (lambda acc, ngram: acc + math.log( ngrams[ngram] ), ngrams.iterkeys(), 0.0)
	return math.pow(product, - math.e / len(ngrams) )
	