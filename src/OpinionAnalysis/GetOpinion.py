#coding=utf-8

'''
CopeOpiAnalyzer returns a score for input string
'''
import logging

class wordDict():
	def __init__(self, file_name):
		self.dict = self.get_list(file_name)
	#
	def get_list(self, file_name):
		word_list = list()
		with open(file_name, 'r') as fp:
			for line in fp:
				word_list.append(line.replace('\n', ''))
		return word_list
	#
	def inDict(self, input_string):
		if input_string in self.dict:
			return True
		else:
			return False

class unigramDict():
	def __init__(self, pos_file_name, neg_file_name):
		self.dict = self.get_dict(pos_file_name, neg_file_name)
	#
	def get_dict(self, pos_file_name, neg_file_name):
		word_dict = {}
		with open(pos_file_name, 'r') as fp:
			for line in fp:
				elements = line.replace('\n', '').split('\t')
				if len(elements) == 5:
					pos_score = float(elements[3])
					neg_score = float(elements[4])
					score = (2 * pos_score - 1) * neg_score
					word_dict[ elements[0] ] = score
		with open(neg_file_name, 'r') as fp:
			for line in fp:
				elements = line.replace('\n', '').split('\t')
				if len(elements) == 5:
					pos_score = float(elements[3])
					neg_score = float(elements[4])
					score = (1 - 2 * pos_score) * neg_score
					word_dict[ elements[0] ] = score
		return word_dict
	#
	def getProperty(self, input_char):
		return self.dict.get(input_char, 0)

class ANTUSD():
	def __init__(self, file_name):
		self.dict = self.get_list(file_name)
	#
	def get_list(self, file_name):
		word_dict = {}
		with open(file_name, 'r') as fp:
			for line in fp:
				elements = line.replace('\n', '').split(',')
				if len(elements) == 7:
					word_dict[ elements[0] ] = float(elements[1])
		return word_dict
	#
	def inDict(self, input_string):
		if input_string in self.dict:
			return True
		else:
			return False
	#
	def getProperty(self, input_string):
		return self.dict.get(input_string, 0)

class CopeOpiAnalyzer():
	def __init__(self, path_to_dict = 'dict/', keyword = ''):
		self.posWords = wordDict(path_to_dict+'positive_new.txt')
		self.negWords = wordDict(path_to_dict+'negative_new.txt')
		self.negationWords = wordDict(path_to_dict+'negation.txt')
		self.stopwords = wordDict(path_to_dict+'stopwords.txt')
		self.unigramScore = unigramDict(path_to_dict+'pos_unigram.txt', path_to_dict+'neg_unigram.txt')
		self.ntusd = ANTUSD(path_to_dict+'ANTUSD.txt')
		self.keyword = keyword

	def token_pos_type(self, input_string):
		'''
		ideal input is like '第一(Neu)'
		'''
		token_list = input_string.split('(')
		if len(token_list) == 2:
			pos_list = token_list[1].split(')')
			if len(pos_list) == 2:
				return token_list[0], pos_list[0], pos_list[1]
		#
		if input_string == '((PERIODCATEGORY)' or input_string == '((PARENTHESISCATEGORY)':
			return '(', 'PARENTHESISCATEGORY', ''
		if input_string != '':
			logging.warning('token = {}.'.format(input_string))
		return '', '', ''

	def normalize_word_score(self, w_score, tag):
		'''
		do an stair function on word
		'''
		if tag in ['Na','Nb', 'Nv']:
			# if noun, no important
			if w_score > 0:
				if w_score > 0.5:
					w_score = 0.3
				elif w_score > 0.2:
					w_score = 0.2
				else:
					w_score = 0.1
		else:
			# max w_score is 0.5
			if w_score > 0.5:
				w_score = 0.5

		return w_score

	def normalize_sentence_score(self, countScore):
		pn_sign = 1 if countScore >= 0 else -1
		if abs(countScore) > 1:
			countScore = pn_sign * 1
		elif abs(countScore) < 0.1 and abs(countScore) > 0:
			countScore = pn_sign * 0.1
		else:
			countScore = int( abs(countScore)/0.1 ) * 0.1 * pn_sign
		return countScore

	def summ_sentence_score(self, sentenceScore, sentenceCount):
		assert( len(sentenceScore)==len(sentenceCount) )
		totalScore = 0
		for i in range(len(sentenceScore)):
			totalScore += sentenceScore[i] * sentenceCount[i] / sum(sentenceCount)
		return totalScore

	def score(self, docString):
		tokens = docString.split(' ')

		wordTH = 0.3 # threadhold
		charTH = 0.5 # threadhold 

		tokenScore = 0 # score for one word
		countScore = 0 # score for one sentence
		sentenceScore = list() # overall score
		sentenceCount = list()

		outString = ''

		negate = False
		negateIdx = -1 # token i which token is negation word
		negateScore = 0 # score of token[negateIdx]

		lastOpinionIdx = -1 # last token i which score does not euqal to 0
		lastOpinion = 0 # score of token[lastOpinionIdx]

		countNegation = 0

		num_words = 0
		num_tokens = len(tokens)
		for i in range(num_tokens):
			inDic = False
			token, POStag, wordType = self.token_pos_type(tokens[i])

			if POStag == '' or token == '':
				continue

			num_words += 1
			if POStag not in ['A', 'Na','Nb', 'Nv', 'Cbb','PERIODCATEGORY','EXCLANATIONCATEGORY','QUESTIONCATEGORY','COMMACATEGORY','SEMICOLONCATEGORY', 'EXCLAMATIONCATEGORY'] and POStag[0] != 'V' and POStag[0] != 'D' and self.negationWords.inDict(token) == False:
				## token is not a sentiment word ##
				if i == num_tokens-1: # the last word in the article
					normal_countScore = self.normalize_sentence_score(countScore)
					sentenceScore.append(normal_countScore)
					sentenceCount.append(num_words)
					outString += '\n***Score={:.4f}->{:.4f}\n'.format(countScore, normal_countScore)

				outString += token + ' '

			else:
				## tokenScore = word score ##
				tkiScore = [self.unigramScore.getProperty(tki) for tki in token]
				tokenScore = sum(tkiScore) / len(token)
				'''
				if wordType == '' or wordType == '0' or wordType == '1' or len(token) < 2:
					# wordType = '' or token = one char
					tkiScore = [self.unigramScore.getProperty(tki) for tki in token]
					tokenScore = sum(tkiScore) / len(token)
				
				elif wordType == '2' or wordType == '4':
					# 
					tokenScore = 0
					w1Score = self.unigramScore.getProperty(token[0])
					w2Score = self.unigramScore.getProperty(token[1])

					if w1Score * w2Score > 0:
						# w1 and w2 have the same sentiment -> w1
						tokenScore = w1Score
					elif w1Score * w2Score < 0:
						# w1 and w2 have different sentiment -> whichever is more important
						tokenScore = w1Score if abs(w1Score) >= abs(w2Score) else w2Score
					elif w1Score == 0:
						tokenScore = w2Score
					elif w2Score == 0:
						tokenScore = w1Score

				elif wordType == '3' or wordType == '5' or wordType == '7':
					# 
					tokenScore = self.unigramScore.getProperty(token[1])
					if tokenScore == 0:
						tokenScore = self.unigramScore.getProperty(token[0])

				elif wordType == '6':
					tokenScore = -1 * self.unigramScore.getProperty(token[1])
				
				else:
					tkiScore = [self.unigramScore.getProperty(tki) for tki in token]
					tokenScore = sum(tkiScore) / len(token)
				'''

				## countScore = sentence score ##
				if self.ntusd.inDict(token):
					# if word in ntusd and != 0 -> use the score here
					inDic = True
					tokenScore = self.ntusd.getProperty(token)
					tokenScore = self.normalize_word_score(tokenScore, POStag)
					countScore += tokenScore

					if negate:
						countScore -= 2 * tokenScore # minus tokenScore

						lastOpinionIdx = -1
						lastOpinion = 0

					elif self.negationWords.inDict(token) is False:
						lastOpinionIdx = i
						lastOpinion = tokenScore

					else:
						lastOpinion = 0

				elif self.negWords.inDict(token):
					# if word not in ntusd but in neg words
					inDic = True
					if tokenScore > 0: 
						tokenScore *= -1 # tokenScore should be negative

					tokenScore = self.normalize_word_score(tokenScore, POStag)
					countScore += tokenScore
					if negate:
						countScore -= 2 * tokenScore
						'''
						if lastOpinionIdx != -1:
							if i - negateIdx > negateIdx - lastOpinionIdx:
								countScore -= 2 * lastOpinion
							else:
								countScore -= 2 * tokenScore
						else:
							countScore -= 2 * tokenScore
						'''
						lastOpinionIdx = -1
						lastOpinion = 0

					elif self.negationWords.inDict(token) is False:
						lastOpinion = tokenScore

					else:
						lastOpinion = 0
					
					# negate = False
					if self.negationWords.inDict(token) is False:
						lastOpinionIdx = i
						lastOpinion = tokenScore

				elif self.posWords.inDict(token):
					# if word not in ntusd but in pos words
					inDic = True
					if tokenScore < 0:
						tokenScore *= -1 # tokenScore should be positive

					tokenScore = self.normalize_word_score(tokenScore, POStag)
					countScore += tokenScore
					if negate:
						countScore -= 2 * tokenScore # minus tokenScore
						'''
						if lastOpinionIdx != -1 and i - negateIdx > negateIdx - lastOpinionIdx:
							countScore -= 2 * lastOpinion
						else:
							countScore -= 2 * tokenScore # minus tokenScore
						'''
						lastOpinionIdx = -1
						lastOpinion = 0

					elif self.negationWords.inDict(token) is False:
						lastOpinion = tokenScore

					else:
						lastOpinion = 0
		            
					# negate = False
					if self.negationWords.inDict(token) is False:
						lastOpinionIdx = i
		            
				
				else:
					# if not inDict
					if abs(tokenScore) > wordTH and self.negationWords.inDict(token) is False:
						if len(token) == 1 and abs(tokenScore) < charTH and POStag != 'A' and POStag != 'D':
							# token char score is not enough
							tokenScore = 0

						elif self.stopwords.inDict(token):
							tokenScore = 0

						elif inDic is False:
							# token has sentiment score but not in any dict
							tokenScore = self.normalize_word_score(tokenScore, POStag)
							tokenScore = tokenScore / 2
							countScore += tokenScore

							if negate and tokenScore>0:
								if tokenScore > 0:
									countScore -= 2 * tokenScore
								'''
								if lastOpinionIdx != -1 and i - negateIdx > negateIdx - lastOpinionIdx:
									countScore -= 2 * lastOpinion
									lastOpinionIdx = i
									lastOpinion = tokenScore
								else:
									countScore -= 2 * tokenScore
								'''

								lastOpinionIdx = -1
								lastOpinion = 0

							elif self.negationWords.inDict(token) is False:
								lastOpinion = tokenScore

							else:
								lastOpinion = 0

							# negate = False

					elif self.negationWords.inDict(token) is False:
						# token score is not enough and not a negation
						tokenScore = 0

				if negate:
					outString += '{}/{:.3f}(n) '.format(token, tokenScore)
				else:
					outString += '{}/{:.3f} '.format(token, tokenScore)

				if self.negationWords.inDict(token) is True:
					inDic = True
					if negate:
						# two negation = positive?
						negate = False
					else:
						negateIdx = i
						negateScore = tokenScore
						negate = True

				if negate and POStag == 'COMMACATEGORY':
					negate = False
					# comma_count += 1
				
				#if negate and comma_count >= 1:
				#	negate = False
				#	comma_count = 0

				## totalScore = overall score ##
				if POStag in ['PERIODCATEGORY', 'QUESTIONCATEGORY', 'EXCLAMATIONCATEGORY', 'SEMICOLONCATEGORY'] or i == num_tokens - 1:
					# 'COMMACATEGORY'
					if negate:
						if lastOpinionIdx != -1:
							countScore -= 2 * lastOpinion
						else:
							countScore += negateScore

					#if POStag == 'QUESTIONCATEGORY':
					#	countScore = -1 * countScore

					normal_countScore = self.normalize_sentence_score(countScore)
					outString += '\n***Score={:.4f}->{:.4f} **weight={}\n'.format(countScore, normal_countScore, num_words)
					if num_words > 2:
						sentenceScore.append(normal_countScore)
						sentenceCount.append(num_words)
					num_words = 0
					countScore = 0
					countNegation = 0
					negate = False

		totalScore = self.summ_sentence_score(sentenceScore, sentenceCount)
		outString += '***totalScore={}\n'.format(totalScore)
		return round(totalScore, 2), outString

def read_text(file_name, is_replace = True):
	docString = ''
	with open(file_name, 'r') as fp:
		for line in fp:
			if is_replace:
				docString += line.replace('\n', '').replace('\r', '')
			else:
				docString += line
	return docString

if __name__ == '__main__':
	# from CopeOpi import *
	CopeOpi = CopeOpiAnalyzer('CopeOpi/dic_trad/')
	docString = read_text('../../data/9.txt')
	totalScore, outString = CopeOpi.score(docString)
	print(outString)

