# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util

import numpy as np
import re
from porter_stemmer import PorterStemmer
import random


# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'Homer Simpson Recommendations'

        self.creative = creative
        self.p = PorterStemmer()

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')
        self.watchedVector = np.zeros(len(self.titles))
        self.watchedMovies = 0
        self.initialRec = 'yes'
        self.numRec = 0

        ########################################################################
        # TODO: Binarize the movie ratings matrix.                             #
        ########################################################################

        # Binarize the movie ratings before storing the binarized matrix.
        ratings = np.where((ratings <= 2.5) & (ratings > .0), -1, ratings)
        ratings = np.where((ratings > 2.5) & (ratings <= 5), 1, ratings)
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
        if self.creative == True:
            greeting_message = """Homer Simpson Bot, powering on... Since I've seen every movie, I'm the best movie recommendation bot! Give me 5 movies and tell me whether you like or don't like them, and I'll tell you some other movies you'll love! Afterwards, we can all go out for some frosty chocolate milkshakes!"""
        else:
            greeting_message = """Hello, I am BoringBot, happy to serve you!"""

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
        if self.creative == True:
            goodbye_message = "Bye Mr. Flanders! Homer Bot, shutting down..."
        else:
            goodbye_message = "Bye! BoringBot, shutting down..."

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
        
        ########################################################################
        # TODO: Implement the extraction and transformation in this method,    #
        # possibly calling other functions. Although your code is not graded   #
        # directly based on how modular it is, we highly recommended writing   #
        # code in a modular fashion to make it easier to improve and debug.    #
        ########################################################################
        """
        positive = ['yes', 'yah', 'ya', 'yeah']
        
        
        
        if self.creative:
            response = "I processed '{}' in creative mode!!".format(line)
        else:
            response = "I processed '{}' in starter mode!!".format(line)
            
            

        if self.creative == True:
            sent0_bank = ["""Hmmmm... Could you tell me a little bit more about that movie? I can't tell if you liked """, """Aaargh! I didn't get that, could you tell me a little more about """, """Doh!! I can't tell if you liked or disliked that movie. Could you clarify how to felt about """, """Jeepers! My radar is confused! Could you clarify your thoughts on """]

            sentpos_bank = ["""Doh! I left the dog on the roof! I'm glad you liked """, """Doh! My goldfish got out of the tank again! Oops, didn't see you there! I also liked """, """Woo Hoo! That's one of my top ranked films! I really liked """, """You like that movie, eh? I liked this donut more than I liked """]

            sentneg_bank = ["""Doh, I'm sorry you didn't like """, """Ay caramba! That's an awful movie. I hated """, """MARGE!! I left the pizza in the oven from last nigh- Oh, oops! I also didn't """, """Whaaaaaat?!?! I loved that movie! I can't believe you hated """]

            no_movie = ["""Stupid flanders! That movie doesn't exist! Try again?""", """Doh! I couldn't find that movie in the Homer Simpson database. Give it another shot?""", """Homer Simpson doesn't know that movie? Want to try another?""", """ARGGGGG! I don't know that movie and now I'm mad!! Can you tell me about another movie? In the meantime, BARTTTT WHERE AREEE YOUUUUU?!?!?!"""]

            recommend_bank1 = ["""Given what you told me, I think you'd love """, """Ay caramba! What an interesting movie palette. I think you'd also like """, """Hmmmm, you might also like """, """Great choices! I'm thinking you'll also love """, """I think someone eats a donut in this movie, so obviously I'd recommend """]

            recommend_bank2 = ["""Would you like another recommendation? Tell me quick, Maggie is crying! """, """Doh, Bart get your head out the microwave!! Quick tell me if you want another recommendation before Bart burns! """, """Marge wants to know if you want another recommendation. Yes or no? """, """You seem to be loving these. Wanna keep it going? """]

            more_data = ["""Tell me about another movie, would ya?""", """BART! STOP LICKING THE DOG!!! Anyways, I want to hear about another movie.""", """Boringgggg. Tell me about a different movie before I fall asleep.""", """Mmmmm, donuts. While I eat this next one, tell me about another movie?"""]

            found_two_movies = ["""You gave me two movies! How bout you tell me about one?""", """Woo Hoo! Wait... thats two movies. Tell me about just one please!""", """Mmmmm, this ice cream would taste so good with a donut. Tell me about just one movie, you gave me two!""", """Doh! Thats two movies! Tell me about just one! After that, want to help me rob the Kwik-E-Mart?"""]
        
        
        
        else:
            sent0_bank = ["""Please include more information about """, """I could not decipher if you liked or disliked """, """I didn't catched whether you liked """]

            sentpos_bank = ["""I'm glad you liked """, """I'm happy to see you enjoyed """, """ I agree! I really like the story in """]

            sentneg_bank = ["""I'm sorry you didn't like """, """I agree. I couldn't stand the story in """, """That's good. No one in their right mind likes """]

            no_movie = ["""I couldn't find that movie.""", """I couldn't find that movie in my database. """, """I don't know that movie. """]

            recommend_bank1 = ["""Given what you told me, I think you'd love """, """I think you'd also like """, """You should watch """]

            recommend_bank2 = ["""Do you want another recommendation?""", """I got more recommendations ready. Do you want more? """, """I'm ready when you are. Wanna continue?"""]

            more_data = ["""Can you tell me about another movie?""", """I can almost give you a recommendation. Could you tell me about another movie?""", """Now onto the next movie! Tell me about another one.""" ]

            found_two_movies = ["""You gave me two movies! Could you tell me about one?""", """Tell me about just one movie please!""", """My tiny little brain can't comprehend more than one movie. Please only give me one move at a time."""]     
            
            
        
        arbitrary_input = {"can": "I'm Homer Simpson. Obviously I can! Not.", "what": "Doh! I don't know what you mean by that...", "are" : "Doh! I'm Homer Simpson, do I look like I know the answer?", "why" : "Why...why...why what? Bart!! Do you know the answer to this question? Sorry, you're out of luck here."}
        
        angerWords = ['contempt', 'disgust', 'revulsion', 'envy', 'jealousy', 'exasperation', 'frustration', 'aggravation', 'agitation', 'annoyance', 'grouchiness', 'grumpiness', 'irritation', 'anger', 'bitterness', 'dislike', 'ferocity', 'fury', 'hate', 'hostility', 'loathing', 'outrage', 'rage', 'resentment', 'scorn', 'spite', 'vengefulness', 'wrath', 'torment', 'angry']

        fearWords = ['alarm', 'fear', 'fright', 'horror', 'hysteria', 'mortification', 'panic', 'shock', 'terror', 'anxiety', 'apprehension', 'distress', 'dread', 'nervousness', 'tenseness', 'uneasiness', 'worry', 'scared']

        happyWords = ['amusement', 'bliss', 'cheerfulness', 'delight', 'ecstasy', 'elation', 'enjoyment', 'euphoria', 'gaiety', 'gladness', 'glee', 'happiness', 'happy', 'jolliness', 'joviality', 'joy', 'jubilation', 'satisfaction', 'contentment', 'pleasure', 'enthrallment', 'rapture', 'eagerness', 'hope', 'optimism', 'pride', 'triumph', 'relief', 'enthusiasm', 'excitement', 'exhilaration', 'thrill', 'zeal', 'zest']

        sadWords = ['disappointment', 'dismay', 'displeasure', 'alienation', 'defeat', 'dejection', 'embarrassment', 'homesickness', 'humiliation', 'insecurity', 'isolation', 'insult', 'loneliness', 'neglect', 'rejection', 'depression', 'despair', 'gloom', 'glumness', 'grief', 'hopelessness', 'melancholy', 'misery', 'sadness', 'sorrow', 'unhappiness', 'woe', 'guilt', 'regret', 'remorse', 'shame', 'agony', 'anguish', 'hurt', 'suffering', 'pity', 'sympathy', 'sad', 'miss']

        loveWords = ['adoration', 'affection', 'attraction', 'caring', 'compassion', 'fondness', 'liking', 'sentimentality', 'tenderness', 'longing', 'arousal', 'desire', 'infatuation', 'lust', 'passion']

        surpriseWords = ['amazement', 'astonishment', 'surprise']
        
        
        
        
        angerPhrase = ["""Woah woah woah! Didn't mean to hurt your feelings pal!""", """D'ohoooopss! Didn't mean to get ya all riled up!"""]
        
        fearPhrase = ["""Hey there, it'll be alright, no one's gonna hurt ya.""", """D'oh! Don't be scared now, you're okay."""]
        
        happyPhrase = ["""Woohoo! When you're happy, I'm happy!""", """You seem almost as happy as me when I have a donut in my hand!"""]
        
        sadPhrase = ["""Argh! You'll be back to normal soon!""", """Don't be sad! Let me take you out for a donut."""]
        
        lovePhrase = ["""Love isn't hopeless. Look, maybe I'm no expert on the subject, but there was one time I got it right.""", """Something you love is like a beer. It looks good and you’d step over your own mother to get it"""]
        
        surprisePhrase = ["""Wohooah! Suprised ya, didn't I?""", """HA! You should see the look of shock on your face!"""]

        if self.creative == True:
            lineTokens = line.split()
            if lineTokens[0].lower() in arbitrary_input:
                return response + " " + arbitrary_input[lineTokens[0].lower()] + " " + random.choice(more_data)

            for token in lineTokens:
                if token.lower() in angerWords:
                    return response + " " + random.choice(angerPhrase)

            for token in lineTokens:
                if token.lower() in fearWords:
                    return response + " " + random.choice(fearPhrase)

            for token in lineTokens:
                if token.lower() in happyWords:
                    return response + " " + random.choice(happyPhrase)

            for token in lineTokens:
                if token.lower() in loveWords:
                    return response + " " + random.choice(lovePhrase)

            for token in lineTokens:
                if token.lower() in sadWords:
                    return response + " " + random.choice(sadPhrase)

            for token in lineTokens:
                if token.lower() in surpriseWords:
                    return response + " " + random.choice(surprisePhrase)
            
        
        foundTitles = self.extract_titles(line)
        if len(foundTitles) == 0:
            return response + " " + random.choice(no_movie)
        
        elif len(foundTitles) >= 2:
            return response + " " + random.choice(found_two_movies)
        

        titleIndex = self.find_movies_by_title(foundTitles[0])
        if not titleIndex and self.creative == False:
            return response + " " + random.choice(no_movie) + " " + random.choice(more_data)
        
        elif not titleIndex and self.creative == True:
            closestMovies = self.find_movies_closest_to_title(foundTitles[0], max_distance=5)
            if len(closestMovies) == 0:
                return response + " " + random.choice(no_movie)
            
            else:
                checkMovie = input("Did you mean the movie '" + self.titles[closestMovies[0]][0] + "'? ").lower()
                if checkMovie in positive:
                    titleIndex.append(closestMovies[0])
                    
        elif len(titleIndex) >= 2:
            return "There's more than one movie with the name '" + foundTitles[0] + "'. Can you repeat with the specific version?"
        
        sentiment = self.extract_sentiment(line)
        if sentiment == 0:
            response += " " + random.choice(sent0_bank) + foundTitles[0] +"."
            return response
            
        elif sentiment >= 1:
            response += " " + random.choice(sentpos_bank) + foundTitles[0] +"."
            self.watchedMovies += 1
            self.watchedVector[titleIndex[0]] = 1

        elif sentiment <= -1:
            response += " " + random.choice(sentneg_bank) + foundTitles[0]+"."
            self.watchedVector += 1
            self.watchedVector[titleIndex[0]] = -1
        
        if self.watchedMovies < 5:
            return response + " " + random.choice(more_data)

        while self.initialRec in positive:
            recs = self.recommend(self.watchedVector, self.ratings, self.numRec + 1, self.creative)
            print(random.choice(recommend_bank1), self.titles[recs[-1]][0])
            self.numRec += 1
            
            self.initialRec = input(random.choice(recommend_bank2) + " ").lower()
            
            if self.initialRec not in positive:
                return self.goodbye()

        return response + random.choice(more_data)

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
        i = 0
        titles = [] 
        start_quote = None
        
        while i < len(preprocessed_input): 
            if preprocessed_input[i] == '"' and start_quote is None:
                start_quote = i
                
            elif preprocessed_input[i] == '"' and start_quote is not None:
                titles.append(preprocessed_input[start_quote+1:i])
                start_quote = None
                
            i = i + 1
            
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
        
        valid_titles = []
        for i in range(len(self.titles)):
            first_term = self.titles[i][0]
            valid_titles.append(first_term)
        
        valid_titles_no_year = []
        for t in valid_titles:
            new_title = t[:-7]
            valid_titles_no_year.append(new_title)
        
        result = []
        article_check = ['an', 'a', 'the', 'An', 'A', 'The', 'AN', 'THE', 'THe']
        # what is the current title we are working with:
        words = title.split()
            
        # to hold articles vs. non-articles
        articles = []
        no_articles = []
        
        has_year = False
        
        # loop over the words 
        for word in words:
            if word in article_check:
                articles.append(word)
            else: 
                no_articles.append(word)
        # rewriting the string
        updated_string = ''
        year = no_articles[-1]
        
        if len(title) > 8:
            if title[-7] == " " and title[-5:-1].isdigit() and title[-1] == ")":
                has_year = True
        
        # case #1 - there are no articles 
        if len(articles) == 0:
            for word in no_articles + articles:
                updated_string += word + ' '
            updated_string = updated_string.strip()
        
        # case #2 - there is no year
        if len(articles) > 0 and has_year == False:
            for word in no_articles: 
                updated_string += word + ' '
            updated_string = updated_string.strip()
            updated_string += ', '
            for word in articles: 
                updated_string += word + ' '
            updated_string = updated_string.strip()
            
   
        if len(articles) > 0 and has_year == True:
            no_articles = no_articles[:-1]
            for word in no_articles: 
                updated_string += word + ' '
            updated_string = updated_string.strip()
            updated_string += ', '
            for word in articles: 
                updated_string += word + ' '
            updated_string += year
            updated_string = updated_string.strip()
        
        # if title == 'The American President':
        # checking if the updated_string is in the list... if there's an exact match
        if updated_string in valid_titles:
            index = valid_titles.index(updated_string)
            result.append(index)
            #continue
        
        # if there are several matches 
        for i in range(len(valid_titles_no_year)):
            curr_entry = valid_titles_no_year[i]
            if curr_entry == updated_string:
                result.append(i)
                
        return result


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
        
        negationWords = ['not', "didn't", 'didnt', 'barely', 'hardly', 'never', 'no', 'nothing']
        positiveWord = ['enjoyed']
        largeP = ['loved']
        largeN = ['hated', 'terrible', 'appalling', 'awful', 'dreadful', 'horrible', 'atrocious', 'horrendous']
        multiplyWords = ['really', 'truly', 'genuinely', 'very', 'undoubtedly', 'greatly']
        sentiment = {'pos' : 0, 'neg' : 0}
        expandedString = ""
        wordList = preprocessed_input.split()
        negation = False
        multiply = False
        
        for word in wordList:
            stemmedWord = self.p.stem(word)
            onlyAlpha = ''
            for ch in word:
                if ch.isalpha():
                    onlyAlpha += ch
            
            word = onlyAlpha
            if word in negationWords:
                negation = True
            
            if word in multiplyWords:
                multiply = True
                
            if word in largeP and negation == True:
                if multiply == True:
                    sentiment['neg'] += 2 * 2
                else:
                    sentiment['neg'] += 2
            
            elif word in largeP and negation == False:
                if multiply == True:
                    sentiment['pos'] += 2 * 2
                else:
                    sentiment['pos'] += 2
                    
            if word in largeN and negation == True:
                if multiply == True:
                    sentiment['pos'] += 2 * 2
                else:
                    sentiment['pos'] += 2
            
            elif word in largeN and negation == False:
                if multiply == True:
                    sentiment['neg'] += 2 * 2
                else:
                    sentiment['neg'] += 2      
                
            elif word in self.sentiment and negation == True:
                if multiply == True:
                    if self.sentiment[word] == 'pos':
                        sentiment['neg'] += 2 * 1
                    else:
                        sentiment['pos'] += 2 * 1
                else:
                    if self.sentiment[word] == 'pos':
                        sentiment['neg'] += 1
                    else:
                        sentiment['pos'] += 1
                    
            elif word in self.sentiment and negation == False:
                if multiply == True:
                    sentiment[self.sentiment[word]] += 2 * 1
                else:
                    sentiment[self.sentiment[word]] += 1
               
            elif stemmedWord in self.sentiment and negation == True:
                if multiply == True:
                    if self.sentiment[stemmedWord] == 'pos':
                        sentiment['neg'] += 2 * 1
                    else:
                        sentiment['pos'] += 2 * 1
                else:
                    if self.sentiment[stemmedWord] == 'pos':
                        sentiment['neg'] += 1
                    else:
                        sentiment['pos'] += 1
            
            elif stemmedWord in self.sentiment and negation == False:
                if multiply == True:
                    sentiment[self.sentiment[stemmedWord]] += 2 * 1
                else:
                    sentiment[self.sentiment[stemmedWord]] += 1
                    
            
            elif word in positiveWord and negation == False:
                if multiply == True:
                    sentiment['pos'] += 2 * 1
                else:
                    sentiment['pos'] += 1
                                
        if sentiment['pos'] > sentiment['neg']:
            dif = sentiment['pos'] - sentiment['neg']
            if dif >= 2:
                return 2
            else:
                return 1
        
        if sentiment['pos'] < sentiment['neg']:
            dif = sentiment['neg'] - sentiment['pos']
            if dif >= 2:
                return -2
            else:
                return -1
        
        if sentiment['pos'] == sentiment['neg']:
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
        if self.creative == True:
            distances = {}
            for index in range(len(self.titles)):
                title = title.lower()
                movieTitle = self.titles[index][0].lower()
                movieToken = movieTitle.split()

                for token in movieToken:
                    if token[0] == '(':
                        movieToken.remove(token)
                        
                onlyMovie = ' '.join(map(str,movieToken))
                onlyMovie = onlyMovie.lower()

                titleLen = len(title) + 1
                movieLen = len(onlyMovie) + 1
                levenshtein = np.zeros((titleLen, movieLen))

                for i in range(titleLen):
                    levenshtein[i, 0] = i

                for j in range(movieLen):
                    levenshtein[0, j] = j

                for i in range(1, titleLen):
                    for j in range(1, movieLen):
                        if title[i-1] == onlyMovie[j-1]:
                            levenshtein[i,j] = min(levenshtein[i-1, j] + 1, levenshtein[i-1, j-1], levenshtein[i, j-1] + 1)
                        else:
                            levenshtein[i,j] = min(levenshtein[i-1,j] + 1, levenshtein[i-1,j-1] + 2, levenshtein[i,j-1] + 1)

                distances[index] = (levenshtein[titleLen - 1, movieLen - 1])


            sort_orders = sorted(distances.items(), key=lambda x: x[1])
            recommendations = []

            i = 0
            distance = sort_orders[0][1]
            while sort_orders[i][1] == distance and distance <= max_distance:
                recommendations.append(sort_orders[i][0])
                i += 1

            return recommendations
        
        else:
            pass

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
        if self.creative == True:
            punctuations = '''!()-[]{};:"\,<>./?@#$%^&*_~'''
            movies = []
            for index in candidates:
                no_punct = ""
                titles = self.titles[index][0]
                for char in titles:
                    if char not in punctuations:
                        no_punct = no_punct + char

                titlesTokens = no_punct.split()
                clarificationTokens = clarification.split()
                clarificationLen = len(clarificationTokens)
                check = 0
                for token in clarificationTokens:
                    if token in titlesTokens:
                        check += 1

                if check == clarificationLen:
                    movies.append(index)

            return movies
        
        else:
            pass

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
        ratings = np.where((ratings <= threshold) & (ratings > .5), -1, ratings)
        ratings = np.where((ratings > threshold) & (ratings <= 5), 1, ratings)

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
        cosine_sim = np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))
        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return cosine_sim

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
        ratings = {}
        movies = len(user_ratings)
        unwatched = []
        watched = []
        for index in range(len(user_ratings)):
            if user_ratings[index] == 0:
                unwatched.append(index)
            else:
                watched.append(index)
                
        for movieA in unwatched:
            rating = 0
            for movieB in watched:
                if np.any(ratings_matrix[movieA]) and np.any(ratings_matrix[movieB]):
                    similarity = self.similarity(ratings_matrix[movieA], ratings_matrix[movieB])
                    userRating = user_ratings[movieB]
                    rating += (similarity * userRating)
                
            ratings[movieA] = rating
         
        for i in range(k):
            idx = max(ratings, key = ratings.get)
            recommendations.append(idx)
            ratings[idx] = -10

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
        return """Hi there! I’m a chatbot created by Jackson Domurad, Tycho Svoboda, Karina Li, and Matthew Yekell. I help generate movie recommendations for people. The way I work is, I’ll ask the user to give 5 movies that they liked or disliked in the format, 'I liked "The Notebook"' or 'I hated "Tron"'. From there, I start to get a sense of what kinds of movies a user does and doesn’t like, and can generate a recommendation - or several for that matter. So, after the user feeds me a few data points, I spit out recs! I also take the character of Homer Simpson when I’m live! Along with movie recs, I am able to spit out responses for arbitrary questions. These responses won't be helpful, but I can do it. \n"""


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
