import nltk, math, random

#filename = "../Proj1Data/test.txt"

"""
	Perform unigram smoothing
"""

NONE = 0
LAPLACE = 1
GOOD_TURING = 2

def is_punct(char):
	return char == "!" or char == "?" or char == "."

def tokenize(string):
	return nltk.regexp_tokenize(string, pattern='\w+|\$[\d\.]+|\S+') 

def add_sentence_markers(tokens):
	# Treat beginning and end of text as a beginning or end of sentence,
	# respectively
	if len(tokens) == 0:
		#print "empty tokens"
		return tokens + ["."]
	end_token = tokens[-1:][0]
	if end_token != "." and end_token != "!" and end_token != "?":
		tokens.append(".")
	return ["."] + tokens

def create_unks(tokens):
	encountered_words = set()
	for i in range(0, len(tokens)):
		word = tokens[i]
		if word not in encountered_words:
			tokens[i] = "<UNK>"
		encountered_words.add(word)
	return tokens

# Note: for Unigram smoothing, do ( C(w) + 1 ) / (N + V), where N = number of tokens
# and v = number of wordtypes 
class Unigram():
	def __init__(self, filename=None, text_string=None, unk=False, smoothed=False):
		self.smoothed = True
		#Reads in text of specified file
		self.unk = True
		if filename != None:
			with open(filename) as fp:
				self.text = fp.read()
		else:
			if text_string == None:
				print "Error: Need either filename or string"
				return 
			else:
				self.text = text_string
		self.tokens = add_sentence_markers(tokenize(self.text))
		if self.unk:
			self.tokens = create_unks(self.tokens)
		self.num_words = float(len(self.tokens))
		
		self.frequencies = None
		self.unigrams = None
		
	def get_num_tokens(self):
		return len(self.tokens)
	
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
					if self.smoothed:
						self.frequencies[word] = 2.
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
				if self.smoothed:
					self.unigrams[word] = frequencies[word] / (self.num_words + len(self.frequencies))
				else:
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

	def generate_sentence(self):
		cur_word = self.next_word()
		sentence = ""
		while not is_punct(cur_word):
			sentence += cur_word + " "
			cur_word = self.next_word()
		return sentence[:-1] + cur_word

	def get_probability(self, unigram):
		probs = self.get_probabilities()
		if unigram not in probs:
			if self.unk:
				return probs["<UNK>"]
			return 0. 
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
				
		self.tokens = create_unks(add_sentence_markers(tokenize(self.text)))
		self.num_words = float(len(self.tokens))
		self.smoothed = NONE
		
		# Adjusted counts using Good-Turing discounting
		self.adjusted_bigram_counts = None
		self.adjusted_unigram_counts = None
		
		# Unsmoothed frequencies
		self.uni_frequencies = None
		self.bi_frequencies = None
		
		#Probabilities
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
		self.smoothed = LAPLACE
	
	
	def guess_freq(self, freq_dict,f,max):
		#we know freq_dict[f-1] exists by the order of filling freq_dict
		left = (f-1,freq_dict[f-1])
		while f <= max:
			f += 1
			if f in freq_dict:
				right = (f,freq_dict[f])
		return left[1] + (right[1] - left[1])/(right[0]-left[0])
			
	
	def get_good_turing_counts(self,freqs):
		self.smoothed = GOOD_TURING
		freq_dict = dict()
		max_freq = 0
		#initialize freq_vector with known bigrams
		for bigram in freqs:
			f = freqs[bigram]
			if f > max_freq:
				max_freq = f
			if f in freq_dict:
				freq_dict[f] += 1.
			else:
				freq_dict[f] = 1.
		#count total number of bigrams observed
		N = len(self.tokens)
		#set all unfound freq = highest neighbor
		for f in range(1,int(max_freq)):
			if f not in freq_dict:
				freq_dict[f] = self.guess_freq(freq_dict,f,max_freq) 
		freq_dict[max_freq+1] = freq_dict[max_freq]
		
		adjusted_counts = dict()
		adjusted_counts[0] = freq_dict[1]
		
		for f in range(1,len(freq_dict)):
			adjusted_counts[f] = (f+1.)*(freq_dict[f+1]/freq_dict[f])
		return adjusted_counts
		
	def good_turing_smooth(self):
		if self.adjusted_bigram_counts == None or self.adjusted_unigram_counts == None:
			(uni_freqs, bi_freqs) = self.get_frequencies()
			# Adjusted counts using Good-Turing discounting
			self.adjusted_bigram_counts = self.get_good_turing_counts(bi_freqs)
			self.adjusted_unigram_counts = self.get_good_turing_counts(uni_freqs)
		return (self.adjusted_unigram_counts, self.adjusted_bigram_counts)
	
	#fix this
	def get_good_turing_probability(self, bigram):
		(adjusted_unigram_counts, adjusted_bigram_counts) = self.good_turing_smooth()
		(uni_freqs, bi_freqs) = self.get_frequencies()
		(first, second) = bigram
		if bigram not in bi_freqs:
			# Use special equation for 0 frequency class bigrams
			pass
			return
		
		bigram_count = adjusted_bigram_counts[bigram]
		unigram_count = adjusted_unigram_counts[(first,)]
		
		# Insert equation to generate probability based on these counts
		pass
		return
		
		
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
		elif bigram not in bi_freqs and self.smoothed == NONE:
			return 0.
		elif bigram not in bi_freqs and self.smoothed == LAPLACE:
			return 1./uni_freqs[(first,)]
		# MAKE SURE THIS IS CORRECT
		"""
		elif self.smoothed == GOOD_TURING:
			return self.get_good_turing_probability(bigram)
		else:
			return probs[bigram]
		"""
		
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
		

b = Bigram(filename="test_text")
#print b.tokens
b.good_turing_smooth()
print b.generate_sentence()

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