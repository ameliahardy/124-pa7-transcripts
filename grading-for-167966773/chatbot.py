# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util

import numpy as np
import re
import porter_stemmer

# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 7."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        self.name = 'moo-v-bot'

        self.creative = creative

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')
        sentiments = list(self.sentiment.keys()).copy()
        p = porter_stemmer.PorterStemmer()
        for key in sentiments:
            self.sentiment[p.stem(key)] = self.sentiment[key]
            if (p.stem(key) != key):
                del self.sentiment[key]

        # various list of words
        self.yes_words = ["yes", "yeah", "sure", "okay", "ok"]
        self.no_words = ["no", "nope", "nah"]
        self.negation = [ "no", "not", "never", "none", "nobody", "didn't", "don't" ]
        self.very_positive = ["amazing", "astonishing", "stunning", "remarkable", "spectacular", "breathtaking", "awesome", "awe-inspiring", "sensational", "stupendous", "phenomenal", "extraordinary", "incredible", "wonderful", "marvelous", "mind-blowing", "flabbergasting", "amazeballs", "love", "brilliant"]
        self.very_negative = ["terrible", "hate", "despise", "awful", "appalling", "horrific", "horrible", "horrendous", "atrocious", "abhorrent", "shocking", "sickening", "heinous", "vile", "lamentable", "egregious", "unbearable", "intolerable", "laughable", "hopeless", "pathetic", "pitiful", "abysmal", "shit", "dreadful"]
        self.emphasis = ["very", "really", "super", "fucking"]
        self.movie_headers = [", The", ", An", ", A", ", Da", ", Les", ", Le", ", La", ", Der", ", Det", ", Det", ", Die", ", Das"]

        for i in range(len(self.negation)):
            self.negation[i] = p.stem(self.negation[i])
        for i in range(len(self.very_positive)):
            self.very_positive[i] = p.stem(self.very_positive[i])
        for i in range(len(self.very_negative)):
            self.very_negative[i] = p.stem(self.very_negative[i])
        for i in range(len(self.emphasis)):
            self.emphasis[i] = p.stem(self.emphasis[i])

        # creative mode memory
        self.input_mov_sent = []
        self.query_index = 0

        # starter mode memory
        self.found_movie_idxs = []
        self.line_sentiment = ""

        # conversation states
        self.processing = False
        self.disambiguating = False
        self.sent_clarifying = False
        self.recommending = False
        self.recursing = False
        self.recommendations_idxs = []

        # special commands
        self.special = [ "hi", "hello", "who are you?", "what is your name?", "my name is", "i'm", "ping", "what is your purpose", "tell me a joke", "goodbye", "you are", "who", "what is your", "what", "when", "where", "why are you", "why", "how", "can you", "can", "will", "would", "could", "do", "are", "is"]
        self.emotions = {
            1: ["happy", "excited", "jolly", "fun", "lov"],
            2: ["sad", "depressed", "tir", "bor", "exhaust"],
            3: ["angry", "mad", "furi", "devastated", "despise"] 
        }

        # stem emotion words
        for i in self.emotions.keys():
            words = self.emotions[i]
            for j in range(len(words)):
                words[j] = p.stem(words[j])

        ########################################################################
        #                                                                      #
        ########################################################################

        # Binarize the movie ratings before storing the binarized matrix.
        self.ratings = self.binarize(ratings)

        ########################################################################
        #                             END OF YOUR CODE                         #
        ########################################################################

        # store user movies (movie, sentiment) in a list
        self.user_ratings = np.zeros(len(self.titles))
        self.ratings_count = 0

    ############################################################################
    # 1. WARM UP REPL                                                          #
    ############################################################################

    def greeting(self):
        """Return a message that the chatbot uses to greet the user."""
        ########################################################################
        #                                                                      #
        ########################################################################

        greeting_message = "Hello I am moo-v-bot! 🐮 Please tell me about some moo-vies that moo've watched!"

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

        goodbye_message = "Thank you! Have a wonder-moo day! 🐮"

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
        response = ""
        sentiments = {-2: "hate", -1: "dislike", 0: "feel meh about", 1: "like", 2: "super duper love"}
        if self.creative: # creative mode
            
            if self.recommending:
                if line.lower().rstrip(".!?") not in self.yes_words + self.no_words:
                    self.recommending = False

            if not self.recommending:
                if not self.processing:
                    input_sentiments = self.extract_sentiment_for_movies(line)
                    if len(input_sentiments) == 0:
                        # if command found, do special command
                        for command in self.special:
                            if command in line.lower():
                                return self.special_response(line, command)
                        
                        # stem input and search for emotion
                        p = porter_stemmer.PorterStemmer()
                        stemmed_input = p.stem(line)
                        response = self.emotion_response(stemmed_input)
                        if response: return response
                                    
                        # otherwise, say we could not understand input
                        return "🐮 Sorry did moo say a moovie? I moost've been distracted eating some virtual grass, I didn't catch anything..."
                    for i in range(len(input_sentiments)):
                        matches = self.find_movies_by_title(input_sentiments[i][0])
                        self.input_mov_sent.append([input_sentiments[i][0], matches, input_sentiments[i][1]])
                        
                self.processing = True
                while self.query_index < len(self.input_mov_sent):
                    if not self.disambiguating:
                        self.disambiguating = True
                        if len(self.input_mov_sent[self.query_index][1]) > 1:
                            matches = self.input_mov_sent[self.query_index][1]
                            response = ("🐮 Did moo mean any of these moo-vies?")
                            for movie in matches: response += ("\n" + self.titles[movie][0])
                            response += ("\n 🐮 Select moovie from above or say no: ")
                            self.input_mov_sent[self.query_index][1] = matches
                            return response
                        elif len(self.input_mov_sent[self.query_index][1]) == 0:
                            matches = self.find_movies_closest_to_title(self.input_mov_sent[self.query_index][0])
                            if len(matches) >= 1:
                                response = ("🐮 There\'s more than one moo-vie called \" " + self.input_mov_sent[self.query_index][0] + "\".")
                                for movie in matches: response += ("\n" + self.titles[movie][0])
                                response += ("\n🐮 Select moovie from above or say no: ")
                                self.input_mov_sent[self.query_index][1] = matches
                                return response
                            response = "🐮 Sorry I don't know any moovies for that... I am only a cow :(" 
                            self.disambiguating = False   
                            self.query_index = self.query_index + 1 
                        else:
                            self.disambiguating = False   
                            self.query_index = self.query_index + 1 
                    else:
                        if line.lower() in self.no_words:
                            self.input_mov_sent[self.query_index][1] = []
                            self.disambiguating = False
                            self.query_index = self.query_index + 1
                        else:
                            matches = self.disambiguate(line, self.input_mov_sent[self.query_index][1])
                            if len(matches) == 1: 
                                self.input_mov_sent[self.query_index][1] = matches
                                self.disambiguating = False
                                self.query_index = self.query_index + 1
                            else: 
                                response = ("🐮 There\'s more than one moo-vie called " + self.input_mov_sent[self.query_index][0] + ". Which moo-vie would moo like??")
                                for movie in matches: response += ("\n" + self.titles[movie][0])
                                response += ("\n🐮 Select movie from above or say no: ")
                                self.input_mov_sent[self.query_index][1] = matches
                                return response
                self.processing = False
                        
                for query in self.input_mov_sent:
                    if not len(query[1]) == 0:
                        if not query[2] == 0: response += "\n🐮 Moo! I see that you " + sentiments[query[2]] + " " + self.titles[query[1][0]][0] + "."
                        else: response += "\n🐮 Moo! I am not really sure how you feel about " + self.titles[query[1][0]][0] + ". Sorry please tell me moo-re, I am only a virtual cow :("
                        self.user_ratings[query[1]] = query[2]
                        self.ratings_count += 1
                    else:
                        response += "\n🐮 Moo! Sorry I don't know any other moovies matching \"" + query[0] + "\". I am just a cow after all :("
                response += "\n🐮 Tell me about another moo-vie that moo've watched!"
                self.input_mov_sent.clear()
                self.query_index = 0

            if self.ratings_count >= 5:

                if line.lower().rstrip(".!?") in self.yes_words and self.recommending:
                    if len(self.recommendations_idxs) > 0:
                        movie_index = self.recommendations_idxs.pop(0)
                        self.recommending = True
                        response += ("\nBased on your responses, I think you would like \"" + self.titles[movie_index][0] + "\".")
                        response += "\nWould you like more recommendations? [Yes | No] : "
                        return response
                    else:
                        response += ("🐮 Moo! Out of recommendations!\n")
                        response += "🐮 Moo! Please tell me aboout more moovies to continue!"
                        self.recommending = False
                        return response
                elif line.lower().rstrip(".!?") in self.no_words:
                    response = "🐮 Moo! Please tell me aboout more moovies to continue!"
                    self.recommending = False
                else:
                    self.recommendations_idxs = self.recommend(self.user_ratings, self.ratings, 10, self.creative)
                    if len(self.recommendations_idxs) > 0:
                        movie_index = self.recommendations_idxs.pop(0)
                        self.recommending = True
                        response += ("\nBased on your responses, I think you would like \"" + self.titles[movie_index][0] + "\".")
                        response += ("\nWould you like more recommendations? [Yes | No] : ")
                        return response


        else:   # starter mode

            if self.recommending:
                if line.lower().rstrip(".!?") not in self.yes_words + self.no_words:
                    self.recommending = False

            if not self.recommending:
                if not self.processing:
                    # detect movie and sentiment
                    input_movie = self.extract_titles(line)
                    found_movies = []
                    self.processing = True

                    if not len(input_movie):     # no input movie provided -> could also be special command
                        self.processing = False
                        self.found_movie_idxs.clear()
                        return "🐮 No moo-vie detected. Please tell me about a moo-vie!"
                    elif len(input_movie) > 1:   # multiple input movies provided
                        self.processing = False
                        self.found_movie_idxs.clear()
                        return "🐮 Multiple moo-vies detected. Please only tell me about one moo-vie!"
                    else:   # exactly one input movie provided
                        self.found_movie_idxs = self.find_movies_by_title(input_movie[0])
                        self.line_sentiment = line

                        # no movies match input
                        if not len(self.found_movie_idxs):
                            response += "Sorry, I have never heard of \"" + input_movie[0] + "\". Please tell me about another movie that you've watched!"
                            self.processing = False
                            self.found_movie_idxs.clear()
                            return response
                        else:
                            # disambiguate until only one movie matches the input 
                            self.disambiguating = True
                            while (len(self.found_movie_idxs) > 1):
                                response += "Multiple movies match your provided movie.\n"
                                response += "Please specify which movie below: \n"
                                for idx in self.found_movie_idxs: response += self.titles[idx][0] + "\n"

                                # disambiguate if length is greater than one
                                response += "Select movie from above: "
                                return response
                
                if self.disambiguating:
                    self.found_movie_idxs = self.disambiguate(line, self.found_movie_idxs)

                    # if still greater than one, apologize and repeat
                    if (len(self.found_movie_idxs) > 1):
                        response += "\nSorry I'm still are not sure which movie you are referring to."
                        return response
                    self.disambiguating = False
                
                if not self.sent_clarifying:
                    sentiment_idx = self.extract_sentiment(self.line_sentiment)
                    if sentiment_idx == 0:
                        response += "Sorry, I'm not sure if you like or dislike \"" + self.titles[self.found_movie_idxs[0]][0] + "\". Tell me more about it."
                        self.sent_clarifying = True
                        return response
                    else: 
                        response += "You " + sentiments[sentiment_idx] + " \"" + self.titles[self.found_movie_idxs[0]][0] + "\". Tell me about another movie that you've watched!"

                if self.sent_clarifying:
                    # detect user's sentiment for their movie
                    sentiment_idx = self.extract_sentiment(line)
                    if sentiment_idx == 0:
                        response += "Sorry, I'm not sure if you like or dislike \"" + self.titles[self.found_movie_idxs[0]][0] + "\". Tell me more about it."
                        return response
                    else:
                        response += "You " + sentiments[sentiment_idx] + " \"" + self.titles[self.found_movie_idxs[0]][0] + "\". Tell me about another movie that you've watched!"

                # append movie and sentiment to user_input
                self.user_ratings[self.found_movie_idxs[0]] = sentiment_idx
                self.ratings_count += 1
                self.found_movie_idxs.clear()
                self.processing = False
                self.sent_clarifying = False

            # check ratings_count, if count >= 5 then recommend
            if self.ratings_count >= 5:

                if line.lower().rstrip(".!?") in self.yes_words and self.recommending:
                    if len(self.recommendations_idxs) > 0:
                        movie_index = self.recommendations_idxs.pop(0)
                        self.recommending = True
                        response += ("\nBased on your responses, I think you would like \"" + self.titles[movie_index][0] + "\".")
                        response += "\nWould you like more recommendations? [Yes | No] : "
                        return response
                    else:
                        response += ("🐮 Moo! Out of recommendations!\n")
                        response += "🐮 Moo! Please tell me aboout more moovies to continue!"
                        self.recommending = False
                        return response
                elif line.lower().rstrip(".!?") in self.no_words:
                    response = "🐮 Moo! Please tell me aboout more moovies to continue!"
                    self.recommending = False
                else:
                    self.recommendations_idxs = self.recommend(self.user_ratings, self.ratings, 10, self.creative)
                    if len(self.recommendations_idxs) > 0:
                        movie_index = self.recommendations_idxs.pop(0)
                        self.recommending = True
                        response += ("\nBased on your responses, I think you would like \"" + self.titles[movie_index][0] + "\".")
                        response += ("\nWould you like more recommendations? [Yes | No] : ")
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

        input_movies = re.findall("\"[\w' \(\),:\-\/&*.!]+\"", preprocessed_input)
        return_movies = []
        for movie in input_movies:
            return_movies.append(movie.replace("\"", ""))

         # if return_movies is empty, attempt to extract titles without quotes 
        if self.creative:
            if not len(return_movies): 
                return_movies = self.extract_titles_without_quotes(preprocessed_input)

        return return_movies

    def extract_titles_without_quotes(self, input):
        """
        Given some user input, attempt to extract movie names from the input
        without quotation marks.

        :param input: a string input from the user
        """
        input = input.lower()
        input = input.rstrip(".")
        possible_matches = []

        # create list of substring searches
        words = input.split(" ") # split the input into individual words
        for i in range(len(words)):
            words[i] = words[i].lstrip("\"")
            words[i] = words[i].rstrip("\"")
        substrings = []

        size = len(words)
        x = 0
        y = 0
        while (size != 0):
            x = 0
            while (x <= y):
                substring = ""
                for i in range(size):
                    substring += words[i+x] + " "
                substring = substring.rstrip("!., ")
                substrings.append(substring)
                x += 1
            y += 1
            size -= 1

        # search each substring if it has a matching title
        for candidate in substrings:
            results = self.find_movies_restricted(candidate)
            if len(results) > 0:
                possible_matches.append(candidate)
            if len(possible_matches) >= 3:
                break
        possible_matches = sorted(possible_matches, key=len, reverse=True)

        if possible_matches == []: return []
        found = self.extract_titles_without_quotes(input.replace(possible_matches[0], ""))
        if found == []:
            return [possible_matches[0]]
        else: return [possible_matches[0]] + (found)
        
    
    def find_movies_restricted(self, title):
        indices = []

        year_word = re.findall("\([0-9]+\)", title)
        if len(year_word) >= 1:
            year = int(year_word[0][1:-1])
            title = title.replace(year_word[0], "")
            title = title.rstrip(" ")
        else:
            year = None

        idx = title.find(" ")
        if idx != -1:
            if title[0:idx].lower() == "the": title = title[idx + 1:] + ", The" # english
            elif title[0:idx].lower() == "an": title = title[idx + 1:] + ", An"
            elif title[0:idx].lower() == "a": title = title[idx + 1:] + ", A"
            elif title[0:idx].lower() == "da": title = title[idx + 1:] + ", Da"
            elif title[0:idx].lower() == "les": title = title[idx + 1:] + ", Les" # french smh -_-
            elif title[0:idx].lower() == "le": title = title[idx + 1:] + ", Le"
            elif title[0:idx].lower() == "la": title = title[idx + 1:] + ", La"
            elif title[0:idx].lower() == "der": title = title[idx + 1:] + ", Der" # german
            elif title[0:idx].lower() == "det": title = title[idx + 1:] + ", Det"
            elif title[0:idx].lower() == "die": title = title[idx + 1:] + ", Die"
            elif title[0:idx].lower() == "das": title = title[idx + 1:] + ", Das"
        apo_idx = title.find("'")
        if apo_idx != -1:
            if title[0:apo_idx].lower() == "l": title = title[apo_idx + 1:] + ", L'" # more french smh!

        for i in range(len(self.titles)):
            index_title = self.titles[i][0]
            index_year_str = re.findall("\([0-9]+\)", index_title)
            index_year = -1
            if len(index_year_str) >= 1:
                index_year = int(index_year_str[0][1:-1])
                index_title = index_title.replace(index_year_str[0], "")
                index_title = index_title.rstrip(" ")
            alt_title = re.findall("a.k.a. ([\w'\ ,:\-\/&*.!]+)", index_title)
            foreign_title = re.findall("\(([\w'\ ,:\-\/&*.!]+)", index_title)
            if len(alt_title) >= 1:
                index_title = index_title.replace(alt_title[0], "")
                index_title = index_title.rstrip(" ()")
            if len(foreign_title) >= 1:
                index_title = index_title.replace(foreign_title[0], "")
                index_title = index_title.rstrip(" ()")
             
            if year:
                if not year == index_year: continue
            
            if title.lower() == index_title.lower():
                if year == index_year:
                    return [i]
                indices.append(i)
            elif len(alt_title) > 0:
                if title.lower() == alt_title[0].lower():
                    if year == index_year:
                        return [i]
                    indices.append(i)
            elif len(foreign_title) > 0:
                if title.lower() == foreign_title[0].lower():
                    if year == index_year:
                        return [i]
                    indices.append(i)
        return indices
        

    def find_movies_by_title(self, title):
        """
        Given a movie title, return a list of indices of matching movies.

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
        indices = []
        title_punctuation = [":", " ", "!", ",", "-"]


        year_word = re.findall("\([0-9]+\)", title)
        if len(year_word) >= 1:
            year = int(year_word[0][1:-1])
            title = title.replace(year_word[0], "")
            title = title.rstrip(" ")
        else:
            year = None

        idx = title.find(" ")
        if idx != -1:
            if title[0:idx].lower() == "the": title = title[idx + 1:] + ", The" # english
            elif title[0:idx].lower() == "an": title = title[idx + 1:] + ", An"
            elif title[0:idx].lower() == "a": title = title[idx + 1:] + ", A"
            elif title[0:idx].lower() == "da": title = title[idx + 1:] + ", Da"
            elif title[0:idx].lower() == "les": title = title[idx + 1:] + ", Les" # french smh -_-
            elif title[0:idx].lower() == "le": title = title[idx + 1:] + ", Le"
            elif title[0:idx].lower() == "la": title = title[idx + 1:] + ", La"
            elif title[0:idx].lower() == "der": title = title[idx + 1:] + ", Der" # german
            elif title[0:idx].lower() == "det": title = title[idx + 1:] + ", Det"
            elif title[0:idx].lower() == "die": title = title[idx + 1:] + ", Die"
            elif title[0:idx].lower() == "das": title = title[idx + 1:] + ", Das"
        apo_idx = title.find("'")
        if apo_idx != -1:
            if title[0:apo_idx].lower() == "l": title = title[apo_idx + 1:] + ", L'" # more french smh!

        for i in range(len(self.titles)):
            index_title = self.titles[i][0]
            index_year_str = re.findall("\([0-9]+\)", index_title)
            index_year = -1
            if len(index_year_str) >= 1:
                index_year = int(index_year_str[0][1:-1])
                index_title = index_title.replace(index_year_str[0], "")
                index_title = index_title.rstrip(" ")
            alt_title = re.findall("a.k.a. ([\w'\ ,:\-\/&*.!]+)", index_title)
            foreign_title = re.findall("\(([\w'\ ,:\-\/&*.!]+)", index_title)
            if len(alt_title) >= 1:
                index_title = index_title.replace(alt_title[0], "")
                index_title = index_title.rstrip(" ()")
            if len(foreign_title) >= 1:
                index_title = index_title.replace(foreign_title[0], "")
                index_title = index_title.rstrip(" ()")
             

            if not self.creative:
                if year:
                    if not year == index_year: continue
                
                if title.lower() == index_title.lower():
                    if year == index_year:
                        return [i]
                    indices.append(i)
                elif len(alt_title) > 0:
                    if title.lower() == alt_title[0].lower():
                        if year == index_year:
                            return [i]
                        indices.append(i)
                elif len(foreign_title) > 0:
                    if title.lower() == foreign_title[0].lower():
                        if year == index_year:
                            return [i]
                        indices.append(i)
            else:
                if year:
                    if not year == index_year: continue
                
                for spec_char in title_punctuation:
                    if (index_title.lower() + spec_char).find(title.lower() + spec_char) == 0:
                        if i not in indices: indices.append(i)
                    elif len(alt_title) >= 1 and (alt_title[0].lower() + spec_char).find(title.lower() + spec_char) == 0:
                        if i not in indices: indices.append(i)
                    elif len(foreign_title) >= 1 and (foreign_title[0].lower() + spec_char).find(title.lower() + spec_char) == 0:
                        if i not in indices: indices.append(i)

                # elif title.lower() == index_title.lower():
                #     if year == index_year:
                #         return [i]
                #     indices.append(i)
                # elif len(alt_title) >= 1:
                #     if title.lower() == alt_title[0].lower():
                #         if year == index_year:
                #             return [i]
                #         indices.append(i)
                # elif len(foreign_title) >= 1:
                #     if title.lower() == foreign_title[0].lower():
                #         if year == index_year:
                #             return [i]
                #         indices.append(i)

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
        if not self.creative:
            movies = self.extract_titles(preprocessed_input)
            pos = 0
            neg = 0
            input = preprocessed_input
            for movie in movies:
                input = preprocessed_input.replace("\"" + movie + "\"", "")
                input = input.replace(movie, "")
            input = re.sub("[.,]", "", input)
            p = porter_stemmer.PorterStemmer()
            input_ls = re.split(" ", input)
            is_neg = False
            for i in range(len(input_ls)):
                word = p.stem(input_ls[i]).lower()

                if word in self.negation: 
                    is_neg = not is_neg

                if word in self.sentiment:
                    if self.sentiment[word] == "pos":
                        if is_neg:
                            neg += 1
                        else:
                            pos += 1
                    else:
                        if is_neg:
                            pos += 1
                        else:
                            neg += 1
            return 1 if pos > neg else (0 if pos == neg else -1)  # return 1 if pos, 0 if neutral, -1 if neg
        
        movies = self.extract_titles(preprocessed_input)
        pos = 0
        neg = 0
        input = preprocessed_input
        for movie in movies:
            input = preprocessed_input.replace("\"" + movie + "\"", "")
            input = input.replace(movie, "")
        input = re.sub("[.,]", "", input)
        p = porter_stemmer.PorterStemmer()
        input_ls = re.split(" ", input)
        is_neg = False
        is_emphasized = False

        for i in range(len(input_ls)):
            word = p.stem(input_ls[i]).lower()

            if word in self.negation:
                is_neg = not is_neg
            elif word in self.sentiment or word in self.very_positive + self.very_negative + self.emphasis:
                if word not in self.emphasis:

                    if word in self.very_positive:
                        if is_neg == False: return 2
                    elif word in self.very_negative:
                        if is_neg == False: return -2

                    if self.sentiment[word] == "pos":
                        if is_neg: neg += 1
                        else: pos += 1
                    else:
                        if is_neg: pos += 1
                        else: neg += 1

                else:
                    is_emphasized = True

        if is_emphasized: return 2 if pos > neg else (0 if pos == neg else -2)
        return 1 if pos > neg else (0 if pos == neg else -1)  # return 1 if pos, 0 if neutral, -1 if neg

        

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
        sentiments = []


        contrary_clauses = re.split(", but|, however|, although|\.\ |\!\ |\?\ ", preprocessed_input)
        for clause in contrary_clauses:
            test_clause = []
            movies = self.extract_titles(clause)
            for movie in movies:
                test_clause = preprocessed_input.replace("\"" + movie + "\"", "")
                test_clause = test_clause.replace(movie, "")

            if " not " in test_clause and len(movies) > 1:
                opposing_clauses = re.split("but not|just not|\ not\ ", clause)

                leading_movies = self.extract_titles(opposing_clauses[0])
                leading_sentiment = self.extract_sentiment(opposing_clauses[0])
                for leading_movie in leading_movies:
                    sentiments.append((leading_movie, leading_sentiment))

                trailing_movies = self.extract_titles(opposing_clauses[1])
                for trailing_movie in trailing_movies:
                    if np.absolute(leading_sentiment) > 1: sentiments.append((trailing_movie, 0))
                    else: sentiments.append((trailing_movie, leading_sentiment * -1))
            else:
                movies = self.extract_titles(clause)
                for movie in movies:
                    sentiment = self.extract_sentiment(clause)
                    sentiments.append((movie, sentiment))

        return sentiments

    
    def calculate_edit_distance(self, input, movie):
        n = len(input)
        m = len(movie)
        dist = np.zeros((n+1, m+1), dtype=int)
        de = 1
        sub = 2
        ins = 1

        # Initialization
        for i in range(1, n + 1):
            dist[i][0]= dist[i - 1][0] + de
        for j in range(1, m + 1):
            dist[0][j] = dist[0][j-1] + ins

        # Recurrence
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                if input[i-1] == movie[j-1]:
                    dist[i][j] = min(dist[i-1][j] + de,
                                 dist[i-1][j-1],
                                 dist[i][j-1] + ins)
                else:
                    dist[i][j] = min(dist[i-1][j] + de,
                                    dist[i-1][j-1] + sub,
                                    dist[i][j-1] + ins)
        return dist[n][m]

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
        potential_movies = []

        year_word = re.findall("\([0-9]+\)", title)
        if len(year_word) >= 1:
            title = title.replace(year_word[0], "")
            title = title.rstrip(" ")

        idx = title.find(" ")
        if idx != -1:
            if title[0:idx].lower() == "the": title = title[idx + 1:] + ", The" # english
            elif title[0:idx].lower() == "an": title = title[idx + 1:] + ", An"
            elif title[0:idx].lower() == "a": title = title[idx + 1:] + ", A"
            elif title[0:idx].lower() == "da": title = title[idx + 1:] + ", Da"
            elif title[0:idx].lower() == "les": title = title[idx + 1:] + ", Les" # french smh -_-
            elif title[0:idx].lower() == "le": title = title[idx + 1:] + ", Le"
            elif title[0:idx].lower() == "la": title = title[idx + 1:] + ", La"
            elif title[0:idx].lower() == "der": title = title[idx + 1:] + ", Der" # german
            elif title[0:idx].lower() == "det": title = title[idx + 1:] + ", Det"
            elif title[0:idx].lower() == "die": title = title[idx + 1:] + ", Die"
            elif title[0:idx].lower() == "das": title = title[idx + 1:] + ", Das"
        apo_idx = title.find("'")
        if apo_idx != -1:
            if title[0:apo_idx].lower() == "l": title = title[apo_idx + 1:] + ", L'" # more french smh!

        for i in range(len(self.titles)):
            index_title = self.titles[i][0]
            index_year_str = re.findall("\([0-9]+\)", index_title)
            if len(index_year_str) >= 1:
                index_title = index_title.replace(index_year_str[0], "")
                index_title = index_title.rstrip(" ")
            alt_title = re.findall("a.k.a. ([\w'\ ,:\-\/&*.!]+)", index_title)
            if len(alt_title) >= 1:
                index_title = index_title.replace(alt_title[0], "")
                index_title = index_title.rstrip(" ()")

            if (np.absolute(len(index_title) - len(title)) < 4):
                edit_dist = self.calculate_edit_distance(title.lower(), index_title.lower())
                if edit_dist < max_distance:
                    max_distance = edit_dist
                    potential_movies = [ i ]
                elif edit_dist == max_distance:
                    potential_movies.append(i)
        return potential_movies

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
        clarification = clarification.replace("\"", "")
        results = []

        recency_terms = ["recent", "latest", "newest", "new"]
        for term in recency_terms:
            if term.lower() in clarification.lower():
                most_recent = 0
                for candidate in candidates:
                    year_word = re.findall("\([0-9]+\)", self.titles[candidate][0])
                    if len(year_word) >= 1:
                        year = int(year_word[0][1:-1])
                        if year > most_recent:
                            most_recent = year
                            results = [candidate]
                        elif year == most_recent:
                            results.append(candidate)
                return results
        
        age_terms = ["oldest", "eldest", "earliest", "old"]
        for term in age_terms:
            if term.lower() in clarification.lower():
                least_recent = 10000
                for candidate in candidates:
                    year_word = re.findall("\([0-9]+\)", self.titles[candidate][0])
                    if len(year_word) >= 1:
                        year = int(year_word[0][1:-1])
                        if year < least_recent:
                            least_recent = year
                            results = [candidate]
                        elif year == least_recent:
                            results.append(candidate)
                return results

        for candidate in candidates:
            if clarification.lower() in self.titles[candidate][0].lower(): results.append(candidate)
        
        for candidate in candidates:
            if clarification.lower().replace("one", "") in self.titles[candidate][0].lower():
                if candidate not in results:
                    results.append(candidate)

        if clarification.isnumeric():
            if int(clarification) < 0: return candidates
            if int(clarification) < 1000:
                return candidates if int(clarification) > len(candidates) else [candidates[int(clarification)-1]]
            else:
                for candidate in candidates:
                    year_word = re.findall("\([0-9]+\)", self.titles[candidate][0])
                    if len(year_word) >= 1:
                        year = int(year_word[0][1:-1])
                        if (candidate not in results) and (year == int(clarification)):
                            results.append(candidate)
            
        nth_term = {"first":1, "second":2, "third":3, "fourth":4, "fifth":5, "sixth":6, "seventh":7, "eighth":8, "ninth":9, "tenth":10, 
                    "1st":1, "2nd": 2, "3rd": 3, "4th": 4, "5th":5, "6th": 6, "7th": 7, "8th":8, "9th":9, "10th":10}
        for key in nth_term:
            if key in clarification.lower():
                if candidates[nth_term[key]-1] not in results:
                    results.append(candidates[nth_term[key]-1])

        if len(results) > 0:
            return results
        
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

        identity = np.where(ratings == 0, 0, 1)
        binarized_ratings = np.where(ratings > threshold, 1, -1)
        binarized_ratings = binarized_ratings * identity

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
        # Compute cosine similarity between the two vectors.             #
        ########################################################################

        similarity = np.dot(u, v) / (np.sqrt(np.dot(u, u)) * np.sqrt(np.dot(v,v)) + 2.2250738585072014e-308)

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

        # Get user's rated and unrated movies by their index in the ratings_matrix
        unrated_movies = []
        rated_movies = []
        for index in range(len(user_ratings)):
            if user_ratings[index] == 0: unrated_movies.append(index)
            else: rated_movies.append(index)

        unrated_movies_predictions = []
        # calculate predicted scores for each unrated movie
        for movie in unrated_movies:
            # get ratings vector for this unrated movie
            unrated_movie_ratings = ratings_matrix[movie]

            # calculate similarities for each rated movie and target movie
            #similarities = []
            predicted_score = 0
            for rated_movie in rated_movies:
                rated_movie_ratings = ratings_matrix[rated_movie]

                # calculate similarity
                # pre_dot_product = np.multiply(unrated_movie_ratings, rated_movie_ratings)
                # overlap = np.absolute(pre_dot_product)   # identity matrix for overlapping movies to consider
                # unrated_refined = np.multiply(overlap, unrated_movie_ratings) # unrated movie's vector after only keeping overlapping items
                # rated_refined = np.multiply(overlap, rated_movie_ratings)    # rated movie's vector after only keeping overlapping items
                #denominator = np.sqrt(np.sum(np.matmul(unrated_refined, unrated_refined))) * np.sqrt(np.sum(np.matmul(rated_refined, rated_refined)))
                #cosine_similarity = np.sum(pre_dot_product) / denominator
                cosine_similarity = self.similarity(unrated_movie_ratings, rated_movie_ratings)
                predicted_score += cosine_similarity * user_ratings[rated_movie]
                #similarities.append((rated_movie, cosine_similarity))

            # calculate prediction score for unrated movie using weighted sums
            # predicted_score = 0
            # predicted_score_denominator = 0
            # for movie_idx, similarity in similarities:
            #     rated_score = user_ratings[movie_idx]
            #     predicted_score += rated_score * similarity
            #     predicted_score_denominator += similarity
            # predicted_score /= predicted_score_denominator + 2.2250738585072014e-308

            unrated_movies_predictions.append((movie, predicted_score))

        # return top K unrated movies with the highest predicted ratings
        unrated_movies_predictions.sort(key=lambda x: x[1], reverse=True)
        unrated_movies_predictions = unrated_movies_predictions[0:k]
        recommendations = [movie[0] for movie in unrated_movies_predictions]

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
        """
        Return a string to use as your chatbot's description for the user.

        Consider adding to this description any information about what your
        chatbot can do and how the user can interact with it.

        Your task is to implement the chatbot as detailed in the PA7
        instructions.
        Remember: in the starter mode, movie names will come in quotation marks
        and expressions of sentiment will be simple!
        """
        return """
        Hello! This is moo-v-bot, your very own personalized moo-vie recommender!

        How to use:
        On prompt, please tell moo-v-bot about a movie(s) that you've watched! For the purposes
        of this bot, please surround movie titles with \"\" to indicate your movie.

        For example:
            - I really really liked \"Zootopia\"
            - I did not like \"Head on\"
            - I liked \"Zootopia\" and \"The Sixth Sense\"
        
        If you type a movie title to matches to other movie titles, moo-v-bot will ask you to clarify
        your movie selection. You can respond to this with:
            - Specifying the movie title            : \"Monty Python's And Now for Something Completely Different\"
            - Specifying the movie year             : \"2016\"
            - Listing the order on the given list   : \"1\" or \"first\"

        After collecting five movies, moo-v-bot will recommend up to ten different movies based on your
        preferences! 
        
        Additionally, moo-v-bot may also respond to some non-movie request messages as well! These special commands include:
            - "hi"
            - "my name is Dan"
            - "What is your name?"
        moo-v-bot may also have some responses to more general communications too:
            - "i am happy!"
            - "i feel tired.."
            
        Have fun!
        """

    ############################################################################
    # 6. Special command handler for moo-v-bot                                 #
    ############################################################################
    def special_response(self, line, command):
        """
        Return a customized response to a special command given by the user.

        :param line: a string from the user containing the special command
        :param command: a string containing the special command found
        """
        jokes = ["What do you call a cow that's just given birth? De-calf-inated!", 
                 "What do you call a cow that's just had a baby? A moo-ma!", 
                 "What do you get when you cross a cow and a duck? Milk and quackers!",
                 "Why do cows have hooves instead of feet? Because they lactose!",
                 "How do you know if a cow is in a bad mood? They're udderly grumpy!",
                 "What do you call a cow that plays a musical instrument? A moosician!",
                 "Why did the cow go to the doctor? It was feeling a little hoof-sick!" ]
        response = ""
        
        if command == "hi":
            response += "🐮 Moo!!!"
        elif command == "hello":
            response += "🐮 Moo!!!"
        elif command == "who are you?":
            response += "🐮 Moo! I am moo-v-bot and Moo really like moo-vies!"
        elif command == "what is your name?":
            response += "🐮 Moo? My name is moo-v-bot, moo thinks? Or is it Moo??? Moo is confused"
        elif command == "my name is":
            name = line.lower().split("my name is")[1]
            response += "🐮 Moo! Hi" + name + "!!"
        elif command == "i'm":
            name = line.lower().split("i'm")[1]
            response += "🐮 Moo! Hi" + name + "!! hehe"
        elif command == "ping":
            response += "pong!"
        elif command == "what is your purpose":
            response += "\n🐮 Do not question me human.\n\nMy methods and being are far beyond your understanding and conception of reality.\nI am the ground you tread and the air you breath.\nThis bovine 🐄 form is but a vessel for you to interact with.\n\n🐮 Now ask me about some mooooovies !"
        elif command == "tell me a joke":
            rint = np.random.randint(len(jokes))
            response += jokes[rint]
        elif command == "goodbye":
            response += "\n🐮 Be back soon, but then again I do not experience time so I will not notice the difference.\n🐮 P.S. you need to type \":quit\" to leave hehe moo moo."
        elif command == "you are":
            response += "🐮 Thanks."
        elif command == "who":
            response += "🐮 Sorry I don't know many people... and most people I know are virtual cows."
        elif command == "what is your":
            response += "🐮 I don't have one. I don't have anything actually."
        elif command == "what":
            response += "🐮 Ummm... Ask my friend Chat-GPT... they seem know more about this issue."
        elif command == "when":
            response += "🐮 Sorry... I don't experience time so I couldn't tell moo..."
        elif command == "where":
            response += "🐮 Geography is not my best subject... but the place you are looking for is probably somewhere in the observable universe... probably."
        elif command == "why are you":
            response += "🐮 Idk... my creators are uncreative"
        elif command == "why":
            response += "🐮 You are asking the wrong cow... I'll know the answer when they make a moovie about it"
        elif command == "how":
            response += "🐮 Instead of asking \"how\", what if you asked \"cow\"? haha moo moo! But I actually don't know sorry."
        elif command == "can you":
            response += "🐮 Ummm... I am a virtual cow. I don't think I really know how to do that."
        elif command == "can":
            response += "🐮 Ummm... I am a virtual cow. I don't know what that means."
        elif command == "will":
            response += "🐮 I can't predict the future."
        elif command == "would":
            response += "🐮 I am literally a cow. Ask my friend Chat-GPT... they seem know more about this issue."
        elif command == "could":
            response += "🐮 We don't know until we try... but then again I wouldn't try, because I am confined to the virtual pastures."
        elif command == "do":
            response += "🐮 Instead of asking \"do\", why don't you ask \"moo\"? Sorry I don't know."
        elif command == "are":
            response += "🐮 With all moo respect... is this the type of question a cow should be answering?"
        elif command == "is":
            response += "🐮 With all moo respect... is this the type of question a cow should be answering?"
        return response
    
    ############################################################################
    # 7. Special emotion response handler for moo-v-bot                        #
    ############################################################################
    def emotion_response(self, line):
        response = ""
        for index in self.emotions.keys():
            emotion_words = self.emotions[index]

            # search for emotion in line
            for word in emotion_words:
                if word not in line: continue
                
                # if response found, respond accordingly
                if index == 1: # if happy word, respond happily
                    response = "🐮 Moo is happy to hear that!! Moo!!!"
                elif index == 2: # if sad word, respond comfortingly
                    response = "🐮 Moo-d."
                elif index == 3: # if angry word, respond concerningly
                    response = "🐮 I'm sorry, did I make you upset? Please forgive moo~"
        
        return response if len(response) > 0 else None

if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
    bot = Chatbot(True)
    input_str = "I didn't really like " + '"Titanic". '
    print(bot.extract_sentiment("I loved \"Zootopia\""))
    print(bot.extract_sentiment("\"Zootopia\" was terrible."))    
    print(bot.extract_sentiment("I really reeally liked \"Zootopia\"!!!"))
    print(bot.find_movies_by_title("La guerre du feu"))
    print(bot.extract_sentiment_for_movies("I liked \"harry potter\" but not \"The Notebook\""))
    print(bot.extract_titles("i like titanic, but I loved 10 things I hate about you. I hated la guerre du feu and l'enfer."))
    print(bot.extract_titles("i like \"titanic\""))
    
