# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util
import math
import numpy as np
import re
import string
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
        self.user_pref = np.zeros(len(self.titles))
        self.curr_user_pref = 0;
        self.all_user_recommendations = []
        self.curr_user_recommendations = []
        self.listen_yes_or_no = False;

        self.answer = False;
        self.clarify = False;
        self.curr_titles = [];
        self.prev_sentiment = "";

        self.related_movie_titles = [];
        ########################################################################
        # TODO: Binarize the movie ratings matrix.                             #
        ########################################################################

        # Binarize the movie ratings before storing the binarized matrix.
        self.ratings = self.binarize(ratings)
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
    def starter_process(self, line):
        if self.listen_yes_or_no:
            if line.lower() == "yes":
                if len(self.curr_user_recommendations) == 0:
                    curr_resp = "Sorry, I couldn't find more recommendations for you. Let's start over! Resetting everything. Tell me about another movie!"
                    self.user_pref = np.zeros(len(self.titles))
                    self.curr_user_pref = 0;
                    return curr_resp;
                else:
                    curr_recomm = self.curr_user_recommendations[0]
                    self.all_user_recommendations.append(curr_recomm)
                    if len(self.curr_user_recommendations) > 1:
                        self.curr_user_recommendations = self.curr_user_recommendations[1:]
                    else:
                        self.curr_user_recommendations = []
                    self.listen_yes_or_no = True;
                    resp = "Based on your what you told me here is a recommendation. I think you should watch " + curr_recomm + ". Would you like more recommendations?"
                    return resp;
            elif line.lower() == "no":
                self.listen_yes_or_no = False;
                resp = "Okay. Resetting all your recommendations. If you want to continue, tell me about another movie. If you are done just say :quit!"
                self.user_pref = np.zeros(len(self.titles))
                return resp;
            else:
                return "Couldn't understand what you want? Can you say yes or no?"

        titles = self.extract_titles(line)
        planned_response = ""
        if len(titles) == 0:
            return "I am sorry, couldn't understand what you mean. Can you tell me about another movie you have seen?"
        elif len(titles) > 1 and self.curr_user_pref < 5:
            return "I see, can you tell me about these movies one by one!"

        curr = titles[0]
        movie_titles = self.find_movies_by_title(curr);

        if len(movie_titles) == 0:
            return "Sorry I couldn't seem to find the movie. Tell me about another movie you liked."

        sent = self.extract_sentiment(line)
        if sent < 0:
            planned_response = "You seem to have not liked " + curr;
        elif sent > 0:
            planned_response = "You seem to have liked " + curr;
        else:
            return "I am not sure how you feel about this movie. Do you mind saying if you liked "+curr+ " or not?"
        for movie in movie_titles:
            self.curr_user_pref += 1;
            self.user_pref[movie] = sent;
        if self.curr_user_pref < 5:
            return planned_response +". Can you tell me about more movies?"
        # if enough recommendations
        recomms = self.recommend(self.user_pref, self.ratings, 10, False)
        recomms = [self.titles[x][0] for x in recomms]
        self.curr_user_recommendations = list(set(recomms).difference(self.all_user_recommendations))
        if len(self.curr_user_recommendations) == 0:
            curr_resp = "Sorry, I couldn't find more recommendations for you. Let's start over! Resetting everything. Tell me about another movie!"
            self.user_pref = np.zeros(len(self.titles))
            self.curr_user_pref = 0;
            return curr_resp;
        curr_recomm = self.curr_user_recommendations[0]
        self.all_user_recommendations.append(curr_recomm)
        if len(self.curr_user_recommendations) > 1:
            self.curr_user_recommendations = self.curr_user_recommendations[1:]
        else:
            self.curr_user_recommendations = []
        self.listen_yes_or_no = True;
        resp = planned_response + ". Based on your inputs here is a recommendation. I think you should watch " + curr_recomm + ". Would you like more recommendations?"
        return resp
    def check_question(self, line):
        question_identifiers = {"can": "I can't answer that", "how": "I don't know how", "why": "I don't know why", "when": "I couldn't tell you when", "who": "I don't know who it could have been", "where": "I genuinely have no idea where", "what": "I couldn't tell you"}
        question_reg = r'\w\?(\s|$)'
        matches = re.search(question_reg, line)
        if matches is not None:
            resp = ""
            curr = line.split(" ")
            curr = [x.strip("'s") for x in curr]
            for key,value in question_identifiers.items():
                if curr[0] in key or curr[0] == key:
                    resp = value;
                    break;
            return True, resp
        else:
            return False, ""
    def check_for_emotion(self, line):
        sent = self.extract_sentiment(line)
        response = ""
        if sent < 0:
            sadness = r"sad|lonely|depressed|inadequate|unhappy|miserable|upset"
            frustrated = r"angry|irritated|frustrated|provoked|resentful|irked"
            anxiety = r"anxious|worried|panicked|scared|jealous"
            if len(re.findall(sadness, line)) > 0:
                response = "I am so sorry that you are feeling dejected. Maybe I could recommend some movies for you to watch?"
            elif len(re.findall(frustrated, line)) > 0:
                response = "We all have our tipping points. If you want, I could make some movies for you to watch which can help get rid of your frustrations?"
            elif len(re.findall(anxiety, line)) > 0:
                response = "Fear not! Just kick back, relax and ask me for some movie recommendations!"
        if sent > 0:
            happy = r"happy|excited|ecstatic|elated|loved|accomplished"
            proud = r"proud|accomplished|rewarded|fulfilled"
            if len(re.findall(happy, line)) > 0:
                response = "So excited to hear that you are happy. Make your day better by asking for some movie recs!"
            elif len(re.findall(proud, line)) > 0:
                response = "You deserve this! Reward yourself by watching a movie. Maybe I can help you decide?"
        return response
    def creative_process(self, line):
        if self.listen_yes_or_no:
            if line.lower() == "yes":
                if len(self.curr_user_recommendations) == 0:
                    curr_resp = "Sorry, I couldn't find more recommendations for you. Let's start over! Resetting everything. Tell me about another movie!"
                    self.user_pref = np.zeros(len(self.titles))
                    self.curr_user_pref = 0;
                    return curr_resp;
                else:
                    curr_recomm = self.curr_user_recommendations[0]
                    self.all_user_recommendations.append(curr_recomm)
                    if len(self.curr_user_recommendations) > 1:
                        self.curr_user_recommendations = self.curr_user_recommendations[1:]
                    else:
                        self.curr_user_recommendations = []
                    self.listen_yes_or_no = True;
                    resp = "Based on your what you told me here is a recommendation. I think you should watch " + curr_recomm + ". Would you like more recommendations?"
                    return resp;
            elif line.lower() == "no":
                self.listen_yes_or_no = False;
                resp = "Okay. Resetting all your recommendations. If you want to continue, tell me about another movie. If you are done just say :quit!"
                self.user_pref = np.zeros(len(self.titles))
                return resp;
            else:
                return "Couldn't understand what you want? Can you say yes or no?"
        if self.clarify:
            if len(self.related_movie_titles) == 1:
                if line.lower() == "yes":
                    curr = self.find_movies_by_title(self.titles[self.related_movie_titles[0]][0])
                    sent = self.extract_sentiment(self.prev_sentiment)
                    self.clarify = False;
                    self.prev_sentiment = ""
                    self.user_pref[curr] = sent;
                    return "Perfect, tell me about some more movies you have liked/disliked!"
                elif line.lower() == "no":
                    self.clarify = False;
                    self.prev_sentiment = ""
                    return "Okay, then tell me about another movie you have watched?"
                else:
                    return "Couldn't tell if you are certain. Can you specify again just a simple yes or no would do!"
            out = self.disambiguate(line, self.related_movie_titles)
            if len(out) == 0:
                return "Looks I couldn't narrow down which one you wanted? Can you be a bit more clear? I am sorry this is totally my fault."
            else:
                self.related_movie_titles = []
                self.clarify = False;
                movie = self.titles[out[0]][0]
                return "Perfect, seems like you were talking about " + movie +". Tell me about some more movies you liked/disliked!"
        self.curr_titles = self.extract_titles(line)
        self.curr_user_pref += len(self.curr_titles)
        if len(self.curr_titles) == 0:
            flag, resp = self.check_question(line)
            planned_response = ""
            emotional_response = self.check_for_emotion(line)
            if flag:
                if resp == "":
                    return "I am so sorry I don't understand your question. Let's talk about some movies you like/dislike!"
                return resp + ". I am so sorry if that is disappointing but I am still learning! I can recommend you movies based on what you tell me though :)";
            elif len(emotional_response) > 0:
                return emotional_response
            else:
                return "Awesome to see you here. I don't think what you said made sense to me, but feel free to tell me about some movies you liked/disliked!"
        elif len(self.curr_titles) >= 1:
            out = self.extract_sentiment_for_movies(line)
            arr = []
            for elem in out:
                if elem[1] < 0:
                    arr.append("but it seems like you did not enjoy " + elem[0] + ".")
                elif elem[1] > 0:
                    arr.append("and it looks like you did enjoy " + elem[0] + ". ")
                else:
                    arr.append("and i couldn't understand how you felt about " + elem[0] + ". ")
                movie_titles = self.find_movies_by_title(elem[0])
                if len(movie_titles) == 0:
                    movie_titles = self.find_movies_closest_to_title(elem[0])
                    if len(movie_titles) == 0:
                        return "Oops, there were no matches for this movie. Guess I need to watch more movies. Let's talk about some other movie you have liked/disliked!"
                    elif len(movie_titles) == 1:
                        self.related_movie_titles += movie_titles
                        self.prev_sentiment = line;
                        self.clarify = True;
                        return "Did you mean " + self.titles[movie_titles[0]][0] + "?"
                resp = "Seems like a lot of movies match what you requested. Which of these were you talking about: "
                arr = []
                for movie in movie_titles:
                    arr.append(self.titles[movie][0])
                    self.related_movie_titles.append(movie)
                    self.user_pref[movie] = elem[1]
                if len(movie_titles) > 1:
                    self.prev_sentiment = line;
                    self.clarify = True;
                    fin = ", ".join(arr)
                    fin += "."
                    return resp + fin;
            planned_response = "".join(arr)
            planned_response = planned_response[4].upper() + planned_response[5:]
            if self.curr_user_pref < 5:
                return planned_response + " Tell me more about movies you have liked/disliked!"

        if self.curr_user_pref >= 5:
            recomms = self.recommend(self.user_pref, self.ratings, 10, False)
            recomms = [self.titles[x][0] for x in recomms]
            self.curr_user_recommendations = list(set(recomms).difference(self.all_user_recommendations))
            if len(self.curr_user_recommendations) == 0:
                curr_resp = "Sorry, I couldn't find more recommendations for you. Let's start over! Resetting everything. Tell me about another movie!"
                self.user_pref = np.zeros(len(self.titles))
                self.curr_user_pref = 0;
                return curr_resp;
            curr_recomm = self.curr_user_recommendations[0]
            self.all_user_recommendations.append(curr_recomm)
            if len(self.curr_user_recommendations) > 1:
                self.curr_user_recommendations = self.curr_user_recommendations[1:]
            else:
                self.curr_user_recommendations = []
            self.listen_yes_or_no = True;
            resp = planned_response + ". Based on your inputs here is a recommendation. I think you should watch " + curr_recomm + ". Would you like more recommendations?"
            return resp
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
        line = self.preprocess(line)
        if self.creative:
            response = self.creative_process(line)
        else:
            response = self.starter_process(line);
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
        reg = r'\"([^\"]+)\"'

        titles = list(re.findall(reg, preprocessed_input))
        if self.creative:
            if len(titles) == 0:
                curr = r'(?:liked|loved|hated|disliked)+ ([\w| ]+)?|(?:thought|believe) ([\w| ]+)? ?(?:was|is)+'
                out = re.findall(curr, preprocessed_input)
                for elem in out:
                    titles += list(elem)
                titles = [x for x in titles if len(x) != 0]
        return titles

    def find_articles(self, input): # change
        articles = ["the", "an", "a"]

        if self.creative:
            articles += ["la", "le", "les", "una", "un", "um", "uma", "los", "las"]

        spl = input.split(" ")
        ret = ""
        if spl[0] in articles:
            # check if title has parentheses
            parenth_reg = r"(\(.*\))"
            findings = re.findall(parenth_reg, input)
            if (len(findings) > 0):
                if spl[len(spl) - 1][0] == '(': # check if it's the last word
                    ret += " ".join(spl[1:len(spl) - 1])
                    ret += ", "
                    ret += spl[0]
                    ret += " " + spl[len(spl) - 1]
            else:
                ret += " ".join(spl[1:])
                ret += ", "
                ret += spl[0]
            return ret
        return input
        # if the word is an article discared it
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
        all_matches = []
        title = title.lower()
        title = self.find_articles(title)
        aka_reg = r"(a.k.a.|also known as|aka)"
        parenth_reg = r"(\(.*\)) \("
        for i, movie in enumerate(self.titles):
            curr_title = movie[0]
            curr_title = curr_title.lower()
            parentheses_removed = curr_title[:curr_title.find("(")].strip()
            if curr_title == title or title == parentheses_removed:
                all_matches.append(i)
            if self.creative:
                foreign_titles = re.findall(parenth_reg, curr_title);
                for j in range(len(foreign_titles)):
                    tit = foreign_titles[j]
                    tit = tit[1:-1]
                    tit = re.sub(aka_reg, ' ', tit).strip()
                    if title == tit:
                        all_matches.append(i)
        all_matches = list(set(all_matches))
        return all_matches


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
        extreme = {'great', 'best', 'worst', 'love', 'hate', 'awful', 'terrible', 'wonderful', 'majestic', 'cringe', 'awesome','amazing', 'favorite'}
        negation = {'wont','seldom', 'rarely', 'wasnt', 'werent', 'hasnt',  'never', 'not', 'hardly', 'cant', 'shouldnt', 'cannot', 'dont', 'didnt', }
        exaggerators = ['really', 'very', 'incredibly', 'extremely', 'highly']
        prev = 1
        weighted = False
        cum_score = 0
        # don't consider the title
        titles = self.extract_titles(preprocessed_input)
        for t in titles:
            preprocessed_input = preprocessed_input.replace(t, '')
        words = re.sub('[%s]' % re.escape(string.punctuation), '', preprocessed_input).split()
        for w in words:
            final_w = ""
            if w in extreme:
                weighted = True
            if w in self.sentiment:
                final_w = w
           #handle plural and past tense with additional 'd'
            elif ((w[-1] == 's' or w[-1] == 'd') and w[:-1] in self.sentiment):
                final_w = w[:-1]
           #handle past tense with additional 'ed'
            elif w[-2:] == 'ed' and w[:-2] in self.sentiment:
                final_w = w[:-2]
            elif w in exaggerators:
                continue;
           #skip this word
            else :
                prev = -1 if w in negation else 1
                continue
            cum_score += 1 * prev if self.sentiment[final_w] == "pos" else -1 * prev
            prev = -1 if final_w in negation else 1
        weight = 2 if (weighted and self.creative) else 1
        return weight * cum_score / abs(cum_score) if cum_score else cum_score
    def cleanup_titles(self, titles):
        for i in range(len(titles)):
            titles[i] = titles[i].strip("\"")
            titles[i] = titles[i].strip(".")
        return titles
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
        # i like harry potter but i don't like spy kids
        # i liked both spy kids and i robot
        # i liked both i robots and
        final = []
        titles = self.extract_titles(preprocessed_input)
        sentiment = self.extract_sentiment(preprocessed_input)
        intersection_indices = []
        connectors = ["and", "but", "although", "however", "whereas"]
        conjunction = r"and|or|also|plus"
        opposite = r'(?:but|however|yet)'

        split_line = preprocessed_input.lower().split(" ")
        copy_line = [x.replace('"','') for x in split_line]
        for i in connectors:
            if i in split_line:
                intersection_indices.append(split_line.index(i))
        intersection_indices.sort()
        for i in range(len(titles)):
            title = titles[i]
            split_title = title.lower().split(" ")
            #tindex = copy_line.index(split_title[0])
            for l in copy_line:
                if split_title[0] in l:
                    index = copy_line.index(l)
                    break
            sent_string = split_line[:index + len(split_title)]
            if len(intersection_indices) > 0:
                if intersection_indices[0] < index:
                    main_ind = -1;
                    for ind in intersection_indices:
                        if index > ind:
                            main_ind = ind
                    sent_string = split_line[main_ind:index + len(split_title)]
            fin_string = ' '.join(sent_string)

            sent_score = self.extract_sentiment(fin_string)
            if sent_score == 0:
                z = re.findall(opposite, fin_string)
                if len(re.findall(conjunction, fin_string)) != 0:
                    if len(final) > 0:
                        sent_score = final[-1][1]
                elif (z is not None):
                    if len(final) > 0:
                        sent_score = -final[-1][1]
            final.append((title, sent_score))
        return final
        #sentiment might be weighted so we should binarize it
        ans = [(t,(sentiment/abs(sentiment) if sentiment else sentiment)) for t in titles]
        #EXTENSION:
        #Consider cases where they should be opposite .i.e when there's "whereas", "however" etc.
        return ans
    def minimum_edit(self, w1, w2):
        w1 = w1.lower()
        w2 = w2.lower()

        cost = np.zeros((len(w1) + 1, len(w2) + 1))

        for i in range(1, len(w1) + 1):
            for j in range(1, len(w2) + 1):
                cost[i][0] = i;
                cost[0][j] = j;
        for j in range(1, len(w2) + 1):
            for i in range(1, len(w1) + 1):
                curr = 0;
                if w1[i - 1] == w2[j - 1]:
                    curr = 0;
                else:
                    curr = 2;
                min_cost = min(cost[i - 1][j] + 1, cost[i][j - 1] + 1, cost[i - 1][j - 1] + curr)
                cost[i][j] = min_cost;
        return cost[len(w1)][len(w2)]

    def remove_brackets(self, word):
        return word[:word.find("(")].strip()

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
        title = self.find_articles(title)
        all_ids = {}
        curr_closest = max_distance + 1;
        for i, movie in enumerate(self.titles):
            # remove potential brackets
            movie = movie[0]
            if movie.find('('):
                movie = self.remove_brackets(movie)
            curr_dist = self.minimum_edit(movie.lower(), title.lower())
            if curr_dist <=max_distance:
                if curr_dist in all_ids:
                    all_ids[curr_dist].append(i)
                else:
                    all_ids[curr_dist] = [i]
        curr_min = []
        for key, val in all_ids.items():
            if key < curr_closest:
                curr_closest = key
                curr_min = val;
        return curr_min

    def refine_movie_name(self, title):
        title = '('.join(title.split('(')[:-1])[:-1]
        return title;

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
        final_ids = []
        match_word = {"first": 1, "1":1, "most recent":1, "1st": 1,"second": 2,
                    "2":2, "2nd": 2,"third": 3, "3":3, "3rd": 3, "4":4, "fourth": 4,
                    "5":5, "4th": 4, "fifth": 5, "5th": 5, "sixth": 6, "6th": 6, "6":6,
                    "seventh": 7, "7th": 7, "7":7, "eigth": 8, "8th": 8, "8":8,
                    "ninth": 9, "9th": 9, "9":9}
        if re.match("none|no", clarification) is not None: # see if usersays none
            return final_ids;
        refined_clarification = [x for x in clarification.split() if x.lower() not in ['the', 'which', 'one', 'a', 'an', 'that']]
        refined = (' '.join(refined_clarification)).lower()
        # remove punctuation
        refined = re.sub(r"[.|!|?|;]$", '',refined)
        for c in candidates:
            title = self.titles[c][0];
            years = re.findall(r"\((.*?)\)", title);
            year = years[-1]
            title = self.refine_movie_name(title).lower();
            # if title or year is mentioned in clarification
            if title.find(refined) != -1 or title.find(year) != -1 or clarification.find(year) != -1:
                final_ids.append(c)
        if final_ids == []:
            for key, val in match_word.items():
                    if refined.find(key) != -1 or clarification.find(key) != -1:
                        final_ids.append(candidates[val - 1])
        return final_ids;


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
        binarized_ratings = np.where(ratings > threshold, 1, binarized_ratings);
        binarized_ratings = np.where(ratings <= threshold, -1, binarized_ratings);
        binarized_ratings = np.where(ratings == 0, 0, binarized_ratings)
        ###################################
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
        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        sim = np.dot(u, v);
        den = np.linalg.norm(u) * np.linalg.norm(v)
        if den == 0:
            return 0
        similarity = sim / den;
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
        user_ratings_vector = {}
        not_user_ratings_vector = {}
        new_ratings_vector = {}
        for index in range(len(user_ratings)):
           if user_ratings[index] == 0:
               not_user_ratings_vector[index] = user_ratings[index]
           else:
               user_ratings_vector[index] = user_ratings[index]
        for item in not_user_ratings_vector.items():
           rating_temp = 0
           for pair in user_ratings_vector.items():
               cosine_sim = self.similarity(ratings_matrix[item[0]], ratings_matrix[pair[0]])
               rating_temp += cosine_sim * pair[1]
           new_ratings_vector[rating_temp] = item[0]
        new_ratings_vecto_sorted = dict(sorted(new_ratings_vector.items(), reverse= True))
        curr = list(new_ratings_vecto_sorted.values())
        for index in range(k):
            recommendations.append(curr[index])
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
