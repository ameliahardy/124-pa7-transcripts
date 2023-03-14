# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util

import numpy as np

import re 

import porter_stemmer 
p = porter_stemmer.PorterStemmer() # stemmer

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
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')

        self.sentiments = np.zeros(9125)
        self.current_movie = None
        self.movies_extracted = []
        self.num_recommended = 0
        self.current_sentiment = None

        self.rec_phrases = ["Sweet, you might like {}. Would you like another rec?", 
            "You should try seeing {}. Should I give you another rec?", 
            "Great, try watching {}. Should I give you another rec?", 
            "{} is a movie you might enjoy. Do you want another rec?", 
            "Ah, try watching {}. Do you want another rec?"]
        self.done_phrases = ["Thanks, type ‘:quit’ to exit",
            "All good, ‘:quit’ will end this session",
            "Type ‘:quit’ to leave; have a nice day!",
            "It was fun! ‘:quit’ to leave",
            "Just say ‘:quit’ to leave"]
        self.spell_confirm_phrases = ["Just checking, did you mean {}? Type ‘yes’ to confirm",
            "Perhaps you meant {}? type ‘yes’ to confirm",
            "Type ‘yes’ if you meant {}, otherwise type ‘no’",
            "Maybe you meant {}?",
            "Could you have possibly meant {}?"]
        self.spell_failure_phrases = ["Sorry, I don’t know which movie you’re talking about. Try inputting what you thought about a movie, and check the spelling!",
            "Oops, I don’t understand. Please input a correctly spelled movie and what you thought about it.",
            "Hey, not sure what you mean - try inputting another movie and what you thought about it!",
            "Wasn’t able to understand which movie you meant. Try again with a correctly spelled movie and your feelings about it!",
            "Hmm, reinput a movie and your response to it, please! Wasn’t able to understand your last one"]
        self.no_sentiment_phrases = ["Great, could you clarify what you thought about {}",
            "Could you describe more of your feelings about {}",
            "Not sure I know how you felt about {}, could you clarify?",
            "So I know you’re talking about {}, but how did you really feel?",
            "Tell me your true feelings about {}"]
        self.disliked_phrases = ["Sounds like you didn’t enjoy {}. Thoughts on any other movies?",
            "So you didn’t like {}. Anything else?",
            "Seems like you didn’t enjoy {}. Tell me about more movies?",
            "I gather you weren’t a fan of {}. Any more movies?",
            "I don’t blame you, I didn’t like {} either. What else?"]
        self.liked_phrases = ["Sounds like you enjoyed {}. Thoughts on any other movies?",
            "So you liked {}. Anything else?",
            "Seems like you enjoyed {}. Tell me about more movies!",
            "I gather you were a fan of {}. Any more movies?",
            "Nice, I liked {} too! What else?"]
        self.unknown_phrases = ["Hmm, that's a new one to me. Try another one!",
            "Don’t think I’m familiar with that one. Any others come to mind?",
            "So sorry, I haven’t heard of that one before. What other movies do you want to talk about?",
            "Oops, I have no recollection of ever seeing that one. Tell me about another movie!",
            "Silly me, don’t know much about that one. Give me another movie.]"]
        self.ambiguous_phrases = ["Ah, which one of these {} were you talking about?",
            "Not sure I know which one you meant out of {} - could you clarify?",
            "Help me figure out which one of {} that you meant ",
            "Did you mean one of {}? Help me understand which one"
            "Could you please help clarify from the list of {} which you meant?"]
        self.multiple_phrases = ["So sorry, I can only handle one at a time. Try again!",
            "One by one, please!",
            "Could you try again, this time just talking about one movie!",
            "Oops, you might have been talking about multiple movies. Could you try again, just talking about one movie this time?",
            "I think you might’ve been talking about more than one movie. Try again, just one movie review at a time! "]
        self.irrelevant_phrases = ["Let’s go back to talking about movies!",
            "I’d rather talk about movies if that’s alright with you.",
            "Sounds cool, but I’m better at talking about movies!",
            "I hope it’s alright that I can only talk about movies.",
            "Nice nice. Now, tell me about another movie you like or dislike!"]

        self.counter = 0


        ########################################################################
        # TODO: Binarize the movie ratings matrix.                             #
        ########################################################################

        # Binarize the movie ratings before storing the binarized matrix.
        self.ratings = self.binarize(ratings, 2.5)
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

        greeting_message = "How can I help you Hamed?"

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

        goodbye_message = "Have a nice day!"

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
            response = "I processed {} in creative mode!!".format(line)
        #else:
            #response = "I processed {} in starter mode!!".format(line)

        ################

        self.counter = self.counter + 1
        rint = self.counter % 5

        if len(self.movies_extracted) == 4:
            if line.lower().find('no') != -1 or line.lower() == "nah":
                response = self.done_phrases[rint]
            ## recommend
            else:
                top_k = self.recommend(self.sentiments, self.ratings, k = self.num_recommended + 1)
                self.num_recommended = self.num_recommended + 1
                recommended = top_k[self.num_recommended - 1]
                response = self.rec_phrases[rint].format(self.titles[recommended][0])

            

        else: 
            if self.current_movie != None:
                #reget sentiment 
                extracted_movie = self.current_movie
                extracted_sentiment = self.extract_sentiment(line)
            elif self.current_sentiment != None:
                #reget movie
                extracted_movie = self.extract_titles(line)
                extracted_sentiment = self.current_sentiment
            else:
                #reget movie & sentiment
                extracted_movie = self.extract_titles(line)
                extracted_sentiment = self.extract_sentiment(line)
            

            if extracted_sentiment == 0:
                if len(extracted_movie) == 1:
                    self.current_movie = extracted_movie
                    response = self.no_sentiment_phrases[rint].format(extracted_movie[0])
            elif len(extracted_movie) == 1: ## we actually got one movie
                idx = self.find_movies_by_title(extracted_movie[0])
                if len(idx) == 1:
                    self.movies_extracted.append(extracted_movie)
                    self.sentiments[idx] = extracted_sentiment
                    self.current_movie = None
                    self.current_sentiment = None
                    if extracted_sentiment < 0:
                        response = self.disliked_phrases[rint].format(extracted_movie[0])
                    elif extracted_sentiment > 0:
                        response = self.liked_phrases[rint].format(extracted_movie[0])
                elif len(idx) == 0:
                    response = self.unknown_phrases[rint]
                elif len(idx) > 1:
                    response = self.ambiguous_phrases[rint].format(extracted_movie[0])
            elif len(extracted_movie) == 0: #is none
                self.current_sentiment = extracted_sentiment
                if self.current_sentiment == -1:
                    response = "so you didn't like some movie... which one are you talking about?"
                else:
                    response = "so you liked some movie...  which one are you talking about?"
            elif len(extracted_movie) > 1: #is multiple:
                response = self.multiple_phrases[rint]


                

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
        potential_titles = []
        yearRE = '\((\d{4})\)'
        # if the sentence has a year in it 
        yearBool = re.search(yearRE, preprocessed_input)
        movies = []
        for movie in self.titles:
            movie = movie[0].lower()
            year = ''
            if re.search(yearRE, movie):
                year = re.findall('(\(\d{4}\))', movie)[0]
                movie = re.sub(yearRE, '', movie)
                if movie[-1] == ' ': # get rid of excess white space
                    movie = movie[:-1]

            movieWords = movie.split(' ') # check for articles 

            if movieWords[-1] == 'the' or movieWords[-1] == 'a' or movieWords[-1] == 'an':
                movieWords[-2] = movieWords[-2][:-1]
                movie = movieWords[-1] + ' ' + ' '.join(movieWords[:-1]) # take out the comma  

            if yearBool:
                movie += ' ' + year
            movies.append(movie.strip())
                

        numMovies = len(movies)
        preprocessed_input = preprocessed_input.lower()

        start = preprocessed_input.find('"')
        while start != -1 and len(preprocessed_input):
            end = preprocessed_input.find('"',start+1)
            if end == -1:
                break 
            movie = preprocessed_input[start+1: end]
            potential_titles.append(movie) # append the movie 
            #remove it 
            if end == len(preprocessed_input):
                preprocessed_input = preprocessed_input[:start] + preprocessed_input[end:]
                break
            preprocessed_input = preprocessed_input[:start] + preprocessed_input[end+1:]
            start = preprocessed_input.find('"',end+1)

        for i in range(numMovies):
            movie = movies[i]
            MovieRE = '(?:^|[ ])(\"|\')? ?' + re.escape(movie) + ' ?(\"|\')?(?:$|[ ]|\.|,|\?|!|;|:)'
            if re.search(MovieRE,preprocessed_input):
                if movie not in potential_titles:
                    potential_titles.append(movie)

        numTitles = len(potential_titles)
        for i in range(numTitles): # correct the capitalization 
            potential_titles[i] = potential_titles[i].title()

        return potential_titles

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

        ''
        with open("data/movies.txt", 'r') as f:
            movies = f.read().lower()

        title = title.lower()

        t_words = title.split(' ')
        article_bool = False
        year_bool = False


        first_word = t_words[0]
        if first_word  == 'the' or first_word == 'a' or first_word  == 'an':
            article = first_word 
            article_bool = True
        if self.creative:
            if first_word  == 'la' or first_word  == 'il' or first_word  =='le' or first_word == 'l' or first_word == 'les' or first_word == 'die' or first_word =='el':
                article = first_word 
                article_bool = True
        if len(t_words[-1]) == 6:
            if t_words[-1][0] == '(' and t_words[-1][5] == ')':
                year = t_words[-1][1:-1] # dont want parenthesies
                year_bool = True

        
        if article_bool:
            if year_bool: 
                movieTitle = ' '.join(t_words[1:-1])
                yearRE = ' \('+year+'\)'
            else: 
                movieTitle = ' '.join(t_words[1:])
                yearRE = '(?: \([0-9]+\))?' # reflects optional 
            alternateTitle = ' '.join(t_words)
            movieTitle += ', ' + article 
            
        else:
            if year_bool:
                movieTitle = ' '.join(t_words[0:-1])
                yearRE = ' \('+year+'\)'
            else: 
                movieTitle = ' '.join(t_words)
                yearRE = '(?: \([0-9]+\))?' # reflects optional 

        if self.creative:
            regex = '([0-9]+)%(?:.* )?'+re.escape(movieTitle)+'(?: .*)?\(.+\)?'+yearRE+'%' #to allow disambiguation'''
            matches = re.findall(regex, movies)
            if article_bool:
                alternateRegex = '([0-9]+)%(.* )?'+re.escape(alternateTitle)+'( .*)?\(.+\)?'+yearRE+'%'
                matches += re.findall(alternateRegex, movies)

            if len(matches) == 0: # no matches try alternative titles
                regex = '([0-9]+)%(?:.+)\((?:.* )?' + re.escape(movieTitle) + '(?: .*)?\)'+yearRE+'%'
                matches = re.findall(regex, movies)
                if article_bool:
                    regex = '([0-9]+)%(?:.+)\((?:.* )?' + re.escape(alternateTitle) + '(?: .*)?\)'+yearRE+'%'
                    matches += re.findall(alternateRegex, movies)
        else:
            regex = '([0-9]+)%'+re.escape(movieTitle)+'(?: \(.+\))?'+yearRE+'%'
            matches = re.findall(regex, movies)
            if article_bool:
                alternateRegex = '([0-9]+)%'+re.escape(alternateTitle)+'(?: \(.+\))?'+yearRE+'%'
                matches += re.findall(alternateRegex, movies)

            if len(matches) == 0: # no matches try alternative titles
                regex = '([0-9]+)%(?:.+)\((?:a.k.a. )?' + re.escape(movieTitle) + '\)'+yearRE+'%'
                matches = re.findall(regex, movies)
                if article_bool:
                    alternateRegex = '([0-9]+)%(?:.+)\((?:a.k.a. )?' + re.escape(alternateTitle) + '\)'+yearRE+'%'
                    matches += re.findall(alternateRegex, movies)

        '''if self.creative:
            regex = '([0-9]+)%'+movieTitle+'(?:[^\w+].* \(.+\))?'+yearRE+'%' #to allow disambiguation
        else:
            regex = '([0-9]+)%'+movieTitle+'(?: \(.+\))?'+yearRE+'%' '''

        matches = [eval(i) for i in matches] # convert to ints
        return matches

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
        total_p = 0
        total_n = 0

        intensifiers = ['really', 'reaally', 'absolutely', 'completely', 'extremely', 'very', 'totally', 'super']
        intense = ['loved', 'hated', 'great', 'terrible', 'amazing', 'awful', 'fantastic', 'horrible', 'incredible', 'abysmal', 'love', 'hate']
        num = len(intensifiers)
        for i in range(num):
            intensifiers[i] = p.stem(intensifiers[i])
        num = len(intense)
        for i in range(num):
            intense[i] = p.stem(intense[i])

        start = preprocessed_input.find('"')
        while start != -1:
            end = preprocessed_input.find('"', start + 1)
            if end == -1:
                break
            if start != 0:
                start -= 1 # get rid of an extra space too
            # remove the movie name 
            preprocessed_input = preprocessed_input[0:start] +preprocessed_input[end + 1:]
            start = preprocessed_input.find('"')

        preprocessed_input = preprocessed_input.replace('.', '')
        preprocessed_input = preprocessed_input.replace(',', '')
        preprocessed_input = preprocessed_input.replace(':', '')
        preprocessed_input = preprocessed_input.replace(';', '')
        preprocessed_input = preprocessed_input.replace('!', '')
        preprocessed_input = preprocessed_input.replace('?', '')
        preprocessed_input = preprocessed_input.lower()

        words = preprocessed_input.split(' ')
        sentiments = {}
        with open("data/sentiment.txt") as f:
            for line in f:
                l = line.split(',')
                sentiments[p.stem(l[0]).lower()] = l[1].strip()    
        
        # stem the words 
        numWords = len(words)
        i = 0
        while i < numWords:
            negation = 1 # assume no negation
            w = words[i].strip().lower() # lower case
            if w == 'not' or w == 'never' or w == "didn't"  or w == "don't" or w == "wouldn't":
                negation *= -1 # if negation, flip the signs 
                i+= 1 
                if i == numWords:
                    break
                w = words[i].lower()
                w = p.stem(w)
                while w not in sentiments and i < numWords-1: # find next word that has a sentiment 
                    i+= 1
                    w=words[i].lower()
                    w = p.stem(w)
            else:
                w = p.stem(w)
            intensifier = 1 # assume no intensifier
            if self.creative:
                if w in intensifiers:
                    intensifier *= 3
                    i += 1
                    w = words[i].strip()
                    w = p.stem(w)
                    while w not in sentiments and i < numWords-1: # find next word that has a sentiment
                        i += 1
                        w = words[i]
                        w = p.stem(w)
                if w in intense:
                    intensifier *= 3

                if w in sentiments:
                    if sentiments[w] == 'pos':
                        if negation == 1:
                            total_p += 1 * intensifier
                        else:
                            total_n += 1 * intensifier
                    elif sentiments[w] == 'neg':
                        if negation == 1:
                            total_n += 1 * intensifier
                        else:
                            total_p += 1 * intensifier
            else:
                if w in sentiments:
                    if negation == 1:
                        if sentiments[w] == 'pos':
                            total_p += 1
                        elif sentiments[w] == 'neg':
                            total_n += 1
                    else:
                        if sentiments[w] == 'pos':
                            total_n += 1
                        elif sentiments[w] == 'neg':
                            total_p += 1
            i+= 1 
        if self.creative:
            if total_p == 0 and total_n == 0:
                return 0 
            elif total_p == 0:
                if total_n >= 2.5:
                    return -2.0
                else: 
                    return -1.0 
            elif total_n == 0:
                if total_p >= 2.5:
                    return 2.0
                else: 
                    return 1 
            if total_p / total_n >= 2.5:
                return 2.0
            if total_p / total_n > 1:
                return 1
            if total_p / total_n < (2/5):
                return -2
            if total_p / total_n < 1:
                return -1
            return 0
       
        if total_p - total_n > 0:
            return 1
        elif total_p - total_n < 0:
            return -1
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
        movie_sentiments = []

        preprocessed_input = preprocessed_input.lower()

        butIdx = preprocessed_input.find('but')
        if butIdx != -1:
            movies = self.extract_titles(preprocessed_input[:butIdx])
            sentiment1 = self.extract_sentiment(preprocessed_input[:butIdx])
            for movie in movies:
                movie_sentiments.append((movie, sentiment1))
            movies = self.extract_titles(preprocessed_input[butIdx+3:])
            sentiment2 = self.extract_sentiment(preprocessed_input[butIdx+3:])
            if sentiment2 == 0 and preprocessed_input[butIdx+3:].find('not') != -1:
                sentiment2 = -1 * sentiment1
            for movie in movies:
                movie_sentiments.append((movie, sentiment2))
        elif preprocessed_input.find(',but') != -1:
            butIdx = preprocessed_input.find(',but')
            movies = self.extract_titles(preprocessed_input[:butIdx])
            sentiment1 = self.extract_sentiment(preprocessed_input[:butIdx])
            for movie in movies:
                movie_sentiments.append((movie, sentiment1))
            movies = self.extract_titles(preprocessed_input[butIdx+4:])
            sentiment2 = self.extract_sentiment(preprocessed_input[butIdx+4:])
            if sentiment2 == 0 and preprocessed_input[butIdx+3:].find('not') != -1:
                sentiment2 = -1 * sentiment1
            for movie in movies:
                movie_sentiments.append((movie, sentiment2))
        else:
            movies = self.extract_titles(preprocessed_input)
            sentiment = self.extract_sentiment(preprocessed_input)
            for movie in movies:
                movie_sentiments.append((movie, sentiment))
    
        return movie_sentiments


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
        title = title.lower()
        editDistance = {}
        
        n = len(title)
        yearRE = '\([0-9]+\)'   
        # check if the title has a year 
        yearBool = re.search(yearRE, title)

        movies =[]
        if yearBool:
            for movie in self.titles:
                movies.append(movie[0].strip().lower())
        else: 
            for movie in self.titles:
                movie = movie[0]
                if re.search(yearRE, movie):
                    movie = re.sub(yearRE, '', movie)
                movies.append(movie.strip().lower())

        numMovies = len(movies)
        for p in range(numMovies): # find min edit distance for each index 
            guess = movies[p].lower()
            # min edit distance 
            k = len(guess)

            DP = np.zeros((n+1,k+1)) # table where dp[i][j] = min edit distance between i letters of title and j titles of guess 
            for i in range(n+1):
                DP[i,0] = i 
            for j in range(k+1):
                DP[0,j] = j 

            for i in range(1, n+1):
                for j in range(1, k+1):
                    delete = DP[i-1, j] +1
                    insert = DP[i, j-1] +1
                    substitute = DP[i-1, j-1]
                    if title[i-1] != guess[j-1]:
                        substitute += 2
                    DP[i,j] = min(delete, insert, substitute)
            editDistance[p] = DP[n,k]
        minEditDistance = min(editDistance.values())

        if minEditDistance > max_distance:
            return []
        minEditMovies = [key for key in editDistance if editDistance[key] == minEditDistance]
        return minEditMovies
            



   

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
        clarified = []
        movies = []
        string = ""

        clarification = clarification.lower()
        for movie in self.titles:
            movies.append(movie[0].strip().lower())

        # there is a date 
        date = '(\d{4})'
        if re.search(date, clarification):
            year = re.findall(date, clarification)[0]
            # just look for the year
            for candidate in candidates:
                if movies[candidate].find(year) != -1:
                    clarified.append(candidate)
            return clarified

        the_one ='the (.+) one'
        if re.search(the_one, clarification):
            clarification = re.findall(the_one, clarification)[0]

        
        # if it only has numbers 
        if clarification.isnumeric():
            num = " " + clarification
            for candidate in candidates:
                if movies[candidate].find(num) != -1:
                    clarified.append(candidate)
            return clarified 

        # try to find the exact string
        for candidate in candidates:
            if movies[candidate].lower().find(clarification) != -1:
                clarified.append(candidate)
            elif clarification.find(movies[candidate].lower()) != -1:
                clarified.append(candidate)
        # there is at least one match 
        if clarified != []:
            return clarified

        # no matches from exact 
        """numeric_words =['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'nineth']
        for word in numeric_words:
            if word in clarification:"""

        return clarified
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
        b_r = np.zeros(np.shape(ratings))
        b_r[np.where(ratings <= threshold)] = -1
        b_r[np.where(ratings > threshold)] = 1
        b_r[np.where(ratings == 0)] = 0


        ########################################################################
        #                        END OF YOUR CODE                              #
        ########################################################################
        return b_r

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

        
        #norm = np.sqrt(np.sum(u**2))
        #norm *= np.sqrt(np.sum(v**2))
        #similarity /= norm
        if np.linalg.norm(u) == 0 or np.linalg.norm(v) == 0: 
            return 0
        u = u/np.linalg.norm(u)
        v = v/np.linalg.norm(v)

        similarity = np.dot(u,v)
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

        # first compute which movies are rated / we need to find predict ratings for 
        haveRatings = list(np.where(user_ratings != 0)[0])
        needRatings = list(np.where(user_ratings == 0)[0])

        # go through each place that needs a rating and find ratings for it 
        predictions = {}
        # this is the user's rating for each item they have seen
        ratings = user_ratings[haveRatings]

        for idx in needRatings:
            #find similarity array to all other items with ratings and array of user's rating for those items 
            similarities = []
            currentItem = ratings_matrix[idx,:]
        
            for validIdx in haveRatings:
                # find similarity before item idx and item validIdx 
                presentItem = ratings_matrix[validIdx,:]
                similarities.append(self.similarity(currentItem, presentItem))
            similarities = np.array(similarities)
            predictions[idx] = np.dot(ratings, similarities)
        predictions = sorted(predictions.items(), key = lambda x: x[1], reverse = True)
        
        for i in range(k):
            recommendations.append(predictions[i][0])
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
