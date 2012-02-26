import nltk, math, random

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
		# Treat beginning and end of text as a beginning or end of sentence,
		# respectively
		#if tokens_with_punct[:-1] != ".":
		#	tokens_with_punct.append(".")
		return tokens_with_punct
	
class Unigram():
	def __init__(self, filename):
		#Reads in text of specified file
		with open(filename) as fp:
			self.file_text = fp.read()
		# self.tokens = add_sentence_markers()
		self.tokens = nltk.wordpunct_tokenize(self.file_text)
		self.num_words = float(len(self.tokens))
		
		self.frequencies = None
		self.unigrams = None
	

			
	def generate_probabilities(self):
		
		self.unigrams = dict()
		for word in self.frequencies:
			self.unigrams[(word,)] = self.frequencies[word] / self.num_words
	
	def get_frequencies(self):
		if self.frequencies != None:
			return self.frequencies
		else:
			self.frequencies = dict()
		for word in self.tokens:
			if word in self.frequencies:
				self.frequencies[word] += 1.
			else:
				self.frequencies[word] = 1.
			return self.frequencies
	
	def get_probabilities(self):
		if self.unigrams != None:
			return self.unigrams
		else:
			frequencies = self.get_frequencies()
			self.unigrams = dict()
			for word in frequencies:
				self.unigrams[(word,)] = frequencies[word] / self.num_words
	
	def get_num_tokens(self):
		return len(self.tokens)
			
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
		
		self.uni_frequencies = None
		self.bi_frequencies = None
		self.bigrams = None
		
	def get_frequencies(self):
		if self.uni_frequencies == None or self.bi_frequencies == None:
			# Still need to figure out beginning-of-sentence markers
			l = len(self.tokens)
			self.uni_frequencies = dict()
			self.bi_frequencies = dict()
			# Disregard final period
			for i in range(l):
				unigram_token = (self.tokens[i],)
				if(i != l-1):
					#bigram frequencies
					bigram_token = (self.tokens[i], self.tokens[i+1])
					if bigram_token in self.bi_frequencies:
						self.bi_frequencies[bigram_token] += 1.
					else:
						self.bi_frequencies[bigram_token] = 1.
						
				#unigram frequencies
				if unigram_token in self.uni_frequencies:
					self.uni_frequencies[unigram_token] += 1.
				else:
					self.uni_frequencies[unigram_token] = 1.
		
		return (self.uni_frequencies, self.bi_frequencies)
	
	def get_num_tokens(self):
		return len(self.tokens)
		
	def generate_probabilities(self):
		if self.bigrams != None:
			return self.bigrams
		else:
			if self.uni_frequencies == None or self.bi_frequencies == None:
				(uni_frequencies, bi_frequencies) = self.get_frequencies()
			self.bigrams = dict()
			for (first, second) in bi_frequencies:
				self.bigrams[(first, second)] = \
					bi_frequencies[(first,second)] / uni_frequencies[(first,)]

u = Bigram("test_text")
u.generate_probabilities()
print u.bigrams