# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util

import numpy as np
from porter_stemmer import PorterStemmer
import re
import math


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
        self.stemmer = PorterStemmer()
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')

        # get negation stemmed words
        negation_words = ["not", "never", "neither", "barely", "hardly", "scarcely", "seldom", "rarely", "don't", "didn't", "doesn't"]
        self.negations = set()
        for w in negation_words:
            self.negations.add(self.stemmer.stem(w))
        
        # get emphasis stemmed words
        emphasis_words = ["really", "so", "very", "extremely", "totally", "absolutely", "completely", "definitely", "highly", "incredibly", "remarkably", "awfully", "terribly", "intensely"]
        self.emphases = set()
        for w in emphasis_words:
            self.emphases.add(self.stemmer.stem(w))

        # get strong adjectives stemmed words
        strong_words = ["love", "adore", "ecstatic", "amazing", "excellent", "delightful", "fantastic", "marvelous", "phenomenal", "wonderful", "hate", "despise", "abhor", "repugnant", "terrible", "disgusting", "awful", "horrendous", "repulsive", "revolting"]
        self.strongs = set()
        for w in strong_words:
            self.strongs.add(self.stemmer.stem(w))
        prestemmed_words = list(self.sentiment.keys())
        for w in prestemmed_words:
            if self.stemmer.stem(w) == 'thought': continue
            self.sentiment[self.stemmer.stem(w)] = self.sentiment[w]


        # Count for how many datapoints there are
        self.data_count = 0

        # Initialize matrix for user ratings for each movie. Unrated movies default to 0.0
        self.user_ratings = np.zeros(ratings.shape[0])

        # List of recommended movies' indices
        self.rec_indices = []

        # Tracker for where in the rec list the chatbot has reached
        self.curr_rec_index = 0

        # Keep track of the last movie a user possibly misspelled and it's sentiment
        self.prev_movie = ""
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
    def get_confirmation(self):
        confirmation_strings = ["Got it! ", "I see. ", "Ok! ", "Understood. "]
        confirmation = np.random.choice(confirmation_strings)
        return confirmation

    def get_doubt(self, movie):
        doubt_strings = ["Sorry, I'm not sure if you liked ", "I'm having trouble telling how you felt about the movie ",
         "I can't seem to figure out your thoughts on ", "I apologize but I can't tell if you enjoyed "]
        doubt = np.random.choice(doubt_strings)
        doubt += movie + "."
        reconfim_strings = [" Please share more about it!", " I'd loved to hear more to better understand your thoughts!",
        " If you give me more details, I may be able to learn more about your opinion!", " To help me better understanding where you're coming from, please share more!"]        
        doubt += np.random.choice(reconfim_strings)
        return doubt
    
    def get_love(self, movie):
        love_strings = ["Wow! I'm so glad to hear you loved ", "Great, it sounds like you loved ", "I'm so happy you thoroughly enjoyed watching "]
        love = np.random.choice(love_strings)
        love += movie + "."
        return love

    def get_like(self, movie):
        like_strings = ["I'm glad you liked ", "Good to hear you enjoyed watching "]
        like = np.random.choice(like_strings)
        like += movie + "."
        return like

    def get_dislike(self, movie):
        dislike_strings = ["Sorry to hear that you didn't enjoy watching ", "That's unfortunate. Apologies that you didn't like "]
        dislike = np.random.choice(dislike_strings)
        dislike += movie + "."
        return dislike

    def get_hate(self, movie):
        hate_strings = ["Yikes, I'm sorry to hear you didn't like ", "Wow, that bad, huh. I'm sorry you didn't enjoy ", "I hope you have a better watch next time. Thank you for telling me about "]
        hate = np.random.choice(hate_strings)
        hate += movie + "."
        return hate

    def more_movies(self):
        prompt_strings = [" Tell me about another movie you've seen.",  " Let me know your thoughts on another movie.", " Please share your thoughts on a different film!"]
        prompt = np.random.choice(prompt_strings)
        return prompt
    
    def more_movies_plural(self):
        prompt_strings = [" Tell me about some other movies you've seen.",  " Let me know your thoughts on other movies.", " Please share your thoughts on a different set of films!"]
        prompt = np.random.choice(prompt_strings)
        return prompt

    def prompt_more_rec(self):
        prompt_strings = ["How about another one?", "Would you like another recommendation?", "Would you like more recommendations?"]
        prompt = np.random.choice(prompt_strings)
        return prompt
    
    def affirm_rec_request(self):
        prompt_strings = ["Sure! I think you would also like ", "For sure, another good choice would be ", "Totally, I think you would also like "]
        prompt = np.random.choice(prompt_strings)
        return prompt

    def get_sentiment_statements(self, sentiments):
        response = ""
        capitalize_first = True
        last_sentiment = 0
        for sentiment in sentiments:
            movie = sentiment[0]
            if self.creative and len(sentiments) > 1:
                movie = "\"" + movie.title() + "\""
                if sentiment[1] > 0:
                    if sentiment[1] == last_sentiment:
                        s = movie
                    elif sentiment[1] == 2:
                        s = "You loved " + movie
                    elif sentiment[1] == 1:
                        s = "You liked " + movie
                    if not capitalize_first:
                        s = ' and ' + s[0].lower() + s[1:]
                    else:
                        response += self.get_confirmation()
                    last_sentiment = sentiment[1]
                    response += s
                elif sentiment[1] < 0:
                    if sentiment[1] == last_sentiment:
                        s = movie
                    elif sentiment[1] == -2:
                        s = "You hated " + movie
                    elif sentiment[1] == -1:
                        s = "You did not like " + movie
                    if sentiment[1] == last_sentiment:
                        s = ' nor ' + s[0].lower() + s[1:]
                    elif not capitalize_first:
                        s = ' and ' + s[0].lower() + s[1:]
                    else:
                        response += self.get_confirmation()
                    last_sentiment = sentiment[1]
                    response += s
                else:
                    response += self.get_doubt(movie)

                if capitalize_first:
                    capitalize_first = False
            else:
                movie = "\"" + movie.title() + "\""
                if sentiment[1] > 0:
                    if sentiment[1] > 1:
                        response += self.get_love(movie)
                    else:
                        response += self.get_like(movie)
                    response += self.more_movies()
                elif sentiment[1] < 0:
                    if sentiment[1] < -1:
                        response += self.get_hate(movie)
                    else:
                        response += self.get_dislike(movie)
                    response += self.more_movies()
                else:
                    response += self.get_doubt(movie)
        return response + ("." + self.more_movies_plural() if self.creative and len(sentiments) > 1 else "")

    def simple_process_movies(self, sentiments):
        if len(sentiments) > 1:
            movies = map(lambda x: "\"" + x[0].title() + "\"", sentiments)
            movies_to_namedrop = " and ".join(movies)
            return ("I'd love to talk about " + movies_to_namedrop + " individually! I'm a simple chatbot and can only handle one movie at a time.", 0)
        elif len(sentiments) == 1:
            movies = self.find_movies_by_title(sentiments[0][0])
            movie = "\"" + sentiments[0][0].title() + "\""
            if len(movies) > 1:
                return ("It looks like there's more than one movie called \"" + movie + "\". You clarify by including the year as (full year) after the title or using an alternate title!", 0)
            elif len(movies) < 1:
                return ("Sorry I haven't heard of " + movie + " before." + self.more_movies(), 0)
            else:
                # Modify user ratings matrix
                self.user_ratings[movies[0]] = sentiments[0][1]
                return (self.titles[movies[0]][0], 1)
        return ("Sorry, I'm not sure what movie you're talking about. Please try again by adding quotation marks around the title of the movie!", 0)

    def run_spellcheck(self, movie):
        movie_indices = self.find_movies_closest_to_title(movie)
        movies = []
        for index in movie_indices:
            movies.append(self.titles[index][0])
        return movies

    def creative_process_movies(self, sentiments):
        processed = []
        ratings_to_add = []
        for sentiment in sentiments:
            movies = self.find_movies_by_title(sentiment[0])
            if len(movies) > 1:
                titles = []
                for m in movies:
                    titles.append("\"" + self.titles[m][0] + "\"")
                return (("It looks like there are multiple movies with that name. Please clarify which movie you are discussing out of the following: \n" + "\n".join(titles)), 0)
            elif len(movies) == 0:
                spellcheck = self.run_spellcheck(sentiment[0])
                if len(spellcheck) == 0:
                    return ("Sorry I haven't heard of \"" + sentiment[0] + "\" before." + self.more_movies(), 0)
                else:
                    for i in range(len(spellcheck)):
                        title = spellcheck[i].split(',')
                        if len(title) == 2 and title[1].startswith(("a","an","the", "la","le","les","un","une","las","los","el","lo","das","die","der","det","en")):
                            spacing_article_and_year = title[1].strip().split(' ')
                            spellcheck[i] = spacing_article_and_year[0] + ' ' + title[0].strip() + ' ' + spacing_article_and_year[1]

                    if len(spellcheck) > 1:
                        similar_titles = " or ".join(spellcheck)
                        return ("I can't say I've heard of \"" + sentiment[0] + "\" but I do know of some similarly titled movies. Did you mean to talk about " + similar_titles + "?", 0)
                    else:
                        return ("I can't say I've heard of \"" + sentiment[0] + "\". Did you mean to talk about \"" + spellcheck[0] + "\"?", spellcheck[0], sentiment[1])
            else:
                ratings_to_add.append((self.titles[movies[0]][0], sentiment[1]))

        for title, sentiment in ratings_to_add:
            movies = self.find_movies_by_title(title)
            self.user_ratings[movies[0]] = sentiment
            processed.append((self.titles[movies[0]][0], 1))
        if not processed:
            return ("Sorry, I'm not sure what movie(s) you're talking about. Please try again by adding quotation marks around the titles!", 0)
        return processed

    def is_positive(self, line):
        line = line.lower()
        return (line.startswith(("yes","yea","sure","ok","yeah")))

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
        response = None
        if self.creative:

            emotions = {
                'happy': set(["happy", "pleased", "delighted", "joyful", "ecstatic", "content", "overjoyed", "gleeful", "elated", "jubilant", "thrilled"]),
                'sad': set(["sad", "unhappy", "depressed", "downhearted", "sorrowful", "miserable", "gloomy", "melancholy", "despondent", "heartbroken", "disheartened"]),
                'angry': set(["angry", "mad", "irritated", "frustrated", "annoyed", "outraged", "furious", "livid", "indignant", "enraged", "incensed"]),
                'afraid': set(["afraid", "scared", "terrified", "panicked", "anxious", "nervous", "uneasy", "worried", "horrified", "petrified"])            
            }
            if not self.extract_titles(line):
                for w in line.split(' '):
                    for e in emotions:
                        if w in emotions[e]:
                            if e == 'angry':
                                return "Oh my I'm so sorry to hear that you are " + w + "! Is there something I did wrong?"
                            elif e == 'happy':
                                return "Yay so glad to hear that you are " + w + "! Let me add to your day by recommending some movies based on your current movie preferences."
                            elif e == 'afraid':
                                return "Why would you be " + w + " of me? I am sorry to hear that."
                            elif e == 'sad':
                                return "I am so sorry to hear that you are " + w + ". I hope I can recommend some movies to make you feel better."
            
            question_patterns = {
                r"^(can|could|would) (you|we|they|i) (.+)\??$": "I'm sorry, I just want to talk about movies. I cannot {action}.",
                r"^(what|where|when|why|how) (is|are|can|do|does|did|will|would|should) (.+)\??$": "I'm not sure what {term} is, how about we focus on your movie preferences?",
                r"^(how) (do|does|did|will|would|should|can) (you|i|we) (.+)\??$": "Sorry, I don't know how to {action}. How about we talk about movies?",
                r"^(do|does|did|will|would|should) (you|i|we) (.+)\??$": "Sorry, I don't know how to {action}. How about we talk about movies?"
            }
            for pattern, response_template in question_patterns.items():
                match = re.match(pattern, line.lower())
                if match:
                    action = match.group(3)
                    term = action
                    if len(match.groups()) >= 4:
                        action = match.group(4)
                        term = match.group(3)
                    if action[-1] in '.?': action = action[:-1]
                    if term[-1] in '.?': term = term[:-1]
                    response = response_template.format(action=action, term=term)
            if response: return response

            if len(self.prev_movie) > 0 and self.is_positive(line):
                sentiments = self.prev_movie
                movie_index = self.find_movies_by_title(self.prev_movie[0][0])
                self.data_count += 1
                self.user_ratings[movie_index[0]] = self.prev_movie[0][1]
                self.prev_movie = ""
                response = self.get_sentiment_statements(sentiments)
            else:
                sentiments = self.extract_sentiment_for_movies(line)
                movies = self.creative_process_movies(sentiments)
                if isinstance(movies, tuple): # didn't process all movies properly, returned a message indication for where error occured
                    if movies[1] == 0:
                        response = movies[0]
                    elif len(movies) > 2:
                        self.prev_movie = [(movies[1],movies[2])]
                        response = movies[0]
                else:
                    self.data_count += len(movies)
                    response = self.get_sentiment_statements(sentiments)

                # Automatically give suggestion if there are at least 5 datapoints
                if self.data_count >= 5:
                    self.rec_indices = self.recommend(self.user_ratings, self.ratings, 10, self.creative)
                    rec_movie = self.titles[self.rec_indices[self.curr_rec_index]][0]
                    # WARNING: there's no guard from this exceeding the rec list just now
                    self.curr_rec_index += 1
                    response = "Given what you told me, I think you would like " + rec_movie + ". " + self.prompt_more_rec() + " (Or enter :quit if you're done.)"

                # Repond to further recommendation requests
                line = line.lower()
                if line.startswith(("yes","yea","sure","ok")):
                    response = self.affirm_rec_request() + self.titles[self.rec_indices[self.curr_rec_index]][0] + ". " + self.prompt_more_rec() + "(Or enter :quit if you're done.)"
                    self.curr_rec_index += 1
                if line.startswith(("no","nah","nope","i'm good")):
                    response = "Ok! You can enter :quit if you're done."
        else:
            sentiments = self.extract_sentiment_for_movies(line)
            movies = self.simple_process_movies(sentiments)
            if movies[1] == 0:
                response = movies[0]
            else:
                # One successful datapoint recorded
                self.data_count += 1
                response = self.get_sentiment_statements(sentiments)

            # Automatically give suggestion if there are 5 datapoints
            if self.data_count == 5:
                self.rec_indices = self.recommend(self.user_ratings, self.ratings, 10, self.creative)
                rec_movie = self.titles[self.rec_indices[self.curr_rec_index]][0]
                # WARNING: there's no guard from this exceeding the rec list just now
                self.curr_rec_index += 1
                response = "Given what you told me, I think you would like \"" + rec_movie + "\". " + self.prompt_more_rec() + " (Or enter :quit if you're done.)"

            # Repond to further recommendation requests
            line = line.lower()
            if line.startswith(("yes","yea","sure","ok")):
                response = self.affirm_rec_request() + "\"" + self.titles[self.rec_indices[self.curr_rec_index]][0] + "\". " + self.prompt_more_rec() + "(Or enter :quit if you're done.)"
                self.curr_rec_index += 1
            if line.startswith(("no","nah","nope","i'm good")):
                response = "Ok! You can enter :quit if you're done."
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
        titles = re.findall('"([^"]*)"', preprocessed_input)
        return titles

    def is_sub(self, sub, full):
        """ Given a subtitle and a full title return whether the subtitle 
        can be found within the full title.

        :param sub: a string containing a movie title to find
        :param full: a string containing a movie title to search through
        :returns: a boolean representing if sub is in full
        """
        first_index = full.find(sub)
        if first_index < 0:
            return False
        if len(sub) + first_index < len(full) :
            return full[len(sub) + first_index].isalpha() == False
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
        movies = []
        title = title.lower()
        if (title.startswith(("a","an","the", "la","le","les","un","une","las","los","el","lo","das","die","der","det","en"))): #need modify title if it starts with an article
            article_index = title.find(" ")
            year_index = title.rfind("(")
            if year_index == -1:
                title = title[article_index + 1:] + ", " + title[:article_index]
            else:
                title = title[article_index + 1: year_index - 1] + ", " + title[:article_index] + title[year_index - 1:]
        for i in range(len(self.titles)):
            current_title = self.titles[i][0].lower()
            if current_title == title: #exact title and year provided
               return [i]
            main_title = current_title[:current_title.find(" (")] # main title only, stops before first '('
            if main_title == title: 
                movies.append(i)
            if self.creative: #disambiguation part 1
                if self.is_sub(title, main_title) and (len(movies) == 0 or movies[-1] != i):
                   movies.append(i)
            # get list of foreign and alternate title(s)
            other_titles = re.findall(r'\((?:a.k.a.\s)?([^\)]+)\)', current_title)
            # loop through all but the last one, the last match is the year: e.g. (1997). If no alternative title, this skips
            for j in range(len(other_titles) - 1):
                curr_other_title = other_titles[j]
                if curr_other_title == title and (len(movies) == 0 or movies[-1] != i):
                    movies.append(i)
                if self.creative:
                    if self.is_sub(title, curr_other_title) and (len(movies) == 0 or movies[-1] != i):
                        movies.append(i)
        return movies
    
    def split_quoted_text(self, text):
        tokens = re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', text)
        # Remove periods from tokens that are not within double-quoted strings
        for i in range(len(tokens)):
            curr_token = tokens[i]
            last = len(tokens[i])
            # Removes period for ("movie title".)
            if tokens[i][last-2] == '"' and tokens[i][last-1] == '.':
                period_removed = tokens[i][:last-1]
                tokens[i] = period_removed
            # Removes period for other strings that are not movie titles
            if tokens[i][0] != '"' and '.' in tokens[i]:
                tokens[i] = tokens[i].replace('.', '')
        return tokens

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
        sentiment = 0

        negate = 1
        extra = False
        words = self.split_quoted_text(preprocessed_input)
        for w in words:
            stemmed_w = self.stemmer.stem(w.lower())
            if stemmed_w in self.negations:
                negate *= -1
                continue
            if stemmed_w in self.emphases or stemmed_w in self.strongs:
                extra = True
            word_sentiment = self.sentiment.get(stemmed_w, '') or self.sentiment.get(w)
            if word_sentiment == 'pos':
                if w.isupper():
                    extra = True
                sentiment += 1
            elif word_sentiment == 'neg':
                if w.isupper():
                    extra = True
                sentiment -= 1

        sent = 0
        if sentiment > 0: sent = 1
        elif sentiment < 0: sent = -1
        sent = negate * sent 

        if preprocessed_input.find('!') != -1:
            extra = True

        if extra:
            if sent < 0:
                sent = -2
            elif sent > 0:
                sent = 2
        return sent


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
        movie_titles = self.extract_titles(preprocessed_input)
        sentiments = []
        words = self.split_quoted_text(preprocessed_input)
        last_movie_indx = -1
        movie_titles.sort(key=lambda t: words.index("\"" + t + "\""))
        for i, title in enumerate(movie_titles):
            title = "\"" + title + "\""
            index = words.index(title)
            description_toward_movie = ' '.join(words[last_movie_indx+1:index+1])
            sentiment = self.extract_sentiment(description_toward_movie)
            if sentiment == 0: # sentiment could come after title
                post_index = len(words) if (i == len(movie_titles) - 1) else (words.index("\"" + movie_titles[i+1] + "\""))
                post_description_toward_movie = ' '.join(words[index:post_index])
                post_sentiment = self.extract_sentiment(post_description_toward_movie)
                if post_sentiment:
                    sentiment = post_sentiment
                elif sentiments: # or e.g. (I liked "Titanic" and "Moneyball") will use "Titanic" sentiment for "Moneyball"
                    sentiment = sentiments[-1][-1]
            sentiments.append((title.replace("\"", ""), sentiment))
            last_movie_indx = index
        return sentiments

    def minimum_edit_distance(self, word1, word2):
        """ Finds the levenstein distance between word1 and word2
        :param word1: a string, word2: a string
        :returns: an int representing the levenstein distance
        """
        longer =  word1 if len(word1) > len(word2) else word2
        shorter = word1 if longer == word2 else word2

        if len(shorter) == 0:
            return(len(longer))
        #initialize distance matrix
        distances = np.zeros((len(longer) + 1, len(shorter) + 1))
        for i in range(len(distances)):
            distances[i][0] = i
        for j in range(len(distances[0])):
            distances[0][j] = j
        
        for i in range(1, len(distances)):
            for j in range(1, len(distances[0])):
                if(longer[i - 1] == shorter[j - 1]):
                   distances[i][j] = distances[i - 1][j - 1] 
                else:
                    left = distances[i - 1][j]
                    down = distances[i][j - 1]
                    diagonal = distances[i - 1][j - 1]
                    distances[i][j] = min([left,down,diagonal]) + 1
        return distances[len(longer)][len(shorter)]

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
        movies = []
        title = title.lower()
        if (title.startswith(("a","an","the"))): #need modify title if it starts with an article
            article_index = title.find(" ")
            year_index = title.rfind("(")
            if year_index == -1:
                title = title[article_index + 1:] + ", " + title[:article_index]
            else:
                title = title[article_index + 1: year_index - 1] + ", " + title[:article_index] + title[year_index - 1:]
        for i in range(len(self.titles)):
            current_title = self.titles[i][0].lower()
            if current_title == title: #exact title and year provided
               return [i]
            current_title = current_title[:current_title.rfind(" (")] #title only
            if current_title == title: 
                movies.append((i, 0))
            dist = self.minimum_edit_distance(current_title, title)
            if dist <= max_distance:
                movies.append((i, dist))
        movies = sorted(movies, key = lambda x: x[1]) 
        most_similar = []
        for i in range(len(movies)):
            if movies[0][1] == movies[i][1]:
                most_similar.append(movies[i][0])
        return most_similar
        


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
        new_candidates = []
        
        # Given index in candidates list
        if clarification.isdigit() and int(clarification) <= len(candidates):
            return [candidates[int(clarification)-1]]
        # Given title or year of the movie
        for index in candidates:
            if self.is_sub(clarification.lower(), self.titles[index][0].lower()) or self.is_sub(clarification, self.titles[index][1].lower()):
                new_candidates.append(index)
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

        # The starter code returns a new matrix shaped like ratings but full of
        # zeros.
        binarized_ratings = np.where(np.logical_and(ratings > 0, ratings <= threshold), -1, ratings)
        binarized_ratings = np.where(np.logical_and(binarized_ratings > 0, binarized_ratings > threshold), 1, binarized_ratings)

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
        similarity = 0
        if u_norm != 0 and v_norm != 0:
            similarity = np.dot(u, v)/(u_norm * v_norm)
        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return similarity

    def weightedAverage(self, movie, user_ratings, ratings_matrix, k):
        cosine_sims = []
        movie_row = ratings_matrix[movie]
        # Extract all the indices of movies that the user has rated
        rated_movies = np.argwhere(user_ratings)

        # this goes through each movie existing to see other movies user has rated, and gets similarity score
        for index in rated_movies:
            if index[0] != movie:
                cosine_sims.append((user_ratings[index[0]], self.similarity(movie_row, ratings_matrix[index[0]])))
        weights = [[(x * y) for x, y in cosine_sims]]
        return np.sum(weights)
        

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
        for i in range(len(user_ratings)):
            if user_ratings[i] == 0:
                score = self.weightedAverage(i, user_ratings, ratings_matrix, k) # compute similarity to all other movies they've watch and return averaged sum
                if not math.isnan(score):
                    recommendations.append((i, score))

        recommendations = sorted(recommendations, key = lambda x: x[1])[-k:]
        recommendations = [i[0] for i in recommendations]
        recommendations.reverse()
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
