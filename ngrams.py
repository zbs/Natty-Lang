import nltk, math, random

filename = "../Proj1Data/test.txt"

"""
	Perform unigram smoothing
"""

def is_punct(char):
    return char == "!" or char == "?" or char == "."

def split_punct(tokens, tokens_with_punct=[]):
	for word in tokens:
		if len(word) > 1 and \
			(word[-1:] == "!"  or word[-1:] == "?" or word[-1:] == "."):
			tokens_with_punct.append(word[:-1])
			tokens_with_punct.append(word[-1:])
		else:
			tokens_with_punct.append(word)
	return tokens_with_punct

def add_sentence_markers(tokens):
	#Need to double-check
	tokens_with_punct = split_punct(tokens, ["."])
	# Treat beginning and end of text as a beginning or end of sentence,
	# respectively
	end_token = tokens_with_punct[-1:][0]
	if end_token != "." and end_token != "!" and end_token != "?":
		tokens_with_punct.append(".")
	return tokens_with_punct

def create_unks(tokens):
	encountered_words = set()
	for i in range(0, len(tokens)):
		word = tokens[i]
		if word not in encountered_words:
			tokens[i] = "<UNK>"
		encountered_words.add(word)
	return tokens

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
		self.tokens = create_unks(split_punct(nltk.wordpunct_tokenize(self.text)))
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
				self.unigrams[word] = frequencies[word] / self.num_words
			return self.unigrams
			
	def next_word(self):
		ran = random.uniform(0,1)
		uni_freqs = self.get_frequencies()
		for word in uni_freqs: 
			ran -= self.get_probability(word)
			if ran <= 0:
				return word
		return "ERROR"
	"""
		num = random.randint(0,len(self.tokens)-1)
		next = self.tokens[num]
		return next
	"""
		
	def generate_sentence(self):
		cur_word = self.next_word()
		sentence = ""
		while not is_punct(cur_word):
			sentence += cur_word + " "
			cur_word = self.next_word()
		return sentence[:-1] + cur_word
	"""
		sentence = ""
		for i in range(sentence_length):
			sentence += self.next_word(self)
	"""
	
	def get_probability(self, unigram):
		probs = self.get_probabilities()
		if unigram not in probs:
			return probs["<UNK>"]
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
				
		self.tokens = create_unks(add_sentence_markers(nltk.wordpunct_tokenize(self.text)))
		self.num_words = float(len(self.tokens))
		self.smoothed = False
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
		self.smoothed = True
	
	#Smooth with Good-Turing	
	def gt_smooth(self):
		pass
	
	def get_probability(self, bigram):
		(first, second) = bigram
		(uni_freqs, bi_freqs) = self.get_frequencies()
		probs = self.get_probabilities()
		# Deal with unknowns here
		if (first,) not in uni_freqs or (second,) not in uni_freqs:
			if (first,) not in uni_freqs and (second,) in uni_freqs:
				return self.get_probability(("<UNK>", second))
			elif (first,) in uni_freqs and (second,) not in uni_freqs:
				return self.get_probability((first, "<UNK>"))
			else:
				return self.get_probability(("<UNK>", "<UNK>"))
		elif bigram not in bi_freqs and not self.smoothed:
			return 0.
		elif bigram not in bi_freqs and self.smoothed:
			return 1./uni_freqs[(first,)]
		else:
			return probs[bigram]
	
	def next_word(self, prev_word):
		ran = random.uniform(0,1)
		(uni_freqs, bi_freqs) = self.get_frequencies()
		for (word,) in uni_freqs: 
			ran -= self.get_probability((prev_word, word))
			if ran <= 0:
				return word
		return "ERROR"
		
	def generate_sentence(self):
		cur_word = self.next_word(".")
		sentence = ""
		while not is_punct(cur_word):
			sentence += cur_word + " "
			cur_word = self.next_word(cur_word)
		return sentence[:-1] + cur_word
		

#b = Bigram(filename="test_text")
#print b.tokens
#b.smooth()
"""
summ = 0.
for (word,) in b.uni_frequencies:
    summ += b.get_probability((word,"."))
print summ"""
#print b.generate_sentence()
"""
print b.bigrams
print b.get_probability(("twice","twice"), True)
print b.get_probability((".","once"),True)
"""
