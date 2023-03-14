# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import numpy as np
from porter_stemmer import PorterStemmer
import random
import re
import util

# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        self.name = 'CASS'

        self.creative = creative
        self.stem = PorterStemmer()

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')

        for k, v in list(self.sentiment.items()):
            del self.sentiment[k]
            k = self.stem.stem(k)
            self.sentiment[k] = v
       
        self.ratings = self.binarize(ratings)
        self.num_rated = 0
        self.user_responses = np.zeros(len(self.titles))

    ############################################################################
    # 1. WARM UP REPL                                                          #
    ############################################################################

    def greeting(self):
        """Return a message that the chatbot uses to greet the user."""

        greeting_message = [
            "I will be recommending a movie for you! Please tell me how you felt about a movie you've seen in the past.",
            "I'm happy to recommend a movie for you! Please let me know about a movie you've viewed in the past.",
            "Do you like movies? I do! I want to recommend a movie for you, so please tell me about how you felt about a movie you've seen.",
        ]
        return random.choice(greeting_message)

    def goodbye(self):
        """
        Return a message that the chatbot uses to bid farewell to the user.
        """

        goodbye_message = [
            "Have a nice day!",
            "It was fun talking to you! See you soon!",
            "This was a great conversation! Catch you later!",
            "I hope this talk about movies was engaging! Bye bye!",
            "As Han Solo said, 'May the Force be with you.' Bye!",
            "Great talking to you! 'I'll be back...' Oh wait, that was the Terminator's line."
            ""
        ]

        return random.choice(goodbye_message)

    ############################################################################
    # 2. Modules 2 and 3: extraction and transformation                        #
    ############################################################################

    def sentiment_responses(self, sentiment, title):
        responses_good_movies = ["\"{}\" is a great movie! Please tell me about another.".format(title), "Okay, you liked \"{}\"! Tell me what you thought of another movie".format(title), "I'm glad to hear you liked \"{}\". Tell me about another movie!".format(title)]
        responses_bad_movies = ["I'm sorry to hear you didn't like \"{}\". Please tell me about another movie!".format(title), "It seems like you didn't enjoy \"{}\". Tell me about another movie!".format(title), "I'm hearing that you didn't like \"{}\". How did you feel about another movie?".format(title)]
        
        if sentiment > 0:
            return random.choice(responses_good_movies)
        if sentiment < 0:
            return random.choice(responses_bad_movies)
        else:
            return "Sorry, I'm not sure how you felt about " + title + ". Tell me more about it."

    def recommend_responses(self):
        if "y" in input("I have enough information now! Can I recommend a movie for you? [Y/N]").lower():
            rec_movies = self.recommend(self.binarize(self.user_responses), self.ratings)
            movies = [self.titles[i][0] for i in rec_movies]
            for i in range(len(movies)):
                if "n" in input("I think you would like \"" + movies[i] + "\". Can I recommend another movie for you? [Y/N]").lower():
                    return "Okay. Feel free to keep telling me about movies you like and I can provide more recommendations when you're ready! You can also type :quit if you're done."
            return "I've given all my movie recommendations based on what you've told me so far. Keep telling me about movies you like and I can provide more recommendations!"
        else:
            return "Okay! Then tell me about another movie."

    def arbitrary_responses(self, num):
        responses_1 = ["Sorry, I'm not sure if I can help you with that. I specialize in movie recommendations so let's talk about movies!", "Sorry, I'm not good with those kinds of inquiries. I'm best at giving movie recommendations so tell me more about movies you've seen!", "Hm, I'm not sure if I want to talk about that right now. Could you tell me more about movies instead?"]
        responses_2 = ["Hm, I'm best equipped to give you recommendations for movies. Let's talk about movies instead!", "Sorry, I don't know much about that topic! How about I recommend you a movie instead?"]
        if num == 1:
            return random.choice(responses_1)
        else:
            return random.choice(responses_2)

    
    def update_data(self, index, sentiment):
        if self.user_responses[index] != 0:
            self.user_responses[index] = sentiment
        else:
            self.num_rated += 1
            self.user_responses[index] = sentiment


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
        
        if self.creative:
            data = self.preprocess(line)
            sentiment = 0
            titles = list(set(self.extract_titles(data)))
            
            
            # When no movie input is given
            if len(titles) == 0:
                # handling arbitrary inputs/questions
                arbitrary_inputs_1 = ["can", "can you", "will you", "able", "able to", "you"]
                arbitrary_inputs_2 = ["what", "what is", "how"]
                if any(arb_word in data["text"] for arb_word in arbitrary_inputs_1):
                    return self.arbitrary_responses(1)
                elif any(arb_word in data["text"] for arb_word in arbitrary_inputs_2):
                    return self.arbitrary_responses(2)

                no_input_response = [
                    "I'm sorry. I couldn't find a movie that corresponds to your input. Please try again!",
                    "Hmmm... Seems like there isn't a movie that matches your input. Please try again!",
                    "My apologies. It seems like there was a mistake in your input. Please try again!"
                ]
                hint_response = " Try putting your movie in quotes or make sure your input is spelled correctly!"
                return random.choice(no_input_response) + hint_response

            if self.num_rated >= 5:
                return self.recommend_responses()

            if len(titles) == 1:
                title = titles[0]
                movie_indices = self.find_movies_by_title(titles[0])
                if len(movie_indices) == 1:
                    sentiment = self.extract_sentiment(data)
                    self.update_data(movie_indices[0], sentiment)
                    return self.sentiment_responses(sentiment, title)
                
                elif len(movie_indices) > 1:
                    return self.narrow_titles(movie_indices, data)

                # Edge case: typo handling
                if len(movie_indices) == 0:
                    mis_title = data["titles"][0]
                    options = self.find_movies_closest_to_title(mis_title)
                    if len(options) == 0:
                        return "Sorry, I couldn't quite catch what movie you were talking about. Could you tell me again or talk about another movie?"
                    if len(options) == 1:
                        found = self.titles[options[0]][0]
                        if "y" in (input("Is this the movie you are referring to: \"" + found + "\"?")).lower():
                            sentiment = self.extract_sentiment(data)
                            self.update_data(options[0], sentiment)
                            return self.sentiment_responses(sentiment, found)
                        else:
                            return "I'm sorry about that. Could you tell me about another movie?"
                    else:
                        to_choose = []
                        for i in options:
                            to_choose.append(self.titles[i][0])
                        for i, m in enumerate(to_choose):
                            print(str(i + 1) + ". " + "\"" + m + "\"" + "\n")
                        if "y" in (input("Is the movie you're referring to any of these? [Y/N]")):
                            index = int(input("Please select the number of the movie you are referring to")) - 1
                            act_title = self.titles[options[index]][0]
                            sentiment = self.extract_sentiment(data)
                            self.update_data(options[index], sentiment)
                            return self.sentiment_responses(sentiment, act_title)
                        else:
                            return "I'm sorry about that. Could you tell me about another movie?"
                else:
                    self.update_data(self.find_movies_by_title(title), self.extract_sentiment(data))
           
            else:
                positive_responses = ["I'm happy to hear that you enjoyed \"{}\"!", "I'll have to remember to watch \"{}\" sometime if it's that good!", "\"{}\" is a great movie!", "You must have great taste to like \"{}\"!"]
                negative_responses = ["I'm sorry you didn't enjoy \"{}\".", "\"{}\" must not have been to your liking!", "I'll keep in mind that \"{}\" wasn't your favorite movie."]
                sentiments = self.extract_sentiment_for_movies(data)
                response = ""
                for movie, sentiment in sentiments:
                    movie_indices = self.find_movies_by_title(movie)
                    if len(movie_indices) == 1:
                        ind = movie_indices[0]
                    elif len(movie_indices) > 1:
                        ind = self.narrow_titles(movie_indices, data, "not")
                    if sentiment > 0:
                        response += random.choice(positive_responses).format(self.titles[ind][0]) + " "
                    elif sentiment < 0:
                        response += random.choice(negative_responses).format(self.titles[ind][0]) + " "
                response += "Please tell me about another movie!"
                return response     
            return "Something went wrong! Please try again!"
            
        else:
            data = self.preprocess(line)
            title = []
            sentiment = 0
            if len(data["titles"]) == 0:
                return "Sorry, I couldn't find a movie in your response. Could you please list the movie title in quotations?"
            if len(data["titles"]) > 1:
                return "I found more than one movie in your response. Could you please tell me how you felt about one movie at a time?"
            if len(data["titles"]) == 1:
                title_s = data["titles"][0]
                title = self.find_movies_by_title(title_s)
                if (len(title) > 1):
                    return "I found more than one movie called " + title_s + ". Can you be more specific by listing the title and then the year in parentheses, or list another movie?"
                if (len(title) == 0):
                    return "I'm sorry, I've never heard of \"" + title_s + "\". Can you try checking if the title was correctly capitalized and spelled or tell me about another movie?"
                sentiment = self.extract_sentiment(data)
                self.num_rated += 1
                self.user_responses[title] = sentiment
            if self.num_rated > 5:
                return self.recommend_responses()
            return self.sentiment_responses(sentiment, title_s)


    def narrow_titles(self, movie_indices, data, flag="process"):
        # elif len(movie_indices) > 1:
        #             # disambiguation case
        for i, index in enumerate(movie_indices):
            print(str(i + 1) + ". " + self.titles[index][0])
        clarification = input("There are multiple movies that match your input. Out of these, which one did you mean?")
        options = self.disambiguate(clarification, movie_indices)
        if len(options) == 0:
            return "Sorry, I couldn't quite catch what movie you were talking about. Could you tell me again or talk about another movie?"
        if len(options) == 1:
            found = self.titles[options[0]][0]
            if "y" in (input("Is this the movie you are referring to: \"" + found + "\"?")).lower():
                if flag == "process":
                    sentiment = self.extract_sentiment(data)
                    self.update_data(options[0], sentiment)
                    return self.sentiment_responses(sentiment, found)
                else:
                    return options[0]
            else:
                return "I'm sorry about that. Could you tell me about another movie?"
        #case where disambiguate didn't narrow down to 1 movie
        else:
            while len(options) > 1:
                for i, index in enumerate(options):
                    print(str(i + 1) + ". " + self.titles[index][0])
                clarification = input("Sorry, there are still multiple movies that match your input. Out of these, which one did you mean?")
                options = self.disambiguate(clarification, options)
            if len(options) == 0:
                return "Sorry, I couldn't quite catch what movie you were talking about. Could you tell me again or talk about another movie?"
            if len(options) == 1:
                found = self.titles[options[0]][0]
                if "y" in (input("Is this the movie you are referring to: \"" + found + "\"?")).lower():
                    sentiment = self.extract_sentiment(data)
                    self.update_data(options[0], sentiment)
                    return self.sentiment_responses(sentiment, found)
                else:
                    return "I'm sorry about that. Could you tell me about another movie?"
        return

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
        
        data = {}   
        data["text"] = text
        text_in_quotes = re.findall(r'"(.*?)"', text)
        data["titles"] = text_in_quotes if len(text_in_quotes) > 0 else []
        
        return data

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
        titles = preprocessed_input["titles"] # ["titanic"]
        if self.creative and len(titles) == 0:  
            parts = preprocessed_input["text"].lower().split()
            for movie in [x[0] for x in self.titles]:
                parts = [re.sub(r'[^\w\s\d]', '', word).strip() for word in parts]
                mov_parts = movie.lower().split()
                the_f = False
                a_f = False
                an_f = False
                if "the" == mov_parts[-2]:
                    the_f = True
                if "a" == mov_parts[-2]:
                    a_f = True
                if "an" == mov_parts[-2]:
                    an_f = True
                if mov_parts[-1][0] == "(":
                    mov_parts = mov_parts[:-1]
                mov_parts = [re.sub(r'[^\w\s\d]', '', word).strip() for word in mov_parts]
                if all(word in parts for word in mov_parts):
                    if the_f:
                        titles.append("the " + " ".join(mov_parts[:-1]))
                    elif a_f:
                        titles.append("a " + " ".join(mov_parts[:-1]))
                    elif an_f:
                        titles.append("an " + " ".join(mov_parts[:-1]))
                    else:
                        titles.append(" ".join(mov_parts))

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
            titanic
            titanic

          print(ids) // prints [1359, 2716]

        self.titles = [(a, comedy|adventure), (b, romance) ...] 
        :param title: a string containing a movie title
        :returns: a list of indices of matching movies
        """

        ind = []
        
        title = self.move_article_to_back(title)
        
        
        for i, movie in enumerate([x[0] for x in self.titles]):
            if self.creative:
                title = title.lower()
                movie = movie.lower()

            f_title = [f for f in re.findall(r'\((.*?)\)', movie) if not f.isdigit()]
            
            if title == movie:
                ind.append(i)
            if self.creative:
                movie = re.sub(r'[^\w\s\d]', '', movie).strip()
                if all(word in movie.split() for word in title.split()):
                    if i not in ind:
                        ind.append(i)
            if len(f_title) > 0:
                f_title = f_title[0].lower()
                if "a.k.a." in f_title:
                    f_title = f_title.replace("a.k.a. ", "")
                elif "aka " in f_title:
                    f_title = f_title.replace("aka ", "")
                
                if f_title == title:
                    ind.append(i)
            else:
                movie = self.remove_year(movie)[0]
                if title == movie:
                    ind.append(i)
        
        return list(set(ind))



    def remove_year(self, title):
        year = None
        if bool(re.search('\([0-9]{4}\)', title)):
            year = re.findall('(\([0-9]{4}\))', title)[0]
            title = title.replace(year, "").strip()
        return (title, year)


    def move_article_to_back(self, title):
        title, year = self.remove_year(title)

        if any(article == title.split()[0] for article in ["A", "An", "The", "La", "Le", "Les"]):
            title = (title.partition(title.split()[0])[2] + ", " + title.split()[0]).strip() 

        if year:
            title += " " + year
        
        return title
    
    def move_article_to_front(self, title):
        title, year = self.remove_year(title)

        if any(article == title.split()[-1] for article in ["A", "An", "The", "La", "Le", "Les"]):

            title = (title.split()[-1] + " " + title.partition(title.split()[-1])[0]).replace(",", "").strip() 
        if year:
            title += " " + year
        
        return title



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
        negations = ["didnt", "didn't", "not", "did not", "dont", "don't", "do not", "no", "cant", "can't" "cannot", "can not", "never"]
        intensifiers = ["really", "extremely", "seriously", "totally", "love", "loved", "hate", "hated", "terrible", "amazing", "awesome", "incredible", "disappointing", "despise", "worst", "best", "believe"]
        sentiment = 0
        to_analyze = preprocessed_input["text"]
        
        flag = 1
        for title in preprocessed_input["titles"]:
            to_analyze = to_analyze.replace('"' + title + '"', "")
        to_analyze = str(to_analyze)

        # if len(to_analyze.split()) > 5:
        #         flag = 2
        negated = False

        if "!" in to_analyze:
            flag = 2
        if self.creative:
            to_analyze = re.sub(r'[^\w\s\d]', '', to_analyze).strip()

        for word in to_analyze.split():
            if word in negations:
                negated = True
            if "ly" in word:
                flag = 2
            word = self.stem.stem(word)
            if word in self.sentiment:
                if self.sentiment[word] == "neg":
                    sentiment -= 1
                else:
                    sentiment += 1

        if negated:
            sentiment *= -1


        if any(self.stem.stem(intensifier) in to_analyze for intensifier in intensifiers):
            flag = 2
        
        if not self.creative:
            flag = 1

        return flag * sentiment / abs(sentiment) if sentiment != 0 else 0


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
        
        if any(word in preprocessed_input["text"] for word in ["and", "both", "either", "or", "neither"]):
            sentiment = self.extract_sentiment(preprocessed_input)
            for title in preprocessed_input["titles"]:
                sentiments.append((title, sentiment))
            
        if "but" in preprocessed_input["text"]:
            sentiment0 = self.extract_sentiment(self.preprocess(preprocessed_input["text"][:preprocessed_input["text"].index("but")]))
            sentiment1 = -1 * sentiment0
            sentiments.append((preprocessed_input["titles"][0], sentiment0))
            for title in preprocessed_input["titles"][1:]:
                sentiments.append((title, sentiment1))


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
        title = re.sub(r'[^\w\s\d]', '', title).strip()
        n = len(title.lower().strip())
        closest = []
        title = title.lower()
        for ind, movie_data in enumerate(self.titles):
            movie = self.remove_year(movie_data[0].lower())[0].strip()
            m = len(movie)
            d_mat = np.zeros((n + 1, m + 1))
            for i in range(1, n + 1):
                d_mat[i][0] += d_mat[i - 1][0] + 1
            for j in range(1, m + 1):
                d_mat[0][j] += d_mat[0][j - 1] + 1    
            for i in range(1, n + 1):
                for j in range(1, m + 1):
                    sub_cost = 2
                    if title[i - 1] == movie[j - 1]:
                        sub_cost = 0
                    d_mat[i][j] = min([d_mat[i - 1][j] + 1, d_mat[i - 1][j - 1] + sub_cost, d_mat[i][j - 1] + 1])
            if d_mat[n][m] < max_distance:
                closest.append((ind, d_mat[n][m]))
            
        if len(closest) > 0:
            min_d = min(closest, key=lambda x: x[1])[1]
        else:
            return []
        
        closest = [movie[0] for movie in closest if movie[1] == min_d]
        return closest


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
        ordinal = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth"]

        results = []
        if clarification.isdigit():
            if int(clarification) < 1700 and (int(clarification) - 1) < len(candidates):
                results.append(candidates[int(clarification) - 1])
                return results
            else:
                for candidate in candidates:
                    title = self.titles[candidate][0]
                    if clarification in title:
                        results.append(candidate)

        for i, ord in enumerate(ordinal):
            if ord in clarification and i < len(candidates):
                results.append(candidates[i])

        if "recent" in clarification:
            titles = [(i, self.titles[x][0][-5:-1]) for i, x in enumerate(candidates) if self.titles[x][0][-5:-2].isdigit()]
            results.append(candidates[max(titles, key=lambda x: x[1])[0]])
        
        if "old" in clarification:
            titles = [(i, self.titles[x][0][-5:-1]) for i, x in enumerate(candidates) if self.titles[x][0][-5:-2].isdigit()]
            results.append(candidates[min(titles, key=lambda x: x[1])[0]])

        for candidate in candidates:
            title = self.titles[candidate][0]
            if clarification.lower() in title.lower():
                results.append(candidate)
            title = title.replace("(", "").replace(")", "")
            if len(set(clarification.lower().split()).intersection(title.lower().split())) / len(clarification.split()) > 0.5:
                results.append(candidate)
        return sorted(list(set(results)))



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
        ratings = np.where((ratings > threshold), 10, ratings)
        ratings = np.where((ratings <= threshold) & (ratings > 0), -10, ratings)
        
        return ratings / 10


    def similarity(self, u, v):
        """Calculate the cosine similarity between two vectors.

        You may assume that the two arguments have the same shape.

        :param u: one vector, as a 1D numpy array
        :param v: another vector, as a 1D numpy array

        :returns: the cosine similarity between the two vectors
        """
        bot = np.linalg.norm(u) * np.linalg.norm(v)
        if bot < 1e-16:
            bot += 1e-8
        similarity = np.dot(u, v) / bot
        
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
        recommendations = []
 
        rated_index = [index for (index, i) in enumerate(user_ratings) if i != 0]

        for i in range(len(ratings_matrix)):
            if i not in rated_index:
                recommendations.append((i, sum([self.similarity(ratings_matrix[i], ratings_matrix[j]) * user_ratings[j] for j in rated_index])))
        return [i[0] for i in sorted(recommendations, key=lambda x: x[1], reverse=True)][:k]


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
        My name is CASS and I'm a chatbot designed to recommend movies. Tell me about movies you like or dislike and I'll help you find movies that you might enjoy!
        """


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')