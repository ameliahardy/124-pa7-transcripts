# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util

import numpy as np
import porter_stemmer
import re
import random

p = porter_stemmer.PorterStemmer()

# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'Sherlock Bot'

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
        self.strong_pos = ["loved", "dazzling", "adore", "cherish", "best"]
        self.magnification = ["really", "very", "extremely"]
        
        for i in range(len(self.magnification)):
            self.magnification[i] = p.stem(self.magnification[i]) 
        self.strong_neg = ["terrible", "horrible", "awful", "depressing", "garbage", "enrage", "resent", "hate", "loathe", "abhor", "despise"]
        for i in range(len(self.strong_pos)):
            self.strong_pos[i] = p.stem(self.strong_pos[i])
        for i in range(len(self.strong_neg)):
            self.strong_neg[i] = p.stem(self.strong_neg[i])
        self.ratings = self.binarize(ratings)
        self.dict = {}
        for key in self.sentiment:
            self.dict[p.stem(key)] = self.sentiment[key]
            
        #the list of recommendations we'll be pulling from    
        self.recommendations = []
        #the index of the next recommendation
        self.r_index = 0
        self.info_count = 0
        #whether or not the bot is in "recommend mode"
        self.recommending = False
        self.user_ratings = np.zeros(len(self.titles))
        self.disambiguating = False
        self.candidates = []
        self.savedsentiment = 0
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
        if not self.creative:
            greeting_message = "How may I assist you?"
        else: 
            greeting_message = "Greetings! How may I be of service!"

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
        if not self.creative:
            goodbye_message = "Thank you, have a great day!"
        else: 
            goodbye_message = "Wonderful, we shall meet again!"
        

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
        if not self.creative:
            positiveverbs = ["like ", "liked ", "enjoy ", "enjoyed ", "appreciated "]
            presentpverbs = ["like ", "enjoy ", "love ", "appreciate "]
            negativeverbs = ["do not like ", "didn't enjoy ", "disliked ", "did not enjoy "]
            address = ["Oh I see, ", "Hm, I see, ", "I see, ", "So "]
            e_address = ["Oh wow! So ", "Oh my, so ", "Oh I see, ", "Hm, I see,", "Oh okay, "]
            exaggedposverbs = ["really liked ", "really loved ", "are a big fan of " , "really love "]
            exaggednegverbs = ["really hated ", "despised ", "are a massive hater of " , "hate "]
            ending = [", huh?", ", right?", ", correct?", "?"]
            apo = ["Sorry, I couldn't tell how you felt about ", "Apologies, I'm not sure if you liked ", "Unfortunately I can't exactly tell how you felt about "]
            tellmemore = [" Tell me more!", " What other movies did you enjoy?", " That's really interesting!", " Tell me more about what movies you've watched!"]
            tellmemoreabout = [" Can you tell me more about it?", " Tell me a bit more about your feelings on it. "]
            a = ["Alright, I think you would also enjoy ", "I would definitely recommend ", "You might be interested in ", "I think you would love ", "Here's another movie for you: "]
            arbitraryinputs = ["Sorry, I didn't quite understand you. Tell me about your movie preferences or ask for recommendations.", "That doesn't seem too relevant. Can we talk about movies instead?", "Didn't quite catch you there, can you tell me about your preferences?", "Didn't hear you -- could you repeat that again?"]
        if self.creative:
            positiveverbs = ["found yourself enjoying ", "like ", "appreciated ", "enjoyed ", "derived satisfaction from "]
            presentpverbs = ["find yourself enjoying ", "like ", "love ", "appreciate "]
            negativeverbs = ["dislike ", "did not find satisfaction in watching ", "did not find yourself enjoying ", "did not enjoy "]
            address = ["From my observations, I deduce that ", "My deduction leads me to believe that ", "Based on the evidence at hand, I conclude that ", "I deduce that "]
            e_address = ["Fascinating, so ", "Extraordinary, so ", "Most intriguing, so ", "Remarkable, so "]
            exaggedposverbs = ["thoroughly enjoyed ", "were deeply impressed by ", "have a keen fondness for " , "adore "]
            exaggednegverbs = ["vehemently disliked ", "detested ", "are a strong opponent of " , "loathe "]
            ending = [", do you not agree?", ", is that not correct?", ", is that right?", "?"]
            apo = ["Apologies, I cannot determine your disposition towards ", "I regret that I am unsure of how you feel about ", "Unfortunately, I am unable to discern your opinion on "]
            tellmemore = [" Pray, expound upon it further!", " What other shows have you found to your liking?", " Splendid!", " Elementary!"]
            tellmemoreabout = [" What have you deduced about your enjoyment of it?", " I implore you to elaborate on your thoughts regarding this matter.", "I would appreciate a more detailed account of your feelings on this matter, if you please."]
            a = ["Very well, I believe you may also find this show to be of interest. It's called ", "I would wholeheartedly recommend ", "You may find it worthwhile to investigate ", "It might be worth your while to examine ", "I suggest you consider looking into "]
            arbitraryinputs = ["I'm sorry, I didn't quite understand you. Would you care to elucidate the matter of your movie preferences or ask for my recommendations?", "I'm not sure I see the connection. Might I suggest we talk about movies instead?", "Pardon me, but might you elaborate on your favorite movies?", "I fail to see the relevance of that. Can we perhaps discuss movies instead?"]
            disambig = ["I must ask for further elucidation. Which of these did you have in mind? ", "Pardon my confusion, but could you please specify which of these you meant? ", "Might I trouble you to specify which of these you had in mind? "]
        
        # if "recommend is spotted in here we go "
        def containsRecommend(line):
            recommendkeys = ["recommend", "show me", "give me"]
            for k in recommendkeys:
                if line.lower().find(k) != -1:
                    return True
                
            return False
        
        #CREATIVE MODE
        if self.creative:
            response = ""
            processed_input = self.preprocess(line)
            sentiment = 0
            title = ""
            if self.recommending:
                if (line.lower() == "no"):
                    response = "Wonderful! Onwards, then! "
                    self.recommending = False
                    self.r_index = 0
                elif (line.lower() == "yes"):
                    self.r_index += 1
                    response = random.choice(a) + self.titles[self.recommendations[self.r_index % 10]][0]
                else:
                    response = random.choice(apo) + "this. " + "Could you repeat yourself? "
            else:
                movie_index = -1
                if self.disambiguating:
                    potential_movies = self.candidates
                    if len(self.disambiguate(line, self.candidates)) != 0:
                        potential_movies = self.disambiguate(line, self.candidates)
                    
                    if (len(potential_movies) != 1):
                        response = random.choice(disambig)
                        for i in range(len(potential_movies)):
                            response += self.titles[potential_movies[i]][0]
                            response += ", " if i < len(potential_movies) - 1 else "?"
                    else:
                        movie_index = potential_movies[0]
                        response = "I see! Thank you."
                        self.disambiguating = False
                if not self.disambiguating:
                    #take case where disambiguation has occurred
                    if movie_index != -1:
                        #grab the previously saved sentiment
                        sentiment = self.savedsentiment
                        movie_title = self.titles[movie_index][0]
                        title = movie_title
                    else:
                        #recommendation case
                         
                        title_list = self.extract_titles(processed_input)
                        #if you can't find a movie title
                        if len(title_list) == 0:
                            if not containsRecommend(line):
                                response += random.choice(arbitraryinputs)
                            else:
                                self.recommending = True
                                self.recommendations = self.recommend(user_ratings = self.user_ratings, ratings_matrix = self.ratings)
                                response += "Ah! Do you desire my recommendations for interesting films? Indicate with a yes or no"    
                            return response
                        else:
                            movie_list = self.find_movies_by_title(title_list[0])
                            #cannot find associated movies, do mispelling check
                            if len(movie_list) == 0:
                                potential_movies = self.find_movies_closest_to_title(title_list[0])
                                if (len(potential_movies) > 0):
                                    response += random.choice(["It appears there are no movies named " + "\"" + title_list[0] + "\". \n" + random.choice(disambig), "I could not discover a movie named " + "\"" + title_list[0] + "\". " + random.choice(disambig)])
                                    for i in range(len(potential_movies)):
                                        response += self.titles[potential_movies[i]][0]
                                        response += ", " if i < len(potential_movies) - 1 else "?"
                                    self.candidates = potential_movies
                                    self.disambiguating = True
                                    self.savedsentiment = self.extract_sentiment(processed_input)
                                else: 
                                     response += "I couldn't find any movies named " + "\"" + title_list[0] + "\", " + "could you try again?"
                                return response
                            elif len(movie_list) > 1:
                                response = "Apologies, there seems to be more than one movie named " + "\"" + title_list[0] + "\".  \n" + random.choice(disambig)
                                for i in range(len(movie_list)):
                                    response += self.titles[movie_list[i]][0]
                                    response += ", " if i < len(movie_list) - 1 else "?"
                                self.disambiguating = True
                                #save the intended sentiment
                                self.savedsentiment = self.extract_sentiment(processed_input)
                                self.candidates = movie_list
                                return response
                            else: 
                                movie_index = self.find_movies_by_title(title_list[0])[0]
                                movie_title = self.titles[movie_index][0]
                                title = title_list[0]
                                sentiment = self.extract_sentiment(processed_input)
                    if sentiment == 2:
                        response = random.choice(e_address) + "you " + random.choice(exaggedposverbs) + "\"" + movie_title + "\"" + random.choice(ending)
                    elif sentiment == 1:
                        response = random.choice(address) + "you " + random.choice(positiveverbs) + "\"" + movie_title + "\"" + random.choice(ending)
                    elif sentiment == 0:
                        response = random.choice(apo) + "\"" + movie_title + "\"" + random.choice(tellmemoreabout)
                    elif sentiment == -1:
                        response = random.choice(address) + "you " + random.choice(negativeverbs) + "\"" + movie_title + "\"" + random.choice(ending)
                    elif sentiment == -2:
                        response = random.choice(e_address) + "you " + random.choice(exaggednegverbs) + "\"" + movie_title + "\"" + random.choice(ending)
                    self.user_ratings[movie_index] = sentiment
                    if sentiment != 0:
                        self.info_count += 1
                    if self.info_count == 5:
                        self.recommendations = self.recommend(user_ratings = self.user_ratings, ratings_matrix = self.ratings)
                        self.recommending = True
                        print(self.recommendations)
                        response += "\n"
                        response += "Aha! From what you've said, I deduce you would " + random.choice(presentpverbs) + self.titles[self.recommendations[self.r_index]][0]
                        response += ". Would you like another wonderful discovery? Respond yes or no."
                    else: 
                        response += random.choice(tellmemore)
                
        #STARTER MODE     
        else:
            if self.recommending:
                if (line.lower() == "no"):
                    response = "Okay, sounds good! Tell me more about your movie preferences please! "
                    self.recommending = False
                    self.r_index = 0
                elif (line.lower() == "yes"):
                    self.r_index += 1
                    response = "Alright, I think you would also " + random.choice(presentpverbs) + self.titles[self.recommendations[self.r_index % 10]][0]
                        
                else:
                    response = "Sorry, I couldn't understand you. Would you like another recommendation?"
            else:
                response = "I processed {} in starter mode!!".format(line)
                response = ""
                processed_input = self.preprocess(line)
                title_list = self.extract_titles(processed_input)
                if len(title_list) == 0:
                    response += "Please tell me about your movie preferences"
                else:
                    if not self.recommending: 
                        movie_list = self.find_movies_by_title(title_list[0])
                        if len(movie_list) == 0:
                            response = "Sorry, I couldn't find a movie named movie named " +  "\"" + title_list[0] + "\""
                        elif len(movie_list) > 1:
                            response = "Sorry, there seems to be more than one movie named " + "\"" + title_list[0] + "\". Could you disambiguate between "
                            for i in range(len(movie_list)):
                                response += self.titles[movie_list[i]][0]
                                response += ", " if i < len(movie_list) - 1 else "?"
                        else:
                            movie_index = self.find_movies_by_title(title_list[0])[0]
                            movie_title = self.titles[movie_index][0]
                            title = title_list[0]
                            sentiment = self.extract_sentiment(processed_input)
                            self.user_ratings[movie_index] = sentiment
                            if sentiment == 2:
                                response += random.choice(e_address) + "you " + random.choice(exaggedposverbs) + "\"" + title + "\"" + random.choice(ending)
                                sentiment = 1
                            elif sentiment == 1:
                                response += random.choice(address) + "you " + random.choice(positiveverbs) + "\"" + title + "\"" + random.choice(ending)
                            elif sentiment == 0:
                                response += random.choice(apo) + "\"" + title + "\"" + random.choice(tellmemoreabout)
                            elif sentiment == -1:
                                response += random.choice(address) + "you " + random.choice(negativeverbs) + "\"" + title + "\"" + random.choice(ending)
                            elif sentiment == -2:
                                response += random.choice(e_address) + "you " + random.choice(exaggednegverbs) + "\"" + title + "\"" + random.choice(ending)
                                sentiment = -1
                            self.user_ratings[movie_index] = sentiment
                            self.info_count += 1
                            if self.info_count == 5:
                                self.recommendations = self.recommend(user_ratings = self.user_ratings, ratings_matrix = self.ratings)
                                self.recommending = True
                                response += "\n"
                                response += "Based on what you've told me, I think you'd " + random.choice(presentpverbs) + self.titles[self.recommendations[self.r_index]][0]
                                response += ". Would you like another recommendation? Respond yes or no."
                            else: 
                                response += random.choice(tellmemore)
                        
            
                
                
                
            

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
        
        lst = preprocessed_input.split('"')[1::2]
        return lst

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

        title = title.lower()
        # user titles are of the form "title (\(subtitle\) )*\(year\)?"
        # need to transform starting articles in `title` and all `subtitle`'s in a few languages
        # https://edstem.org/us/courses/20570/discussion/2736351?answer=6271594

        # store the year in a variable and remove it from user title if it exists
        year_str = r" (\([0-9]{4}\))?$"
        year_match = re.search(year_str, title)
        year = ""
        if year_match is not None:
            # store the year and get rid of it in the title
            year = year_match.group(1)
            title = re.sub(year_str, "", title)
        
        # search for articles then postpend them
        regex_str = r"^((?:a|an|the|el|la|los|las|lo|la|le|l\'|les|lo|il|la|gli)) (.+)"
        title = re.sub(regex_str, r"\2, \1", title)

        # regex string to match movie, widen funnel for disambiguate pt 1
        # movie_str = r"(?:^" + title + r" \()|(?:\((?:a.k.a. )?" + title + r"\))"
        movie_str = r"(?:^" + title + r" )|(?:\((?:a.k.a. )?" + title + r"\))"
        # regex string to match movie, widen funnel for disambiguate pt 1
        # movie_str = r"(?:^" + title + r" \()|(?:\((?:a.k.a. )?" + title + r"\))"
        movie_str = r"(?:^" + title + r" )|(?:\((?:a.k.a. )?" + title + r"\))"

        movies = []
        for i in range(len(self.titles)):
            movie = self.titles[i][0]
            movie = movie.lower()

            if re.search(movie_str, movie) is not None:
                if year == "" or movie.find(year) != -1:
                    movies.append(i)
        return movies

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
        
        negation = ["don't", "can't", "not", "didn't", "never"]
        titles = self.extract_titles(preprocessed_input)
        for title in titles:
            preprocessed_input.replace(title, "")
        s = 0
        negate = False
        fine_tune = False
        magnify = False
        if preprocessed_input[len(preprocessed_input) - 1] == '.':
            preprocessed_input = preprocessed_input[:len(preprocessed_input) - 2] 
        for word in preprocessed_input.split(" "): 
            word = p.stem(word)
            if word in self.magnification: 
                magnify = True
            if word not in self.strong_neg and word not in self.strong_pos:
                if word in self.dict and word not in negation:
                    if self.dict[word] == "pos" and negate == False:
                        s += 1
                    elif negate == False and self.dict[word] == "neg":
                        s -= 1
                    elif negate == True and self.dict[word] == "pos":
                        s -= 1
                    else: #negated and sentiment == pos
                        s += 1
                    if word.find(",") or word.find('.'):
                        negate = False 
                    if magnify == True:
                            fine_tune = True
            else: 
                if word in self.strong_pos and negate == False:
                    s += 2
                    fine_tune = True
                if word in self.strong_neg and negate == False:
                    s -= 2
                    fine_tune = True
            if word in negation:
                negate = True 
        if s > 0:
            if fine_tune == False:
                return 1
            else:
                return 2
        if s == 0:
            return 0
        if s < 0:
            if fine_tune == False:
                return -1   
            else:
                return -2    

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
        return []

    def edit_distance(self, word1, word2, pos1, pos2, max_distance, currcount):
        if pos1 == 0:
            return pos2
        if pos2 == 0:
            return pos1
        if abs(pos1 - pos2) > max_distance + 1:
            return max_distance * 10
        if currcount > 3:
            return max_distance * 10
        if word1[pos1 - 1] == word2[pos2 - 1]:
            return self.edit_distance(word1, word2, pos1 - 1, pos2 - 1, max_distance, currcount)
        return 1 + min(self.edit_distance(word1, word2, pos1 - 1, pos2, max_distance, currcount + 1), self.edit_distance(word1, word2, pos1, pos2 - 1, max_distance, currcount + 1))

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
        lst = []
        title = title.lower()
        titlelen = len(title)
        min_distance = max_distance + 1
        for i in range(len(self.titles)):
            movie = self.titles[i][0].lower()
            movie = movie.split('(')[0]
            movielen = len(movie) - 1
            the = movie.find(', the')
            if the != -1 and the == len(movie) - 6:
                movie = 'the ' + movie[0:(len(movie) - 6)]
                movielen -= 1
            if abs(movielen - titlelen) < max_distance + 1 and movielen > 0:
                distance = self.edit_distance(title, movie, titlelen, movielen, max_distance, 0)
                if distance <= max_distance:
                    lst.append([i, distance])
                if distance < min_distance:
                    min_distance = distance
        smallest = []
        for item in lst:
            if item[1] == min_distance:
                smallest.append(item[0])
        return smallest

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
        final = []
        for candidate in candidates:
            c = clarification.lower()
            s = self.titles[candidate][0].lower()
            candidate_year = s[s.find("(")+1:s.find(")")]
            s = s[0:s.find("(")]
            if s.find(c) != -1 or c == candidate_year:
                final.append(candidate)
        return final

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

        binarized_ratings = ratings
        for row in range(binarized_ratings.shape[0]): 
            for elem in range(binarized_ratings.shape[1]):
                if binarized_ratings[row][elem] > threshold: 
                    binarized_ratings[row][elem] = 1
                elif binarized_ratings[row][elem] <= threshold and binarized_ratings[row][elem] > 0:
                    binarized_ratings[row][elem] = -1

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
        denom = (np.linalg.norm(u) * np.linalg.norm(v))
        if denom == 0:
            return 0
        similarity = np.dot(u, v) / denom
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
        ratings_lst = []
        for i in range(len(user_ratings)):
            lst = []
            if user_ratings[i] == 0:
                for j in range(ratings_matrix.shape[0]):
                    if user_ratings[j] != 0:
                        lst.append(self.similarity(ratings_matrix[i], ratings_matrix[j]))
                    else:
                        lst.append(0)
                ratings_lst.append(np.dot(np.array(lst), user_ratings))
            else:
                ratings_lst.append(-1)
        for i in range(k):
            index_max = ratings_lst.index(max(ratings_lst))
            recommendations.append(index_max)
            ratings_lst[index_max] = -1

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
        Sherlock bot will deduce the best movie for you! Give it your opinion of a movie and it will extract
        the sentiment. Ask for it to show you interesting movies or give you recommendations and it will 
        begin returning a list of possible movie recommendations! If you spell something wrong or give a vague title,
        no worries! Sherlock bot will help you clarify.
        """


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
