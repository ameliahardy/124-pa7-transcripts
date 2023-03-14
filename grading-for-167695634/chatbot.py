# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util
import re
import porter_stemmer
import string
import random 
import numpy as np


# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.creative = creative

        self.name = 'botto'
        if self.creative:
            self.name = 'micco jax'

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')

        # porter stem all keys
        p = porter_stemmer.PorterStemmer()
        self.sentiment =  {p.stem(k, 0, len(k) - 1): v for k, v in self.sentiment.items()}

        # array of tuples (movie id, predicted sentiment) for movies described by user
        self.gathered_ratings = [0 for i in range(len(ratings))]

        self.confirm_movie_name = None
        self.disambiguate_option = None
        self.arbitrary_response_count = 0
        self.question_response_count = 0

        # index of what the next recommendation should be from the recommendations list
        self.next_recommendation = 0
        self.recommendations = []
        ########################################################################
        # TODO: Binarize the movie ratings matrix.                             #
        ########################################################################

        # Binarize the movie ratings before storing the binarized matrix.
        self.ratings = self.binarize(ratings)
        ########################################################################
        #                             END OF YOUR CODE                         #
        ########################################################################

    # function to retrieve bot responses dependent on creative tag
    def get_response(self, response_type, movie_title=''):
        if response_type == 'greeting':
            if self.creative: return "I'm micco jax, Michael Jackson's long lost cousin! He HEE"
            return "Hi, I'm botto. I'm designed to generate movie suggestions for you. Can you start by telling me about a movie you liked or disliked?"
        elif response_type == 'goodbye':
            if self.creative: return "It's time for me to go. Heal the world and make it a better place... He HEE"
            return "Keep in touch and have a great day!"
        elif response_type == 'no_recommendations':
            if self.creative: return "I got no more movie recommendations, but have you tried music? ;)"
            return "Looks like I'm out of recommendations, sorry about that!"
        elif response_type == 'give_recommendation':
            if self.creative: return "My recommendation is for you to watch " + movie_title + ' next, He HEE. Do you want me to recommend more?'
            return 'Try watching ' + movie_title + ' next! Would you like another recommendation?'
        elif response_type == 'stop_recommending':
            if self.creative: return "This is awkward now. Do you want another recommendation now?"
            return "Okay, I won't give you one just yet. Are you ready for another recommendation now?"
        elif response_type == 'sentiment_neg':
            if self.creative: return "Don't like " + movie_title + "? Just beat it (beat it)!"
            return "Sorry to hear you disliked " + movie_title + "."
        elif response_type == 'sentiment_pos':
            if self.creative: return "Ah, so you liked " + movie_title + ". Noted."
            return "Great, you liked " + movie_title + "."
        elif response_type == 'sentiment_unclear':
            if self.creative: return "I'm not a mind-reader, honey. I'm gonna need some more information."
            return "I'm sorry. I'm not sure if you liked " + movie_title + ', can you tell me more about it?'
        elif response_type == 'too_many_movies':
            if self.creative: "Slow down there, tiger. Try giving me one at a time."
            return "Woah, that's a lot of movies! Let's try one at a time."
        elif response_type == 'no_movies_found':
            if self.creative: "You know I love a good puzzle, but this one's too hard. I'm gonna need you to try that again."
            return "Hm. Are you sure you sure you inputted a movie title? Let's try this again, but remember to put the movie title in quotation marks."


    ############################################################################
    # 1. WARM UP REPL                                                          #
    ############################################################################

    def greeting(self):
        """Return a message that the chatbot uses to greet the user."""
        ########################################################################
        # TODO: Write a short greeting message                                 #
        ########################################################################

        return self.get_response('greeting')

        ########################################################################
        #                             END OF YOUR CODE                         #
        ########################################################################

    def goodbye(self):
        """
        Return a message that the chatbot uses to bid farewell to the user.
        """
        ########################################################################
        # TODO: Write a short farewell message                                 #
        ########################################################################

        return self.get_response('goodbye')

        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################

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
        
        # if self.creative:
        #     response = "I processed {} in creative mode!!".format(line)

        yes_variations = ['yes', 'yeah', 'sure']
        
        # if we've already started offering suggestions, check if they've requested more
        if self.next_recommendation > 0:
            if (self.next_recommendation >= len(self.recommendations)):
                return self.get_response('no_recommendations')
            elif (any(yes_variation in line.lower() for yes_variation in yes_variations)):
                recommendation_title = '\"' + self.titles[self.recommendations[self.next_recommendation]][0] + '\"'
                self.next_recommendation += 1
                return self.get_response('give_recommendation', recommendation_title)
            else:
                return self.get_response('stop_recommending')

        if self.disambiguate_option:
            correct_movie_name = '\"' + self.article_before_title(self.titles[self.disambiguate(line, self.disambiguate_option[0])[0]][0]) + '\"'
            sentiment = self.disambiguate_option[1]
            if sentiment == -1:
                self.disambiguate_option = None
                return self.get_response('sentiment_neg', correct_movie_name)
            elif sentiment == 1:
                self.disambiguate_option = None
                return self.get_response('sentiment_pos', correct_movie_name)
            else:
                return self.get_response('sentiment_unclear', correct_movie_name)

        if line.lower() == "yes":
            if self.confirm_movie_name:
                movie_name = '\"' + self.confirm_movie_name[0] + '\"'
                if self.confirm_movie_name[1] == -1:
                    self.confirm_movie_name = None
                    return self.get_response('sentiment_neg', movie_name)
                elif self.confirm_movie_name[1] == 1:
                    self.confirm_movie_name = None
                    return self.get_response('sentiment_pos', movie_name)
                else:
                    return self.get_response('sentiment_unclear', movie_name)
        if line.lower() == "no":
            if self.confirm_movie_name:
                self.confirm_movie_name = None
                return "Could you clarify what movie you are talking about?"
                

        express_sentiment= ["i feel", "i am", 'i\'m']
        angry_words = ['angry','mad','disgusted','annoyed','irritated','vexed','angered','furious','rage']
        happy_words = ['happy','excited','delighted','thrilled','smiling','joy','merry','content','pleased','satisfied']
        sad_words = ['sad','upset','crying','dismal','somber','unhappy','discontent','displeased','dissatisfied']
        express_emotion_love = ['i love','i like','i really love','i really like']
        express_emotion_hate = ['i dislike','i hate','i really dislike','i really hate']
        how_are_you = ['how are you','sup','what\'s up','what are you doing']
        question_starters = ['what ','what ','how ', 'do ','does ','can ','what\'s ','what\'re ','how\'re ','how\'s ','where','when\'re ','when\'s ','when ','why']
        greeting = ['hey','hi','hello','howdy']
        arbitrary_input = ['Okay, Got it','Let us chat about movies now', 'Can we talk about movies','Alright, I hear you!','Okay,now tell me about movies','Yes, I understand',"Subject change please!","I prefer we talk about something else...movies","Hm, okay, now talk to me about movies","Ah makes sense"]
        question_finishers = ['hmm....i don\'t know','Let\'s see...','Not quite sure...']
        titles = self.extract_titles(line)

        if (len(titles) > 1):
            return self.get_response('too_many_movies')
        elif (len(titles) == 0):
            if self.creative:
                if (any(sentiment_starter in line.lower() for sentiment_starter in express_sentiment)):
                    if (any(angry_word in line.lower() for angry_word in angry_words)):
                        return("Did I make you angry? I'm sorry you feel that way.")
                    elif (any(sad_word in line.lower() for sad_word in sad_words)):
                        return("Are you upset? Do you need a tissue?")
                    elif (any(happy_word in line.lower() for happy_word in happy_words)):
                        if (any(str("not "+ happy_word) in line.lower() for happy_word in happy_words)):
                            return("Are you not happy? What can I do?")
                        else:
                            return("I am happy that you are happy!!")
                    else: 
                        i = self.arbitrary_response_count % 10
                        return_str = arbitrary_input[i]
                        self.arbitrary_response_count += 1
                        return(return_str)
                elif (any(emotion in line.lower() for emotion in express_emotion_love)):
                    return("I\'m flattered, I like you!")
                elif (any(emotion in line.lower() for emotion in express_emotion_love)):
                    return('Oh okay, I will work on it. I am sorry')
                elif (any(expression in line.lower() for expression in how_are_you)):
                    return('Same old. Same old. You? ')
                elif (any(expression in line.lower() for expression in greeting)):
                    return('Hey you!')
                elif (any(line.lower().startswith(expression) for expression in question_starters)):
                    for expression in question_starters:
                        if line.lower().startswith(expression):
                                strs = line
                                list_of_words = line.split(' ')
                                new_list = list_of_words
                                for i in range(len(list_of_words)):
                                    if list_of_words[i].lower() == 'you':
                                        new_list[i] = 'I'
                                    elif list_of_words[i].lower() == 'your':
                                        new_list[i] = 'my'
                                    elif list_of_words[i].lower() == 'me':
                                        new_list[i] = 'you'
                                    elif list_of_words[i].lower() == 'my':
                                        new_list[i] = 'your'
                                    elif list_of_words[i].lower() == 'mine':
                                        new_list[i] = 'yours'
                                    elif list_of_words[i].lower() == 'yours':
                                        new_list[i] = 'mine'
                                i = self.question_response_count % 3
                                new_string = " ".join(new_list)+" "+ question_finishers[i]
                                self.question_response_count += 1
                                return(new_string)
                else:
                    i = self.arbitrary_response_count % 10
                    return_str = arbitrary_input[i]
                    self.arbitrary_response_count += 1
                    return(return_str)

            return self.get_response('no_movies_found')
        
        # in starter mode, take the first movie id available and assign sentiment
        sentiment = self.extract_sentiment(line)

        for title in titles:
            movie_ids = self.find_movies_by_title(title)
            movie_title = '\"' + title + '\"'
            if (len(movie_ids) == 0):
                if self.creative:
                    close_movie_ids = self.find_movies_closest_to_title(title)
                    if len(close_movie_ids) == 0:
                        return "Sorry, I couldn't find any titles close to " + movie_title
                    else:
                        correct_movie_name = self.article_before_title(self.titles[close_movie_ids[0]][0])
                        self.confirm_movie_name = (correct_movie_name, sentiment)
                        
                        
                        if len (close_movie_ids) == 1:
                            return 'Did you mean "' + str(correct_movie_name) + '"?'
                        else:
                            return_str = "Did you mean "
                            for i in len(close_movie_ids) - 1:
                                return_str += str(self.titles[close_movie_ids[i]][0]) + ' or '
                            return_str = return_str + str(self.titles[close_movie_ids[len(close_movie_ids)]][0]) + '"?'
                            return return_str

                                
                else:
                    return "I don't seem to recognize " + movie_title + ". Try giving me another one."
            elif (len(movie_ids) > 1):
                if self.creative:
                    # candidates = self.disambiguate()
                    candidates = [self.article_before_title(self.titles[id][0]) for id in movie_ids]
                    self.disambiguate_option = (movie_ids, sentiment)
                    return 'Which one did you mean? ' + ', '.join(candidates)
                else:
                    return 'I found more than one movie with the title ' + movie_title + '. Try to be more specific.'
            
            movie_id = movie_ids[0]
            self.gathered_ratings[movie_id] = sentiment

        if sentiment == -1:
            echo = self.get_response('sentiment_neg', movie_title)
        elif sentiment == 1:
            echo = self.get_response('sentiment_pos', movie_title)
        else:
            return self.get_response('sentiment_unclear', movie_title)

        if (np.count_nonzero(self.gathered_ratings) < 5):
            return echo + " Let's keep going! Tell me about another movie."
        # generate k recommendations
        k = 10
        self.recommendations = self.recommend(self.gathered_ratings, self.ratings, k, False)
        recommendation_title = '\"' + self.titles[self.recommendations[self.next_recommendation]][0] + '\"'
        self.next_recommendation += 1
        return echo + " " + self.get_response('give_recommendation', recommendation_title)

        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################

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
        titles = []

        start_search_index = 0
        while (start_search_index < len(preprocessed_input)):
            first_quote = preprocessed_input.find('\"', start_search_index)
            second_quote = preprocessed_input.find('\"', first_quote + 1)
            if (first_quote == -1 or second_quote == -1):
                break
            titles.append(preprocessed_input[first_quote + 1 : second_quote])
            start_search_index = second_quote + 1
        
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
            indices = []

            query_name, query_year = self.get_movie_parts_creative(title)

            for i in range(len(self.titles)):
                movie_name, movie_year = self.get_movie_parts_creative(self.titles[i][0])
                query_name_list = []
                movie_name_list = []
                if (query_year == '' and query_name.lower() in movie_name.lower()) or (query_year == movie_year and query_name.lower() in movie_name.lower()):
                    query_name_list = (query_name.lower()).split(' ')
                    movie_name_list = (movie_name.lower()).split(' ')
                    if (all(x in movie_name_list for x in query_name_list)):
                        indices.append(i)
                elif (query_year == '' and self.article_adjusted_title(query_name).lower() in movie_name.lower()) or (query_year == movie_year  and self.article_adjusted_title(query_name).lower() in movie_name.lower()):
                    query_name_list = (self.article_adjusted_title(query_name).lower()).split(' ')
                    movie_name_list = (movie_name.lower()).split(' ')
                    if (all(x in movie_name_list for x in query_name_list)):
                        indices.append(i)

            return indices
        else:
            indices = []

            query_name, query_year = self.get_movie_parts(title)

            for i in range(len(self.titles)):
                movie_name, movie_year = self.get_movie_parts(self.titles[i][0])
                # print('movie_name: ' + movie_name)
                # print('movie_year: ' + movie_year)
                if (query_year == '' and query_name == movie_name) or (query_year == movie_year and query_name == movie_name):
                    indices.append(i)

            return indices

     
    # this function returns the movie title with the article following the title for creative
    def article_adjusted_title(self, title):
        article_list = ['die','den','der','das','dem','des','la','lo','las','los','uno','una','unas','unos','en','il','i','gli','l','gli','un','la','le','de','les','un','une','el','a','an','the']
        movie_name = self.get_movie_parts_creative(title)[0]
        first_word = movie_name[0 : movie_name.find(' ')]
        if (first_word.lower() in article_list):
            title = title[title.find(' ') + 1:] + ', ' + first_word
        return(title)
    
    # this function returns a movie title with the article beginning the title
    def article_before_title(self, title):
        article_list = ['die','den','der','das','dem','des','la','lo','las','los','uno','una','unas','unos','en','il','i','gli','l','gli','un','la','le','de','les','un','une','el','a','an','the']
        movie_name = self.get_movie_parts_creative_keep_punc(title)[0]
        article = movie_name[movie_name.find(', '):][2:]
        if (article.lower() in article_list):
            movie_name = article + " " + movie_name[0:movie_name.find(', ')]
        return(movie_name)


    # this function returns the movie title, movie year for the creative mode
    def get_movie_parts_creative(self,title):
        date = re.findall('(\(\d{4}\))',title)
        if date == []:
            date = re.findall('(\(\d{4}-\d{4}\))',title)
        if date == []:
            date = re.findall('(\(\d{4}-\))',title)
        if date == []:
            movie_name = title
            movie_year = ''
        else:
            movie_name = title.split(date[0])[0].strip()
            movie_year = date[0].strip()
        movie_name = re.sub(r'[^a-zA-Z0-9,\s]', '', movie_name)
        movie_year = re.sub(r'[\(\)]', '', movie_year)
        return movie_name, movie_year
    

    # this function returns the movie title, movie year for the creative mode
    def get_movie_parts_creative_keep_punc(self,title):
        date = re.findall('(\(\d{4}\))',title)
        if date == []:
            date = re.findall('(\(\d{4}-\d{4}\))',title)
        if date == []:
            date = re.findall('(\(\d{4}-\))',title)
        if date == []:
            movie_name = title
            movie_year = ''
        else:
            movie_name = title.split(date[0])[0].strip()
            movie_year = date[0].strip()
        # remove punctuation
        # movie_name = re.sub(r'[^a-zA-Z0-9,\s]', '', movie_name)
        movie_year = re.sub(r'[\(\)]', '', movie_year)
        return movie_name, movie_year
    
    # this function returns the movie title, movie year --> just a way for us to look at them separately
    def get_movie_parts(self, title):
        regex_pattern = '([\w\.\s,]+)(\(\d\d\d\d\))?'

        matches = re.findall(regex_pattern, title)
        movie_match = matches[0]

        # movie_name = first part of title, not including (####)
        movie_name = movie_match[0].strip()
        # movie_year = (####) part of title, or '' if not present
        movie_year = movie_match[1]

        first_word = movie_name[0 : movie_name.find(' ')]
        if (first_word.lower() == 'a' or first_word.lower() == 'an' or first_word.lower() == 'the'):
            # movie a, an, or the to the back if found as the first word
            movie_name = movie_name[movie_name.find(' ') + 1:] + ', ' + first_word
        return movie_name, movie_year

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
        # initialize stemmer
        p = porter_stemmer.PorterStemmer()

        # define negation words
        negations = ["wouldn't", "won't", "didn't", "don't" 'no', 'not', 'never']
        negations = [p.stem(word, 0, len(word) - 1) for word in negations]
        extra_pos_words = ['enjoyed', 'brilliant', 'terrific', 'incredible', 'amazing', 'awesome']
        extra_pos_words = [p.stem(word, 0, len(word) - 1) for word in extra_pos_words]
        extra_neg_words = ['bad', 'hated', 'terrible', 'sucked', 'awful', 'despised', 'horrible', 'ridiculous']
        extra_neg_words = [p.stem(word, 0, len(word) - 1) for word in extra_neg_words]
        intensifiers = ['really', 'most', 'so', 'extremely', 'completely', 'totally']
        intensifiers = [p.stem(word, 0, len(word) - 1) for word in intensifiers]

        titles = self.extract_titles(preprocessed_input)
        if (len(titles) > 0):
            preprocessed_input = preprocessed_input.replace(titles[0], '')

        threshold = 0
        sum = 0

        # coefficient = -1 if in negation
        coefficient = 1

        # next word counts for double if intensifier found, otherwise intensifier stays at 1
        intensifierFound = 1

        words = preprocessed_input.split(' ')
        words = [p.stem(word, 0, len(word) - 1) for word in words]
        for word in words:
            if word in negations:
                coefficient = -1
            # if in negation but have hit the next punctuation mark, exit negation
            elif coefficient == -1 and any(char in string.punctuation for char in word):
                coefficient = 1

            if word in intensifiers:
                intensifierFound = 2
            
            if word not in self.sentiment and word not in extra_pos_words and word not in extra_neg_words:
                continue

            if word in self.sentiment:
                sum += intensifierFound * coefficient * (-1 if self.sentiment[word] == 'neg' else 1)
            elif word in extra_pos_words:
                sum += intensifierFound * coefficient * 1
            else:
                sum += intensifierFound * coefficient * -1
            
            intensifierFound = 1

        if (sum < threshold):
            return -1
        elif (sum == threshold):
            return 0
        else:
            return 1

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
        movie_list = self.extract_titles(preprocessed_input)
        sentiment_list = []
        phrases = []
        # sentiment = 0
                      
        # we extract the sentiment for each title
        words = preprocessed_input.split(' ')
        sentiment_change = ['but', 'yet', 'however']
        sent_shift = False
        
        for word in words:
            # if the movies have different sentiments
            if word in sentiment_change:
                phrases = preprocessed_input.split(word)
                sent_shift = True
        if sent_shift == False:
            phrases = [preprocessed_input]
        prev_sent = 0
        for phrase in phrases:
            sentiment = self.extract_sentiment(phrase)
            if sentiment == 0:
                if prev_sent == 1:
                    sentiment = -1
                elif prev_sent == -1:
                    sentiment = 1
            titles = self.extract_titles(phrase)
            count = len(titles)
            for i in range(count):
                sentiment_list.append(sentiment)
            prev_sent = sentiment
        return(list(zip(movie_list,sentiment_list)))


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
        indices = []
        candidates = []
        min_distance = []
        query_name = title
        for i in range(len(self.titles)):
            # TODO: currently using get_movie_parts_creative_keep_punc here. Might need to change
            movie_name, movie_year = self.get_movie_parts_creative_keep_punc(self.titles[i][0])
            if (self.min_distance(query_name.lower(), movie_name.lower()) <= max_distance):
                min_distance.append(self.min_distance(query_name.lower() ,movie_name.lower()))
                candidates.append(i)
        
        if candidates == []:
            return (candidates)
        else:
            min_val = min(min_distance)
            min_indices = [i for i, val in enumerate(min_distance) if val == min_val]
            indices = [candidates[i] for i in range(len(candidates)) if i in min_indices]
            return(indices)
        
    #helper function calculating minimum distance
    def min_distance(self,source, target):
        n = len(source)
        m = len(target)
        dist_matrix = [[0 for x in range(m+1)] for y in range(n+1)]
        for i in range(1,n+1):
            dist_matrix[i][0] = i
        for j in range(1,m+1):
            dist_matrix[0][j] = j
        for i in range(1,n+1):
            for j in range(1,m+1):
                if source[i-1] == target[j-1]:
                    insert = 0
                else:
                    insert= 2
                dist_matrix[i][j] = min(dist_matrix[i-1][j] + 1, dist_matrix[i][j-1] + 1, dist_matrix[i-1][j-1] + insert)
        return(dist_matrix[n][m])
            
        
            
        
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
        clarification = clarification.lower().strip()
        clarification_title = self.get_movie_parts_creative(clarification)[0]
        #handles queries in the form "the ___ one"
        if len(clarification_title) > 7:
            if (clarification_title[0:3] == 'the' and clarification_title[len(clarification_title)-3:len(clarification_title)] == 'one'):
                #removes the
                clarification_title= clarification_title.replace(clarification_title[:3],'')
                #removes one
                clarification_title = clarification_title[:-3].strip()
        new_candidates = []
        if clarification_title == 'first' or clarification_title == '1st':
            return([candidates[0]])    
        if clarification_title == 'second' or clarification_title == '2nd': 
            if len(candidates) > 1:
                return([candidates[1]])           
        if clarification_title == 'third' or clarification_title == '3rd': 
            if len(candidates) > 2:
                return([candidates[2]])      
        if clarification_title == 'fourth' or clarification_title == '4th': 
            if len(candidates) > 3:
                return([candidates[3]])      
        if clarification_title == 'fifth' or clarification_title == '5th': 
            if len(candidates) > 4:
                return([candidates[4]])          
        if ("most recent" in clarification_title) or ("newest" in clarification_title) or ("recent" in clarification_title): 
            year_list = []
            candidate_list = []
            for candidate in candidates:
                candidate_year = (self.get_movie_parts_creative(self.titles[candidate][0])[1])
                if candidate_year.isdigit():
                    year_list.append(candidate_year)
                    candidate_list.append(candidate)
            max_year_index = year_list.index(max(year_list))
            return([candidate_list[max_year_index]])
        #if they give year in parenthesis, eg "Moviename (2006)" or "(2006)"
        clarification_year = self.get_movie_parts_creative(clarification)[1]
        #if they just give a year, eg "2006"
        if len(clarification_title) == 4 and clarification_title.isdigit():
            clarification_year = clarification_title
            clarification_title = ''

        for candidate in candidates:            
            candidate_title = self.get_movie_parts_creative(self.titles[candidate][0])[0].lower()
            candidate_year = self.get_movie_parts_creative(self.titles[candidate][0])[1]
            # if the clarification is a year:
            if (clarification_year != ''):
                if (clarification_year in candidate_year):
                    new_candidates.append(candidate)
            elif (clarification_year == '') and (clarification_title != ''):
                if (clarification_title in candidate_title):
                    new_candidates.append(candidate)
                elif (len(clarification_title) == 1) and (clarification_title.isdigit()):
                    index = (int(clarification_title)) - 1 
                    if (index) <= len(candidates) :
                        new_candidates.append(candidates[index])
                        break
        return new_candidates

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

        one_indices = np.where((ratings > threshold) & (ratings != 0))
        negative_one_indices = np.where((ratings <= threshold) & (ratings != 0))

        ratings[one_indices] = 1
        ratings[negative_one_indices] = -1

        binarized_ratings = ratings
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
        numerator = np.dot(u, v)
        denominator = (np.linalg.norm(u) * np.linalg.norm(v))

        similarity = numerator if denominator == 0 else numerator / denominator
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

        # expected user scores for unrated movies using cosine similarity --> (movie index, expected rating)
        similarity_list = []

        numerator = 0

        for i in range(len(user_ratings)):
            # if movie i is unrated by user
            if user_ratings[i] == 0:
                numerator = 0

                # use all other user-rated movies to predict rating
                for j in range(len(user_ratings)):
                    if user_ratings[j] == 0:
                        continue
                    cos_sim = self.similarity(ratings_matrix[i], ratings_matrix[j])
                    # print('cos_sim with movie ' + str(j) + " is " + str(cos_sim))
                    numerator += user_ratings[j] * cos_sim
                
                similarity_list.append((i, numerator))
        
        similarity_list = sorted(similarity_list, key=lambda t: t[1], reverse=True)

        # print(similarity_list)

        recommendations = [similarity_list[i][0] for i in range(min(len(similarity_list), k))]
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
