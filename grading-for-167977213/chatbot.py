# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util

import numpy as np
import re
import random
import porter_stemmer
from enum import Enum

stemmer = porter_stemmer.PorterStemmer()
class PriorInputStatus(Enum):
    NONE = 0
    TYPO = 1
    DISAMBIGUATE = 2
    COMPLETE = 3
    
class PriorInput:
    def __init__(self):
        self.status = PriorInputStatus.NONE
        self.full_input = ""
        self.disambiguate_options = []
        self.movie = ""

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
        # stem all keys
        self.sentiment = {stemmer.stem(key): sentiment[key] for key in sentiment}

        self.positive_words = [word.lower() for word, sentiment in self.sentiment.items() if sentiment == "pos"]
        self.negative_words = [word.lower() for word, sentiment in self.sentiment.items() if sentiment == "neg"]

        self.negating_words = ["no", "neither", "never", "nor", "didn't", "none", "nothing", "nowhere", "hardly", "scarcely", "barely"]
       
        # New features:
        self.inputed_movies = []
        self.yes = ["yes", "yep", "affirmative", "yea", "yeah", "yup", "fine", "okay", "ok", "certainly", "definitely", "sure"]
        self.no = ["no", "nah", "nope"]
        self.subject_change = [
            "Let’s talk about movies. Please tell me your thoughts on a movie.",
            "I want to hear more about movies! Tell me about another movie you have seen.",
            "Okay, great. I’d love to hear your thoughts on a movie though!"
        ]
        self.finished = [
            "That's enough for me to make a recommendation.",
            "Thank you for telling me about movies you've watched! I have a movie in mind for you.",
            "Those are some cool movies! Let me tell you about one that I think you will like.",
            "Cool! Based on those movies, I have an idea of what you might like."
        ]
        self.another = [
            "Enjoy the movie! If you want more recommendations, I'd be happy to provie them. Would you like that? (Or enter :quit if you're done.)",
            "Do you want more suggestions? (Or enter :quit if you're done.)",
            "Would you like to hear another recommendation? (Or enter :quit if you're done.)",
            "I hope you like it! Would you like another recommendation? (Or enter :quit if you're done.)"
        ]

        self.user_ratings = np.zeros((ratings.shape[0]))
        self.user_ratings_count = 0
        self.max_movie_recommendations = 10
        self.recommendation_idx = 0
        self.recommendation_titles = []
        self.prior_input = PriorInput()

        ########################################################################
        # TODO: Binarize the movie ratings matrix.                             #
        ########################################################################

        # Binarize the movie ratings before storing the binarized matrix.
        ratings = Chatbot.binarize(ratings)
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

        greeting_message = "Hello! I am " + self.name + """, a chatbot designed
                        to recommend you movies. To start, please tell me your
                        opinion about a movie you have watched. To exit this
                        conversation, type ":quit" and hit Enter."""
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

        possible_messages = [
            "Have a nice day!",
            "Bye! Enjoy your next movie!",
            "Cya! Come back any time!",
            "See you soon!",
            "Thanks for talking with me!",
            "Thank you for hanging out with me! Stay in touch! Goodbye!"
        ]
        goodbye_message = random.choice(possible_messages)

        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return goodbye_message

    ############################################################################
    # 2. Modules 2 and 3: extraction and transformation                        #
    ############################################################################

    def continuation(self, line):
        """Process a line of input if the user has already provided 5 movies.

        :param line: a user-supplied line of text
        :returns: a string containing the chatbot's response to the user input
        """
        # Do they want more recommendations?
        def cleanup():
            self.recommendation_idx = 0
            self.recommendation_titles = []
            self.user_ratings = np.zeros((self.ratings.shape[0]))
            self.user_ratings_count = 0
            self.prior_input = PriorInput()

        found_confirmation = any(ext in line.lower() for ext in self.yes)
        if found_confirmation:
            if self.recommendation_idx < len(self.recommendation_titles):
                recommendation = self.recommendation_titles[self.recommendation_idx]
                self.recommendation_idx += 1
                response = recommendation + "\n" + "Do you want to hear another recommendation? (Or enter :quit if you're done.)"
            else:
                cleanup()
                response = "You've seen all the movies I have to recommend you! " + self.goodbye()
        else:
            cleanup()
            response = self.goodbye()

        return response

    def get_recommendation_from_movie_title(self, line, movie_title):
        movie_idxs = self.find_movies_by_title(movie_title.replace('"', ''))    
        if len(movie_idxs) == 0:
            return "Sorry, I couldn't find a movie with the title {}. Can you tell me about another movie?".format(f'"{movie_title}"')
        elif len(movie_idxs) > 1:
            return "Sorry, I found multiple movies with the title {}. Can you specify?".format(f'"{movie_title}"')

        # get the sentiment
        sentiment = self.extract_sentiment(line)
        if sentiment == 0:
            return "I'm sorry, I'm not sure if you liked {}. Tell me more about it.".format(f'"{movie_title}"')
        elif sentiment == -1:
            response = "It seems like you didn't like {}. Can you clarify?".format(f'"{movie_title}"')
        elif sentiment == 1:
            response = "It seems like you liked {}. Tell me about another movie you liked.".format(f'"{movie_title}"')

        # get the rating
        self.user_ratings[movie_idxs[0]] = sentiment
        self.user_ratings_count += 1

        if self.user_ratings_count < 5:
            return f"Thanks for telling me about {movie_title}. Tell me about another movie you've seen."
        print(f"{response}\nFirst, give me a second to think about some recommendations...")

        # get the recommendations
        recommendations = self.recommend(self.user_ratings, self.ratings, k=self.max_movie_recommendations, creative=False)
        self.recommendation_titles = [self.titles[movie_idx][0] for movie_idx in recommendations]
        recommendation = f"I recommend you watch: {self.recommendation_titles[self.recommendation_idx]}\nDo you want another recommendation?"
        self.recommendation_idx +=1

        return recommendation

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
        if (line == ":quit"):
            return self.goodbye()

        # if the user is responding to getting another recommendation
        contains = lambda arr : any(ext in line.lower() for ext in arr)
        if self.user_ratings_count >= 5 and (contains(self.yes) or contains(self.no)):
            return self.continuation(line)

        if self.creative:
            if self.prior_input.status == PriorInputStatus.COMPLETE:
                self.prior_input.status = PriorInputStatus.NONE
                return self.get_recommendation_from_movie_title(self.prior_input.full_input, self.prior_input.movie)
            elif self.prior_input.status == PriorInputStatus.TYPO:
                if any(ext in line.lower() for ext in self.yes):
                    self.prior_input.status = PriorInputStatus.COMPLETE
                    return self.process(line)
                else:
                    self.prior_input.status = PriorInputStatus.NONE
                    return "Ok, let's start over. Tell me about a movie you've seen."
            elif self.prior_input.status == PriorInputStatus.DISAMBIGUATE:
                movie_options = self.prior_input.disambiguate_options
                # get the matching option (may be substring)
                matching_movies = [movie for movie in movie_options if line.lower() in movie.lower()]
                if len(matching_movies) == 1:
                    self.prior_input.status = PriorInputStatus.COMPLETE
                    self.prior_input.movie = matching_movies[0]
                    return self.process(line)
                elif len(matching_movies) > 1:
                    self.prior_input.status = PriorInputStatus.DISAMBIGUATE
                    self.prior_input.disambiguate_options = matching_movies
                    return f"Sorry please clarify again. Please enter one of the options above or 'none' if none of them are correct." + f"\n{matching_movies}"

                for movie in movie_options:
                    if line.lower() in movie.lower():
                        matching_movie = movie
                        break
                if matching_movie is not None:
                    self.prior_input.status = PriorInputStatus.COMPLETE
                    self.prior_input.movie = matching_movie
                    return self.process(line)

                elif any(ext in line.lower() for ext in self.no):
                    self.prior_input.status = PriorInputStatus.NONE
                    return "Ok, let's start over. Tell me about a movie you've seen."
                else:
                    return "Sorry, I didn't understand your response. Please enter one of the options above or 'none' if none of them are correct."
            elif self.prior_input.status == PriorInputStatus.NONE:
                self.prior_input.full_input = line
                # get the movie titles
                movie_titles = self.extract_titles(line)
                if len(movie_titles) == 0:
                    return "Sorry I couldn't find the movie in your response. Ensure that the movie title is in quotation marks!"
                elif len(movie_titles) > 1:
                    return "Please tell me about one movie at a time."

                # get the movie index
                movie_title = movie_titles[0]
                movie_idxs = self.find_movies_by_title(movie_title.replace('"', ''))
                if len(movie_idxs) == 0:
                    # get similar movies
                    similar_movies_idx = self.find_movies_closest_to_title(movie_title.replace('"', ''))
                    similar_movies = [self.titles[movie_idx][0] for movie_idx in similar_movies_idx]
                    if len(similar_movies) == 0:
                        return f"Sorry, I couldn't find any movies similar to {movie_title}! Please tell me about another movie."
                    similar_movie = self.remove_year(self.reconstruct_title(similar_movies[0]))
                    self.prior_input.movie = similar_movie
                    self.prior_input.status = PriorInputStatus.TYPO
                    return f"Sorry, I couldn't find {movie_title}! Did you mean {similar_movie}?"
                    # if no similar movies, return message
                elif len(movie_idxs) > 1:
                    self.prior_input.status = PriorInputStatus.DISAMBIGUATE
                    movie_titles = [self.titles[movie_idx][0] for movie_idx in movie_idxs]
                    self.prior_input.disambiguate_options = movie_titles
                    return f"Which movie did you mean? {', '.join(movie_titles)}"
                
                self.prior_input.movie = movie_title
                self.prior_input.status = PriorInputStatus.COMPLETE
                return self.process(line)
        # started mode
        else:
            # get the movie titles
            movie_titles = self.extract_titles(line)
            if len(movie_titles) == 0:
                return "Sorry I couldn't find the movie in your response. Ensure that the movie title is in quotation marks!"
            elif len(movie_titles) > 1:
                return "Please tell me about one movie at a time."

            # get the movie index
            movie_title = movie_titles[0]
            return self.get_recommendation_from_movie_title(line, movie_title)

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
        return re.findall('"([^"]*)"', preprocessed_input)

    def reconstruct_title(self, title):
        title_date_regex = "^(.+),\s(a|an|the|el|la|los|las|il|lo|l'|la|i|gli|le|les|der|den|dem|des|die|das)\s*\((\d{4})\)$"
        title_date_deconstruct = re.match(title_date_regex, title, re.IGNORECASE)

        title_only_regex = "^(.+),\s(a|an|the|el|la|los|las|il|lo|l'|la|i|gli|le|les|der|den|dem|des|die|das)$"
        title_only_deconstruct = re.match(title_only_regex, title, re.IGNORECASE)

        if title_date_deconstruct:
            new_title = '{} {} ({})'.format(title_date_deconstruct.group(2), title_date_deconstruct.group(1), title_date_deconstruct.group(3))
        elif title_only_deconstruct:
            new_title = '{} {}'.format(title_only_deconstruct.group(2), title_only_deconstruct.group(1))
        else:
            new_title = title
        return new_title

    def extract_text_in_paren(self, text):
        pattern = r'\((.*?)\)'
        matches = re.findall(pattern, text)
        return matches

    def extract_title_info(self, title):
        title_info = {}
        paren_info = self.extract_text_in_paren(title)
        title = self.reconstruct_title(title)

        if len(paren_info) == 0:
            title_info['title'] = title
            return title_info
        
        title_only = title[:title.find('(')].strip()
        title_info['title'] = title_only
        title_info['date'] = paren_info[0] # assuming that the only parentheses in title is the date

        return title_info

    def extract_movie_cand_info(self, movie):
        movie_info = {}
        paren_info = self.extract_text_in_paren(movie)
        titles = []
        date_regex = '^\d{4}$'
        aka_regex = '^a.k.a'
        movie = self.reconstruct_title(movie)

        if len(paren_info) == 0:
            movie_info['titles'] = [movie.lower()]
            return movie_info
        
        movie_title = movie[:movie.find('(')].strip()
        movie_title = self.reconstruct_title(movie_title)
        titles.append(movie_title.lower())
        for info in paren_info:
            if len(re.findall(date_regex, info)) != 0:
                movie_info['date'] = info
            elif len(re.findall(aka_regex, info)) != 0:
                aka_title = info[info.find('a.k.a.') + len('a.k.a.'):].strip()
                aka_title = self.reconstruct_title(aka_title)
                titles.append(aka_title.lower())
            else:
                info = self.reconstruct_title(info)
                titles.append(info.lower())
        movie_info['titles'] = titles
        return movie_info

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

        matches = []
        title_info = self.extract_title_info(title)
        for i, cand in enumerate(self.titles):
            curr_movie = cand[0]
            movie_info = self.extract_movie_cand_info(curr_movie)

            if 'date' not in title_info:
                if title_info['title'].lower() in movie_info['titles']:
                    matches.append(i)
            else:
                if title_info['title'].lower() in movie_info['titles'] and title_info['date'] == movie_info['date']:
                    matches.append(i)
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
        # remove periods and commas
        preprocessed_input = re.sub(r'[.,]', '', preprocessed_input)

        # remove titles
        for title in self.extract_titles(preprocessed_input):
            preprocessed_input = preprocessed_input.replace(f'"{title}"', "")
       
        # stem words
        preprocessed_input = " ".join([stemmer.stem(word) for word in preprocessed_input.split(" ")])
        is_negated = False

        sentiment = 0
        sentiment_rating = lambda word: 1 if word in self.positive_words else -1
        for word in preprocessed_input.split(" "):
            # check for negation
            if word in self.negating_words:
                is_negated = True
                continue
            if word not in self.positive_words and word not in self.negative_words:
                continue
            if is_negated:
                sentiment -= sentiment_rating(word.lower())
                is_negated = False
            else:
                sentiment += sentiment_rating(word.lower())
           
        return 1 if sentiment > 0 else -1 if sentiment < 0 else 0 

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
        # split input by titles
        titles = self.extract_titles(preprocessed_input)
       
        # create an array, splitting by titles
        for title in titles:
            preprocessed_input = preprocessed_input.replace(f'{title}', '')
        text = preprocessed_input.split('""')
        text = [t.strip() for t in text if t.strip() != '']

        text[-2] = f"{text[-2]} {text[-1]}"
        text = text[:-1]
        count_negatives = lambda sentence : len([word for word in sentence.split(" ") if word in np.append(self.negating_words, "but")])

        sentiments = []
        for i in range(len(titles)):
            if i == 0:
                sentiments.append((titles[i], self.extract_sentiment(text[i])))
                continue
            if count_negatives(text[i]) > 0:
                sentiments.append((titles[i], (1 if count_negatives(text[i]) % 2 == 0 else -1) * self.extract_sentiment(text[i-1])))
            else:
                sentiments.append((titles[i], self.extract_sentiment(text[i-1])))  

        return sentiments

    # Implementation by Christopher P. Matthews
    # From https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python in Python section
    def edit_distance(self, s, t):
        ''' From Wikipedia article; Iterative with two matrix rows. '''
        s = s.lower()
        t = t.lower()
        if s == t: return 0
        elif len(s) == 0: return len(t)
        elif len(t) == 0: return len(s)
        v0 = [None] * (len(t) + 1)
        v1 = [None] * (len(t) + 1)
        for i in range(len(v0)):
            v0[i] = i
        for i in range(len(s)):
            v1[0] = i + 1
            for j in range(len(t)):
                cost = 0 if s[i] == t[j] else 2
                v1[j + 1] = min(v1[j] + 1, v0[j + 1] + 1, v0[j] + cost)
            for j in range(len(v0)):
                v0[j] = v1[j]
                
        return v1[len(t)]

    def remove_year(self, s):
        if s.rfind('(') == -1:
            return s
        return s[:s.rfind('(')].strip()

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
        closest_movie_idx = []
        min_dist = 3
        for i in range(len(self.titles)):
            curr_title = self.reconstruct_title(self.titles[i][0])
            curr_title = self.remove_year(curr_title)
            if self.edit_distance(title, curr_title) <= max_distance and self.edit_distance(title, curr_title) == min_dist:
                closest_movie_idx.append(i)
                min_dist = self.edit_distance(title, curr_title)
            elif self.edit_distance(title, curr_title) <= max_distance and self.edit_distance(title, curr_title) < min_dist:
                closest_movie_idx = [i]
                min_dist = self.edit_distance(title, curr_title)
        return closest_movie_idx

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

        movies = []
        for (i, title) in [(idx, title) for idx in candidates for title in self.titles[idx]]:
            movie_year = re.search(r'\((\d{4})\)', title)
            if movie_year is not None:
                movie_year = movie_year.group(1).replace("(", "").replace(")", "")
                title = title.replace(f"({movie_year})", "").strip()
            
            if clarification == movie_year or clarification in title:
                movies.append(i)

        return movies

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

        for i in range(len(ratings)):
            for j in range(len(ratings[i])):
                if ratings[i][j] > threshold:
                    binarized_ratings[i][j] = 1
                elif ratings[i][j] == 0:
                    binarized_ratings[i][j] = 0
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
        if np.isnan(u).any() or np.isnan(v).any() or np.isinf(u).any() or np.isinf(v).any() or np.all(u == 0) or np.all(v == 0):
            return np.nan

        similarity = np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v)) 
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

        recommendations = np.zeros(user_ratings.shape)
        for i in range(len(user_ratings)):
            # if user has already rated the movie, skip
            if user_ratings[i] == 0:
                # calculate similarity between user and other users
                similarities = np.zeros(user_ratings.shape)
                # calculate similarity between user and other users
                for j in range(len(user_ratings)):
                    # if user has already rated the movie, skip
                    if user_ratings[j] == 0:
                        continue
                    # calculate similarity between user and other users
                    similarities[j] = self.similarity(ratings_matrix[i], ratings_matrix[j])
                recommendations[i] = user_ratings.dot(similarities)

        # replace 0 with -inf
        recommendations[recommendations == 0] = -np.inf

        # multiply by -1 to sort in descending order
        recommendations = -1 * recommendations
        recommendations = list(np.argsort(recommendations)[:k])
        
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
