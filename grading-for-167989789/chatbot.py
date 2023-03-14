# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util

import numpy as np
import re
import porter_stemmer
import random


# noinspection PyMethodMayBeStatic

class Chatbot:
    """Simple class to implement the chatbot for PA 7."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # Give your chatbot a new name.
        if creative:
            self.name = 'iHOP'
        else:
            self.name = 'moviebot'
        self.creative = creative

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')

        def transform(title):
            if title.endswith(", The"):
                title = "The " + title[0:-5]
            elif title.endswith(", A"):
                title = "A " + title[0:-3]
            elif title.endswith(", An"):
                title = "An " + title[0:-4]
            elif title.endswith(", L'"):
                title = "L'" + title[0:-4]
            elif title.endswith(", Le"):
                title = "Le " + title[0:-4]
            elif title.endswith(", La"):
                title = "La " + title[0:-4]
            elif title.endswith(", En"):
                title = "En " + title[0:-4]
            elif title.endswith(", El"):
                title = "El " + title[0:-4]
            elif title.endswith(", Les"):
                title = "Les " + title[0:-5]
            elif title.endswith(", Las"):
                title = "Las " + title[0:-5]
            elif title.endswith(", Los"):
                title = "Los " + title[0:-5]
            return title

        raw_titles = []
        alt_titles = {}
        for i in range(len(self.titles)):
            tokens = self.titles[i][0].split(' (')
            raw_title = transform(tokens[0])
            raw_titles.append(raw_title)
            if len(tokens) > 2:
                alts = tokens[1:-1]
                for alt in alts:
                    alt_title = alt.replace(')', '')
                    if 'aka' in alt_title:
                        alt_title = alt_title[4:]
                    elif 'a.k.a.' in alt_title:
                        alt_title = alt_title[7:]
                    alt_title = transform(alt_title)
                    alt_titles[alt_title] = i

        self.raw_titles = raw_titles
        self.alt_titles = alt_titles

        temp_sentiment = util.load_sentiment_dictionary('data/sentiment.txt')
        sentiment = {}
        p = porter_stemmer.PorterStemmer()
        for token in temp_sentiment:
            word = p.stem(token, 0, len(token) - 1)
            if word not in sentiment:
                if temp_sentiment[token] == 'pos':
                    sentiment[word] = 1
                else:
                    sentiment[word] = -1
        self.sentiment = sentiment

        self.dab_flag = False
        self.dab_movies = []
        self.dab_sentiment = 0

        self.rec_flag = False
        self.rated_movies = []
        self.user_ratings = np.zeros((len(self.titles), 1))
        self.rec_index = 0

        self.spellcheck_flag = False
        self.spellcheck_movies = []
        self.spellcheck_index = 0
        self.spellcheck_sentiment = 0

        ########################################################################
        # Binarize the movie ratings matrix.                             #
        ########################################################################
        ratings = self.binarize(ratings, 2.5)
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
        # Write a short greeting message                                 #
        ########################################################################

        name = self.name
        if self.creative:
            greeting_message = "Hi! I am {}. How can I make your day a little hoppy, my dear friend?".format(name)
        else:
            greeting_message = "Hi! I am {}. How can I help?".format(name)

        ########################################################################
        #                             END OF YOUR CODE                         #
        ########################################################################
        return greeting_message

    def goodbye(self):
        """
        Return a message that the chatbot uses to bid farewell to the user.
        """
        ########################################################################
        # Write a short farewell message                                 #
        ########################################################################

        if self.creative: 
            goodbye_message = "Appreciate ya, bunny buddy! May your day be filled with plenty of sunshine and lots of fresh veggie." + '''
              |\     /|           
              | \   / |         
              |  | |  |           
              \  | |  /          
               .'   '.           
              /       \        
              `'-. .-'`          
                _| |_               
              /`     `\          
             | /     \ |         
             |/       \|        
             /         \         
            |   .-~-.   |       
            \  {     }  /       
             \  '-=-'  /         
          .--'  ;---;  '--.   
         `-------' '-------`           
            '''
        else:
            goodbye_message = "Thank You! Have a nice day!"
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
        # Implement the extraction and transformation in this method,    #
        # possibly calling other functions. Although your code is not graded   #
        # directly based on how modular it is, we highly recommended writing   #
        # code in a modular fashion to make it easier to improve and debug.    #
        ########################################################################

        response = ""
        confirmations = ["yes", "yeah", "yep", "sure"]
        stops = ["no", "nah", "nope"]

        # For each of the following, prepare a starter version and a creative version
        if self.creative:
            groundings = ["Gotcha", "Okey dokey", "Alrighty"]
            catch_alls = [
                "I only recommend movies and eat carrots.. We could go back to movies or we could have some carrots.",
                "Alrighty!", "Let's go back to movies!"]
            clarifications = ["Forgive my rabbit brain, could you please clarify that for me?",
                              "I'm feeling a bit lost in the rabbit hole, which one did you mean?",
                              "I'm a little lost, would you mind clarify?"]
            apologies = ["Please forgive me like a rabbit who stole a farmer's carrot",
                         "Please forgive me, I was acting like a silly bunny",
                         "I'm sorry friend"]
            initial_recommend = ["Based on what you've said, I think this movie will be your carrot cake:",
                                 "I think you might also want to watch",
                                 "Given what you told me, I think you'd like"]
            follow_up = ["Can I hook you up with some more carrot recommendations?",
                         "Are you ready for the ultimate movie marathon, bunny? I've got more recommendations than you can hop to!",
                         "How about another one?"]
        else:
            groundings = ["Ok", "I see", "Got it"]
            catch_alls = ["Well, that's not really what I want to talk about right now, let's go back to movies!",
                          "Ok, got it.", "I see.", "Hmm, why not chat about movies?"]
            clarifications = ["Which one did you mean?", "Would you mind clarify?", "Can you clarify?"]
            apologies = ["I'm sorry", "Sorry", "I apologize"]
            initial_recommend = ["Given what you told me, I think you would like",
                                 "Based on what you said so far, I believe that you'd love",
                                 "I think you might also want to watch"]
            follow_up = ["Would you like more recommendations?", "How about another one?", "Do you want another recommendation?"]

        # temp = self.creative
        # self.creative = True
        movie_sentiments = self.extract_sentiment_for_movies(line)
        # self.creative = temp

        has_neutral = False

        for movie_sentiment in movie_sentiments:
            title = movie_sentiment[0]
            rating = movie_sentiment[1]
            if rating == 0:
                has_neutral = True
                continue
            movies = self.find_movies_by_title(title)
            if len(movies) == 1:
                temp = (movies[0], rating)
                self.rated_movies.append(temp)
                self.user_ratings[movies[0]] = rating
        recommendation = self.recommend(self.user_ratings, self.ratings)

        # This if statement is entirely creative, implement chatbot persona directly into the responses!
        if self.spellcheck_flag:
            confirmation_score = 0
            tokens = re.split(r'\W', line.lower())
            for sc_confirmation in confirmations:
                if sc_confirmation in tokens:
                    confirmation_score += 1
            for sc_stop in stops:
                if sc_stop in tokens:
                    confirmation_score -= 1
            if confirmation_score > 0:
                response = "{},".format(random.choice(groundings))
                movie_index = self.spellcheck_movies[self.spellcheck_index - 1]
                movie = self.raw_titles[movie_index]
                self.spellcheck_flag = False
                self.spellcheck_movies = []
                self.spellcheck_index = 0
                sentiment = self.spellcheck_sentiment
                if sentiment > 0:
                    response += " you liked \"{}\". Good choice! I give you my seal of approval.".format(movie)
                elif sentiment == 0:
                    response += " I'm not sure if you liked \"{}\".".format(movie)
                else:
                    response += " of course you realize, this means war when you said you didn't like \"{}\", but I respect your opinion.".format(movie)
                response += "."
            elif self.spellcheck_index < len(self.spellcheck_movies) and confirmation_score < 0:
                self.spellcheck_index += 1
                movie_index = self.spellcheck_movies[self.spellcheck_index]
                movie = self.titles[movie_index][0]
                response = "Ahhh, you have trouble spelling? Did you mean \"{}\"?".format(movie)
            else:
                self.spellcheck_flag = False
                self.spellcheck_movies = []
                self.spellcheck_index = 0
                response = "{},".format(random.choice(groundings))
                response += "I have long ears that help me hear very well, tell me about some other movies that you liked or hated!"

        elif self.rec_flag:
            confirmation_score = 0
            tokens = re.split(r'\W', line.lower())
            for rec_confirmation in confirmations:
                if rec_confirmation in tokens:
                    confirmation_score += 1
            for rec_stop in stops:
                if rec_stop in tokens:
                    confirmation_score -= 1
            if self.rec_index < 10 and confirmation_score > 0:
                movie_index = recommendation[self.rec_index]
                movie = self.titles[movie_index][0]
                self.rec_index += 1
                response = random.choice(initial_recommend) + " \"" + movie + "\". " + random.choice(follow_up)
            elif self.rec_index < 10 and confirmation_score < 0:
                self.rec_flag = False
                self.rec_index = 0
                self.rated_movies = []
                # starter versus creative
                response = "{},".format(random.choice(groundings))
                response += " got it."
            else:
                self.rec_flag = False
                self.rec_index = 0
                self.rated_movies = []
                # starter versus creative
                response = "{},".format(random.choice(groundings))
                if self.creative:
                    response += " I have long ears that help me hear very well, tell me about some other movies that you liked or hated!"
                else:
                    response += " tell me about some other movies that you liked or hated!"

        # This elif statement is entirely creative, implement chatbot persona directly into the responses!
        elif self.dab_flag:
            line = line.replace('.', '')
            dab_results = self.disambiguate(line, self.dab_movies)
            if len(dab_results) == 1:
                self.dab_flag = False
                self.dab_movies = []
                response = "{},".format(random.choice(groundings))
                movie = self.titles[dab_results[0]][0]
                sentiment = self.dab_sentiment
                temp = (movie, sentiment)
                self.rated_movies.append(temp)
                if sentiment > 0:
                    response += " you liked \"{}\". Good choice! I give you my seal of approval.".format(movie)
                elif sentiment < 0:
                    response += " of course you realize, this means war when you said you didn't like \"{}\", but I respect your opinion.".format(movie)
            elif len(dab_results) > 1:
                self.dab_movies = dab_results
                response = "I still found"
                for i in range(len(dab_results)):
                    response += " \"{}\"".format(self.titles[dab_results[i]][0])
                    if i < len(dab_results) - 1:
                        response += " and"
                    else:
                        response += " in my carrotbox."
                response += " {}".format(random.choice(clarifications))
            else:
                self.dab_flag = False
                self.dab_movies = []
                response = "I have long ears that help me hear very well, tell me about some other movies that you liked or hated!"

        elif movie_sentiments:
            dab_title = movie_sentiments[0][0]
            dab_movies = self.find_movies_by_title(dab_title)
            if len(dab_movies) == 1:
                neutral_movies = []
                response = "{},".format(random.choice(groundings))
                for i in range(len(movie_sentiments)):
                    movie = movie_sentiments[i][0]
                    sentiment = movie_sentiments[i][1]
                    if sentiment > 0:
                        response += " you liked \"{}\"".format(movie)
                    elif sentiment == 0:
                        response += " I'm not sure if you liked \"{}\"".format(movie)
                        neutral_movies.append(movie)
                    else:
                        response += " you didn't like \"{}\"".format(movie)
                    if i < len(movie_sentiments) - 1:
                        response += " and"
                    else:
                        response += "."
                if neutral_movies:
                    # starter versus creative
                    if self.creative:
                        response += " I am all about that rabbit life, so give me the deets! Tell me more about"
                    else:
                        response += " Tell me more about"
                    for i in range(len(neutral_movies)):
                        response += " \"{}\"".format(neutral_movies[i])
                        if i < len(neutral_movies) - 1:
                            response += " and"
                        else:
                            response += "."
                else:
                    if len(self.rated_movies) > 4:
                        self.rec_flag = True
                        movie_index = recommendation[0]
                        self.rec_index += 1
                        title = self.titles[movie_index][0]
                        response += " " + random.choice(initial_recommend) + " \"" + title + "\". " + random.choice(follow_up)
                    else:
                        # starter versus creative
                        if self.creative:
                            response += " I have long ears that help me hear very well, tell me about some other movies that you liked or hated!"
                        else:
                            response += " Tell me about some other movies that you liked or hated!"

            elif len(dab_movies) == 0:
                movies = self.find_movies_closest_to_title(dab_title)

                # TODO: This if statement is entirely creative, implement chatbot persona directly into the responses!
                if len(movies) > 0:
                    self.spellcheck_movies = movies
                    self.spellcheck_flag = True
                    self.spellcheck_sentiment = movie_sentiments[0][1]
                    self.spellcheck_index += 1
                    response = "Do you have trouble spelling? Did you mean \"{}\"?".format(self.raw_titles[movies[0]])
                else:
                    
                    # TODO: starter versus creative
                    if self.creative:
                        response = "{},".format(random.choice(apologies))
                        response += "I guess I must have been too busy eating carrrots to hear about \"{}\". Tell me about some other movies that you liked or hated!".format(dab_title)
                    else:
                        response = "{},".format(random.choice(apologies))
                        response += " I've never heard of \"{}\". Tell me about some other movies that you liked or hated!".format(dab_title)

            elif not has_neutral and len(dab_movies) > 1:
                # TODO: starter versus creative
                if self.creative:
                    response += "Hold on to your carrots, bunny, we've got multiple movies named \"{}\".".format(dab_title)
                else:
                    response = " I found more than one movie called \"{}\".".format(dab_title)

                # TODO: This if statement is entirely creative, implement chatbot persona directly into the responses!
                if self.creative:
                    self.dab_flag = True
                    self.dab_movies = dab_movies
                    self.dab_sentiment = movie_sentiments[0][1]
                    response += " I found"
                    for i in range(len(dab_movies)):
                        response += " \"{}\"".format(self.titles[dab_movies[i]][0])
                        if i < len(dab_movies) - 1:
                            response += " and"
                        else:
                            response += " in my carrotbox."
                response += " {}".format(random.choice(clarifications))

                # This elif statement is entirely creative, implement chatbot persona directly into the responses!
                # No need to edit lines with replace()
            elif self.creative and line.lower().startswith("i am ") or line.lower().startswith("i'm "):
                response = line.replace("I am", "")
                response = response.replace("i am", "")
                response = response.replace("I'm", "")
                response = response.replace("i'm", "")
                response = "Did I make you" + response
                response = response.replace(".", "")
                sentiment = self.extract_sentiment(line)
                if sentiment > 0:
                    response += "? That's great!"
                elif sentiment < 0:
                    response += "? I apologize. Have some carrots! They will make you feel better."
                else:
                    response = random.choice(catch_alls)

            # This elif statement is entirely creative, implement chatbot persona directly into the responses!
            # No need to edit lines with replace()
            elif self.creative and line.lower().startswith("can you ") or line.lower().startswith("could you "):
                response = line.replace("Can you", "")
                response = response.replace("can you", "")
                response = response.replace("Could you", "")
                response = response.replace("could you", "")
                response = "I'm sorry, I can't" + response
                response = response.replace("?", "")
                if "me" in response or "my" in response:
                    response = response.replace("me", "you")
                    response = response.replace("my", "your")
                else:
                    response = response.replace("your", "my")
                    response = response.replace("you", "me")
                response += ". I can recommend movies and eat carrot."

            # This elif statement is entirely creative, implement chatbot persona directly into the responses!
            # No need to edit lines with replace()
            elif self.creative and line.lower().startswith("what is ") or line.lower().startswith("what's "):
                response = line.replace("What is", "")
                response = response.replace("what is", "")
                response = response.replace("What's", "")
                response = response.replace("what's", "")
                response = "Sorry, I don't know" + response
                response = response.replace("?", "")
                if "me" in response or "my" in response:
                    response = response.replace("me", "you")
                    response = response.replace("my", "your")
                else:
                    response = response.replace("your", "my")
                    response = response.replace("you", "me")
                response += ". I know movies...... and CARROTS!"

            elif line.lower().startswith("who are you"):
                # starter versus creative
                if self.creative:
                    response = "I am {}. I am a wabbit!".format(self.name)
                else:
                    response = "I am {}.".format(self.name)
            else:
                response = random.choice(catch_alls)

        # This elif statement is entirely creative, implement chatbot persona directly into the responses!
        # No need to edit lines with replace()
        elif self.creative and line.lower().startswith("i am ") or line.lower().startswith("i'm "):
            response = line.replace("I am", "")
            response = response.replace("i am", "")
            response = response.replace("I'm", "")
            response = response.replace("i'm", "")
            response = "Did I make you" + response
            response = response.replace(".", "")
            sentiment = self.extract_sentiment(line)
            if sentiment > 0:
                response += "? That's great!"
            elif sentiment < 0:
                response += "? I apologize. Have some carrots! They will make you feel better."
            else:
                response = random.choice(catch_alls)

        # This elif statement is entirely creative, implement chatbot persona directly into the responses!
        # No need to edit lines with replace()
        elif self.creative and line.lower().startswith("can you ") or line.lower().startswith("could you "):
            response = line.replace("Can you", "")
            response = response.replace("can you", "")
            response = response.replace("Could you", "")
            response = response.replace("could you", "")
            response = "I'm sorry, I can't" + response
            response = response.replace("?", "")
            if "me" in response or "my" in response:
                response = response.replace("me", "you")
                response = response.replace("my", "your")
            else:
                response = response.replace("your", "my")
                response = response.replace("you", "me")
            response += ". I can recommend movies and eat carrot."

        # This elif statement is entirely creative, implement chatbot persona directly into the responses!
        # No need to edit lines with replace()
        elif self.creative and line.lower().startswith("what is ") or line.lower().startswith("what's "):
            response = line.replace("What is", "")
            response = response.replace("what is", "")
            response = response.replace("What's", "")
            response = response.replace("what's", "")
            response = "Sorry, I don't know" + response
            response = response.replace("?", "")
            if "me" in response or "my" in response:
                response = response.replace("me", "you")
                response = response.replace("my", "your")
            else:
                response = response.replace("your", "my")
                response = response.replace("you", "me")
            response += ". I know movies...... and CARROTS!"

        elif line.lower().startswith("who are you"):
            # starter versus creative
            if self.creative:
                response = "I am {}. I am a wabbit!".format(self.name)
            else:
                response = "I am {}.".format(self.name)
        else:
            response = random.choice(catch_alls)

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

        Note that this method is intentionally made static, as you shouldn't need
        to use any attributes of Chatbot in this method.

        :param text: a user-supplied line of text
        :returns: the same text, pre-processed
        """
        ########################################################################
        # Preprocess the text into a desired format.                     #
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
        potential_titles = re.findall('"([^"]*)"', preprocessed_input)
        if self.creative and not potential_titles:
            input_lower = " " + preprocessed_input.lower() + " "
            for title in self.raw_titles:
                escaped_title = re.escape(title.lower())
                results = re.findall(r" ({})\W".format(escaped_title), input_lower)
                if results:
                    potential_titles.append(title)
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
        def isSublist(test_list, sub_list):
            if all(x in test_list for x in sub_list):
                return True
            return False

        movies = []
        for i in range(len(self.raw_titles)):
            if title == self.raw_titles[i]:
                movies.append(i)
            elif title.lower() == "" + self.raw_titles[i].lower() + self.titles[i][0][-7:]:
                movies.append(i)
            elif self.creative and title.lower() == self.raw_titles[i].lower():
                movies.append(i)
            elif self.creative and isSublist(list(self.raw_titles[i].split(" ")), list(title.split(" "))):
                movies.append(i)

        if title in self.alt_titles.keys():
            movies.append(self.alt_titles[title])
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
        negation_words = ["no", "not", "none", "nobody", "nor", "never", "hardly"]
        degree_words = ["really", "very", "extremely", "greatly", "absolutely", "genuinely", "truly", "honestly",
                        "undoubtedly", "totally"]
        # TODO: add more tokens into strong_tokens
        strong_tokens = ["terrible", "horrible", "awful", "bad", "disgusting", "love", "amazing", "fantastic"]
        strong_words = []
        p = porter_stemmer.PorterStemmer()
        for token in strong_tokens:
            strong_words.append(p.stem(token, 0, len(token) - 1))
        sentiment_sum = 0
        negation = 1
        isMovie = False
        degree_count = 1
        tokens = preprocessed_input.lower().split()
        for token in tokens:
            if token.startswith('"'):
                if token.count('"') == 2:
                    continue
                else:
                    isMovie = True
                    continue
            if token.count('"') == 1:
                isMovie = False
                continue
            if isMovie:
                continue
            if "n't" in token or token in negation_words:
                negation = -1
                continue
            if token in degree_words:
                degree_count += 2
                continue
            temp = re.split(r'\W+', token)[0]
            word = p.stem(temp, 0, len(temp) - 1)
            if word in self.sentiment:
                extra_degree = 1
                if word in strong_words:
                    extra_degree = 3
                sentiment_sum += negation * degree_count * self.sentiment[word] * extra_degree
        sentiment_sum *= (preprocessed_input.count("!") + 1)
        if sentiment_sum > 0:
            if self.creative and sentiment_sum > 2:
                return 2
            else:
                return 1
        elif sentiment_sum == 0:
            return 0
        else:
            if self.creative and sentiment_sum < -2:
                return -2
            else:
                return -1

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
        clauses = re.split(r' but | But | however | however,| However,', preprocessed_input)
        if len(clauses) > 1:
            titles = self.extract_titles(clauses[1])
            if not titles:
                clauses = [preprocessed_input]
        prev_sentiment = 0
        for clause in clauses:
            titles = self.extract_titles(clause)
            if clause.startswith("not"):
                sentiment = -prev_sentiment
            else:
                temp = clause.lower()
                for title in titles:
                    temp = temp.replace(title.lower(), "")
                sentiment = self.extract_sentiment(temp)
                prev_sentiment = sentiment
            for title in titles:
                entry = (title, sentiment)
                sentiments.append(entry)
        return sentiments

    def editDistance(self, strm, strn, m, n):
        dp = [[0 for x in range(n + 1)] for x in range(m + 1)]
        for i in range(m + 1):
            for j in range(n + 1):
                if i == 0:
                    dp[i][j] = j
                elif j == 0:
                    dp[i][j] = i
                elif strm[i - 1] == strn[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    dp[i][j] = min(dp[i][j - 1] + 1,
                                   dp[i - 1][j] + 1,
                                   dp[i - 1][j - 1] + 2)
        return dp[m][n]

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
        items = []
        min_distance = max_distance + 1
        for i in range(len(self.raw_titles)):
            distance = self.editDistance(self.raw_titles[i].lower(), title.lower(), len(self.raw_titles[i]), len(title))
            if distance <= max_distance and distance <= min_distance:
                item = (i, distance)
                items.append(item)
                if distance < min_distance:
                    min_distance = distance
        results = []
        for item in items:
            if item[1] == min_distance:
                results.append(item[0])
        return results

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
        def isSublist(test_list, sub_list):
            if all(x in test_list for x in sub_list):
                return True
            return False

        movies = []
        for i in candidates:
            if isSublist(list(self.raw_titles[i].split(" ")), list(clarification.split(" "))):
                movies.append(i)
            elif clarification == self.titles[i][0][-5:-1]:
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
        # Binarize the supplied ratings matrix.                          #
        #                                                                      #
        # WARNING: Do not use self.ratings directly in this function.          #
        ########################################################################

        # The starter code returns a new matrix shaped like ratings but full of
        # zeros.
        zeros = np.where(ratings == 0)
        binarized_ratings = np.where(ratings > threshold, 1, -1)
        binarized_ratings[zeros] = 0

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
        if np.linalg.norm(u) * np.linalg.norm(v) == 0:
            return 0
        else:
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
        # Implement a recommendation function that takes a vector        #
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
        seenIndex = np.array([])
        scores = np.array([])

        for movie in range(len(ratings_matrix)):
            if user_ratings[movie] != 0:
                seenIndex = np.append(seenIndex, movie)

        for i in range(len(ratings_matrix)):
            movie_vector = ratings_matrix[i]

            score = 0
            for j in range(len(seenIndex)):
                index = int(seenIndex[j])
                temp = self.similarity(movie_vector,
                                       ratings_matrix[index]) * user_ratings[index]
                score += temp
            scores = np.append(scores, score)

        for i in range(len(scores)):
            if user_ratings[i] != 0:
                scores[i] = 0

        ind = np.argpartition(scores, -k)[-k:]
        top = scores[ind]

        a = list(ind[np.argsort(scores[ind])])

        return a[::-1]

        ########################################################################
        #                        END OF YOUR CODE                              #
        ########################################################################
        # return recommendations

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
        # TODO: Write here the description for your own chatbot!
        if self.creative:
            return """
            
                  |\     /|
                  |\\   //|
                  | \| |/ |
                  \ || || /
                   \||_||/
                   .'   '.
                   |o   o|
                  /=  Y  =\ 
                  `'-.^.-'`
                    _| |_
                  /`     `\             
                 |  (   )  |
                 /\  \ /  /\ 
                |  '._)_.'  |
                \           /
                 \ '.___.' /
              .--'  \---/  '--.
              `-------' '-------`
            I can chat about movies!
            """
        else:
            return "I can chat about movies."



if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
