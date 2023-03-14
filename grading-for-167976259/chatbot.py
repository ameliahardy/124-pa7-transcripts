# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util
import re
import numpy as np
import porter_stemmer
from collections import Counter
import string
import random

p = porter_stemmer.PorterStemmer()

# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    # simple function to negate a sentiment
    def negate(self, sentiment):
        if sentiment == 'pos':
            return 'neg'
        return 'pos'

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'piratebot'

        self.creative = creative

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')

        lexicon = util.load_sentiment_dictionary('data/sentiment.txt')
        sentiment = {}

        # add stemmed and negated words to sentiment dictionary
        for word, sent in lexicon.items():
            stemmed = p.stem(word)
            negated = 'NOT_'+ word
            negated_stemmed = 'NOT_'+stemmed
            if word not in sentiment:
                sentiment[word] = sent
                sentiment[negated] = self.negate(sent)
            if stemmed not in sentiment:
                sentiment[stemmed] = sent
                sentiment[negated_stemmed] = self.negate(sent)
        
        self.sentiment = sentiment

        # store user's sentiment responses
        self.user_ratings = np.zeros(len(self.titles))
        self.num_ratings = 0

        # book-keeping variables for making recommendations
        self.recommend_mode = False
        self.recommendations_made = 0
        self.recommendations = []
        self.yes = ['y', 'yes', 'yeah', 'ok', 'okay', 'yep', 'aye']
        self.no = ['n', 'no', 'nah', 'nay']

        # book-keeping variables for spell-checking dialogue
        self.spell_check_mode = False
        self.spell_check_sentiment = 0
        self.spell_check_movie_index = -1
        self.spell_check_movie_title = ""

        # book-keeping variables for disambiguation
        self.disambiguation_mode = False
        self.disambiguation_sentiment = 0
        self.disambiguation_candidates = []

        # responses
        self.no_movies_found = ["Barnacles, I don't understand yer words. Tell me about a movie, and put yer movie in double-quotes when you do.",
                                "Arrrr, what did you say? Are you talking about movies? Make sure to put yer movie in double-quotes.",
                                "Heave hoo. Put yer words in a way that I can understand. Double-check yer movie in double-quotes."]
        self.never_heard = ["Barnacles, never heard of ",
                            "Shiver me timbers, I have never come across a movie called ",
                            "Argh, all across the seven seas, I have never heard of "]
        self.no_new_candidates = ["Hmm none of the above movies matched yer description. Try again, mate.",
                                  "Argh, are you talking about the any of the above movies? Clarify yer movie, matey.",
                                  "Barnacles, yer description doesn't match any of the above movies. Rephrase yerself, matey."]
        self.no_change_disambiguation = ["I'm still not sure which movie you mean. Be more specific, mate.",
                                         "Young lad, I still don't know what yer movie you're referring to. Specify yerself",
                                         "Matey, be mor specific with yer words, so I can narrow down what yer saying."]
        self.narrow_down_disambiguation = ["Aye aye, I was able to narrow down the options but I don't know which of these movies you're referring to:",
                                           "Aha matey, that helped me narrow down the options, but clarify yerself further:",
                                           "I was able to narrow yer options further, but which one of these options were you talking about, matey?"]
        self.narrow_disambiguation_ques = ["\nCan you name just one of them, mate?",
                                           "\nPick what yer movie is from these options, mate.",
                                           "\nName yer movie, seadog."]
        self.spell_check_false = ["Shiver me timbers, clarify what movie you are talking about.",
                                  "What is yer movie then, matey?",
                                  "Avast ye, tell me yer movie, again. Careful of yer spelling."]
        self.spell_check_idk = ["I don't understand. Mate, be clear, let me know whether yer talking about ",
                                "Nay, what yer talking about? Answer my question. Are you talking about ",
                                "Shiver me timbers, answer my question clearly first. Is yer movie "]
        self.zero_sentiment = ["I can't tell whether yer like the movie not not, mate. Make sure to inlcude a name of a movie and how you felt about it.",
                               "Mate, I don't know how you feel about yer movie. Be clear how you felt about yer movie, and include the name of it.",
                               "Alas mate, be a tad more clear whether you enjoyed yer movie. Include yer movie name and yer feelings about it."]
        self.multi_movies = ["Shiver me timbers! Too many movies! Please tell me about one movie at a time. Go ahead.",
                             "Mate, tell me one movie at a time. Do that for me.",
                             "Arrrr, one movie at a time, mate. Go again."]
        self.start_recs1 = ["\nAvast, I have enough information to make a recommendation.",
                            "\nI can give you a recommendation now.",
                            "\nYer in luck, mate. I have a recommendation for you."]
        self.start_recs2 = ["\nI suggest you watch ",
                            "\nYou should try watching ",
                            "\nMatey, the best movie for you is "]
        self.start_recs3 = [" You want another recommendation, mate? (Or enter :quit if you're done).",
                            " I got more recommendations. You want another, mate? (Or enter :quit if you're done).",
                            " There's more recommendations I plundered for you. Care for another? (Or enter :quit if you're done)."]
        self.recs_yes = ["Ahoy! Another movie I would recommend is ",
                         "Yarr, you should watch ",
                         "A mate like you should watch "]
        self.recs_10 = ["\nArgh, you've got 10 recommendations already.  I want to hear more about yer movie preferences now. Tell me more about another movie.",
                        "\nArrrr, I'm all out of recommendations. Yer turn to talk about movies.",
                        "\nBlast it seadog, you've had enough recommendations. Yer turn to talk."]
        self.recs_ques = ["More recs for ya?",
                          "Yer feeling for more recs, mate?",
                          "I got more recs for ya. Want to hear another, matey?"]
        self.recs_no = ["Garr, I see that you don't want any more recommendations. Tell me more about yer movie taste, seadog.",
                        "Mate, I guess you're tired of my recs. Give me more opinions on yer movies."]
        self.recs_idk = ["Garrr, I don't understand. Do you want more recommendations (type yes/no/:quit)?",
                         "Nay, what yer talking about? Answer my question. Do you want more recommendations (type yes/no/:quit)?",
                         "Shiver me timbers, answer my question clearly first. Do you want more recommendations (type yes/no/:quit)?"]
        self.liked = ["Arr, I see that you liked ",
                      "It's great to see that you liked watching ",
                      "Ahoy! You liked "]
        self.disliked = ["Garr, it seems you didn't enjoy ",
                         "Shiver me timbers, you didn't like ",
                         "Arrrr, I see that you felt badly about "]
        self.neutral = ["Hurr, I'm not sure if you liked ",
                        "Blimey! I can't tell if you liked ",
                        "Argh, tell again whether you liked "]
        self.neutral2 = [
            "Tell me more, lad,",
            "Be clear how you felt about yer movie.",
            "Alas mate, be a tad more clear whether you enjoyed yer movie."]
        self.tell_me_more = ["Tell me about another movie, mate.",
                             "Tell me about another movie, or walk the plank.",
                             "Yo-ho-ho, add on another movie opinion for me."]
        self.multi_possible1 = ["Blimey! I found more than one movie called ",
                                "Shiver me timbers, there are more than one movies called "]
        self.multi_possible2 = ["Clarify yerself.", "Can you clarify which movie you mean, mate?"]




        ########################################################################
        # TODO: Binarize the movie ratings matrix.                             #
        ########################################################################

        # Binarize the movie ratings before storing the binarized matrix.
        self.ratings = self.binarize(ratings)
        # self.ratings = ratings
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

        greeting_message = "Ahoy! I am " + self.name + ". Give me ye movie taste, matey. I shall grant you some recommendations."

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

        goodbye_message = "Good talking to you, matey."

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
        no_movie_found = random.choice(self.no_movies_found)
        if self.creative:
            if self.disambiguation_mode:
                # get new candidates from old ones and new clarification line
                new_candidates = self.disambiguate(line.lower(), self.disambiguation_candidates)
                if (len(new_candidates) == 0):
                    return random.choice(self.no_new_candidates)
                if (len(new_candidates) == 1):
                    self.disambiguation_mode = False
                    s = self.disambiguation_sentiment
                    self.disambiguation_sentiment = 0
                    return self.process_from_sentiment_creative(new_candidates[0],
                                                                self.titles[new_candidates[0]][0],
                                                                s)
                if (len(new_candidates) == len(self.disambiguation_candidates)):
                    return random.choice(self.no_change_disambiguation)
                if (len(new_candidates) > 1):
                    self.disambiguation_candidates = new_candidates
                    response = random.choice(self.narrow_down_disambiguation)
                    for i in new_candidates:
                        response += "\n\"" + self.titles[i][0] + "\""
                    response += random.choice(self.narrow_disambiguation_ques)
                    return response
            if self.recommend_mode:
                return self.process_recommendation("in progress", line)
            if self.spell_check_mode:
                line = line.lower()
                if line in self.yes:
                    self.spell_check_mode = False
                    for movie, sentiment in self.spell_check_sentiment:
                        if movie.lower() == self.spell_check_movie_title.lower():
                            self.spell_check_sentiment = sentiment
                    return self.process_from_sentiment_creative(self.spell_check_movie_index, self.spell_check_movie_title, self.spell_check_sentiment)
                elif line in self.no:
                    self.spell_check_mode = False
                    return random.choice(self.spell_check_false)
                else:
                    return random.choice(self.spell_check_idk) + "\"" + self.spell_check_movie_title + "\" (yes/no)."

            response = ""
            possible_movies = self.extract_titles(line.lower())
            if (possible_movies == []):
                if ("i am" in line.lower()):
                    response+= "I hear that you are" + line[line.lower().find("i am")+4:]
                elif ("i feel" in line.lower()):
                    response += "I hear that you are feeling" + line[line.lower().find("i feel")+6:]
                elif ("i'm'" in line.lower()):
                    response += "I hear that you are" + line[line.lower().find("i'm'")+3:]
                else:
                    response += "Arr I don't understand"
                response += ". Describe how you felt about movie you've seen, or type \":quit\" to jump ship."
                return response
            sentiment = self.extract_sentiment(line)
            if sentiment == 0:
                return random.choice(self.zero_sentiment)
            if len(possible_movies) == 0:
                return no_movie_found
            else:
                response += self.process_movie_creative(possible_movies, line)

        else:
            if self.recommend_mode:
                return self.process_recommendation("in progress", line)

            response = ""
            possible_movies = self.extract_titles(line)
            if len(possible_movies) == 0:
                return no_movie_found
            elif len(possible_movies) > 1:
                return random.choice(self.multi_movies)
            else:
                sentiment = self.extract_sentiment(line)
                if sentiment == 0:
                    return random.choice(self.zero_sentiment)
                response += self.process_movie(possible_movies[0], line)  # only processes the first quoted input
        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return response

    # processes the potential movie and returns a response based on possible movie and sentiment
    def process_movie(self, possible_movie, line):
        movie_indeces = self.find_movies_by_title(possible_movie)

        if movie_indeces == []:
            return random.choice(self.never_heard) + "\"" + possible_movie + "\". " + random.choice(self.tell_me_more)
        elif len(movie_indeces) > 1:
            question = random.choice(self.multi_possible1) + "\"" + possible_movie + "\". " + random.choice(self.multi_possible2)
            for i in movie_indeces:
                question += "\n\"" + self.titles[i][0] +"\""
            return question
        else:
            movie_index = movie_indeces[0]
            movie_title = self.titles[movie_index][0]
            sentiment = self.extract_sentiment(line)
            if sentiment == 0:
                return random.choice(self.neutral) + "\"" + movie_title + "\". " + random.choice(self.neutral2)
            elif sentiment < 0:
                self.user_ratings[movie_index] = -1
                self.num_ratings += 1
                response = random.choice(self.disliked) + "\"" + movie_title + "\"!"
                # make recommendation
                if self.num_ratings % 5 == 0:  # recommendation mode activates after every 5 ratings inputted
                    response += self.process_recommendation("start recs")
                else:
                    response += " " + random.choice(self.tell_me_more)
                return response
            else:
                self.user_ratings[movie_index] = 1
                self.num_ratings += 1
                response = random.choice(self.liked) + "\"" + movie_title + "\"!"
                # make recommendation
                if self.num_ratings != 0 and self.num_ratings % 5 == 0:  # recommendation mode activates after every 5 ratings inputted
                    response += self.process_recommendation("start recs")
                else:
                    response += " " + random.choice(self.tell_me_more)
                return response

    # returns a recommendation and manages book-keeping in recommendation mode
    def process_recommendation(self, stage, line=""):
        line = line.lower()
        line = re.sub(r'[,.!?]', '', line)
        if stage == "start recs":  # initializes recommendations automatically at first
            self.recommend_mode = True
            self.recommendations = [self.titles[index][0]for index in self.recommend(self.user_ratings, self.ratings, 10)]
            self.recommendations_made += 1
            return random.choice(self.start_recs1) + random.choice(self.start_recs2) + "\"" + self.recommendations[0] + "\"." + random.choice(self.start_recs3)
        elif stage == "in progress":
            line = line.lower()
            if line in self.yes:
                response = ""
                response += random.choice(self.recs_yes) + "\"" + self.recommendations[self.recommendations_made] + "\". "
                self.recommendations_made += 1
                if self.recommendations_made == 10:   # end recommendation mode; return to asking for ratings
                    response += random.choice(self.recs_10)
                    self.recommend_mode = False
                    self.recommendations = []
                    self.recommendations_made = 0
                else:
                    response += random.choice(self.recs_ques)
                return response
            elif line in self.no:
                self.recommend_mode = False
                self.recommendations = []
                self.recommendations_made = 0
                return random.choice(self.recs_no)
            else:
                return random.choice(self.recs_idk)

    # CREATIVE MODE: processes the potential movie and returns a response based on possible movie and sentiment
    def process_movie_creative(self, possible_movies, line):
        movie_index = []
        for possible_movie in possible_movies:
            index = self.find_movies_by_title(possible_movie)
            if index == []:
                movie_indices = self.find_movies_closest_to_title(possible_movie)
                # spell check dialogue prompting
                if len(movie_indices) > 0:
                    self.spell_check_movie_index = movie_indices[0]
                    self.spell_check_movie_title = self.titles[movie_indices[0]][0]
                    self.spell_check_mode = True
                    self.spell_check_sentiment = self.extract_sentiment_for_movies(line.lower().replace(possible_movie, self.spell_check_movie_title))
                    return "Did you mean \"" + self.spell_check_movie_title + "\"?"
                return random.choice(self.never_heard) + "\"" + possible_movie + "\". " + random.choice(self.tell_me_more)
            elif len(index) > 1:
                self.disambiguation_mode = True
                self.disambiguation_sentiment = self.extract_sentiment_for_movies(line)[0][1]
                #print("the sentiment is", self.disambiguation_sentiment)
                question = random.choice(self.multi_possible1) + "\"" + possible_movie + "\". " + random.choice(self.multi_possible2)
                for i in index:
                    question += "\n\"" + self.titles[i][0] + "\""
                self.disambiguation_candidates = index
                return question
            else:
                movie_index.append(index)

        sentiments = self.extract_sentiment_for_movies(line)
        return self.process_from_sentiment_creative(movie_index, None, sentiments)

    def process_from_sentiment_creative(self, movie_index, movie_title, sentiments):
        liked = []
        disliked = []
        neutral = []

        # if processing spell-check corrected movie
        if movie_title:
            if sentiments == 0:
                self.sentiment_dis
                return random.choice(self.neutral) + "\"" + movie_title + "\". " + random.choice(self.neutral2)
            elif sentiments < 0:
                self.user_ratings[movie_index] = -1
                self.num_ratings += 1
                response = random.choice(self.disliked) + "\"" + movie_title + "\"!"
                # make recommendation
                if self.num_ratings % 5 == 0:  # recommendation mode activates after every 5 ratings inputted
                    response += self.process_recommendation("start recs")
                else:
                    response += " " + random.choice(self.tell_me_more)
                return response
            else:
                self.user_ratings[movie_index] = 1
                self.num_ratings += 1
                response = random.choice(self.liked) + "\"" + movie_title + "\"!"
                # make recommendation
                if self.num_ratings != 0 and self.num_ratings % 5 == 0:  # recommendation mode activates after every 5 ratings inputted
                    response += self.process_recommendation("start recs")
                else:
                    response += " " + random.choice(self.tell_me_more)
                return response
            
        # otherwise, process sentiments for all mentioned movies
        for i in range(len(sentiments)):
            sentiment = sentiments[i][1]
            movie_title = self.titles[movie_index[i][0]][0]
            if sentiment < 0:
                disliked.append("\"" + movie_title + "\"")
                self.user_ratings[movie_index[i]] = -1
            elif sentiment > 0:
                liked.append("\"" + movie_title + "\"")
                self.user_ratings[movie_index[i]] = 1
            else:
                neutral.append("\"" + movie_title + "\"")
            self.num_ratings += 1

        liked_res, disliked_res, neutral_res = "", "", ""
        if liked:
            if len(liked) > 1:
                liked[0] =  ", ".join(liked[:-1]) + " and " + liked[-1]
            liked_res = random.choice(self.liked) + liked[0] + "."
        if disliked:
            if len(disliked) > 1:
                disliked[0] =  ", ".join(disliked[:-1]) + " and " + disliked[-1]
            disliked_res = random.choice(self.disliked) + disliked[0] + "."
        if neutral:
            if len(neutral) > 1:
                neutral[0] =  ", ".join(neutral[:-1]) + " and " + neutral[-1]
            neutral_res = random.choice(self.neutral) + neutral[0] + ". Tell me more."
        
        response = liked_res + " " + disliked_res + " " + neutral_res
    
        if self.num_ratings != 0 and self.num_ratings % 5 == 0:  # recommendation mode activates after every 5 ratings inputted
            response += self.process_recommendation("start recs")
        else:
            response += "\n" + random.choice(self.tell_me_more)
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
        # text = text.lower() // taken out bc it messed with the sanity checks
        # text = re.sub(r'[,.!?]', '', text)
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
        rtn = []
        # starter mode
        pattern = r'"(.*?)"'
        rtn = re.findall(pattern, preprocessed_input)

        return rtn

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
        rtn = []
        stopwords = ['a', 'an', 'the', 'la', 'el', 'un', 'una', 'le', 'une', 'a.k.a.', 'los', 'las', 'die']

        # starter mode
        year_pattern = r'(\([\d-]+\))'
        word_pattern = r'([\w]+)'
        token_pattern = r'(\([[\d-]+]|[\w]+]\))'
        alternate_name_pattern = r'(\([^\d\(\)]+\))'

        # divide test into words and remove stopwords
        title = title.lower()  # REMOVE .LOWER() PREPROCESS IF NEEDED
        test_words = re.findall(word_pattern, title)
        test_tokens = test_words
        test_words = [w for w in test_words if w not in stopwords]
        #test_tokens = re.findall(token_pattern, title)

        for i in range(len(self.titles)):
            t = self.titles[i][0].lower()  # REMOVE .LOWER() PREPROCESS IF NEEDED

            # divide title into words and remove stopwords
            title_words = re.findall(word_pattern, t)
            alternate_titles = re.findall(alternate_name_pattern, t)  # get alternate titles

            title_tokens = title_words
            title_words = [w for w in title_words if w not in stopwords]

            # tokenize and remove stopwords from each alternate title found 
            for j in range(len(alternate_titles)):
                alt_title_words = re.findall(word_pattern, alternate_titles[j])
                alt_title_words = [w for w in alt_title_words if w not in stopwords] 
                alternate_titles[j] = alt_title_words

            # subtract year from current title if needed
            year = re.findall(year_pattern, t)

            # if title matches test w/ year included or year excluded
            if title_words == test_words or (year != [] and title_words[:-1] == test_words):
                rtn.append(i)

            # CREATIVE MODE: if the title has the same words as a sublist, also add it
            # returning all movies containing the tokens in title as a sublist (i.e. consecutively and in the same order)

            elif (self.creative and len(test_tokens) > 0):
                start = 0
                while (test_tokens[0] in title_tokens[start:]):
                    # check everything lines up
                    found = True
                    index = start + title_tokens[start:].index(test_tokens[0])
                    next_start = index + 1
                    for token in test_tokens:
                        if title_tokens[index] == token:
                            index += 1
                        else:
                            found = False
                            break
                    if found:
                        rtn.append(i)
                        break
                    start = next_start

            # find alternate names of movies
            if self.creative:
                for title in alternate_titles:
                    if title == test_words and i not in rtn:
                        rtn.append(i)
                        break

        return rtn
    
    def extract_sentiment(self, preprocessed_input):
        str = preprocessed_input.lower()
        titles = self.extract_titles(str)

        # remove title words from sentiment analysis
        filtered = ""
        for title in titles:
            filtered = str.replace(title, "")
        
        # split string into tokens
        #tokens include punctuation, exclude whitespaces
        words = re.findall(r"[\w']+|[.,!?;]", filtered)


        # split on conjunctions indicating a contrast
        # take only the clause after the contrast word
        if "but" in words:
            words = words[words.index("but"):]
        elif "though" in words:
            # though is the first word, split on the comma
            # though I liked the start of "x", I hated the end
            # words = ["I", "hated", "the", "end"]
            if words.index("though") == 0 and "," in words:
                words = words[words.index(","):]
            
            # otherwise just split on though itself
            # I liked the start of "x" though the rest is terrible
            # words = ["though", "the", "rest", "is", "terrible"]
            else:
                if words.index("though") != len(words) - 1:
                    words = words[words.index("though"):]
        elif "although" in words and "," in words:
            if words.index("although") == 0:
                words = words[words.index(","):]
            else:
                if words.index("although") != len(words) - 1:
                    words = words[words.index("although"):]
        else:
            pass

        res = self.extract_sentiment_helper(words)

        return res


    def extract_sentiment_helper(self, words):
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

        map = {'pos': 1, 'neg': -1}

        word_sentiments = []

        negation = False
        negate_words = {"no", "not", "never", "none", "nobody"}
        punctuation = {".", ",", "!", "?", ";"}

        multiplier = 1
        intensifiers = {"absolutely", "absolute", "completely", "complete", "extremely", "extreme", "highly", "rather", "really", "so", "too", "totally", "total", "utterly", "utter", 
                        "very", "painfully", "!"}
        strong_pos = {"outstanding", "great", "excellent", "splendid", "astounding", "magnificent", "superb", 
                      "faboulous", "fantastic", "terrific", "amazing", "wonderful", "astonishing", "tremendous",
                      "incredible", "awesome", "perfect", "marvelous",
                      "loved", "adored"}
        strong_neg = {"pathetic", "appalling", "dreadful", "horrible", "horrific", "abhorrent", "horrid", "terrible", "atrocious", "abhorrent", "awful", "disgusting", "digraceful", "nasty", "miserable",
                      "hated", "abhorred", "despised", "detested", "loathed", "worst",
                      "agony", "misery", "torture", "suffer", "suffering",
                      "garbage", "trash", "mess"}

        # once encounter punctuation, negation = False
        for word in words:
            stemmed = p.stem(word)

            # negate all words after a negation word
            if word in negate_words or "n't" in word:
                negation = True
                continue
            # until the next punctuation mark
            if word in punctuation:
                negation = False
                continue
            if negation:
                word = "NOT_" + word
                stemmed = "NOT_" + stemmed
            
            # add a multiplier to next/prev if an intensifier word is present
            if word in intensifiers: 
                if word == '!' and len(word_sentiments) >= 2:
                    word_sentiments[-1] *= 2
                multiplier = 2
                continue
            # strong sentiment words multiplied by 2
            if word in strong_neg or word in strong_pos:
                multiplier = 2
            if word in self.sentiment:
                word_sentiments.append(multiplier * map[self.sentiment[word]])
                multiplier = 1
            elif stemmed in self.sentiment:
                word_sentiments.append(multiplier * map[self.sentiment[stemmed]])
                multiplier = 1
            else:
                word_sentiments.append(0)

            # account for pos-neg pairs and neg-pos pairs
            # "terribly good" [-1, 1] becomes [0, 1]
            # "outstandingly bad" [1, -1] becomes [0, -1]
            if len(word_sentiments) >= 2 and word_sentiments[-2] * word_sentiments[-1] < 0:
                word_sentiments[-2] = 0

        sentiment_count = Counter(word_sentiments)

        # no positive or negative sentiment words found
        if len(sentiment_count) == 1 and 0 in sentiment_count:
            return 0
        
        sum_sentiment = np.sum(word_sentiments)
        
        # more positive sentiment than negative
        if sum_sentiment > 0:
            # strong positive word present
            if 2 in sentiment_count:
                return 2
            return 1
        
        if sum_sentiment < 0:
            if -2 in sentiment_count:
                return -2
            return -1
        
        # if equal amount of positive and negative sentiment
        # decide sentiment based on whether there's a strong word present
        if -2 in sentiment_count:
            return -2
        if 2 in sentiment_count:
            return 2
        
        # if no strong words, use the sentiment of the last word
        if len(word_sentiments) > 0:
            for sentiment in word_sentiments.reverse():
                if sentiment != 0:
                    return sentiment
        
        return 0
    
    def split_clauses(self, words, split_on):
        # split on conjunctions indicating a contrast
        # take only the clause after the contrast word
        clauses = []

        # if split_on not in words:
        #     return [words]
        
        indices = list(np.where(np.array(words) == split_on)[0])

        for i in range(len(indices)):
            if i == 0:
                clauses.append(words[:indices[i]])
                if i == len(indices) - 1:
                    clauses.append(words[indices[i]:])
            elif i == len(indices) - 1:
                clauses.append(words[indices[i-1]: indices[i]])
                clauses.append(words[indices[i]:])
            else:
                clauses.append(words[indices[i-1]: indices[i]])
        return clauses


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

        str = preprocessed_input
        titles_capitalized = self.extract_titles(str)

        str = str.lower()
        titles = self.extract_titles(str)

        # remove title words from sentiment analysis
        for title in titles:
            str = str.replace(title, "<TITLE>")
        
        # split string into tokens
        # tokens include punctuation, exclude whitespaces
        words = re.findall(r"[\w']+|[.,!?;]|<TITLE>", str)

        if "but" in words:
            clauses = self.split_clauses(words, "but")
        elif "though" in words:
            # though is the first word, split on the comma
            # though I liked the start of "x", I hated the end
            # words = ["I", "hated", "the", "end"]
            if words.index("though") == 0 and "," in words:
                clauses = self.split_clauses(words, ",")
            
            # otherwise just split on though itself
            # I liked the start of "x" though the rest is terrible
            # words = ["though", "the", "rest", "is", "terrible"]
            else:
                if words.index("though") != len(words) - 1:
                    clauses = self.split_clauses(words, "though")
        elif "although" in words and "," in words:
            if words.index("although") == 0:
               clauses = self.split_clauses(words, ",")
            else:
                if words.index("although") != len(words) - 1:
                    clauses = self.split_clauses(words, "though")
        else:
            clauses = [words]

        sentiments = []
        titles_processed = 0

        for clause in clauses:
            title_count = Counter(clause)["<TITLE>"]
            res = self.extract_sentiment_helper(clause)

            # if a clause has zero sentiment and it follows a contrasting conjunction
            # assume its sentiment is the opposite of the previous clause
            if res == 0 and clause != clauses[0]:
                res = -1 * sentiments[-1][1]
            
            # movies in the same clause get the same sentiment
            for i in range(title_count):
                sentiments.append((titles_capitalized[titles_processed], res))
                titles_processed += 1
        return sentiments

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
        rtn = []
        stopwords = ['a', 'an', 'the']

        # starter mode
        year_pattern = r'(\([\d-]+\))'
        word_pattern = r'([\w]+)'

        # divide test into words and remove stopwords
        title = title.lower()  # REMOVE.LOWER() PREPROCESS IF NEEDED
        test_words = re.findall(word_pattern, title)
        test_words = [w for w in test_words if w not in stopwords]

        test_title = " ".join(test_words)

        for i in range(len(self.titles)):
            t = self.titles[i][0].lower()  # REMOVE.LOWER() PREPROCESS IF NEEDED

            # divide title into words and remove stopwords
            title_words = re.findall(word_pattern, t)
            title_words = [w for w in title_words if w not in stopwords]

            # subtract year from current title if needed
            year = re.findall(year_pattern, t)

            title_year = " ".join(title_words)
            title_no_year = title_year
            if year != []:
                title_no_year = " ".join(title_words[:-1])

            distance1 = self.calc_edit_distance(test_title, title_no_year)
            distance2 = self.calc_edit_distance(test_title, title_year)
            if distance1 == max_distance or distance2 == max_distance:
                rtn.append(i)
            if distance1 < max_distance or distance2 < max_distance:
                rtn = [i]
                max_distance = min(distance1, distance2)

        return rtn

    # helper function for find_movies_closest_to_title
    def calc_edit_distance(self, title1, title2):
        len1 = len(title1) + 1
        len2 = len(title2) + 1
        dp = [[-1 for j in range(len2)] for j in range(len1)]

        for i in range(len1):
            for j in range(len2):
                if i == 0:
                    dp[i][j] = j
                elif j == 0:
                    dp[i][j] = i
                else:
                    sub_weight = 2
                    if title1[i - 1] == title2[j - 1]:
                        sub_weight = 0
                    sub = dp[i - 1][j - 1] + sub_weight
                    rem = dp[i - 1][j] + 1
                    add = dp[i][j - 1] + 1
                    dp[i][j] = min(sub, min(rem, add))
        return dp[len1 - 1][len2 - 1]


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
        # we count the number of tokens that the clarification shares with the candidate for each
        # candidate, and at the end return the candidates with the max number of shared tokens
        #print(candidates)
        counts = []
        years = {}
        word_pattern = r'([\w]+)'
        year_pattern = r'\(([\d-]+)\)'
        stopwords = ['a', 'an', 'the', 'la', 'el', 'un', 'una', 'le', 'une']
        clarification_tokens = re.findall(word_pattern, clarification.lower())
        clarification_tokens = [t for t in clarification_tokens if t not in stopwords]
        for i in candidates:
            title = self.titles[i][0].lower()
            title_tokens = re.findall(word_pattern, title)
            title_tokens = [t for t in title_tokens if t not in stopwords]
            year = re.findall(year_pattern, title)
            if (year != []):
                if year[0] not in years:
                    years[year[0]] = []
                years[year[0]].append(i)
            #print(title_tokens)
            # count how many tokens in common
            c = 0
            for token in clarification_tokens:
                if token in title_tokens:
                    c += 1
            counts.append(c)
        if (len(years.keys()) > 0):
            if ("newest" in clarification or "most recent" in clarification):
                return years[max(years.keys())]
            if ("oldest" in clarification):
                return years[min(years.keys())]
        #print(counts)
        max_count = max(counts)
        min_count = min(counts)
        ret = []

        if (max_count == min_count):
            try:
                i = int(clarification)
                if (i > 0):
                    return [candidates[i - 1]]
            except:
                pass

        # if the max and min are the same, maybe the user was saying something about the movie that was not related
        # to the title, such as its ordering or its age
        #print(self.titles[524][0])
        #print(self.titles[5743][0])
        if (True):
            if ("first" in clarification and len(candidates) > 0):
                ret.append(candidates[0])
                return ret
            elif ("second" in clarification and len(candidates) > 1):
                ret.append(candidates[1])
                return ret
            elif ("third" in clarification and len(candidates) > 2):
                ret.append(candidates[2])
                return ret
            elif ("fourth" in clarification and len(candidates) > 3):
                ret.append(candidates[3])
                return ret

        if (max_count == 0):
            ret = []
        elif (max_count == min_count):
            ret = candidates

        if (max_count != min_count):
            for i in range(len(candidates)):
                if counts[i] == max_count:
                    ret.append(candidates[i])
        return ret

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
        binarized_ratings = np.where((ratings <= threshold) & (ratings > 0), -1, ratings)
        binarized_ratings = np.where(binarized_ratings > 2.5, 1, binarized_ratings)

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
        similarity = np.dot(u, v)
        similarity /= np.linalg.norm(u)
        similarity /= np.linalg.norm(v)
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

        # get the indices of the movies the user has rated
        # get the indices of the movies the user has rated
        rated = []
        for i in range(len(user_ratings)):
            if user_ratings[i] != 0:
                rated.append(i);

        scores = []
        for potential_movie_index in range(ratings_matrix.shape[0]):
            if (sum(ratings_matrix[potential_movie_index]) == 0 or potential_movie_index in rated):
                scores.append(-100)
                continue;

            score = 0
            for rated_movie_index in rated:
                score += user_ratings[rated_movie_index] * self.similarity(ratings_matrix[rated_movie_index],
                                                                           ratings_matrix[potential_movie_index])
            scores.append(score)

        movies_sorted = [m for _, m in sorted(zip(scores, [i for i in range(ratings_matrix.shape[0])]), reverse=True)]

        # Populate this list with k movie indices to recommend to the user.
        recommendations = movies_sorted[:k]

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
        Ahoy mate, I am a pirate-themed chat bot. Tell me about yer movie taste, and I'll give you some recs.
        Stay on topic though, or walk the plank.
        Arrrrrr
        """


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
