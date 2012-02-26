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
		tokens_with_punct = ["."]
		for word in tokens:
			if len(word) > 1 and \
				(word[-1:] == "!"  or word[-1:] == "?" or word[-1:] == "."):
				tokens_with_punct.append(word[:-1])
				tokens_with_punct.append(word[-1:])
			else:
				tokens_with_punct.append(word)
		# Treat beginning and end of text as a beginning or end of sentence,
		# respectively
		end_token = tokens_with_punct[-1:][0]
		if end_token != "." and end_token != "!" and end_token != "?":
			tokens_with_punct.append(".")
		return tokens_with_punct
	
class Unigram():
	def __init__(self, filename=None, text_string=None):
		#Reads in text of specified file
		if filename != None:
			with open(filename) as fp:
				self.text = fp.read()
		else:
			if text_string == None:
				print "Error: Need either filename or string"
				return 
			else:
				self.text = text_string
		# self.tokens = add_sentence_markers()
		self.tokens = nltk.wordpunct_tokenize(self.text)
		self.num_words = float(len(self.tokens))
		
		self.frequencies = None
		self.unigrams = None
		
	def get_num_tokens(self):
		return self.tokens
	
	def has_tokens(self, gram):
		freqs = self.get_frequencies()
		return gram in freqs
	
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
			return self.unigrams
			
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
	
	def get_probability(self, unigram):
		probs = self.get_probabilities()
		if unigram not in probs:
			return 0
		return probs[unigram] 
		
class Bigram():
	def __init__(self, filename=None, text_string=None):
		if filename != None:
			with open(filename) as fp:
				self.text = fp.read()
		else:
			if text_string == None:
				print "Error: Need either filename or string"
				return 
			else:
				self.text = text_string
				
		self.tokens = add_sentence_markers(nltk.wordpunct_tokenize(self.text))
		self.num_words = float(len(self.tokens))
		
		self.uni_frequencies = None
		self.bi_frequencies = None
		self.bigrams = None
		
	def get_num_tokens(self):
		return len(self.tokens)
	
	def has_tokens(self, gram):
		(first, second) = gram
		(uni_freqs, bi_freqs) = self.get_frequencies()
		return first in uni_freqs and second in uni_freqs
		
	def get_frequencies(self):
		if self.uni_frequencies == None or self.bi_frequencies == None:
			# Still need to figure out beginning-of-sentence markers
			l = len(self.tokens)
			end_punct = self.tokens[-1:][0]
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
			self.uni_frequencies[(end_punct,)] -= 1.
		return (self.uni_frequencies, self.bi_frequencies)
		
	def get_probabilities(self):
		if self.bigrams != None:
			return self.bigrams
		else:
			(uni_frequencies, bi_frequencies) = self.get_frequencies()
			self.bigrams = dict()
			for (first, second) in bi_frequencies:
				self.bigrams[(first, second)] = \
					bi_frequencies[(first,second)] / uni_frequencies[(first,)]
			return self.bigrams

	def smooth(self):
		(uni_freqs, bi_freqs) = self.get_frequencies()
		for key in bi_freqs:
			bi_freqs[key] += 1.
		for key in uni_freqs:
			uni_freqs[key] += len(uni_freqs)
		self.bigrams = None
		self.get_probabilities()
		
	def get_probability(self, bigram, smoothed=False):
		(first, second) = bigram
		(uni_freqs, bi_freqs) = self.get_frequencies()
		probs = self.get_probabilities()
		if bigram not in bi_freqs and not smoothed:
			return 0.
		elif smoothed:
			# Deal with unknowns here
			if first not in uni_freqs or second not in uni_freqs:
				return 0.
			else: 
				return 1./uni_freqs[(first,)]
		return probs[bigram]
"""
b = Bigram("test_text")
b.smooth()
print b.bigrams
print b.get_probability(("twice","twice"), True)
print b.get_probability((".","once"),True)
"""