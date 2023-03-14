# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util
import random
import numpy as np

import re

import string

import porter_stemmer



# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'Filmy'
        if creative:
            self.name = 'Yoda'
            
        self.creative = creative

        self.p = porter_stemmer.PorterStemmer()

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')
        self.sentiment = {self.p.stem(word): score for word, score in self.sentiment.items()}
        ########################################################################
        # TODO: Binarize the movie ratings matrix.                             #
        ########################################################################

        # Binarize the movie ratings before storing the binarized matrix.
        self.ratings = self.binarize(ratings)
        self.user_ratings = np.zeros(9125)
        self.movie_counter = 0
        self.rec_count = 0


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
        greeting_message = "Hi there! My name is Filmy. I'm a movie fanatic. Let's talk movies! Tell me about a movie you watched recently :)"
        if self.creative:
            greeting_message = "Yoda, I am. Talk about movies, we shall, young Padawan."
        

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

        goodbye_message = "Have a nice day! I hope we meet again :)"
        if self.creative: 
            goodbye_message = "May the Force be with you."
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
        if self.movie_counter == 5:
            if line.lower() == "yes" or line.lower() == "no":
                response = self.give_recs(line)

        if self.creative:
            titles = self.extract_titles(line)
            movie_matches = []
            movie_sentiment = self.extract_sentiment(self.preprocess(line))
            response = ""
            if titles and len(titles) == 1: 
                movie_matches = self.find_movies_by_title(titles[0])
                if (len(movie_matches) > 1):
                    response = "\"{}\", there is more than one. Of these, the one you seek, you must tell?\n".format(titles[0])
                elif len(movie_matches) == 0:
                    response = "\"{}\", I do not know. Another movie you liked, tell me you must.\n".format(titles[0])
                elif len(movie_matches) == 1 and movie_sentiment != 0:
                    index = movie_matches[0]
                    if movie_sentiment > 0:
                        self.user_ratings[index] = 1
                        self.movie_counter += 1
                        responseOptions = ["Liked \"{}\", have you? Other movies, you must name\n".format(titles[0]),
                        "\"{}\", enjoyed you have? More movies you enjoyed, tell me you must.\n".format(titles[0]),
                        "Young Padawan, fond of \"{}\", I am. More about movies you enjoyed, I must know.\n".format(titles[0])]
                        if self.movie_counter == 5:
                            response = self.give_recs(line)
                        else: 
                            response = random.choice(responseOptions)
                    elif movie_sentiment < 0:
                        self.user_ratings[index] = -1
                        self.movie_counter += 1
                        responseOptions = ["Not liked \"{}\", you have! A movie you liked, now you must tell.\n".format(titles[0]),
                        "Your dislike for \"{}\", see I! Tell me about a different movie, you must.\n".format(titles[0]), 
                        "Heard that about \"{}\", I have. About another movie you liked or disliked, you must tell.\n".format(titles[0])]
                        if self.movie_counter == 5:
                            response = self.give_recs(line)
                        else:
                            response = random.choice(responseOptions)
                    else: 
                        responseOptions = [
                            "Of your like or dislike for \"{}\", I am uncertain. More about it, you must tell.\n".format(titles[0]),
                            "\"{}\"? More of your thoughts on this movie, know I must.\n.".format(titles[0]),
                            "More about \"{}\", you must tell. Know more I must, before recommendations I give.\n".format(titles[0])
                        ]
                        response = random.choice(responseOptions)
        
            elif titles and len(titles) > 1:
                responseOptions = [
                    "Patience is the fuit of life. Slow down, you must. One movie only, must you tell me about.\n",
                    "A Jedi talks of only one movie at a time.\n",
                    "Your passion for movies, I appreciate. But talk only of one, you must.\n",
                ]
                        
            else:
                if self.movie_counter != 5:
                    if line.lower() != "no":
                        response = self.arb_input_handler(line)
                else: 
                    response = self.give_recs(line)

            
        else:
            #response = "I processed {} in starter mode!!".format(line)
            titles = self.extract_titles(line)
            movie_matches = []
            movie_sentiment = self.extract_sentiment(self.preprocess(line))
            response = ""
            if titles and len(titles) == 1: 
                movie_matches = self.find_movies_by_title(titles[0])
                if (len(movie_matches) > 1):
                    response = "I found more than one movie called \"{}\". Can you clarify?\n".format(titles[0])
                elif len(movie_matches) == 0:
                    response = "Sorry, I've never heard of \"{}\"...Tell me another movie you liked\n".format(titles[0])
                elif len(movie_matches) == 1 and movie_sentiment != 0:
                    index = movie_matches[0]
                    if movie_sentiment > 0:
                        self.user_ratings[index] = 1
                        self.movie_counter += 1
                        responseOptions = ["Ooh, I see that you liked \"{}\"! What other movie have you liked?\n".format(titles[0]),
                        "Oh, you liked \"{}\"? Tell me about another movie that you've watched.\n".format(titles[0]),
                        "Oh, you liked \"{}\"? I've heard great things about that movie! Have you watched another movie recently?\n".format(titles[0])]
                        if self.movie_counter == 5:
                            response = self.give_recs(line)
                        else: 
                            response = random.choice(responseOptions)
                    elif movie_sentiment < 0:
                        self.user_ratings[index] = -1
                        self.movie_counter += 1
                        responseOptions = ["Okay! I see that you didn't like \"{}\"! Tell me about a movie you liked.\n".format(titles[0]),
                        "Mm, I see that you didn't like \"{}\"! Tell me about another movie you've watched.\n".format(titles[0]), 
                        "Oh, I've heard that about \"{}\"! I'm sorry you didn't like it. Tell me about another movie you liked or disliked.\n".format(titles[0])]
                        if self.movie_counter == 5:
                            response = self.give_recs(line)
                        else:
                            response = random.choice(responseOptions)
                    else: 
                        responseOptions = [
                            "Sorry, I'm not sure if you liked \"{}\". Tell me more about it.\n".format(titles[0]),
                            "I'm not really sure how you feel about \"{}\". I'd love to hear more of your thoughts about it!\n.".format(titles[0]),
                            "Could you tell me more about \"{}\". I wanna make sure I really understand how you feel about this movie.\n".format(titles[0])
                        ]
                        response = random.choice(responseOptions)
        
            elif titles and len(titles) > 1:
                responseOptions = [
                    "Sorry I might need us to slow down a little. Could you tell me about one movie at a time instead?\n",
                    "Sorry I think I lost my focus. Let's talk about one movie at a time.\n",
                    "Woah, I love that you want to talk about multiple movies. Let's talk about one movie at a time so I can learn about how you feel about them.\n",
                ]
                        
            else:
                if self.movie_counter != 5:
                    if line.lower() != "no":
                        responseOptions = ["Okay got it! Could we talk about movies though? I'm really passionate about them. Tell me about a some movies you've seen recently and I might be able to recommend some!\n",
                        "Hmm... I think we should talk about movies you like instead.\n", 
                        "Sorry, I don't know much about that. Could we focus on movies instead? Tell me about a movie you've watched recently.\n",
                        "Sorry I didn't catch that! Could you tell me about a movie you liked?\n"]
                        response = random.choice(responseOptions)
                else: 
                    response = self.give_recs(line)
            #mode = "I processed {} in starter mode!! \n".format(line)  
            #titles = "I found the following movie titles: {}. \n".format(titles)
            #movie_match = "These are indexes: {}".format(movie_matches)
            #response = mode + titles + movie_match


        
        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return response

    def arb_input_handler(self, line):
        other = ["Hmm... Movies you like, tell me instead, young Padawan.", "Patience you must have, young Padawan. Catch that, I did not. Me, a liked movie you must tell.", ]
        response = random.choice(other)
        option = {}
        option["what"] = ["In what you seek, the answer lies not in.", "Ask not what. Movies you like, must you tell instead."]
        option["what's"] = ["In what you seek, the answer lies not in.", "Ask not what. Movies you like, must you tell instead."]
        option["why"] = ["Not ask why, let us. On track, let's stay.", "Why not, young Padawan?"]
        option["who"] = ["Who, I know not.", "Tell you who, I shall. Movie you like first I must know, before reveal I shall."]
        option["who's"] = ["Who's, I know not.", "Tell you who, I shall. Movie you like first I know, before reveal I shall."]
        option["how"] = ["Hm. 'How's' not make one great.", "Know not, I how.", "Movie you like first I know, before think how, I shall. "]
        option["can"] = ["Know if one can, I do not.", "Know if I can, I do not.", "Think if one can, let me. Movie you like, first I must know."]
        option["did"] = ["Know not I, did it?", "It did not, thinks I."]
        option["are"] = ["Know if they are, I do not.", "Are you, young Padawan?"]
        option["aren't"] = ["Know if they are, I do not.", "Aren't you, young Padawan?"]
        option["is"] = ["Yes, but guarantee correctness, I cannot.", "No, but guarantee correctness, I cannot."]
        option["I'm"] = ["That you are, young Padawan. But talk about movies, we must."]
        option["hi"] = ["Greetings, young Padawan. Talk about movies, we must."]
        option["hello"] = ["Greetings, young Padawan. Talk about movies, we must."]
        option["hey"] = ["Greetings, young Padawan. Talk about movies, we must."]
        words = line.split()
        first_word = words[0].lower()
        res = re.sub(r'[^\w\s]', '', line)
        words_no_punc = res.split()
        first_word_no_punc = words_no_punc[0].lower()
        if first_word in option.keys():
            responseOptions = option[first_word]
            response = random.choice(responseOptions)
        if first_word_no_punc in option.keys():
            responseOptions = option[first_word_no_punc]
            response = random.choice(responseOptions)

        return response

    def emotion_response(self, emotion):
        emotions = {}
        default = "Understand not, did I. Movie you like, tell you must."
        # happy, sad, disgust
        emotions["sad"] = ["Part of life, sadness is.", "Not let sadness consume, you must. Faith in you, I have."]
        emotions["defeat"] = ["If no mistake have you made, yet losing you are, a different game you should play."]
        emotions["happy"] = ["Happy you are, happy I am.", "Grateful for your happiness, I am, young Padawan."]
        emotions["angry"] = ["Once you start down the dark path, forever will it dominate your destiny. Consume you, it will.", "Solution to anything, anger is not."]
        emotions["afraid"] = ["Fear is the path to the dark side. Fear leads to anger. Anger leads to hate. Hate leads to suffering.", "A challenge lifelong it is, not to bend fear into anger."]
        emotions["scared"] = ["Fear is the path to the dark side. Fear leads to anger. Anger leads to hate. Hate leads to suffering.", "A challenge lifelong it is, not to bend fear into anger."]
        emotions["disgusted"] = ["Feel disgust, I do too.", ]
        emotions["amusement"] = ["Ha ha ha, young Padawan."]
        emotions["jealous"] = ["Attachment leads to jealousy. Jealous, do not be.", "Jealousy, a true Padawan does not feel. The shadow of greed, that is."]
        emotions["awe"] = ["Glad I am, that awe is inspired."]
        emotions["lonely"] = ["The path of the Jedi is a lonely one."]
        emotions["excited"] = ["Adventure. Excitement. A Jedi craves not these things."]
        emotions["miserable"] = ["Hope you feel less miserable, I do."]
        emotions["worried"] = ["Let worry not cloud your mind. Clear minded, you must stay."]
        emotions["nervous"] = ["Let nerves not cloud your mind. Clear minded, you must stay."]
        emotions["annoyed"] = ["Share your annoyance, I do."]
        emotions["bored"] = ["Empty mind, you must fill."]
        if emotion == "" or emotion not in emotions:
            return default
        else:
            return random.choice(emotions[emotion])

    def give_recs(self, line):
        response = ""
        lineArr = line.split()
        recs = self.recommend(self.user_ratings, self.ratings)
        movie_names = []
        for rec in recs:
            movie_names.append(self.titles[rec][0])
        if self.rec_count == len(recs):
            response = "I'm sorry, I can't think of any more! Instead, tell me about different movies you like!"
            if self.creative:
                response = "My limits, I have reached! Think of more, I cannot! Tell me about different movies, you must."
            self.rec_count = 0
            self.movie_counter = 0
        elif self.rec_count == 0:
            responseOptions = ["Given what you told me, I think you'd like \"{}\". Would you like more recommendations?\n".format(movie_names[self.rec_count]), "Thanks for tell me about these movies. I think you'd like \"{}\". Would you like more recommendations?\n".format(movie_names[self.rec_count])]
            if self.creative:
                responseOptions = ["The Force believes like \"{}\", you will. Like more recommendations, would you?\n".format(movie_names[self.rec_count]), "Hearing of these, grateful I am. \"{}\", I think you would like. Want more recommendations, yes?\n".format(movie_names[self.rec_count])]
            response = random.choice(responseOptions)
            self.rec_count += 1
        else:
            if "yes" in lineArr:
                responseOptions = ["I would also recommend \"{}\". How about another one?\n".format(movie_names[self.rec_count]),
                "I think you'd enjoy \"{}\". Shall I suggest another one?\n".format(movie_names[self.rec_count])]
                if self.creative: 
                    responseOptions = ["Also recommend \"{}\", I would. Another one, you would like, yes?\n".format(movie_names[self.rec_count]),
                    "Enjoy \"{}\", I think you would. Pass on what you have learned. Like more, would you?\n".format(movie_names[self.rec_count])]
                self.rec_count += 1
                response = random.choice(responseOptions)
            elif "no" in lineArr:
                response = "Alright then, tell me your thoughts on some more movies."
                if self.creative:
                    response = "Different things you want, I see. More about your thoughts on other movies, know I must."
                self.rec_count = 0
                self.movie_counter = 0
            elif "yes" not in lineArr and "no" not in lineArr:
                responseOptions = ["Catch that, I did not. Said you 'yes' or 'no', young Padawan?"]
                response = random.choice(responseOptions)
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

          potential_titles = chatbot.extract_titles(chatbot.preprocess(
                                            'I liked The NoTeBoOk!'))
          print(potential_titles) // prints ["The NoTeBoOk"]

          potential_titles = chatbot.extract_titles(chatbot.preprocess(
                                            'I thought 10 things i hate about you was great'))
          print(potential_titles) // prints ["10 things i hate about you"]

        :param preprocessed_input: a user-supplied line of text that has been
        pre-processed with preprocess()
        :returns: list of movie titles that are potentially in the text
        """
        pattern = r'"(.+?)"'
        title_list = re.findall(pattern, preprocessed_input)
        if not title_list:
            end_words = ["is", "was"]
            start_words = ["thought", "liked", "saw", "think", "like", "enjoyed"]
            movie_title = ""
            for word in preprocessed_input.split():
                if word in end_words:
                    break
                movie_title = movie_title + word.strip(string.punctuation) + " "
                if word in start_words:
                    movie_title = ""
            if (movie_title[0].isupper() or (not movie_title[0].isalpha())) and movie_title[:-1] != preprocessed_input[:-1]:
                title_list.append(movie_title[:-1])
        return title_list
    
    def incorrect_capitalization(self, regex1, regex2, curr_title): 
        if re.search(regex1.lower(), curr_title.lower()) or (regex2 and re.search(regex2.lower(), curr_title.lower())): 
            return True
        else:
             return False

    def foreign_language(self, raw_title, year, curr_title): 
        regex1 = r'.+? \((?:a.k.a. |aka |AKA |A.K.A. )?' + raw_title + r'\)'
        if year: 
            regex1 = regex1 + ' ' + year + r'$' 
        else: 
            regex1 = regex1 + r'(?: \([0-9]{4}\))?$' 

        if re.search(regex1, curr_title):  
                return True

        articles = r"^(El|Los|La|Las|Le|L'|Les|O|Il|Gli|I|Der|Die|Das) (.*)$"

        art_search = re.search(articles, raw_title)
        regex2 = ''
        if art_search: 
            regex2 = r'.+? \((?:a.k.a. |aka |AKA |A.K.A. )?' + art_search.group(2) + ', ' + art_search.group(1) + r'\)'
        if regex2:
            if year:  
                regex2 = r'^' + regex2 + ' ' + year + r'$'
            else: 
                regex2 = r'^' + regex2 + r'(?: \([0-9]{4}\))?$'
            if re.search(regex2, curr_title): 
                return True

        return False

    def ambiguous(self, title, curr_title, index): 
        regex = r"^(?:.*\b)?" + title + r"(?:\b.*)?$"

        if re.search(regex, curr_title): 
            return True
        

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
        idx_matches = []

        #Figure out if there is a year included in the search
        og_title = title
        year = ''
        year_regex = r'^(.*?)( \([0-9]{4}\))?$'
        year_found = re.search(year_regex, title)
        title = year_found.group(1)

        regex_title1 = ""
        if year_found.group(2): 
            year = r'\(' +year_found.group(2)[2:-1] + r'\)'
            regex_title1 = r'^' + title + ' ' + year + r'$' 
        else: 
            regex_title1 = r'^' + title  + r'(?: \([0-9]{4}\))?$' 


        
        #Figure out if there is an article at the start
        articles = r'^(A|An|The) (.*)$'
        art_search = re.search(articles, title)
        regex_title2 = ''
        if art_search: 
            regex_title2 = art_search.group(2) + ', ' + art_search.group(1)
        if regex_title2:
            if year:  
                regex_title2 = r'^' + regex_title2 + ' ' + year + r'$'
            else: 
                regex_title2 = r'^' + regex_title2 + r'(?: \([0-9]{4}\))?$'
       
        for index, curr_movie in enumerate(self.titles):
            curr_title = curr_movie[0]
            
            if re.search(regex_title1, curr_title):  
                idx_matches.append(index)
        
            if regex_title2 and re.search(regex_title2, curr_title): 
                idx_matches.append(index)

            if self.creative and index not in idx_matches: 
                if self.incorrect_capitalization(regex_title1, regex_title2, curr_title): 
                    idx_matches.append(index)
                
                elif self.foreign_language(title, year, curr_title): 
                    idx_matches.append(index)

                elif self.ambiguous(og_title, curr_title, index): 
                    idx_matches.append(index)

                
                

        #  if there are multiple matches for the given movie title, it will call disambiguate on a list of movie titles to get the index of the chosen movie
        # if len(idx_matches) > 1:
        #     movie_titles = [self.titles[i][0] for i in idx_matches]
        #     idx = self.disambiguate(movie_titles)
        #
        #     return [idx_matches[idx]]
       
        return idx_matches


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
        #words = preprocessed_input.split()
        negation_words = ["not", "no", "cannot", "never", "neither", "nor", "barely", "hardly", "scarcely", "seldom", "rarely", "nothing", "none", 'nobody', "nowhere", "impossible"]
        super_words = ["really", "very", "extremely", "totally", "especiallly", "particularly", "seriously", "most", "absolutely"]
        super_neg_words = ["terrible", "horrible", "awful", "abysmal", "horrendous", "atrocious", "appalling", "dreadful", "deplorable", "disgusting", "offensive", "objectionable", "repulsive", "repugnant", "revolting", "sickening"]
        super_pos_words = ["amazing", "fantastic", "wonderful", "acclaimed", "legendary", "awesome", "brilliant", "beautiful", "exciting", "energized", "enchanting", "genius", "heavenly", "innovative", "love", "lovely", "loved", "masterful", "marvelous", "meritorious", "phenomenal", "perfect", "powerful", "stunning", "thrilling", "wondrous"]
        suffix = ["ed", "est", "ing", "tion"]
        #split words and punctuation using regex
        input_no_title = re.sub(r'"(.+?)"', '', preprocessed_input)
        regex = r"([\w']+|[^\w' ])"
        split_string = re.findall(regex, input_no_title)
        #need to check if n't is in word 

        polarity = 0
        negated = False
        super = False
        super_neg = False
        super_pos = False
        for i, word in enumerate(split_string):
            
            if word.lower() in super_neg_words:
                super_neg = True
            elif word.lower() in super_pos_words:
                super_pos = True
        
            #print(word)
            sentiment = None
            if word.lower() in negation_words or re.search(r"n't", word.lower()): 
                negated = True
            elif word.lower() in super_words:
                super = True
            elif re.search(r"[^\w']", word): 
                negated = False
            elif word.lower() in self.sentiment:
                sentiment = 1 if self.sentiment[word.lower()] == 'pos' else -1
            elif self.p.stem(word.lower()) in self.sentiment: 
                sentiment = 1 if self.sentiment[self.p.stem(word.lower())] == 'pos' else -1
            else:
                sentiment = 0
        
            if sentiment: 
                if negated:
                    polarity -= sentiment

                else:
                    polarity += sentiment

        if polarity > 0:
            return 2 if (super or super_pos) else 1
        
        elif polarity < 0:
            return -2 if (super or super_neg) else -1
        
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
        titles = self.extract_titles(preprocessed_input)
        sentiments = []
        same_sentiment = ["and", "both", "or"]
        opp_sentiment = ["but", "except"]

        for word in same_sentiment:
            if re.search(word, preprocessed_input.lower()):
                movie_sentiment = self.extract_sentiment(preprocessed_input)
                for title in titles:
                    sentiments.append((title, movie_sentiment))
                return sentiments
                
        for word in opp_sentiment:
            if re.search(word, preprocessed_input.lower()):
                movie_sentiment = self.extract_sentiment(preprocessed_input)
                if movie_sentiment != 0:
                    sentiments.append((titles[0], movie_sentiment))
                    for title in titles[1:]:
                        sentiments.append((title, -1 * movie_sentiment))
                else:
                    sptr = ", " + word
                    parts = preprocessed_input.split(sptr)
                    i = 0
                    for title in titles:
                        movie_sentiment = self.extract_sentiment(parts[i])
                        sentiments.append((title, movie_sentiment)) 
                        i += 1
                return sentiments
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

        closest_movies = {}
        min_key = max_distance
        year = ''
        year_regex = r'^(.*?)( \([0-9]{4}\))?$'
        for index, curr_movie in enumerate(self.titles):
            movie_name = curr_movie[0]
            #print(movie_name)
            year_found = re.search(year_regex, movie_name)
            movie_name = year_found.group(1)
            #print(movie_name)
            rows = len(title) + 1
            cols = len(movie_name) + 1
            dist = [[0 for x in range(cols)] for x in range(rows)]
            for i in range(1, rows):
                dist[i][0] = i
            for i in range(1, cols):
                dist[0][i] = i
            
            for col in range(1, cols):
                for row in range(1, rows):
                    if title[row-1].lower() == movie_name[col-1].lower():
                        cost = 0
                    else:
                        cost = 1
                    dist[row][col] = min(dist[row-1][col] + 1,      # deletion
                                 dist[row][col-1] + 1,      # insertion
                                 dist[row-1][col-1] + cost) # substitution
            distance = dist[row][col]
            if distance <= max_distance:
                if distance not in closest_movies:
                     closest_movies[distance] = []
                closest_movies[distance].append(index)
                if distance < min_key:
                    min_key = distance

        if not closest_movies:
            return []
        else:
            return closest_movies[min_key]

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
        result = []

        newest = ["most recent", "newest", "recent one", "new"]
        oldest = ["least recent", "oldest", "old one", "old"]


        if clarification.isdigit() and int(clarification) <= len(candidates): 
            return [candidates[int(clarification) - 1]]


        if clarification.lower() in newest or clarification.lower() in oldest: 
            years = np.array([])
            for index in candidates: 

                title = self.titles[index][0]
                regex = r'^(.*?)( \([0-9]{4}\))?$'
                temp = re.search(regex, title)
                year = int(temp.group(2)[2:-1])
                years = np.append(years, year)

            indexes = np.argsort(years)

            if clarification.lower() in newest: 
                return [candidates[indexes[-1]]]

            else: 
                return [candidates[indexes[0]]]

        the_blank_one = re.search('(?:the )?(.*) one', clarification)
        numeric = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth', 'last', 'second to last']
        if the_blank_one: 
            if the_blank_one.group(1).lower() in numeric:

                number = [i for i, number in enumerate(numeric) if the_blank_one.group(1) == number][0]
                if number <= 9: 

                    return [candidates[number]]
                if number == 10: 
                    return [candidates[-1]]
                if number == 11: 
                    return [candidates[-2]]
            else: 
                res = []
                for index in candidates: 
                    title = self.titles[index][0]
                    if re.search(the_blank_one.group(1), title):
                        res.append(index)
                return res


        for index in candidates:

            title = self.titles[index][0]
            regex = r'^(.*?)( \([0-9]{4}\))?$'
            temp = re.search(regex, title)
            title_stripped = temp.group(1)
            year = temp.group(2)


            if re.search(r'^[0-9]{4}$', clarification) and year: 
                if re.search(clarification, year): 
                    result.append(index)
                    continue

            if re.search(clarification, title_stripped):
                result.append(index)
                continue

        return result

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
        #binarized_ratings = np.zeros_like(ratings)
        binarized_ratings = np.where((ratings <= threshold) & (ratings > 0), -1, ratings)
        binarized_ratings = np.where(binarized_ratings > threshold, 1, binarized_ratings)
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
        if np.linalg.norm(u) != 0 and np.linalg.norm(v) != 0:
            similarity = (np.matmul(u, v))/(np.linalg.norm(u) * np.linalg.norm(v))
        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return similarity


    def predicted_weight(self, rated, ratings_matrix, user_ratings, i):
        j = rated[0]
        r_xj = user_ratings[j]
        row_j = ratings_matrix[j]
        row_i = ratings_matrix[i]
        s_ij = self.similarity(row_i, row_j)
        return s_ij * r_xj


    def predicted_ratings(self, not_rated, rated, ratings_matrix, user_ratings): 
        i = not_rated[0]
        weight = np.apply_along_axis(self.predicted_weight, axis=0, arr=np.array([rated]), ratings_matrix=ratings_matrix, user_ratings=user_ratings, i=i)
        return np.sum(weight)


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
        sim_dict = {}
        
        #figure out which movies have been rated and not rated
        rated = np.nonzero(user_ratings)
        not_rated = np.nonzero(user_ratings == 0)[0]
        #calculate predicted rating for every movie not rated
        predicted_values = np.apply_along_axis(self.predicted_ratings, axis=0, arr=np.array([not_rated]), rated=rated, ratings_matrix=ratings_matrix, user_ratings=user_ratings)
        sorted_index = np.argsort(-predicted_values)
        recs = [not_rated[x] for x in sorted_index]




        ########################################################################
        #                        END OF YOUR CODE                              #
        ########################################################################
        return recs[:k]

    ############################################################################
    # 4. Debug info                                                            #
    ############################################################################

    def debug(self, line):
        """
        Return debug information as a string for the line string from the REPL

        NOTE: Pass the debug information that you may think is important for
        your evaluators.
        """
        debug_info = self.p.stem("enjoyed")
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
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⣤⠤⠐⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡌⡦⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⣼⡊⢀⠔⠀⠀⣄⠤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⣤⣄⣀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣶⠃⠉⠡⡠⠤⠊⠀⠠⣀⣀⡠⠔⠒⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⣿⢟⠿⠛⠛⠁
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⡇⠀⠀⠀⠀⠑⠶⠖⠊⠁⠀⠀⠀⡀⠀⠀⠀⢀⣠⣤⣤⡀⠀⠀⠀⠀⠀⢀⣠⣤⣶⣿⣿⠟⡱⠁⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣾⣿⡇⠀⢀⡠⠀⠀⠀⠈⠑⢦⣄⣀⣀⣽⣦⣤⣾⣿⠿⠿⠿⣿⡆⠀⠀⢀⠺⣿⣿⣿⣿⡿⠁⡰⠁⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⣿⣿⣧⣠⠊⣠⣶⣾⣿⣿⣶⣶⣿⣿⠿⠛⢿⣿⣫⢕⡠⢥⣈⠀⠙⠀⠰⣷⣿⣿⣿⡿⠋⢀⠜⠁⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⢿⣿⣿⣿⣿⣰⣿⣿⠿⣛⡛⢛⣿⣿⣟⢅⠀⠀⢿⣿⠕⢺⣿⡇⠩⠓⠂⢀⠛⠛⠋⢁⣠⠞⠁⠀⠀⠀⠀⠀⠀⠀⠀
⠘⢶⡶⢶⣶⣦⣤⣤⣤⣤⣤⣀⣀⣀⣀⡀⠀⠘⣿⣿⣿⠟⠁⡡⣒⣬⢭⢠⠝⢿⡡⠂⠀⠈⠻⣯⣖⣒⣺⡭⠂⢀⠈⣶⣶⣾⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠙⠳⣌⡛⢿⣿⣿⣿⣿⣿⣿⣿⣿⣻⣵⣨⣿⣿⡏⢀⠪⠎⠙⠿⣋⠴⡃⢸⣷⣤⣶⡾⠋⠈⠻⣶⣶⣶⣷⣶⣷⣿⣟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠈⠛⢦⣌⡙⠛⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡀⠀⠀⠩⠭⡭⠴⠊⢀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⣿⣿⣿⣿⡇⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠈⠙⠓⠦⣄⡉⠛⠛⠻⢿⣿⣿⣿⣷⡀⠀⠀⠀⠀⢀⣰⠋⠀⠀⠀⠀⠀⣀⣰⠤⣳⣿⣿⣿⣿⣟⠑⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠓⠒⠒⠶⢺⣿⣿⣿⣿⣦⣄⣀⣴⣿⣯⣤⣔⠒⠚⣒⣉⣉⣴⣾⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠛⠹⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣭⣉⣉⣤⣿⣿⣿⣿⣿⣿⡿⢀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠟⡁⡆⠙⢶⣀⠀⢀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣴⣶⣾⣿⣟⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⢛⣩⣴⣿⠇⡇⠸⡆⠙⢷⣄⠻⣿⣦⡄⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣼⣿⣿⣿⣿⣿⣿⣿⣎⢻⣿⣿⣿⣿⣿⣿⣿⣭⣭⣭⣵⣶⣾⣿⣿⣿⠟⢰⢣⠀⠈⠀⠀⠙⢷⡎⠙⣿⣦⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣼⣿⣿⣿⣿⣿⣿⣿⣿⡟⣿⡆⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠿⠟⠛⠋⠁⢀⠇⢸⡇⠀⠀⠀⠀⠈⠁⠀⢸⣿⡆⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡜⡿⡘⣿⣿⣿⣿⣿⣶⣶⣤⣤⣤⣤⣤⣤⣤⣴⡎⠖⢹⡇⠀⠀⠀⠀⠀⠀⠀⠀⣿⣷⡄⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⡀⠘⢿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠿⠛⠋⡟⠀⠀⣸⣷⣀⣤⣀⣀⣀⣤⣤⣾⣿⣿⣿⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣭⣓⡲⠬⢭⣙⡛⠿⣿⣿⣶⣦⣀⠀⡜⠀⠀⣰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣭⣛⣓⠶⠦⠥⣀⠙⠋⠉⠉⠻⣄⣀⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣶⣆⠐⣦⣠⣷⠊⠁⠀⠀⡭⠙⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡆⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⢉⣛⡛⢻⡗⠂⠀⢀⣷⣄⠈⢆⠉⠙⠻⢿⣿⣿⣿⣿⣿⠇⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠘⣿⣿⡟⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⣉⢁⣴⣿⣿⣿⣾⡇⢀⣀⣼⡿⣿⣷⡌⢻⣦⡀⠀⠈⠙⠛⠿⠏⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠙⢿⣿⡄⠙⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠛⠛⠛⢯⡉⠉⠉⠉⠉⠛⢼⣿⠿⠿⠦⡙⣿⡆⢹⣷⣤⡀⠀⠀⠀⠀⠀⠀⠀
   
        This chatbot emulates Yoda's speech patterns and is designed to help users find movies based on their preferences. 
        The chatbot can handle a variety of user inputs, including movie titles, genres, and plot keywords and uses the information to generate appropriate responses and provide relevant recommendations.

        The chatbot can also handle ambiguous movie titles. 
        If a user mentions a movie title that has multiple versions or remakes, the chatbot asks for clarification and uses this additional information to narrow down the search results.
        """


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
