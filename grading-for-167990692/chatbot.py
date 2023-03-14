# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util
import numpy as np
from porter_stemmer import PorterStemmer
import random
import re
import string


# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        self.name = 'MOOvies'
        
        self.creative = creative

        self.state = 'extract'
        self.recommendations = []
        self.curr_rec = 0
        self.focus = ("Let's talk about moooovies! ", "I'd rather we talk about mooovies, though. ", "That's interesting, but I think mooovies are coooler! ")
        self.focus_question = ("What's a mooovie you love? ", "Tell me about a mooovie you've seen recently. ", "What's a mooovie you'd never watch again? ")
        self.apology = ("I'm sorry. ", "Oops! ", "Awww shoot. ", "Whoops! ", "Oopsies... ", "My apologies. ")
        self.failed_to_recongize = ("I didn't recognize a title.", "I can't find a title.", "I can't tell where the title is.")
        self.no_movies = ("I haven't heard of ", "I don't know the mOoovie ")
        self.accknowledge = ("Moo Moo... ", "Ahhh I see. ", "MoooOooo... ", "Okay. ", "Ahhhh. ", "MmmmHmmm... ", "Gotcha. ", "Oh! ", "Ok, got it! ")
        self.starter = ("It seems you ", "You ", "From what I can tell, you ")
        self.liked = ("liked ", "enjoyed ", "appreciated ", "took pleasure in ", "adored ", "loved ", "took a liking to ", "approved of ")
        self.disliked = ("disliked ", "didn't enjoy ", "didn't like ", "were displeased with ", "didn't get a kick out of ", "disapproved of ")
        self.more_movies = ("Give me another mooooovie!", "MooooOoore please!", "Can I get another moo, moo, moovie?")
        self.rec = ("Want another rec?", "How about another one?", "One more?", "Would you like more recommendations?")
        self.no = ('no', 'nah', "nope", 'negative', "i'm good", "i'm okay", "not really", "it's okay")
        self.yes = ('yes', 'sure', 'yup', 'yeah', 'absolutely', 'sounds good', 'please', 'like', 'okay')
        self.think = ("think ", "believe ", "have a feeling ")
        self.like = ("like ", "enjoy ", "appreciate ", "take pleasure in ", "adore ", "love ", "take a liking to ", "approve of ")
        self.rec = ("Want another rec?", "How about another one?", "One more?", "Would you like more recommendations?")

        self.jokes = ("Why do cows have hooves? \n Because they lac-tose!", "Why did do cows wear a bell around its neck? \n Because its horn didn't work!",
                       "Why did the cow cross the road? \n To get to the udder side!", "What do you call a cow who hasn't had their cup of coffee? \n de-calf-inated!")
        
        self.edge_cases = (("it", 5841), ("ed", 545), ("m", 1014), ("o", 3720), ("pi", 1484), ("go", 2069), ("z", 4156), ("w.", 7061))

        self.closest_title = []
        self.line = ''

        self.strong_pos = (
        "love",
        "adore",
        "best",
        "amazing",
        "phenomenal",
        "marvelous",
        "ecstatic",
        "incredible",
        "hilarious",
        "dazzling",
        "riveting",
        "outstanding",
        "favorite",
        "insightful",
        "imaginative",
        )

        self.strong_neg = (
        "detest",
        "horrible",
        "despise",
        "horrific",
        "offensive",
        "nauseating",
        "miserable",
        "abhorrent",
        "moronic",
        "loathe",
        "disdain",
        "worst",
        "abhor",
        "vapid",
        "pathetic",
        )

        self.amplifiers = (
        "really",
        "very",
        "extremely",
        "especially",
        "tremendously",
        "overly",
        "especially",
        "immensely"
        )

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')

        self.movies = []
        for i in range(len(self.titles)):
            title = self.titles[i]
            title = title[0].split()
            name = title[:-1]
            year = title[-1]
            if self.creative:
                translation = re.search("\(([-'0-9a-zA-ZÀ-ÖØ-öø-ÿ\s,\.]+)\)", ' '.join(name))
                if translation:
                    alt_title = translation.group(1).split()
                    if alt_title[-1] in ['The', 'An', 'A', "El", "La", "Los", "Las", "Un", "Le", "Les", "Une", "Der", "Die", "Das", "Die"]:
                        alt_title = [alt_title[-1]] + alt_title[:-1]
                        alt_title[-1] = alt_title[-1][:-1]
                    self.movies.append((i, ' '.join(alt_title), year))
                    name = re.sub("(\([-'0-9a-zA-ZÀ-ÖØ-öø-ÿ\s,\.]+\))", '', ' '.join(name)).strip()
                    name = name.split()
        
            if name[-1] in ['The', 'An', 'A']:
                self.movies.append((i, ' '.join(name), year))
                name = [name[-1]] + name[:-1]
                name[-1] = name[-1][:-1]
            self.movies.append((i, ' '.join(name), year))

        p = PorterStemmer()
        self.stemmed_sentiments = {}
        for word in self.sentiment.keys():
            self.stemmed_sentiments[p.stem(word)] = self.sentiment[word]
        
        self.user_ratings = np.zeros(len(self.titles))
        self.num_user_ratings = 0

        ratings = self.binarize(ratings)

        # Binarize the movie ratings before storing the binarized matrix.
        self.ratings = ratings

    ############################################################################
    # 1. WARM UP REPL                                                          #
    ############################################################################

    def greeting(self):
        """Return a message that the chatbot uses to greet the user."""
        # ASCII art from https://en.wikipedia.org/wiki/Cowsay
        greeting_message = """
                +----------------------------+
                |      Let me recommend      |
                |      you a MOOooOvie.      |
                |  Tell me about one that    |
                |        you've seen.        |
                +----------------------------+
                        \   ^__^
                         \  (oo)\_______
                            (__)\       )\/\\
                                ||----w |
                                ||     ||
        """
        return greeting_message

    def goodbye(self):
        """
        Return a message that the chatbot uses to bid farewell to the user.
        """
        # ASCII art fromhttps://en.wikipedia.org/wiki/Cowsay
        goodbye_message = """
                +----------------------------+
                |        I think that        |
                |   you are like no udder!   |
                |       See you later...     |
                +----------------------------+
                        \   ^__^
                         \  (oo)\_______
                            (__)\       )\/\\
                                ||----w |
                                ||     ||
        """
        return goodbye_message

    ############################################################################
    # 2. Modules 2 and 3: extraction and transformation                        #
    ############################################################################
    def process_titles(self, titles, line):
        if not titles and not self.creative:
            return random.choice(self.apology) + random.choice(self.failed_to_recongize) + " Try putting quotations!"
        elif not titles and self.creative:
            if '"' in line and self.state == 'extract':
                return True, random.choice(self.apology) + random.choice(self.failed_to_recongize)
            else:
                return True, random.choice(self.accknowledge) + random.choice(self.focus) + random.choice(self.focus_question)
        
        return False, titles
    
    def process_movies(self, titles, line):
        movies = []
        for title in titles:
            match = self.find_movies_by_title(title)
            if match:
                for movie in match:
                    movies.append(movie)
            elif self.creative and self.state == 'extract':
                index = self.find_movies_closest_to_title(title)
                if index:
                    self.closest_title.append(self.titles[index[0]][0])
                    self.line = line
                    self.state = 'correction'
                    return True, "Did you mean " + self.titles[index[0]][0]
        movies = list(set(movies))

        if not movies:
            return True, random.choice(self.no_movies) + " or ".join(titles) + '.'
        if len(movies) > 1:
            response = 'There were multiple MOOooOovies with that title in my database: \n '
            for movie in movies:
                response += str(self.titles[movie][0]) + " \n "
            return True, response + "Can you please specify which movie?"

        return False, movies
    
    def process_sentiment(self, movies, line):
        movie = movies[0]
        sentiment = self.extract_sentiment(line)
        if sentiment == 0:
            return True, "Clairfy sentiment."
        
        opinion = random.choice(self.liked) if sentiment == 1 else random.choice(self.disliked)

        if self.user_ratings[movie] == 0:
                self.num_user_ratings += 1
        self.user_ratings[movie] = sentiment
    
        return False, random.choice(self.accknowledge) + random.choice(self.starter) + opinion +  "{}. ".format(self.titles[movie][0])
    
    def process_recommend(self, response):
        if self.num_user_ratings == 5:
            self.recommendations = self.recommend(self.user_ratings, self.ratings)
            film = self.titles[self.recommendations[self.curr_rec]][0]
            response += '\n\n'
            response += """
              (      )
              ~(^^^^)~        {}
               ) @@ \~_          |\\
              /     | \        \~ /
             ( 0  0  ) \        | |
              ---___/~  \       | |
               /'__/ |   ~-_____/ |
M              ~----~      ___---~
  O              |         |
   O     ((~\  _|         -|
   v      -_ \/ |        ~  |
    i   s   \_ /         ~  |
      e        |          ~ |
               |     /     ~ |
               |     (       |
                \     \      /\\
               / -_____-\   \ ~~-*
               |  /       \  \\
               / /         / /
             /~  |       /~  |
             ~~~~        ~~~~
            """.format(film)
            response += "\n\nBased on what you've told me, I would recommend " + film + ". " + random.choice(self.rec)
            self.curr_rec += 1
            self.state = 'recommend'
        else:
            response += random.choice(self.more_movies)

        return response
  
    def process_input(self, line):
        if self.creative:
            line = self.preprocess_input(line)
        titles = self.extract_titles(line)

        has_response, titles = self.process_titles(titles, line)
        if has_response:
            return titles
        
        has_response, movies = self.process_movies(titles, line)
        if has_response:
            return movies
        
        has_response, response = self.process_sentiment(movies, line)
        if has_response:
            return response
        
        return self.process_recommend(response)

    def correction_state(self, line):
        self.state = 'extract'
        line = line.split()
        for token in line:
            if any(token == n for n in self.no):
                return "Got it. Let's go back to movies."
            elif any(token == y for y in self.yes):          
                has_response, movies = self.process_movies(self.closest_title, self.line)
                if has_response:
                    return movies
                has_response, response = self.process_sentiment(movies, self.line)
                if has_response:
                    return response
                return self.process_recommend(response)
        
        return "didn't quite get that."

    def recommend_state(self, line):
        self.num_user_ratings = 0
        line = line.split()
        for token in line:
            if any(token == n for n in self.no):
                self.state = 'extract'
                response = random.choice(self.accknowledge) + "Tell me about another movie."
            elif any(token == y for y in self.yes):
                movie = self.titles[self.recommendations[self.curr_rec]][0]
                response = "I " + random.choice(self.think) + "you will " + random.choice(self.like) + movie + ". " + random.choice(self.rec)
                self.curr_rec += 1
            else:
                response = "didn't quite get that."

        return response


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
        if "joke" in line.lower() and "was a joke" not in line.lower():
            response = random.choice(self.jokes)
        elif self.state == 'extract':
            response = self.process_input(line)
        elif self.state == 'recommend':
            response = self.recommend_state(line)
        elif self.state == 'correction':
            response = self.correction_state(line)
            self.closest_title = []
            self.line = ''

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
        return text

    def preprocess_input(self, text):
        if '"' in text:
            return text
        input = [token.lower() for token in text.split()]
        has_year = False
        if any(re.match('(\([0-9]{4}(?:-(?:[0-9]{4})?)?\))', t) for t in input):
            has_year = True

        candidates = []
        edge_case_indices = []
        for i in range(len(input)):
            for j in range(i + 1, len(input) + 1):
                line = ' '.join(input[i:j])
                for movie in self.movies:
                    title = movie[1].lower()
                    if 'a.k.a.' in title:
                        title = title[7:]
                    if (any(line == t[0] for t in self.edge_cases)):
                        edge_case_indices.append((i, j))
                        break
                    if has_year and title + ' ' + movie[2] == line:
                        candidates.append((movie[1] + ' ' + movie[2], i, j))
                    elif not has_year and line == title:
                        candidates.append((movie[1], i, j))
                        
        indices = []
        for i in range(len(candidates)):
            is_sub_string = False
            for j in range(len(candidates)):
                if i == j:
                    continue
                if candidates[i][0].lower() == candidates[j][0].lower():
                    is_sub_string = False
                elif candidates[i][0].lower() in candidates[j][0].lower():
                    is_sub_string = True
                    break
            if not is_sub_string:
                indices.append((candidates[i][1], candidates[i][2]))
        to_add = []
        if not indices:
            indices = edge_case_indices
        else:
            for i in edge_case_indices:
                edge_case = ' '.join(input[i[0]:i[1]])
                is_edge_case = True
                for j in indices:
                    title = ' '.join(input[j[0]:j[1]])
                    if edge_case in title and (i[0] >= j[0] and i[1] <= j[1]):
                        is_edge_case = False

                if is_edge_case:
                    to_add.append((i[0], i[1]))

            indices = indices + to_add

        indices = list(set(indices))
        for i in indices:
            input[i[0]] = '"' + input[i[0]]
            input[i[1]- 1] = input[i[1] - 1] + '"'
        
        return ' '.join(input)

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
        titles = re.findall(r'"(.*?)"', preprocessed_input)
        return titles

    def find_movies_by_title(self, title):
        """ Given a movie title, return a list of indices of matching movies.

        - If no movies are found that match the given title, return an empty
        list.
        - If multiple movies are found that match the given title, return a list
        containing all of the indices of these matching movies.
        - If exactly one movie is found that matches the given title, return a
        list that contains the index of that matching movie.

        Example:
          ids = chatbot.find_movies_by_title('Titanic')
          print(ids) // prints [1359, 2716]

        :param title: a string containing a movie title
        :returns: a list of indices of matching movies
        """
        title = title.lower()

        for t in self.edge_cases:
            if title == t[0]:
                return [t[1]]

        name = title.split()

        if len(name) == 0:
            return []

        year = re.search(r'(\([0-9]{4}(?:-(?:[0-9]{4})?)?\))', name[-1])
        if not year and self.creative:
            name.append('')
        elif not year:
            name.append('(')

        name = ' '.join(name)
        indices = []

        for i in range(len(self.movies)):
            movie = self.movies[i][1] + ' ' + self.movies[i][2]
            if name in movie.lower():
                indices.append(self.movies[i][0])
            elif self.creative and not year and name[:-1] + ':' in movie.lower():
                indices.append(self.movies[i][0])
        
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
        stemmer = PorterStemmer()
        negation_words = ["didn't", "not", "isn't", "never"]
        negation = False
        amp = False

        sentiment = 0

        input = re.sub(r'"(.*?)"', '', preprocessed_input).strip()
        input = input.split()

        for word in input:
            if any(p in word for p in string.punctuation):
                if any(p == word[-1] for p in string.punctuation):
                    word = word[:-1]
                negation = False
            if word in negation_words:
                negation = True
            stemmed = stemmer.stem(word)
            if stemmed in self.stemmed_sentiments:
                label = self.stemmed_sentiments[stemmed]
                if label == 'pos':
                    sentiment = sentiment - 1 if negation else sentiment + 1
                elif label == 'neg':
                    sentiment = sentiment + 1 if negation else sentiment - 1
            if self.creative:
                if amp:
                    sentiment = sentiment + 1 if sentiment > 0 else sentiment - 1
                    amp = False
                if word in self.strong_pos:
                    sentiment = sentiment - 1 if negation else sentiment + 1
                elif word in self.strong_neg:
                    sentiment = sentiment + 1 if negation else sentiment - 1
                elif word in self.amplifiers:
                    if sentiment != 0:
                        sentiment = sentiment + 1 if sentiment > 0 else sentiment - 1 
                    else:
                        amp = True

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
        stemmer = PorterStemmer()
        negation_words = ["didn't", "not", "isn't", "never"]
        negation = False
        conjunctions = ["and", "but", "or", "since", "because", "however", "because"]
        #maybe split on conjunctions???
        sentiments = []
        input = re.sub(r'"(.*?)"', '', preprocessed_input).strip()
        input = input.split()

        titles = self.extract_titles(preprocessed_input)
        prevSentiment = None
        for title in titles:
            input = preprocessed_input.split('"' + title + '"')[0]
            listInput = input.split()
            input += '"' + title + '"'
            sentiment = self.extract_sentiment(input)
            #first iter check that sentiment was calcualted correctly
            if sentiment == 0 and prevSentiment == None:
                pInput = preprocessed_input.split()
                for i in range(1,len(pInput)):
                    if pInput[i] not in conjunctions and pInput[i] != ('"' + title + '"'):
                        input += pInput[i]
                    else:
                        sentiment = self.extract_sentiment(input)
                        break                           
            #if there is a conjunction, find the most recent conjunction to determine sentiment
            for elem in reversed(listInput):
                if elem in ['but','however']:
                    if prevSentiment == -1:
                        sentiment = 1
                    elif prevSentiment == 1:
                        sentiment = -1
                    else:
                        sentiment = 0
                    break
                elif elem in conjunctions:
                    sentiment = prevSentiment
                    break
            sentiments.append((title, sentiment))
            prevSentiment = sentiment
        return sentiments
    
    def levenshtein_distance(self, x, y):
        m, n = len(x), len(y)
        d = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(1, m + 1):
            d[i][0] = i
            
        for j in range(1, n + 1):
            d[0][j] = j
            
        for j in range(1, n + 1):
            for i in range(1, m + 1):
                if x[i - 1] == y[j - 1]:
                    substitution_cost = 0
                else:
                    substitution_cost = 2
                d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + substitution_cost)

        return d[m][n]

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
        has_year = False
        if any(re.match('(\([0-9]{4}(?:-(?:[0-9]{4})?)?\))', t) for t in title):
            has_year = True
        
        matches = []
        best_matches = []
        for movie in self.movies:
            film = movie[1] if not has_year else movie[1] + ' ' + movie[2]
            dist = self.levenshtein_distance(title.lower(), film.lower())
            if dist <= max_distance:
                matches.append((dist, movie[0]))

        if matches:
            matches.sort()
            min_edit = matches[0][0]
            for match in matches:
                if match[0] == min_edit:
                    best_matches.append(match[1])

        return best_matches

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
        indices = []
        temp = clarification.lower().split()

        order = ('first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'nineth', 'tenth')
        recent = ('most recent', 'the latest', 'top')
        is_order = False
        if any(t in order for t in temp) or any(p in clarification for p in recent) or any(t.isdigit() for t in temp):
            is_order = True
        year = re.search(r'(\([0-9]{4}(?:-(?:[0-9]{4})?)?\))', clarification)
        if year:
            clarification = '(' + clarification + ')'
        elif is_order:
            for token in temp:
                index = None
                if token in order:
                    index = order.index(token)
                    break
                elif token.isdigit() and int(token) < len(candidates):
                    index = int(token) - 1
                    break

            if not index and any(p in clarification for p in recent):
                index = 0

            if index != None:
                return [candidates[index]]

        for index in candidates:
            if clarification in self.titles[index][0]:
                indices.append(index)

        return indices

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
        # The starter code returns a new matrix shaped like ratings but full of
        # zeros.
        binarized_ratings = np.where(ratings == 0, 0, np.where(ratings > 2.5, 1, -1))
        return binarized_ratings

    def similarity(self, u, v):
        """Calculate the cosine similarity between two vectors.

        You may assume that the two arguments have the same shape.

        :param u: one vector, as a 1D numpy array
        :param v: another vector, as a 1D numpy array

        :returns: the cosine similarity between the two vectors
        """
        if np.linalg.norm(u) == 0 or np.linalg.norm(v) == 0:
            return 0.0
        return np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))

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
        ratings = []
        unrated_indicies = np.where(user_ratings == 0)[0]
        rated_indicies = np.nonzero(user_ratings)[0]
        user_rates = [user_ratings[i] for i in rated_indicies]

        for i in unrated_indicies:
            similarities = []
            r_i = ratings_matrix[i]
            for j in rated_indicies:
                r_j = ratings_matrix[j]
                similarities.append(self.similarity(r_i, r_j))
            predicted_rating = np.dot(np.array(similarities), np.array(user_rates))
            ratings.append((predicted_rating, i))

        recommendations = sorted(ratings, key=lambda x: x[0], reverse=True)
        top_k = [choice[1] for choice in recommendations[:k]]

        return top_k


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
        Hi! This is Moovies, your friendly neighborhood mooovie recommendations
        chatbot! Give Moovies some movies you enjoy (or not so much) and Moovies
        will take your preferences, extract their sentiment, and then uses collaborative
        filtering to recommend new flicks to binge! 
        
        Place movies in quotation marks (unless in creative mode!) so that Moovies can
        give the best recommendations! 
        """


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
