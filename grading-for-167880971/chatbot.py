# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util
import re
import random
import porter_stemmer
p = porter_stemmer.PorterStemmer()

import numpy as np


# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'Walley'

        self.creative = creative


        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')

        ########################################################################
        # TODO: Binarize the movie ratings matrix.                             #
        ########################################################################

        # Binarize the movie ratings before storing the binarized matrix.
        self.ratings = self.binarize(ratings)

        # create empty matrix for the user's movie ratings
        self.user_ratings = np.zeros(len(ratings))

        # global var for how many data points we have from the user
        self.data_count = 0
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

        greeting_message = "Hiya I'm Walley! What can I do for ya?"

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

        goodbye_message = "Walley out!"

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
        no_titles = ["Please tell me about a movie you've seen!", "I'm sorry, I didn't quite catch the name of the"
                     " movie. Could you repeat that for me?", "I'm afraid I didn't understand which movie you're talking"
                    " about. Could you give me the title again?", "Sorry, I didn't catch the name of the movie. Could"
                    " you clarify which movie you're referring to?", "I'm sorry, I didn't get the movie title. Could you"
                    " please tell me the name of the movie you're referring to?"]

        like = ["I understand you liked ", "I'm glad you enjoyed ", "It's great to hear that you liked ",
                "Okay, so I'm hearing that you enjoyed ", "Thanks for sharing that you like "]

        dislike = ["I understand you didn't like ", "I'm sorry you didn't like ", "Sorry to hear you didn't like ",
                   "Okay, so I'm hearing that you didn't enjoy ", "Thanks for sharing that you disliked "]

        unsure_1 = ["I'm not sure I understand if you liked the movie ", "I'm sorry, I'm not sure if you liked ", "Hmmm,"
                     "I didn't understand your opinion on ", "Walley couldn't understand if you have a good review of "]

        unsure_2 = [". Could you please tell me more?", ". Please enter your opinion again", ". Try to enter your movie review again.",
                    ". Please try different words or phrases.", ". Tell me more about it."]

        pos_recs = [". You could also try ", ". A similar movie is ", ". I'd recommend that you watch ", ". Another great one is ",
                    ". I think you'd like "]
        neg_recs = [". I think you'd prefer ", ". A better choice may be ", ". I think you should watch ", ". I'd recommend that you watch "]
        more_than_one = ["Starter mode only supports one movie per line. Please enter movies separately", "Walley can only understand "
                       "one movie at a time in this mode. Please only enter one movie.", "Only one movie at a time, please!"]
        no_movie = ["Walley couldn't find a movie in your input!", "Walley is not familiar with this movie -- please try another one",
                    "I don't know this movie; please try a different one!"]

        adject_like = ["Sweet! You're a fan of ", "Another great movie! And such a cool name! ", "Big time stuff watching ",
                "Isn't it great to find a movie you like. Glad you enjoyed ", "Appreciate you filling me in about your love of "]

        adject_dislike = ["Not every movie is a winner. I guess you didn't like ", "Hate that you spent time watching a bad movie like ", "Unfortunate to have a negative experience watching ",
                   "So I'm picking up that you hated ", "Appreciate you giving me the details of not liking "]

        adject_unsure_1 = ["I'm real confused, what's going on with ", "Be straight with me, did you like  ",
                     "What's your take on ", "Be clear with me here, what's your opinion of "]

        adject_unsure_2 = [". Send over the 411 ASAP.", ". Give it another shot old sport.", ". Fire off another for me.",
                    ". Spin your answer around and send it back my way.", ". Fill me in on the deets."]

        adject_pos_recs = [". Look at this, you should also check out ", ". My calculations suggest you see ", ". It's a no-brainer, watch", ". If you want to have fun, watch ",
                    ". I guarentee you'll like "]
        adject_neg_recs = [". Just watch ", ". Don't waste your time, watch ", ". I did a lot of thinking for you. Watch ", ". It will upset me if you don't watch "]
    
        adject_no_movie = ["Nice try! There's no movie in your input. Can't fool me!", "I don't know what you're talking about. I know many many movies, that is not one of them -- please try another one",
                    "I don't know movies that obscure, maybe try one people actually know."]
        
        arbitrary_responses = ["I'm sorry, I didn't quite understand what you meant. Could you please rephrase your response?",
                                "I'm not sure how to respond to that. Could you please provide me with more information?",
                                "That's an interesting point, but could you please bring the conversation back to movies?",
                                "I'm sorry, I don't think that's relevant to what we're discussing. Could you please stick to movies?",
                                "I'm having trouble following you. Could you please clarify what you mean?",
                                "I'm sorry, but that doesn't seem to relate to our conversation. Can you bring us back on track?"
                                ]

        short_expansion = ["Can you elaborate on what you mean when you say ", "I'm confused, what is ", "What do you mean by ", "Can you give a bit more information about",
                           "Please dive a little deeper on the topic of "]

        emotion_leading_words = ["I'm", "am", "feel", "feeling", "experience", "experiencing"]

        emotions = {'happy': 0, 'sad': 1, 'angry': 2, 'fearful': 1, 'excited': 0, 'hopeful': 0, 'disgusted': 2, 'upset': 1,
                    'surprised': 0, 'content': 0, 'anxious': 0, 'jealous': 2, 'proud': 0, 'guilty': 1, 'ashamed': 1, 'mad': 2,
                    'grateful': 0, 'nostalgic': 1, 'lonely': 1, 'energetic': 0, 'calm': 0, 'frustrated': 1, 'bored': 1, 'thrilled': 0,
                    'determined': 0, 'insecure': 1, 'sympathetic': 0, 'affectionate': 0, 'inspired': 0, 'smiling': 0, 'overwhelmed': 1,
                    'curious': 0, 'confused': 1, 'terrified': 1, 'relieved': 0, 'loved': 0, 'admiration': 0, 'frowning': 1,
                    'betrayed': 2, 'disappointed': 1, 'rejected': 1}

        happy_responses = ["I'm so glad to hear that you're feeling good!",
                            "That's great news! I'm happy to hear that you're feeling happy!",
                            "Yay! It's always good to feel happy!",
                            "Awesome! I'm so happy that you're happy!",
                            "That's wonderful! It's always a great feeling to be happy!",
                            "I'm thrilled to hear that you're feeling happy! Keep up the good vibes!"]
        
        sad_responses = ["I'm sorry to hear that you're feeling sad. Is there anything I can do to help?",
                        "It's okay to feel sad sometimes. Would you like to talk about what's bothering you?",
                        "I understand that sadness can be difficult to deal with. Please know that I'm here for you.",
                        "I'm sorry that you're going through a tough time. Remember that things will get better.",
                        "It's okay to not be okay. Take your time to process your feelings, and let me know if you need anything."]

        angry_responses = [ "I'm sorry to hear that you're feeling angry. Is there anything that's been frustrating you?",
                            "I can sense that you're angry. It's okay to feel that way. What's been bothering you?",
                            "I understand that anger can be difficult to manage. Can you tell me more about what's been causing your anger?",
                            "It's important to acknowledge and process our emotions, including anger. Would you like to talk about what's going on?",
                            "I'm here to listen and support you, even when you're feeling angry. Let me know how I can help."]


        if self.creative:
            response = ""
            # response = "I processed {} in creative mode!!".format(line)
            titles = self.extract_titles(line)
            sentiment = self.extract_sentiment(line)

            if len(titles) == 0:
                words = line.split()
                emotion = 0
                for i in range(len(words)):
                    word = words[i]
                    if word in emotion_leading_words:
                        emotion = 1
                    if emotion == 1:
                        if word not in emotions:
                            emotion = 0
                            break
                        if emotions[word] == 0:
                            response = random.choice(happy_responses)
                        elif emotions[word] == 1:
                            response = random.choice(sad_responses)
                        elif emotions[word] == 2:
                            response = random.choice(angry_responses)

                if len(words) < 4 and emotion == 0: # We'll catch short inputs and deal with them separately
                    response = random.choice(short_expansion) + line
                elif emotion == 0:
                    response = random.choice(arbitrary_responses)

            else:
                for i in range(len(titles)): 
                    title = titles[i]
                    movies_index = self.find_movies_by_title(title)
                    if len(movies_index) == 0:
                        close = self.find_movies_closest_to_title(title)
                        if len(close) != 0: print("Did you mean %s?" % close[0])
                        else: response = random.choice(adject_no_movie)
                    else:
                        if len(movies_index) > 1:
                            print("Which one did you mean?")
                            for movie in movies_index:
                                print(movie)
                        # if they hadn't previously said something about the movie...
                        if self.user_ratings[movies_index[0]] == 0:
                            self.user_ratings[movies_index[0]] = sentiment
                            if sentiment != 0:
                                self.data_count += 1

                        # if they did, update sentiment but not count
                        else:
                            self.user_ratings[movies_index] = sentiment

                        if sentiment >= 1:
                            response += random.choice(adject_like) + title + "!"
                        if sentiment <= -1:
                            response += random.choice(adject_dislike) + title + "!"
                        if sentiment == 0:
                            response += random.choice(adject_unsure_1) + title + random.choice(adject_unsure_2)

                        # recommend
                        if self.data_count >= 5:
                            recommended = self.recommend(self.user_ratings, self.ratings, k=1)
                            if sentiment == 1:
                                response = random.choice(adject_like) + str(title) + random.choice(adject_pos_recs) + str(self.titles[recommended[0]][0]) + "!"
                            if sentiment == -1:
                                response = random.choice(adject_dislike) + str(title) + random.choice(adject_neg_recs) + str(self.titles[recommended[0]][0]) + "!"
        else:
            #response = "I processed {} in starter mode!!".format(line)
            titles = self.extract_titles(line)
            sentiment = self.extract_sentiment(line)

            if len(titles) == 0:
                response = random.choice(no_titles)
            elif len(titles) > 1:
                response = random.choice(more_than_one)
            else:
                title = titles[0]
                movies_index = self.find_movies_by_title(title)
                if len(movies_index) == 0:
                    response = random.choice(no_movie)
                else:
                    # if they hadn't previously said something about the movie...
                    if self.user_ratings[movies_index[0]] == 0:
                        self.user_ratings[movies_index[0]] = sentiment
                        if sentiment != 0:
                            self.data_count += 1

                    # if they did, update sentiment but not count
                    else:
                        self.user_ratings[movies_index] = sentiment

                    if sentiment == 1:
                        response = random.choice(like) + title + "!"
                    if sentiment == -1:
                        response = random.choice(dislike) + title + "!"
                    if sentiment == 0:
                        response = random.choice(unsure_1) + title + random.choice(unsure_2)

                    # recommend
                    if self.data_count >= 5:
                        recommended = self.recommend(self.user_ratings, self.ratings, k=1)
                        if sentiment == 1:
                            response = random.choice(like) + str(title) + random.choice(pos_recs) + str(self.titles[recommended[0]][0]) + "!"
                        if sentiment == -1:
                            response = random.choice(dislike) + str(title) + random.choice(neg_recs) + str(self.titles[recommended[0]][0]) + "!"


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
        potential_movies = re.findall('"([^"]*)"', preprocessed_input)
        if self.creative:
            pass
        return potential_movies

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
        indices = []
        title_words = title.split()

        year = False
        if title_words[-1][0] == "(":
            year = True

        # rearrange article
        if title_words[0] == "The" or title_words[0] == "A" or title_words[0] == "An":
            if year:
                title_words.insert(-1, ',')
                title_words.insert(-1, title_words.pop(0))
                title = " ".join(title_words)

            else:
                title_words.append(',')
                title_words.append(title_words.pop(0))
                title = " ".join(title_words)
            title = title.replace(" ,", ",")

        for i in range(len(self.titles)):
            # exact match
            if title == self.titles[i][0] or (self.creative and title.lower() == self.titles[i][0].lower()):
                indices.append(i)

            elif not year and self.creative:

                test_title = self.titles[i][0].split()
                
                if test_title[-1][0] == "(":
                    test_title = test_title[:-1]
                test_title = " ".join(test_title)
                if test_title.lower() == title.lower():
                    indices.append(i)

            elif not year:

                test_title = self.titles[i][0].split()
                if test_title[-1][0] == "(":
                    test_title = test_title[:-1]
                test_title = " ".join(test_title)
                if test_title == title:
                    indices.append(i)

            

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
        pos_words = 0
        neg_words = 0

        negation_words = ["not", "don't", "isn't", "didn't", "won't", "aren't", "can't", "couldn't", "doesn't",
                          "haven't", "hasn't", "hadn't", "never"]

        passion_words = ["realli", "really", "terrible", "love", "despise", "adore", "favorite", "beautiful", "perfect", "atrocious", "extreme", "completely",
                         "detest", "disgust", "very", "awful", "horrible", "pristine", "fantastic", "phenomenal", "loved", "hated", "hate"]
        passion = 0 
        prev_neg = False
        titles = self.extract_titles(preprocessed_input)

        for title in titles:
            preprocessed_input = preprocessed_input.replace(title, "")

        word_list = preprocessed_input.split()

        for word in word_list:
            word = p.stem(word)
            if word[-1] == "." or word[-1] == ",":
                word = word[:len(word)-1]
            if word == "enjoi":
                word = "enjoy"
            if word in self.sentiment:
                if (self.sentiment[word] == "pos" and not prev_neg) or (self.sentiment[word] == "neg" and prev_neg):
                    pos_words += 1
                else:
                    neg_words += 1
            

            if word in negation_words:
                prev_neg = True
            elif word in self.sentiment:
                prev_neg = False
        
            if word in passion_words and self.creative:
                passion = 1

        if pos_words == neg_words:
            return 0
        elif pos_words > neg_words:
            return (1 + passion)
        else:
            return (-1 - passion)

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
        result = []
        titles = self.extract_titles(preprocessed_input)
        if len(titles) == 1:
            result = [(titles[0], self.extract_sentiment(preprocessed_input))]
        elif len(titles) > 1:
            if preprocessed_input.find("both")  >=0 or preprocessed_input.find("and") >=0 or \
               preprocessed_input.find("either" )>=0 or preprocessed_input.find("or") >=0:
                sent = self.extract_sentiment(preprocessed_input)
                for title in titles:
                    result.append((title, sent))

            elif preprocessed_input.find('but') >=0 or preprocessed_input.find('however') >= 0:
                index = preprocessed_input.find("but") + 4 if preprocessed_input.find('but') >=0 else preprocessed_input.find("however") + 8
                curr = preprocessed_input[:index]
                sent = self.extract_sentiment(curr)
                for title in titles:
                    if preprocessed_input.find(title) >= index:
                        result.append((title, -sent))
                    else: result.append((title, sent))
            else:
                for title in titles:
                    index = preprocessed_input.find(title) + len(title) + 1
                    curr = preprocessed_input[:index]
                    preprocessed_input = preprocessed_input[index:]
                    sent = self.extract_sentiment(curr)
                    result.append((title, sent))
        return result
                # split, get sentiment
            
        

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
        def find_dist(a,b):
            matrix = [[0 for i in range(len(a)+1)] for j in range(len(b)+1)]

            for i in range(1, len(a)+1):   
                matrix[0][i] = i
            for i in range(1, len(b)+1):
                matrix[i][0] = i
            
            for row in range(1, len(b)+1):
                for col in range(1, len(a) +1):
                    cost = 0
                    if str.lower(a[col-1]) != str.lower(b[row-1]):
                        cost = 2
                    matrix[row][col] = min(matrix[row-1][col] +1, matrix[row][col-1] +1, matrix[row-1][col-1] + cost)
            return matrix[len(b)][len(a)]
        
        result = []
        min_dist = max_distance
        for i in range(len(self.titles)):
            movie = self.titles[i][0]
            if "(" in movie:
                movie = movie[:movie.find(" (")]
            curr_dist = find_dist(title, movie)
            if curr_dist == min_dist:
                result.append(i)
            if curr_dist < min_dist:
                result = [i]
                min_dist = curr_dist
        print(result)
        return result
        

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
        cardinality = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth"]
        nums = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
        result = []
        for i in range(len(cardinality)):
            if cardinality[i] in clarification:
                return [candidates[i]]
        
        if len(clarification) < 3:
            for i in range(len(nums)):
                if nums[i] in clarification:
                    return [candidates[i]]
        
        if "recent" in clarification or "oldest" in clarification:
            newest = [0, 0]
            oldest = [0, 2100]
            for cand in candidates:
                mov = self.titles[cand][0]
                year = int(mov[len(mov)-5:][:4])
                if year > newest[1]:
                    newest = [cand, year]
                if year < oldest[1]:
                    oldest = [cand, year]
            if "recent" in clarification: return [newest[0]]
            if "oldest" in clarification: return [oldest[0]]


        for cand in candidates:
            if clarification in self.titles[cand][0]:
                result.append(cand)
        
        if result == []:
            # took inspiration from generic longest common substring function from avanitrachhadiya2155
            min_cand = [-1, 0]
            for cand in candidates:
                t = self.titles[cand][0]
                dp = [[0 for i in range(len(t) + 1)] for j in range(2)]
                res = 0
                
                for i in range(1,len(clarification) + 1):
                    for j in range(1,len(t) + 1):
                        if(clarification[i - 1] == t[j - 1]):
                            dp[i % 2][j] = dp[(i - 1) % 2][j - 1] + 1
                            if(dp[i % 2][j] > res):
                                res = dp[i % 2][j]
                        else:
                            dp[i % 2][j] = 0

                if res > min_cand[1]:
                    min_cand = [cand, res]            
            if min_cand[0] != -1: result.append(min_cand[0])
        

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

        ratings[np.logical_and((ratings <= threshold), (ratings != 0))] = -1
        ratings[np.logical_and((ratings > threshold), (ratings != 0))] = 1


        ########################################################################
        #                        END OF YOUR CODE                              #
        ########################################################################
        return ratings

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
        denom = np.sqrt((np.sum(np.square(u)) * np.sum(np.square(v))))
        if denom != 0:
            similarity = np.dot(u, v) / np.sqrt((np.sum(np.square(u)) * np.sum(np.square(v))))
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
        guess_ratings = []
        not_seen = []
        seen = []
        for i in range(len(user_ratings)):
            if user_ratings[i] == 0:
                not_seen.append(i)
            else:
                seen.append(i)

        for i in range(len(ratings_matrix)):
            if i in not_seen:
                score = 0
                for j in seen:
                    num = self.similarity(ratings_matrix[i], ratings_matrix[j])*user_ratings[j]
                    score += num
                guess_ratings.append(score)
            else:
                guess_ratings.append(-10)
        recommendations = sorted(range(len(guess_ratings)), key=lambda k: guess_ratings[k], reverse=True)

        recommendations = recommendations[:k]
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
        
        Walley is a movie recommending chatbot! Tell him about some movies you have seen and he can give you some 
        recommendations on what to watch next!"
        """

if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
