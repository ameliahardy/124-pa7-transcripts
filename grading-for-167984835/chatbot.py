# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util
import re 
import string
import numpy as np
import nltk
from nltk.stem import PorterStemmer
import random


# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'Cardi Bot'

        self.creative = creative

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')

        ########################################################################
        # TODO: Binarize the movie ratings matrix.                             #
        ########################################################################
        self.fifthRecCheck = 0
        self.moviecount = 0
        self.reccount = 0
        self.user_rating = np.zeros(9125)
        self.rec_list = []
        self.candidates = []
        self.clarification = ""
        self.disambiguate_question = 0
        self.disambiguate_sentiment = 0
        self.spellcheck_binary = 0
        self.candidate_movie = []
        self.candidate_sentiment = 0
        self.multiple_titles = 0
        # Binarize the movie ratings before storing the binarized matrix.
        self.ratings = self.binarize(ratings)
        ########################################################################
        #                             END OF YOUR CODE                         #
        ########################################################################

    ############################################################################
    # 1. WARM UP REPL                                                          #
    ############################################################################


    def greeting(self):
        """Return a message that the chatbot uses to greet the user."""
        if (self.creative):
            greeting_message = "Hiiii bestie!! This is your girl Cardi Bot. I'm a regular shmegular bot that gives people movie recommendations cuz you know, I LOOOVE movies. To start off, tell me a movie you watched and how you felt."
        else:
            greeting_message = "Hi! I'm a simple bot that focuses on one thing and one thing only: to give you movie recommendations! To start off, tell me a movie you watched and how you felt about it. "
        return greeting_message

    def goodbye(self):
        """
        Return a message that the chatbot uses to bid farewell to the user.
        """
        if (self.creative):
            goodbye_message = "Okurrr, bye! Catch you later!"
        else:
            goodbye_message = "I hope I've been helpful. Have a nice day!"
        return goodbye_message

    ############################################################################
    # 2. Modules 2 and 3: extraction and transformation                        #
    ############################################################################
    def confirm_emotions(self, sentiment, movie_name):
            if sentiment == 1:
                output = " So you liked "  + movie_name + ". "
            elif sentiment == 2:
                output = "You loved "  + movie_name +"! "
            elif sentiment == -1:
                output = "I didn't like " + movie_name + " either. "
            elif sentiment == -2:
                output = "I hated " + movie_name + " too! "
            return output


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
        processed = self.preprocess(line)
        potential_title_dup = self.extract_titles(processed)
        potential_title_set = set(potential_title_dup) 
        potential_titles = list(potential_title_set)
        for title in potential_titles: 
            if title == 'not': 
                potential_titles.remove(title)
            if title == 'hate': 
                potential_titles.remove(title) 
            if title == '10': 
                potential_titles.remove(title) 
            if title == 'hated': 
                potential_titles.remove(title)

        """
        for title in potential_titles: 
            title_index_list = self.find_movies_by_title(title)
            dict[title] = title_index_list
        print(dict)"""
        
        if len(potential_titles) > 1:
            p0 = self.extract_sentiment_for_movies(processed)
            p1 = set(p0)
            potential_titles_sentiment = list(p1)

            for title in potential_titles_sentiment: 
                if title[0] not in potential_titles: 
                   potential_titles_sentiment.remove(title)

            response = "Purr, "
            for i in range(len(potential_titles_sentiment)):
                # title_index = dict[potential_titles_sentiment[i][0]][0]
                sentiment = potential_titles_sentiment[i][1]
                if (sentiment > 0):
                    if i == (len(potential_titles_sentiment) - 1):
                        str_part = "you liked " + potential_titles_sentiment[i][0] + "."
                    else: 
                        str_part = "you liked " + potential_titles_sentiment[i][0] + " and " 
                elif (sentiment < 0):
                    if i == (len(potential_titles_sentiment) - 1):
                        str_part = "you did not like " + potential_titles_sentiment[i][0] + "."
                    else: 
                        str_part = "you did not like " + potential_titles_sentiment[i][0] + " and " 
                else: 
                    if i == (len(potential_titles_sentiment) - 1):
                        str_part = "you saw " + potential_titles_sentiment[i][0] + "."
                    else: 
                        str_part = "you saw " + potential_titles_sentiment[i][0] + " and " 
            
                #self.user_rating[title_index] = sentiment
                #self.moviecount += 1
                response = response + str_part
            response = response + " Tell your bestie Cardi more!"
            

            try:
                return response
            except:
                self.potential_candidates = []
                self.disambiguate_sentiment = 0
                self.disambiguate_question = 0
                self.candidate_movie = []
                self.candidate_sentiment = 0
                self.spellcheck_binary = 0
                return failing_gracefully_random
        self.multiple_titles = 0
        if (len(potential_titles) > 1):
            self.multiple_titles = 1

        #randomzing reponses
        asking_for_more_movies = ["What else boo? ", "Hit me with another one! ", "Tell me more girrrrrl. ", "Ooh, girl, you can't leave me hanging like that. Tell me another one, don't hold back! "]
        ask_for_more_random = random.choice(asking_for_more_movies)
        another_rec = ["You want some more fire recommendations? I gotchu, just say the word. ", "You liked what I gave you so far? Don't worry, I've got plenty more where that came from. Want me to keep 'em coming? ", "Yo, you want me to put you on to some more stuff? I got plenty of recommendations if you need 'em. ", "More??? ", "Listen, if you need some more bangers, just let me know. I've got a whole list of recommendations ready to go. "]
        another_rec_random = random.choice(another_rec)
        stupid_sorry = ["Huh? I don't understand what you're saying.", "I'm sorry, but I don't get it. Can you explain it to me again? I need you to break it down real simple for me, because I'm not following.", "I don't wanna be trippin', but I need to know what do you mean. Say it agaiin?", "Hold on, slow down. I don't wanna be lost in the sauce, can you explain it to me again?"]
        stupid_sorry_random = random.choice(stupid_sorry)
        rec_question = "Given what you've told me, I know what's the best for you. I'm the queen of recommendations, honey. You need anything else, just say the word and I'll hook you up."
        arbitrary_reponse = ["Hmmm what are you talking about girl? ", "Okuuuuur I got it. ", "Hm, you know that's not really what I want to talk about right now, let's go back to movies", "Okuur", "Perfff"]
        arbitrary_reponse_random = random.choice(arbitrary_reponse)
        neg_emotion_reactions = ["My bad.", "I apologize", "I hope you feel better"]
        neg_emotion_reactions_random = random.choice(neg_emotion_reactions)
        failing_gracefully = ["Huh? What you talkin' 'bout? I don't understand, can you say that again?", "Hold up, what does that mean? Can you break it down for me?", "Say what? I'm not picking up what you're putting down.", ]
        failing_gracefully_random = random.choice(failing_gracefully)
        
        if (self.creative): #creative mode
            #randomzing reponses
            asking_for_more_movies = ["What else boo? ", "Hit me with another one! ", "Tell me more girrrrrl. ", "Ooh, girl, you can't leave me hanging like that. Tell me another one, don't hold back! "]
            ask_for_more_random = random.choice(asking_for_more_movies)
            another_rec = ["You want some more fire recommendations? I gotchu, just say the word. ", "You liked what I gave you so far? Don't worry, I've got plenty more where that came from. Want me to keep 'em coming? ", "Yo, you want me to put you on to some more stuff? I got plenty of recommendations if you need 'em. ", "More??? ", "Listen, if you need some more bangers, just let me know. I've got a whole list of recommendations ready to go. "]
            another_rec_random = random.choice(another_rec)
            stupid_sorry = ["Huh? I don't understand what you're saying.", "I'm sorry, but I don't get it. Can you explain it to me again? I need you to break it down real simple for me, because I'm not following.", "I don't wanna be trippin', but I need to know what do you mean. Say it agaiin?", "Hold on, slow down. I don't wanna be lost in the sauce, can you explain it to me again?"]
            stupid_sorry_random = random.choice(stupid_sorry)
            rec_question = "Given what you've told me, I know what's the best for you. I'm the queen of recommendations, honey. You need anything else, just say the word and I'll hook you up."
            arbitrary_reponse = ["Hmmm what are you talking about girl? ", "Okuuuuur I got it. ", "Hm, you know that's not really what I want to talk about right now, let's go back to movies", "Okuur", "Perfff"]
            arbitrary_reponse_random = random.choice(arbitrary_reponse)
            neg_emotion_reactions = ["My bad.", "I apologize", "I hope you feel better"]
            neg_emotion_reactions_random = random.choice(neg_emotion_reactions)
            failing_gracefully = ["Huh? What you talkin' 'bout? I don't understand, can you say that again?", "Hold up, what does that mean? Can you break it down for me?", "Say what? I'm not picking up what you're putting down.", ]
            failing_gracefully_random = random.choice(failing_gracefully)

            yes_words = {"Yes", "yes", "yeah", "sure", "okay", "Sure", "Okay", "Yep", "yep"} # to be added
            no_words = {"No", "no", "Nah", "nah", "nope"} # to be added


            if (self.moviecount > 4):
                self.fifthRecCheck = 1

            if self.moviecount < 5: #collecting data
                
                # SPELL CHECK YES/NO x1 MOVIE ONLY
                if self.spellcheck_binary == 1:
                    if (processed in yes_words):
                        self.user_rating[self.candidate_movie] = self.candidate_sentiment
                        self.moviecount += 1
                        response = self.confirm_emotions(self.candidate_sentiment, self.titles[self.candidate_movie][0]) + ask_for_more_random
                    elif (processed in  no_words):
                        response = "Oop my bad boo! Tell me about another sch-film then!"
                    else:
                        response = "Girl whatever you said is out of my knowledge. Tell me another one!"
                    self.candidate_movie = []
                    self.candidate_sentiment = 0
                    self.spellcheck_binary = 0
                    

                # DISAMBIGUATE() IMPLEMENTATION
                if self.disambiguate_question == 1: 
                    movie_indexes = self.disambiguate(processed, self.potential_candidates)

                    if len(movie_indexes) > 1: # disambiguate() returns 2+ movies, redo disambiguate()
                        movie_versions = []
                        for i in range(len(movie_indexes)):
                            movie_versions.append(self.titles[movie_indexes[i]][0])
                        response = "Phew I am still not sure which schfilm you're talking bout. I'm stuck between " + ','.join(movie_versions) + ". Which one do you mean???"
                        self.potential_candidates = movie_indexes
                    
                    elif len(movie_indexes) < 1:
                        try: 
                            possible_movies = self.find_movies_closest_to_title(potential_titles[0])
                        except:
                            self.potential_candidates = []
                            self.disambiguate_sentiment = 0
                            self.disambiguate_question = 0
                            return "Huh? What you talkin' 'bout? Tell me about another sch-film"
                            
                        
                        if (len(possible_movies) == 1 & self.disambiguate_sentiment != 0): #found one possible bc of mispelling
                            response = "Did you mean {}?".format(self.titles[possible_movies[0]][0])
                            self.spellcheck_binary = 1
                            self.candidate_movie = possible_movies[0]
                            self.candidate_sentiment = self.disambiguate_sentiment
                            self.potential_candidates = []
                            self.disambiguate_sentiment = 0
                            self.disambiguate_question = 0

                            #if next input = yes
                            #self.user_rating[possible_movies[0]] = self.disambiguate_sentiment
                            #self.moviecount += 1
                        elif ((len(possible_movies) == 1) & (self.disambiguate_sentiment == 0)):
                            response = "Wait, hold up. I'm not sure if I'm reading the room right. How do you feel about " + potential_titles[0] + ".  Are you vibing with this or nah? Pls answer with movie titles cuz I'm forgetful"
                            self.potential_candidates = []
                            self.disambiguate_question = 0
                        elif (len(possible_movies) > 1): # found more than one possible bc of mispelling
                            movie_versions = []
                            for i in range(len(possible_movies)):
                                movie_versions.append(self.titles[possible_movies[i]][0])
                            response = "I'm confused. Which one are you talking about? " + ' '.join(movie_versions)
                            self.potential_candidates = possible_movies
                            try:
                                self.disambiguate_sentiment = user_sentiment
                            except:
                                user_sentiment = self.extract_sentiment(processed)
                                self.disambiguate_sentiment = user_sentiment

                            self.disambiguate_question = 1
                        elif (len(possible_movies) == 0): # really can't find that movie
                            response = "Girl whatever you said is out of my knowledge. Tell me another one!"
                            self.potential_candidates = []
                            self.disambiguate_sentiment = 0
                            self.disambiguate_question = 0

                    elif len(movie_indexes) == 1 : #disambiguate() works and returns 1 movie
                        potential_titles = self.titles[movie_indexes[0]]
                        if self.disambiguate_sentiment == 0:
                            response = "Wait, hold up. I'm not sure if I'm reading the room right. How do you feel about " + potential_titles[0] + ".  Are you vibing with this or nah? Pls answer with movie titles cuz I'm forgetful"
                        elif self.disambiguate_sentiment != 0:
                            self.user_rating[movie_indexes[0]] = self.disambiguate_sentiment
                            self.moviecount += 1
                            response = self.confirm_emotions(self.disambiguate_sentiment, potential_titles[0]) + ask_for_more_random
                        self.potential_candidates = []
                        self.disambiguate_sentiment = 0
                        self.disambiguate_question = 0

                ## REGULAR STUFF - ADDING DATA POINTS MOVIES. ONLY 1 MOVIE CASE
                elif (len(potential_titles) > 1): # more than 1 titles multiple sentiment in one sentence, THE COMPLICATED CASE
                    user_sentiment_tuples =  self.extract_sentiment_for_movies(processed)
                    outputs = []
                    for pair in user_sentiment_tuples:
                        movie_indexes = self.find_movies_by_title(pair[0])
                        if (len(movie_indexes) == 1) & (pair[1] != 0): #found one movie
                            self.user_rating[movie_indexes[0]] = pair[1]
                            self.moviecount += 1
                            outputs.append(self.confirm_emotions(pair[1], pair[0]))
                            reponse = "Okuuuuuurt" + ' '.join(outputs) + ask_for_more_random #TODO: the for loop here seems weird, to be tested; but basically it should confirm all emotions for all movies
                        elif (len(movie_indexes) != 0) & (pair[1] != 0): # found more than one matching movie
                            self.candidates = movie_indexes # storing possible candidates for 
                            #TODO not sure how to get clarification from the next input
                            movie_indexes = self.disambiguate(self.candidates, self.clarification)
                            output = self.confirm_emotions(pair[1], pair[0])
                            movie_index_confirmed = 0 # change when figure out how to implement clarificatoin
                            self.user_rating[movie_index_confirmed] = pair[1]
                            self.moviecount += 1
                            response = "Okuuuuuurt" + output + ask_for_more_random
                        #it seems like in multiple movies & sentiments the sentiment will not be neutral so im not tackling this for now
                        
                elif (len(potential_titles) == 1): # one movie title
                    user_sentiment = self.extract_sentiment(processed)
                    movie_indexes = self.find_movies_by_title(potential_titles[0])
                    if (len(movie_indexes) == 1) & (user_sentiment != 0): #best case: one movie and one sentiment
                        self.user_rating[movie_indexes[0]] = user_sentiment
                        self.moviecount += 1
                        response = self.confirm_emotions(user_sentiment, potential_titles[0]) + ask_for_more_random
                    elif len(movie_indexes) > 1: #more than one match
                        # self.candidates = movie_indexes
                        movie_versions = []
                        for i in range(len(movie_indexes)):
                            movie_versions.append(self.titles[movie_indexes[i]][0])
                        response = "Girrl I found more than one movie called " + potential_titles[0] + ". They are " + ','.join(movie_versions) + ". Which one do you mean???"
                        self.potential_candidates = movie_indexes
                        self.disambiguate_sentiment = user_sentiment
                        self.disambiguate_question = 1
                    elif (len(movie_indexes) == 1) & (user_sentiment == 0): #unknown sentiment
                         response = "Wait, hold up. I'm not sure if I'm reading the room right. How do you feel about " + potential_titles[0] + ".  Are you vibing with this or nah? Pls answer with movie titles cuz I'm forgetful"
                    elif (len(movie_indexes) == 0) & (user_sentiment != 0): #cant find movie
                        possible_movies = self.find_movies_closest_to_title(potential_titles[0])
                        if (len(possible_movies) == 1): #found one possible bc of mispelling
                            response = "Did you mean {}?".format(self.titles[possible_movies[0]][0])
                            self.spellcheck_binary = 1
                            self.candidate_movie = possible_movies[0]
                            self.candidate_sentiment = user_sentiment

                            #if next input = yes
                            #self.user_rating[possible_movies[0]] = user_sentiment
                            #self.moviecount += 1
                        elif (len(possible_movies) > 1): # found more than one possible bc of mispelling
                            # self.candidates = movie_indexes
                            movie_versions = []
                            for i in range(len(possible_movies)):
                                movie_versions.append(self.titles[possible_movies[i]][0])
                            response = "I'm confused. Which one are you talking about? " + ' '.join(movie_versions)
                            # print(" tsting response for edit distance: {}" + response)
                            self.potential_candidates = possible_movies
                            self.disambiguate_sentiment = user_sentiment
                            self.disambiguate_question = 1
                        elif (len(possible_movies) == 0): # really can't find that movie
                            response = "Girl whatever you said is out of my knowledge. Tell me another one!"
                            self.potential_candidates = []
                            self.disambiguate_sentiment = 0
                            self.disambiguate_question = 0
                    else: #all other inputs
                        reponse = stupid_sorry_random
                
                elif (len(potential_titles) == 0): #all other arbitrary inputs 
                    specific_questions = ["Can you", "can you", "What is", "what is"] #specific questions
                    neg_emotion_words = ["angry", "sad", "depressed"] # tackle different emotion inputs, add more emotions
                    pos_emotion_words = ["happy", "peaceful"] # add more words idk
                    for substring in specific_questions:
                        index = processed.find(substring)
                        if index == -1: #truly arbitrary inputs
                            reponse = arbitrary_reponse_random
                        else:
                            new_string = processed[:index] + processed[index + len(substring):]
                            response = "Sorry, I don't know " + new_string + "Are we still taking about movies or what?"
                    for emotion in neg_emotion_words:
                        index = processed.find(emotion)
                        if index != -1: 
                            response = "AWWWWWW I'm sorry that you feel " + processed[:index] + processed[index + len(emotion):] +"," + neg_emotion_reactions_random
                    for emotion in pos_emotion_words:
                        index = processed.find(emotion)
                        if index != -1: 
                            response = "Eeeeoowwww! I'm glad that you feel " + processed[:index] + processed[index + len(emotion):] +"," + "Keep da good vibes!"
                
                 
                if ((self.moviecount > 4) & (self.fifthRecCheck == 0)): #gathered 5 datapoints
                    response = response + rec_question
                    self.rec_list = self.recommend(self.user_rating, self.ratings, 10)
        
            #when recommending
            if ((self.moviecount > 4) & (self.fifthRecCheck == 1)):
                if ((processed in yes_words) & (self.reccount < 10)):
                    response = "Perfff. I would recommend watching " + self.titles[self.rec_list[self.reccount]][0] + ". " + another_rec_random
                    self.reccount += 1
                    
                elif ((processed in no_words) & (self.reccount > 9)):
                    response = "Girl you are really pressuring me here. I ain't Wikipedia you know, this is all I have for ya. If you are up for some fresh recommendations, type in 'more'. If not, type ':quit'"

                elif processed in no_words:
                    response = "Okay..."
                
                elif (((processed == "more") or (processed == "More")) & (self.reccount > 9)):
                    self.moviecount = 0
                    self.rec_list = []
                    self.reccount = 0
                    self.fifthRecCheck = 0
                    response = "Eeeeoowwww let's gooooo. You know the rules. Tell me how you feel about another movie?"

                elif (self.reccount < 10):
                    response = "Huh? I don't understand what you're saying. Just say 'Yes' or 'No' if you want a recommendation"
                
                elif (self.reccount > 9):
                    response = "Girl you are really pressuring me here. I ain't Wikipedia you know, this is all I have for ya. If you are up for some fresh recommendations, type in 'more'. If not, type ':quit'"
                else: #all other cases? someone clean up the logic here
                    response = stupid_sorry_random
            





                    



                
                

        else: #starter mode
            #generating non-repeating reponses & response strings
            asking_for_more_movies = [". Did you like/dislike any other movies?", ". Tell me about another one!", ". Your movie taste is spectacular. Tell me more!"]
            ask_for_more_random = random.choice(asking_for_more_movies)
            another_rec = [". Would you like another recommendation?", ". Do you want to hear one more?", ". How about another one?", ". More?", ". Interested in hearing more?"]
            another_rec_random = random.choice(another_rec)
            stupid_sorry = "Sorry, I don't know what you're talking about... we are but just an undergrad-level bot. If you want movie recs, tell me about movies you liked or disliked with correct capitalization, spelling, and within quotation marks!"
            rec_question = ". Given what you've told me, do you want a recommendation? (Type precisely: Yes or No)"

            if (self.moviecount > 4):
                self.fifthRecCheck = 1

            user_sentiment = self.extract_sentiment(processed)        

            # case when STILL COLLECTING MOVIE DATA (counter < 5)
            if (self.moviecount < 5):
                if (len(potential_titles) == 1) & (user_sentiment != 0):
                    if potential_titles[0].find('(') != -1 and potential_titles[0].find(')') == -1: 
                        response = stupid_sorry
                    elif potential_titles[0].find('(') == -1 and potential_titles[0].find(')') != -1: 
                        response = stupid_sorry
                    else: 
                        movie_indexes = self.find_movies_by_title(potential_titles[0])
                        if len(movie_indexes) == 1:
                            if user_sentiment > 0: 
                                self.user_rating[movie_indexes[0]] = user_sentiment
                                self.moviecount += 1
                                if (self.moviecount > 4):
                                    response = "I see that you liked " + potential_titles[0] + rec_question
                                    self.rec_list = self.recommend(self.user_rating, self.ratings, 10)
                                else:
                                    response = "I see that you liked " + potential_titles[0] + ask_for_more_random
                            elif user_sentiment < 0: 
                                self.user_rating[movie_indexes[0]] = user_sentiment
                                self.moviecount += 1
                                if (self.moviecount > 4):
                                    response = "I see that you disliked " + potential_titles[0] + rec_question
                                    self.rec_list = self.recommend(self.user_rating, self.ratings, 10)
                                else:
                                    response = "I see that you disliked " + potential_titles[0] + ask_for_more_random
                        elif len(movie_indexes) == 0:
                            response = "Sorry, I could not find this movie. Can you tell me once more? Make sure you use quotation marks and correct capitalization please."
                        else:
                            movie_versions = []
                            for i in range(len(movie_indexes)):
                                movie_versions.append(self.titles[movie_indexes[i]][0])
                if len(potential_titles) == 0:
                    response = stupid_sorry
                if len(potential_titles) > 1:
                    response = "Sorry, I can only process one movie at a time. Can you say it again?"
                
                if (len(potential_titles) == 1) & (user_sentiment == 0):
                    response = "Sorry, I'm not sure how you feel about " + potential_titles[0] + ". Can you clarify whether you liked the movie or not?"
                
            # case when RECOMMENDING (counter > 4)
            if ((self.moviecount > 4) & (self.fifthRecCheck == 1)):
                if ((processed == "Yes") & (self.reccount < 10)):
                    response = "I would recommend watching " + self.titles[self.rec_list[self.reccount]][0] + another_rec_random
                    self.reccount += 1
                
                elif ((processed == "Yes") & (self.reccount > 9)):
                    response = "We have no more recommendations. You got 10 movies, that's like 30 hours. Go. If you would like more recommendations, type in 'more'. If not, type ':quit'"

                elif ((processed == "more") & (self.reccount > 9)):
                    self.moviecount = 0
                    self.rec_list = []
                    self.reccount = 0
                    self.fifthRecCheck = 0
                    response = "Awesome! Tell me how you feel about another movie?"

                
                elif (processed == "No"):
                    response = "Okay..."

                elif (self.reccount < 10):
                    response = "Please answer 'Yes' or 'No' if you want a recommendation"
                
                elif (self.reccount > 9):
                    response = "We have no more recommendations. You got 10 movies, that's like 30 hours. Go. If you would like more recommendations, type in 'more'. If not, type ':quit'"


        try:
            return response
        except:
            self.potential_candidates = []
            self.disambiguate_sentiment = 0
            self.disambiguate_question = 0
            self.candidate_movie = []
            self.candidate_sentiment = 0
            self.spellcheck_binary = 0
            return failing_gracefully_random
            


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
        # leave this method unmodified.  
        # 
        ########################################################################

        ########################################################################
        #                             END OF YOUR CODE                         #
        ########################################################################
        
        return text

    def get_powerset(self, lst):
        if len(lst) == 0:
            return [[]]
        else:
            result = []
            for subset in self.get_powerset(lst[1:]):
                result.append(subset)
                result.append([lst[0]] + subset)
            return result
    
    def concatenate_strings(self, lst):
        result = ""
        for i in range(len(lst)):
            if i > 0:
                result += " "
            result += lst[i]
        return result

    def move_article_to_end(self, input_string):
        words = input_string.split()
        if words[0].lower() in ["a", "an", "the", "le", "la", "les", "der", "die", "das", "el", "los", "las", "il", "lo", "i", "gli"]:
            words.append(',' + ' ' + words.pop(0))
            output_string = ' '.join(words) 
            first_param = output_string.find('(')
            last_param = output_string.find(')')
            if first_param != -1 and last_param != -1: 
                output_string = output_string[0: first_param] + output_string[last_param + 2:] + " " +  output_string[first_param:last_param + 1]
    
            output_string = output_string.replace(" ,",",")
        
        else: 
            output_string = ' '.join(words) 

        return output_string

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
        
        movie_titles = []

        if preprocessed_input.find('"') != -1:
            pattern = '"(.*?)"'
            matches = re.findall(pattern, preprocessed_input)
            for m in matches:
                movie_titles.append(m)

        else:
            # all lower 
            sentence = preprocessed_input.lower()
            # remove punc 
            punc = ",.!;"
            for elem in sentence:
                if elem in punc:
                    sentence = sentence.replace(elem, "")
            
            # split into list 
            input = sentence.split()
            
            possible_titles = self.get_powerset(input)[1:]

            for possible_title in possible_titles: 
                title_str = self.concatenate_strings(possible_title)
                # should delete 
                input_title = self.move_article_to_end(title_str)

                for title in self.titles: 
                    # include year 
                    if input_title.find('(') != -1 and input_title.find(')') != -1:
                        # title does not contain extra ()
                        if title[0].count('(') == 1: 
                            to_be_matched = title[0].lower()
                        else: 
                            index_1 = title[0].find('(')
                            index_2 = title[0].find(')') 
                            first_match = title[0][0:index_1 - 1].lower()
                            second_match = title[0][index_1 + 1:index_2].lower()
                            if 'a.k.a.' in second_match:
                                second_match = second_match[7:]
                            if input_title == first_match:
                                to_be_matched = first_match
                            if input_title == second_match:
                                to_be_matched = second_match

                    # does not include year 
                    else: 
                        length = len(title[0])
                        to_be_matched = title[0][0: length - 7].lower()
                        # could be alternative title 
                        if to_be_matched.find('(') != -1:
                            index_1 = title[0].find('(')
                            index_2 = title[0].find(')') 
                            first_match = title[0][0:index_1 - 1].lower()
                            second_match = title[0][index_1 + 1:index_2].lower()
                            if 'a.k.a.' in second_match:
                                second_match = second_match[7:]
                            if input_title == first_match:
                                to_be_matched = first_match
                            if input_title == second_match:
                                to_be_matched = second_match
                    if input_title == to_be_matched: 
                        movie_titles.append(input_title)
           
        return movie_titles
    
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
         
        with open("data/movies.txt") as file: 
            data = file.read().lower()
        
        index_list = []
        var = title
        
        # convert inputted title to lowercase
        title = title.lower()
        
        # parse out title
        title_list = title.split(" ")
        new_title = ""
        a_an_the_binary = 0
        new_title_list = []

        if '(' in title:
            if title_list[0] in ["a", "an", "the", "le", "la", "les", "der", "die", "das", "el", "los", "las", "il", "lo", "i", "gli"]:
                a_an_the_binary = 1
                new_title_list = []
                for i in range(len(title_list) - 2):
                    new_title_list.append(title_list[i+1])
                new_title_list.append(title_list[0])
                new_title_list.append(title_list[len(title_list)-1])
                title_list = new_title_list
            # deal with spaces if (year1995) IS present
            for i in range(len(title_list)):
                if (a_an_the_binary == 0):
                    new_title += title_list[i]
                    if (i != (len(title_list) - 1)): # do not add space after last part
                        new_title += "\s"
                else: # if a_an_the_binary==1
                    if (i == (len(title_list) - 3)):
                        new_title += title_list[i]
                        new_title += ","
                        new_title += "\s"
                    else:
                        new_title += title_list[i]
                        if (i != (len(title_list) - 1)): # do not add space after last part
                            new_title += "\s"
            # now deal with "("
            title_list = new_title.split("(")
            new_title = ""
            new_title += title_list[0]
            new_title += "\("
            new_title += title_list[1]

            # now deal with ")"
            title_list = new_title.split(")")
            new_title = ""
            new_title += title_list[0]
            new_title += "\)"
            new_title += title_list[1]
        else:
            if title_list[0] in ["a", "an", "the", "le", "la", "les", "der", "die", "das", "el", "los", "las", "il", "lo", "i", "gli"]:
                a_an_the_binary = 1
                new_title_list = []
                for i in range(len(title_list) - 1):
                    new_title_list.append(title_list[i+1])
                new_title_list.append(title_list[0])
                title_list = new_title_list
            # deal with spaces
            for i in range(len(title_list)):
                if (a_an_the_binary == 0):
                    new_title += title_list[i]
                    if (i != (len(title_list) - 1)): # do not add space after last part
                        new_title += "\s"
                else: # if a_an_the_binary==1
                    if (i == (len(title_list) - 2)):
                        new_title += title_list[i]
                        new_title += ","
                        new_title += "\s"
                    else:
                        new_title += title_list[i]
                        if (i != (len(title_list) - 1)): # do not add space after last part
                            new_title += "\s"
        
        # 2A) IF INPUTTED TITLE DOES *NOT* INCLUDE YEAR
        if '(' not in title:
            pattern = r"([0-9]{1,4})%" + new_title + r"+\s\([0-9]{4}\)%.*"
            matches = re.findall(pattern, data) #problem: returning the whole line, not just title

        # 2A) IF INPUTTED TITLE DOES INCLUDE YEAR
        else:
            pattern = r"([0-9]{1,4})%" + new_title + r"+%.*"
            matches = re.findall(pattern, data) #problem: returning the whole line, not just title

        # 2D) DISAMBIGUOUS / CASTING WIDER NET, *NOT* INCLUDING YEAR
        if (self.creative) and ( '(' not in title ):
            pattern = r"([0-9]{1,4})%.*" + new_title + r"+\s+.*\([0-9]{4}\)%.*"
            matches = re.findall(pattern, data) #problem: returning the whole line, not just title
             
        
        # 2C) AKA TITLES, *NOT* INCLUDING YEAR
        if len(matches) == 0:
            pattern = r"([0-9]{1,4})%.*\(a.k.a.\s" + new_title + r"\)+\s\([0-9]{4}\)%.*"
            matches = re.findall(pattern, data) #problem: returning the whole line, not just title

        # 2C) FOREIGN TITLES, *NOT* INCLUDING YEAR
        if len(matches) == 0:
            pattern = r"([0-9]{1,4})%.*\(" + new_title + r"\)+\s\([0-9]{4}\)%.*"
            matches += re.findall(pattern, data) #problem: returning the whole line, not just title
        
        # extracting indices from line string
        for m in matches:
            index_list.append(int(m))
        return index_list


    def extract_sentiment_standard(self, preprocessed_input): 
        sentence = preprocessed_input

        first_quo = sentence.find("\"")
        next_quo = sentence.find("\"", first_quo + 1) 
        checking = True; 
        while checking: 
            sentence = sentence[:first_quo] + sentence[next_quo + 1:]
            first_quo = sentence.find("\"")
            next_quo = sentence.find("\"", first_quo + 1) 
            if first_quo == -1 or next_quo == -1: 
                checking = False; 

        #get rid of . ; and , 
        punc = ".,;"
        for ele in sentence: 
            if ele in punc: 
                sentence = sentence.replace(ele, "")

        ps = PorterStemmer()
        input = sentence.split()
        input_list = self.stem_word(input)

        new_sentiment = {}
        for key in self.sentiment: 
            new_sentiment[ps.stem(key)] = self.sentiment[key]

        negation_list = ["didn't", "not", "never", "don't", "isn't", "wasn't", "neither", "barely", "hardly", "rarely", "seldom", "no", "nothing", "nobody", "none"]
        negation_list = self.stem_word(negation_list)
        
        sum = 0

        transition_words = ["but", "however"]

        for word in input_list: 
            if word in transition_words:
                sum = 0
            elif word in new_sentiment: 

                # account for negaive 
                if input_list.index(word) >= 1 and input_list[input_list.index(word) - 1] in negation_list: 
                    if new_sentiment[word] == 'pos': 
                        sum -= 2
                    if new_sentiment[word] == 'neg':
                        sum += 2
                    
                if input_list.index(word) >= 2 and input_list[input_list.index(word) - 2] in negation_list:
                    if new_sentiment[word] == 'pos': 
                        sum -= 2
                    if new_sentiment[word] == 'neg':
                        sum += 2
                
                if input_list.index(word) >= 3 and input_list[input_list.index(word) - 3] in negation_list:
                    if new_sentiment[word] == 'pos': 
                        sum -= 2
                    if new_sentiment[word] == 'neg':
                        sum += 2

                else: 
                    if new_sentiment[word] == 'pos': 
                        sum += 1
                    if new_sentiment[word] == 'neg':
                        sum -= 1
        if sum > 0:
            sum = 1
        elif sum < 0:
            sum = -1
        else: 
            sum = 0
        return sum 


    def stem_word(self, input_list):
        ps = PorterStemmer()
        stemmed_list = []
        for word in input_list:
            stemmed_list.append(ps.stem(word))
        return stemmed_list

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
        
        if (self.creative == False): 
            return self.extract_sentiment_standard(preprocessed_input)

        else: 
            sentence = preprocessed_input

            first_quo = sentence.find("\"")
            next_quo = sentence.find("\"", first_quo + 1) 
            checking = True; 
            while checking: 
                sentence = sentence[:first_quo] + sentence[next_quo + 1:]
                first_quo = sentence.find("\"")
                next_quo = sentence.find("\"", first_quo + 1) 
                if first_quo == -1 or next_quo == -1: 
                    checking = False; 

            #get rid of . ; and , 
            punc = ".,;"
            for ele in sentence: 
                if ele in punc: 
                    sentence = sentence.replace(ele, "")

            input_list = []
            ps = PorterStemmer()
            input = sentence.split()
            for word in input:
                input_list.append(ps.stem(word))

            new_sentiment = {}
            for key in self.sentiment: 
                new_sentiment[ps.stem(key)] = self.sentiment[key]

            negation_list = ["didn't", "not", "never", "don't", "isn't", "wasn't", "neither", "barely", "hardly", "rarely", "seldom", "no", "nothing", "nobody", "none"]
            sum = 0

            # need to "neutral" - didn't love 
            degree_list = ["love", "hate", "absolute", "ever", "extreme", "total", "really", "reeally", "super", "terrible", "aw", "fantastic", "best", "worst", "!", "!!!", "!!!!", "!!", "!!!!!", "too", "very", "much", "spectacular", "insane", "spectacularly", "great", "favorite"]
            stemmed_degree = []
            for word in degree_list:
                stemmed_degree.append(ps.stem(word))
            
            degree = 1
            
            transition_words = ["but", "however"]

            for word in input_list:
                if word in stemmed_degree:
                    degree = 2
            
            for word in input_list: 
                if word in transition_words:
                    sum = 0
                elif word in new_sentiment: 
                    if input_list.index(word) >= 1 and input_list[input_list.index(word) - 1] in negation_list: 
                        if new_sentiment[word] == 'pos': 
                            sum -= 2
                        if new_sentiment[word] == 'neg':
                            sum += 2
                        
                    if input_list.index(word) >= 2 and input_list[input_list.index(word) - 2] in negation_list:
                        if new_sentiment[word] == 'pos': 
                            sum -= 2
                        if new_sentiment[word] == 'neg':
                            sum += 2
                    
                    if input_list.index(word) >= 3 and input_list[input_list.index(word) - 3] in negation_list:
                        if new_sentiment[word] == 'pos': 
                            sum -= 2
                        if new_sentiment[word] == 'neg':
                            sum += 2

                    else: 
                        if new_sentiment[word] == 'pos': 
                            sum += 1
                        if new_sentiment[word] == 'neg':
                            sum -= 1
            
            score = sum * degree
            if score > 1:
                score = 2
            if score < -1: 
                score = -2
            return score 
            

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
        result = []

        if 'but' in preprocessed_input: 
            index = preprocessed_input.index('but')
            first = preprocessed_input[:index]
            second = preprocessed_input[index:]
            first_movies = self.extract_titles(first)
            second_movies = self.extract_titles(second) 
            first_sentiment = self.extract_sentiment(first)
            second_sentiment = first_sentiment * (-1) 
            for movie in first_movies:
                result.append((movie, first_sentiment))
            for movie in second_movies:
                result.append((movie, second_sentiment))

        elif 'however' in preprocessed_input: 
            index = preprocessed_input.index('however')
            first = preprocessed_input[:index]
            second = preprocessed_input[index:]
            first_movies = self.extract_titles(first)
            second_movies = self.extract_titles(second) 
            first_sentiment = self.extract_sentiment(first)
            second_sentiment = first_sentiment * (-1) 
            for movie in first_movies:
                result.append((movie, first_sentiment))
            for movie in second_movies:
                result.append((movie, second_sentiment))
        
        elif 'and' in preprocessed_input or 'both' in preprocessed_input or 'all' in preprocessed_input or "either" in preprocessed_input or "or" in preprocessed_input: 
            movies = self.extract_titles(preprocessed_input)
            sentiment = self.extract_sentiment(preprocessed_input)
            for movie in movies: 
                result.append((movie, sentiment))
        
        elif 'neither' in preprocessed_input: 
            movies = self.extract_titles(preprocessed_input)
            sentiment = self.extract_sentiment(preprocessed_input) * (-1)
            for movie in movies: 
                result.append((movie, sentiment))
        
        return result 


    def min_edit_distance(self, title, potential_match):
        n = len(title)
        m = len(potential_match)
        d_matrix = np.zeros((n + 1, m + 1))
        
        # costs
        del_cost = 1
        ins_cost = 1
        sub_cost = 2

        # initialize values for just recreating string
        for i in range(1, n + 1):
            d_matrix[i, 0] = d_matrix[i - 1, 0] + del_cost
        
        for j in range(1, m + 1):
            d_matrix[0, j] = d_matrix[0, j - 1] + ins_cost

        # populate matrix 
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                delete = d_matrix[i - 1, j] + del_cost
                insert = d_matrix[i, j - 1] + ins_cost
                substitute = d_matrix[i - 1, j - 1]
                if (title[i - 1].lower() != potential_match[j - 1].lower()):
                    substitute += sub_cost

                d_matrix[i, j] = min(delete, insert, substitute)
        
        return d_matrix[n, m]
    
    
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

        possible_movies = []
        min_distance = max_distance
        
        i = -1
        for movie in self.titles:
            i += 1
            movie = movie[0]

            # truncate if parentheses
            paren_index = movie.find('(')
            if (paren_index != -1):
                movie = movie[:(paren_index - 1)]
            edit_dist = self.min_edit_distance(title, movie)

            # shortest edit distance
            if (edit_dist < min_distance):
                min_distance = edit_dist
                possible_movies = [i]        
            elif (edit_dist == min_distance): # same as max
                possible_movies.append(i)
        
        return possible_movies

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
        movie_identified = []
        can_dict = {}
        for candidate in candidates: 
            can_dict[self.titles[candidate][0]] = candidate
        for key in can_dict: 
            if clarification.isdigit() and len(clarification) == 4: 
                if clarification in key: 
                    movie_identified.append(can_dict[key])
            else: 
                if clarification in key[:len(key) - 6]: 
                    movie_identified.append(can_dict[key])
        
        # need to tackle complex cases?
        
        return movie_identified



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
        stage_1 = np.zeros_like(ratings)
        binarized_ratings = np.zeros_like(ratings)       
        stage_1 = np.where(((ratings >= 0.5) & (ratings <= 2.5)), -1, ratings)
        binarized_ratings = np.where(stage_1 > 2.5, 1, stage_1) 

        return binarized_ratings

    def similarity(self, u, v):
        """Calculate the cosine similarity between two vectors.

        You may assume that the two arguments have the same shape.

        :param u: one vector, as a 1D numpy array
        :param v: another vector, as a 1D numpy array

        :returns: the cosine similarity between the two vectors
        """
        num = np.dot(u, v)
        den = (np.linalg.norm(u) * np.linalg.norm(v))
        if den == 0:
            den += 1e-323               
        cosine_sim = num / den
        return cosine_sim


    def append_ranked(self, list, similarities, movie_index):
        result = []
        
        cur_sim = similarities[movie_index] # can optimize by just passing in similarity 
        for i in range(len(list)):
            elem_index = list[i]
            elem_sim = similarities[elem_index]
            if(cur_sim > elem_sim):
                list.insert(i, movie_index)
                result = list
                return result
        
        list.append(movie_index)
        result = list
        return result
        

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

        recommendations = []
        watched_movies = np.nonzero(user_ratings)[0]
        predicted_ratings = {}
        ranked_list = []

        # loop through each movie
        for i in range(len(user_ratings)):
            # skip movies we have already watched
            if i in watched_movies:
                continue
            
            # store rating
            r_xi = 0
            for rated_movie in watched_movies: # rated movie is j 
                r_xj = user_ratings[rated_movie]
                s_ij = self.similarity(ratings_matrix[i], ratings_matrix[rated_movie])
                r_xi += r_xj * s_ij
                
            # store rating in dict
            predicted_ratings[i] = r_xi
            # update ranked list
            ranked_list = self.append_ranked(ranked_list, predicted_ratings, i)

        recommendations = ranked_list[:k]              
        
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
        if self.creative:
            intro = "This is movie recommending bot that embodies the persona of Cardi B. It is able to take in your feelings about movies and recommend you based on your input. "
        else: 
            intro = "This is movie recommending bot. It is able to take in your feelings about movies and recommend you based on your input. Please be clear with what you say and the movie you are referring to. "
        return intro
        """
        Your task is to implement the chatbot as detailed in the PA7
        instructions.
        Remember: in the starter mode, movie names will come in quotation marks
        and expressions of sentiment will be simple!
        """


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
