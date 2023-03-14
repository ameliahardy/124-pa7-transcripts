# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util

import numpy as np
import re
import porter_stemmer
from collections import defaultdict
stemmer = porter_stemmer.PorterStemmer()
# from editdistance import eval as calculate_edit_distance
from nltk.metrics.distance import edit_distance as calculate_edit_distance


YES_INPUTS = {'yes', 'sure', 'absolutely', 'of course', 'certainly', 'definitely', 'yeah', 'y', 'ya', 'ye', 'yep', 'yup'}
NO_INPUTS = {'no', 'not at all', 'absolutely not', 'never', 'no way', 'n', 'nah'}




# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'moviebot'

        self.creative = creative

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        sentiment = util.load_sentiment_dictionary('data/sentiment.txt')

        stemmed_sentiment = {}
        for key in sentiment:
            stemmed_key = stemmer.stem(key)
            stemmed_sentiment[stemmed_key] = sentiment[key]
        self.sentiment = stemmed_sentiment

        self.negations = ['not', 'never', 'no', 'none', 'neither', 'nor', 'hardly', 'scarcely', 'barely', 'doesn\'t', 'isn\'t', 'wasn\'t', 'weren\'t', 'haven\'t', 'hasn\'t', 'hadn\'t', 'cannot', 'can\'t', 'won\'t', 'wouldn\'t', 'shouldn\'t', 'mustn\'t', 'don\'t', 'doesn\'t', 'didn\'t']
        self.enhancers = ['really', 'reeally', 'realli', 'realli']
        self.strong_like = ['love']
        self.strong_dislike = ['hate', 'terrible']

        self.negative_emotions = ['angry', 'frustrated', 'disappointed', 'depressed', 'anxious', 'afraid', 'guilty', 'ashamed', 'insecure', 'jealous', 'lonely', 'rejected', 'helpless', 'hopeless', 'powerless', 'resentful', 'bitter', 'irritated', 'stressed', 'tense', 'sad']
        self.positive_emotions = ['joyful', 'loving', 'grateful', 'hopeful', 'content', 'proud', 'amused', 'excited', 'awed', 'serene', 'inspired', 'optimistic', 'happy', 'pleased', 'enthusiastic', 'compassionate', 'peaceful', 'confident', 'eager', 'delighted']   

        self.user_ratings = np.zeros((ratings.shape[0]))
        self.input_count = 0
        self.recommendations = None
        self.current_recommendation = 0
        self.waiting_on_response = False
        self.waiting_on_typo = False
        self.waiting_on_disambiguate = False
        self.last_preprocessed_line = None

        ########################################################################
        # TODO: Binarize the movie ratings matrix.                             #
        ########################################################################
        ratings = Chatbot.binarize(ratings)
        # Binarize the movie ratings before storing the binarized matrix.
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

        if self.creative:
            greeting_message = "What up, what up! This is MovieBot in the house! I gotchu covered with some lit movie recommendations, but first let me get a feel for your vibe. Can you tell me about a movie you've seen and what you thought of it? That way I can get a sense of your taste in flicks."
        else:
            greeting_message = "Hi! I'm MovieBot! I'm going to recommend a movie to you. First I will ask you about your taste in movies. Tell me about a movie that you have seen."

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
        if self.creative:
            goodbye_message = "Have a nice day!"
        else: 
            goodbye_message = "Ayye, stay cool and have a chillaxin' day, my homie! Peace out! *drops mic*"

        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return goodbye_message

    def process_sentiment(self, line, movie_index):
        '''
        line: preprocess line with correct tile
        return: (0 if unsuccesful 1 if successful, response)
        '''
        sentiment = self.extract_sentiment(line)
        response = ""
        if sentiment == 0:
            return (0, f"I'm not sure if you liked {self.current_title}, can you tell me more about it?")
        elif sentiment == -1:
            response = f"I'm sorry to hear you didn't like {self.current_title}."
        elif sentiment == 1:
            response = f"Great, you liked {self.current_title}."
        
        self.user_ratings[movie_index] = sentiment
        self.input_count += 1
        return (1, response)

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
        def recommend_movie():
            recommendation = f'"{self.titles[self.recommendations[self.current_recommendation]][0]}"'

            RECOMMENDATIONS = [
f"Thats enough for me to make a recommendation. Based on your interests, I believe you will enjoy {recommendation}. Do you want to hear additional suggestions?",
f"I have a feeling that {recommendation} will pique your interest. Shall I offer you some more recommendations?",
f"I am confident that you will find {recommendation} appealing. Would you like me to provide you with more options?",
f"My intuition tells me that {recommendation} will catch your attention. Do you want me to give you further recommendations?",
f"Judging from your preferences, I think {recommendation} would suit your taste. Can I suggest more options for you?",
f"I think {recommendation} would be right up your alley. If you're interested, I can suggest some similar options as well.",
f"Based on what I know about your tastes, I'm pretty sure you'll love {recommendation}. Want me to offer some additional suggestions?",
f"If you're looking for something new and exciting, I highly recommend {recommendation}. And if you're open to it, I can suggest some related ideas too.",
f"In my opinion, {recommendation} is a standout choice. But if you'd like to explore some other options, just let me know.",
f"From my analysis of your interests, I believe {recommendation} would be an excellent choice. But if you'd like some more ideas, I'd be happy to provide them."
]

            RECOMMENDATIONS_SNOOP_DOGG = [
                f"Fo' shizzle, my dizzle, check it! I'm feelin' good about this recommendation, my homie. Based on what you've been tellin' me, I think you gonna straight-up love {recommendation}. You want me to drop some more ideas your way, or you good with that one?",
                f"Aight, listen up! I got a vibe that {recommendation} is gonna be your jam, my dude. But if you're lookin' for more, I can keep the suggestions comin'. What you thinkin', my homie?",
                f"Yo, yo, yo! I'm gettin' some major positive energy from this recommendation, my man. I think {recommendation} is gonna be just what you're lookin' for. But if you're open to more ideas, I can definitely hook you up!",
                f"A'ight, a'ight, I see you, my dude! From what you've been sayin', I think {recommendation} is gonna be your ticket to ride. But if you want me to drop some more knowledge, just say the word!",
                f"Yo, yo, yo, check it! I'm gettin' some major good vibes from this recommendation, my homie. I think {recommendation} is the way to go. But if you want me to keep the party goin' with more ideas, I got you covered!",
                f"Listen up, my dude! From what you've been tellin' me, I'm pretty sure {recommendation} is the one for you. But if you're lookin' for some more flicks to check out, I got plenty of options up my sleeve!",
                f"Aight, aight, my bad, my bad! I must've misunderstood you, my homie. But check it out, I got a feeling that {recommendation} is gonna be your jam. Want me to keep the suggestions comin' or you good with that one?",
                f"Yo, yo, yo! I'm feelin' some major positive energy from this recommendation, my man. I think {recommendation} is gonna be straight fire. But if you're lookin' for more dope flicks to check out, just let me know!",
                f"Ay, fo shizzle! That's enough for me to drop a recommendation on ya. Based on your interests, I'm feelin' like {recommendation} is gonna be right up your alley. You want some more options to choose from? I gotchu covered, my homie."
            ]

            self.waiting_on_response = True
            if not self.creative:
                response = RECOMMENDATIONS[self.current_recommendation % len(RECOMMENDATIONS)]
            else:
                response = RECOMMENDATIONS_SNOOP_DOGG[self.current_recommendation % len(RECOMMENDATIONS_SNOOP_DOGG)]
            self.current_recommendation += 1 # TODO: get more recommendations if needed
            return response
        
        preprocessed_line = self.preprocess(line)

        if self.creative:
            def process_sentiment(index):
                    sentiment = self.extract_sentiment(preprocessed_line)
                    response = ""
                    if sentiment == 0:
                        return f"I ain't quite sure if you feelin' {title} or not, so why don't you let me in on the scoop?"
                    elif sentiment < 0:
                        response = f"Aw, snap, that's a bummer to hear you didn't vibe with {title}, my dude."
                    elif sentiment > 0:
                        response = f"Ayyye, that's what's up, my homie! I'm stoked to hear that you're feelin' {title}!"
                    
                    self.user_ratings[index] = sentiment
                    self.input_count += 1

                    if self.input_count < 5:
                        return f"{response} What other flicks you into?"
                    
                    self.recommendations = self.recommend(self.user_ratings, self.ratings)
                    return f"{response} {recommend_movie()}"
            
            if not self.waiting_on_response and not self.waiting_on_typo and not self.waiting_on_disambiguate:
                titles = self.extract_titles(preprocessed_line)
                if len(titles) == 0:
                    # Check for emotion
                    def check_for_emotion(emotions, line):
                        emotions_found = []
                        for emotion in emotions:
                            if emotion in line:
                                emotions_found.append(emotion)
                        return emotions_found

                    negative_emotions = check_for_emotion(self.negative_emotions, line)
                    if len(negative_emotions) != 0:
                        return f"Aw, fo' shizzle my nizzle, did I make you feel {negative_emotions[0]}? My sincerest apologies, G."
                    positive_emotions = check_for_emotion(self.positive_emotions, line)
                    if len(positive_emotions) != 0:
                        return f"That's what's up, my homie! I'm glad to hear you feeling {positive_emotions[0]} - that's dope!"              

                    return "My bad, fam. I couldn't identify no movie in your response. Make sure to put quotation marks around the movie title, ya dig?"
                elif len(titles) > 1:
                    return  "Yo, slow down for a minute, my homie! Let's take it one flick at a time, so we can make sure we're on the same page."
                
                title = f'"{titles[0]}"'
                movie_indexes = self.find_movies_by_title(title.replace('"', ''))

                if len(movie_indexes) == 0:
                    similar_movies = self.get_names_from_index(self.find_movies_closest_to_title(title.replace('"', '')))
                    if len(similar_movies) == 0:
                        return f"My apologies, my dude. I couldn't find nothin' on {title}. Can you put me on to another flick that you're into?"
                    self.waiting_on_typo = True
                    self.last_preprocessed_line = preprocessed_line
                    print(similar_movies)
                    return f'Aw yeah, my bad, my bad, my homie! It looks like I couldn\'t find what you were lookin\' for with {title}. But don\'t trip, I got your back! Check it, I\'m thinking you meant "{similar_movies[0]}", am I right?'
                
                if len(movie_indexes) > 1:
                    self.waiting_on_disambiguate = True
                    self.last_preprocessed_line = preprocessed_line
                    return f"Which one of these joints did you mean? {self.get_names_from_index(movie_indexes)}"
 
                # Get sentiment
                
                
                return process_sentiment(movie_indexes[0])

            # Starter
            else: 
                if self.waiting_on_typo:
                    if preprocessed_line in NO_INPUTS:
                        self.waiting_on_typo = False
                        return "Ok, try entering the movie again or tell me about anothere movie."
                    titles = self.extract_titles(self.last_preprocessed_line)
                    title = f'"{titles[0]}"'
                    correct_movie_index = self.find_movies_closest_to_title(title.replace('"', ''))[0]
                    title = f'"{self.get_names_from_index([correct_movie_index])[0]}"'

                    if preprocessed_line not in YES_INPUTS:
                        return f"Sorry, I didn't understand that. Is {title} the movie you were thinking about? [yes/no]"
                    # else yes
                    preprocessed_line = self.last_preprocessed_line
                    self.waiting_on_typo = False
                    return process_sentiment(correct_movie_index)

                if self.waiting_on_disambiguate:
                    self.waiting_on_disambiguate = False
                    titles = self.extract_titles(self.last_preprocessed_line)
                    title = f'"{titles[0]}"'
                    movie_indexes = self.find_movies_by_title(title.replace('"', ''))
                    disambiguated_indexes = self.disambiguate(preprocessed_line, movie_indexes)
                    if len(disambiguated_indexes) != 1:
                        return f"Sorry, please try telling me about another movie."
                    correct_movie_index = disambiguated_indexes[0]
                    title = f'"{self.get_names_from_index([correct_movie_index])[0]}"'
                    preprocessed_line = self.last_preprocessed_line
                    return process_sentiment(correct_movie_index)
                
                # asked if they wanted more recommendations
                if preprocessed_line in NO_INPUTS:
                    self.waiting_on_response = False                    
                    return "Ok, enter :quit to quit or tell me about another movie that you've seen."
                elif preprocessed_line in YES_INPUTS:
                    return recommend_movie()
                else:
                    return "Sorry, I didn't understand that. Would you like more recommendations? [yes/no]"

                
        else:
            if not self.waiting_on_response:
                # Get movie titles from input
                titles = self.extract_titles(preprocessed_line)
                if len(titles) == 0: 
                    return "Sorry, I couldn't identify a movie in your response. Make sure the movie title is surrounded by quotation marks."
                elif len(titles) > 1:
                    return  "Sorry, please tell me about one movie at a time."

                title = f'"{titles[0]}"'
                # Find movies by the title
                movie_indexes = self.find_movies_by_title(title.replace('"', ''))
                if len(movie_indexes) == 0:
                    return f"Sorry, I coudn't find the movie {title}, please tell me about another movie that you've watched."
                elif len(movie_indexes) > 1:
                    return f"Sorry, I found more than one movie called {title}. Can you clarify?"
                
                # Get sentiment
                sentiment = self.extract_sentiment(preprocessed_line)
                response = ""
                if sentiment == 0:
                    return f"I'm not sure if you liked {title}, can you tell me more about it?"
                elif sentiment == -1:
                    response = f"I'm sorry to hear you didn't like {title}."
                elif sentiment == 1:
                    response = f"Great, you liked {title}."
                
                self.user_ratings[movie_indexes[0]] = sentiment
                self.input_count += 1

                if self.input_count < 5:
                    return f"{response} Tell me about other movies that you've seen."
                
                self.recommendations = self.recommend(self.user_ratings, self.ratings)
                return f"{response}  {recommend_movie()}"
            else:
                print(f"pre_process: {preprocessed_line}")
                

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
        TITLE = "<title>"

        text_no_title = text
        titles = Chatbot.extract_titles(text)
        for title in titles:
            text_no_title = text_no_title.replace(title, TITLE)

        new_text = ""
        for word in text_no_title.split(" "):
            new_word = stemmer.stem(word) if word != TITLE else TITLE
            new_text = f"{new_text} {new_word}"
        new_text = new_text.lower()

        new_text = new_text.translate(str.maketrans("", "", ",.!?")).strip()

        for title in titles:
            new_text = new_text.replace(TITLE, title, 1)

        text = new_text
        ########################################################################
        #                             END OF YOUR CODE                         #
        ########################################################################

        return text

    @staticmethod
    def extract_titles(preprocessed_input):
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
        # print(preprocessed_input)
        titles = re.findall(r'"(.+?)"', preprocessed_input)
        # print(titles)

        return titles


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
            years = re.findall(r'\([0-9]{4}\)', title)
            year_braced = None if len(years) == 0 else years[-1]
            year = year_braced.replace("(", "").replace(")", "") if year_braced else None

            title_to_find = title
            if year_braced:
                title_to_find = title.replace(year_braced, "").strip()
            
            indexes = []
            def get_indexes(): 
                for i, movie in enumerate(self.titles):
                    curr_movie = movie[0].lower()
                    if curr_movie.startswith(f"{title_to_find}") or curr_movie == title_to_find:
                        if year and year in movie[0] or not year:
                            indexes.append(i)
            get_indexes()

            if len(indexes) == 0: 
                start = re.findall(r'^(the |an |a )', title)
                if len(start):
                    title_to_find = f"{title_to_find.replace(start[0], '', 1)}, {start[0].strip()}"
                    get_indexes()


            return indexes
        else:
            title = title.lower()
            years = re.findall(r'\([0-9]{4}\)', title)
            year_braced = None if len(years) == 0 else years[-1]
            year = year_braced.replace("(", "").replace(")", "") if year_braced else None

            title_to_find = title
            if year_braced:
                title_to_find = title.replace(year_braced, "").strip()
            
            indexes = []
            def get_indexes(): 
                for i, movie in enumerate(self.titles):
                    curr_movie = movie[0].lower()
                    if curr_movie.startswith(f"{title_to_find} (") or curr_movie == title_to_find:
                        if year and year in movie[0] or not year:
                            indexes.append(i)
            get_indexes()

            if len(indexes) == 0: 
                start = re.findall(r'^(the |an |a )', title)
                if len(start):
                    title_to_find = f"{title_to_find.replace(start[0], '', 1)}, {start[0].strip()}"
                    get_indexes()


            return indexes

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
        if self.creative:
            input_no_title = preprocessed_input
            for title in Chatbot.extract_titles(preprocessed_input):
                input_no_title = input_no_title.replace(title, "")

            sentiment = 0
            negate = False
            enhance = False
            strong_like = False
            strong_dislike = False
            for word in input_no_title.split(" "):
                if word in self.negations:
                    negate = True
                    continue
                if word in self.enhancers:
                    enhance = True
                    continue
                if word in self.strong_like:
                    strong_like = True
                if word in self.strong_dislike:
                    strong_dislike = True
                if word not in self.sentiment:
                    continue
                curr_sentiment = 1 if self.sentiment[word] == "pos" else -1
                if negate:
                    curr_sentiment *= -1
                    negate = False
                sentiment += curr_sentiment

            if strong_like:
                sentiment = 2
            elif strong_dislike:
                sentiment = -2
            elif enhance:
                sentiment *= 2
            return sentiment
        else:
            input_no_title = preprocessed_input
            for title in Chatbot.extract_titles(preprocessed_input):
                input_no_title = input_no_title.replace(title, "")

            sentiment = 0
            negate = False
            for word in input_no_title.split(" "):
                if word in self.negations:
                    negate = True
                    continue
                if word not in self.sentiment:
                    continue

                curr_sentiment = 1 if self.sentiment[word] == "pos" else -1
                if negate:
                    curr_sentiment *= -1
                    negate = False

                sentiment += curr_sentiment

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
        

        def prep_title(to_prep):
            open_parentheses = to_prep.find('(')
            close_parentheses = to_prep.find(')')
            if open_parentheses != -1 and close_parentheses != -1:
                to_prep = to_prep[:open_parentheses]
        
            to_prep = to_prep.strip()
            to_prep = to_prep.lower()
            return to_prep

        title = prep_title(title)
        indexes = []
        def get_indexes(): 
            best_distance = max_distance
            for i, movie in enumerate(self.titles):
                curr_movie = prep_title(movie[0])
                distance = calculate_edit_distance(curr_movie, title_to_find)
                # if i == 524 or i == 5743:
                #     print(f"title: {title_to_find} curr_movie: {curr_movie}, distance: {distance}")
                # return
                if distance <= max_distance and distance <= best_distance: 
                    if distance < best_distance:
                        best_distance = distance
                        indexes.clear()
                        indexes.append(i)
                    else:
                        indexes.append(i)


        title_to_find = title
        get_indexes()

        return indexes

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



        titles = [(self.titles[candidate][0], candidate) for candidate in candidates]
        potential_movies = []
        for (title, index) in titles:
            year = re.findall(r'\([0-9]{4}\)', title)[0].replace("(", "").replace(")", "")
            title = title.replace(year, "")
            if clarification == year or clarification in title:
                potential_movies.append(index)

        return potential_movies

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
        binarized_ratings = ratings.copy()
        binarized_ratings[ratings > threshold] = 1
        binarized_ratings[ratings <= threshold] = -1
        binarized_ratings[ratings == 0] = 0

        

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
        u = np.array(u)
        v = np.array(v)
        if np.all(u == 0) or np.all(v == 0) or np.isnan(u).any() or np.isnan(v).any() or np.isinf(u).any() or np.isinf(v).any():
            similarity = np.nan
        else:
            similarity = (u.dot(v)) / (np.linalg.norm(u) * np.linalg.norm(v)) 

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
        # print(ratings_matrix)
        ratings = np.zeros(user_ratings.shape)
        # print(f"user ratings: {user_ratings}, shape: {ratings.shape}")
        for i in range(len(user_ratings)):
            if user_ratings[i] != 0: 
                continue
            cosines = np.zeros(user_ratings.shape)
            for j in range(len(user_ratings)):
                if user_ratings[j] == 0:
                    continue
                # print(f"A: {ratings_matrix[i]}")
                # print(f"B: {ratings_matrix[j]}")

                cosines[j] = self.similarity(ratings_matrix[i], ratings_matrix[j])
            # print(f"{i}: {cosines}")
            # print(f"ratings[{i}]: {user_ratings.dot(cosines)}")
            ratings[i] = user_ratings.dot(cosines)

        ratings[ratings == 0] = np.NINF
        sorted_ratings = np.argsort(-ratings)
        # print(sorted_ratings)
        recommendations = list(sorted_ratings[0:k])

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
        if self.creative:
            return """
            Yo, what's good homie? Welcome to MovieBot! 
            This dope bot is gonna hook you up with some tight movie recommendations based on your likes and dislikes. 
            So why don't you lay down your thoughts on some flicks and let this bot work its magic. Fo shizzle!
            """
        else:
            return """
            Hello! Welcome to MovieBot! 
            MovieBot will give you movie recommendations based on what movies you liked or disliked. 
            Go ahead and let it know your opinions on some movies.
            """
    
    def get_names_from_index(self, index):
        names = []
        for i in index:
            names.append(self.titles[i][0])
        return names


disambiguate_test_cases = [(("2", [1142, 1357, 2629, 546]), [1357]), 
                           (("1997", [1359, 2716]), [1359]),
                           (("Sorcerer's Stone", [3812, 4325, 5399, 6294, 6735, 7274, 7670, 7842]), [3812])]

by_title_test_cases = [("Scream", [1142, 1357, 2629, 546]),
                       ("Percy Jackson", [7463, 8377])]

fine_sentiment = [('I loved "Zootopia"', 2), 
                  ('"Zootopia" was terrible.', -2), 
                  ('I really reeally liked "Zootopia"!!!', 2)]

edit_distance_test = [(("Sleeping Beaty", 3), [1656]), 
                      (("Te", 3), [8082, 4511, 1664]),
                      (("BAT-MAAAN", 3), [524, 5743]), 
                      (("Blargdeblargh", 4), [])]

if __name__ == '__main__':
    chatty = Chatbot()
    tests = edit_distance_test
    func = chatty.find_movies_closest_to_title
    chatty.creative = True

    for test_case in tests:
        (input, expected) = test_case
        result = func(input[0], max_distance=input[1])
        print(f"{'PASS' if result == expected else 'FAIL'}: Input: {input} Output: {result} Expected: {expected}")
