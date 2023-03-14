# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util
import porter_stemmer
import numpy as np
import re
import random

# noinspection PyMethodMayBeStatic


class Chatbot:
    """Simple class to implement the chatbot for PA 7."""

    def __init__(self, creative=False):
        self.name = 'FlixFinder'
        self.creative = creative

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')

        # Binarize the movie ratings matrix.
        ratings = self.binarize(ratings)
        # self.inputs = 0

        # Store the binarized matrix.
        self.ratings = ratings

        # Create other variables for our implementation
        self.movie_titles = []
        self.movie_titles_without_years = []
        articles = ['the', 'an', 'a', 'la', 'el', 'le', 'les', "l'", "lo", "il", "le"]
        for x in self.titles:
          t = x[0]
          t_no_year = x[0][:len(t) - 7]
          x_split = x[0].split()
          pos_article = len(x_split) - 2
          if x_split[pos_article].lower() in articles and ',' in x_split[pos_article - 1].lower():
            x_split[pos_article - 1] = x_split[pos_article - 1].replace(',', '')
            x_split = [x_split[pos_article]] + x_split[0:pos_article] + [x_split[len(x_split) - 1]]
            t = ' '.join(x_split)
            t_no_year = t[:len(t) - 7]
          t = t.lower()
          t_no_year = t_no_year.lower()
          self.movie_titles.append(t)    
          self.movie_titles_without_years.append(t_no_year)     

        self.ratings_collected = [] #list()
        self.recommend_list = [] #list()
        self.recommending = False
        self.starters = ["Based on those inputs, I recommend ",
                            "Given what you told me, I think you would like ",
                            "I suggest ", 
                            " From what you shared, I think you would like "]

        self.finishers = [" Would you like another rec?",
                             " How about another suggestion?",
                             " Need any more ideas?",
                             " One more? ;)"]
        self.clarifying = False
        self.clarifying_toomany_times = 0
        self.candidate_movies = []
        self.clarifying_sentiment = 0
        self.misspell_question = False
        self.misspell_offer = []
        self.misspell_sentiment = 0

    def greeting(self):
        """Return a message that the chatbot uses to greet the user."""
        num = random.randint(0, 6)
        greeting_message = [
            "Hello!", "Welcome!", "Hiiiiii", "Hola!", "привет!", "Bonjour!",  "'ello!"
        ]
        return greeting_message[num]

    def goodbye(self):
        """Return a message that the chatbot uses to bid farewell to the user."""
        num = random.randint(0, 3)
        greeting_message = [
            "Goodbye!", "See you later!!", "Thanks for visiting!", "Ciao!"
        ]
        return greeting_message[num]

    def process(self, line):
        """Process a line of input from the REPL and generate a response.

        This is the method that is called by the REPL loop directly with user
        input.

        Takes the input string from the REPL and call delegated functions that
          1) extract the relevant information, and
          2) transform the information into a response to the user.

        Example:
          resp = chatbot.process('I loved "The Notebook" so much!!')
          print(resp) // prints 'So you loved "The Notebook", huh?'

        :param line: a user-supplied line of text
        :returns: a string containing the chatbot's response to the user input

        :param user_ratings: a binarized 1D numpy array of the user's movie
            ratings
        :param ratings_matrix: a binarized 2D numpy matrix of all ratings, where
          `ratings_matrix[i, j]` is the rating for movie i by user j
        """
        response = ""

        ###### CREATIVE MODE ############################## 
        if self.creative:
            if self.recommending:
              if "no" in line.lower() or "not" in line.lower() or "nah" in line.lower() or "stop" in line.lower():
                self.recommending = False
                self.ratings_collected = []
                return np.random.choice([
                  "Okay! Hope you discover a new favorite film! Feel free to start again.",
                  "Sounds good, let me know when you've watched the films and I can recommend you more!",
                  "Okay, hope these suggestions were helpful!",
                  "Got it! Let's move on.",
                  "Alright! Hope you like my recommendations!",
                ]) 
              elif "yes" in line.lower() or "yeah" in line.lower() or "sure" in line.lower() or "okay" in line.lower():
                if len(self.recommend_list) == 0:
                    self.recommending = False
                    self.ratings_collected = []
                    return np.random.choice([
                      "Sorry, that's all the movies we have to recommend. Tell me about a new movie if you want more!",
                      "We've run out of films to recommend :( We can start over if you want new recommendations!",
                      "That's all we have! Tell me what you think about other movies and I can recommend you more!",
                      "That's it! I can give you more movies if you tell me what you think about other movies."
                    ]) 
                else:
                    num = random.randint(0, 3)
                    state = "\n" + "Another movie you might like is \"{}\"".format(self.recommend_list[0]) + self.finishers[num]
                    self.recommend_list.pop(0)
                    # self.recommending = True
                    return state
              else:
                  return np.random.choice([
                      "I'm not sure what you'd like to do next. Would you like another recommendation?",
                      "I don't quite understand if you would like another recommendation. Can you clarify again?",
                      "Hmm, I'm confused by what to do next. I still have other recommendations, do you want to hear them?"
                    ]) 
              
            if self.clarifying:
                movie_indices = self.disambiguate(line, self.candidate_movies)
                if len(movie_indices) == 1:
                    if self.clarifying_sentiment == 0:
                        return "I'm sorry, I'm not sure if you liked \"{}\". Tell me about it again.".format(self.titles[movie_indices[0]][0])                        
                    if self.clarifying_sentiment == 1:
                        if len(self.ratings_collected) < 5:
                            response += " Okay, you liked \"{}\". Got it! What's another!".format(self.titles[movie_indices[0]][0])
                        # we have our 5 movie
                        else:
                            response += " So you liked \"{}\". Cool!".format(self.titles[movie_indices[0]][0])
                    elif self.clarifying_sentiment == -1:
                        if len(self.ratings_collected) < 5:
                            response += " Okay, you liked \"{}\". Got it! Tell me another one!".format(self.titles[movie_indices[0]][0])
                        # we have our 5 movie
                        else:
                            response += " So you liked \"{}\". Cool!".format(self.titles[movie_indices[0]][0])
                    rating_tuple = (movie_indices[0], self.clarifying_sentiment)
                    self.ratings_collected.append(rating_tuple)
                    self.clarifying = False
                    self.candidate_movies = []
                    self.clarifying_sentiment = 0
                    return response
                elif len(movie_indices) > 1:
                    candidate_list = [self.titles[ind][0] for ind in movie_indices]
                    response += "We narrowed it down to these {}. Can you clarify once again?".format(candidate_list)
                    self.candidate_movies = movie_indices
                    return response
                elif len(movie_indices) == 0:
                    self.clarifying_toomany_times += 1
                    if self.clarifying_toomany_times > 1:
                        self.clarifying_toomany_times = 0
                        self.clarifying = False
                        return "Okay sorry I didn't get that. Tell me about another movie to continue :)"
                    else:
                        return "I'm still not sure which you mean. Do you know the year it came out? Or the full title? That will help!"
            
            # If originally misspelled, we ask if they mean X yes or no
            # or we ask to index which one they mean
            if self.misspell_question:
                # question 1
                if len(self.misspell_offer) == 1:
                    if "yes" in line.lower() or "yeah" in line.lower() or "sure" in line.lower() or "okay" in line.lower():
                        movie = self.titles[self.misspell_offer[0]][0]
                        if self.misspell_sentiment == 0:
                            return "I'm sorry, I'm not sure if you liked \"{}\". it. Tell me more about it.".format(movie)                        
                        if self.misspell_sentiment == 1:
                            if len(self.ratings_collected) < 5:
                                response += " Okay, you liked \"{}\". Got it! Tell me another one!".format(movie)
                            # we have our 5 movie
                            else:
                                response += " So you liked \"{}\". Cool!".format(movie)
                        elif self.misspell_sentiment == -1:
                            if len(self.ratings_collected) < 5:
                                response += " Okay, you liked \"{}\". Got it! Tell me another one!".format(movie)
                            # we have our 5 movie
                            else:
                                response += " So you liked \"{}\". Cool!".format(self.misspell_offer[0])
                        rating_tuple = (self.misspell_offer[0], self.misspell_sentiment)
                        self.ratings_collected.append(rating_tuple)
                        self.misspell_question = False
                        self.misspell_offer = []
                        self.misspell_sentiment = 0
                        return response 
                    else:
                        return " Sorry then. Try to tell me again how you feel about this movie. Spell carefully pls"
                # question 2
                else:
                    rating_tuple = (self.misspell_offer[int(line)], self.misspell_sentiment)
                    self.ratings_collected.append(rating_tuple)
                    self.misspell_question = False
                    self.misspell_offer = []
                    self.misspell_sentiment = 0
                    return "Got it, thank you!"

            titles = self.extract_titles(line)
            sentiment = self.extract_sentiment(line)

            # arbitrary inputs
            if len(titles) == 0:
                arbit = False
                if "do you" in line.lower() or "can you" in line.lower() or "will you" in line.lower() or "could you" in line.lower() or "would you" in line.lower():
                    arbit = True
                    response += "I might...I might not. Maybe, we'll never know hehe"
                elif "what is" in line.lower() or "are you" in line.lower() or "how are" in line.lower() or "how is" in line.lower() or "what are" in line.lower() or "where is" in line.lower():
                    arbit = True
                    response += "I'm working on connecting to the Internet. Soon I will be able to answer that! But for now, I only know movies."

                # can add more choices of dialogue per sentiment
                if sentiment == 1 and not arbit:
                    response += "And that's wonderful to hear! When you're ready, tell me about a film to get started :)"
                elif sentiment == -1 and not arbit:
                    response +=  "And I'm so sorry to hear that :( When you're ready, please tell me about a film to get started."
                elif sentiment == 0 and not arbit:                    
                    response += "Okay! I'm FlixFinder...tell me about movies!"
                elif len(response) == 0: 
                    response += "You have left me speechless, so let's go back to movies!"

            # more than one movie mentioned
            elif len(titles) > 1:
                pairs = self.extract_sentiment_for_movies(line)
                for pair in pairs:
                    # pair = pairs[i]
                    movie = pair[0]
                    movie_ind = self.find_movies_by_title(movie)
                    sentiment = pair[1]
                    if sentiment == -1:
                        rating_tuple = (movie_ind, sentiment)
                        self.ratings_collected.append(rating_tuple)
                        response += " I see you didn't like {} and".format(movie)
                    elif sentiment == 1:
                        rating_tuple = (movie_ind, sentiment)
                        self.ratings_collected.append(rating_tuple)
                        response += " I see you liked {}".format(movie)
                    else:
                        response += " I'm sorry, I'm not sure if you liked {}. Tell me more about it.".format(movie)           

            # exactly one film mentioned
            else:
                movies = self.find_movies_by_title(titles[0])
                # no movies found -> check if they misspelled
                if len(movies) == 0:
                    movies_approx = self.find_movies_closest_to_title(titles[0], 3)
                    if len(movies_approx) == 0:
                        response += "Sorry, I've never heard of {}... Tell me about another movie.".format(titles[0])
                    elif len(movies_approx) == 1:
                        response += "Did you mean {}?".format(self.titles[movies_approx[0]][0])
                        self.misspell_question = True
                        self.misspell_offer = movies_approx
                        self.misspell_sentiment = sentiment
                    else:
                        response += "Which did you mean {}? Use an index please.".format(self.titles[movies_approx])
                        self.misspell_question = True
                        self.misspell_offer = movies_approx
                        self.misspell_sentiment = sentiment
                # multiples movies found
                elif len(movies) > 1:
                    response += "I found more than one movie called \"{}\". Can you clarify which of these titles you mean? Here is a list of all the results:".format(titles[0])
                    for ind in movies:
                      response += "\n" + self.titles[ind][0]
                    self.clarifying = True
                    self.candidate_movies = movies
                    self.clarifying_sentiment = sentiment
                # one movie found
                elif len(movies) == 1:
                    if sentiment == -1:
                        rating_tuple = (movies[0], sentiment)
                        self.ratings_collected.append(rating_tuple)
                        if len(self.ratings_collected) < 5:
                            response += " So you didn't like \"{}\". Got it! Tell me another one!".format(titles[0])
                        # we have our 5 movies
                        else:
                            response += " So you didn't like \"{}\". Got it!".format(titles[0])
                    elif sentiment == 1:
                        rating_tuple = (movies[0], sentiment)
                        self.ratings_collected.append(rating_tuple)
                        if len(self.ratings_collected) < 5:
                            response += " Great, you liked \"{}\"! Tell me what you thought about another movie.".format(titles[0])
                        # we have our 5 movies
                        else:
                            response += " Great, you liked \"{}\"!".format(titles[0])
                    else:
                        # should we catch a response? ie "I liked it"
                        response += "I'm sorry, I'm not sure if you liked {}. Tell me more about it.".format(titles[0])

            if len(self.ratings_collected) < 5:
                return response
            else:                
                # first movie we recommend. rest happens at the top of starter mode code
                user_ratings = np.zeros(9125)
                for ind, senti in self.ratings_collected:
                    user_ratings[ind] = senti
                rec_indices = self.recommend(user_ratings, self.ratings)
                self.recommend_list = [self.titles[ind][0] for ind in rec_indices]
                num = random.randint(0, 3)
                response += "\n" + self.starters[num] + "\"{}\"".format(self.recommend_list[0]) + self.finishers[num]
                self.recommend_list.pop(0)
                self.recommending = True
                return response  

        ###### STARTER MODE ##############################
        else:
            if self.recommending:
              if "no" in line.lower() or "not" in line.lower() or "nah" in line.lower() or "stop" in line.lower():
                self.recommending = False
                self.ratings_collected = [] 
                return np.random.choice([
                  "Okay! Hope you discover a new favorite film! Feel free to start again.",
                  "Sounds good, let me know when you've watched the films and I can recommend you more!",
                  "Okay, hope these suggestions were helpful!",
                  "Got it! Let's move on.",
                  "Alright! Hope you like my recommendations!",
                ]) 
              elif "yes" in line.lower() or "yeah" in line.lower() or "sure" in line.lower() or "okay" in line.lower():
                if len(self.recommend_list) == 0:
                    self.recommending = False
                    self.ratings_collected = []  
                    return np.random.choice([
                      "Sorry, that's all the movies we have to recommend. Tell me about a new movie if you want more!",
                      "We've run out of films to recommend :( We can start over if you want new recommendations!",
                      "That's all we have! Tell me what you think about other movies and I can recommend you more!",
                      "That's it! I can give you more movies if you tell me what you think about other movies."
                    ]) 
                else:
                    num = random.randint(0, 3)
                    state = np.random.choice([
                      "\n" + "Another movie you might like is \"{}\"".format(self.recommend_list[0]) + self.finishers[num],
                      "\n" + "We also recommend: \"{}\"".format(self.recommend_list[0]) + self.finishers[num],
                      "\n" + "One other thing you might be interested in is \"{}\"".format(self.recommend_list[0]) + self.finishers[num],
                      "\n" + "You might also enjoy \"{}\"".format(self.recommend_list[0]) + self.finishers[num],
                      "\n" + "\"{}\" might be a good movie for you! Would you like another recommendation?".format(self.recommend_list[0])
                    ]) 
                    self.recommend_list.pop(0)
                    # self.recommending = True
                    return state
              else:
                  return np.random.choice([
                      "I'm not sure what you'd like to do next. Would you like another recommendation?",
                      "I don't quite understand if you would like another recommendation. Can you clarify again?",
                      "Hmm, I'm confused by what to do next. I still have other recommendations, do you want to hear them?"
                    ]) 
                
            if self.clarifying:
                movie_indices = self.disambiguate(line, self.candidate_movies)
                if len(movie_indices) == 1:
                    if self.clarifying_sentiment == 0:
                        return np.random.choice([
                          "I'm sorry, I'm not sure if you liked \"{}\". it. Tell me more about it.".format(self.titles[movie_indices[0]][0]),
                          "Hmm, I can't tell exactly how you feel about \"{}\". Can you clarify?".format(self.titles[movie_indices[0]][0]),
                          "I see, do you mind talking more specifically about your opinion of \"{}\"?".format(self.titles[movie_indices[0]][0]),
                          "Do you mind clarifying how you feel about \"{}\"? I didn't fully get what you meant.".format(self.titles[movie_indices[0]][0])      
                        ])                    
                    if self.clarifying_sentiment == 1:
                        if len(self.ratings_collected) < 5:
                            response += np.random.choice([
                              "Okay, you liked \"{}\". Got it! Tell me another one!".format(self.titles[movie_indices[0]][0]),
                              "I see you liked \"{}\". Let's hear more!".format(self.titles[movie_indices[0]][0]),
                              "Cool! You liked \"{}\". I'm curious to hear about your opinion on more movies!".format(self.titles[movie_indices[0]][0]),
                              "Ooh nice! You liked \"{}\". Any other movies?".format(self.titles[movie_indices[0]][0])
                            ])
                        # we have our 5 movie
                        else:
                            response += "So you liked \"{}\". Cool!".format(self.titles[movie_indices[0]][0])
                    elif self.clarifying_sentiment == -1:
                        if len(self.ratings_collected) < 5:
                            response += "Okay, you liked \"{}\". Got it! Tell me another one!".format(self.titles[movie_indices[0]][0])
                        # we have our 5 movie
                        else:
                            response += "So you liked \"{}\". Cool!".format(self.titles[movie_indices[0]][0])
                    rating_tuple = (movie_indices[0], self.clarifying_sentiment)
                    self.ratings_collected.append(rating_tuple)
                    self.clarifying = False
                    self.candidate_movies = []
                    self.clarifying_sentiment = 0
                    return response
                elif len(movie_indices) > 1:
                    response += " We narrowed it down to these. Can you clarify once again?"
                    self.candidate_movies = movie_indices
                    return response
                elif len(movie_indices) == 0:
                    self.clarifying_toomany_times += 1
                    if self.clarifying_toomany_times > 1:
                        self.clarifying_toomany_times = 0
                        self.clarifying = False
                        return "Please tell me about a new film -- in quotation marks -- to continue :)"
                    else:
                        return " I'm still not sure which you mean. Do you know the year it came out? Or the full title? That will help!"
                  
            titles = self.extract_titles(line)
            sentiment = self.extract_sentiment(line)

            # arbitrary inputs
            if len(titles) == 0:
                if sentiment == 1:
                    response += "That's wonderful to hear! When you're ready, tell me about a film -- in quotation marks -- to get started :)"
                elif sentiment == -1:
                    response +=  "I'm so sorry to hear that :( When you're ready, please tell me about a film -- in quotation marks -- to get started."
                else:
                    response += "Please tell me about a film -- in quotation marks -- to get started :)"

            # more than one movie mentioned
            elif len(titles) > 1:
                # response += "Sorry, I can only handle one film at a time. Which one do you want to mention first?: {}".format(titles)
                response += np.random.choice([
                  "Sorry, I can only handle one film at a time.",
                  "I feel overwhelmed and can't handle multiple movies at the same time. :( Sorry about that.",
                  "Got it! But let's start with one movie at a time.",
                  "I'm sorry, I am not capable to handle more than one movie at a time.",
                ])
            # exactly one film mentioned
            else:
                movies = self.find_movies_by_title(titles[0])
                # no movies found
                if len(movies) == 0:
                    response += np.random.choice([
                      "I've never heard of {}, sorry... Tell me about another movie you liked.".format('"' + titles[0] + '"'),
                      "{}? Sorry, I haven't heard of it... What about another movie?".format('"' + titles[0] + '"'),
                      "Hmm... I don't think I know {}. Why don't we talk about a different movie instead?".format('"' + titles[0] + '"'),
                      "I don't know {}. Let's try another movie?".format('"' + titles[0] + '"')
                    ])

                # multiples movies found
                elif len(movies) > 1:
                    # will use disambiguate in response to a clarification (above)
                    response += np.random.choice([
                      "I found more than one movie called \"{}\". Can you clarify which you mean?".format(titles[0]),
                      "There's multiple movies called \"{}\". Which one do you want to talk about?".format(titles[0]),
                      "Ooh, multiple results for \"{}\". Can you be more specific?".format(titles[0]),
                      "I know of multiple movies called \"{}\". Can you clarify?".format(titles[0])
                    ])
                    self.clarifying = True
                    self.candidate_movies = movies
                    self.clarifying_sentiment = sentiment
                # one movie found
                elif len(movies) == 1:
                    if sentiment == -1:
                        rating_tuple = (movies[0], sentiment)
                        self.ratings_collected.append(rating_tuple)
                        if len(self.ratings_collected) < 5:
                            response += np.random.choice([
                              "So you didn't like \"{}\". Got it! Tell me another one!".format(titles[0]),
                              "I see that you weren't fond of \"{}\". What about other movies?".format(titles[0]),
                              "Ahh... not the biggest fan of \"{}\". Why don't we talk about another movie?".format(titles[0]),
                              "Noted. You don't like \"{}\". Let's talk about other movies!".format(titles[0]),
                            ])
                        # we have our 5 movies
                        else:
                            response += "So you didn't like \"{}\". Got it!".format(titles[0])
                    elif sentiment == 1:
                        rating_tuple = (movies[0], sentiment)
                        self.ratings_collected.append(rating_tuple)
                        if len(self.ratings_collected) < 5:
                            response += np.random.choice([
                              "Okay, you liked \"{}\". Got it! Tell me another one!".format(titles[0]),
                              "I see you liked \"{}\". Let's hear more!".format(titles[0]),
                              "Cool! You liked \"{}\". I'm curious to hear about your opinion on more movies!".format(titles[0]),
                              "Ooh nice! You liked \"{}\". Any other movies?".format(titles[0])
                            ])
                            #response += " Great, you liked \"{}\"! Tell me what you thought about another movie.".format(titles[0])
                        # we have our 5 movies
                        else:
                            response += "Great, you liked \"{}\"!".format(titles[0])
                    else:
                        # should we catch a response? ie "I liked it"
                        # response += "I'm sorry, I'm not sure if you liked {}. Tell me more about it.".format(titles[0])
                        response += np.random.choice([
                          "I'm sorry, I'm not sure if you liked \"{}\". it. Tell me more about it.".format(titles[0]),
                          "Hmm, I can't tell exactly how you feel about \"{}\". Can you clarify?".format(titles[0]),
                          "I see, do you mind talking more specifically about your opinion of \"{}\"?".format(titles[0]),
                          "Do you mind clarifying how you feel about \"{}\"? I didn't fully get what you meant.".format(titles[0])      
                        ])         

            if len(self.ratings_collected) < 5:
                return response
            else:                
                # first movie we recommend. rest happens at the top of starter mode code
                user_ratings = np.zeros(9125)
                for ind, senti in self.ratings_collected:
                    user_ratings[ind] = senti
                rec_indices = self.recommend(user_ratings, self.ratings)
                self.recommend_list = [self.titles[ind][0] for ind in rec_indices]
                num = random.randint(0, 3)
                response += "\n" + self.starters[num] + "\"{}\"".format(self.recommend_list[0]) + self.finishers[num]
                self.recommend_list.pop(0)
                self.recommending = True
                return response        


    # def clarify(self, input, line):
    #     response = ""
    #     if input.lower() == "yes":
    #         sentiment = self.extract_sentiment_for_movies(line)
    #         #print(sentiment)
    #         if sentiment == -1:
    #             self.inputs += 1
    #             user_ratings += self.extract_sentiment_for_movies(line)
    #             response += "So you didn't like {}. Got it!".format(line)
    #         elif sentiment == 1:
    #             self.inputs += 1
    #             user_ratings += self.extract_sentiment_for_movies(line)
    #             response += "Ok! You liked {}. That will help my recommendations.".format(line)
    #         else:
    #             response += "I'm sorry, I'm not sure if you liked {}. Tell me more about it.".format(line)
    #     else:
    #         response += "I'm sorry, I couldn't understand your input. Please start over."

    #     return response

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
        # standard mode
        pattern = r'"([^"]+)"'
        matches = re.findall(pattern, preprocessed_input)
        if matches == [] and self.creative: 
            preprocessed_input = preprocessed_input.rstrip(",.'!")
            inp = preprocessed_input.lower().split()
            running_title = ''
            length = len(inp)
            is_there_year = bool(re.search(r'\(\d{4}\)', preprocessed_input))
            movie_data = None
            if is_there_year: 
              movie_data = self.movie_titles
            else: 
              movie_data = self.movie_titles_without_years
            res = []
            for i in range(length):
              running_title = inp[i]
              for j in range(i + 1,length):
                running_title = running_title + ' ' + inp[j]
                if running_title in movie_data:
                  res.append(running_title)
            return res
        return matches


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
        res = []
        title_split = title.split()
        articles = ['the', 'an', 'a', 'la', 'el', 'le', 'les', "l'", "lo", "il", "le"]
        is_there_year = bool(re.search(r'\(\d{4}\)', title_split[len(title_split) - 1]))
        new_title = []
        new_title_str = title

        year = None 
        if is_there_year:
          year = re.search(r'\(\d{4}\)', title_split[len(title_split) - 1])
          year = year.group()
          year = year[1:len(year) - 1]
          new_title_str = ' '.join(title_split[:len(title_split) - 1])

        if title_split[0].lower() in articles: 
          if is_there_year:
            new_title = title_split[1:len(title_split) - 1]
            new_title.append(", " + title_split[0])
            # new_title.append(title_split[len(title_split) - 1])
          else: 
            new_title = title_split[1:]
            new_title.append(", " + title_split[0])
          new_title_str = ' '.join(new_title)
          new_title_str = new_title_str.replace(" ,", ',')

        if is_there_year:
          res = [i for i, movie in enumerate(self.titles) if (new_title_str).lower() + " " + title_split[len(title_split) - 1] == movie[0].lower()]
          # Handle alternate titles with years
          if self.creative: 
            res.extend([i for i, movie in enumerate(self.titles) if ((new_title_str).lower() in movie[0].lower() and year in movie[0].lower()) or title.lower() in movie[0].lower()])
        else: 
          # Handle disambiguation - creative
          if self.creative: 
            res = [i for i, movie in enumerate(self.titles) if (((new_title_str + " ").lower() in movie[0].lower()) or ((new_title_str + ":").lower() in movie[0].lower()) or (('(' + new_title_str + ')').lower() in movie[0].lower()) or (('(a.k.a. ' + new_title_str + ')').lower() in movie[0].lower()) or (title.lower() + " " in movie[0].lower()) or (title.lower() + ":" in movie[0].lower()) or (('(' + title.lower() + ')').lower() in movie[0].lower()) or (('(a.k.a. ' + title.lower() + ')').lower() in movie[0].lower()))]
          else:
            res = [i for i, movie in enumerate(self.titles) if ((new_title_str + " (").lower() in movie[0].lower()) or (title.lower() + " (" in movie[0].lower())]
        return res


# Extract sentiment HELPERS BELOW!!!!!!!!!!!!!!!!!!!!!!!!

    def get_rid_of_movies(self, input):
        return_input = ""
        quotation = False
        for letter in input:
            if letter == "\"" and quotation == False:
                return_input += letter
                quotation = True
            elif quotation == True and letter == "\"":
                return_input += letter
                quotation = False
            if not quotation and letter != '!':
                return_input += letter
        return return_input

    def negated_points(self, sen_val, pos, neg):
        if sen_val == "neg":
            pos += 1
        else:
            neg += 1
        return neg, pos

    def regular_points(self, sen_val, pos, neg):
        if sen_val == "neg":
            neg += 1
        else:
            pos += 1
        return neg, pos

    def get_words(self, ps, capture_words, negation_words, text_split, strong_words):
        text_to_get_sentiment = []
        for word in text_split:
            word = word.lower()
            if word == "enjoyed":
                text_to_get_sentiment.append("enjoy")
            if ps.stem(word) in self.sentiment or word in negation_words or word in capture_words or word in strong_words:
                text_to_get_sentiment.append(word)
        return text_to_get_sentiment

    def extract_sentiment(self, preprocessed_input):
        # print(preprocessed_input)
        text_to_split = self.get_rid_of_movies(preprocessed_input)
        text_split = text_to_split.split(" ")
        text_split = [x.strip() for x in text_split]
        #print(text_split)

        capture_words = ["enjoy", "terrible", "dislike", "disliked", "amazing", "awesome"] 
        negation_words = ["not", "didn\'t", "never",
                          "don\'t", "isn\'t", "noone", "nor", "can\'t"]
        strong_words = ["terrible", "love", "really", "great",
                        "awful", "loved", "hated", "hate", "extremely", "very", "really", "terribly", 'amazing']
        ps = porter_stemmer.PorterStemmer()

        strong_coef = 1
        text_list = self.get_words(
            ps, capture_words, negation_words, text_split, strong_words)
        #print(text_list)

        negated = False
        pos = 0
        neg = 0
        
        for i in range(len(text_list)):
            word = text_list[i].lower()
            if (not negated and word in strong_words) or word[-2:] == 'ly':
                strong_coef = 2
            if word[-2:] != "ly" and word not in negation_words:
                if word not in capture_words:
                    word = ps.stem(text_list[i])
                if word in self.sentiment or word in capture_words:
                    sen_val = self.sentiment[word]
                    if negated:
                        if word not in strong_words:
                            neg, pos = self.negated_points(sen_val, pos, neg)
                        negated = False
                    else:
                        neg, pos = self.regular_points(sen_val, pos, neg)
            if word in negation_words:
                negated = True


        if self.creative:
          if pos > neg:
            # print(strong_coef)
            return 1 * strong_coef
          elif pos < neg:
            # print(strong_coef * -1)
            return -1 * strong_coef 
          return 0

        else:
            if pos > neg:
                return 1
            elif pos < neg:
                return -1
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
          print(
              sentiments) // prints [("Titanic (1997)", 1), ("Ex Machina", 1)]

        :param preprocessed_input: a user-supplied line of text that has been
        pre-processed with preprocess()
        :returns: a list of tuples, where the first item in the tuple is a movie
        title, and the second is the sentiment in the text toward that movie
        """

        movies = self.extract_titles(preprocessed_input)  # list of movies in order

        if len(movies) == 1:  # one movie
            return (movies[0], self.extract_sentiment(preprocessed_input))

        text = self.get_rid_of_movies(preprocessed_input)

        punctuation = ['.', ',', '!', ';', ':']
        sentences = []
        inner_sen = ""

        for letter in text:
            if letter not in punctuation:
                inner_sen += letter
            else:
                sentences.append(inner_sen)
                inner_sen = ""
        if inner_sen not in sentences and inner_sen != "":
            sentences.append(inner_sen)
        # print(sentences)
        # ['I hated both """ and """', ' but """ was good', '']

        listed_sentences = []
        for sentence in sentences:
            list_of_words = sentence.split(" ")
            num_of_movies = list_of_words.count('"""')
            list_of_words = [x.strip() for x in list_of_words]
            list_of_words = list(filter(('"""').__ne__, list_of_words)) # remove the quotations
            sen = ' '.join(list_of_words)
            listed_sentences.append([sen, num_of_movies, 0])
         # [('I hated both """ and """', 2, 0), (' but """ was good', '', 1, 0)]
        #print(listed_sentences)

        list_of_movies = []
        conjunctions_diff = ['but', 'yet']
        conjunctions_same = ['and', 'or', 'both', 'either', 'nor']
        negation_words = ["not", "didn\'t", "never",
                          "don\'t", "isn\'t", "noone", "nor", "can\'t"]
        prev_sen = None
        updated_listed_sentences = []
        for i in range(len(listed_sentences)):
            if any(word in listed_sentences[i][0] for word in conjunctions_same): # if same
                sentiment = self.extract_sentiment(listed_sentences[i][0])
                updated_listed_sentences.append((listed_sentences[i][0], listed_sentences[i][1], [sentiment]))
                prev_sen = sentiment
            elif any(word in listed_sentences[i][0] for word in conjunctions_diff) and listed_sentences[i][1] > 1: # 2 diff w conjunction
                sentiment1 = 0
                sentiment2 = 0
                for word in conjunctions_diff:
                    index = listed_sentences[i][0].find(word)
                    if index != -1:
                        sentiment1 = self.extract_sentiment(listed_sentences[i][0][:index])
                        sentiment2 = self.extract_sentiment(listed_sentences[i][0][index:])
                        if any(word in listed_sentences[i][0][index:] for word in negation_words):
                            if sentiment1 < 0:
                                sentiment2 = abs(sentiment1)
                            elif sentiment1 > 0:
                                sentiment2 = -sentiment1
                        break
                updated_listed_sentences.append((listed_sentences[i][0], listed_sentences[i][1], [sentiment1, sentiment2]))
            else:
                sentiment = self.extract_sentiment(listed_sentences[i][0])
                if any(word in listed_sentences[i][0] for word in negation_words):
                    if prev_sen < 0:
                        sentiment = abs(prev_sen)
                    else:
                        sentiment = -prev_sen
                updated_listed_sentences.append((listed_sentences[i][0], listed_sentences[i][1], [sentiment]))
                prev_sen = sentiment

        movie_count = 0
        for sentence in updated_listed_sentences:
            num = sentence[1]
            j = 0
            for i in range(movie_count, movie_count + num):
                if len(sentence[2]) > 1:
                    list_of_movies.append((movies[i], sentence[2][j]))
                    j += 1
                else:
                    list_of_movies.append((movies[i], sentence[2][0]))
            movie_count += num
        return list_of_movies


    def levenshtein(self, str1, str2):
        length_str1 = len(str1)
        length_str2 = len(str2)
        DP = np.zeros([length_str1 + 1, length_str2 + 1])
        DP[0][0] = 0
        for i in range(1, length_str1 + 1):
            DP[i][0] = i
        for j in range(1, length_str2 + 1):
            DP[0][j] = j

        for i in range(1, length_str1 + 1):
            for j in range(1, length_str2 + 1):
                deletion = DP[i - 1][j] + 1
                insertion = DP[i][j - 1] + 1
                sub = DP[i - 1][j - 1]
                if str1[i - 1] != str2[j - 1]:
                    sub += 2
                DP[i][j] = min([deletion, insertion, sub])
        return DP[length_str1][length_str2]

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
        # movie_titles = []
        # articles = ['the', 'an', 'a', 'la', 'el', 'le', 'les', "l'", "lo", "il", "le"]
        # for x in self.titles:
        #   t = x[0]
        #   x_split = x[0].split()
        #   pos_article = len(x_split) - 2
        #   if x_split[pos_article].lower() in articles and ',' in x_split[pos_article - 1].lower():
        #     x_split[pos_article - 1] = x_split[pos_article - 1].replace(',', '')
        #     x_split = [x_split[pos_article]] + x_split[0:pos_article] + [x_split[len(x_split) - 1]]
        #     t = ' '.join(x_split)
        #   movie_titles.append(t)     
        # movie_titles = [x[0] for x in self.titles]
        res = []
        min_dist_so_far = max_distance
        is_there_year = bool(re.search(r'\(\d{4}\)', title))
        for i, movie in enumerate(self.movie_titles):
            if is_there_year == False:
              movie = movie[:len(movie) - 7]
            dist = self.levenshtein(movie.lower(), title.lower())
            if dist <= max_distance:
                if dist < min_dist_so_far:
                    res = []
                    res.append(i)
                    min_dist_so_far = dist
                elif dist == min_dist_so_far:
                    res.append(i)
        return res

    def disam2_find_movies_closest_to_title(self, title, options, max_distance=3):
        movie_titles = [x[0] for x in options]
        res = []
        min_dist_so_far = max_distance
        for i, movie in enumerate(movie_titles):
            # title = title[0].upper() + title[1:].lower()
            movie = movie[:len(movie) - 7]
            dist = self.levenshtein(movie.lower(), title.lower())
            if dist <= max_distance:
                if dist < min_dist_so_far:
                    res = []
                    res.append(i)
                    min_dist_so_far = dist
                elif dist == min_dist_so_far:
                    res.append(i)
        return res

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
        options = [self.titles[ind] for ind in candidates]
        narrowed = []
        going_off_order = False
        # repeat_question = False
        clarification = clarification.rstrip(",.'!")
        if len(clarification) == 1:
          res = [i for i, movie in enumerate(options) if (" " + clarification + " ").lower() in movie[0].lower()]
          if len(res) == 0:
            going_off_order = True
            narrowed = candidates[int(clarification)]
        else:
          res = [i for i, movie in enumerate(options) if (clarification).lower() in movie[0].lower()]
          if len(res) == 0:
            res = self.disam2_find_movies_closest_to_title(clarification, options)
            if len(res) == 0 :
              # repeat_question = True
              return []
        if not going_off_order:
          narrowed = [candidates[i] for i in res]
        return narrowed

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
        binarized_ratings = np.apply_along_axis(lambda x: np.where(x > threshold, 1,
                                                                   (np.where(x == 0, 0, -1))), axis=1, arr=ratings)
        return binarized_ratings

    def reshape_indices(self, x, y):
        x_ind = np.nonzero(x)
        y_ind = np.nonzero(y)
        match_ind = np.intersect1d(x_ind, y_ind)
        return x[match_ind], y[match_ind]

    def similarity(self, u, v):
        """Calculate the cosine similarity between two vectors.

        You may assume that the two arguments have the same shape.

        :param u: one vector, as a 1D numpy array
        :param v: another vector, as a 1D numpy array

        :returns: the cosine similarity between the two vectors
        """
        row1, row2 = self.reshape_indices(u, v)
        if np.linalg.norm(u) != 0 and np.linalg.norm(v) != 0:
            return np.dot(row1, row2) / (np.linalg.norm(u)*np.linalg.norm(v))
        return 0

    def pred_per_movie(self, unseen_movie, user, ratings_seen):
        cosine_vector = np.apply_along_axis(lambda seen_movie: self.similarity(
            unseen_movie, seen_movie), axis=1, arr=ratings_seen)
        pred_rating = np.dot(user, cosine_vector)
        return pred_rating


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

        ind_missed = np.nonzero(user_ratings == 0)[0]
        ind_seen = np.nonzero(user_ratings)[0]
        ratings_missed = np.apply_along_axis(
            lambda user_i: user_i[ind_missed], axis=0, arr=ratings_matrix)
        ratings_seen = np.apply_along_axis(
            lambda user_i: user_i[ind_seen], axis=0, arr=ratings_matrix)
        
        predicted_ratings = np.apply_along_axis(lambda unseen_movie: self.pred_per_movie(
            unseen_movie, user_ratings[ind_seen], ratings_seen), axis=1, arr=ratings_missed)
        topk_ind_unseen = np.argsort(predicted_ratings)[-k:][::-1].tolist()
        ind_missed_list = ind_missed.tolist()
        topk_ind_whole = [ind_missed_list[x] for x in topk_ind_unseen]
        return topk_ind_whole

    def intro(self):
        """Return a string to use as your chatbot's description for the user."""
        description = """
                      This chatbot is designed to help users discover movies that match their 
                      interests and preferences. Tell our bot some information about a movie you
                      like or dislike, and the chatbot will use natural language processing to 
                      generate an appropriate movie recommendation list!
                      """
        return description


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
