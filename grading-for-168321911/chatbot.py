# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util




import numpy as np
import re
import random








# noinspection PyMethodMayBeStatic
class Chatbot:
   """Simple class to implement the chatbot for PA 6."""




   def __init__(self, creative=False):
       # The chatbot's default name is `moviebot`.
       # TODO: Give your chatbot a new name.
       self.name = 'Elmo'




       self.creative = creative




       self.movies_rated = 0
       self.recommendations = []
       self.restart_offered = False
       self.disambiguation = False
       self.candidate_titles = []
       self.candidate_indices = []
       self.new_candidates_titles = []
       self.disambiguate_line = ''
       self.arbitrary_index = 0




       # This matrix has the following shape: num_movies x num_users
       # The values stored in each row i and column j is the rating for
       # movie i by user j
       self.titles, ratings = util.load_ratings('data/ratings.txt')
       self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')




       # Binarize the movie ratings before storing the binarized matrix.
       self.ratings = self.binarize(ratings)
       self.user_ratings = np.zeros(len(self.titles))




       self.restart_responses = [
           "Oh boy, let's begin again! Elmo wants to hear about some movies you've seen!",
           "Yay! Let's try again! Elmo loves hearing about movies. What have you watched?",
           "Elmo thinks it's fun to start fresh! Tell Elmo about some movies you've seen before!",
           "Haha, Elmo loves restarting! What movies have you seen? Share with Elmo!",
           "Oh boy, let's do it again! Elmo wants to know about the movies you've watched!"
       ]




       self.confirm_yes_or_no_responses = [
           "Elmo's ears are little, and sometimes Elmo doesn't hear everything. Could you please say yes or no?",   
           "Oh dear, Elmo didn't quite understand that. Can you tell Elmo yes or no, please?",   
           "Elmo didn't quite catch that. Yes or no would be great! Could you help Elmo out?",   
           "Hmm, Elmo's not sure what you meant. Could you please say yes or no, so Elmo can understand?",   
           "Elmo loves hearing from you, but Elmo needs a little help. Can you respond with a yes or no, please?"
       ]
     
       self.more_info_responses = [
           "Oh no! Elmo didn't quite understand. Can you tell Elmo more about what types of movies you like?",
           "Elmo's not quite sure what you mean. Could you give Elmo some more information about your taste in movies?",
           "Uh oh, Elmo needs more information to help you. Can you tell Elmo more about the kinds of movies you enjoy?",
           "Elmo's confused. Could you provide more details about what you like in movies",
           "so Elmo can recommend some great ones?",
           "Oopsie! Elmo didn't catch that. Can you tell Elmo more about your favorite types of movies?"
       ]




       self.one_movie_responses = [
           "Oopsie, Elmo can only handle one movie at a time. Can you tell Elmo about one movie first?",
           "Elmo is excited to hear about your movie, but please tell Elmo about one movie at a time, okay?",   
           "Elmo's little ears can only handle one movie at a time. Could you please tell Elmo about one movie for now?",   
           "Elmo loves hearing about movies, but Elmo needs you to slow down. Please tell Elmo about one movie at a time, please.",   
           "Uh oh, Elmo can only process one movie at a time. Could you please share one movie with Elmo first?"
       ]




       self.unknown_movie_responses = [
           "Oh dear, Elmo doesn't know much about {}. Can you tell Elmo about another movie?",   
           "Elmo is stumped! Could you tell Elmo more about another movie? Elmo doesn't know much about {}.",
           "Uh oh, Elmo's not familiar with {}. Could you tell Elmo about a different movie instead?",   
           "Elmo loves learning about new movies, but Elmo doesn't know much about {}. Can you tell Elmo about another movie?",   
           "Elmo is sorry, but Elmo doesn't know much about {}. Could you share some details about another movie instead?"
       ]




       self.multiple_movie_responses = [
           "Oh my, Elmo found more than one movie called {}. Can you please clarify which one you mean?",   
           "Elmo is a little confused! Could you please clarify which {} movie you're referring to?",   
           "Uh oh, Elmo found multiple movies called {}. Can you provide some more details so Elmo knows which one you're talking about?",   
           "Elmo loves movies, but Elmo needs some help here. Which {} movie are you referring to?",   
           "Elmo found more than one {} movie in the database. Could you please clarify which one you're talking about?"
       ]




       self.movie_feelings_responses = [
           "Hmm, Elmo is not quite sure how you feel about {}. Could you give Elmo a little more information about it?",   
           "Elmo doesn't have a good sense of how you feel about {}. Can you tell Elmo more about it?",   
           "Elmo's not quite sure how you feel about {}. Could you please share more about your thoughts on it?",   
           "Elmo's a little unsure about how you feel about {}. Can you provide Elmo with more details?",   
           "Elmo's not quite getting a sense of your thoughts on {}. Could you elaborate a little more?"
       ]




       self.movie_recommendation_responses = [
           "Based off of what you've told Elmo, Elmo recommends that you watch {}!",   
           "Elmo thinks that you would really enjoy watching {}. That's Elmo's recommendation based on what you've shared with Elmo.", 
           "Hmm, based on what you've told Elmo, Elmo would recommend that you watch {}.",   
           "Elmo has a recommendation for you! Based on what you've shared with Elmo, Elmo thinks you would love watching {}.",   
           "Elmo has been thinking about it, and based on what you've told Elmo, Elmo recommends that you watch {}."
       ]




       self.pos_ask_for_another_movie_responses = [
           "Elmo is happy to hear that you liked {}. Could you tell Elmo about another movie you've seen?",   
           "Oh boy, Elmo is tickled pink to hear that you enjoyed {}! What other movies have you seen?", 
           "Elmo loves hearing about the movies you've watched! Could you tell Elmo about another one?",   
           "Wow, it sounds like you're a big movie buff! Elmo would love to know what other movies you've enjoyed besides {}. Could you share another one?",   
           "Elmo is so glad you enjoyed {}. Now, tell Elmo about another movie you've watched recently!",
           "Yippee, Elmo's so glad you liked {}! Can you think of any other movies that you enjoyed watching?"
       ]




       self.neg_ask_for_another_movie_responses = [   
           "Elmo understands that you didn't like {}. What about some other movies? Can you tell Elmo about a different movie you've seen?",   
           "It sounds like {} wasn't quite your cup of tea. That's okay! Can you tell Elmo about another movie you've seen?",   
           "Elmo is sorry to hear that you didn't enjoy {}. There are so many other movies to choose from. Can you tell Elmo about another one you've watched?",   
           "Elmo knows that not every movie is for everyone. If you didn't like {}, can you tell Elmo about another movie you've seen?",   
           "Elmo wants to help you find the perfect movie. If {} wasn't quite right, can you tell Elmo about another movie you've watched?"
       ]




       self.out_of_recommendations_responses = [   
           "Uh oh, it looks like Elmo has run out of recommendations. Would you like to start the process over and tell Elmo about some more movies you've watched?",   
           "Elmo has given you all the recommendations based on what you've told Elmo so far. Do you want to tell Elmo about some more movies and start over?",   
           "Elmo has exhausted all the options based on what you've shared. Would you like to start over and tell Elmo about some different movies?",   
           "Elmo has recommended all the movies that fit your preferences so far. Do you want to tell Elmo about some other movies and start the process over?",   
           "Elmo has given you all the recommendations Elmo can based on what you've shared. Would you like to start the process over and tell Elmo about some more movies?"
       ]




       self.next_recommendation = [   
           "Ta-da! Elmo's next recommendation is {}!",   
           "Elmo thinks you'll really like {}! That's the next movie Elmo recommends.",   
           "Elmo has another great recommendation for you! It's {}.",   
           "Drumroll, please! The next movie Elmo recommends for you is {}.",   
           "Elmo's next pick for you is {}! Get the popcorn ready!"
       ]




       self.no_next_recommendations_responses = [
           "Oh, Elmo understands! Would you like to start the movie magic all over again?",
           "Elmo hears you loud and clear! Does that mean you want to start over with more movies?",
           "Aww, Elmo is sorry to hear that. Should we try again with some different movies?"
       ]


       self.arbitrary_input = [
           "Hmm, Elmo doesn't want to talk about that topic right now. Let's talk about movies!",
           "Elmo not sure that's the best topic for us to discuss right now. Maybe we can talk about movies!",
           "Oh boy, that's not really what Elmo had in mind. Let's switch gears and chat about movies instead!",
           "Hmm, Elmo not so interested in talking about that right now. Let's chat about movies!",
           "Sorry, Elmo not up for discussing that topic at the moment. Let us focus on movies instead!"
       ]




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




       greeting_message = "Hiya there! Elmo's the name, and recommending movies is Elmo's game!\n" \
       "Let Elmo know how you're feeling about the movies you've seen, and Elmo will recommend some new ones for you to enjoy!"




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




       goodbye_message = "Aww, Elmo had such a great time recommending movies to you! \n" \
       "Don't forget to grab some popcorn and enjoy the show! Bye-bye for now, friend!"




       ########################################################################
       #                          END OF YOUR CODE                            #
       ########################################################################
       return goodbye_message




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
           response = "Not processed."
           titles = self.extract_titles(line)
           if self.restart_offered:
               if line.lower().strip() == "yes":
                   self.movies_rated = 0
                   self.recommendations = []
                   self.restart_offered = False
                   self.candidate_titles = []
                   self.user_ratings = np.zeros(len(self.titles))
                   response = "Let's start over! Tell me about some movies you've watched."
               elif line.lower().strip() == "no":
                 # TODO: figure out how to exit chat bot from here or force user to type :quit?
                   response = self.goodbye()
               else:
                   response = "I didn't quite catch that. Please respond yes or no."








           elif self.disambiguation:
               self.candidate_titles = self.new_candidates_titles
               self.candidate_indices = self.disambiguate(line, self.candidate_indices)
               if len(self.candidate_indices) == 1:
                   title = self.candidate_titles[0]
                   self.disambiguation = False
                   self.candidate_titles = []
                   self.new_candidates_titles = []
                   line = self.disambiguate_line
                   #print("the line was ", line)
                   sentiment = self.extract_sentiment(line)
                   if sentiment == 0:
                       response = random.choice(self.movie_feelings_responses).format(title)
                   else:
                       self.user_ratings[self.candidate_indices[0]] = sentiment
                       self.movies_rated += 1
                       if self.movies_rated >= 5:
                           self.recommendations = self.recommend(self.user_ratings, self.ratings)
                           recommended_movie = self.titles[self.recommendations.pop(0)][0]
                           response = f"{random.choice(self.movie_recommendation_responses)}\n" \
                                          "Would you like another recommendation? Please tell Elmo yes or no.\n" \
                                          "You could also type :quit to quit.".format(recommended_movie)
                       elif sentiment == 1:
                           response = random.choice(self.pos_ask_for_another_movie_responses).format(title)
                       else:
                           response = random.choice(self.neg_ask_for_another_movie_responses).format(title)


               else:
                   response = "Which one did you mean?: " + str(self.candidate_titles)
                   self.disambiguation = True
           elif self.movies_rated < 5:
               self.arbitrary_index += 1
               if len(titles) == 0:
                   response = self.arbitrary_input[self.arbitrary_index % len(self.arbitrary_input)]
               elif len(titles) > 1:
                   response = "Please only tell me about one movie at a time!"
               else:
                   title = titles[0]
                   movie_indices = self.find_movies_by_title(title)
                   if len(movie_indices) == 0:
                       response = "I don't know much about {}, could you tell me about another movie?".format(title)
                   elif len(movie_indices) > 1:
                       candidates = []
                       candidates_i = []
                       for i in range(len(movie_indices)):
                           title = self.titles[movie_indices[i]][0]
                           index = movie_indices[i]
                           candidates.append(title)
                           candidates_i.append(index)
                       self.candidate_indices = candidates_i
                       self.candidate_titles = candidates
                       self.disambiguation = True
                       self.disambiguate_line = line
                       response = "Which one did you mean?: " + str(candidates)
                   else:
                       sentiment = self.extract_sentiment(line)
                       if sentiment == 0:
                           response = random.choice(self.movie_feelings_responses).format(title)
                       else:
                           self.user_ratings[movie_indices[0]] = sentiment
                           self.movies_rated += 1
                           if self.movies_rated >= 5:
                               self.recommendations = self.recommend(self.user_ratings, self.ratings)
                               recommended_movie = self.titles[self.recommendations.pop(0)][0]
                               response = f"{random.choice(self.movie_recommendation_responses)}\n" \
                                          "Would you like another recommendation? Please tell Elmo yes or no.\n" \
                                          "You could also type :quit to quit.".format(recommended_movie)
                           elif sentiment == 1:
                               response = random.choice(self.pos_ask_for_another_movie_responses).format(title)
                           else:
                               response = random.choice(self.neg_ask_for_another_movie_responses).format(title)
           else:
               if line.lower().strip() == "yes":
                   if len(self.recommendations) == 0:
                       self.restart_offered = True
                       response = "Looks like I'm all out of recommendations! Do you want to restart the recommendation process?"
                   else:
                       recommended_movie = self.titles[self.recommendations.pop(0)][0]
                       response = "My next recommendation is {}!\n" \
                                "Would you like another recommendation? Please reply yes or no.\n" \
                                "You could also type :quit to quit.".format(recommended_movie)
               elif line.lower().strip() == "no":
                   self.restart_offered = True
                   response = "Understandable. Do you want to restart the recommendation process?"
               else:
                   response = "I didn't quite catch that. Please respond yes or no."
               
       else:
           response = "Not processed."
           titles = self.extract_titles(line)
           if self.restart_offered:
               if line.lower().strip() == "yes":
                   self.movies_rated = 0
                   self.recommendations = []
                   self.restart_offered = False
                   self.user_ratings = np.zeros(len(self.titles))
                   response = random.choice(self.restart_responses)
               elif line.lower().strip() == "no":
                   response = "Elmo understands you don't want to restart the recommendation system.\n" \
                   "But Elmo is always here to help! Remember, you are the one with the power to end our conversation.\n"\
                   "Just type :quit to say goodbye to Elmo. Elmo is happy to stay and chat!"
               else:
                   response = random.choice(self.confirm_yes_or_no_responses)
           elif self.movies_rated < 5:
               if len(titles) == 0:
                   response = random.choice(self.more_info_responses)
               elif len(titles) > 1:
                   response = random.choice(self.one_movie_responses)
               else:
                   title = titles[0]
                   movie_indices = self.find_movies_by_title(title)
                   if len(movie_indices) == 0:
                       response = random.choice(self.unknown_movie_responses).format(title)
                   elif len(movie_indices) > 1:
                       response = random.choice(self.multiple_movie_responses).format(title)
                   else:
                       sentiment = self.extract_sentiment(line)
                       if sentiment == 0:
                           response = random.choice(self.movie_feelings_responses).format(title)
                       else:
                           self.user_ratings[movie_indices[0]] = sentiment
                           self.movies_rated += 1
                           if self.movies_rated >= 5:
                               self.recommendations = self.recommend(self.user_ratings, self.ratings)
                               recommended_movie = self.titles[self.recommendations.pop(0)][0]
                               response = f"{random.choice(self.movie_recommendation_responses)}\n" \
                                          "Would you like another recommendation? Please tell Elmo yes or no.\n" \
                                          "You could also type :quit to quit.".format(recommended_movie)
                           elif sentiment == 1:
                               response = random.choice(self.pos_ask_for_another_movie_responses).format(title)
                           else:
                               response = random.choice(self.neg_ask_for_another_movie_responses).format(title)
           else:
               if line.lower().strip() == "yes":
                   if len(self.recommendations) == 0:
                       self.restart_offered = True
                       response = random.choice(self.out_of_recommendations_responses)
                   else:
                       recommended_movie = self.titles[self.recommendations.pop(0)][0]
                       response = f"{random.choice(self.next_recommendation)}\n" \
                                  "Would you like another recommendation? Please tell Elmo yes or no.\n" \
                                  "You could also type :quit to quit.".format(recommended_movie)
               elif line.lower().strip() == "no":
                   self.restart_offered = True
                   response = random.choice(self.no_next_recommendations_responses)
               else:
                   response = random.choice(self.confirm_yes_or_no_responses)




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
       ########################################################################
       # TODO: Preprocess the text into a desired format.                     #
       # NOTE: This method is completely OPTIONAL. If it is not helpful to    #
       # your implementation to do any generic preprocessing, feel free to    #
       # leave this method unmodified.                                        #
       ########################################################################




       ########################################################################
       #                             END OF YOUR CODE                         #
       ########################################################################




       return text




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
       if self.creative:
           titles = [title[1:-1] for title in re.findall(r'".+?"', preprocessed_input)]
           if titles:
               return titles
           else:
               possible_substrings = []
               tokens = preprocessed_input.split()
               for i in range(len(tokens)):
                   prev1 = None
                   prev2 = None
                   for j in range(i, len(tokens)):
                       substr1 = []
                       substr2 = []
                       if prev1:
                           substr1.append(prev1)
                       if prev2:
                           substr2.append(prev2)
                       token = tokens[j]
                       token = token.replace("!", "")
                       token = token.replace(".", "")
                       substr1.append(token)
                       substr2.append(tokens[j])
                       new1 = (" ".join(substr1))
                       new2 = (" ".join(substr2))
                       possible_substrings.append(new1)
                       possible_substrings.append(new2)
                       prev1 = new1
                       prev2 = new2
               matches = []
               stop_words = ['the', 'an', 'a']
               for elem in self.titles:
                   title = elem[0].lower()
                   for candidate in possible_substrings:
                       real_candidate = candidate
                       candidate = candidate.lower()
                       if candidate.lower() == title or title[:-7] == candidate.lower():
                           if real_candidate not in matches:
                               matches.append(real_candidate)
                       elif candidate.lower().split()[0] in stop_words:
                           stop_word = candidate.lower().split()[0]
                           date = candidate.split()[-1] if candidate.split()[-1][0] == '(' else ''
                           if date:
                               modified_title = candidate[len(stop_word) + 1:-7] + f", {stop_word} {date}"
                           else:
                               modified_title = candidate[len(stop_word) + 1:] + f", {stop_word}"
                           if candidate == modified_title or title[:-7] == modified_title:
                               matches.append(real_candidate)
               return matches
       else:
           return [title[1:-1] for title in re.findall(r'".+?"', preprocessed_input)]




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
       if self.creative:
           title = title.lower()
           stop_words = ['the', 'an', 'a']
           foreign_stop_words = ['la', 'el', 'los', 'las', 'il', 'lo', "l'", 'gli', 'i', 'le', 'les', 'der', 'die', 'das']
           titles_indices = []
        
           for i, elem in enumerate(self.titles):
               cur_title = elem[0].lower()
               if cur_title == title or cur_title[:-7] == title:
                   titles_indices.append(i)
               elif title in cur_title:
                   if cur_title.split()[0] == title.split()[0]:
                    titles_indices.append(i)
                   if cur_title.find('a.k.a.') != -1:
                       pos = cur_title.find('a.k.a.')
                       start_of_foreign_title = pos + 7
                       foreign_title = cur_title[start_of_foreign_title:]
          
                       end = start_of_foreign_title + foreign_title.find(")")
                       foreign_title = cur_title[start_of_foreign_title:end]
                       if title == foreign_title:
                           titles_indices.append(i)
                   else: 
                       start = cur_title.find('(')
                       end = cur_title.find(')')
                       foreign_title = cur_title[start+1:end]
                       if title == foreign_title:
                           titles_indices.append(i)
               elif title.split()[0] in stop_words or title.split()[0] in foreign_stop_words:
                   stop_word = title.split()[0]
                   start = cur_title.find('(')
                   end = cur_title.find(')')
                   foreign_title = cur_title[start+1:end]
                   date = title.split()[-1] if title.split()[-1][0] == '(' else ''
                   if date:
                       modified_title = title[len(
                           stop_word) + 1:-7] + f", {stop_word} {date}"
                   else:
                       modified_title = title[len(
                           stop_word) + 1:] + f", {stop_word}"
                   if cur_title == modified_title or cur_title[:-7] == modified_title or foreign_title == modified_title:
                       titles_indices.append(i)
           return titles_indices
       else:
           title = title.lower()
           stop_words = ['the', 'an', 'a']
           titles_indices = []
           for i, elem in enumerate(self.titles):
               cur_title = elem[0].lower()
               if cur_title == title or cur_title[:-7] == title:
                   titles_indices.append(i)
               elif self.creative and title in cur_title:
                   if cur_title.split()[0] == title.split()[0]:
                       titles_indices.append(i)
               elif title.split()[0] in stop_words:
                   stop_word = title.split()[0]
                   date = title.split()[-1] if title.split()[-1][0] == '(' else ''
                   if date:
                       modified_title = title[len(
                           stop_word) + 1:-7] + f", {stop_word} {date}"
                   else:
                       modified_title = title[len(
                           stop_word) + 1:] + f", {stop_word}"
                   if cur_title == modified_title or cur_title[:-7] == modified_title:
                       titles_indices.append(i)
           return titles_indices




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
       stems = {
           "enjoyed": "enjoy",
           "disliked": "dislike",
           "hated" : "hate",
           "loved": "love",
           "liked": "like"
       }
       negation_words = ["didn't", "never", "not", "don't"]
       # Replace movie title with nothing
       preprocessed_input = preprocessed_input.replace(
           self.extract_titles(preprocessed_input)[0], "")




       tokens = preprocessed_input.split()
       positive_count = 0
       negative_count = 0
       negation_words_count = 0
       for token in tokens:
           t = token.lower()
           if t in negation_words:
               negation_words_count += 1
           if t in stems:
               t = stems[t]
           if t in self.sentiment:
               if self.sentiment[t] == 'pos':
                   positive_count += 1
               else:
                   negative_count += 1
       if positive_count > negative_count:
           if negation_words_count % 2 == 0:
               return 1
           else:
               return -1
       elif negative_count > positive_count:
           if negation_words_count % 2 == 0:
               return -1
           else:
               return 1
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
       pass
      


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


      min_dis = max_distance
      min_list = []


      title = title.lower()


      for i in range(len(self.titles)):
          cur_title = self.titles[i][0].lower()


          A = np.zeros( (len(title)+1, len(cur_title)-6 )) #initializes matrix with appropriate dimensions, but with all-zero values




          for j in range (len(title)+1): #fills in values for mispelled title column
              A[j][0] = j




          for k in range (len(cur_title) - 6): #fills in values for movie title row
              A[0][k] = k




          for l in range (1, len(title)+1):




              for o in range (1, len(cur_title)-6):




                  A[l][o] = min((A[l-1][o]+1), (A[l][o-1]+1))
                  if cur_title[o-1] == title[l-1]:
                      A[l][o] = min(A[l-1][o-1], A[l][o])
                  else:
                      A[l][o] = min(A[l-1][o-1] + 2, A[l][o])




          edit_dis = A[len(title)][len(cur_title)-7]
         


          if (edit_dis < min_dis):
              min_list = [self.find_movies_by_title(cur_title)[0]]
              #print(cur_title)
              min_dis = edit_dis
              #if min_dis == 1 and title == "te":
                 # print(cur_title)
           #    print(min_dis)


          if edit_dis == min_dis:
              min_list.append(self.find_movies_by_title(cur_title)[0])
              #print(cur_title)










          #is this index's edit-distance less than the current minimum? (and less than max edit distance param)
          # then scrap old list and create new one w/ just this one




          #ties? add index to current list




          #greater? ignore index
      return min_list







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
       clarification = clarification.lower()
       indices = []
       for candidate in candidates:
           full = self.titles[candidate][0]
           date = full[-6:].strip("()")
           date_with_parentheses = full[-6:]
           title = full[:-6].lower()
           if clarification == full:
               self.new_candidates_titles.append(full)
               indices.append(candidate)
               # print("1 if")
           elif clarification == title:
               self.new_candidates_titles.append(full)
               indices.append(candidate)
               # print("2 if")
           elif clarification == date:
               self.new_candidates_titles.append(full)
               indices.append(candidate)
               # print("3 if")
           elif clarification == date_with_parentheses:
               self.new_candidates_titles.append(full)
               indices.append(candidate)
               # print("4 if")
           elif clarification in title and clarification not in date:
               self.new_candidates_titles.append(full)
               indices.append(candidate)
               # print("5 if")
           elif clarification in title and clarification in date:
               self.new_candidates_titles.append(full)
               indices.append(candidate)
               # print("6 if")
          
       # print(indices)
       return indices






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
       temp = np.where((0 < ratings) & (ratings <= 2.5), -1, ratings)
       binarized_ratings = np.where(temp > 2.5, 1, temp)




       ########################################################################
       #                        END OF YOUR CODE                              #
       ########################################################################
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
       similarity = 0
       if np.dot(u,v) == 0:
           return similarity
       else:
           return np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))
       ########################################################################
       #                          END OF YOUR CODE                            #
       ########################################################################
     
       # return similarity




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
       recommendations = []
       rated_movies = np.nonzero(user_ratings)[0]




       # def calculate_rating(movie_rating, user_rating):
       #     # sim = self.similarity(movie_rating, user_rating)
       #     # return np.dot(sim, user_ratings)
       #     print(self.similarity(movie_rating, user_rating))




       # np.apply_along_axis(calculate_rating, 1, np.array([[1,-1,0],[1,-1,1], [0,1,1]]), np.array([1,-1, 0]))
       ratings = []
       for i in range(len(ratings_matrix)):
           if i not in rated_movies:
               rating_sum = 0
               for j in rated_movies:
                   sim = self.similarity(ratings_matrix[i], ratings_matrix[j])
                   rating_sum += sim * user_ratings[j]
               ratings.append((i, rating_sum))




       indices = sorted(ratings, key=lambda x: x[1], reverse=True)
       for i in range(k):
           recommendations.append(indices[i][0])




       # for movie in ratings_matrix:




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
       Your task is to implement the chatbot as detailed in the PA7
       instructions.
       Remember: in the starter mode, movie names will come in quotation marks
       and expressions of sentiment will be simple!
       TODO: Write here the description for your own chatbot!
       """






if __name__ == '__main__':
   print('To run your chatbot in an interactive loop from the command line, '
         'run:')
   print('    python3 repl.py')









