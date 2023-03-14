# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import copy
import math
import util
import re
import random
import numpy as np
import re
import heapq
from porter_stemmer import PorterStemmer

CATCH_ALL = 0

GREETINGS_LIST = ["Welcome, welcome, my young friend. Recommend movies, I can. Hmmmm.",
"Watch movies, you must. Learn from them, you will. Mmmmm.",
"Good taste in movies, have you? Hmmmm. Recommend great movies, I will. Yes, hmmm.",
"Ready for movie recommendations, are you? Mmmmm. Strong in the Force, you must be. Watch great movies, you will. Mmmmm.",
"Ah, movie recommendations, you seek. Strong in the ways of cinema, I am. Hmmmm. Suggest great movies, I will.",
"Watch movies, you must. From them, learn you will. Good taste in movies, have you? Hmmmm. Recommend great movies, I can.",
"Movie recommendations, hmmm? Watch great films, you shall. Wise in the ways of cinema, I am. Mmmmm.",
"Patience, young Padawan. Movie recommendations, I have for you. Watch them, you should. Learn from them, you will. Mmmmm."
]

FAREWELL_LIST = ["Watch great movies, you will. Learn from them, you must. Mmmmm. Farewell, I bid you.",
"May the Force be with you on your movie-watching journey. Mmmmm. Farewell, I must.",
"Movie recommendations, I have given. Watch them, you should. Learn from them, you will. Mmmmm. Farewell, young friend.",
"Time to watch movies, it is. Good luck, you have. Mmmmm. Farewell, I bid you.",
"Movie recommendations, follow you must. Enjoy them, I hope. Mmmmm. Farewell, young Padawan.",
"Movie-watching journey, begun it has. Learn from movies, you will. Mmmmm. Farewell, I bid.",
"Watch great movies, you shall. Wisdom from them, you will gain. Mmmmm. Farewell, young friend.",
"Movie recommendations, heed them you should. Enjoy great movies, you will. Mmmmm. Farewell, I must.",
"Journey into the world of cinema, embark you have. Learn from movies, you will. Mmmmm. Farewell, young Padawan.",
"Patience, young one. Watch movies, you will. Learn from them, you must. Mmmmm. Farewell, I bid you."]

CATCH_ALL_LIST = ["The movies, let us not forget. Return to this topic, we must.",
"Movies, our focus should remain. Return to them, we must.",
"Patience, we must have. Return to the topic of movies, we shall.",
"Discussion of movies, let us not stray from. Return to it, we must.",
"Distraction, we must avoid. Return to the topic of movies, we shall.",
"Off topic, we have wandered. Return to movies, we must.",
"Tangents, we must resist. Return to the main topic of movies, we shall.",
"Movies, our main focus should be. Return to them, we must.",
"Back to movies, let us return. Discussion of them, we shall continue.",
"Movies, the topic at hand is. Return to it, we must."]

REC_LIST = ["Considered your preferences, I have. Movie named {}, I recommend. Enjoy, you will.",
"Tailored to your preferences, this movie is. {} movie, I recommend. Watch, you must.",
"A movie to match your tastes, {} is. Recommend it, I do. Watch, you should.",
"Your preferences, taken into account, they have been. {} movie, I suggest. Watch, you must.",
"Movie named {}, perfect for your tastes it is. Watch, you should.",
"Your preferences, carefully considered they have been. Movie named {}, I recommend. Enjoy, you will.",
"{} movie, to your liking it will be. Recommend, I do. Watch, you must.",
"After considering your preferences, {} movie I recommend. Enjoyable, it is.",
"Your preferences, taken into consideration, they have been. {} movie, I recommend. Watch, you must.",
"Considered your preferences, I have. {} movie, highly recommended it is. Watch, you must."]

ASK_FOR_MORE_LIST = ["More recommendations, do you need?",
"Want more recommendations, do you?",
"Need more movies, do you?",
"More movies, would you like?",
"Recommendations, more do you require?",
"Require more recommendations, do you?",
"Desire more movies, do you?",
"More suggestions, would you like?",
"More movies, do you seek?",
"More recommendations, do you crave?",
"Seeking more movie suggestions, are you?",
"More movies, do you want?",
"Desiring more recommendations, are you?",
"Require more movie suggestions, do you do?",
"Need more movie recommendations, do you?",
"More suggestions, do you require?"]

# Responding to positive user sentiment on a movie and probing for more
POS_SENT_REC_PROBE = ["A good movie, {} is. Enjoyed it, did you? What other movies you like, hmm? Share with me, you can. Expand your horizons, we will.",
"{} was an enjoyable movie, it was. Other movies you like, you must have. What are they? Tell me, you must. Discover new movies, together we will.",
"Ah, {} you liked, did you? Good taste in movies, you have. More movies you find interesting, what are they? Please share with me. A journey through cinema, we will embark on.",
"Liked {} you did, hmmm? Watched many movies, I have. Other movies you recommend, what are they? A list, you could give. Together, explore the world of movies, we will.",
"A great movie, {} is. Enjoyed it, you did. What other movies spark joy, in you? Share with me, your favorites. Help you discover new movies, I will.",
"Hmm, {} you liked. A wise movie choice, that was. What other movies you like, I wonder? Share with me, your movie favorites. Together, explore the vast world of cinema, we will.",
"Enjoyed {} you did. Good taste in movies, you have. What other movies you recommend, hmm? Please share with me. Discover new movies, we will. Hmmmm.",
"Ah, {} you liked, did you? A classic movie, that is. What other movies you love, I ask? A list, you could give. Expand your movie knowledge, together we will."]

V_POS_SENT_REC_PROBE = ["Great joy this brings to me, that you loved the movie named {}. What other movies, do you love?",
"Astonishing it is, that the movie named {} you loved. More movies to recommend, I have. Share your favorite ones, will you?",
"Delighted, I am, that the movie named {} you enjoyed. Your movie taste, I must know. What other movies, do you watch?",
"Pleased, I am, that the movie named {} you loved. More recommendations, I have for you. Tell me, what other movies, do you hold dear?",
"Enlightened, I feel, that the movie named {} you loved. But more, you must see. Other movies, you enjoyed, tell me.",
"Thrilled, I am, that the movie named {} you loved. Hmm, curious about your taste in movies, I am. What other movies, have you adored?",
"Impressed, I am, that the movie named {} you loved. But much more, there is to see. More movie recommendations, do you seek?",
"Overjoyed, I am, that the movie named {} you loved. Other great movies, there are. Your opinion, I want. What other movies, have you loved?"]

NEG_SENT_REC_PROBE = ["Hmm, {} you did not like. Disappointed, I am. But fear not, the taste in movies, it is subjective. What other movies you have seen, I ask?",
"Did not enjoy {} you did. Understandable, that is. What other movies you have watched, I ask? Share with me, your movie journey. Discover more about your preferences, we will.",
"Hmm, not a fan of {} you were. Disappointed, I am. But perhaps, other movies you have seen? Share with me, your movie experiences. Together, learn more about the movies you like, we will.",
"Disliked {} you did, hmmm. Unfortunate, that is. But no need to fret, other movies you have watched, I am sure. Please share with me, your movie journey. Discover more about your preferences, we will.",
"Hmm, {} did not resonate with you. Understandable, that is. Other movies you have seen, there must be. Tell me, your movie tastes I want to understand.",
"Unimpressed with {} you were. Curious, I am. Other movies you have watched, there are? Share with me, your thoughts on them.",
"Hmm, {} did not capture your attention. Intrigued, I am. Other movies you have viewed, there must be. Speak of them, you should.",
"Did not enjoy {} you did. Disappointed, I am. Other movies you have seen, there are? To know your preferences better, I wish."]

V_NEG_SENT_REC_PROBE = ["Strong, your emotions are! Hated {} you did. Tell me more, I will. Understand your movie tastes, I must.",
"Dislike {} strongly, you did. More movies you have seen, tell me. Learn about your preferences, I will.",
"Hated {} you did? Strong, your reaction is. Other movies you enjoy, I must know. Recommend better movies to you, I can.",
"Hate, hate, hate {} you do! Understand your movie tastes, I must. More movies you have seen, share with me, you will.",
"Disliked {} greatly, you did. Learn more about your preferences, I will. More movies you have seen, tell me, hmm?"]

NEUTRAL_SENT = ["Mixed your feelings are about {}, hmmm? Clarify, you must. Like it, did you? Or like it not?",
"Unclear, your opinion of {} is. Speak with certainty, you should. Enjoy it, did you? Or enjoy it not?",
"Confused, I am. Your thoughts on {} are muddled. Help me understand, you must. Did you like it, or did you not?",
"Difficult to discern, your reaction to {} is. Elaborate, you should. Did you find it pleasing, or displeasing?",
"Confused, your words make me. Like {} did you, or not like it? Speak plainly, you must.",
"Unclear, your answer is. Did you enjoy {} or not? Make up your mind, you must.",
"Hazy, your judgment is. Like or not like {}? Tell me clearly, you must.",
"Mixed, your emotions are. Did you appreciate {} or not? Tell me, you must.",
"Ambiguous, your response is. Like {} you did, or did not like it? Help me understand, you must."]

MULT_MOVIES_POS_PROBE = ["Pleased I am, to hear that you enjoyed {}. More movies, I must hear of.",
                   "Mmmm. {}, you enjoyed. More movies, I must hear of.",
                   "Glad I am, to hear of your enjoyment of {}. More movies I must hear from you",
                   "Pleased to hear I am, that you enjoyed watching {}. More movies you must tell me of."]

MULT_MOVIES_NEG_PROBE = ["Hmm, {} you did not like. Disappointed, I am. But fear not, the taste in movies, it is subjective. What other movies you have seen, I ask?",
"None of {} did you enjoy. Understandable, that is. What other movies you have watched, I ask? Share with me, your movie journey. Discover more about your preferences, we will.",
"Hmm, not a fan of {} you were. Disappointed, I am. But perhaps, other movies you have seen? Share with me, your movie experiences. Together, learn more about the movies you like, we will."]

MULT_MOVIES_V_POS_PROBE = ["Great joy this brings to me, that you loved the movies named {}. What other movies, do you love?",
"Astonishing it is, that the movise named {} you loved. More movies to recommend, I have. Share your favorite ones, will you?",
"Delighted, I am, that the movies named {} you enjoyed. Your movie taste, I must know. What other movies, do you watch?",
"Pleased, I am, that the movies named {} you loved. More recommendations, I have for you. Tell me, what other movies, do you hold dear?",
"Enlightened, I feel, that the movies named {} you loved. But more, you must see. Other movies, you enjoyed, tell me."]



# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'moviebot'

        self.creative = creative

        self.p = PorterStemmer()

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')

        self.stemmed_sentiment = {}
        for key in self.sentiment:
            stemmed_key = self.p.stem(key)
            self.stemmed_sentiment[stemmed_key] = self.sentiment[key]

        """ These are global variables for process()"""
        # self.user_ratings stores the binarized ratings a user has given
        self.user_ratings = np.zeros(9125)
        self.titles_received = []
        # self.ratings_matrix is stored here so that we do not run binarize each time process() is called

        # self.recommendations_given keeps track of how many recommendations a user has been given so we know which to give next
        self.recommendations_given = 0

        # self.last_movie_mentioned keeps track of which movie they mentioned last when we ask them to clarify their sentiment
        # example: "I saw Titanic (1995)". "Please clarify." "I liked it."
        self.last_title_mentioned = ''

        # self.last_input_line stores the last input line so we can remember their sentiment for when we ask a user to clarify which movie they meant
        # example: "I liked 'Titanic'." "Which one?" "'Titanic(1995)"
        self.last_input_line = ''

        # a list to store the potential movies a user might mean when they don't clarify the first time
        self.potential_movies = []

        # list of movies to recommend
        self.rec_titles = []


        ########################################################################
        # TODO: Binarize the movie ratings matrix.                             #
        ########################################################################

        # Binarize the movie ratings before storing the binarized matrix.
        ratings = self.binarize(ratings)
        self.ratings = ratings
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


        greeting_message = random.choice(GREETINGS_LIST);

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

        goodbye_message = random.choice(FAREWELL_LIST)

        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return goodbye_message

    ############################################################################
    # 2. Modules 2 and 3: extraction and transformation                        #
    ############################################################################
    def find_closest_movie_by_date(self, title):
        # get the date from their input, and covert to an int
        title_date = int(title[-5:-1])
        
        # initialzie a variable to store which title is closest in date
        closest_index = 0

        # initialize variable to store the gap between their input and an actual movie in the database
        smallest_gap = 100

        # iterate through all the potential movies
        for i in range(len(self.potential_movies)):
            # get the date from each movie ibn potential movies
            date = int(self.potential_movies[i][-5:-1])

            # calculate the difference between input date and this movie's date
            if abs(title_date - date) < smallest_gap:
                # if closer than any other movie, store this movie and gap
                smallest_gap = abs(title_date - date)
                closest_index = i

        return self.potential_movies[closest_index]
    
    # function for when chatbot has already given user recommendations
    def give_recommendations(self, line):
        answer = ''
        yes = ['yes', 'yeah' , 'sure', 'yep', 'ok', 'ya']
        no = ['no', 'nope', 'nah']

        for word in yes:
            if word in line.lower():
                answer = 'yes'
        
        for word in no:
            if word in line.lower():
                answer = 'no'
        # if the user responds yes and has already been given movie recommendations, then they want the next recommendation
        if answer == 'yes':
            # to alternate responses for diversity, one possible response
            #if self.recommendations_given % 2 == 0:
            response = random.choice(REC_LIST).format(self.rec_titles[self.recommendations_given]) \
                        + "\n" + random.choice(ASK_FOR_MORE_LIST)
                #response = "I would also recommend " + self.rec_titles[self.recommendations_given] + ". How about another one?"
            # another possible response 
            # else:
            #     response = self.rec_titles[self.recommendations_given] + " would be a good movie for you! Would you like more recommendations?"
            self.recommendations_given += 1
            return response
        
        # if the user responds no and has already been given movie recommendations, then they want to end
        if answer == 'no':
            response = random.choice(FAREWELL_LIST)
            return response
       
        else: 
            response = random.choice(ASK_FOR_MORE_LIST)

        return response
    
    # function to handle data point 1-4
    def handle_data_point(self, sentiment, movie_index, title):
        movie = self.titles[movie_index][0]

        # if it is a positive sentiment
        if sentiment == 1:
            self.user_ratings[movie_index] = 1
            response = random.choice(POS_SENT_REC_PROBE).format(movie)
            #response = "OK, you liked " + movie + "! Tell me what you thought of another movie."
            return response

        # if it is a negative sentiment
        if sentiment == -1:
            self.user_ratings[movie_index] = -1
            response = random.choice(NEG_SENT_REC_PROBE).format(movie)
            #response = "I'm sorry you didn't like " + movie + ":(. Tell me what you thought of another movie."
            return response
        
        if sentiment == 2:
            self.user_ratings[movie_index] = 2
            response = random.choice(V_POS_SENT_REC_PROBE).format(movie)
            return response        
        
        if sentiment == -2:
            self.user_ratings[movie_index] = -2
            response = random.choice(V_NEG_SENT_REC_PROBE).format(movie)
            return response  

        # if it is a neutral sentiment
        if sentiment == 0:
            # remove the movie we just added
            self.titles_received.pop()
            # store the title globally so we remember in case they don't mention it next time
            if self.last_title_mentioned == '':
                self.last_title_mentioned = movie
            response = random.choice(NEUTRAL_SENT).format(movie)
            #response = "I'm sorry, I'm not sure if you liked " + movie + ". Tell me more about it."
            return response
    
    # function to handle when user provides the fifth data point, so the chatbot moves on to giving recs
    def handle_fifth_data_point(self, sentiment, movie_index, ratings_matrix):
        # if it is a positive sentiment
        if sentiment == 1:
            self.user_ratings[movie_index] = 1

        # if it is a negative sentiment
        if sentiment == -1:
            self.user_ratings[movie_index] = -1

        # user has given 5 data points, so build recommendations list
        self.recommendations = self.recommend(self.user_ratings, ratings_matrix, k=100)


        for index in self.recommendations:
            self.rec_titles.append(self.titles[index][0])


        # this variable keeps track of how many movie recommendations we have given to know which movie to recommend next
        response = random.choice(REC_LIST).format(self.rec_titles[self.recommendations_given]) \
                            + "\n" + random.choice(ASK_FOR_MORE_LIST)
        #response = "Given what you told me, I think you would like " + self.rec_titles[self.recommendations_given] + ". Would you like more recommendations?"
        self.recommendations_given += 1
        return response
   
    # function to handle when user asks a question
    def handle_question(self, line):
        request = ''
    
        if 'can you' in line.lower():
            request =  line.lower().replace('can you', '')
            request = request.replace('?','.')
            request = request.replace(' me ',' you ')
            request = request.replace(' my ',' your ')
            request = request.replace(' I ',' you ')
            request = request.replace(' your ',' my ')
            response = "Mmmm. " + request + " I cannot do. " + random.choice(CATCH_ALL_LIST)

        if 'what is' in line.lower():
            request = line.lower().replace('what is', '')
            request = request.replace('?','')
            request = request.replace(' me ',' you ')
            request = request.replace(' my ',' your ')
            request = request.replace(' I ',' you ')
            request = request.replace(' your ',' my ')
            response = "Mmmm. " + request + " I know not " + random.choice(CATCH_ALL_LIST) 

        if 'what is' not in line.lower() and 'can you' not in line.lower():
            response = "Answer your question, I cannot. " + random.choice(CATCH_ALL_LIST)

        # chatbot has not given movie recs
        if self.recommendations_given == 0:
            response += " Seen many movies, have you? Which ones, can you recall?"
        
        # chatbot has already started giving movie recs
        if self.recommendations_given > 0:
            response += " " + random.choice(ASK_FOR_MORE_LIST)
            #response += " Let's get back to that. Would you like to hear another?"
        
        return response
    
    def handle_2_plus_movies(self, title, movie_index, ratings_matrix, line):
        response = ''
        movie_string = ''
        movies = []
        indices = []
        for i in range(len(title)):
            index = self.find_movies_by_title(title[i])[0]
            indices.append(index)
            movies.append(self.titles[index][0])

        # remove movies from line to do sentiment
        line_without_titles = line

        for i in range(len(title)):
            
            movie_name = title[i]

            movie_name = movie_name.lower()

            if line_without_titles.lower().find(movie_name.lower()) != -1:
                begin = line_without_titles.lower().index(movie_name.lower())
                length = len(movie_name)
                line_without_titles = line_without_titles[:begin] + line_without_titles[begin + length + 1:]



        # extract the sentiment -- do we pass in self?
        sentiment = self.extract_sentiment(line_without_titles)

        # add the title to the global list of titles
        for i in range(len(movies)):
            # add the movies that we have found, with real names to global variable
            self.titles_received.append(self.titles[indices[i]])

            # make this global variable empty again
            self.last_title_mentioned = ''
            self.potential_movies = []

            # make this global variable empty agiain
            self.last_input_line = ''

            # if we are at the fifth data point, move on to recommending movies
            if sentiment != 0 and len(self.titles_received) == 5:
                response = ''
                # if it is a positive sentiment
                if sentiment == 1:
                    self.user_ratings[indices[i]] = 1

                # if it is a negative sentiment
                if sentiment == -1:
                    self.user_ratings[indices] = -1
                    

                # user has given 5 data points, so build recommendations list
                self.recommendations = self.recommend(self.user_ratings, ratings_matrix, k=100)


                for j in range(len(self.recommendations)):
                    self.rec_titles.append(self.titles[j][0])


                # at last movie (i.e. in shrek and scream, we are at scream)
                if i == len(title) - 1:
                    response = random.choice(REC_LIST).format(self.rec_titles[self.recommendations_given]) \
                            + "\n" + random.choice(ASK_FOR_MORE_LIST)
                self.recommendations_given += 1

            # if they gave us a valid movie and we are at data points 1-4
            else:
                movie = movies[i]
                if i == 0:
                    movie_string += movie
                if len(title) > 2 and i != 0 and i != len(title) - 1:
                    movie_string += ", " + movie
                elif i == len(title) - 1:
                    movie_string += " and " + movie

                # if it is a positive sentiment
                if sentiment == 1:
                    self.user_ratings[indices[i]] = 1
                    if i == len(title) - 1:
                        response = random.choice(MULT_MOVIES_POS_PROBE).format(movie_string)

                # if it is a very positive sentiment
                if sentiment == 2:
                    self.user_ratings[indices[i]] = 1
                    if i == len(title) - 1:
                        response = random.choice(MULT_MOVIES_V_POS_PROBE).format(movie_string)

                # if it is a negative sentiment
                if sentiment == -1 or sentiment == -2:
                    self.user_ratings[indices[i]] = -1
                    if i == len(title) - 1:
                        response = random.choice(MULT_MOVIES_NEG_PROBE).format(movie_string)
            
        
        return response


        

    
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



        ratings_matrix = self.ratings
            
        # if user asks a question
        if line[-1] == "?":
            response = self.handle_question(line)
            return response
        
        # if we have already started giving recommendations
        if self.recommendations_given > 0:
            response = self.give_recommendations(line)
            return response
        
        
        # extract the title from their line of input
        title = self.extract_titles(line)
        # title = ['Shrek'] or title =['Shrek', 'Finding Nemo']

        # the user is trying to clarify a movie, without using the full title or quotation marks
        #I like "Titanic" --> Which one? --> 1997
        if len(self.potential_movies) > 0 and self.last_input_line != '' and self.last_title_mentioned != '' and len(title) == 0:
            title.append(self.last_title_mentioned)
            candidates = []

            # this is to avoid the bug where inputing wrong first clarification (1995) for titanic makes the self.potential_movies double
            old_potential_movies = []
            for potential in self.potential_movies:
                old_potential_movies.append(potential)
            for i in range(len(self.potential_movies)): #['Titanic (1997)', 'Titanic (1953)']
                index = self.find_movies_by_title(self.potential_movies[i])
                candidates.append(index[0])
            movies = self.disambiguate(line, candidates)
            # we were able to clarify the movies they like
            if len(movies) == 1:
                title = []
                one_movie = movies[0]
                title.append(self.titles[one_movie][0])
                line = self.last_input_line
                self.last_input_line = ''
                self.last_title_mentioned = ''
                self.potential_movies = []
            if len(movies) > 1:
                # avoid repeating potential movies twice bug
                self.potential_movies = []
                for movie in movies:
                    self.potential_movies.append(self.titles[movie][0])
                    
                potential_movies_string = ''
                if len(self.potential_movies) == 2:
                    potential_movies_string = self.potential_movies[0] + ' or ' + self.potential_movies[1]
                else:
                    for i in range(len(self.potential_movies)):
                        if i == len(self.potential_movies) - 1:
                            potential_movies_string += ' or ' + self.potential_movies[i] 
                        else:
                            potential_movies_string += self.potential_movies[i]  + ', '
                response = "More than one movie, I found. You meant " + potential_movies_string + ", did you?"
                # do we need to store their previous line to remember sentiment?
                self.last_title_mentioned = title[0]
                return response
            if len(movies) == 0:
                self.potential_movies = []
                self.potential_movies = old_potential_movies
                potential_movies_string = ''
                if len(self.potential_movies) == 2:
                    potential_movies_string = self.potential_movies[0] + ' or ' + self.potential_movies[1]
                else:
                    for i in range(len(self.potential_movies)):
                        if i == len(self.potential_movies) - 1:
                            potential_movies_string += ' or ' + self.potential_movies[i] 
                        else:
                            potential_movies_string += self.potential_movies[i]  + ', '
                response = "None movie of that kind there is. Meant you " + potential_movies_string
                return response


        unhappy_words = ["angry", "mad", "frustrated", "irritated", "upset", "annoyed", "disappointed", "sad", "hurt", "betrayed", "distressed", "devastated", "depressed", "overwhelmed", "confused", "anxious"]
        happy_words = ['happy', 'pleased', 'joyful', 'delighted', 'grateful', 'ecstatic', 'thrilled', 'content', 'satisfied', 'overjoyed', 'elated', 'exhilarated', 'enchanted', 'exultant', 'radiant', 'jubilant', 'blissful', 'fulfilled']
        punc = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''

        # if the user did not give anything in quotation marks AND they are not clarifying a sentiment
        if len(title) == 0 and self.last_title_mentioned == '':
            # break input into list of strings
            list_of_words = line.split()
            # go word by word to check if happy/unhappy word
            for word in list_of_words:
                # convert word to lower
                word = word.lower()
                # remove punctuation 
                for char in word:
                    if char in punc:
                        word = word.replace(char, "") 
                # check if word is unhappy, respond accordingly
                if any(word in words for words in unhappy_words):
                    response = word + ", did I make you? Apologize, I must."
                # check if word is happy, respond accordingly
                elif any(word in words for words in happy_words):
                    response = "Glad I am, that you feel " + word + "."
                # if neither happy nor sad sentiment, return catch all
        # figure out later how to make this less awkward]
                else:
                    response = random.choice(CATCH_ALL_LIST)
            return response
        
        # if the user did give a title OR they are clarifying sentiment
        else:
            # if the user switches topics but does not give another movie, example "Titanic" --> which one did you mean --> I like cheese.
            if len(title) == 0:
                # break input into list of strings
                list_of_words = line.split()
                # go word by word to check if happy/unhappy word
                for word in list_of_words:
                    # convert word to lower
                    word = word.lower()
                    # remove punctuation 
                    for char in word:
                        if char in punc:
                            word = word.replace(char, "") 
                    # check if word is unhappy, respond accordingly
                    if word in unhappy_words:
                        response = "My apologies, I offer. Make you " + word + ", did I? Forgive me, I hope you can."
                    elif any(word in words for words in happy_words):
                        response = "Glad I am, that you feel " + word + "."
                    # if neither happy nor sad sentiment, return catch all
                    else:
                        response = random.choice(CATCH_ALL_LIST)
                return response

            # if the user is switching topics and gives a different movie
            # example: gave "Titanic (1995)" then said "I like "King Kong"""
            if len(title) != 0:
                if self.last_title_mentioned != '' and self.last_title_mentioned not in title[0]:
                    self.last_title_mentioned = ''
                    self.last_input_line = ''
                    self.potential_movies = []

            # this is the case where the user is clarifying sentiment and they did not give the title again
            # I saw "Titanic" --> I liked it.
            if self.last_title_mentioned != '' and self.last_input_line == '':
                title = []
                title.append(self.last_title_mentioned) 

            # if they gave us more than one title
            if len(title) > 1:
                indices = []
                for i in range(len(title)):
                    movie_index = self.find_movies_by_title(title[i])
                    for index in movie_index:
                        indices.append(index)
                response = self.handle_2_plus_movies(title, indices, ratings_matrix, line)
                return response
            
            # check that it is in the movie databse
            movie_index = self.find_movies_by_title(title[0])


            # if not in our movie database AND they are not clarifying
            # we need to account for a case where they are clarifying (self.last_input_line is filled) AND movie not in database
            if len(movie_index) == 0 and self.last_input_line == '':

                response = "Never heard of " + title[0] + " I have. Other movies, you must give."
                return response
            
            # the case where we are trying to identify the right title, they gave us a wrong one when trying to specify which
            # example: gave us "Titanic (1995)"
        
            if len(movie_index) == 0 and self.last_input_line != '':
                # create list of possible movies
                potential_movies_string = ''
                if len(self.potential_movies) == 2:
                    potential_movies_string = self.potential_movies[0] + ' or ' + self.potential_movies[1]
                else:
                    for i in range(len(self.potential_movies)):
                        if i == len(self.potential_movies) - 1:
                            potential_movies_string += ' or ' + self.potential_movies[i] 
                        else:
                            potential_movies_string += self.potential_movies[i]  + ', '
                response = "Never heard of " + title[0] + ", I have. " + potential_movies_string + ", did you mean?"
                return response
            
                

            # if the title that they gave can be more than one movie, it's the first time we ask them to clarify
            if len(movie_index) > 1:
                # create list of possible movies
                potential_movies_string = ''
                if len(self.potential_movies) == 2:
                    potential_movies_string = self.potential_movies[0] + ' or ' + self.potential_movies[1]
                else:
                    for i in range(len(self.potential_movies)):
                        if i == len(self.potential_movies) - 1:
                            potential_movies_string += ' or ' + self.potential_movies[i] 
                        else:
                            potential_movies_string += self.potential_movies[i]  + ', '
                response = "More than one " + title[0] + " there is. Meant you " + potential_movies_string + "?"
                # do we need to store their previous line to remember sentiment?
                self.last_title_mentioned = title[0]
                self.last_input_line = line
                return response
            
            # they gave us a valid line of input, and we found a corresponding title in our database
            else:

                # add the title to the global list of titles
                self.titles_received.append(self.titles[movie_index[0]])

                # make this global variable empty again
                self.last_title_mentioned = ''
                self.potential_movies = []

                # if they are clarifying which movie they gave without giving sentiment again
                if self.last_input_line != '':
                    line = self.last_input_line
                # make this global variable empty agiain
                self.last_input_line = ''

                line_without_titles = line
                for i in range(len(title)):
                    #movie_name = title[i][:-7]  #["Conjuring, The (2009)"] --> 'conjuring, the (2009)' --> conjuring, the' in line 'i like conjuring'
                    movie_name = title[i]
                    if ', the' in movie_name.lower():
                        movie_name = movie_name.replace(', The', '')
                    movie_name = movie_name.lower()

                    if line_without_titles.lower().find(movie_name.lower()) != -1:
                        begin = line_without_titles.lower().index(movie_name.lower())
                        length = len(movie_name)
                        line_without_titles = line_without_titles[:begin] + line_without_titles[begin + length + 1:]
            


                # extract the sentiment -- do we pass in self?
                sentiment = self.extract_sentiment(line_without_titles)


                # if we are at the fifth data point, move on to recommending movies
                if sentiment != 0 and len(self.titles_received) == 5:
                    response = self.handle_fifth_data_point(sentiment, movie_index[0], ratings_matrix)
                    return response

                # if they gave us a valid movie and we are at data points 1-4
                else:
                    response = self.handle_data_point(sentiment, movie_index[0], title)
                    return response


    ########################################################################
    #                          END OF YOUR CODE                            #
    ########################################################################
    #return response

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
        
        regex = "\"(.[^\"]+)\""
        result = re.findall(regex, str(preprocessed_input))

        longest_title = 0

        punctuation = ['.', '!']

        avoid_phrases = ['i', 'i am', 'and', 'you', 'you are', 'you make me', 'i like', 'but', 'like', 'did', 'not', 'liked', 'are', 'am', 'a', 'the']
  
        # handle " i like 10 things i hate about you"
        if len(result) == 0 and self.last_title_mentioned == '' and self.last_input_line == '':
            result = []
            preprocessed_input = preprocessed_input.lower()
            for punc in punctuation:
                preprocessed_input = preprocessed_input.replace(punc, '')
            word_array = preprocessed_input.split()
    
            for i in range(len(word_array)):
                title = word_array[i]
                for j in range (i, len(word_array)):
                    if j != i:
                        title += " " + word_array[j]
                    if title.lower() not in avoid_phrases and (j-1+1) < 10:
                        for k in range(len(self.titles)):
                            if self.titles[k][0][: len(title) + 2].lower() == title.lower() + " (" or self.titles[k][0][: len(title) + 2].lower() == title.lower() + ", ":
                                if (j - i + 1) > longest_title:
                                    longest_title = j -i + 1
                                    # we found a longer title, reset result so it doesn't include shorter titles
                                    result = []
                                    result.append(title)
                                    # MAYBE DELETE
                                    self.last_input_line = preprocessed_input
                                    #self.last_title_mentioned = title
                                if (j - i + 1) == longest_title:
                                    if title not in result:
                                        result.append(title)
                                    # if self.titles[k][0] not in result:
                                    #     result.append(self.titles[k][0])
                                #result.append(self.titles[k][0])

        if len(result) == 0 and self.last_title_mentioned == '' and self.last_input_line == '':
            #print("in final wide search")
            result = []
            word_array = preprocessed_input.split()

            for i in range(len(word_array)):
                title = word_array[i]
                for j in range (i, len(word_array)):
                    if j != i:
                        title += " " + word_array[j]
                    #print(title)
                    for k in range(len(self.titles)):
                        if title not in avoid_phrases:                   
                            if self.titles[k][0][: len(title) + 4].lower() == title.lower() + ' and':
                                if title.lower() != 'i':
                                    if (j - i + 1) > longest_title:
                                        longest_title = j -i + 1
                                        # we found a longer title, reset result so it doesn't include shorter titles
                                        result = []
                                        result.append(title)
                                        self.last_input_line = preprocessed_input
                                    if (j - i + 1) == longest_title:
                                        if title not in result:
                                            result.append(title)


        return result
        
         

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


        # store the indices in a list
        indices = []
        # get the length of the title to account for when more than one title is returned


        if title == '' or title == ' ':
            return indices
        
        if title[:4].lower() == 'the ' and re.match(r".*(\(\d{4}\))$", title[-6:]):
            beginning = title[4:-7]
            middle = ', ' + title[:4]
            end = title[-6:]
            new_title = beginning + middle + end
            title = new_title

        if title[:3].lower() == 'an ' and re.match(r".*(\(\d{4}\))$", title[-6:]):
            beginning = title[3:-7]
            middle = ', ' + title[:3]
            end = title[-6:]
            new_title = beginning + middle + end
            title = new_title

        if title[:2].lower() == 'a ' and re.match(r".*(\(\d{4}\))$", title[-6:]):
            beginning = title[2:-7]
            middle = ', ' + title[:2]
            end = title[-6:]
            new_title = beginning + middle + end
            title = new_title

        title_length = len(title)

        sequels = []

        for i in range(9):
            sequel = '' 
            sequel += title + ' ' + str(i) + ' ('
            sequel = sequel.lower()
            sequels.append(sequel)


        # iterate through all the titles
        for i in range(len(self.titles)):
            if self.titles[i][0][:title_length + 2].lower() == title.lower() + ' (' or self.titles[i][0].lower() == title.lower() or self.titles[i][0][:title_length + 1].lower() == title.lower() + ',' or self.titles[i][0][:title_length + 4].lower() in sequels: 
                indices.append(i)
                # we are NOT trying to disambiguate
                self.potential_movies.append(self.titles[i][0])


        # widen search if nothing found
        if len(indices) == 0:
            for i in range(len(self.titles)):
                # "Harry Potter" --> indices for ["Harry Potter and the Sorcerer's Stone...", "Harry Potter and the Prisoner of..."]
                if self.titles[i][0][:title_length].lower() == title.lower(): #Titanic --> Titanic (!975) Titanic (1997)
                    indices.append(i)
                    self.potential_movies.append(self.titles[i][0])
        # continue to widen search if nothing is found --> in this case handle an alternate title or a foreign title
        # e.g., if the user input is "Se7en", this should return the index for "Seven (a.k.a. Se7en) (1995)" 
        # e.g., if the user input is "Gazon maudit", this should return the index for French Twist (Gazon maudit) (1995) 
        if len(indices) == 0:
            substring_alternate_title = "a.k.a. " + title
            substring_foreign_title = "(" + title + ") " + "("
            for i in range(len(self.titles)):
                if substring_alternate_title in self.titles[i][0] or substring_foreign_title in self.titles[i][0]:
                    indices.append(i)
                    self.potential_movies.append(self.titles[i][0])
                    
        # continue to widen search if nothing is found --> in this case handle a foreign article
        # e.g., if the input is "La Guerre du feu", this should return the index for "Quest for Fire (Guerre du feu, La) (1981)"
        if len(indices) == 0 and len(title.split()) > 1:
            title_list = title.split()
            substring_foreign_article = str(title_list[1])
            for i in range(len(title_list) - 2):
                substring_foreign_article += (" " + str(title_list[i + 2]))
            substring_foreign_article += (", " + str(title_list[0]))

            for i in range(len(self.titles)):
                if substring_foreign_article in self.titles[i][0]:
                    indices.append(i)
        return indices
        
        

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
        strong_pos_adj = ["amazing", "awesome", "brilliant", "captivating", "engaging", 
               "enthralling", "fantastic", "impressive", "masterful", 
               "memorable", "phenomenal", "riveting", "spectacular", 
               "superb", "thrilling", "stunning", "mesmerizing", 
               "mind-blowing", "unforgettable", "outstanding", "love", "adore", "cherish", "treasure", "delight",
                "enchant", "fascinate", "thrill", "exhilarate",
                "rejoice", "celebrate", "embrace", "appreciate",
                "glow", "laugh", "bless", "savor"]
        strong_neg_adj = ["terrible", "horrible", "atrocious", "appalling", "disastrous",
                "dreadful", "abysmal", "awful", "repulsive",
                "offensive", "unwatchable", "miserable", "painful",
                "boring", "tedious", "insipid", "lackluster",
                "underwhelming", "disappointing", "frustrating", "hate", "detest", "despise", "loath",
                "disgust", "revile", "execrate", "reject",
                "spurn", "abandon", "avoid", "dismiss",
                "ignore", "scorn", "criticize", "blame",
                "condemn", "curse", "vilify"]
        amplifying = ["really", "super", "very"]

        punctuation = ['.', '!']
        for punc in punctuation:
            preprocessed_input = preprocessed_input.replace(punc, '')


        for i in range(len(strong_neg_adj)):
            strong_neg_adj[i] = self.p.stem(strong_neg_adj[i])

        for i in range(len(strong_pos_adj)):
            strong_pos_adj[i] = self.p.stem(strong_pos_adj[i])

        strong_pos_present = False
        strong_neg_present = False
        amplify_present = False

        # turn the preprocesed input into an array of words
        list_of_words = preprocessed_input.split()

        for i in range(len(list_of_words)):
            if list_of_words[i] not in amplifying:
                list_of_words[i] = self.p.stem(list_of_words[i])

        # turn the words into stem version, example "liked" -> "like"
        
        # initialize variables to store sums
        positive = 0
        negative = 0

        negation_words = ['didn\'t', 'don\'t', 'not', 'nobody', 'none', 'nothing', 'never']

        flip = 1

        

        # [i, like, this, movie]
        for i in range(len(list_of_words)):
            if list_of_words[i] in negation_words:
                flip *= -1
            if list_of_words[i] in strong_pos_adj:
                strong_pos_present = True
            if list_of_words[i] in strong_neg_adj:
                strong_neg_present = True
            if list_of_words[i] in amplifying:
                if list_of_words[i-1] not in negation_words:
                    amplify_present = True
            if list_of_words[i] in self.stemmed_sentiment:
                if self.stemmed_sentiment[list_of_words[i]]== 'pos':
                    positive += 1
                if self.stemmed_sentiment[list_of_words[i]] == 'neg':
                    negative -= 1

        # Using a positive to negative word ratio to determine sentiment
        sentiment = 0
        # more positive than negative
        if (positive + negative) > 0:
            sentiment = 1
        # more negative than positive
        if (positive + negative) < 0:
            sentiment = -1 

        if strong_pos_present == True and sentiment == 1:
            sentiment = 2
        if strong_neg_present == True and sentiment == -1:
            sentiment = -2

        if sentiment < 2 and sentiment > -2:
            if amplify_present == True:
                sentiment *= 2
            
        sentiment *= flip
    
        return sentiment

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

        num_movies = len(titles)

        # remove title from line so we don't accidentally use it for sentiment
        for title in titles:
            preprocessed_input.replace(title, '')
        

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

        pass

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
        possible_movies = []

        for candidate in candidates:
            candidate_name = self.titles[candidate][0].lower()
            if clarification.lower() in candidate_name:
                possible_movies.append(candidate)

        return possible_movies
        
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
        
        # make a copy of the matrix to binarize
        # binarized_ratings = ratings

        # iterate through each vector in the matrix
        for j in range(len(ratings)):
            ratings_vec = np.ndarray.tolist(ratings[j])
            # iterate through each rating in the vector
            for i in range(len(ratings_vec)):
                if ratings_vec[i] == 0:
                    continue
                elif ratings_vec[i] > threshold:
                    ratings_vec[i] = 1
                elif ratings_vec[i] <= threshold:
                    ratings_vec[i] = -1
            binarized_ratings[j] = np.asarray(ratings_vec)



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
        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return similarity
    



    """
    Constructs a sets of movies the user has not seen and seen using the user_ratings nparray
    passed into recommend. This ensures we do not compute cosine similarities between
    not seen movies and movies in the ratings matrix.
    """
    def construct_seen_and_not_seen_sets(self, user_ratings):
        not_seen = set()
        seen = set()
        for i in range(len(user_ratings)):
            if user_ratings[i] == 0:
                not_seen.add(i)
            else:
                seen.add(i)
        return seen, not_seen

    """
    Calculates the raw recommendation score for a given movie the user hasn't seen
    (denoted by movie_index) using the formula given on Slide 59 of Recommender Systems
    lecture. 
    """
    def calculate_rec_score(self, movie_index, seen, ratings_matrix, user_ratings):
        
        # Looping through the matrix 
        rec_score = 0

        cosine_sim_to_movie = []
        movie_arr = ratings_matrix[movie_index]

        # Looping and calculating all the cosine similrities between unseen
        # movie and all other movies seen by the user 
        for index in seen:
            if not movie_arr.any() or not ratings_matrix[index].any():
                continue
            cosine_sim = (np.dot(movie_arr, ratings_matrix[index])) / \
                (np.linalg.norm(movie_arr) * np.linalg.norm(ratings_matrix[index]))
            cosine_sim_to_movie.append((index, cosine_sim))


        #Loop through all cosine similarities and get final score
        for cosine_movie_tuple in cosine_sim_to_movie:
            rec_score += (cosine_movie_tuple[1] * user_ratings[cosine_movie_tuple[0]])
        
        return rec_score    
            
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

        # user_ratings : [ 1, -1, 1, 0, ....]
        #                          user_1  user_2    ....
        # ratings_matrix: movie_1 : [ 1   ,    -1    , ...]
        #                 movie_2 : [ 1   ,     1,   , ...]
        #                   ...

        # Where a Recommendation score is basically user's predicted drating for a movie based on
        # prior ratings for simliar movies

        # Make a sets of movie indices the user has seen and NOT seen before
        # ERROR: the function below is not found
        seen, not_seen = self.construct_seen_and_not_seen_sets(user_ratings)

        # recommendation scores of the form -> (Movie we haven't seen index, rec score)
        recommendation_scores = []

        # Go through every movie a user has not seen and calculate a rec score
        for movie in not_seen:
            score = (movie, self.calculate_rec_score(movie, seen, ratings_matrix, user_ratings))
            recommendation_scores.append(score)
        
        # Get top k indices that translate to top recommended movies
        largest_tuples = heapq.nlargest(k, recommendation_scores, key=lambda x: x[1])

        recommendations = [x[0] for x in largest_tuples]
        
    
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
