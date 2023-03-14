# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util

import numpy as np
import re
import random
from porter_stemmer import PorterStemmer

# noinspection PyMethodMayBeStatic
class Chatbot:
	

	"""Simple class to implement the chatbot for PA 6."""

	def __init__(self, creative=False):
		# The chatbot's default name is `moviebot`.
		# TODO: Give your chatbot a new name.
		self.name = 'moviebot'

		self.creative = creative

		# Process Line Vars
		self.prompted_movies = False
		self.user_ratings = dict()
		self.prompted_recs = False
		self.random_responses = -1
		self.happy_responses = -1
		self.sad_responses = -1
		self.ambiguous_responses = -1
		self.grateful_responses = -1
		self.angry_responses = -1
		self.confused_responses = -1
		self.amb = False
		self.recommended = 0

		self.movie_title = ""
		self.clarifying_sentiment = False

		self.movie_sentiment = 0
		self.clarifying_movie = False
		# This matrix has the following shape: num_movies x num_users
		# The values stored in each row i and column j is the rating for
		# movie i by user j
		self.titles, ratings = util.load_ratings('data/ratings.txt')
		self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')

		########################################################################
		# TODO: Binarize the movie ratings matrix.                             #
		########################################################################

		# Binarize the movie ratings before storing the binarized matrix.
		self.ratings = ratings
		self.ratings = self.binarize(ratings, threshold=2.5)
		########################################################################
		#                             END OF YOUR CODE                         #
		########################################################################

	############################################################################
	# 1. WARM UP REPL                                                          #
	############################################################################

	def greeting(self):
		"""Return a message that the chatbot uses to greet the user."""
		########################################################################
		# TODO: Write a short greeting message                                 #
		########################################################################

		greeting_message = "It's Captain Jack Sparrow! Let me know which movies (indicate them in parentheses) you like/dislike and I'll provide recommendations!"
		########################################################################
		#                             END OF YOUR CODE                         #
		########################################################################
		return greeting_message

	def goodbye(self):
		"""
		Return a message that the chatbot uses to bid farewell to the user.
		"""
		########################################################################
		# TODO: Write a short farewell message                                 #
		########################################################################

		goodbye_message = "Happy to have been at service. Never forget the greatest pirate who ever lived."

		########################################################################
		#                          END OF YOUR CODE                            #
		########################################################################
		return goodbye_message
	
	def nonMovieResponse(self, text):
		responseBool,responseText = self.arbitraryResponse(text)
		if responseBool:
			return responseText
		else:
			return self.emotionalResponse(text)


	def emotionalResponse(self, text):
		happiness = ["happy", "excited", "thrilled", "delighted", "ecstatic", "joyful", "joy", "delightful"]
		sadness = ["sad", "depressed", "miserable", "disappointed", "melancholy", "melancholic", "sadness", "despair", "saddened"]
		anger = ["angry", "frustrated", "hate", "irritated", "annoyed", "outraged", "enraged", "livid", "fuck", "fuck you", "incensed", "anger", "sucks", "stinks","horrible", "bad", "poorly", "awful", "sorry", "lousy", "crappy", "waste", "wasting"]
		gratitude = ["thanks", "thank", "great", "good", "nice", "thx", "wonderful", "awesome", "woohoo", "sweet", "cool", "amazing", "love", "like","liked","loved"]
		confusion = ["confused", "perplexed", "confusion", "puzzled", "unclear", "understand"]

		happiness_response = ["Happy to hear!", "Awesome!", "Great!", "Perfect!", "I'm glad!", "Whoopie!", "Awesome sauce!", "Nice!"]
		sadness_response = ["I'm sorry to hear that", "I hope you feel better", "Feel better soon", "I'm sorry you're going through a tough time", "I understand that it's hard to feel sad", "It's okay to not be okay.", "I'm sorry.", "You will get through this"]
		anger_response = ["Woah! I'm trying here", "Oh snap! I'm sorry", "Say what? I'll try to be better", "For real? I'm Captain Jack Sparrow", "Don't make me come out of this computer!", "Really? I'm sorry you feel that way", "Come on, I'm doing my best.", "I don't see you trying to recommend movies!"]
		gratitude_response = ["That means a lot!", "Wait till I tell the whole crew! Thanks!", "Sweet! Good to hear", "I'm happy you said that", "Whoopie! Thanks", "Wahoooooo! Thank you", "I really needed that today. Thanks", "You know me! I do it because I love recommending movies but also for the gratitude"]
		confused_response = ["I'm Jack Sparrow and I recommend movies", "Please tell me which movies you like and dislike and I'll give you recommendations", "Just send me movie titles and tell me whether you liked them or not and I will recommend you movies", "If you tell me 5 movie names along with whether or not you liked them, I can recommend you some movies.", "My job is to recommend movies. Just type in titles of movies you've seen",
			   "You give me the titles of movies and how you felt about them. I give you movie recommendations", "Sorry you're having trouble. Make sure to type in the name of the movie and how you feel about it to receive recommendations.", "You can keep going as long as you want."]
		ambiguous_response = ["I'm sorry, I don't understand.", "Could you try to rephrase that please?", "I'm not quite sure what you're trying to say.", "I'm sorry. Can you rephrase?", "I don't quite understand.", "Please bear with me. What was that?", "Come again? I didn't understand.", "One more time. What were you trying to say?"]

		words = text.lower().split()
		sad = True
		happy = True
		angry = True
		grate = True

		if "not" in words and (set(words).intersection(set(happiness))):
			the_word = ""
			for word in words:
				if word in happiness:
					the_word = word
			happy = not (words.index("not") < words.index(the_word))

		if "don't" in words and (set(words).intersection(set(happiness))):
			the_word = ""
			for word in words:
				if word in happiness:
					the_word = word
			happy = not (words.index("don't") < words.index(the_word))
		
		if "not" in words and (set(words).intersection(set(sadness))):
			the_word = ""
			for word in words:
				if word in sadness:
					the_word = word
			sad = not (words.index("not") < words.index(the_word))
		
		if "not" in words and (set(words).intersection(set(anger))):
			the_word = ""
			for word in words:
				if word in anger:
					the_word = word
			angry = not (words.index("not") < words.index(the_word))
		
		if "don't" in words and (set(words).intersection(set(anger))):
			the_word = ""
			for word in words:
				if word in anger:
					the_word = word
			angry = not (words.index("don't") < words.index(the_word))

		if "don't" in words and (set(words).intersection(set(gratitude))):
			the_word = ""
			for word in words:
				if word in gratitude:
					the_word = word
			grate = not (words.index("don't") < words.index(the_word))
		
		if "not" in words and (set(words).intersection(set(gratitude))):
			the_word = ""
			for word in words:
				if word in gratitude:
					the_word = word
			grate = not (words.index("not") < words.index(the_word))

		if ((set(words).intersection(set(happiness))) and happy) or not angry:
			if self.happy_responses == 7:
				self.happy_responses = 0
			self.happy_responses += 1
			return happiness_response[self.happy_responses]
		
		if ((set(words).intersection(set(sadness))) and sad) or not happy:
			if self.sad_responses == 7:
				self.sad_responses = 0
			self.sad_responses += 1
			return sadness_response[self.sad_responses]
		
		if ((set(words).intersection(set(anger))) and angry) or not grate:
			if self.angry_responses == 7:
				self.angry_responses = 0
			self.angry_responses += 1
			return anger_response[self.angry_responses]
		
		if ((set(words).intersection(set(gratitude))) and grate):
			if self.grateful_responses == 7:
				self.grateful_responses = 0
			self.grateful_responses += 1
			return gratitude_response[self.grateful_responses]
		
		if (set(words).intersection(set(confusion))):
			if self.confused_responses == 7:
				self.confused_responses = 0
			self.confused_responses += 1
			return confused_response[self.confused_responses]
		
		else:
			if self.ambiguous_responses == 7:
				self.ambiguous_responses = 0
			self.ambiguous_responses += 1
			self.amb = True
			return ambiguous_response[self.ambiguous_responses]
	
	def arbitraryResponse(self, text):
		request = r'(?:[cC]an you|[Ww]ill you|[cC]ould you|[Ww]ould you|[Pp]lease|[Dd]o you|[Hh]elp|[Ww]hat|([Hh]ow))\s*(.*[.?!]*)'
		question = r'\b((I have | I have a)questio[ns])\b'
		responses = ["I can only pilot my ship and give movie recommendations. Type movies in parentheses, tell me how you feel about them, and I can recommend movies to you.", "I love the sea and giving you movie recommendations. I can give you movie recommendations", "I'm a captain and a movie connoisseur. I recommend movies.", "I hunt for treasure and good movies. I'll recommend movies but not where to find treasure!", 
		   "Movies are my treasure. I'll recommend some for ya.", "I'm happy to sail the seas and recommend you movies.", "I can find Davy Jones' locker for myself, but I can recommend movies for you."]
		matches = re.findall(request, text)
		questions = re.findall(question, text)
		if len(matches) > 0:
			if self.random_responses == 6:
				self.random_responses = 0
			self.random_responses +=1
			return len(matches) > 0, "Arrggghhhh?" + " " + responses[self.random_responses]
		if len(questions) > 0:
			if self.random_responses == 6:
				self.random_responses = 0
			self.random_responses +=1
			return len(questions) > 0, "Arrggghhhh?" + " " + responses[self.random_responses]
		else:
			return False, "Blimey! I don't understand"
		
	def affirmative(self, text):
		aff = ["yes", "yeah", "ye", "y", "yup", "sure", "ok", "okay", "alright", "absolutely", "of course", "definitely", "you bet", "please", "yes please"]
		words = text.lower().split()
		appears = False
		for word in words:
			if word in aff:
				appears = True
		return appears
		

	############################################################################
	# 2. Modules 2 and 3: extraction and transformation                        #
	############################################################################

	def process(self, line):
		"""Process a line of input from the REPL and generate a response.

		This is the method that is called by the REPL loop directly with user
		input.

		You should delegate most of the work of processing the user's input to
		the helper functions you write later in this class.

		Takes the input string from the REPL and call delegated functions that
		  1) extract the relevant information, and
		  2) transform the information into a response to the user.

		Example:
		  resp = chatbot.process('I loved "The Notebook" so much!!')
		  print(resp) // prints 'So you loved "The Notebook", huh?'

		:param line: a user-supplied line of text
		:returns: a string containing the chatbot's response to the user input
		"""
			
		########################################################################
		# TODO: Implement the extraction and transformation in this method,    #
		# possibly calling other functions. Although your code is not graded   #
		# directly based on how modular it is, we highly recommended writing   #
		# code in a modular fashion to make it easier to improve and debug.    #
		########################################################################
		if self.creative:
			response = "I processed {} in creative mode!!".format(line)
		else:
			response = "I processed {} in starter mode!!".format(line)
		
		if line == ":quit":
			return self.goodbye()

		if self.clarifying_movie:
			movie_list = self.extract_titles(self.preprocess(line))
			if len(movie_list) == 0:
				response = self.nonMovieResponse(line)
				if self.amb:
					response = response + " " + "If you meant to talk about a movie, please put it in parentheses"
				self.amb = False
				return response
			else:
				# got movies out
				self.clarifying_movie = False
				# populate user_ratings w new movie titles & correct sentiment
				self.movie_sentiment = self.extract_sentiment(self.preprocess(line))
				if self.sentiment == 0:
					self.clarifying_sentiment = True
					# can get stuck here by repromiting for movie even tho we need sentiment
					response = "I didn't understand. Did you like or dislike the movie?"
					return response
				else:
					self.movie_title = movie_list[0]
					self.user_ratings[self.find_movies_by_title(self.movie_title)[0]] = self.movie_sentiment
					if len(self.user_ratings) > 4:
						# Instatiantiate list of recommended movies & prompt user if they'd like recommendations now
						self.recommended_movies = self.recommend(self.user_ratings, self.ratings, 10)
						if (self.movie_sentiment == -1):
							response = "You didn't like " + self.movie_title + ". Got it! "
						else:
							response = "You liked " + self.movie_title + ". Got it! "
						response += "Would you like a movie recommendation?"
						self.prompted_recs = True
						return response
					else:
						#later handle "I didn't understand that"
						if (self.movie_sentiment == -1):
							response = "You didn't like " + self.movie_title + ". Got it! Tell me about another movie."
						else:
							response = "You liked " + self.movie_title + ". Got it! Tell me about another movie."
						return response



		# if clarifying sentiment, add new sentiment to dict, prompt user for next movie if under 5 in dict
		if self.clarifying_sentiment:
			self.movie_sentiment = self.extract_sentiment(self.preprocess(line))
			if self.movie_sentiment == 0:
				response = "I didn't understand. Did you like or dislike the movie?"
				return response
			else:
				#got the sentiment
				self.clarifying_sentiment = False
				# populate the user_ratings w new, correct sentiment, no longer clarifying
				self.user_ratings[self.find_movies_by_title(self.movie_title)[0]] = self.movie_sentiment
				if len(self.user_ratings) > 4:
					# Instatiantiate list of recommended movies & prompt user if they'd like recommendations now
					self.recommended_movies = self.recommend(self.user_ratings, self.ratings, 10)
					if (self.movie_sentiment == -1):
						response = "You didn't like " + self.movie_title + ". Got it! "
					else:
						response = "You liked " + self.movie_title + ". Got it! "
					response += "Would you like a movie recommendation?"
					self.prompted_recs = True
					return response
				else:
					#later handle "I didn't understand that"
					if (self.movie_sentiment == -1):
						response = "You didn't like " + self.movie_title + ". Got it! Tell me about another movie."
					else:
						response = "You liked " + self.movie_title + ". Got it! Tell me about another movie."
					return response
	
		if len(self.user_ratings) < 5:
			# we are populating user preferences dict
			processed = self.preprocess(line)
			movie_list = self.extract_titles(processed)
			self.movie_sentiment = self.extract_sentiment(processed)
			# TODO: check size of movie_list, if 0, then prompt for movie title in quotes, keep track of sentiment, allow for two movies to be added
			
			
			
			if len(movie_list) == 0:
				self.clarifying_movie = True
				#response = "Which movie did you like / dislike?"
				response = self.nonMovieResponse(line)
				if self.amb:
					response = response + " " + "If you meant to talk about a movie, please put it in parentheses"
				self.amb = False
				return response
			
			# check if movie is valid
			if len(self.find_movies_by_title(movie_list[0])) == 0:
				self.clarifying_movie = True
				response = "Sorry I don't know that movie... Tell me about a different one"
				return response
			elif len(self.find_movies_by_title(movie_list[0])) > 1:
				self.clarifying_movie = True
				response = "Sorry there are multiple movies with that name. Which did you mean?"
				movies = " "
				i = 0
				for movie in self.find_movies_by_title(movie_list[0]):
					if i < 4:
						movies += self.titles[movie][0]
						movies += " "
						i += 1
					else:
						break
				i = 0
				return response + " " + movies
			self.movie_title = movie_list[0]
			# if sentiment is zero prompt for correction & clarifying sentiment = true
			if self.movie_sentiment == 0:
				response = "Did you like or dislike the movie?"
				self.clarifying_sentiment = True
				return response
			# if didn't understand movie title or movie sentiment, prompt for clarification
			self.user_ratings[self.find_movies_by_title(self.movie_title)[0]] = self.movie_sentiment
			if len(self.user_ratings) > 4:
				# Instatiantiate list of recommended movies & prompt user if they'd like recommendations now
				self.recommended_movies = self.recommend(self.user_ratings, self.ratings, 10)
				if (self.movie_sentiment == -1):
					response = "You didn't like " + self.movie_title + ". Got it! "
				else:
					response = "You liked " + self.movie_title + ". Got it! "
				response += "Would you like a movie recommendation?"
				self.prompted_recs = True
				return response
			else:
				#later handle "I didn't understand that"
				if (self.movie_sentiment == -1):
					response = "You didn't like " + self.movie_title + ". Got it! Tell me about another movie."
				else:
					response = "You liked " + self.movie_title + ". Got it! Tell me about another movie."
				return response
			# Preprocess the lines and get the movie: preprocess -> tokenize -> extract 
			# Movies: reformat -> find movies by title ->
			# Get the sentiment: extract_sentiment
			# then response = "I didn't understand. Please repeat" or "Got it. What's the next movie?"
			# if this was fifth movie, response = "Would you like recommendations" and prompted_recs = true
		else:
			# we can provide recommendations
			if not self.prompted_recs:
				response = "Would you like a movie recommendation?"
				self.prompted_recs = True
				return response
				#prompt user if they'd like recs

			elif self.affirmative(line):
				#self.recommended_movies = self.recommend(self.user_ratings, self.ratings, 10)
				#print(self.titles[index.pop()])
				self.recommended += 1
				if self.recommended == 11:
					return "Those are all the movies I have to recommend. Would you like to review more movies? Type ':quit' to exit or 'yes' to continue"
				if self.recommended == 12:
					self.prompted_movies = False
					self.user_ratings = dict()
					self.prompted_recs = False
					self.recommended = 0
					self.movie_title = ""
					self.clarifying_sentiment = False
					self.movie_sentiment = 0
					self.clarifying_movie = False
					return "Back to the start! What movie do you like or dislike?"
				response = "I think you'd like " + self.titles[self.recommended_movies.pop()][0] + ". Would you like another recommendation?"
				return response
				# provide recommendations and prompt if they'd like another rec or type "no"
			
			else:
				response = self.nonMovieResponse(line)
				if self.amb:
					response = response + " " + "Type ':quit' to exit or 'yes' to get a recommendation"
				self.amb = False
				return response
				# add case for a not yes or no later
				# user said "no" or something nonsensical
				# prompt user to type ":quit" to exit or "yes" to get a recommendation
			

		########################################################################
		#                          END OF YOUR CODE                            #
		########################################################################
		return response
	
	@staticmethod
	def preprocess(text):
		"""Do any general-purpose pre-processing before extracting information
		from a line of text.
		Given an input line of text, this method should do any general
		pre-processing and return the pre-processed string. The outputs of this
		method will be used as inputs (instead of the original raw text) for the
		extract_titles, extract_sentiment, and extract_sentiment_for_movies
		methods.
		Note that this method is intentially made static, as you shouldn't need
		to use any attributes of Chatbot in this method.
		:param text: a user-supplied line of text
		:returns: the same text, pre-processed
		"""
		return text

	def tokenize(self, text):
		quoted_sections = re.findall('"([^"]*)"', text)
		new_text = text

		for i, quote in enumerate(quoted_sections):
			new_text = text.replace(quote, f'quote{i}')
		
		split_text = new_text.split()

		return split_text, quoted_sections

	def extract_titles(self, preprocessed_input):
		"""Extract potential movie titles from a line of pre-processed text.
		Given an input text which has been pre-processed with preprocess(),
		this method should return a list of movie titles that are potentially
		in the text.
		- If there are no movie titles in the text, return an empty list.
		- If there is exactly one movie title in the text, return a list
		containing just that one movie title.
		- If there are multiple movie titles in the text, return a list
		of all movie titles you've extracted from the text.
		Example:
		  potential_titles = chatbot.extract_titles(chatbot.preprocess(
											'I liked "The Notebook" a lot.'))
		  print(potential_titles) // prints ["The Notebook"]
		:param preprocessed_input: a user-supplied line of text that has been
		pre-processed with preprocess()
		:returns: list of movie titles that are potentially in the text
		"""
		_, quoted_sections =  self.tokenize(preprocessed_input) 
		return quoted_sections

	@staticmethod
	def adjust_articles(title):
		
		if title.startswith("A "):
			formated_title = title[2:] + ', A'
		elif title.startswith("An "):
			formated_title = title[3:] + ', An'
		elif title.startswith("The "):
			formated_title = title[4:] + ', The'
		elif title.startswith("La "):
			formated_title = title[3:] + ', La'
		elif title.startswith("El "):
			formated_title = title[3:] + ', El'
		elif title.startswith("Los "):
			formated_title = title[4:] + ', Los'
		elif title.startswith("Las "):
			formated_title = title[4:] + ', Las'
		elif title.startswith("Les "):
			formated_title = title[4:] + ', Les'
		elif title.startswith("Il "):
			formated_title = title[3:] + ', Il'
		elif title.startswith("Le "):
			formated_title = title[3:] + ', Le'
		elif title.startswith("Der "):
			formated_title = title[4:] + ', Der'
		elif title.startswith("Die "):
			formated_title = title[4:] + ', Die'
		elif title.startswith("das "):
			formated_title = title[4:] + ', Die'
		else:
			formated_title = title

		return formated_title

	
	def find_movies_by_title(self, title):
		""" Given a movie title, return a list of indices of matching movies.
		- If no movies are found that match the given title, return an empty
		list.
		- If multiple movies are found that match the given title, return a list
		containing all of the indices of these matching movies.
		- If exactly one movie is found that matches the given title, return a
		list
		that contains the index of that matching movie.
		Example:
		  ids = chatbot.find_movies_by_title('Titanic')
		  print(ids) // prints [1359, 2716]
		:param title: a string containing a movie title
		:returns: a list of indices of matching movies
		"""
		def get_all_titles(title):
			regex = '\(a\.k\.a\. ([\w ]*)\)'

			matches = re.findall(regex, title)

			sliced_title = title

			all_titles = []

			for match in matches:
				sliced_title = sliced_title.replace("(a.k.a. " + match+')', "")
				all_titles.append(match)
			
			pattern2 = "\(.*?\)"
	
			matches = re.findall(pattern2, sliced_title)

			for match in matches:
				sliced_title = sliced_title.replace(match, "")
				all_titles.append(match[1:-1])

			all_titles.append(sliced_title.rstrip())

			return all_titles
				
		def get_movie_and_year(title):
			match = re.search('\(\d{4}\)', title)
			if match:
				year = match.group(0)
				end_index = match.start()
				title = title[:end_index - 1]
				return title, year

			return title, None
		

		titles = util.load_titles('data/movies.txt')

		title, year = get_movie_and_year(title)
		article_title = Chatbot.adjust_articles(title)


		indicies = []
		for i, movie in enumerate(titles):

			movie_title, movie_year = get_movie_and_year(movie[0])
			movie_titles = get_all_titles(movie_title)
			if article_title in movie_titles:
				if year == None or year == movie_year:
					indicies.append(i)
		
		return indicies


	def extract_sentiment(self, preprocessed_input):
		"""Extract a sentiment rating from a line of pre-processed text.
		You should return -1 if the sentiment of the text is negative, 0 if the
		sentiment of the text is neutral (no sentiment detected), or +1 if the
		sentiment of the text is positive.
		As an optional creative extension, return -2 if the sentiment of the
		text is super negative and +2 if the sentiment of the text is super
		positive.
		Example:
		  sentiment = chatbot.extract_sentiment(chatbot.preprocess(
													'I liked "The Titanic"'))
		  print(sentiment) // prints 1
		:param preprocessed_input: a user-supplied line of text that has been
		pre-processed with preprocess()
		:returns: a numerical value for the sentiment of the text
		"""
		input_list = preprocessed_input.lower().split()

		stemmer = PorterStemmer()

		quote_portion = False
		sign = 1
		score = 0
		power = 1
		neg_first = False

		negations = ["don't", "not", "never", "didn't", "wasn't", "isn't", "won't"]
		extream_words = ["love", "loved", "terrible", "awful", "atrocious", "hate", "hated", "amazing", "fantastic", "horrible"]
		emphasis_words = ["really", "reeally", "soo", "undoubtably", "super", "absolutly"]

		for word in input_list:
			word = word.strip()
			word_clean = word.rstrip(',.')
			stem = stemmer.stem(word)

			if word.startswith("\""):
				quote_portion = True
			
			if word.endswith("\""):
				quote_portion = False
				continue
			
			if quote_portion:
				continue
			
			if word_clean in negations:
				sign = sign*-1
				neg_first = True

			if word_clean in extream_words and not neg_first:
				power = 2
			
			if word_clean in emphasis_words and not neg_first:
				power = 2
			
			if word[-1] == '!':
				power = 2
			
			if stem.endswith('i'):
				stem = stem[:-1] + 'y'
			if word_clean in self.sentiment:
				to_add = sign if self.sentiment[word_clean] == 'pos' else -1*sign
				score += to_add
			elif stem in self.sentiment:
				to_add = sign if self.sentiment[stem] == 'pos' else -1*sign
				score += to_add
				

		if score > 0:
			print(preprocessed_input, " had score of ", 1*power)
			return 1*power
		elif score < 0:
			print(preprocessed_input, " had score of ", -1*power)
			return -1*power
		else:
			print(preprocessed_input, " had score of ", 0)
			return 0




	def extract_sentiment_for_movies(self, preprocessed_input):
		"""Creative Feature: Extracts the sentiments from a line of
		pre-processed text that may contain multiple movies. Note that the
		sentiments toward the movies may be different.
		You should use the same sentiment values as extract_sentiment, described
		above.
		Hint: feel free to call previously defined functions to implement this.
		Example:
		  sentiments = chatbot.extract_sentiment_for_text(
						   chatbot.preprocess(
						   'I liked both "Titanic (1997)" and "Ex Machina".'))
		  print(sentiments) // prints [("Titanic (1997)", 1), ("Ex Machina", 1)]
		:param preprocessed_input: a user-supplied line of text that has been
		pre-processed with preprocess()
		:returns: a list of tuples, where the first item in the tuple is a movie
		title, and the second is the sentiment in the text toward that movie
		"""
		


		titles = self.extract_titles(preprocessed_input)

		#check for a list of words that would lead us to having opposing scores
		conflict_word = 'but'

		sentiment = self.extract_sentiment(preprocessed_input)

		sentiments_with_titles = []

		#sentiments_with_titles.append((titles[0], sentiment))
		if conflict_word not in preprocessed_input:
			for i in range(len(titles)):
				sentiments_with_titles.append((titles[i], sentiment))
		else:
			#split up string and research for sentiment
			first_movie = str(titles[0])
			first_movie_string = preprocessed_input.split(first_movie, 1)[0]
			sentiment_first_movie = self.extract_sentiment(first_movie_string)
			#then flip sentiments
			sentiments_with_titles.append((titles[0], sentiment_first_movie))
			sentiments_with_titles.append((titles[1], -sentiment_first_movie))

		

		return sentiments_with_titles
		#pass

	def find_movies_closest_to_title(self, title, max_distance=3):
		"""Creative Feature: Given a potentially misspelled movie title,
		return a list of the movies in the dataset whose titles have the least
		edit distance from the provided title, and with edit distance at most
		max_distance.
		- If no movies have titles within max_distance of the provided title,
		return an empty list.
		- Otherwise, if there's a movie closer in edit distance to the given
		title than all other movies, return a 1-element list containing its
		index.
		- If there is a tie for closest movie, return a list with the indices
		of all movies tying for minimum edit distance to the given movie.
		Example:
		  # should return [1656]
		  chatbot.find_movies_closest_to_title("Sleeping Beaty")
		:param title: a potentially misspelled title
		:param max_distance: the maximum edit distance to search for
		:returns: a list of movie indices with titles closest to the given title
		and within edit distance max_distance
		"""
		return []
		#pass

	def disambiguate(self, clarification, candidates):
		"""Creative Feature: Given a list of movies that the user could be
		talking about (represented as indices), and a string given by the user
		as clarification (eg. in response to your bot saying "Which movie did
		you mean: Titanic (1953) or Titanic (1997)?"), use the clarification to
		narrow down the list and return a smaller list of candidates (hopefully
		just 1!)
		- If the clarification uniquely identifies one of the movies, this
		should return a 1-element list with the index of that movie.
		- If it's unclear which movie the user means by the clarification, it
		should return a list with the indices it could be referring to (to
		continue the disambiguation dialogue).
		Example:
		  chatbot.disambiguate("1997", [1359, 2716]) should return [1359]
		:param clarification: user input intended to disambiguate between the
		given movies
		:param candidates: a list of movie indices
		:returns: a list of indices corresponding to the movies identified by
		the clarification
		"""
		#three cases: a sequential response, the year it was made in, and finally a further text clarification, 
		#such as specificying the subtitle for a longer title

		candidate_list = []

		print(candidates)
		#case one: a sequential response -- can only be one 

		if len(clarification) == 1:  
			index = int(clarification)
			candidate_list.append(candidates[index - 1])
			return candidate_list
			
				

		#case two: a year response, return all years that match -- need to access title and check that
		elif len(clarification) == 4: 
			for candidate in candidates:
				current_title = self.titles[candidate][0]
				print(current_title) 
				if clarification in current_title:
					print(clarification)
					candidate_list.append(candidate)        
			return candidate_list
			

		#case three: a text clarification, we need to go through and check each movie title and if it matches, add it to the list
		else:
			for candidate in candidates: 
				current_title = self.titles[candidate][0]
				if clarification in current_title:
					candidate_list.append(candidate)
			return candidate_list

		#if all else fails, then we return our original list as we did not disambiguate

		return candidates

	############################################################################
	# 3. Movie Recommendation helper functions                                 #
	############################################################################

	@staticmethod
	def binarize(ratings, threshold=2.5):
		"""Return a binarized version of the given matrix.
		To binarize a matrix, replace all entries above the threshold with 1.
		and replace all entries at or below the threshold with a -1.
		Entries whose values are 0 represent null values and should remain at 0.
		Note that this method is intentionally made static, as you shouldn't use
		any attributes of Chatbot like self.ratings in this method.
		:param ratings: a (num_movies x num_users) matrix of user ratings, from
		 0.5 to 5.0
		:param threshold: Numerical rating above which ratings are considered
		positive
		:returns: a binarized version of the movie-rating matrix
		"""
		########################################################################
		# TODO: Binarize the supplied ratings matrix.                          #
		#                                                                      #
		# WARNING: Do not use self.ratings directly in this function.          #
		########################################################################

		# The starter code returns a new matrix shaped like ratings but full of
		# zeros.
		binarized_ratings = np.zeros_like(ratings)
		
		for i in range(len(ratings)):
			for j in range(len(ratings[0])):
				if ratings[i][j] > threshold:
					binarized_ratings[i][j] = 1
				elif ratings[i][j] <= threshold and ratings[i][j] != 0:
					binarized_ratings[i][j] = -1
		return binarized_ratings      
		
		

	def similarity(self, u, v):

		"""Calculate the cosine similarity between two vectors.
		You may assume that the two arguments have the same shape.
		:param u: one vector, as a 1D numpy array
		:param v: another vector, as a 1D numpy array
		:returns: the cosine similarity between the two vectors
		"""
		########################################################################
		# TODO: Compute cosine similarity between the two vectors.             #
		########################################################################
		

		similarity = u @ v / (np.linalg.norm(u) * np.linalg.norm(v) + 1e-10)
		########################################################################
		#                          END OF YOUR CODE                            #
		########################################################################
		return similarity

	def recommend(self, user_ratings, ratings_matrix, k=10, creative=False):
		"""Generate a list of indices of movies to recommend using collaborative
		 filtering.
		You should return a collection of `k` indices of movies recommendations.
		As a precondition, user_ratings and ratings_matrix are both binarized.
		Remember to exclude movies the user has already rated!
		Please do not use self.ratings directly in this method.
		:param user_ratings: a binarized 1D numpy array of the user's movie
			ratings
		:param ratings_matrix: a binarized 2D numpy matrix of all ratings, where
		  `ratings_matrix[i, j]` is the rating for movie i by user j
		:param k: the number of recommendations to generate
		:param creative: whether the chatbot is in creative mode
		:returns: a list of k movie indices corresponding to movies in
		ratings_matrix, in descending order of recommendation.
		"""

		########################################################################
		# TODO: Implement a recommendation function that takes a vector        #
		# user_ratings and matrix ratings_matrix and outputs a list of movies  #
		# recommended by the chatbot.                                          #
		#                                                                      #
		# WARNING: Do not use the self.ratings matrix directly in this         #
		# function.                                                            #
		#                                                                      #
		# For starter mode, you should use item-item collaborative filtering   #
		# with cosine similarity, no mean-centering, and no normalization of   #
		# scores.                                                              #
		########################################################################
	   
		# Populate this list with k movie indices to recommend to the user.
		# recommendations = []
		

		rating_map = {}
		
		nonzero_indices = [i for i, rating in enumerate(user_ratings) if rating != 0]

		for i, row in enumerate(ratings_matrix):
			rating_score = np.sum([self.similarity(row, ratings_matrix[y]) * user_ratings[y] for y in nonzero_indices])
			rating_map[i] = rating_score 

		[rating_map.pop(value) for value in nonzero_indices]
		
		recommendations = sorted(rating_map.keys(), key=lambda key: rating_map[key], reverse=True)[:k]

		########################################################################
		#                        END OF YOUR CODE                              #
		########################################################################
		return recommendations
		
	

	############################################################################
	# 4. Debug info                                                            #
	############################################################################

	def debug(self, line):
		"""
		Return debug information as a string for the line string from the REPL
		NOTE: Pass the debug information that you may think is important for
		your evaluators.
		"""
		debug_info = 'debug info'
		return debug_info

	############################################################################
	# 5. Write a description for your chatbot here!                            #
	############################################################################
	def intro(self):
		"""Return a string to use as your chatbot's description for the user.
		Consider adding to this description any information about what your
		chatbot can do and how the user can interact with it.
		"""
		return """
		This chatbot emulates Captain Jack Sparrow and will recommend you movies after 
		you have told it which movies you liked or disliked. You must talk about 5 movies
		before a recommendation can be made. All movies must be indicated with parentheses.
		"""

if __name__ == '__main__':
	print('To run your chatbot in an interactive loop from the command line, '
		  'run:')
	print('    python3 repl.py')
