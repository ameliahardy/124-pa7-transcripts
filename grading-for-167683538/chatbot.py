# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util
import re
import numpy as np
import porter_stemmer


# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'MovieGenie'

        self.creative = creative
        
        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')

        self.user_ratings_count = 0
        self.user_ratings = np.zeros(len(ratings))
        self.recommendations = []
        self.potential_movies = []
        self.potential_line = ''
        self.clean_title = False

        self.p = porter_stemmer.PorterStemmer()
        self.stemmed_sentiment = {}
        for k, v in self.sentiment.items():
            k = self.p.stem(k)
            self.stemmed_sentiment[k] = v
       
        self.negation = ['didn\'t', 'don\'t', 'not', 'never']
        self.punctuation = [',', '?', '!', '.', ';', ':']
        self.strong_pos = ['love', 'loved', 'incredible', 'amazing', 'astounding', 'inspiring', 'extraordinary', 'fabulous', 'prodigious', 'fantastic', 'phenomenal']
        self.strong_pos_stemmed = ['love', 'incred', 'amaz', 'astound', 'inspir', 'extraordinari', 'fabul', 'prodigi', 'fantast', 'phenomen']
        self.strong_neg = ['hate', 'hated', 'terrible', 'detest', 'despise', 'loathe', 'resent', 'appalling', 'appalled', 'atrocious', 'horrendous']
        self.strong_neg_stemmed = ['hate', 'terribl', 'detest', 'despis', 'loath', 'resent', 'appal', 'atroci', 'horrend']
        self.intensity = ['really', 'reeally', 'very', 'extremely', 'absolutely', 'exceptionally', 'remarkably', 'severely', 'excessively', 'truly', 'undoubtedly', 'alot']

        ########################################################################
        # TODO: Binarize the movie ratings matrix.                             #
        ########################################################################
        ratings = Chatbot.binarize(ratings)
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
        # TODO: Write a short greeting message                                 #
        ########################################################################

        greeting_message = "Hello! I am MovieGenie, a bot that makes movie recommendations. First I will ask you about your taste in movies. Tell me about a movie that you have seen and whether you liked it."
        if self.creative:
            greeting_message = "Howdy! My name's MovieGenie, a bot that suggests movies. I reckon I should ask you about your movie tastes. Come on, honey, tell me bout a movie you've seen and whether not you had a grand ol time watchin it."
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

        goodbye_message = "Thank you for your time. Have a nice day!"
        if self.creative:
            goodbye_message = "Alright, sugarplum! Take care now!"

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
        if self.creative:
            can_you = re.search(r"[Cc][Aa][Nn] [Yy][Oo][Uu] ([\w]+[?])", line)
            what_is = re.search(r"[Ww][Hh][Aa][Tt] [Ii][Ss] ([\w]+[?])", line)
            how_is = re.search(r"[Hh][Oo][Ww] [Ii][Ss] ([\w]+[?])", line)
            why_is = re.search(r"[Ww][Hh][Yy] [Ii][Ss] ([\w]+[?])", line)
            are_you = re.search(r"[Aa][Rr][Ee] [Yy][Oo][Uu] ([\w]+[?])", line)
            i_am = re.search(r"[Ii] am |[Ii]'m ", line)
            if can_you:
                responses = ["I can sure {}! Matter fact, I can do anythin! Just kiddin, since I'm just a chatbot.".format(can_you.group(1).replace('?', '')), 
                            "Hmmmm, I don't reckon if I can {}.".format(can_you.group(1).replace('?', '')),
                            "Maybe... can I {}?".format(can_you.group(1).replace('?', ''))]
                return np.random.choice(responses)
            elif what_is:
                responses = ["I don't reckon I know what {} is. Maybe ask someone else bout that.".format(what_is.group(1).replace('?', '')),
                            "I ain't sure what {} is. You reckon you can tell me?".format(what_is.group(1).replace('?', '')),
                            "Is that movie related? Alrighty then, ask me for movie recommendations!"]
                return np.random.choice(responses)
            elif how_is:
                responses = ["I ain't sure how {} is. Let's go back to talkin bout movie recommendations!".format(how_is.group(1).replace('?', '')),
                            "I ain't sure how {} is. Reckon you can tell me?".format(how_is.group(1).replace('?', '')),
                            "Mighty fine question! But I ain't sure I can answer how {} is.".format(how_is.group(1).replace('?', '')),
                            "Hmmmm... thata a tricky one. I don't reckon I know how {} is.".format(how_is.group(1).replace('?', ''))]
                return np.random.choice(responses)
            elif why_is:
                responses = ["I ain't sure why {}. Though I would also love to know why!".format(why_is.group(1).replace('?', '')),
                            "I also wonder why {}. 'S time to investigate".format(why_is.group(1).replace('?', '')),
                            "What an interestin question to ask why {}. I ain't sure.".format(why_is.group(1).replace('?', '')),
                            "I ain't sure, but did you know that I can recommend movies?".format(why_is.group(1).replace('?', ''))]
                return np.random.choice(responses)
            elif are_you:
                responses = ["I ain't sure if I am {}! I am a chatbot. I am not a human.".format(are_you.group(1).replace('?', '')),
                            "Maybe I am {}...Maybe I am not.".format(are_you.group(1).replace('?', '')),
                            "I am a chat bot".format(are_you.group(1).replace('?', ''))]
                return np.random.choice(responses)
            elif i_am:
                responses = ["Got it!", "Sugar, that ain't really what I had in mind. Let's go back to movies.", "Hmm, I ain't sure if I'm followin, but alright!", "Ain't that wild!", "Honeyplum, that's crazy."]
                return np.random.choice(responses)
        ah_words = np.array(['Ah. ', 'I see. ', 'I understand. ', 'Ah ha. ', 'Right. ', 'Got it. ', 'Alright. '])
        like_words = np.array(['liked ', 'enjoyed ', 'had fun watching ', 'were pleased with ', 'were delighted with ', 'appreciated '])
        dislike_words = np.array(["didn't like ", "didn't enjoy ", 'did not have fun watching ', 'were not pleased with ', 'disliked ', 'did not appreciate ', 'were not delighted with '])
        suggest_words = np.array(['I suggest you watch ', 'You should watch ', 'You will enjoy ', 'You will like ', 'You will have fun watching ', 'You will be pleased with '])
        retry_words = np.array(["I'm sorry, I do not understand your response. Please tell me about a movie you have seen.", "Sorry, I don't think I understood your response. Please tell me about a movie you've recently watched.", "It seems that I cannot understand what you mean. Please tell me about what movies you liked or disliked."])
        goodbye_words = np.array(['Okay. I hope you had fun!', 'Ok, I hope you enjoyed my suggestions!', 'Got it. I hope I was helpful today.', 'OK, thank you for your time!'])
        unsure_words = np.array(["I'm not sure if you ", "Hmm, I can't tell if you ", "I'm sorry, I don't know if you "])
        tell_me_more_words = np.array(["Please tell me about another movie you have watched.", "Tell me about another movie.", "What about another movie?", "I want to hear more! Please tell me about another movie you have seen."])
        multiple_different_movies_words = np.array(["Please tell me about one movie at a time. Go ahead.", "Please only mention one movie.", "I can only understand one movie at a time. Please answer again.", "One movie at a time please!"])
        multiple_same_movies_words = np.array(["I found more than one movie with the title ", "There is more than one movie with the title ", "There are multiple movies with the title "])
        nothing_found_words = np.array(["I'm sorry, I don't recognize ", "Sorry, I don't know about ", "I apologize. I have never heard of ", "I don't think I know "])
        creative_multiple_same_movies_words = ['Which one do you mean? ', 'Which of these do you mean? ', 'Which movie do you mean? ', 'Pick one out of this list, please: ']
        if self.creative:
            ah_words = np.array(['Ah. ', 'Sure thing, sugar. ', 'I reckon thats right. ', 'Uh-huh. ', 'Indeed-y. ', 'Gotcha. ', 'Alrighty. '])
            like_words = np.array(['were dancin like a junebug when watchin ', 'were grinnin like a possum at ', 'had a grand ol time watchin ', 'were pleased as a peach with ', 'were downright delighted with ', 'would give some sugar to '])
            dislike_words = np.array(["were prayin for God to turn off ", "needed a Come to Jesus meetin after watching ", 'were fixin to turn off ', 'thought there was a cattywampus flavor to ', 'were hollerin at the TV to hush up during ', 'were screaming Goodness Gracious durin ', 'had a dying duck fit during '])
            suggest_words = np.array(['I reckon you should watch ', 'Heavens to Betsy, you should watch ', 'Im fixin to suggest ', 'Golly, you would love ', 'Your pickle would be dilled by ', 'If you arent busy as a cat on a hot tin roof, you should watch '])
            retry_words = np.array(["Sorry, sugar, I don't understand. Why dontcha tell me bout a movie you've seen.", "Hold your horses there -- I don't quite understand. Please tell me a lil bit about a movie you've recently watched.", "Bless your heart, but I don't know what you mean. Please tell me about what movies you liked or disliked."])
            goodbye_words = np.array(['Alrighty then. Holler if you need me!', 'Ok, lets swap spit and hit the road!', 'Got it. Yall come back now, hear?', 'Alright, toodoloo!'])
            unsure_words = np.array(["I reckon I can't tell if you ", "Bless your heart, but I can't tell if you ", "I'm fixin to understand -- I can't tell if you "])
            tell_me_more_words = np.array(["Aren't you precious? Why don't you tell me about another movie you have watched.", "Well, I declare you ought ta tell me about another movie.", "How's about another movie?", "Golly, tell me more! Heavens know I'd love to hear about another movie you have seen."])
            multiple_different_movies_words = np.array(["Hold your horses, one movie at a time!", "Hush up for a moment -- please, just one movie at a time.", "Well aren't you eager as a choir boy on Sunday morning? Just one movie at a time, dear.", "Oh, you think I'm some highfalutin' chatbot? I can only handle one movie at a time -- please answer again!"])
            multiple_same_movies_words = np.array(["Looks like we have our pickings of movies with the title ", "Well I'll be, I found multiple movies with the title ", "Well ain't that a doosy? There's multiple movies with the title "])
            nothing_found_words = np.array(["Bless your heart, but I never heard of ", "Hmmm... I reckon I never heard of ", "That's awfully cattywampus... I've never heard of ", "Well, I declare I've never heard of "])
            creative_multiple_same_movies_words = ['You have your pickings: which one do you mean? ', 'I reckon you outta pick one of these movies: ', 'Which movie do you mean, sugar? ', 'It would really butter my biscuit if you could pick one of the following: ']
        response = ""
        preprocessed = self.recognize_input(line)
        if preprocessed[0] == '':
            response = np.random.choice(retry_words)
        elif preprocessed[0] == 'nothing found':
            if self.creative:
                response = np.random.choice(nothing_found_words) + '"' + preprocessed[1] + '"' + '.' + ' Try again, will ya?'
            else:
                response = np.random.choice(nothing_found_words) + '"' + preprocessed[1] + '"' + '.' + ' Please try again.'
        elif preprocessed[0] == 'multiple different movies':
            response = np.random.choice(multiple_different_movies_words)
        elif preprocessed[0] == 'multiple same movies':
            if self.creative:
                response = np.random.choice(multiple_same_movies_words) + '"' + preprocessed[1] + '"' + '.' + ' Clarify for me, good fella.'
            else:
                response = np.random.choice(multiple_same_movies_words) + '"' + preprocessed[1] + '"' + '.' + ' Please clarify.'
        elif preprocessed[0] == 'creative-multiple same movies':
            response = np.random.choice(creative_multiple_same_movies_words) + str([self.titles[preprocessed[1][i]][0] for i in range(len(preprocessed[1]))])
        elif preprocessed[0] == 'pick in potential' or preprocessed[0] == 'pick one in potential':
            if self.creative:
                response = 'Go ahead and pick one for me, wontcha?: ' + str([self.titles[i][0] for i in self.potential_movies])
            else:
                response = 'Please pick one movie in the list of potential matches: ' + str([self.titles[i][0] for i in self.potential_movies])
        elif preprocessed[0] == 'not sure':
            response = np.random.choice(unsure_words) + np.random.choice(like_words) + '"' + self.titles[preprocessed[1]][0] + '"' + '.'
            response += "\nTell me more about " + '"' + self.titles[preprocessed[1]][0] + '"' + '.'
        elif preprocessed[0] == 'confirm':
            if preprocessed[1] == 'yes':
                response = np.random.choice(suggest_words) + '"' + self.titles[self.recommendations.pop(0)][0] + '"' + '.'
                if self.creative:
                    response += "\n" + "You want nother, darling? (if not, enterin :quit will do!)"
                else:
                    response += "\n" + "Would you like another recommendation? (Or enter :quit if you're done.)"
            else:
                response = np.random.choice(goodbye_words) + ' Please enter :quit to finish.'
        else:
            self.user_ratings[preprocessed[1]] = preprocessed[2]
            self.user_ratings_count += 1
            if preprocessed[2] >= 1:
                response = np.random.choice(ah_words) + 'You ' + np.random.choice(like_words) + '"' + self.titles[preprocessed[1]][0] + '"' + '!'
            if preprocessed[2] <= -1:
                response = np.random.choice(ah_words) + 'You ' + np.random.choice(dislike_words) + '"' + self.titles[preprocessed[1]][0] + '"' + '.'
            if self.user_ratings_count >= 5:
                response += "\nThat's enough for me to make a recommendation."
                self.recommendations = self.recommend(self.user_ratings, self.ratings, len(self.ratings))
                response += "\n" + np.random.choice(suggest_words) + '"' + self.titles[self.recommendations.pop(0)][0] + '"' + '.'
                response += "\n" + "Would you like another recommendation? (Or enter :quit if you're done.)"
            else:
                response += "\n" + np.random.choice(tell_me_more_words)
        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return response

    def recognize_input(self, line):
        if self.creative and len(self.potential_movies) > 0:
            if len(self.disambiguate(line, self.potential_movies)) == 0:
                return ['pick in potential']
            if len(self.disambiguate(line, self.potential_movies)) > 1:
                return ['pick one in potential']
            movie = self.disambiguate(line, self.potential_movies)[0]
            self.potential_movies = []
            potential_line = self.potential_line.lower()
            self.potential_line = ''
            self.clean_title = True
            if '"' not in potential_line:
                title_split = re.split(' |, ', self.titles[movie][0].lower())
                for word in title_split:
                    regex = '(^' + word + '$' + ')|(' + '^' + word + '[^a-zA-Z0-9]' + ')|(' + '[^a-zA-Z0-9]' + word + '$' + ')|(' + '[^a-zA-Z0-9]' + word + '[^a-zA-Z0-9])'
                    potential_line = re.sub(regex, ' ', potential_line)
                return self.recognize_input('"' + self.titles[movie][0] + '" ' + potential_line)
            return self.recognize_input(re.sub('".+"', '"' + self.titles[movie][0] + '"', potential_line))
        potential_titles = self.extract_titles(line)
        if len(potential_titles) > 0:
            movies_list = []
            for title in potential_titles:
                movies_found = self.find_movies_by_title(title)
                if len(movies_found) > 1:
                    if not self.creative:
                        return ['multiple same movies', title]
                    self.potential_movies = movies_found
                    self.potential_line = line
                    if len(movies_list) == 0:
                        return ['creative-multiple same movies', movies_found]
                    self.potential_movies = []
                movies_list.append(movies_found)
            movies_list = np.hstack(movies_list)#np.array(movies_list).flatten()
            if len(movies_list) == 1:
                sentiment = self.extract_sentiment(line)
                if sentiment != 0:
                    return ['found', movies_list[0], sentiment]
                return ['not sure', movies_list[0]]
            if len(movies_list) == 0:
                return ['nothing found', title]
            if not self.creative or len(self.potential_movies) > 0:
                return ['multiple different movies']
            self.potential_movies = movies_list
            self.potential_line = line
            return ['creative-multiple same movies', movies_list]

        else:
            yes = ['yes', 'YES', 'Yes', 'y', 'Y', 'yeah', 'Yeah', 'YEAH', 'yep', 'Yep', 'YEP']
            no = ['no', 'NO', 'No', 'n', 'N', 'nah', 'Nah', 'NAH']
            if any(word in line for word in yes) or any(word in line for word in no):
                if self.user_ratings_count >= 5:
                    if any(word in line for word in yes):
                        return ['confirm', 'yes']
                    return ['confirm', 'no']
        return ['']

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
        result = re.findall('"([^"]*)"', preprocessed_input)
        if len(result) == 0 and self.creative:
            articles = ['A', 'An', 'The', 'a', 'an', 'the']
            result = []
            for i in range(len(self.titles)):
                title = re.split(' |, ', self.titles[i][0].lower())
                if title[-2] in articles:
                    title = title[-2] + ' ' + ' '.join(title[:-2])
                else:
                    title = ' '.join(title[:-1])
                title = title.replace('*', '\*').replace('[', '').replace(']', '')
                regex = '(^' + title + '$' + ')|(' + '^' + title + '[^a-zA-Z0-9]' + ')|(' + '[^a-zA-Z0-9]' + title + '$' + ')|(' + '[^a-zA-Z0-9]' + title + '[^a-zA-Z0-9])'
                if bool(re.search(regex, preprocessed_input.lower())):
                    result.append(self.titles[i][0][:-7])
            return result
        return result

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
        articles = ['A', 'An', 'The', 'a', 'an', 'the']
        if (self.clean_title and self.creative) or not self.creative:
            if self.clean_title:
                self.clean_title = False
            title_split = title.split()
            if title_split[0] in articles:
                if '(' in title_split[-1]:
                    regex = ' '.join(title_split[1:-1]) + ', ' + title_split[0] + ' ' + title_split[-1]
                    regex = regex.replace('(', '\(').replace(')', '\)')
                else:
                    regex = ' '.join(title_split[1:]) + ', ' + title_split[0] + ' \([0-9]{4}\)'
            else:
                if '(' in title_split[-1]:
                    regex = title
                    regex = regex.replace('(', '\(').replace(')', '\)')
                else:
                    regex = title + ' \([0-9]{4}\)'
            indices = []
            for i in range(len(self.titles)):
                if re.match(regex, self.titles[i][0]):
                    indices.append(i)
            return indices
        if self.creative:
            new_title = title
            title_split = title.split()
            if title_split[0].lower() in articles:
                if re.match('.* \([0-9]{4}\)', title):
                    new_title = ' '.join(title_split[1:-1]) + ', ' + title_split[0] + ' ' + title_split[-1]
                else:
                    if len(title_split) == 2:
                        new_title = ' '.join(title_split[1:]) + ', ' + title_split[0]
                    else:
                        new_title = ' '.join(title_split[1:-1]) + ', ' + title_split[0]
            return self.disambiguate(new_title, np.arange(len(self.titles)))

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
        overall_sentiment = 0
        last_sentiment = 0
        negation_flag = False

        # remove everything between quotes 
        preprocessed_input = re.sub(r'".*"', '', preprocessed_input)
        text_list = re.findall(r"[\w']+|[.,!?;:\"]", preprocessed_input)
        text_list = [''.join(c for c in s if c != "\"") for s in text_list]
        text_list = [s for s in text_list if s]
        
        if not self.creative:
            for word in text_list:
                stemmed_word = self.p.stem(word)

                # if negation word, negate all sentiments until next punctuation
                if word in self.negation or stemmed_word in self.negation:
                    negation_flag = not negation_flag
                if word in self.punctuation:
                    negation_flag = False

                if word in self.sentiment:
                    if self.sentiment[word] == 'pos' and not negation_flag or self.sentiment[word] == 'neg' and negation_flag:
                        overall_sentiment += 1
                        last_sentiment = 1
                    else:
                        overall_sentiment -= 1
                        last_sentiment = -1
                elif stemmed_word in self.stemmed_sentiment:
                    if self.stemmed_sentiment[stemmed_word] == 'pos' and not negation_flag or self.stemmed_sentiment[stemmed_word] == 'neg' and negation_flag:
                        overall_sentiment += 1
                        last_sentiment = 1
                    else:
                        overall_sentiment -= 1
                        last_sentiment = -1
            
            if overall_sentiment > 0:
                return 1
            elif overall_sentiment < 0:
                return -1
            
            # decide sentiment by last word if 0
            if last_sentiment > 0:
                return 1
            elif last_sentiment < 0:
                return -1
            return 0
        else:
            intensity_count = 0
            neutral_flag = False

            for word in text_list:
                stemmed_word = self.p.stem(word)

                # if intensity word, increase multiplier
                # if negation word, negate all sentiments until next punctuation
                if (word in self.intensity or stemmed_word in self.intensity or 
                word in self.strong_pos or stemmed_word in self.strong_pos_stemmed or 
                word in self.strong_neg or stemmed_word in self.strong_neg_stemmed):
                    if negation_flag and intensity_count == 0:
                        neutral_flag = True
                    intensity_count += 1
                if word in self.negation or stemmed_word in self.negation:
                    negation_flag = not negation_flag
                if word in self.punctuation:
                    negation_flag = False
                    intensity_count = 0
                    neutral_flag = False

                if neutral_flag:
                    # neutral, don't do anything to overall_sentiment
                    last_sentiment = 0
                elif word in self.strong_pos or stemmed_word in self.strong_pos_stemmed:
                    if not negation_flag:
                        overall_sentiment += 3 * intensity_count
                        last_sentiment = 1
                    else:
                        overall_sentiment -= 3 * intensity_count
                        last_sentiment = -1
                elif word in self.strong_neg or stemmed_word in self.strong_neg_stemmed:
                    if not negation_flag:
                        overall_sentiment -= 3 * intensity_count
                        last_sentiment = -1
                    else:
                        overall_sentiment += 3 * intensity_count
                        last_sentiment = 1
                
                elif word in self.sentiment:
                    if self.sentiment[word] == 'pos' and not negation_flag or self.sentiment[word] == 'neg' and negation_flag:
                        overall_sentiment += 3 * intensity_count if intensity_count > 0 else 1
                        last_sentiment = 1
                    else:
                        overall_sentiment -= 3 * intensity_count if intensity_count > 0 else 1
                        last_sentiment = -1
                elif stemmed_word in self.stemmed_sentiment:
                    if self.stemmed_sentiment[stemmed_word] == 'pos' and not negation_flag or self.stemmed_sentiment[stemmed_word] == 'neg' and negation_flag:
                        overall_sentiment += 3 * intensity_count if intensity_count > 0 else 1
                        last_sentiment = 1
                    else:
                        overall_sentiment -= 3 * intensity_count if intensity_count > 0 else 1
                        last_sentiment = -1
            
            if overall_sentiment > 0:
                if overall_sentiment >= 3:
                    return 2
                return 1
            elif overall_sentiment < 0:
                if overall_sentiment <= -3:
                    return -2
                return -1
            
            # decide sentiment by last word if overall_sentiment is 0
            if last_sentiment > 0:
                return 1
            elif last_sentiment < 0:
                return -1
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

    def edit_distance(self, s1, s2):
        """Helper function for find_movies_closest_to_title: Given two strings, 
        returns the edit distance between them.

        :param s1: the first string
        :param s2: the second string
        :returns: the edit distance between the two strings
        """
        s1 = s1.lower()
        s2 = s2.lower()
        len1 = len(s1)
        len2 = len(s2)

        # initialization
        grid = np.zeros((len1 + 1, len2 + 1))
        for i in range(len1 + 1):
            grid[i][0] = i
        for j in range(len2 + 1):
            grid[0][j] = j

        # recurrence relation -- grid[i][j] is the edit distance between s1[:i] and s2[:j]
        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                 # if characters are the same, no substitution cost
                if s1[i - 1] != s2[j - 1]:
                    substitute = 2
                else:
                    substitute = 0
                grid[i][j] = min(grid[i - 1][j] + 1, grid[i][j - 1] + 1, grid[i - 1][j - 1] + substitute)
        
        # termination
        return grid[len1][len2]

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
        title_year = re.search(r"^.*(?:\s(\(\d{4}\)))$", title)
        if title_year:
            title_year = title_year.group(1)
            title = title[: len(title) - 7]  # removes year from title
        
        movies = []
        min_distance = float('inf')
        for i, movie in enumerate(self.titles):
            cur_title = movie[0]
            year = re.search(r"^.*(?:\s(\(\d{4}\)))$", cur_title)
            if year:
                year = year.group(1)
                cur_title = cur_title[: len(cur_title) - 7]

            edit_distance = self.edit_distance(title, cur_title)
            if edit_distance > max_distance:
                continue
            if edit_distance == min_distance:  # tie for best edit distance, append to list
                movies.append(i)
            elif edit_distance < min_distance:  # new best edit distance, clears list and appends
                movies = [i]
                min_distance = edit_distance
        
        return movies

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
        result = []
        clarification = clarification.replace('(', '\(').replace(')', '\)').replace('"', '')
        clarification = clarification.lower()
        for candidate in candidates:
            regex = '(^' + clarification + '$' + ')|(' + '^' + clarification + '[^a-zA-Z0-9]' + ')|(' + '[^a-zA-Z0-9]' + clarification + '$' + ')|(' + '[^a-zA-Z0-9]' + clarification + '[^a-zA-Z0-9])'
            if bool(re.search(regex, self.titles[candidate][0].lower())):
                result.append(candidate)
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
        binarized_ratings = np.where(ratings > threshold, -10, ratings)
        binarized_ratings = np.where(binarized_ratings > 0, -1, binarized_ratings)
        binarized_ratings = np.where(binarized_ratings == -10, 1, binarized_ratings)
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
        similarity = np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))
        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return similarity

    def recommend_helper(self, movie_idx, known_rating_list, ratings_matrix):
        similarity_list = np.zeros(len(ratings_matrix))
        for i in known_rating_list:
            if ratings_matrix[movie_idx].any() and ratings_matrix[i].any():
                similarity_list[i] = self.similarity(ratings_matrix[movie_idx], ratings_matrix[i])
        return np.array(similarity_list)

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
        rec_map = np.zeros(len(self.titles))
        unknown_rating_list = np.where(user_ratings == 0)[0]
        known_rating_list = np.nonzero(user_ratings)[0]
        for i in unknown_rating_list:
            similarity_list = self.recommend_helper(i, known_rating_list, ratings_matrix)
            rating = np.dot(user_ratings, similarity_list)
            rec_map[i] = rating
        # Populate this list with k movie indices to recommend to the user.
        recommendations = list((-rec_map).argsort()[:k])
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
        Hi, I'm your movie chatbot, MovieGenie. I can talk about movie recommendations, and please ask me about one movie at a time!
        You can input up to five movies that you like, and I'll find a movie that I think you would like.
        In starter mode, please put your movie in quotation marks! In creative mode, watch me transform into a Southern chatbot.
        You don't have to put titles in quotation marks and can only mention parts of a title in quotes. I'll guide you through the selection process!
        """


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
