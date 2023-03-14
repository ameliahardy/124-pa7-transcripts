# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util

import numpy as np
import re
import random
import math
from porter_stemmer import PorterStemmer


# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'Bot'

        self.creative = creative

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')
        self.user_ratings = np.zeros(len(self.titles))
        self.recommendations = []
        self.min_needed_inputs = 5
        self.user_inputs_processed = 0
        self.yes_words = ['yes', 'yea', 'y', 'ya', 'yer', 'ye', 'yeah', 'sure']
        self.no_words = ['nope', 'nah', 'no', 'n']
        self.negation_words = ['not', 'never', 'no', "didn't"]
        self.strong_positive_words = ['love', 'loved', 'exceptionally liked', 'really really liked', 'really liked', 
        'in love with', 'fantastic', 'magnificent', 'incredible', 'mind-blowing', 'amazing', 'fascinating', 'beautiful', 'great', 'beautiful']
        self.strong_negative_words = ['horrible', 'terrible', 'hate', 'hated', 'despise', 'despised', 'awful', 'sucks', 'horrible', 'horrendous', 'apalling']
        self.same_style_list = ['and', 'either', 'both', 'or']
        self.different_style_list = ['but']
        self.same_style = False
        self.different_style = False
        self.negation = False

        # positive sentiment
        self.positive_sentiment_responses = [
            "Im glad to hear you enjoyed ",
            "Its great to hear that you liked ",
            "Awesome! Glad you enjoyed watching ",
            "Yay! I love that you had a good time viewing ",
            "That's fantastic! Im glad you liked ",
            "That's wonderful! Its always great to hear positive feedback about "
        ]
        self.positive_sentiment_responses_british = [
            "I'm chuffed to bits that you enjoyed ",
            "Brilliant news, I'm delighted to hear you enjoyed ",
            "Top notch, glad you fancy ",
            "Jolly good, I'm so pleased you appreciate " ,
            "Marvelous, quite rare to come across a film such a masterclass as ",
            "Fantastic, gather your mates next time you watch "
        ]

        #negative sentiment
        self.negative_sentiment_responses = [
            "I'm sorry to hear that you didn't like watching ",
            "Oh no! Sorry you didn't enjoy ",
            "Thats unfortunate. You didn't like ",
            "I understand. Very sorry you did not have a good time watching ",
            "That's too bad. I was hoping you would enjoy "
        ]
        self.negative_sentiment_responses_british = [
            "Ah, I see. It's a shame that you didn't care for ",
            "Well, you can't love them all! Too bad you didn't like ",
            "That's a shame, old chap. Sorry you didn't appreciate ",
            "Unfortunate to hear, old bean. Too bad you hated ",
            "Well, that's a pity. Unfortunate you didn't like ",
            "Terribly sorry to hear you didn't enjoy "
        ]

        #neutral sentiment
        self.neutral_sentiment_responses = [
            "Fair enough, you didnt feel strongly about this one.",
            "Got it, this movie didnt stand out either way to you.",
            "Alright, so you feel neutral about this one.",
            "I can see that you have a mixed reaction.",
            "Thanks for letting me know your thoughts on this one.",
            "Your feedback is appreciated. It seems like you had a neutral experience. " 
        ]
        self.neutral_sentiment_responses_british = [
            "I'm terribly sorry, old chap, but I'm a bit confused. Might you be so kind as to provide a bit more information about ?",
            "Would you mind terribly elaborating on that a bit more? I want to make sure I'm following what your thoughts are on ",
            "I'm afraid I'm not quite getting you. Could you please clarify, my good fellow, on the criticisms of ",
            "Mate, can you clarify what your views are on ",
            "M'lad Im a touch confused, what did you think about "
        ]

        #Clarification
        self.clarification_responses = [
            "I'm a bit confused. Can you please explain that in more detail?",
            "Can you elaborate on that a bit more? I want to make sure I understand what you're saying.",
            "I'm not sure I follow. Could you please clarify?",
            "Can you please clarify what you mean?",
            "Can you help me understand what you mean please."
        ]
        self.clarifcation_responses_british = [
            "I'm terribly sorry, old chap, but I'm a bit confused. Might you be so kind as to assist me in which of the movies suit your query?",
            "Would you mind terribly elaborating on that a bit more? Which film matches your request?",
            "I'm afraid I'm not quite getting you. Could you please clarify?",
            "Mate, can you clarify which of these productions suit your search?"
        ]

        self.british_disambig_phrases =  [
            "Oy mate, I gathered these films from your request ",
            "Would you mind terribly elaborating on that a bit more? Which film matches your request:",
            "Terribly sorry, I couldn't quite get down to a particular film from your request. Here's what I could muster:"
        ]
        
        self.confirm_phrases = [
            "Oy Mate, can you confirm if you meant ",
            "Good lad, were you meaning to say ",
            "Good, are you talking about ",
            "Mate, were you trying to refer to"
        ]

        self.suggest_phrases = [
            "I recommend this for you lad: ",
            "Thanks mate, here's what I suggest: ",
            "You should check out "
        ]

        self.thanks_for_feedback_phrases = [
            "Thanks for telling me about what you thought!",
            "Appreciate you thoughts mate!",
            "Thanks for letting me know good sir!"
        ]

        self.did_not_find_phrases = [
            "Sorry, I didn't find any movies matching ",
            "Mate I didn't find ",
            "Unfortunately, I wasn't able to pin down ",
            "I was unable to locate "
        ]
        
        self.make_recommendation = [
            "With your help, I have enough information to make a recommendation. Would like to hear one?\n",
            "Do you want a recommendation now?\n",
            "How about I make a recommendation, do you want one?\n"
        ]

        self.could_not_understand = [
            "Sorry, I'm not sure if I understand what you're to say.\n",
            "Let's skip the banter, I don't quite follow!\n",
            "Oh my days, I'm a little lost, my friend!\n",
            "Sorry chap, do you have any thoughts on some movies?\n"
        ]

        self.ask_for_movies = [
            "Give me another movie mate.\n",
            "Oy, keep fancying me, pal! What else have you seen?\n",
            "Hit me with another one that's your cup of tea\n",
            "Good work lad, give me another movie you like\n"
        ]
    
        self.found_movie_index = {}


        ########################################################################
        # TODO: Binarize the movie ratings matrix.                             #
        ########################################################################      
        # Binarize the movie ratings before storing the binarized matrix.
        ratings = self.binarize(ratings, threshold=2.5)
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
        if self.creative:
            greeting_message = "Jolly good day! I'm Arnold, your personal movie bot! Whatcha fancy on the telly?"
        else:
            greeting_message = "Hi! I'm MovieBot! Here to help! Tell me about some movies you've seen or would like to see."

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
            goodbye_message = "Fancy chat! Cheers, old chap."
        else:
            goodbye_message = "Have a good one. Hope to see you soon!"

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
        response = ""

        preprocessed_input = self.preprocess(line)
        titles = self.extract_titles(preprocessed_input)
        titles = list(set(titles))
        self.found_movie_index = {}
        # didn't find any
        if len(titles) == 0:
            return self.arb_and_emotion(preprocessed_input, '')
        # found too many movies, need to clarify down
        if len(titles) > 1:
            for title in titles:  # go through each given title
                self.found_movie_index[title] = self.find_movies_by_title(title)
                if len(self.found_movie_index[title]) == 0:  # no exact match found, need to use closest to function
                    spell_check_options = self.find_movies_closest_to_title(title)
                    # found spell-checking options
                    if len(spell_check_options) > 0:       
                        loop = True     
                        while loop:
                            question = random.choice(self.confirm_phrases) + self.titles[spell_check_options[0]][0] + "?\n"
                            confirm = self.bot_input(question)
                            if confirm.lower() in self.yes_words:  # if user confirmed store
                                self.found_movie_index[title] = spell_check_options
                                loop = False
                            elif confirm.lower() in self.no_words:
                                response += random.choice(self.did_not_find_phrases) + title
                                loop = False
                            else:
                                response += self.arb_and_emotion(preprocessed_input, title)
                                response += random.choice(self.confirm_phrases) + self.titles[spell_check_options[0]][0]

                    else:
                        # no matches through spell check
                        return self.arb_and_emotion(preprocessed_input, title)
                elif len(self.found_movie_index[title]) == 1:
                   pass
                else:  # found multiple options, need to clarify
                    #DISAMBIG
                    question = random.choice(self.british_disambig_phrases) + title + ":\n"
                    for idx in self.found_movie_index[title]:
                        question += self.titles[idx][0] + '\n'
                    question += random.choice(self.clarifcation_responses_british) + "\n"
                    clarification = self.bot_input(question)
                    disambig = self.disambiguate(clarification, self.found_movie_index[title])
                    while len(disambig) != 1:
                        clarification = self.bot_input(question)
                        disambig = self.disambiguate(clarification, self.found_movie_index[title])
                    # disambig should hold one index now
                    self.found_movie_index[title] = disambig

        elif len(titles) == 1:  # only given one title
            title = titles[0]
            potential_matches = self.find_movies_by_title(title)

            if len(potential_matches) == 0:
                spell_check_options = self.find_movies_closest_to_title(title)
                if len(spell_check_options) > 0:       
                    loop = True     
                    while loop:
                        question = random.choice(self.confirm_phrases) + self.titles[spell_check_options[0]][0] + '?\n'
                        confirm = self.bot_input(question)
                        if confirm.lower() in self.yes_words:  # if user confirmed store
                            self.found_movie_index[title] = spell_check_options
                            loop = False
                        elif confirm.lower() in self.no_words:
                            response += random.choice(self.did_not_find_phrases) + title
                            loop = False
                        else:
                            response += self.arb_and_emotion(preprocessed_input, title)
                            response += random.choice(self.confirm_phrases) + self.titles[spell_check_options[0]][0]
                else:
                    return random.choice(self.did_not_find_phrases) + title
            elif len(potential_matches) == 1:  # found exact match
                self.found_movie_index[title] = self.find_movies_by_title(title)              
            else:  # found multiple options, need to clarify
                # DISAMBIG
                question = random.choice(self.british_disambig_phrases) + title + ":\n"
                self.found_movie_index[title] = potential_matches
                for idx in self.found_movie_index[title]:
                    question += self.titles[idx][0] + '\n'
             
                question += random.choice(self.clarifcation_responses_british) + "\n"
                clarification = self.bot_input(question)
                disambig = self.disambiguate(clarification, self.found_movie_index[title])
                while len(disambig) != 1:
                    clarification = self.bot_input(question)
                    disambig = self.disambiguate(clarification, self.found_movie_index[title])
                # disambig should hold one index now
                self.found_movie_index[title] = disambig
        # plug in correct movie names into preprocessed_input
        for movie in self.found_movie_index.keys():
            idx = self.found_movie_index[movie][0]
            movie_title = self.titles[idx][0]
            processed_input = preprocessed_input.replace(movie, self.filter_out_movie_year(movie_title))
     
        # at this point, we have a dictionary in self.found_movie_index which each input and movie index
        # now we have to get sentiments
        if len(self.found_movie_index) > 1:
            sentiments = self.extract_sentiment_for_movies(preprocessed_input)
            # sentiments = tuples of (movie, sentiment rating)    
            for sentiment in sentiments:
                rating = sentiment[1]
                title = sentiment[0]
                while rating == 0: # keep asking until receive non-neutral sentiment
                    question = random.choice(self.neutral_sentiment_responses_british) + sentiment[0] + "?\n"
                    answer = self.bot_input(question)
                    if answer.lower() in self.no_words:
                        break
                    rating = self.extract_sentiment(answer)
                if rating >= 1:
                    response += random.choice(self.positive_sentiment_responses_british) + sentiment[0] + (".\n")
                elif rating <= 1:
                    response += random.choice(self.negative_sentiment_responses_british) + sentiment[0] + (".\n")

                self.user_inputs_processed += 1
                for index_lst in self.found_movie_index.values():
                    index = index_lst[0]
                    if self.filter_out_movie_year(self.titles[index][0]) == self.filter_out_movie_year(sentiment[0]):
                        self.user_ratings[index] = rating
                        break
        elif len(self.found_movie_index) == 1: # only analyze sentiment for one movie
            real_title = self.titles[self.found_movie_index[title][0]][0]
            rating = self.extract_sentiment(preprocessed_input)
            while rating == 0: # keep asking until receive non-neutral sentiment
                question = random.choice(self.neutral_sentiment_responses_british) + real_title + "?\n"
                answer = self.bot_input(question)
                if answer.lower() in self.no_words:
                    break
                rating = self.extract_sentiment(answer)
            if rating >= 1:
                response += random.choice(self.positive_sentiment_responses_british) + real_title + (".\n")
            elif rating <= 1:
                response += random.choice(self.negative_sentiment_responses_british) + real_title + (".\n")
            self.user_inputs_processed += 1
            self.user_ratings[self.found_movie_index[title][0]] = rating

        # now we have to reccomend
        if self.user_inputs_processed >= self.min_needed_inputs:  
            loop = True
            while loop:
                question = random.choice(self.make_recommendation)
                answer = self.bot_input(question)
                if answer.lower() in self.yes_words:
                    # give rec 
                    self.recommendations = self.recommend(self.user_ratings, self.ratings)
                    print(random.choice(self.suggest_phrases) + self.titles[random.choice(self.recommendations)][0] + ".\n")
                elif answer.lower() in self.no_words:
                    response += random.choice(self.thanks_for_feedback_phrases)
                    loop = False
                else:
                    print(self.arb_and_emotion(preprocessed_input, ''))
        
        self.found_movie_index = {}
        return response #+ random.choice(self.ask_for_movies)


    @staticmethod
    def preprocess(text):
        """Do any general-purpose pre-processing before extracting information
        from a line of text.python repl.py --creative < testing/test_scripts/simple.txt

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
        if text[len(text) - 1] in {',', '.', '?','!'}:
            text = text[:-1]
        ########################################################################
        #                             END OF YOUR CODE                         #
        ########################################################################

        return text
    
    def bot_input(self, question):
        answer = input(question)
        if answer == ':quit':
            quit()
        return answer
    
    def create_emotion(self):
        my_dict = {}
        my_dict["I am feeling"] = 13
        my_dict["I am"] = 5
        my_dict["I feel"] = 7
        my_dict["I'm"] = 4
        return my_dict
    
    def recognize_emotion(self, input_line):
        my_dict = self.create_emotion()
        words = input_line.split()
        emotion = ''
        for key in my_dict:
          key_words = key.split()
          last = key_words[len(key_words) - 1]
          if last in words:
            index = words.index(key_words[-1])
            if index + 1 < len(words) and index != -1:
                emotion = words[index + 1]
            else:
                emotion = ''
        if emotion in self.sentiment:
            if self.sentiment[emotion] == 'pos':
                return "Jolly! I'm glad to hear that you are " + ' ' + emotion
            elif self.sentiment[emotion] == 'neg':
                return "Oh no, chap! I'm sorry to hear that you are " + '' + emotion

        return ''
    
    
    def arb_and_emotion(self, preprocessed_input, title):
        emotion = self.recognize_emotion(preprocessed_input)
        q_word = self.arbitrary_catch(preprocessed_input)
        if (emotion != ''):
            return emotion
        elif (q_word != ''):
            return q_word
        else: 
            return "Sorry chap, I couldn't find the movie " + title
    
    def arbitrary_catch(self, preprocessed_input):
        if preprocessed_input.find("Can you") != -1 or preprocessed_input.find("What is") != -1:
            return "You asked" + "' " + preprocessed_input + " ' " + "." + " " + "I can't help with that. Could we go back to movies?"
        return ""     


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

        if self.creative == True:
            movie_pattern = '"(.*?)"'
            movies = re.findall(movie_pattern, preprocessed_input)
            if len(movies) == 0:
                movies += self.extract_titles_complex(preprocessed_input)
            return movies
        else:
            movie_pattern = '"(.*?)"'
            movies = re.findall(movie_pattern, preprocessed_input)
            return movies
        
    def filter_out_movie_year(self, movie):
        """
        Takes in a movie in the form like "Titanic (1997)
        Return in form: 'Titanic'
        """
        year_pattern = '([0-9]{4})'
        year = re.findall(year_pattern, movie)
        if len(year) == 0:
            return movie
        year_start_idx = movie.find(year[0])
        return movie[:year_start_idx - 2] + movie[year_start_idx + 6:]
            

    def extract_titles_complex(self, preprocessed_input):
            # Split input into lowercase words
        words = preprocessed_input.lower().split()

        # Find potential titles by combining words
        potential_titles = set()
        for i in range(len(words)):
            for j in range(i, len(words)):
                title = ' '.join(words[i:j+1])
                if self.find_movies_by_title(title):
                    potential_titles.add(title)

        # Extract contained titles from dataset
        contained_titles = set()
        for title_entry in self.titles:
            title = title_entry[0].lower()

            # Re-format title by removing article and year
            article_match = re.match('.*(, The|, An|, A)', title)
            if article_match:
                article = article_match.group(1)
                title = title.replace(article, '').strip() + f' {article.strip()}'

            title = re.sub('\(\d{4}\)', '', title).strip()

            # Check if title is in potential titles
            if title in potential_titles:
                contained_titles.add(title)
        

        return list(contained_titles)


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
        #CHANGE but works
        
        formatted = title.title()
        year = re.match('.*(\(\d{4}\)).*', title)
        if year != None:
            year_index = title.find(year.group(1))
        article = re.match('^(A |An |The ).*', formatted)
        if article != None and year == None:
            formatted = title[len(article.group(1)):] + ", " + article.group(1)[:-1]
        elif article != None and year != None:
            formatted = title[
                        len(article.group(1)):(year_index - 1)] + ", " + article.group(
                1) + year.group(1)

        formatted_title = formatted.lower()
        res = []
        for i in range(len(self.titles)):
                title = self.titles[i][0].lower()
                if (formatted_title == title) or (formatted_title + " (" in title):
                    res.append(i)
        return res


    def extract_sentiment(self, preprocessed_input):
        """Extract a sentiment rating from a line of pre-processed text.

        You should return -1 if the sentiment of the text is negative, 0 if the
        sentiment of the text is neutral (no sentiment detected), or +1 if the
        sentiment of the text is positive.

        As an optional creative extension, return -2 if the sentiment of the
        text is super negative and +2 if the sentiment of the text is super
        positive.

        Example:
          sentiment = chatbot.extract_sentiment(chatbot.preprocess('I liked "The Titanic"'))
          print(sentiment) // prints 1

        :param preprocessed_input: a user-supplied line of text that has been
        pre-processed with preprocess()
        :returns: a numerical value for the sentiment of the text
        """
        base = 0
        split_preprocessed = preprocessed_input.split()

        negation = False
        for word in split_preprocessed:
            if word in self.sentiment:
                if negation:
                    if self.sentiment[word] == 'pos':
                        base -= 1
                    else:
                        base += 1
                    negation = False
                else:
                    if self.sentiment[word] == 'pos':
                        base += 1
                    else:
                        base -= 1
            else:
                p = PorterStemmer()
                w = p.stem(word)
                if word == "enjoyed":
                    w = "enjoy"
                if w in self.sentiment:
                    if negation:
                        if self.sentiment[w] == 'pos':
                            base -= 1
                        else:
                            base += 1
                        negation = False
                    else:
                        if self.sentiment[w] == 'pos':
                            base += 1
                        else:
                            base -= 1
                elif word in ['not', 'never', 'no', "didn't"]:
                    negation = True

        result = 0
        if base > 0:
            result = 1
        elif base == 0:
            result = 0
        else:
            result = -1
        return result
    
   
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
        movies = self.extract_titles(preprocessed_input)
        sentiment = []
        sentence = preprocessed_input
        len_mov = len(movies)
        for i in range(len_mov):
            start = 0
            title = movies[i]
            if i > 0:
                prev = movies[i - 1]
                start = sentence.find(prev) + len(prev) + 1
            end = sentence.find(title)

            movie_sentiment = self.extract_sentiment(sentence[start : end])
            if movie_sentiment == 0 and i == len(movies) - 1:
                end = len(sentence)
                movie_sentiment = self.extract_sentiment(sentence[start : end])
            if movie_sentiment == 0 and i > 0:
                movie_sentiment = sentiment[i - 1][1]
            if 'but' in sentence[start : end].lower().split() or 'however' in sentence[start : end].lower().split():
                movie_sentiment = sentiment[i - 1][1] * -1

            sentiment.append((title, movie_sentiment))
        return sentiment

    
    def edit_distance(self, s1, s2):
            v = len(s1)
            w = len(s2)
            dp = [[0] * (w+1) for _ in range(v+1)]
            for i in range(1, v + 1):
                dp[i][0] = i
            for j in range(1, w + 1):
                dp[0][j] = j
            for i in range(1, v + 1):
                for j in range(1, w + 1):
                    if s1[i-1] == s2[j-1]:
                        dp[i][j] = dp[i-1][j-1]
                    else:
                        dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
            return dp[v][w]

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

        def edit_distance(s1, s2):
            if len(s1) < len(s2):
                return edit_distance(s2, s1)
            if len(s2) == 0:
                return len(s1)
            prev_row = range(len(s2) + 1)
            for i, c1 in enumerate(s1):
                curr_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = prev_row[j + 1] + 1
                    deletions = curr_row[j] + 1
                    substitutions = prev_row[j] + (c1 != c2)
                    curr_row.append(min(insertions, deletions, substitutions))
                prev_row = curr_row
            return prev_row[-1]
        
        titles = [(i, t) for i, t in enumerate(self.titles)]
        
        distances = [(i, t, edit_distance(title.lower(), self.filter_out_movie_year(t[0]).lower())) for i, t in titles]
    
        closest = [i for i, t, d in distances if d <= max_distance]

        if not closest:
            return []
        min_distance = min(d for i, t, d in distances)
        closest = [i for i, t, d in distances if d == min_distance]
  
        return closest
    def extractYear(self, title):
        """
        Extracts the year from a movie title string.

        Args:
            title (str): the movie title string

        Returns:
            (int): the year of the movie
        """
        pattern = r"\(([0-9]{4})\)"
        match = re.search(pattern, title)
        if match:
            return int(match.group(1))
        else:
            return None


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
        narrowed_list = []


        if clarification.lower() == ['the first one', 'first', '1']:
            narrowed_list.append(candidates[0])
        elif clarification.lower() in ['the second one', 'second', '2']:
            narrowed_list.append(candidates[1])
        elif clarification.lower() in ['the last one', 'last', 'final']:
            narrowed_list.append(candidates[-1])

        for movie_idx in candidates:
            movie_title = self.titles[movie_idx][0]
            movie_title_lower = movie_title.lower()
            if len(clarification.split()) == 1:
                movie_title_lower = self.tokenizeTitle(movie_title_lower)
            if clarification.lower() in movie_title_lower:
                narrowed_list.append(movie_idx)
            if movie_title_lower == clarification.lower():
                narrowed_list.append(movie_idx)

        # If only one movie remains in the narrowed list, return it
        if len(narrowed_list) == 1:
            return narrowed_list
        
        if clarification.isdigit():
            if (int(clarification) > 0 and int(clarification) < len(candidates)):
                return [candidates[int(clarification)-1]]

        # Otherwise, try to disambiguate further using year information
        year = self.extractYear(clarification)
        if year:
            narrowed_list = [idx for idx in narrowed_list if str(year) in self.titles[idx][0]]
        if len(narrowed_list) == 1:
            return narrowed_list

        return narrowed_list
    
    def tokenizeTitle(self, title):
        tokens = title.split()
        new_toks = []
        for tok in tokens:
            if (tok[0] == '(' and tok[len(tok) - 1] == ')'):
                tok = tok[1:len(tok) - 1]
            new_toks.append(tok)
        return new_toks

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
        for j in range(len(ratings[0])):
            for i in range(len(ratings)):
                if ratings[i][j] == 0:
                    ratings[i][j] = 0
                elif ratings[i][j] > threshold:
                    ratings[i][j] = 1
                else:
                    ratings[i][j] = -1
        # The starter code returns a new matrix shaped like ratings but full of
        # zeros.
        binarized_ratings = ratings

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
        similarity = 0
        dot_product = np.dot(u, v)
        u_magnitude = np.linalg.norm(u)
        v_magnitude = np.linalg.norm(v)
        if (u_magnitude == 0 or v_magnitude == 0):
            return 0
        similarity = dot_product / (u_magnitude * v_magnitude)
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
        recommendations = []
        recIndex = []
        rating = 0
        for i in range(ratings_matrix.shape[0]):
            if (user_ratings[i] == 0):
                for j in range(len(user_ratings)): 
                    if (user_ratings[j] != 0):
                        rating += user_ratings[j] * self.similarity(ratings_matrix[i], ratings_matrix[j])
                recIndex.append((rating, i))
                rating = 0
        newRecommendations = sorted(recIndex, reverse=True)
        for i in range(k):
            first = newRecommendations[i]
            recommendations.append(first[1])
        
       
        
       
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
        intro = "Ladies and gentlemen, may I introduce you to our humble chatbot that specializes in the art of recommending the finest cinematic productions. Hailing from the land of afternoon tea, rainy days, and well-mannered conversations, this chatbot possesses a refined taste in movies that is sure to impress even the most discerning of movie-goers. With its vast knowledge of British and international cinema, it stands ready to assist you in finding the perfect movie for any occasion. So sit back, relax, and let our dear chatbot guide you through the wonderful world of movies. Cheers!"
        return intro 
        """
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
