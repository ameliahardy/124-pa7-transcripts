# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util

import numpy as np
import re
import porter_stemmer

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

        # Stem the sentiments
        self.stemmer = porter_stemmer.PorterStemmer()
        self.stemmed_sentiments = {}
        for k in self.sentiment:
            self.stemmed_sentiments[self.stemmer.stem(k)] = self.sentiment[k]
        
        # Set up negation words and punctuation
        self.negation_words = ['no', 'not', 'nobody', 'nothing', 'neither', 'nowhere', 'never', 'overly', 'too']
        self.punctuation = '!#()-[]\{\};:\,<>./?@#$%^&*_~'
        self.reverse_words = ['but', 'however', 'yet', 'nevertheless']
        self.verbs_describe_movies = ["like", "liked", "think", "thought","love","loved","adored","adore","enjoy","enjoyed", 
                                      "hate","hated","abhorred","abhor","loathed","loathe","despise", "despised"]
        self.movie_articles = ["the", "an", "a"]
        self.similarity_conjunctions = ["and", "both", "or", "either"]
        self.difference_conjunctions = ["but", "yet"]

        # Other setup
        self.count = 0
        self.data_points = np.zeros(len(self.titles))
        self.recommendations = []

        self.prev = False
        self.prev_movie = ""
        self.prev_sentiment = 0

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

        if self.creative:
            greeting_message = "Dear reader, the social season is upon us. It is I, Lady Whistledown, and today I shall recommend to you a moving picture, a movie as they say nowadays.\n I must know what movies have pleased you so that I am able to make a most appropriate reccommendation. Would you please write about a movie that you have enjoyed?"
        else:
            greeting_message = "Hi, my name is Whistledown. I'd like to recommend a movie to you. First, I need to know about your taste in movies. Please tell me about a movie you have liked."

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

        if self.creative:
            goodbye_message = "I bid you farewell. All if fair in love and war. \nYours Truly,\nLady Whistledown"
        else:
            goodbye_message = "Goodbye."

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

        movies = self.extract_titles(line)
        sentiment = self.extract_sentiment(line)
        
        #ENTER STARTER MODE
        if self.creative == False:
            if len(movies) == 0:
                response = "I apologize dearly, I do not understand which movie you have seen. Would you please type it again?"

            if len(movies) == 1:
                match = self.find_movies_by_title(movies[0])
                if len(match) == 1:   
                    if sentiment == 0:
                        response = "I apologize, I'm not sure if you liked \"" + movies[0] + "\" Tell me more about \"" + movies[0] + "\". "
                    else:
                        if sentiment > 0:
                            sent = "enjoyed "
                        else:
                            sent = "did not enjoy "

                        self.data_points[match[0]] = sentiment
                        self.count += 1
                        if self.count < 5:
                            response = "I understand. You " + sent + "\"" + movies[0] + "\". Thank you. Would you tell me about another film you've watched?"
                        else:
                            response = "I understand. You " + sent + "\"" + movies[0] +"\"."
                elif len(match) == 0:
                    response = "I apologize, I cannot find " + "\"" + movies[0] + "\" in my database. Please enter another title."
                elif len(match) > 1:
                    response = "I found multiple movies that match this movie title. Please clarify which movie you're referring to: "
                    for id_mov in match:
                            response = response + "\n\"" + self.titles[id_mov][0] + "\""
                        
            if len(movies) > 1:
                response = "Please tell me about one movie at a time."

            if self.count >= 5:
                if len(self.recommendations) == 0:
                    response = "No recommendations. Please provide more information to get new recommendations."
                    return response
                num = np.random.randint(0,len(self.recommendations))
                if line == "yes":
                    if len(self.recommendations) == 0:
                        response = "You have exhausted all recommendations. Please provide more information to get new recommendations."
                    else:
                        response = "\"" + self.titles[self.recommendations[num]][0] + "\" would be another good title for you. \n Would you like to hear another recommendation? (or enter :quit to :quit)"
                        self.recommendations.remove(self.recommendations[num])
                else:
                    recommendations = self.recommend(self.data_points, self.ratings)
                    self.recommendations = recommendations
                    response = response + "\nI have enough information to make a recommendation. I believe you would enjoy " + "\"" + self.titles[recommendations[num]][0] + "\"\n Would you like to hear another recommendation? (type yes or enter :quit to quit)"
        
        #ENTER CREATIVE MODE
        else:
            if self.prev == True:
                if self.prev_sentiment > 0:
                    sent = "enjoyed "
                else:
                    sent = "did not enjoy "
                response = "Great. You " + sent + "\"" + self.prev_movie + "\". Please tell me about another movie."
                self.prev = False
                
            else:
                if len(movies) == 0:
                    response = "Dear reader, we all must know what the queen despises more than anything--an incomprehendible response to a simple question. I do not understand which movie you have seen. Would you please write it out again?"

                if len(movies) == 1:
                    match = self.find_movies_by_title(movies[0])
                    if len(match) == 1:   
                        if sentiment == 0:
                            response = "I apologize, I am unsure whether \"" + movies[0] + "\" pleased you. Would you care to tell me more about \"" + movies[0] + "\". "
                        else:
                            if sentiment > 0:
                                sent = "enjoyed "
                            else:
                                sent = "did not enjoy "

                            self.data_points[match[0]] = sentiment
                            self.count += 1
                            if self.count < 5:
                                response = "I understand, dear reader. You " + sent + "\"" + movies[0] + "\". You certainly have an appreciation for the arts. Would you tell me another film that has tickled your fancy?"
                            else:
                                response = "I understand, dear reader. You " + sent + "\"" + movies[0] +"\"."
                    elif len(match) == 0:
                        close_movies = self.find_movies_closest_to_title(movies[0])
                        if len(close_movies) == 1:
                            response = "I apologize, I was unable to locate \"" + movies[0] + "\" in my database. I found a close title, is this what you meant: \"" + self.titles[close_movies[0]][0] + "\"?"
                            self.prev = True
                            self.prev_movie = self.titles[close_movies[0]][0]
                            self.prev_sentiment = sentiment

                        elif len(close_movies) > 1:
                            response = "I apologize, I did not find \"" + movies[0] + "\" among the queen's ever so cherished crown jewels. However, I found a few titles that shine just as bright--are you mistaken for one of these: "
                            for mov in close_movies:
                                response = response + "\n\"" + self.titles[close_movies[mov]][0] + "\""
                        else:
                            response = "I apologize, I cannot find \"" + movies[0] + "\" among the queen's ever so cherished crown jewels. Please write another title, ."
                    elif len(match) > 1:
                        response = "Multiple films were found among the queen's crown jewels. Which movie would you refer to: "
                        for mov in match:
                            response = response + "\n\"" + self.titles[mov][0] + "\""

                if len(movies) > 1:
                    response = "Dear reader, this is scandalous, the queen can only handle so much. Please only refer to one film title at a time."

            if self.count >= 5:
                if len(self.recommendations) == 0:
                    response = "It seems I need a tad more information to recommond to you more films. Would you tell me about another film you have seen, perhaps at last night's soiree?"
                    return response
                num = np.random.randint(0,len(self.recommendations))
                if line == "yes":
                    if len(self.recommendations) == 0:
                        response = "It seems I need a tad more information to recommond to you more films. Would you tell me about another film you have seen, perhaps at last night's soiree?"
                    else:
                        response = "The diamond of the season has found her match! \"" + self.titles[self.recommendations[num]][0] + "\" would be phenomenal title for you. \n Would you care for an additioa\nal recommendation? (yes or enter :quit to quit)"
                        self.recommendations.remove(self.recommendations[num])
                else:
                    recommendations = self.recommend(self.data_points, self.ratings)
                    self.recommendations = recommendations
                    response = response + "\nThis author finds herself compelled to share the most curious of news. I believe you would enjoy " + "\"" + self.titles[recommendations[num]][0] + "\", it is a treasure.\n May I share an additional recommendation?(type yes or enter :quit to quit)"

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

    def getTitlesList(self):
        all_titles = [title[0] for title in self.titles]
    
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
        # CREATIVE MODE: extracting movie titles w/o quotation marks/capitalization
        if self.creative:
            lowercase_input = preprocessed_input.lower()
            num_quotes = preprocessed_input.count("\"")
            if num_quotes % 2 == 0 and num_quotes != 0:  # if even number of quotes, return original logic
                return preprocessed_input.split("\"")[1::2]
            
            potential_titles = []
            pattern_1 = 'i ([\w]+) ([^?.!]+)([?.!]*$)'  # ex: I liked <movie>! 
            matches_1 = re.findall(pattern_1, lowercase_input)
            
            pattern_2 = 'i ([\w]+) ([\w]+) ([^?.!]+)([?.!]*$)'  # ex: I really liked <movie>! 
            matches_2 = re.findall(pattern_2, lowercase_input)
            
            # ex: I thought Percy Jackson was a good movie (remove the "was a good movie")
            # Used further below when adding potential titles
            detail_pattern = '([ ]*)(?:is|was|isn\'t|is not|wasn\'t|was not|are|aren\'t|are not).*$'
            
            first_matches = [m_1[1] for m_1 in matches_1] # add from 2nd register
            second_matches = [m_2[2] for m_2 in matches_2] # add from 3rd register
            
            num_matches = len(first_matches)
            
            if num_matches == 0:
                potential_title = re.sub(detail_pattern, '', lowercase_input).strip()
                potential_titles.append(potential_title)
                return potential_titles
            
            for m in range(num_matches):
                title_1 = first_matches[m]
                if m >= len(second_matches):
                    potential_titles.append(title_1)
                    continue
                title_2 = second_matches[m]
                

                title_1 = re.sub(detail_pattern, '', title_1).strip()  # .strip() removes whitespace from beg/end
                title_2 = re.sub(detail_pattern, '', title_2).strip()  
                
                if title_1[0] in self.verbs_describe_movies:
                    potential_titles.append(title_2)
                elif title_1[0] in self.movie_articles:
                    potential_titles.append(title_1)
                else:
                    potential_titles.append(title_1)
            return potential_titles
                    
        # If we see something like: hello "there" what is "up with u",
        # then splitting gives us [hello , there,  what is , up with u,]
        # notably, we want all the odd elements, so we do [1::2]
        # (grab every second element, starting with element at index 1)        
        return preprocessed_input.split("\"")[1::2]

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

        def split_year_and_title(x):
            # We're using rfind instead of find because some movies have parentheses not used for years
            # For instance, "Dumb & Dumber (Dumb and Dumber) (1994)"
            from_idx = x.rfind('(')
            to_idx = x.rfind(')')
            if from_idx == -1 or to_idx == -1:
                return (x, None)
            year = x[from_idx + 1 : to_idx]
            # If it's a four-digit number, we're in the clear
            if year.isnumeric() and len(year) == 4:
                return (x[:from_idx].strip(), int(year))
            return (x, None)

        def split_into_details(x):
            # For example, "Hello (World) (What's Up) (1993)"
            # Returns ["Hello", ["World", "What's Up"], 1993]
            if not( '(' in x and ')' in x ):
                return ([x], None)
            titles = [x[:x.find('(')].strip()] # "Hello"
            year = None
    
            x = x[x.find('('):] # "(World) (What's Up) (1993)"
            while (x.find('(') != -1): # while we still have a parenthesis
                to_idx = x.find(')')
                if to_idx == -1:
                    return (titles, year)

                info = x[1:to_idx] # "World"

                # If it's a four-digit number, that's a year
                if info.isnumeric() and len(info) == 4:
                    year = int(info)
                else:
                    if info.startswith("aka "):
                        info = info[4:]
                    elif info.startswith("a.k.a. "):
                        info = info[7:]
                    titles.append(info)
                
                # Update the string
                if to_idx < len(x):
                    x = x[to_idx+1:].strip()
                else:
                    x = ""

            # Remove aka, a.k.a.
            return (titles, year)
        
        def move_article_to_end(x):
            # English
            if x.startswith("the "):
                return x[4:] + ", the"
            if x.startswith("an "):
                return x[3:] + ", an"
            if x.startswith("a "):
                return x[2:] + ", a"
            # French and Spanish
            if x.startswith("la "):
                return x[3:] + ", la"
            if x.startswith("le "):
                return x[3:] + ", le"
            if x.startswith("un "):
                return x[3:] + ", un"
            if x.startswith("une "):
                return x[4:] + ", une"
            if x.startswith("una "):
                return x[4:] + ", una"
            if x.startswith("los "):
                return x[4:] + ", los"
            if x.startswith("las "):
                return x[4:] + ", las"
            if x.startswith("les "):
                return x[4:] + ", los"
            return x
                
        matching_titles = []
        # Loop through all the titles in self.titles (enumerate lets us grab the element AND its index)
        # Each title is formatted like: ["Toy Story (1995)", "Adventure|Animation|Children|Comedy|Fantasy"]
        if not self.creative:
            for idx, t in enumerate(self.titles):
                inputted = split_into_details(title.lower()) # Should already be in lowercase
                potential = split_into_details(t[0].lower()) # Grab the title, not the genres

                # If the title matches exactly
                if inputted == potential:
                    matching_titles.append(idx)
                    continue

                # If they typed in a potential title (titles, year)
                matching = False
                for inputted_title in inputted[0]:
                    for potential_title in potential[0]:
                        if move_article_to_end(inputted_title) == move_article_to_end(potential_title):
                            matching = True
                        if inputted_title == potential_title:
                            matching = True

                # Matching title!
                if matching:
                    # Either the dates are the same, or the input title has no date
                     if inputted[1] == None or inputted[1] == potential[1]:
                        matching_titles.append(idx)
                        continue
        else:  # CREATIVE mode
           for idx, t in enumerate(self.titles):
                inputted = split_into_details(title.lower()) # Should already be in lowercase
                potential = split_into_details(t[0].lower()) # Grab the title, not the genres

                # If the title matches exactly
                if inputted == potential:
                    matching_titles.append(idx)
                    continue

                # If they typed in a potential title (titles, year)
                matching = False
                for inputted_title in inputted[0]:
                    for potential_title in potential[0]:
                        if move_article_to_end(inputted_title) == move_article_to_end(potential_title):
                            matching = True
                        if inputted_title == potential_title:
                            matching = True

                # Matching title!
                if matching:
                    # Either the dates are the same, or the input title has no date
                     if inputted[1] == None or inputted[1] == potential[1]:
                        matching_titles.append(idx)
                        continue

                # Disambiguation (part 1) return titles that have it as a subtoken
                for potential_match in potential[0]:
                    if title not in potential_match:  # skip if title not a substring of current title
                        continue
                    print("Title in:", potential_match)
                    title_pattern = '' + title + '[^\w]'  # the title by itself (not within another word) 
                    matches = re.findall(title_pattern, potential_match)
                    if len(matches) == 0:
                        continue
                    matching_titles.append(idx)
        return matching_titles

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
        
        # Remove titles and punctuation from sentiment analysis
        titles = self.extract_titles(preprocessed_input)
        for title in titles:
            preprocessed_input = preprocessed_input.replace(title, "")
        for punc in self.punctuation:
            preprocessed_input = preprocessed_input.replace(punc, "")

        sentiment_sum = 0
        words = preprocessed_input.lower().strip().split()
        base_sentiment = 1 # This is so that when you say "however" or "but" it INCREASES the value of what comes next
        for idx, word in enumerate(words):
            
            if word in self.reverse_words:
                base_sentiment += 1
            
            stemmed_word = self.stemmer.stem(word)
            if stemmed_word in self.stemmed_sentiments:

                sentiment = base_sentiment

                # If they say "super" or "really", ignore the meaning of that word and double the next one
                if idx > 0 and words[idx - 1] in ['super', 'really', 'very']:
                    sentiment += 1
                if idx > 1 and words[idx - 2] in ['super', 'really', 'very']:
                    sentiment += 1

                if self.stemmed_sentiments[stemmed_word] == 'neg':
                    sentiment *= -1
                    
                # Two opportunities to reverse the meaning ("It's not not good" vs. "It's not good")
                if idx > 0 and (words[idx - 1] in self.negation_words or words[idx - 1].endswith("n't")):
                    sentiment *= -1
                if idx > 1 and (words[idx - 2] in self.negation_words or words[idx - 2].endswith("n't")):
                    sentiment *= -1

                # Words that we want to ignore
                if word in ['thought', 'super']:
                    sentiment = 0

                sentiment_sum += sentiment

        if sentiment_sum == 0:
            return 0
        elif sentiment_sum > 0:
            return 1
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
        titles = self.extract_titles(preprocessed_input)
        overall_sentiment = self.extract_sentiment(preprocessed_input)
        title_positions = []
        punctuation_chars = self.punctuation.split()
        
        lowercased_input = preprocessed_input.lower()
        
        for t in titles:
            lower_title = t.lower()
            title_positions.append(lowercased_input.index(lower_title))
            
        num_titles = len(title_positions)
        
        for i in range(num_titles):           
            t_pos = title_positions[i]
            title = titles[i]
            similar_conjunction = False
            diff_conjunction = False
            punctuation = False
            if i == 0:  # if first movie mentioned
                beg_text = preprocessed_input[0:t_pos]
            else:
                prev_pos = title_positions[i-1] + len(titles[i-1])  # previous pos + len of title
                beg_text = preprocessed_input[prev_pos:t_pos]
            after_title = t_pos + len(titles[i])  # pos + len of title
            if i == num_titles - 1:  # if last movie mentioned
                end_text = preprocessed_input[after_title:]
            else:
                next_pos = title_positions[i+1] # next pos + len of title
                end_text = preprocessed_input[after_title:next_pos]
              
            beg_sentiment = self.extract_sentiment(beg_text)
            end_sentiment = self.extract_sentiment(end_text)
            if any(conj in beg_text for conj in self.similarity_conjunctions):
                similar_conjunction = True
            if any(conj in beg_text for conj in self.difference_conjunctions):
                diff_conjunction = True
            if any(punc in beg_text for punc in punctuation_chars):
                punctuation = True
            
            if i == 0:
                sentiments.append((title, beg_sentiment)) # sentiment of first part of sentence
            elif similar_conjunction:
                last_sentiment = sentiments[-1][1]
                sentiments.append((title, last_sentiment))
            elif diff_conjunction:  #but, yet
                last_sentiment = sentiments[-1][1]
                sentiments.append((title, -last_sentiment))  # store opposite sentiment
            elif punctuation:
                if (beg_sentiment > 0 and end_sentiment < 0) or (beg_sentiment < 0 and end_sentiment > 0):
                    sentiments.append((title, end_sentiment))  # store what is described afterwards
                else:
                    sentiments.append((title, beg_sentiment))
            else:
                sentiments.append((title, beg_sentiment)) 
        return sentiments

    def calculate_edit_distance(self, title_A, title_b):
       
        def split_year_and_title(x):
            # We're using rfind instead of find because some movies have parentheses not used for years
            # For instance, "Dumb & Dumber (Dumb and Dumber) (1994)"
            from_idx = x.rfind('(')
            to_idx = x.rfind(')')
            if from_idx == -1 or to_idx == -1:
                return (x, None)
            year = x[from_idx + 1 : to_idx]
            # If it's a four-digit number, we're in the clear
            if year.isnumeric() and len(year) == 4:
                return (x[:from_idx].strip(), int(year))
            else:
                return (x, None)
           
        b_pair = split_year_and_title(title_b)
        title_B = b_pair[0]
       
        edit_distance = np.zeros((len(title_A) + 1, len(title_B) + 1))
        edit_distance[0][0] = 0
       
        for i in range(len(title_A)):
            edit_distance[i+1][0] = i + 1
        for i in range(len(title_B)):
            edit_distance[0][i+1] = i + 1
       
        for a, char_a in enumerate(title_A):
            id_a = a + 1
            for b, char_b in enumerate(title_B):
                id_b = b + 1
               
                left = edit_distance[id_a - 1][id_b] + 1
                down = edit_distance[id_a][id_b - 1] + 1
                diag = edit_distance[id_a - 1][id_b - 1] + 2
                if char_a == char_b:
                    diag = edit_distance[id_a - 1][id_b - 1]
                edit_distance[id_a][id_b] = np.amin([left, down, diag])
        return edit_distance[len(title_A)][len(title_B)]


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
        
        def edit_distance(s1, s2_orig):
            def split_year_and_title(x):
                # We're using rfind instead of find because some movies have parentheses not used for years
                # For instance, "Dumb & Dumber (Dumb and Dumber) (1994)"
                from_idx = x.rfind('(')
                to_idx = x.rfind(')')
                if from_idx == -1 or to_idx == -1:
                    return (x, None)
                year = x[from_idx + 1 : to_idx]
                # If it's a four-digit number, we're in the clear
                if year.isnumeric() and len(year) == 4:
                    return (x[:from_idx].strip(), int(year))
                else:
                    return (x, None)
           
            s2 = split_year_and_title(s2_orig)[0]
            n = len(s1)
            m = len(s2)
            dist = [[0 for x in range(n + 1)] for y in range(m + 1)]

            for i in range(1, m + 1):
                dist[i][0] = i

            for j in range(1, n + 1):
                dist[0][j] = j

            for j in range(1, n + 1):
                for i in range(1, m + 1):
                    if s1[j - 1] is s2[i - 1]:
                        cost = 0
                    else:
                        cost = 2
                    dist[i][j] = min(dist[i - 1][j] + 1,
                                  dist[i][j - 1] + 1,
                                  dist[i - 1][j - 1] + cost)

            return dist[m][n]
        
        close_titles = []
        smallest_ed = max_distance + 1
        ed_dists = []
        
        for i, t in enumerate(self.titles):
            title = title.lower()
            potential_match = t[0].lower()
          
            ed_dist = edit_distance(title, potential_match) #self.calculate_edit_distance(title, potential_match)
            ed_dists.append(ed_dist)
            if ed_dist <= max_distance:
                if ed_dist < smallest_ed:
                    smallest_ed = ed_dist
                    close_titles = [i]
                elif ed_dist == smallest_ed:
                    close_titles.append(i) 
        return close_titles

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
        lowercase_titles = [self.titles[idx][0].lower() for idx in candidates]
        lowercase_clarification = clarification.lower()
        new_candidates = []
        order_words = {"first": 0,
                       "second": 1,
                       "third": 2,
                       "fourth": 3,
                       "recent": 0,
                       "last": -1,
                       "one": 1}
#         print(lowercase_titles)
        if lowercase_clarification.isnumeric():
            num = int(lowercase_clarification)
            if num < 1000 and num <= len(candidates):
                return [candidates[num - 1]]
            
        # TODO: Handle cases like "the second one, second, etc.", "most recent")
        for word in order_words.keys():
            pattern = '' + word  # ex: the second one, match: second 
            matches = re.findall(pattern, lowercase_clarification)
            if len(matches) == 0:
                continue
            idx = order_words[word]
            if word == "one" and len(lowercase_clarification) > len("one"):
                lowercase_clarification = re.sub("one", "", lowercase_clarification)  # remove "one" from "the Goblet of Fire one
                lowercase_clarification = lowercase_clarification.strip()
                continue  
            return [candidates[idx]]
       
        for t in range(len(lowercase_titles)):
            title = lowercase_titles[t]
            if lowercase_clarification not in title:
                continue
            new_candidates.append(candidates[t])  # substring in title 
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
        positive = np.where(ratings > threshold, 1, 0)
        negative = np.where((ratings <= threshold) & (ratings > 0), -1, 0)
        binarized_ratings = np.add(positive, negative)

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
        norm_u = np.linalg.norm(u)
        norm_v = np.linalg.norm(v)
        if norm_u == 0 or norm_v == 0:
            return 0
        similarity = np.dot(u, v) / (norm_u * norm_v)
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
        ratings = []

        for i, movie_ratings_i in enumerate(ratings_matrix):
            # We only want to recommend movies the user hasn't seen
            if user_ratings[i] != 0:
                continue

            cosine_similarities = np.zeros_like(user_ratings)
            for j, movie_ratings_j in enumerate(ratings_matrix):
                # We only care about movies that the user has rated here
                if user_ratings[j] == 0:
                    continue

                # Calculate the cosine similarity between movies i and j
                cosine_similarities[j] = self.similarity(movie_ratings_i, movie_ratings_j)
            ratings.append((np.dot(cosine_similarities, user_ratings), i))
        ratings = sorted(ratings, key=lambda x: x[0], reverse=True)
        recommendations = [rating[1] for rating in ratings[:k]]

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
