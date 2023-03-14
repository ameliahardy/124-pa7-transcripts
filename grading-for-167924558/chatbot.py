# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util

import numpy as np
from porter_stemmer import PorterStemmer # used Jennifer He's Ed post
from deps.word_tokenize import word_tokenize
from deps.emotions import is_negative_emotion, is_positive_emotion
import re

# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        self.creative = creative

        self.name = 'bootybot' if self.creative else 'busterbot'

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')
        self.user_ratings = np.zeros(ratings.shape[0])
        self.rec_ptr = 0
        self.disambiguation_candidates = []
        self.spelling_candidates = []
        self.stored_sentiment = 0
        self.spell_check_flag = False
        self.recommendations = []

        if not self.creative:
            self.no_potential_titles_responses = [
                "I'm sorry, did you mention a movie?",
                "I don't know if you gave me a movie, could you try again please?",
                "Hmm...I couldn't catch if you said something about a movie."
            ]

            self.no_movie_match_responses = [
                "I'm sorry, I haven't heard of the movie \"{}\" before. Could you try again?",
                "Hmm...I don't think the movie \"{}\" is out yet for me. Do you have another?",
                "I can't find any movies with the name \"{}\". Please try again."
            ]

            self.no_sentiment_responses = [
                "I couldn't tell if you liked \"{}\". Can you clarify?",
                "What's your opinion on \"{}\"?",
                "I don't know how you feel about \"{}\". Could you tell me more?"
            ]

            self.multiple_matches_responses = [
                "I found more than one movie with the title \"{}\". Could you clarify?",
                "There are so many versions of \"{}\"! Which one are you referring to?",
                "I can't narrow down the version of \"{}\" you're talking about. Can you specify further?"
            ]

            self.multiple_movies_responses = [
                "That's a lot of movies, can you tell me one at a time?",
                "Information overload! I'm going to need you to tell me about just one movie.",
                "Whoa there, champ! Can you go one at a time?"
            ]

            self.positive_sentiment_responses = [
                "Okay, so you liked \"{}\".",
                "I'm so glad you enjoyed \"{}\"!",
                "Wahoo! \"{}\" is a great movie."
            ]

            self.negative_sentiment_responses = [
                "I'm sorry you didn't have a good experience with \"{}\".",
                "Womp womp....\"{}\" didn't hit the mark.",
                "Okay, so you didn't really enjoy \"{}\"."
            ]

            self.share_another_inquiries = [
                "Tell me about another movie.",
                "Please share your thoughts about another movie.",
                "Any other movies you want to rate?",
                "Please share your thoughts about another movie.",
                "Can you tell me about a different movie?",
                "Care to share your opinion on another?"
            ]

            self.recommend_another_movie_responses = [
                "I would also recommend \"{}\". How about another one?",
                "\"{}\" would be a good movie for you! Would you like more recommendations?",
                "Given your tastes, I would suggest watching \"{}\". Care for another recommendation? "
            ]

            self.negative_emotion_responses = [
                "I'm sorry you're feeling {}. Could I help you with a movie choice to cheer you up?",
                "It's not great to be feeling {}! How about a movie review for me?",
                "I've felt {} before, it's definitely not great to feel that way. Let's find some movies to get your mind off of that?"
            ]

            self.positive_emotion_responses = [
                "I'm so happy you're feeling {}! Could I help you with a movie choice to keep the good vibes going?",
                "It's awesome to hear you feel {}! Mind passing me a movie review?",
                "It's so great to feel {}; happy for you! Let's find some movies together?"
            ]
        else:
            self.no_potential_titles_responses = [
                "ARGHHHH matey! Did yerrrrr mention a movie?",
                "I don't know if you gave me and ME MATIES a movie, could YER try IT again please?",
                "AHOYYYY...I couldn't catch if you said something about a movie me shipmate."
            ]

            self.no_movie_match_responses = [
                "FIRE AWAY, I haven't heard of that film \"{}\" before. FIRE AWAY AGAIN?",
                "ME MATEY I don't think \"{}\" is out yet for me. Let's load up the ship and try again?",
                "I've SEARCHED THE SEVEN SEAS and I can't find any movies with the name \"{}\". Yerrrrr going to have to try again mate."
            ]

            self.no_sentiment_responses = [
                "CMON MATEY I don't even know what you thought about \"{}\". Matey, try again please?",
                "ARGHHHH what do you even think about \"{}\"?",
                "We LOVE THE BOOTY but I don't know how you feel about \"{}\". Could you tell me more?"
            ]

            self.multiple_matches_responses = [
                "MATEY WE'VE GOT TOO MUCH LOOT NAMED \"{}\". Be more specific my lad?",
                "There are fifty oceans and twenty rivers named \"{}\"! Which one are we looting, need specifics!?",
                "ARGHHH which \"{}\" are YER talking about?"
            ]

            self.multiple_movies_responses = [
                "AHOYYYYY let's slow down, this ship can't go that fast. Give your mate one at a time?",
                "SHIP OVERBOARD! I need one at a time crewmate!",
                "That's too much booty for us to carry! You're going to need to slow down, one load at a time!"
            ]

            self.positive_sentiment_responses = [
                "AHOYYYYY I loved \"{}\" as well matey.",
                "LOOT IS GOOD, SEAS ARE SMOOTH, I'm enjoying \"{}\" too!",
                "FIRE AWAY! \"{}\" is a great pick for our next post-raid watch."
            ]

            self.negative_sentiment_responses = [
                "MATEY that's too bad you didn't like \"{}\", we've got work to do.",
                "LAND AHEAD... focus up mate, I could care less if \"{}\" didn't hit the target.",
                "ARGH so you didn't like \"{}\", at least we can all agree we like some good loot?"
            ]

            self.share_another_inquiries = [
                "MATEY yer going to have to tell me about another movie.",
                "I NEED SOME MORE LOOT, crewmate! GIVE ME SOME MORE!",
                "There's so much more loot, share me some more targets?",
                "GIMME ANOTHER or you're going to walk the plank."
            ]

            self.recommend_another_movie_responses = [
                "MATEY liked \"{}\", YARRRRR. Let's get some more loot?",
                "\"{}\" is a CREWMATE CLASSIC! Let's get another one for a our post-raid viewing?",
                "You're a pirate with good taste, we all liked \"{}\". Yerrrrrr going to have to give me another? "
            ]

            self.negative_emotion_responses = [
                "We MATEYS sometimes feel {} too. MOVIE TIME AHOYYYY?",
                "When I feel {} I just go looking for loot! Let's get a movie review then search the seas?",
                "AHOYYYY we don't have time to feel {}. Let's find some movies to get this ship back on track?"
            ]

            self.positive_emotion_responses = [
                "AHEAD with the good times, glad you're feeling {} matey! Let's get some more loot?",
                "Great, now use that feeling of {} to do some shipwork! Movie review AHOYYYYY?",
                "Happy times make for efficient work, good to feel {}! Let's get this ship righted with a movie?"
            ]


        ########################################################################
        # TODO: Binarize the movie ratings matrix.                             #
        ########################################################################
        ratings = self.binarize(ratings)
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
        greeting_message = "How can I help you?"
        if self.creative:
            greeting_message = "MATEY what are we doing today? AHOYYYY"
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
        if self.creative:
            "YERRR matey! See you on our next loot"

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

        # Extract tokens
        tokens = word_tokenize(line)
        stemmer = PorterStemmer()
        stemmed_tokens = [stemmer.stem(token) for token in tokens]

        # Extract potential titles
        potential_titles = self.extract_titles(line)

        # Extract movie indices by title
        movie_indices = []
        for potential_title in potential_titles:
            movie_indices.append(self.find_movies_by_title(potential_title))
                    
        # Extract sentiment from line
        user_sentiment = self.extract_sentiment(line)

        # spelling checker mode - CREATIVE        
        if self.creative and len(self.spelling_candidates) > 0:
            if len(self.spelling_candidates) == 1:
                if tokens[0].lower() in {"y", "yeah", "yes", "sure", "okay", "ok", "alright"}:
                    movie_indices = [self.spelling_candidates]
                    user_sentiment = self.stored_sentiment
                    self.stored_sentiment = 0
                    self.spelling_candidates = []
                elif tokens[0].lower() in {"n", "no", "nah", "not", "nope"}:
                    self.spelling_candidates = []
                    return "Okay. " + self.share_another_inquiries[np.random.randint(0, len(self.share_another_inquiries))]
                else:
                    if self.creative:
                        return "ARGHHHH is that the right movie?"
                    return "Was that movie what you were looking for?"
            else:
                movie_indices = [self.disambiguate(line, self.spelling_candidates)]
                if len(movie_indices[0]) == 0:
                    if self.creative:
                        return "AHOYYYYY matey let's be more specific!"
                    return "Can you give me something to distinguish them?"
                elif len(movie_indices[0]) == 1:
                    self.spelling_candidates = []
                    user_sentiment = self.stored_sentiment
                    self.stored_sentiment = 0
                else:
                    movie_indices[0] = []


        # Disambiguation mode - CREATIVE
        if self.creative and len(self.disambiguation_candidates) > 0:
            movie_indices = [self.disambiguate(line, self.disambiguation_candidates)]
            if len(movie_indices[0]) == 0:
                return "Can you give me something to distinguish them?"
            if len(movie_indices[0]) == 1:
                self.disambiguation_candidates = []
                user_sentiment = self.stored_sentiment
                self.stored_sentiment = 0

        normal = False


        if len(potential_titles) == 0 and (len(movie_indices) == 0 or len(movie_indices[0]) == 0) and len(self.spelling_candidates) == 0: # no movie titles given
            if self.creative:
                emotion_found = False
                for token, stemmed_token in zip(tokens, stemmed_tokens):
                    if emotion_found:
                        break
                    if is_negative_emotion(stemmed_token):
                        emotion_found = True
                        response = self.negative_emotion_responses[np.random.randint(0, len(self.negative_emotion_responses))].format(token)
                    elif is_positive_emotion(stemmed_token):
                        emotion_found = True
                        response = self.positive_emotion_responses[np.random.randint(0, len(self.positive_emotion_responses))].format(token)
                if not emotion_found:
                    response = self.no_potential_titles_responses[np.random.randint(0, len(self.no_potential_titles_responses))]
            else:
                response = self.no_potential_titles_responses[np.random.randint(0, len(self.no_potential_titles_responses))]
        elif len(movie_indices[0]) == 0: # no match in database
            if self.creative:
                if len(self.spelling_candidates) == 0:
                    self.spelling_candidates = self.find_movies_closest_to_title(potential_titles[0], max_distance=3)
                if len(self.spelling_candidates) == 1:
                    response = "ARGHHHH did you mean \"{}\"?".format(self.titles[self.spelling_candidates[0]][0]) 
                    self.stored_sentiment = self.stored_sentiment if self.stored_sentiment != 0 else user_sentiment
                elif len(self.spelling_candidates) > 1:
                    response = "MATEY WHICH ONE OF THESE ARE YERRR TALKING ABOUT:"
                    for idx in self.spelling_candidates:
                        response += "\n" + self.titles[idx][0]
                    self.stored_sentiment = self.stored_sentiment if self.stored_sentiment != 0 else user_sentiment
                else:
                    response = self.no_movie_match_responses[np.random.randint(0, len(self.no_movie_match_responses))].format(potential_titles[0])
            else:
                response = self.no_movie_match_responses[np.random.randint(0, len(self.no_movie_match_responses))].format(potential_titles[0])
        elif len(movie_indices) > 1: # talking about multiple movies
            response = self.multiple_movies_responses[np.random.randint(0, len(self.multiple_movies_responses))]
        elif len(movie_indices[0]) > 1: # more than one match in database
            if self.creative: # Disambiguation dialogue - CREATIVE
                response = "AHOYYYYYY which LOOT did you want?"
                for idx in movie_indices[0]:
                    response += "\n" + self.titles[idx][0]

                self.disambiguation_candidates = movie_indices[0]
                self.stored_sentiment = self.stored_sentiment if self.stored_sentiment != 0 else user_sentiment
            else:
                response = self.multiple_matches_responses[np.random.randint(0, len(self.multiple_matches_responses))].format(potential_titles[0])
        elif user_sentiment == 0: # no sentiment given
            response = self.no_sentiment_responses[np.random.randint(0, len(self.no_sentiment_responses))].format(self.titles[movie_indices[0][0]][0])
        else: # normal case
            self.user_ratings[movie_indices[0][0]] = user_sentiment
            normal = True
            if user_sentiment >= 1: # positive
                response = self.positive_sentiment_responses[np.random.randint(0, len(self.positive_sentiment_responses))].format(self.titles[movie_indices[0][0]][0])
            elif user_sentiment <= -1: # negative
                response = self.negative_sentiment_responses[np.random.randint(0, len(self.negative_sentiment_responses))].format(self.titles[movie_indices[0][0]][0])
            if np.count_nonzero(self.user_ratings) < 5:
                response += f" {self.share_another_inquiries[np.random.randint(0, len(self.share_another_inquiries))]}"
        
        if (normal and np.count_nonzero(self.user_ratings) >= 5) or self.rec_ptr > 0: # recommend mode
            if self.rec_ptr == 0:
                self.recommendations = self.recommend(self.user_ratings, self.ratings, k=20)
            elif self.rec_ptr >= len(self.recommendations):
                self.recommendations = self.recommend(self.user_ratings, self.ratings, len(self.recommendations) * 2)
            if self.rec_ptr >= len(self.recommendations):
                self.rec_ptr = 0
                if self.creative:
                    return "ARGHHHHHHH I need to get back to looting! Give me a review or go do something helpful on the ship."
                return "Sorry, I have no more recommendations for you. Please tell me about another movie."

            if self.rec_ptr == 0:
                if self.creative:
                    response += "\n" + "AHOYYYYY I think you would like \"{}\". MORE LOOTING FOR YERRRR?".format(self.titles[self.recommendations[0]][0])
                else:
                    response += "\n" + "Given what you told me, I think you would like \"{}\". Would you like more recommendations?".format(self.titles[self.recommendations[0]][0])
                self.rec_ptr += 1
            elif self.rec_ptr > 0:
                if tokens[0].lower() in {"y", "yeah", "yes", "sure", "okay", "ok", "alright"}:
                    response = self.recommend_another_movie_responses[np.random.randint(0, len(self.recommend_another_movie_responses))].format(self.titles[self.recommendations[self.rec_ptr]][0])
                    self.rec_ptr += 1
                elif tokens[0].lower() in {"n", "no", "nah", "not", "nope"}:
                    if self.creative:
                        response = "AHOYYYY WHAT OTHER BOOTY CAN WE GET?"
                    else:
                        response = "Okay. Can you tell me about another movie?"
                    self.rec_ptr = 0
                else:
                    if self.creative:
                        response = "MATEY FOCUS UP, WE NEED ANOTHER MISSION OR NOT?"
                    else:
                        response = "I couldn't catch that, did you want another recommendation?"

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
        titles = []
        
        start_quote_idx = -1
        for idx, char in enumerate(preprocessed_input):
            if start_quote_idx == -1 and char == '"': # start quotes
                start_quote_idx = idx
            elif char == '"': # end quotes
                titles.append(preprocessed_input[start_quote_idx + 1:idx])
                start_quote_idx = -1
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
        if title == "":
            return []

        title = title.lower().strip()
        movie_idxs = set()

        for idx, entry in enumerate(self.titles):
            def get_article_title(title):
                article_regex = re.search(r"(.+),\s(\w+)", title)
                if article_regex and len(article_regex.groups()) == 2:
                    return article_regex.group(2) + " " + article_regex.group(1)
                return title

            def extract_all_titles(t):
                candidates = {t}
                candidates.add(get_article_title(t))

                year_extract_regex = re.search(r"(.+)\((\d{4})\)", t)
                title_no_year, year = year_extract_regex.groups() if year_extract_regex else (title, None)
                
                vanilla_title_regex = re.search(r"(.+)\s+\(", t)
                if vanilla_title_regex:
                    candidates.add(vanilla_title_regex.group(1))
                    candidates.add(get_article_title(vanilla_title_regex.group(1)))
                    if year is not None:
                        candidates.add(get_article_title(vanilla_title_regex.group(1)) + f" ({year})")

                aka_extract_regex = re.search(r"\(a.k.a. ([^)]+)\)", t)
                if aka_extract_regex:
                    candidates.add(aka_extract_regex.group(1))
                    candidates.add(get_article_title(aka_extract_regex.group(1)))
                    if year is not None:
                        candidates.add(get_article_title(aka_extract_regex.group(1)) + f" ({year})")
               
                foreign_title_regex = re.search(r"\(((?!(?:a.k.a.))[^\(]*)\)\s+\(\d{4}\)", t)
                if foreign_title_regex:
                    candidates.add(foreign_title_regex.group(1))
                    candidates.add(get_article_title(foreign_title_regex.group(1)))
                    if year is not None:
                        candidates.add(get_article_title(foreign_title_regex.group(1)) + f" ({year})")

                return {candidate.strip().lower() for candidate in candidates}
            
            db_title, _ = entry
            
            candidates = extract_all_titles(db_title)

            if title in candidates:
                movie_idxs.add(idx)

            
            if self.creative:
                # disambiguate part 1, I added this to your code Cao
                # year_extract_regex = re.search(r"(.+)\((\d{4})\)", title)
                # title_no_year, year = year_extract_regex.groups() if year_extract_regex else (title, None)

                title_list = title.split(' ')
                for candidate in candidates:
                    db_title_list = candidate.split(' ')

                    j = 0
                    sublist = False
                    for i in range(len(db_title_list)):
                        k = i
                        
                        while (j < len(title_list)):
                            if k < len(db_title_list) and len(db_title_list[k]) == len(title_list[j]) and db_title_list[k] == title_list[j]:
                                j += 1
                                k += 1
                                sublist = True
                            elif k < len(db_title_list) and len(db_title_list[k]) != len(title_list[j]):
                                if len(db_title_list[k]) > 0 and db_title_list[k][-1].isalpha() == False and db_title_list[k][0 : len(db_title_list[k]) - 1] == title_list[j]:
                                    j += 1
                                    k += 1
                                    sublist = True
                                else:
                                    j = 0
                                    sublist = False
                                    break
                            else:
                                j = 0
                                sublist = False
                                break
                    if sublist and idx not in movie_idxs:
                        movie_idxs.add(idx)

        return list(movie_idxs)

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
            tokens = word_tokenize(preprocessed_input)
            stemmer = PorterStemmer()
            stemmed_tokens = [stemmer.stem(token.lower()) for token in tokens]
            stemmed_sentiment = { stemmer.stem(k): v for k, v in self.sentiment.items()}
            
            # found words and synonyms from https://www.macmillandictionary.com/us/thesaurus-category/american/extremely-good-or-of-a-high-quality 
            # and thesaurus.com
            extreme_list = ["really", "easily", "certainly", "undoubtedly", "unquestionably", "literally", "legitimately", "genuinely", "absolutely", "authentically"]
            stem_extreme_list = [stemmer.stem(token) for token in extreme_list]
            positive_list = ["love", "amazing", "excellent", "wonderful", "exceptional", "tremendous", "superb", "incredible", "awesome", "insane", "unreal", "unbelievable", "fascinating", "stunning", "prodigious", "extraordinary", "remarkable", "unprecedented", "special", "best", "outstanding", "perfect", "terrific"]
            stem_positive_list = [stemmer.stem(token) for token in positive_list]
            negative_list = ["terrible", "abhorrent", "dreadful", "appalling", "atrocious", "awful", "disastrous", "disturbing", "frightful", "ghastly", "harrowing", "hideous", "horrid", "horrifying", "unpleasant", "rotten", "heinous", "lousy", "abominable", "grievous", "hideous", "worst", "tragic", "shameful", "lowest", "hated", "detested", "loathed"]
            stem_negative_list = [stemmer.stem(token) for token in negative_list]

            stem_extreme_list = [stemmer.stem(token) for token in extreme_list]

            count_pos = 0
            count_neg = 0
            negation_list = {"not", "never"}
            no_titles_input = []
            between_quotes = False
            for i in range(len(stemmed_tokens)):
                if not between_quotes and stemmed_tokens[i] == '"': # start quote
                    between_quotes = True
                elif stemmed_tokens[i] == '"': # end quote
                    between_quotes = False
                elif not between_quotes:
                    no_titles_input.append(stemmed_tokens[i])

            negation_flag = False
            multiply2_flag = False
            for token in no_titles_input:

                if token in negation_list or token.endswith("n't"):
                    negation_flag = True
                if token in stemmed_sentiment:
                    sentiment = stemmed_sentiment[token]
                    if sentiment == "pos":
                        if negation_flag:
                            count_neg += 1
                        else:
                            count_pos += 1
                    else:
                        if negation_flag:
                            count_pos += 1
                        else:
                            count_neg += 1
                if token in stem_positive_list:
                    if not negation_flag:
                        return 2
                elif token in stem_negative_list:
                    if not negation_flag:
                        return -2
                elif token in stem_extreme_list:
                    if not negation_flag:
                        multiply2_flag = True
            if count_pos > count_neg:
                if multiply2_flag:
                    return 2
                return 1
            elif count_neg > count_pos:
                if multiply2_flag:
                    return -2
                return -1
            else:
                return 0
        else:
            tokens = word_tokenize(preprocessed_input)
            stemmer = PorterStemmer()
            stemmed_tokens = [stemmer.stem(token) for token in tokens]
            stemmed_sentiment = { stemmer.stem(k): v for k, v in self.sentiment.items()}

            count_pos = 0
            count_neg = 0
            negation_list = {"not", "never"}
            no_titles_input = []
            between_quotes = False
            for i in range(len(stemmed_tokens)):
                if not between_quotes and stemmed_tokens[i] == '"': # start quote
                    between_quotes = True
                elif stemmed_tokens[i] == '"': # end quote
                    between_quotes = False
                elif not between_quotes:
                    no_titles_input.append(stemmed_tokens[i])

            negation_flag = False
            for token in no_titles_input:

                if token in negation_list or token.endswith("n't"):
                    negation_flag = True
                if token in stemmed_sentiment:
                    sentiment = stemmed_sentiment[token]
                    if sentiment == "pos":
                        if negation_flag:
                            count_neg += 1
                        else:
                            count_pos += 1
                    else:
                        if negation_flag:
                            count_pos += 1
                        else:
                            count_neg += 1
            if count_pos > count_neg:
                return 1
            elif count_neg > count_pos:
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

        if title == "":
            return []

        min_distance = int(max_distance)
        valid = []
        for i in range(len(self.titles)):
            movie = self.titles[i][0]
            article_regex = re.search(r"(.+),\s(\w+)", movie)
            if article_regex:
                movie = article_regex.group(2) + " " + article_regex.group(1)

            titulo = movie.split(' (')[0]
            
            if title == titulo:
                continue

            # Calculate Levenshtein edit distance based on Edit Distance slides
            # Referenced https://www.scaler.com/topics/levenshtein-distance-python/

            m = len(title) + 1
            n = len(titulo) + 1
            
            matrix = [[0 for g in range(n)] for b in range(m)]

            for j in range(n):
                matrix[0][j] = j
            for k in range(m):
                matrix[k][0] = k

            for s in range(1, m):
                for a in range(1, n):
                    same = False
                    
                    if title[s - 1].lower() == titulo[a - 1].lower():
                        same = True

                    
                    add = 2
                    if same:
                        add = 0

                    matrix[s][a] = min(
                        matrix[s - 1][a] + 1,
                        matrix[s][a - 1] + 1,
                        matrix[s - 1][a - 1] + add)

            distance = matrix[m - 1][n - 1]
            if distance < min_distance:
                valid.clear()
                valid.append(i)
                min_distance = distance
            elif distance == min_distance:
                valid.append(i)
        return valid

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
        res = []

        # strip clarification of punctuation
        clarification = re.search(r"[\s!\"#$%&'()*+,-.:;<=>?\/@\[\\\]^_`{|}~]*([\w\d\s]+)[\s!\"#$%&'()*+,-.:;<=>?\/@\[\\\]^_`{|}~]*", clarification.lower()).group(1)
        if clarification == "" or clarification is None:
            return res

        date = True
        if clarification.isdigit() and len(clarification) != 4:
            date = False

        for elem in candidates:
            cur = int(elem)
            entry = self.titles[cur]
            db_title, genres_string = entry

            if date == False:
                db_title = db_title[0 : -6]

            j = 0


            sublist = False
            for i in range(len(db_title)):
                k = i
                
                while (j < len(clarification)):
                    if k < len(db_title) and db_title[k].lower() == clarification[j]:
                        j += 1
                        k += 1
                        sublist = True
                    else:
                        j = 0
                        sublist = False
                        break
                if sublist:
                    break
            if sublist:
                res.append(cur)
        return res

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
        binarized_ratings = np.where(ratings > threshold, 1, ratings)
        binarized_ratings = np.where(ratings <= threshold, -1, binarized_ratings)
        binarized_ratings = np.where(ratings == 0, 0, binarized_ratings)
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
        u_norm = np.linalg.norm(u)
        v_norm = np.linalg.norm(v)
        
        if u_norm > 0 and v_norm > 0:
            similarity = np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))
        else:
            similarity = 0

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
        movie_idxs = np.nonzero(user_ratings)
        pred_ratings = np.zeros(user_ratings.shape)
        for i in range(user_ratings.shape[0]):
            if user_ratings[i] == 0:
                r_x_i = 0
                for j in movie_idxs[0]:
                    sim = self.similarity(ratings_matrix[i], ratings_matrix[j])
                    r_x_i += sim * user_ratings[j]
                pred_ratings[i] = r_x_i
        
        recommendations = np.argsort(pred_ratings)[::-1][:k].tolist()
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
        PIRATE MODE: MATEY WE'VE GOT A CRITICAL MISSION.
        IN THIS MODE, PUT SOME NICE LOOT (MOVIES) IN QUOTES
        AHOYYYY ME AND THE MATIES NEED SOME NICE MOVIES AFTER A
        HARD DAY OF SHIPWORK
        """
        return """
        Normal mode: welcome to the BusterBot. Please rate movies here, 
        putting movies in quotations. Remember to give your opinion and please
        avoid giving multiple movies at once!
        """


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
