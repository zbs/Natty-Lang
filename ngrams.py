import nltk, math, random

#filename = "../Proj1Data/test.txt"

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
		self.smoothed = smoothed
		#Reads in text of specified file
		self.unk = unk
		if filename != None:
			with open(filename) as fp:
				self.text = fp.read()
		else:
			if text_string == None:
				print "Error: Need either filename or string"
				return 
			else:
				self.text = text_string
		self.tokens = tokenize(self.text)
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

	def get_probability(self, unigram):
		probs = self.get_probabilities()
		if unigram not in probs:
			if self.unk:
				return probs["<UNK>"]
			return 0. 
		return probs[unigram] 
	
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
		
class Bigram():
	def __init__(self, filename=None, text_string=None, unk=False, smoothed=NONE):
		if filename != None:
			with open(filename) as fp:
				self.text = fp.read()
		else:
			if text_string == None:
				print "Error: Need either filename or string"
				return 
			else:
				self.text = text_string
				
		self.smoothed = smoothed
		self.unk = unk
		
		self.tokens = add_sentence_markers(tokenize(self.text))
		if self.unk:
			self.tokens = create_unks(self.tokens)
		self.num_words = float(len(self.tokens))
		
		# Adjusted counts using Good-Turing discounting
		self.adjusted_bigram_counts = None
		# Represents the sum across the row of a 
		# table of adjusted counts (C*)
		self.adjusted_denominator = dict()
		
		# Unsmoothed frequencies
		self.uni_frequencies = None
		self.bi_frequencies = None
		
		#Probabilities
		self.bigrams = None
		
	def get_num_tokens(self):
		return len(self.tokens)
	
	def has_tokens(self, gram):
		(first, second) = gram
		(uni_freqs, _) = self.get_frequencies()
		return (first,) in uni_freqs and (second,) in uni_freqs
		
	def get_frequencies(self):
		if self.uni_frequencies == None or self.bi_frequencies == None:
			l = len(self.tokens)
			self.uni_frequencies = dict()
			self.bi_frequencies = dict()
			for i in range(l):
				if(i != l-1):
					# Bigram frequencies
					bigram_token = (self.tokens[i], self.tokens[i+1])
					if bigram_token in self.bi_frequencies:
						self.bi_frequencies[bigram_token] += 1.
					else:
						self.bi_frequencies[bigram_token] = 1.
				
				# Unigram frequencies
				unigram_token = (self.tokens[i],)
				if unigram_token in self.uni_frequencies:
					self.uni_frequencies[unigram_token] += 1.
				else:
					self.uni_frequencies[unigram_token] = 1.
					
			# Decrement count for artificially inserted period
			# so that the denominator for bigram probabilities is accurate.
			end_punct = self.tokens[-1:][0]
			self.uni_frequencies[(end_punct,)] -= 1.
			
			# Add one smoothing -- couldn't be implemented above because 
			# the number of wordtypes wasn't known a priori.
			if (self.smoothed == LAPLACE):
				for key in self.bi_frequencies:
					self.bi_frequencies[key] += 1.
				for key in self.uni_frequencies:
					self.uni_frequencies[key] += len(self.uni_frequencies)
				
		return (self.uni_frequencies, self.bi_frequencies)
		

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
		N = len(self.tokens) - 1
		
		#set all unfound freq = highest neighbor
		for f in range(1,int(max_freq)):
			if f not in freq_dict:
				freq_dict[f] = self.guess_freq(freq_dict,f,max_freq) 
		freq_dict[max_freq+1] = \
			2.*freq_dict[max_freq] - freq_dict[max_freq-1]
		
		adjusted_counts = dict()
		adjusted_counts[0] = freq_dict[1]/N
		for f in range(1,int(max_freq+1)):
			adjusted_counts[f] = (f+1.)*(freq_dict[f+1]/freq_dict[f])
		return adjusted_counts
		
	def good_turing_smooth(self):
		if self.adjusted_bigram_counts == None:
			(_, bi_freqs) = self.get_frequencies()
			# Adjusted counts using Good-Turing discounting
			self.adjusted_bigram_counts = self.get_good_turing_counts(bi_freqs)
		return self.adjusted_bigram_counts
	
	"""
		This essentially calculates the sum across the row of bigrams that begin 
		with prev_word
	"""	
	def get_gt_bigram_count(self,prev_word):
		if prev_word not in self.adjusted_denominator:
			(uni_freqs, bi_freqs) = self.get_frequencies()
			adjusted_bigram_counts = self.good_turing_smooth() 
			
			self.adjusted_denominator[prev_word] = 0.
			for (word,) in uni_freqs:
				if (prev_word, word) not in bi_freqs:
					self.adjusted_denominator[prev_word] += adjusted_bigram_counts[0]
				else:
					self.adjusted_denominator[prev_word] += \
						adjusted_bigram_counts[bi_freqs[(prev_word, word)]]	
		return self.adjusted_denominator[prev_word]	
	
	def get_good_turing_probability(self, bigram):
		adjusted_bigram_counts = self.good_turing_smooth()
		(_, bi_freqs) = self.get_frequencies()
		(first, _) = bigram
		
		if bigram not in bi_freqs:
			adjusted_numerator_count = adjusted_bigram_counts[0]
		else:
			adjusted_numerator_count = adjusted_bigram_counts[bi_freqs[bigram]] 
		
		return adjusted_numerator_count / self.get_gt_bigram_count(first)
		
	def get_probability(self, bigram):
		(first, second) = bigram
		(uni_freqs, bi_freqs) = self.get_frequencies()

		# Deal with unknowns here
		if (self.unk):
			if (first,) not in uni_freqs and (second,) not in uni_freqs:
				return self.get_probability(("<UNK>", "<UNK>"))
			if (first,) not in uni_freqs and (second,) in uni_freqs:
				return self.get_probability(("<UNK>", second))
			if (first,) in uni_freqs and (second,) not in uni_freqs:
				return self.get_probability((first, "<UNK>"))
		
		# Deal with Laplace smoothing appropriately
		if (self.smoothed == LAPLACE):
			if bigram not in bi_freqs:
				return 1./uni_freqs[(first,)]
			else:
				return bi_freqs[(first,second)] / uni_freqs[(first,)]
				
		# Deal with Good-Turing smoothing 
		if (self.smoothed == GOOD_TURING):
			prob = self.get_good_turing_probability(bigram)
			return prob
		
		# No smoothing
		if (self.smoothed == NONE):
			if bigram not in bi_freqs:
				return 0.
			else:
				return (bi_freqs[(first,second)] / uni_freqs[(first,)])
				
	def next_word(self, prev_word):
		ran = random.uniform(0,1)
		(uni_freqs, _) = self.get_frequencies()
		for (word,) in uni_freqs: 
			word_prob = self.get_probability((prev_word, word))
			ran -= word_prob
			if ran <= 0:
				return word
		
	def generate_sentence(self):
		cur_word = self.next_word(".")
		sentence = ""
		while not is_punct(cur_word):
			sentence += cur_word + " "
			cur_word = self.next_word(cur_word)
		return sentence[:-1] + cur_word
		

#b = Bigram(filename="data/Dataset4/Train.txt", smoothed=GOOD_TURING)
#print b.tokens
#b.good_turing_smooth()
#print b.generate_sentence()
