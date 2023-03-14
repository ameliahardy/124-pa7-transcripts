# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util

import numpy as np
import re
import string
import random
from porter_stemmer import PorterStemmer

stemmer = PorterStemmer()


# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        self.name = 'Movie Bot'
        if creative:
            self.name = 'Baddie Bot'

        self.creative = creative

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')
        self.stemmed_sentiment = self.stem_dict(self.sentiment)
        self.negations = ["didn't", "never", "not", "neither", "nor", "barely", "hardly", "don't", 'dont', 'didnt']
        self.punctuations = string.punctuation
        self.stopwords = ['a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was', 'were', 'will', 'with']
        self.super_pos = ['awesome', 'loved', 'lovely', 'delightful', 'marvelous', 'splendid', 'wonderful', 'brilliant', 'brilliant', 'adored', 'best', 'pleased']
        self.super_neg = ['despise', 'despised', 'hate', 'hated', 'detest', 'detested', 'horrible', 'worst', 'lackluster', 'terrible', 'disgusting']
        self.user_recs = []
        self.cid = 0
        self.adverbs= ['really','extremely','very','especially','truly','undeniably','genuinely','honestly',
                        'seriously','tremendously', 'downright','remarkably','exceedingly']
       


        self.no_quotes_response = [
            [
                "Sorry, I don't understand. ",
                "I don't think I understand what movie you are talking about. ",
                "I am not sure if I know what you are talking about. "
            ],
            [
                "Don't waste my time now. I'm here to talk about movies. ",
                "Huh? Whatchu talking about? "
            ]
        ]
        self.one_movie_response = [
            [
                "Please tell me about one movie at a time. Go ahead.",
                "Woah, slow down, I can only hear about one movie at a time. What movie would you like to tell me about?"
            ],
            [
                "Hey, you can't rush a baddie! One movie at a time. Go ahead."
            ]
        ]
        self.not_exist_responses = [[
            "I'm sorry, I don't think I've heard of {} before. ",
            "I'm not sure about {}. ",
            "Interesting, {} must be a niche movie. ",
            "I have not seen {} before. ",
            "I'm sorry, I've never heard of {}. "
        ],
            [
            "Don't waste my time with this {} movie that I haven't heard of before. ",
            "{}? Huh? "
        ]
        ]

        self.another_movie_response = [[
            "Is there another movie that you have seen?",
            "Tell me about another movie that you have seen.",
            "Tell me your opinions on another movie.",
            "Can you tell me about a movie that you have seen?",
            "Is there  another movie that you like or dislike?",
        ],
            [
            "Gimme another movie.",
        ]
        ]

        self.like_movie_responses = [
            [
                "Ok, you liked {}! ",
                "You liked {}. Thank you! ",
                "So you liked {}! "
            ],
            [
                "Purrr, {} is so good. ",
                "Yesss, I love a good watching of {}. ",
                "You actually like {}? High key judging you for that one... ",
            ]
        ]

        self.dislike_movie_responses = [
            [
                "Ok, you did not like {}. ",
                "You did not like {}. Thank you! ",
                "So you did not like {}! "
            ],
            [
                "PERIOD, Queen. I can't with {}, too. ",
                "Pleeasseee, I can't with {} either. "
            ]
        ]
        self.clarify_responses = [
            [
                "Did you mean {}? ",
                "Are you talking about {}? "
            ],
            [
                "You're getting me tight with these unspecific movie titles. Are you talking about {}? ",
                "You mean {}? ",
                "You're talking about {}, right? "
            ]
        ]

        self.neutral_responses = [
            [
                "I'm sorry, I'm not sure if you liked {}. Tell me more about it. ",
                "Did you like or dislike {}? "
            ],
            [
                "I want opinions. Did you like {} or not? ",
                "I can't with nonchalant people. Did you like {} or not? ",
                "You can just tell me if you didn't like {}. Or are you afraid to tell me that you actually like {} "
            ]
        ]

        self.make_rec_response = [
            [
                "Given what you told me, I think you would like {}. ",
                "Based on what you've told me, I would recommend watching {}. ",
            ],
            [
                "From our little chit chat, I think you'd like {}. ",
                "Based on our convo, you give me {} vibes. ",
                "Cause you're that type of person, you would probably be into {}. ",
                "You seem like a baddie, like me, and all baddies watch {}. "
            ]
        ]

        self.want_more_recs_response = [
            [
                "Would you like more recommendations? ",
                "Do you want another movie recommendation? "
            ],
            [
                "I got another one if you want it. ",
                "Want another one? ",
                "I know you want another baddie rec. "
            ]
        ]

        self.arb_inputs = [
            "Ok, got it.",
            "I don't really want to talk about that, let's go back to movies",
            "That shouldn't be the topic of our conversation."
        ]

        num_movies = len(self.titles)
        self.movie_inputs = []
        self.user_ratings = np.zeros(num_movies)
        self.num_user_ratings = 0
        self.can_make_rec = False
        self.typo_checking = False
        self.typo_sentiment = 0
        self.typo_list = []
        self.typo_title = ""

        self.clarifying = False
        self.candidates = []

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

        if self.creative:
            greeting_message = "What do you want munch?"

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
            goodbye_message = "Boy bye!"

        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return goodbye_message

    ############################################################################
    # 2. Modules 2 and 3: extraction and transformation                        #
    ############################################################################

    def does_not_exist(self, line):
        return 0

    def min_edit_dist(self, s, t):
        m, n = len(s), len(t)
        d = np.zeros((m+1, n+1))
        for i in range(m+1):
            d[i, 0] = i
        for j in range(n+1):
            d[0, j] = j
        for j in range(1, n+1):
            for i in range(1, m+1):
                if s[i-1] == t[j-1]:
                    cost = 0
                else:
                    cost = 1
                d[i, j] = min(d[i-1, j]+1, d[i, j-1]+1, d[i-1, j-1]+cost)
        return d[m, n]

    def handle_no_matches(self, line, input):
        # Check for disambiguates
        all_partial = [i for i, x in enumerate(self.titles) if x[0].lower().find(input.lower()) != -1]
        if all_partial:
            self.candidates = all_partial
            self.clarifying = True
            self.typo_sentiment = self.extract_sentiment(line)
            all_matches = "\n".join([self.titles[x][0] for x in all_partial])
            return f"I found more than one movie called {input}. Can you clarify?\n{all_matches}"

        # Check for typo
        closest = self.find_movies_closest_to_title(input)
        if not closest:
            return random.choice(self.not_exist_responses[self.cid]).format(self.typo_title) + random.choice(self.another_movie_response[self.cid])

        text = self.titles[closest[0]][0]
        self.typo_list = closest
        self.typo_checking = True
        self.typo_sentiment = self.extract_sentiment(line)
        return random.choice(self.clarify_responses[self.cid]).format(text)

    def found_movie(self, matched_title_idx, sentiment):
        # Passed all checks and can store movie.
        self.movie_inputs.append(matched_title_idx)
        self.user_ratings[matched_title_idx] = sentiment
        self.num_user_ratings += 1
        matched_title = self.titles[matched_title_idx][0]

        # Positive sentiment response
        response = ""
        if sentiment > 0:
            response = random.choice(
                self.like_movie_responses[self.cid]).format(matched_title)
        # Negative sentiment response
        if sentiment < 0:
            response = random.choice(
                self.dislike_movie_responses[self.cid]).format(matched_title)

        # Case: Need more info on user before making recs
        if self.num_user_ratings < 5:
            return response + random.choice(self.another_movie_response[self.cid])

        # Case: Can make recommendation
        self.can_make_rec = True
        self.user_recs = self.recommend(
            self.user_ratings, self.ratings, 10, False)
        return response + self.make_rec()

    def typo_mode(self, line):
        neg = False
        for x in self.negations:
            if line.find(x) != -1:
                neg = True
        if neg:
            if len(self.typo_list) == 1:
                self.typo_checking = False
                return random.choice(self.not_exist_responses[self.cid]).format(self.typo_title) + random.choice(self.another_movie_response[self.cid])
            poss = self.titles[self.typo_list[1]][0]
            self.typo_list = self.typo_list[1:]
            return random.choice(self.clarify_responses[self.cid]).format(poss)
        self.typo_checking = False
        return self.found_movie(self.typo_list[0], self.typo_sentiment)

    def clarify_mode(self, line):
        temp_candidates = self.disambiguate(line, self.candidates)

        if len(temp_candidates) == 0:
            return f"I can't find '{line}' in any of these. Try clarifying in a different way."

        self.candidates = temp_candidates
        if len(self.candidates) == 1:
            self.clarifying = False
            return self.found_movie(self.candidates[0], self.typo_sentiment)
        
        # self.typo_sentiment = self.extract_sentiment(line)
        all_matches = "\n".join([self.titles[x][0] for x in self.candidates])
        return f"I found more than one movie '{line}' in it. Can you clarify?\n{all_matches}"

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
        if self.creative:
            self.cid = 1
        emotion = self.detect_emotions(line)
        if emotion != None:
            return self.redirect_to_movies(emotion)
        question = self.check_question_type(line)
        if question[1] != None:
            return self.generate_response(question[0], question[1], self.creative)
        if self.clarifying:
            return self.clarify_mode(line)
        if self.typo_checking:
            return self.typo_mode(line)
        if self.can_make_rec:
            return self.make_rec(l=line)
        else:
            input_titles = self.extract_titles(line)
            num_input = len(input_titles)
            # Case: No movie found in input (ie. no quotes)
            if num_input == 0:
                return random.choice(self.no_quotes_response[self.cid]) + random.choice(self.another_movie_response[self.cid])
            # Case: User input multiple movie titles.
            if num_input > 1:
                return random.choice(self.one_movie_response[self.cid]) + random.choice(self.another_movie_respons[self.cid])

            input_title = input_titles[0]
            matched_titles = self.find_movies_by_title(input_title)
            num_matched = len(matched_titles)
            # Case: No matches found.
            if num_matched == 0:
                self.typo_title = input_title
                return self.handle_no_matches(line, input_title)
            # Case: More than one match found.
            if num_matched > 1:
                self.clarifying = True
                self.typo_sentiment = self.extract_sentiment(line)
                self.candidates = matched_titles
                all_matches = "\n".join(
                    [self.titles[x][0] for x in matched_titles])
                return f"I found more than one movie called {input_title}. Can you clarify?\n{all_matches}"

            matched_title_idx = matched_titles[0]
            # Case: User already told us about this movie.
            if matched_title_idx in self.movie_inputs:
                return "You've already told me your opinions on this movie. " + random.choice(self.another_movie_response[self.cid])

            sentiment = self.extract_sentiment(line)
            # Case: Neutral sentiment
            if sentiment == 0:
                return random.choice(self.neutral_responses[self.cid]).format(input_title)
            
            self.typo_sentiment = sentiment
            return self.found_movie(matched_title_idx, sentiment)

        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return response

    def make_rec(self, l=""):
        neg_present = False
        for x in self.negations:
            if l.find(x) != -1:
                self.can_make_rec = False
                response = "Ok! If you don't want recommendations, type 'quit'. \nTell me about another movie that you liked."
                if self.creative:
                    response = "Bruh, if you don't want another recommendation, just type 'quit' and quit playing around with me. But if you want to keep talking, give me another movie."
                return response

        if not self.user_recs:
            self.can_make_rec = False
            response = "Please tell me another movie you like for more recommendations."
            if self.creative:
                response = "Fine, if you want another rec, I'll need to hear about another movie."
            return response
        movie_rec = self.user_recs[0]
        self.user_recs = self.user_recs[1:]
        return random.choice(self.make_rec_response[self.cid]).format(self.titles[movie_rec][0]) + random.choice(self.want_more_recs_response[self.cid])

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
        if self.creative:
            pattern = r"\b([A-Z][\w\s]*(?:(?:of|the|and|in|on)\s[A-Z][\w\s]*)*)\b"
    
    # Find all matches of the regular expression in the text
            matches = re.findall(pattern, preprocessed_input)
    
    # Filter out non-movie titles and return the set of movie titles
            movie_titles = set()
            for match in matches:
                if match.isalpha() and len(match) > 1 and not match.lower() in ["the", "and", "in", "on", "of", "about"]:
                    movie_titles.add(match.strip())
    
            return movie_titles
        pattern = r'"([^"]+)"'
        matches = re.findall(pattern, preprocessed_input)
        return matches

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

        hasYear = len(re.findall('( \([0-9]{4}\))', title)) > 0
        raw_title = sorted(title.lower().replace(',', '').split(" "))
        inds = []
        with open("data/movies.txt", encoding='UTF-8') as f:
            l_num = 0
            for line in f:
                line = re.findall("%(.+)%", line)[0]
                alt_titles = re.findall(' \(([a-zA-Z][\w|,|\s]*)\)\s\(', line)
                hasAlt = len(alt_titles) != 0

                # Alt Title Search
                if hasAlt:
                    isAlt = False
                    for cur_alt in alt_titles:
                        # handle a.k.a
                        if cur_alt.find("a.k.a") != -1:
                            cur_alt = cur_alt[6:]
                        cur_alt = sorted(
                            cur_alt.lower().replace(',', '').split(" "))
                        # handle year
                        if hasYear:
                            if raw_title[1:] == cur_alt:
                                isAlt = True
                        else:
                            if raw_title == cur_alt:
                                isAlt = True
                    if isAlt:
                        inds.append(l_num)

                # Normal Title Search
                line = sorted(line.lower().replace(',', '').split(" "))
                if hasYear and line == raw_title:
                    if l_num not in inds:
                        inds.append(l_num)
                if not hasYear and line[1:] == raw_title:
                    if l_num not in inds:
                        inds.append(l_num)
                l_num += 1

        return inds

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
        sentiment_score = 0
        pattern = r'\"[^\"]*\"'
        sentiment_scores = {'pos': 1, 'neg': -1}
        input = re.sub(pattern, '', preprocessed_input)
        input = self.remove_stopwords(input)
        negation = False
        adverb = False
        exclaimation = False
        previous_sentiment = 0

        for word in input.split():
            
            word = word.lower()
            sentiment = 0
            if word in self.negations:
                negation = True
            elif word in self.adverbs:
                adverb = True
            elif word in self.punctuations:
                negation = False
            else:
                if word.find('!') != -1:
                    exclaimation = True
                    word = word.replace('!', "")
                if word in self.super_pos:
                    sentiment += 2
                elif word in self.super_neg:
                    sentiment -= 2
                elif stemmer.stem(word) in self.stemmed_sentiment:
                    word = stemmer.stem(word)
                    sentiment += sentiment_scores[self.stemmed_sentiment[word]]
                    if exclaimation:
                        sentiment += sentiment_scores[self.stemmed_sentiment[word]]
                elif exclaimation:
                    sentiment += previous_sentiment
                if negation:
                    sentiment *= -1
                if adverb:
                    sentiment *= 2
                if sentiment != 0:
                    previous_sentiment = sentiment
                exclaimation = False
                sentiment_score += sentiment

        if self.creative:
            if sentiment_score >= 2:
                return 2
            elif sentiment_score <= -2:
                return -2
            else:
                return sentiment_score
        else:
            if sentiment_score > 0:
                return 1
            elif sentiment_score < 0:
                return -1
            else:    
                return 0

    def stem_dict(self, dict):
        stemmed_dict = {}
        for key, value in self.sentiment.items():
            stemmed_key = stemmer.stem(key)
            stemmed_dict[stemmed_key] = value
        return stemmed_dict

    def remove_stopwords(self, s):
        filtered_words =[word for word in s.split()if word.lower()not in self.stopwords]
        return " ".join(filtered_words)

    def check_question_type(self, input_text):
    # Check if the input is a question and what type of question it is
        match = None

        match = re.match(r"(C|c)an you (.+)\?*", input_text, re.IGNORECASE)
        if match:
            return (match.group(2), "can_do")
            
        match = re.match(r"(W|w)hat is (.+)\?*", input_text, re.IGNORECASE)
        if match:
            return (match.group(2), "definition")
            
        match = re.match(r"(H|h)ow do I (.+)\?*", input_text, re.IGNORECASE)
        if match:
            return (match.group(2), "tip")
            
        match = re.match(r"(W|w)hy is (.+)\?*", input_text, re.IGNORECASE)
        if match:
            return (match.group(2), "analysis")
            
        match = re.match(r"(W|w)hen did (.+)\?*", input_text, re.IGNORECASE)
        if match:
            return (match.group(2), "release_date")
            
        match = re.match(r"(W|w)here is (.+)\?*", input_text, re.IGNORECASE)
        if match:
            return (match.group(2), "location")
        match = re.match(r"(W|w)ho is (.+)\?*", input_text, re.IGNORECASE)
        if match:
            return (match.group(2), "person")
            
        match = re.match(r"(W|w)hich (is|are) (.+)\?*", input_text, re.IGNORECASE)
        if match:
            return (match.group(2), "recommendation")        
        return None, None
    
    def generate_response(self, match, question_type, creative):
    # Generate a response based on the type of question
        if question_type == "can_do":
            if creative:
                response = "What do I look like, a genie in a bottle? I can do anything I want! So yeah, I can do that. But let's talk about something more interesting, like movies you've seen."
            else:
                response = "Unfortunately, I'm not able to " + match + ", but I'd be happy to recommend a great movie for you to watch! What movies do you typically watch?"
            
        elif question_type == "definition":
            if creative:
                response = "Uh, sorry, but if you don't know what that means, you might wanna get with the program. A baddie like me doesn't have time for basic vocabulary. Instead, let's talk about some of your favorite movies!"
            else:
                response = "Well, I'm not sure about " + match + ", but lets shift our focus back to movies."
            
        elif question_type == "tip":
            if creative:
                response = "Oh honey, you don't need any tips. Lets talk about movies you enjoy instead."
            else:
                response = "Hmm, I'm not sure about " + match + ", but here's a pro tip: talking about movies is way more fun."
            
        elif question_type == "analysis":
            if creative:
                response = "Why are we even talking about this? Lets talk about the movies that make you feel like a boss babe. You know, like 'Kill Bill' or 'The Matrix'. These movies are all about taking control and being in charge of your life."
            else:
                response = "Interesting question! Have you ever thought about why certain movies are considered classics? Let's discuss what classics and modern movies you like!"
            
        elif question_type == "release_date":
            if creative:
                response = "Dates are important, but the real question is: what movies were released during that time? Some of my personal favorites were released in the 90s, like 'Clueless' and 'Pulp Fiction'. What are some of your favorite movie releases?"
            else:
                response = "Hmm, I'm not sure when " + match + " happened, but did you know that some of the best movies were released in the 80s and 90s? Let's talk about some great movie releases!"
            
        elif question_type == "location":
            if creative:
                response = "I'm all about traveling to new places, but what really gets me excited are movies set in exotic locations. Have you seen 'Eat Pray Love'? It's all about exploring new cultures and finding yourself in the process. What movies that you like have great scenery?"
            else:
                response = "I'm not sure where " + match + " is, but did you know that some of the best movies take place in exotic locations? Let's talk about some great movie settings!"
            
        elif question_type == "person":
            if creative:
                response = "Honey, the only person you should be concerned with is the baddie right here. Lets get back to movies."
            else:
                response = "I'm not sure who " + match + " is, but lets focus on movies instead!" 
        elif question_type == "recommendation":
            if creative:
                response = "I got you, boo! I just need you to tell me more movies you like or dislike!"
            else:
                response = "Sure, let me know what movies you like or dislike."
    
        return response


    def detect_emotions(self, input_text):
        emotions = {
            'anger': r"(I am|I'm|im|I’m|I feel|I'm feeling|im feeling) +.*(?:angry|mad|pissed off|irritated|frustrated|annoyed).*",
            'sad': r"(I am|I'm|im|I’m|I feel|I'm feeling|im feeling) +.*(?:sad|unhappy|depressed|down|blue|low).*",
            'happy': r"(I am|I'm|im|I’m|I feel|I'm feeling|im feeling) +.*(?:happy|glad|pleased|delighted|joyful|ecstatic).*",
            'tired': r"(I am|I'm|im|I’m|I feel|I'm feeling|im feeling) +.*(?:tired|exhausted|drained|weary|spent|fatigued).*",
            'stressed': r"(I am|I'm|im|I’m|I feel|I'm feeling|im feeling) +.*(?:stressed|anxious|pressured|burdened|overwhelmed).*",
            'bored': r"(I am|I'm|im|I’m|I feel|I'm feeling|im feeling) +.*(?:bored|uninterested|disinterested|apathetic).*",
            'excited': r"(I am|I'm|im|I’m|I feel|I'm feeling|im feeling) +.*(excited|thrilled|stoked|pumped|eager|anticipating|looking forward to|can't wait for).*"

        }
        
        for emotion, regex in emotions.items():
            match = re.search(regex, input_text, re.IGNORECASE)
            if match:
                return emotion
            
        return None

    def redirect_to_movies(self, emotion):
        if emotion == "happy":
            if self.creative:
                return "I'm glad to hear you're feeling fly! Let's talk movies, y'all."
            else:
                return "Great to hear! Let's get back to our discussion about movies."
        elif emotion == "sad":
            if self.creative:
                return "I know it's tough, but let's distract ourselves with some movie talk!"
            else:
                return "I'm sorry to hear that. Let's get back to talking about movies and maybe we can cheer you up."
        elif emotion == "anger":
            if self.creative:
                return "You ain't gotta be so mad, let's talk about movies instead!"
            else:
                return "I'm sorry if I upset you. Let's get back to our movie chat and have some fun."
        elif emotion == "excited":
            if self.creative:
                return "Oh yeah, baby! Let's keep that energy going and talk about some movies."
            else:
                return "I'm excited too! Let's get back to our discussion about movies."
        elif emotion == "tired":
            if self.creative:
                return "I feel you, let's chill and talk about some movies to help you relax."
            else:
                return "I understand. Maybe talking about movies will help energize us!"
        elif emotion == "stressed":
            if self.creative:
                return "Take a breather and let's talk about some movies to take your mind off things."
            else:
                return "I'm sorry to hear that. Let's get back to our movie discussion and maybe it will help you relax."
        elif emotion == "bored":
            if self.creative:
                return "What?! How can you be bored when there are so many great movies out there?! Let's talk about some!"
            else:
                return "I don't want you to be bored. Let's get back to our discussion about movies and find something interesting to talk about."
        else:
            return "Let's talk about movies, shall we?"  

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
          print(
              sentiments) // prints [("Titanic (1997)", 1), ("Ex Machina", 1)]

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
        inds = []
        min_so_far = float('inf')
        for i in range(len(self.titles)):
            cur_title = self.titles[i][0][:self.titles[i][0].find("(") - 1]
            distance = self.min_edit_dist(title.lower(), cur_title.lower())
            # print(f"Inds: {inds}; Cur_Title: {cur_title}; Dist: {distance}")
            if distance < min_so_far:
                min_so_far = distance
            if distance <= max_distance:
                inds.append((distance, i))

        inds = [x[1] for x in inds if x[0] == min_so_far]
        return inds

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
        inds = []
        for canidate in candidates:
            choice = self.titles[canidate][0].lower().replace(',', '')
            choice = "".join([i for i in choice if i not in self.punctuations])
            choice = choice.split()
            clarification = "".join(
                [i for i in clarification if i not in self.punctuations])
            clarification = clarification.lower().replace(',', '')
            # print(clarification, choice)
            if clarification in choice:
                inds.append(canidate)

        return inds

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
        binarized_ratings[ratings > threshold] = 1
        binarized_ratings[ratings <= threshold] = -1
        binarized_ratings[ratings == 0] = 0

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
        dot_product = np.dot(u, v)
        norm_u = np.linalg.norm(u)
        norm_v = np.linalg.norm(v)
        if norm_u * norm_v != 0:
            similarity = dot_product / (norm_u * norm_v)
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
        movie_idxs = np.array(np.where(user_ratings == 0))[0]
        rated = np.where(user_ratings != 0)
        rated = np.array(rated)[0]

        # Find s_ij for each unrated movie
        sims = np.zeros(len(movie_idxs))
        pos = 0
        for i in movie_idxs:
            vec_i = ratings_matrix[i, :]
            for j in rated:
                vec_j = ratings_matrix[j, :]
                sims[pos] += self.similarity(vec_i, vec_j) * user_ratings[j]
            pos += 1
        ind = np.lexsort((-movie_idxs, sims))
        recommendations = [movie_idxs[m] for m in np.flip(ind)]
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
        if self.creative:
            return """
            I'm Baddie Bot. I know you want to Netflix and Chill with me. 
            But I gotta assess your vibe first. Tell me about your movie taste.
            """
        return """
        I'm Movie Bot! I'd love to chat with you about your movie taste and give 
        you some recommendations.
        """


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
