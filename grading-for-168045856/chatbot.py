# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util

import numpy as np
import re
from porter_stemmer import PorterStemmer
from random import randint

# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'Lebron James'
        self.creative = creative

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')
       
        ########################################################################
        # TODO: Binarize the movie ratings matrix.                             #
        ########################################################################

        # Binarize the movie ratings before storing the binarized matrix.
        p = PorterStemmer()
        self.ratings = ratings
        self.ratings = self.binarize(self.ratings)
        self.movie_thoughts = np.zeros(self.ratings.shape[0])
        self.movie_count = 0
        self.keep_making_recs = False
        self.movie_recommendations = []
        self.given_recs = 0
        self.yes_responses = ["yes", "yeah", "yep", "Yes", "yes!"]
        self.no_responses = ["no", "No", "nope", "nah"]
        self.strong_pos = ["love", "loved", "adore", "amazing", "exciting", "fantastic", "superb", "favourite", "delightful", "best", "brilliant"]
        self.strong_negative = ["hated", "hate", "despised", "terrible", "disgusting", "vile", "worst"]
        self.emphasize = ["really", "thoroughly","really reaally", "extremely", "strongly", "super"]
        self.random_conversation = ["weather", "sports", "news", "current_affairs", "fashion", "music"]
        self.random_responses = ["Hmmmm, I don't really want to talk about that right now. Let's talk about movies!", "Ok, got it. But do you mind talking about movies instead?", "That's nice", "Hmmm... I'd rather talk about movies"]

        self.detected_emotion = 0
        self.emotions_felt = [0,0,0,0,0]
        self.angry_emotions = ["angry", "frustrated", "annoyed", "irritated", "vexed"]
        self.happy_emotions = ["happy", "delighted", "ecstatic"]
        self.confused_emotions = ["unsure", "puzzled", "confused"]
        self.sad_emotions = ["sad", "depressed", "upset", "miserable"]
        self.scared_emotions = ["terrified", "scared", "alarmed", "horrified"]
        self.angry_responses = ["Oh no! Don't be angry! Everything is okay! Just play some basketball!", "Let's all calm down and do the harlem shake", "Take a chill pill bro. Go shoot some hoops boy"]
        self.happy_responses = ["YESSS! That's what I felt when I won my chip with the Cavs", "LETS GOOOOOOOOO.", "Amazing! Almost as amazing as me coming back from a 3-1 deficit agaisnt the Warriors"]
        self.confused_responses = ["Dont worry, you will figure it out, just like I figured out how to beat the Warriros", "Take your time with it. greatness doesn't happen overnight", "Its okay to be confused. I was confused when I did not know which team to go to in 2014"]
        self.scared_responses = ["It will be okay, trust me. I will fight for you.", "Go to your happy place, mine's the basketball court", "Take a deep breath. I might be a 6'7 giant but I get scared sometimes too"]
        self.sad_responses = ["I am sorry to hear that. Even when you make 100 million dollars a year like me, you can still be sad", "Hope you feel better soon. I just get in my cyrochamber", "Let's cheer you up by chatting about some movies"]
        self.sad_emotions_stemmed = []
        self.scared_emotions_stemmed  = []
        self.angry_emotions_stemmed = []
        self.happy_emotions_stemmed = []
        self.confused_emotions_stemmed = []

        self.responses_pos = ["I have seen {} too!!! I saw it when I was on the Heat. Tell me another one", " Oh I've heard of {}! Give me another one maybe?", "{} was my favorite movie when I was playing for the Cavs. Tell me another!", "The director of {} was my buddy actually. Give me another one", "Bronny liked {}. Hmmmm, what else you got?", "I showed {} to my guy Dwayne Wade. Any other movie you wanna talk about?", "Oh, you liked {}? TACO TUESDAY! Can you tell me what you thought of another movie?" ]
        self.responses_neg = ["Yea {} was whack! King James does not approve. Give another one.", "Man {} was straight trash, that was D. Wades least favorite movie of all time! Give me another movie.", "{} was horrible. Almost as bad as when J.R. Smith cost us Game 1 in the playoffs. Send another movie my way, champ.", "Sheesh, Bronny hated {} too! What other movies have you watched?","That is crazy, I was almost in {} but I turned it down for Space Jam 2. Looks like it was a good decision! Any other movies?", "Dang, {} is almost as bad as the Cavs without me. Send me another movie.", "Aye man, {} was garbage. I watched that one with Savannah and she hated it, man. What other movies have you watched?", "Noted - you did not like {}. Just like I didnt like Draymond at the time. Tell me your thoughts on another movie."]
        self.responses_net = ["Not sure what youre talking about man. Tell me more about {}. Give it to me straight, like my coach.", "Communication is key on the court...and lets just say I dont know what you are talking about. Lets be a little more specific about {}.", "Let us make sure we are on the same page, I dont want either of us ending up like J.R. Smith. Can you be a little bit more clear about {}?", "I'm sorry, I'm not sure if you liked {}. Tell me more about it."]
        for word in self.angry_emotions:
            self.angry_emotions_stemmed.append(p.stem(word))
        for word in self.happy_emotions:
            self.happy_emotions_stemmed.append(p.stem(word))    
        for word in self.confused_emotions:
            self.confused_emotions_stemmed.append(p.stem(word))
        for word in self.sad_emotions:
            self.sad_emotions_stemmed.append(p.stem(word))
        for word in self.scared_emotions:
            self.scared_emotions_stemmed.append(p.stem(word))

        self.stemmed_strong_pos = []
        self.stemmed_strong_negative = []
        self.stemmed_emphasize = []
       
        for word in self.strong_pos:
            self.stemmed_strong_pos.append(p.stem(word))
        for word in self.strong_negative:
            self.stemmed_strong_negative.append(p.stem(word))
        for word in self.emphasize:
            self.stemmed_emphasize.append(p.stem(word))    
       
       

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

        greeting_message = "Hello! I'm Lebron James! When I'm not playing basketball, I love to talk about movies! Tell me your thoughts on a movie of your choice and I can hook you up with some recommendations?"

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

        goodbye_message = "GET TO THE GYM! ITS ALL ABOUT THAT MENTALITY. Have a good one. I'll see you out there."

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
        input_line = self.preprocess(line)
        rando = randint(0,6)
        self.detected_emotion = 0
        #if self.creative:
            #response = "I processed {} in creative mode!!".format(line)
        #else:
            #response = "I processed {} in starter mode!!".format(line)
        if (self.keep_making_recs):
            if input_line in self.yes_responses:
                if (len(self.movie_recommendations) == self.given_recs):
                    return "That's all the recommendations I have for you based on what you told me! I havent seen thaaat many movies cuz I focus on playing ball more!"
                next_movie_rec = self.titles[self.movie_recommendations[self.given_recs]][0]
                rec_responses = ["How about "+ next_movie_rec +". Do you want another one?", " Maybe you will like "+ next_movie_rec +". Its good vibes before a game. AND ONE more (get it?)?", "You have got to see "+ next_movie_rec +". Savannah wont stop talking about it. Want me to keep going?", "I would definitely recommend "+ next_movie_rec +". Want me to tell you about some other movie as well?", "OHHHHHHH you should see "+ next_movie_rec +". Call me DJ Khaled cuz how about another one?"]
                response =  rec_responses[randint(0,len(rec_responses) - 1)]
                self.given_recs += 1
                return response
            elif input_line not in self.no_responses:
                return "I don't think that is a valid response. Please try and stick to yes/no."
            else: # 'no' case
                return "Good stuff champ. Thank you for chatting with me. Let me know if you want to talk about anything else. King James out."
       
        if self.movie_count < 5:
            movie = self.extract_titles(line)
            # Check if there's zero movies
            if len(movie) == 0:
                if self.creative:
                    self.detect_emotion(input_line)
                    return self.arbitrary_input_responses(input_line)
                unknown_responses = ["I couldnt figure out a movie from that. Wanna tell me about a movie you have seen?", "I didn't seem to recognize a movie from what you said. Could you tell me about a movie you liked?", "Hmmmm, not sure whether there was a movie in there. Wanna try again?" ]
                response = unknown_responses[randint(0, len(unknown_responses) - 1)]
                return response
            # Check if there's one movie
            elif len(movie) == 1:
                if "" in movie:
                    return "I would need an input to be able to help you"    
                mv = "'" + movie[0] + "'"
                movie_i = self.find_movies_by_title(movie[0])
                # Check if movie is in database
                if len(movie_i) == 0:
                    response = "I've never heard of {}, sorry...I play basketball for a living man, not watch movies. Tell me about another movie you liked?".format(mv)
                    return response
                if len(movie_i) > 1:
                    response = "I found more than one movie called {}. Can you clarify?".format(mv)
                    return response
                # Checks for 1 movie index
                if len(movie_i) == 1:
                    # Check based on sentiment
                    line_sentiment = self.extract_sentiment(line)
                    if line_sentiment == 1: # good sentiment
                        #print("in sentiment = 1")
                        response = self.responses_pos[rando].format(mv)
                        self.movie_thoughts[movie_i[0]] = 1 
                        self.movie_count += 1
                        if self.movie_count != 5:
                            return response
                    if line_sentiment == 0: # no sentiment
                        response = self.responses_net[randint(0,3)].format(mv)
                        return response
                    if line_sentiment == -1: # bad sentiment
                        response = self.responses_neg[randint(0,7)].format(mv)
                        self.movie_thoughts[movie_i[0]] = -1 
                        self.movie_count += 1
                        if self.movie_count != 5:
                            return response
            # Check if there's multiple movies
            elif len(movie) > 1:
                if self.creative:
                    lst = self.extract_sentiment_for_movies(input_line)
                    movie1 = lst[0][0]
                    movie2 = lst[1][0]
                    if lst[0][1] == 1 and lst[1][1] == 1:
                        response = "Oh you liked {} and {}. Those are my favorite movies too man. Noted. Can you tell your thoughts on another movie?".format(movie1,movie2)
                        self.movie_thoughts[self.find_movies_by_title(lst[0][0])] = 1
                        self.movie_thoughts[self.find_movies_by_title(lst[1][0])] = 1
                        self.movie_count += 2
                        if self.movie_count < 5:
                            return response
                    elif lst[0][1] == -1 and lst[1][1] == -1:
                        response = "Oh I see. You did not like {} and {}. Noted. Mind telling me more about some movies you have seen?".format(movie1,movie2)
                        self.movie_thoughts[self.find_movies_by_title(lst[0][0])] = -1
                        self.movie_thoughts[self.find_movies_by_title(lst[1][0])] = -1
                        self.movie_count += 2
                        if self.movie_count < 5:
                            return response
                    else:
                        response = " Oh I am actually not sure about how you felt about those movies. Can you be more specific?"
                        return response
                response = "It seems you're talking about more than one movie. Cmon man its always like what coach says: Take it one play at a time. So please try to give me one movie at a time."
                return response
               
        self.movie_recommendations = self.recommend(self.movie_thoughts, self.ratings)
        top_recommendation = "'" + self.titles[self.movie_recommendations[0]][0] + "'"
        response = "Given what you said, my super analytical high basketball IQ bain has come with a few recommendations for you. I think you would like {}. Would you like more recommednations? (please answer yes/no)".format(top_recommendation)
        self.given_recs += 1
        self.keep_making_recs = True
        return response
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
        res = []
        frst_i = 0
        while True:
            frst_i = preprocessed_input.find('"', frst_i)
            if frst_i != -1:
                sec_i = preprocessed_input.find('"', frst_i + 1)
                if sec_i == -1:
                    break
                movie_title = preprocessed_input[frst_i + 1:sec_i]
                res.append(movie_title)
                frst_i = sec_i + 1
            else:
                break

       
        return res

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
        lowtitle = title.lower()
        is_alternate = False
        lowtitle = lowtitle.replace("(", "").replace(")", "")
        title_l = lowtitle.split()

        year = ""
        articles = ["the", "an", "a", "un", "el", "la", "le"]
        # Handle Year
        if title_l[-1].isdigit():
            year = " (" + title_l[-1] + ")"
            title_l.pop(-1)

        # Handle article formatting
        for a in articles:
            if a == title_l[0]:
                title_l.pop(0)
                title_l[-1] = title_l[-1] + ", " + a

        res = []
        ##print(self.titles[67])
        #print(title_l)
        title_year = " ".join(title_l) + year
        for i in range(len(self.titles)):
            # Add year to formatted string
            if "(" in title_year:
                name_year = self.titles[i][0].lower()
                if title_year == name_year:
                    res.append(i)
            else:
                name_year = (self.titles[i][0]).split(" (")
                #if len(name_year) > 2:
                movie_names = name_year[:-1]
                # if len(year) > 0:
                movie_names = [x.lower() for x in movie_names]
                for y in range(len(movie_names)):
                    if movie_names[y][len(movie_names[y])-1] == ")":
                        movie_names[y] = movie_names[y][:-1]
                    if "a.k.a" in movie_names[y]:
                        movie_names[y] = movie_names[y][7:]

                for j in range(len(movie_names)):
                    if title_year == movie_names[j]:
                        res.append(i)
                # else:
                    # movie_names = name_year[:-1]
                    # for i in range(len(movie_names)):
                    #     if title_year in movie_names[i]:
                    #         res.append(i)
        return res
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
        # self.creative = True
        p = PorterStemmer()
        negations = ["don't", "dont", "not", "never", "didn't", "didnt"]
        negations_stemmed = []
        for word in negations:
            negations_stemmed.append(p.stem(word))
        count_pos = 0
        count_neg = 0
        stemmed_sentiment = {}
        titles = self.extract_titles(preprocessed_input)
        for i in range(len(titles)):
            preprocessed_input = preprocessed_input.replace(titles[i], "")
        for word in self.sentiment:
            stemmed_key = p.stem(word)
            stemmed_sentiment[stemmed_key] = self.sentiment[word]
        words  = preprocessed_input.lower().split()
        neg_present = 1

        ###### creative
        strong_pos_present = 0
        strong_neg_present = 0
        emphasizer_present = 0
        prev_emphasize = 0
        for word in words:
            check_word = p.stem(word)
            if (check_word in self.stemmed_strong_pos):
                count_pos += 2
                strong_pos_present += 1
            elif (check_word in self.stemmed_strong_negative):
                count_neg += 2
                strong_neg_present += 1
            elif check_word in negations_stemmed:
                neg_present = -1
            elif check_word in stemmed_sentiment:
                if stemmed_sentiment[check_word] == 'pos':
                    if prev_emphasize == 1:
                        count_pos += 2
                    else:
                        count_pos += 1
                else:
                    if prev_emphasize == 1:
                        count_neg += 2
                    else:
                        count_neg += 1
            if check_word in self.stemmed_emphasize:
                emphasizer_present = 1
                prev_emphasize = 1
            else:
                prev_emphasize = 0
        if (self.creative == True) and ((strong_pos_present > 0) or (strong_neg_present > 0) or (emphasizer_present == 1)):
            # print("in correct if")
            if count_pos > count_neg + 1:
                if neg_present == -1:
                    return 0
                return 2
            elif count_neg > count_pos + 1:
                if neg_present == -1:
                    return 0
                return -2
            elif count_pos == count_neg:
                return 0
            elif count_pos > count_neg:
                return 1
            else:
                return -1
        else:
            if count_pos > count_neg:
                return 1 * neg_present
            elif count_pos < count_neg:
                return -1 * neg_present
            else:
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
        separated = None
        titls = self.extract_titles(preprocessed_input)
        res = []
        for conj in ["and", "but", "or"]:
            if conj in preprocessed_input:
                separated = preprocessed_input.split(conj)
       
        for i in range(len(separated)):
            sent = self.extract_sentiment(separated[i])
            if "not" in separated[i]:
                sent = -1 * res[i-1][1]
            if sent != 0:
                tup = (titls[i], sent)
                res.append(tup)
            if sent == 0:
                tup = (titls[i], res[i-1][1])
                res.append(tup)
       
        return res

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
        """
        Given a movie title and a maximum edit distance, return a list of movie ids
        for movies whose titles are within that edit distance of the given title.
        """
        viable = {}
        final = []
        for i in range(len(self.titles)):
            movie_split = self.titles[i][0].split(" (")
            dist = self.edit_distance(movie_split[0].lower(), title.lower())
            if dist <= max_distance:
                viable[i] = dist
       
        if len(viable.values()) >= 1:
            min_val = min(viable.values())
            for key, dist in viable.items():
                if dist == min_val:
                    final.append(key)
           
        return final

    def edit_distance(self, word1, word2):

        dist = []
        for i in range(len(word1) + 1) :
            dist.append(i)
       
        for j in range(1, len(word2) + 1):

            diag = dist[0]
            dist[0] = j
           
            for i in range(1, len(word1) + 1):
                prev_dist = dist[i]
               
                if word1[i - 1] != word2[j - 1]:
                    diag += 2
                else:
                    diag += 0
                dist_i1 = dist[i - 1] + 1
                dist_i = dist[i] + 1
                min_val = min(dist_i1, dist_i, diag)
                dist[i] = min_val

                temp = diag
                diag = prev_dist
                prev_dist = temp

        return dist[len(dist)-1]
       

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
        out_list = []
        for can in candidates:
            regex_string = r'\b' + clarification + r'\b'
            if re.search(regex_string, self.titles[can][0]):

            #if clarification in movie_split[0]:
                out_list.append(can)
        return out_list

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
        for i in range(binarized_ratings.shape[0]):
            for j in range(len(binarized_ratings[i])):
                if ratings[i][j] == 0:
                    continue
                elif ratings[i][j] > threshold:
                    binarized_ratings[i][j] = 1
                else:
                    binarized_ratings[i][j] = -1
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
        dot_product = np.dot(u, v)
        norm_u = np.linalg.norm(u)
        norm_v = np.linalg.norm(v)
        similarity = dot_product / (norm_u * norm_v)
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
        recommendations = []
        seen = []
        for j in range(user_ratings.shape[0]):
            if user_ratings[j] != 0:
                seen.append(j)

        rx = [ ]
        for i in range(ratings_matrix.shape[0]):
            rx_i = 0
            for j in range(len(seen)):
                idx = seen[j]
                if np.linalg.norm(ratings_matrix[i]) != 0 and np.linalg.norm(ratings_matrix[idx]) != 0:
                    cossim = self.similarity(ratings_matrix[i], ratings_matrix[idx])
                    val = cossim * user_ratings[idx]
                    rx_i += val
                else:
                    rx_i += 0
            rx.append(rx_i)
       
        # "Remove" Movies We've Seen
        for i in range(len(rx)):
            if i in seen:
                rx[i] = -1 # lowest possible val for cosine similarity, hacky solution

        recommendations = lambda rx, k: sorted(range(len(rx)), key=lambda i: rx[i], reverse=True)[:k]
               
        ########################################################################
        #                        END OF YOUR CODE                              #
        ########################################################################
        return recommendations(rx, k)

    def arbitrary_input_responses(self, input):
        #processedq = asked_question.split(' ')
        random_response_conversation = randint(0, 3)
        random_emo_res = randint(0,2)
        lower_q = input.lower()#.split(' ')

        if ('?' == lower_q[-1]): # if question
            if lower_q[:3] == 'who':
                return "Sorry, I am not sure who that may be."
            if lower_q[:3] == 'can':
                return "Hmmmm... I don't think I will be able to help you with that. But I can definitely help you with some movie recommendations, if you tell me the kind of movies you like!"
            if lower_q[:3] == 'how':
                return " I am sorry, but I do not know how to answer that question."
            if lower_q[:3] == 'who':
                return "That is a good question, but I think you would be better off asking that from someone else."
            if lower_q[:5] == "where":
                return "Have you tried Google Maps?"
        elif (self.detected_emotion): # if emotional comment
            if self.emotions_felt[0] == 1:
                self.emotions_felt[0] = 0
                return self.angry_responses[random_emo_res]
            if self.emotions_felt[1] == 1:
                self.emotions_felt[1] = 0
                return self.happy_responses[random_emo_res]
            if self.emotions_felt[2] == 1:
                self.emotions_felt[2] = 0
                return self.confused_responses[random_emo_res]
            if self.emotions_felt[3] == 1:
                self.emotions_felt[3] = 0
                return self.sad_responses[random_emo_res]
            if self.emotions_felt[4] == 1:
                self.emotions_felt[4] = 0
                return self.scared_responses[random_emo_res]
        else: # random conversation topic i.e. sports/fashion or just completely random
            lower_list = lower_q.split(' ')
            for word in lower_list:
                if word in self.random_conversation:
                    return self.random_responses[random_response_conversation]
            return "Let's chat about movies!"

    def detect_emotion(self, input):
        #p = PorterStemmer()
        processed = input.lower().split(' ')
        for word in processed:
            #stemmed_word = p.stem(word)
            if word in self.angry_emotions:
                self.emotions_felt[0] += 1
                self.detected_emotion = 1
            if word in self.happy_emotions:
                self.emotions_felt[1] += 1
                self.detected_emotion = 1
            if word in self.confused_emotions:
                self.emotions_felt[2] += 1
                self.detected_emotion = 1
            if word in self.sad_emotions:
                self.emotions_felt[3] += 1
                self.detected_emotion = 1
            if word in self.scared_emotions:
                self.emotions_felt[4] += 1
                self.detected_emotion = 1
       
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