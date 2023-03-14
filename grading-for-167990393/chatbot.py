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
        self.creative = creative
        self.memory = []  # stack to hold memory--elements pushed onto memory are list of form [title(s), sentiment, type]
        self.name = 'Candace'
        if self.creative: self.name = 'British Candace'
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')
        self.recommended = []  # movies we've already recommended
        self.cur_recs = []  # movies that we can recommended based on users
        self.user_ratings = np.zeros(ratings.shape[0])
        self.num_rated = 0
        ########################################################################
        # Binarize the movie ratings matrix.                             #
        ########################################################################
        self.ratings = self.binarize(ratings)
        ########################################################################
        #                             END OF YOUR CODE                         #
        ########################################################################

    ############################################################################
    # 1. WARM UP REPL                                                          #
    ############################################################################
    def greeting(self):
        """Return a message that the chatbot uses to greet the user."""
        greeting_message = "Hi, I am Candace. I'm here to recommend a movie to you. Can you tell me about a movie you've seen before?"
        if self.creative: greeting_message = "\'Ello, mate! I'm Candace, originally from Newcastle, England. I'm here to recommend a bloody good movie to you today! Can you tell me about a movie you've seen before?"
        return greeting_message

    def goodbye(self):
        """Return a message that the chatbot uses to bid farewell to the user."""
        goodbye_message = "Have a wonderful day!"
        if self.creative: goodbye_message = 'It\'s a wonderful day today, innit? I\'ll talk to you later, mate — I\'m going to go get a cup of tea!'
        return goodbye_message

    ############################################################################
    # 2. Modules 2 and 3: extraction and transformation                        #
    ############################################################################
    def emotion_response(self, line):
        """
        Helper function for process() to respond to emotions in the user's input.
        :param: user input
        :return: True if emotion in response, False if not
                 Emotional response if True, empty string if not
        """
        angry_emotions = ['angry', 'mad', 'furious', 'annoyed', 'irritated']
        sad_emotions = ['sad', 'unhappy', 'depressed', 'down', 'miserable', 'despondant', 'gloomy']
        happy_emotions = ['happy', 'excited', 'cheerful', 'delighted', 'cheery', 'merry', 'joyful']
        fear_emotions = ['stressed', 'stress', 'scared', 'fear', 'terrified', 'fearful', 'panic', 'anxious', 'nervous']
        tired_emotions = ['tired', 'weary', 'exhausted', 'sleepy', 'drowsy']
        if any(angry in line for angry in angry_emotions): return True, "Apologies, mate. Didn't mean to make you angry."    
        if any(sad in line for sad in sad_emotions): return True, "It's bloody horrible feeling that way. What's bringing you down, mate?"

        if any(fear in line for fear in fear_emotions):
            fear_word = ''
            for fear in fear_emotions:
                if fear in line:
                    fear_word = fear
                    break
            return True, "I'm sorry, mate. I hate feeling {}. I hope it gets better soon.".format(fear_word)

        if any(tired in line for tired in tired_emotions): return True, "Get some rest, mate! You've been working hard, I'm sure."
        if any(happy in line for happy in happy_emotions): return True, "I'm glad you're feeling cheery! Who isn't on a bloody wonderful day like today?"
        return False, ''
    
    def arbitrary_input(self, line):
        """
        Helper function for process() to respond to arbitrary input.
        :param: user input
        :return: string response to the arbitrary input
        """
        if 'how are you' in line.lower():
            how_are_you_responses = ['I\'ve been better.', 'Doing alright.', 'I\'m ok. What about you?', 'Hanging in there!']
            return np.random.choice(how_are_you_responses)

        if "who are you" in line.lower() or "what are you" in line.lower():
            return "I'm " + self.name + ", your movie recommender chatbot! What about you?"

        if "what can you do" in line.lower():
            return 'I can recommend movies for you! Do you want to tell me about one?'

        brit_pattern = '.*(London|london|United Kingdom|united kingdom|u.k.|Britain|britain|Great Britain|great britain|England|england|tea|scones|biscuits|crumpets).*'
        brit_matches = re.findall(brit_pattern, line)
        if len(brit_matches) > 0:
            match = brit_matches[0]
            response = 'I love %s! I\'m British, ya know?' % match
            return response

        to_you_pattern = '(.*) to (.*) you'
        to_you_matches = re.findall(to_you_pattern, line)
        if len(to_you_matches) > 0:
            match = to_you_matches[0]
            return "It's %s to % you too." % match

        can_you_pattern = '[Cc]an you (.*)'
        can_you_matches = re.findall(can_you_pattern, line)
        if len(can_you_matches) > 0:
            match = can_you_matches[0]
            match = match.replace('me', 'you').strip('?')
            if 'my' in match: match = match.replace('my', 'your')
            elif 'your' in match: match = match.replace('your', 'my')
            else: match
            return 'I can %s, but I don\'t want to right now.' % match

        are_you_pattern = '[Aa]re you (.*)'
        are_you_matches = re.findall(are_you_pattern, line)
        if len(are_you_matches) > 0:
            match = are_you_matches[0].strip('?')
            if 'my' in match: match = match.replace('my', 'your')
            elif 'your' in match: match = match.replace('your', 'my')
            else: match
            return 'I might be %s, but I also might not be. That\'s up to you to figure out, mate.' % match

        what_is_pattern = '(?:[Ww]hat is|[Ww]hat\'s) (.*)'
        what_is_matches = re.findall(what_is_pattern, line)
        if len(what_is_matches) > 0:
            match = what_is_matches[0].strip('?')
            if 'my' in match: match = match.replace('my', 'your')
            elif 'your' in match: match = match.replace('your', 'my')
            else: match
            return 'I\'m not sure what %s is. Apologies, mate.' % match

        everybody_pattern = '[Ee]verybody (.*)'
        everybody_matches = re.findall(everybody_pattern, line)
        if len(everybody_matches) > 0:
            match = everybody_matches[0].strip('?!.')
            return 'Is there a specific person that you think %s?' % match
        
        greeting_pattern = '.*(hi|hello|sup|hey|greetings|hola|ello).*'
        greeting_matches = re.findall(greeting_pattern, line.lower())
        if len(greeting_matches) > 0:
            match = greeting_matches[0]
            return '%s to you too, mate!' % match

        generic_responses = ['Ok, got it.', 'Ok.', 'I see.', 'I see, I\'ll have to ponder that.', 'I understand.', 'That makes sense.', "Hmmm mate, that's bloody interesting, but I'd love to talk more about specific movies you've seen.",
                             "Bonkers, I didn't understand what you said! Can you tell me about a movie you've seen before?",
                             "Oh that's bloody interesting. Can we talk more about movies now though, mate?", "Rubbish!", 'Please go on, mate.']
        return np.random.choice(generic_responses)

    def construct_sentiment_response(self, title, sentiment, inds):
        """
        Helper function for process() to construct a response depending on the sentiment.
        :param: title (string), sentiment (int), and index of movie
        :return: string response
        """
        if sentiment == 0:
            verbs = ["like", "enjoy"]
            prompt_for_info = ["Can you tell me more about it?", "Tell me more about it!"] # make bri-ish
            self.memory.append([[title], sentiment, 'sentiment'])
            return "Did you {} \"{}\"? I'm not sure whether you did. {}".format(np.random.choice(verbs), title, np.random.choice(prompt_for_info)) + ' '
            
        self.user_ratings[inds[0]] = sentiment  # Add movie sentiment pair to user_ratings
        self.num_rated += 1

        if sentiment >= 1:  # pos sentiment about movie
            pos_responses = ["Golly! You {0} \"{1}\".", "Alrighty, you {0} watching \"{1}\".", "Ah yes, \"{1}\" is a bloody good movie! I {0} it too."]
            pos_verbs = ['liked', 'enjoyed']
            if sentiment >= 2: pos_verbs = ['loved']  # substitute with stronger verbs
            return np.random.choice(pos_responses).format(np.random.choice(pos_verbs), title) + ' '

        else:  # negative sentiment about movie
            neg_responses = ["Oh naur. You {0} \"{1}\".", "Blimey, you {0} watching \"{1}\".", "\"{1}\" was pure rubbish. I {0} it too."]
            neg_verbs = ['disliked', 'did not enjoy']
            if sentiment <= -2: neg_verbs = ['hated']  # substitute with stronger verbs
            return np.random.choice(neg_responses).format(np.random.choice(neg_verbs), title) + ' '
        
    def process(self, line):
        """Process a line of input from the REPL and generate a response.
        This is the method that is called by the REPL loop directly with user input.
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
        prompts_for_info = ["Can you tell me about another movie now?", "Can you talk about a different movie you've seen recently?", "What other movies have you watched, and what did you think about them?"]
        follow_up = ["Would you like to hear another recommendation?", "How about another one?"]
            
        # There are recs left to give (only give 5 out of the 10) + user hasn't quit yet
        if len(self.cur_recs) > 5 and ("yes" in line.lower() or "yeah" in line.lower() or "ok" in line.lower()):
            new_rec_response = ["Another movie I would recommend you watch is \"{}\".", "I think you would also love \"{}\"!", "You should also check out \"{}\"!"]
            to_recommend = self.titles[self.cur_recs[0]][0]
            self.recommended.append(self.cur_recs[0])
            del self.cur_recs[0]
            if len(self.cur_recs) == 5: # already given 5 recs, prompt for movie again
                self.cur_recs = [] # reset
                return np.random.choice(new_rec_response).format(to_recommend) + " " + "I have no other recommendations for now." + np.random.choice(prompts_for_info)
            # Otherwise, ask again if they want another rec
            return np.random.choice(new_rec_response).format(to_recommend) + " " + np.random.choice(follow_up) + " " + "Or if you're done, you can enter :quit"
        
        if self.creative:
            memory_iter = 0
            memory_response = ''
            while len(self.memory) > 0 and memory_iter < 2:  # User input is related to memory
                memory = self.memory[0]
                self.memory.remove(memory)
                memory_title_list = memory[0]
                memory_sentiment = memory[1]
                memory_type = memory[2]
                first_title = memory_title_list[0]

                if memory_type == 'spellcheck':
                    if memory_iter == 1:
                        self.memory.insert(0, memory)
                        return memory_response + ' For the other movie you mentioned earlier, did you mean ' + first_title + ', mate?'
                    if 'yes' in line.lower():
                        inds = self.find_movies_by_title(first_title)  # Find index for movie title
                        memory_response += self.construct_sentiment_response(first_title, memory_sentiment,inds) + ' '
                    else:  # not correct
                        if len(memory_title_list) > 1:
                            memory_title_list.remove(first_title)
                            self.memory.append(memory_title_list, memory_sentiment, 'spellcheck')
                            return 'Hmm, I see. Perhaps did you mean "' + memory_title_list[0] + '", mate?'
                        else:
                            if len(self.memory) == 0: return 'Sorry, mate. I\'m not sure what you mean then. Why don\'t you tell me about a different movie?'
                            else: memory_response += 'Sorry, mate. I\'m not sure what you mean then.'
                
                if memory_type == 'disambiguate':
                    if memory_iter == 1:
                        possible_movies = ''
                        inds = memory_title_list
                        for i in range(len(inds)):
                            ind = inds[i]
                            movie_title = self.titles[ind][0]
                            possible_movies += movie_title

                            if len(inds) > 2:
                                if i == len(inds) - 2: possible_movies += ', or '
                                elif i == len(inds) - 1: possible_movies += '?'
                                else: possible_movies += ', '
                            else:  # len(inds) == 2
                                if i == 0: possible_movies += ' or '
                                else: possible_movies += '?'
                        self.memory.insert(0, memory)
                        return memory_response + ' For the other movie you mentioned earlier, did you mean ' + possible_movies
                    
                    clarification = line.strip('.,?!')  # strip user's line of punctuation
                    remaining_candidates = self.disambiguate(clarification, memory_title_list)
                    if len(remaining_candidates) == 1:  # Found the correct candidate
                        memory_response += self.construct_sentiment_response(self.titles[remaining_candidates[0]][0], memory_sentiment, remaining_candidates) + ' '
                    else:  # Multiple candidates remaining, just give up
                        if len(self.memory) == 0:
                            return 'Sorry, mate. I\'m still not sure which movie you\'re referring to, but it\'s okay. Why don\'t you tell me about a different movie?'
                        else:
                            memory_response += 'Sorry, mate. I\'m still not sure which movie you\'re referring to, but it\'s okay.'

                if memory_type == 'sentiment':
                    if memory_iter == 1:
                        return memory_response + self.construct_sentiment_response(first_title, memory_sentiment, memory_title_list)
                    if first_title.lower() in line.lower():
                        self.add_quotes(first_title.lower(), line.lower())

                    new_sentiment = self.extract_sentiment(self.preprocess(line))

                    if new_sentiment == 0:
                        if len(self.memory) == 0:
                            return 'Sorry, mate. I still can\'t tell how you feel about ' + first_title + ', but it\'s okay. Why don\'t you tell me about a different movie?'
                        else:
                            memory_response += 'Sorry, mate. I still can\'t tell how you feel about ' + first_title + ', but it\'s okay.'
                    else:
                        inds = self.find_movies_by_title(first_title)  # Find index for movie title
                        memory_response += self.construct_sentiment_response(first_title, new_sentiment, inds)
                memory_iter += 1

            if memory_iter != 0: return memory_response

            titles = self.extract_titles(line)
            if len(titles) == 0:  # Candace can't find any titles in user's input
                # Respond to any emotions in response
                emotion, emotion_response = self.emotion_response(line.lower())
                if emotion: return emotion_response
                return self.arbitrary_input(line) + " " + np.random.choice(prompts_for_info)  # Handle arbitrary input if no emotion in it

            sentiments = self.extract_sentiment_for_movies(line)  # Get sentiments for each movie in the input
            sentiment_response = ""  # Used for building up sentiment response for multiple movies
            clarification_response = ""  # Used for building up response asking for clarification (if applicable)
            for title, sentiment in sentiments:  # Get corresponding movie indices
                inds = self.find_movies_by_title(title)  # Find index for movie title
                if len(inds) == 0:
                    # check if it might be a spelling error
                    closest_titles = self.find_movies_closest_to_title(title)
                    if len(closest_titles) == 0:  # can't find similar titles
                        sentiment_response += "Hm... Sorry! I haven't heard of {}. ".format(title)
                        continue
                    else:
                        maybe_movies = []
                        for ind in closest_titles:
                            maybe_movies.append(self.titles[ind][0])

                        self.memory.append([maybe_movies,sentiment,'spellcheck'])
                        if clarification_response == "":
                            clarification_response = 'Did you mean "' + maybe_movies[0] + '", mate?'
                        continue
                    
                elif len(inds) > 1:  # Clarify which movie person is talking about (disambiguate)
                    self.memory.append([inds, sentiment, 'disambiguate'])
                    if clarification_response == "":
                        # Response to user should include list of possible movies to choose from
                        possible_movies = ''
                        for i in range(len(inds)):
                            ind = inds[i]
                            movie_title = self.titles[ind][0]
                            possible_movies += movie_title

                            if len(inds) > 2:
                                if i == len(inds) - 2: possible_movies += ', or '
                                elif i == len(inds) - 1: possible_movies += '?'
                                else: possible_movies += ', '
                            else:  # len(inds) == 2
                                if i == 0: possible_movies += ' or '
                                else: possible_movies += '?'
                        
                        responses = ['Blimey, I found multiple movies called \"{}\". Could you clarify which one you\'re talking about bruv?', 'There is more than one movie called \"{}\". Which one are you thinking about bruv?', 'Which bloody \"{}\" movie are you talking about bruv?']
                        clarification_response = np.random.choice(responses).format(title) + ' ' + possible_movies
                    continue
                
                if sentiment == 0:
                    if clarification_response == '': clarification_response = self.construct_sentiment_response(title, sentiment, inds)
                    else: self.construct_sentiment_response(title, sentiment, inds)
                else: sentiment_response += self.construct_sentiment_response(title, sentiment, inds) + ' '  # else, len(inds) == 1
                
            if self.num_rated < 5:  # Not enough data points, prompt again for movie
                if clarification_response != "": return sentiment_response + " " + clarification_response
                else: return sentiment_response + " " + np.random.choice(prompts_for_info)
            
            # At this point, we have enough information to make a recommendation
            self.cur_recs = self.recommend(self.user_ratings, self.ratings)  
            to_recommend = self.titles[self.cur_recs[0]][0]
            self.recommended.append(self.cur_recs[0])
            del self.cur_recs[0]
            self.num_rated = 0  # reset so that user needs to enter 5 more data points next time
            rec_responses = ["Mate I've got it! I think you'd bloody love \"{}\".", "Thanks mate, that's enough for me! You absolutely must check out \"{}\".", "Thanks for that! I recommend that you watch \"{}\"."]
            return sentiment_response + " " + np.random.choice(rec_responses).format(to_recommend) + " " + np.random.choice(follow_up) + " " + "Or if you're done, you can enter :quit"

        else:
            titles = self.extract_titles(line)
            if len(titles) == 0:  # user must enter at least one title - accounts for input cases w/o quotation marks
                responses = ["Hmmm that's cool, but I'd love to talk more about specific movies you've seen!", "Sorry, I didn't understand what you said! Can you tell me about a movie you've seen before?", "Oh interesting. Can we talk more about movies now?", "Great!"]
                return np.random.choice(responses)
            
            if len(titles) > 1:  # only expected to process one movie per line
                return "Oh! Do you actually mind telling me about one movie at a time? It's easier for me to follow!"
            
            title = titles[0]  # extract the single title in list
            inds = self.find_movies_by_title(title)  # Find index for movie title

            # Not a title in our database, need to ask for a new one
            if len(inds) == 0: return "I've never heard of \"{}\". Sorry about that! Can you tell me about a different movie?".format(title)

            # Clarify which movie person is talking about
            if len(inds) > 1:
                responses = ['I found multiple movies called \"{}\". Do you mind clarifying which one you\'re referring to?', 'There is more than one movie called \"{}\". Which one are you talking about?', 'Which \"{}\" movie are you talking about?']
                return np.random.choice(responses).format(title)
            
            sentiment = self.extract_sentiment(self.preprocess(line))  # extract sentiment from line
            if sentiment == 0:  # Want user to give sentiment opinion about movie
                verbs = ["like", "enjoy"]
                prompt_for_info = ["Can you tell me more about it?", "Tell me more about it!"]
                return "Did you {} \"{}\"? I'm not sure whether you did. {}".format(np.random.choice(verbs), title, np.random.choice(prompt_for_info))

            self.user_ratings[inds] = sentiment  # Store user sentiment at found movie index
            self.num_rated += 1
            sentiment_response = ""
            if sentiment >= 1:  # pos sentiment about movie
                pos_responses = ["Great! You {0} \"{1}\".", "Okay, you {0} watching \"{1}\".", "Ah yes, \"{1}\" is a good movie! I {0} it too."]
                pos_verbs = ['liked', 'enjoyed']
                if sentiment >= 2: pos_verbs = ['loved']  # substitute with stronger verbs
                sentiment_response = np.random.choice(pos_responses).format(np.random.choice(pos_verbs), title)

            else:  # negative sentiment about movie
                neg_responses = ["I see. You {0} \"{1}\".", "Okay, you {0} watching \"{1}\".", "Yeah, \"{1}\" is not a great movie. I {0} it too."]
                neg_verbs = ['disliked', 'did not enjoy']
                if sentiment <= -2: neg_verbs = ['hated']  # substitute with stronger verbs
                sentiment_response = np.random.choice(neg_responses).format(np.random.choice(neg_verbs), title)
                
            # Not enough data points, prompt again for movie
            if self.num_rated < 5: return sentiment_response + " " + np.random.choice(prompts_for_info)
                
            # At this point, we have enough information to make a recommendation
            self.cur_recs = self.recommend(self.user_ratings, self.ratings)  
            to_recommend = self.titles[self.cur_recs[0]][0]
            self.recommended.append(self.cur_recs[0])
            del self.cur_recs[0]
            self.num_rated = 0  # reset so that user needs to enter 5 more data points next time
            rec_responses = ["I've got it! I think you would love \"{}\".", "That's enough for me to make a recommendation. I suggest you watch \"{}\".", "Thank you for that! I recommend that you watch \"{}\"."]
            return sentiment_response + " " + np.random.choice(rec_responses).format(to_recommend) + " " + np.random.choice(follow_up) + " " + "Or if you're done, you can enter :quit"

    @staticmethod
    def preprocess(text):
        """Do any general-purpose pre-processing before extracting information from a line of text.
        Given an input line of text, this method should do any general
        pre-processing and return the pre-processed string. The outputs of this
        method will be used as inputs (instead of the original raw text) for the
        extract_titles, extract_sentiment, and extract_sentiment_for_movies methods.
        Note that this method is intentially made static, as you shouldn't need
        to use any attributes of Chatbot in this method.
        :param text: a user-supplied line of text
        :returns: the same text, pre-processed
        """
        neg = False
        quote = False
        delims = "?.,!:;"
        neg_words = ['n\'t', 'not', 'never', 'no ', ' no ', 'no!', 'no.', 'no?', 'neither', 'nor', 'Neither']
        neg_result = []
        tokens = text.split()  # split text by spaces
        
        for token in tokens:
            if '\"' in token:  # switch quote states when we encouter a quotation mark
                neg_result.append(token)
                if '\"' == token[0] and '\"' in token[1:]: continue  # token contains start and end quotes
                if quote and neg and any(c in token for c in delims): neg = False
                quote = not quote  
                continue
            
            if quote:  # ignore words that are in the middle of a movie title
                neg_result.append(token)
                continue
            
            stripped = token.strip(delims).lower()

            if neg and 'NOT_' not in token: negated = "NOT_" + token
            else: negated = token
            neg_result.append(negated)

            # switch negation states when we encounter neg word
            if any(neg.lower() in token.lower() for neg in neg_words): neg = True

            # stop negating once we reach a punctuation mark
            if any(c in token for c in delims): neg = False

        return ' '.join(neg_result)

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
        matches = []
        pattern = "\"([ !,\(\)\'\w.-]+)\""
        matches = re.findall(pattern, preprocessed_input)
        result = matches
        # creative mode has support for titles not in quotation marks or with incorrect capitalization
        if self.creative:
            articles = ['la', 'le', 'les', 'il', "l'",'a', 'die', 'das', 'an', 'the', 'der']
            lc_matches = []
            for match in matches:
                lc_matches.append(match.lower()) # all matches converted to lowercase
                
                # remove found titles with quotation marks around it from input
                ind = preprocessed_input.index(match) - 1
                preprocessed_input = preprocessed_input[:ind] + preprocessed_input[ind + len(match) + 2:]
            
            lc_input = preprocessed_input.lower()  # lowercase version of input

            # Check known movie titles to see if they're in the input
            for entry in self.titles:
                title = entry[0]
                no_year_title = title[:len(title) - 7].lower()  # remove year from title and make lowercase
                eng_title = no_year_title

                foreign_title = "NOT IN INPUT"
                # Handle case like American Friend, The (Amerikanische Freund, Der)
                
                split_titles = no_year_title.split(' (')   # e.g. separate "Story of O, The" and "Histoire d'O)"
                if len(split_titles) > 1:   # only if the title contains both english and foreign versions, split
                    eng_title = split_titles[0]
                    foreign_title = split_titles[1][:-1]
                
                eng_split = eng_title.split(', ')
                if len(eng_split) > 1 and eng_split[1] in articles:
                    eng_title = eng_split[1] + " " + eng_split[0]   # Turn "Secret Agent, The" into "The Secret Agent"

                # Brute force fix to stop it from saying the verb hated was a title (can maybe make better fix where we recognize it's verb for a title already found?)
                if eng_title == 'hated' or eng_title == 'hate':
                    continue

                foreign_split = foreign_title.split(", ")
                if len(foreign_split) > 1 and foreign_split[1] in articles:
                    foreign_title = foreign_split[1] + " " + foreign_split[0]   # Turn "Amerikanische Freund, Der" into "Der Amerikanische Freund"

                if (eng_title not in lc_input) and (foreign_title not in lc_input): # don't even try if it's not contained in lc_input
                    continue

                pattern2 = "[^'\w](" + eng_title + ")\\b"
                matches2 = re.findall(pattern2, lc_input)

                pattern3 = "[^'\w](" + foreign_title + ")\\b"
                matches3 = re.findall(pattern3, lc_input)
                
                # Found movie title in input (case insensitive, doesn't need quotes around it) that we did not already find
                if (len(matches2) > 0) and (eng_title not in lc_matches) or (len(matches3) > 0) and (foreign_title not in lc_matches):
                    if len(matches2) > 0:
                        matches.append(eng_title)
                    else:
                        matches.append(foreign_title)
        
            matches = list(set(matches))  # remove duplicate titles found
            # get rid of false positives
            for match1 in matches:
                for match2 in matches:
                    if match1 != match2 and re.findall(match1, match2) != [] and match1 in result:
                        result.remove(match1)
        # removes potential duplicate titles from the list
        result = [*set(result)]
        return result
    
    def handle_capitalization(self, words_in_title):
        # Creative feature: identify movies without right capitalization
        capitalized_titles = []
        capitalized_titles.append("")

        # dict that maps a "standardized" word (first letter uppercase only) to list of all possible spellings in the db
        non_standard = {'To': ['To', 'to'], 'Of': ['of', 'Of'], 'The': ['the', 'The'], 'Ii': ['II'], 'And': ['And', 'and'], 'Goldeneye': ['GoldenEye'], 'Des': ['des'], 'Enfants': ['enfants'], 'Perdus,': ['perdus,'], 'A': ['A', 'a'], 'Yao': ['Yao', 'yao'], 'Dao': ['dao'], 'Waipo': ['waipo'], 'Qiao': ['qiao'], 'A.k.a.': ['a.k.a.'], 'Iii': ['III'], 'An': ['An', 'an'], 'For': ['For', 'for'], 'In': ['In', 'in'], 'If': ['if', 'If'], 'By': ['by', 'By'], 'Bio-dome': ['Bio-Dome'], 'Maudit': ['maudit'], 'Sefid': ['sefid'], 'Faan': ['faan'], 'Kui': ['kui'], 'Sam': ['sam', 'Sam'], 'Lam': ['lam'], 'Delle': ['delle'], 'Stelle,': ['stelle,'], 'Neverending': ['NeverEnding'], 'Iii,': ['III,'], 'Mcmullen,': ['McMullen,'], 'De': ['De', 'de'], 'Jour': ['jour'], 'Solntsem': ['solntsem'], 'Dozhdot': ['dozhdot'], 'On': ['on', 'On'], 'Demarco': ['DeMarco'], 'Shi': ['Shi', 'shi'], 'Nan': ['nan', 'Nan'], 'Nu': ['nu'], 'Il': ['Il', 'il'], 'Castrato': ['castrato'], 'I.q.': ['I.Q.'], 'With': ['with', 'With'], 'Iv': ['IV'], 'Agua': ['agua'], 'Para': ['para'], 'Chocolate': ['Chocolate', 'chocolate'], 'Vida': ['vida'], 'Loca': ['loca'], 'Photo': ['Photo', 'photo'], 'Pret-a-porter': ['Pret-A-Porter'], 'Couleurs:': ['couleurs:'], 'Kolory:': ['kolory:'], 'Y': ['y', 'Y'], 'From': ['From', 'from'], 'Baby-sitters': ['Baby-Sitters'], 'Der': ['Der', 'der'], 'Iii:': ['III:'], 'Ii:': ['II:'], 'Wang': ['wang'], 'Bie': ['bie'], 'Ji': ['ji', 'Ji'], 'Or': ['Or', 'or'], 'As': ['as', 'As'], 'No': ['No', 'no'], 'Corrida': ['corrida'], 'Robocop': ['RoboCop'], 'Fauves,': ['fauves,'], 'Thirty-two': ['Thirty-Two'], 'Speriamo': ['speriamo'], 'Che': ['che'], 'Me': ['Me', 'me'], 'La': ['la', 'La'], 'Cavo': ['cavo'], 'Au': ['Au', 'au'], 'E': ['e', 'E'], 'Cioccolata': ['cioccolata'], 'Flor': ['Flor', 'flor'], 'Mi': ['Mi', 'mi'], 'Secreto': ['secreto'], 'Aus': ['aus'], 'Libertad': ['libertad'], 'Soleil': ['Soleil', 'soleil'], 'Une': ['Une', 'une'], 'Étrange': ['étrange'], 'Aventure': ['aventure'], 'Torchon': ['torchon'], 'Sur': ['Sur', 'sur'], 'Le': ['Le', 'le'], 'Toit,': ['toit,'], 'Kidôtai': ['kidôtai'], 'Or:': ['or:'], 'Sai': ['Sai', 'sai'], 'Duk': ['duk'], "'til": ["'Til"], 'Id4': ['ID4'], 'Compagnie': ['compagnie'], "D'antonin": ["d'Antonin"], 'En': ['en', 'En'], 'Ce': ['ce', 'Ce'], 'Jardin,': ['jardin,'], 'Sans': ['Sans', 'sans'], 'Visage,': ['visage,'], 'San': ['San', 'san'], 'Yue': ['yue'], 'Tian': ['Tian', 'tian'], 'Niezi': ['niezi'], 'L.a.': ['L.A.'], 'Lo': ['lo', 'Lo'], 'Cha': ['cha'], 'Gu': ['gu'], 'Jing': ['jing', 'Jing'], "L'amour": ["L'Amour"], 'Qing': ['qing'], 'Wan': ['wan'], 'Sui': ['sui'], 'Hua': ['hua'], 'Roseaux': ['roseaux'], 'Sauvages': ['sauvages'], 'At': ['At', 'at'], 'Jie': ['jie'], 'Victor/victoria': ['Victor/Victoria'], 'E.t.': ['E.T.'], 'Extra-terrestrial': ['Extra-Terrestrial'], 'Iv:': ['IV:'], 'Peuple': ['Peuple', 'peuple'], "L'herbe": ["l'herbe"], 'Vs.': ['vs.'], 'Sources': ['sources'], 'T-men': ['T-Men'], 'Ou': ['ou'], 'Choses': ['choses'], 'Que': ['Que', 'que'], 'Je': ['je'], 'Sais': ['sais'], "D'elle": ["d'elle"], 'Cinema': ['cinema', 'Cinema'], '¡átame!': ['¡Átame!'], 'Brutto,': ['brutto,'], 'Cattivo,': ['cattivo,'], 'Una': ['una'], 'Volta': ['volta'], 'Vi': ['Vi', 'VI'], 'Über': ['über'], 'Bleu,': ['bleu,'], 'Xue': ['xue'], 'Shuang': ['shuang', 'Shuang'], 'Xiong': ['xiong'], 'Ii,': ['II,'], 'Inseglet,': ['inseglet,'], 'Hong': ['hong', 'Hong'], 'Deng': ['deng', 'Deng'], 'Long': ['long', 'Long'], 'Gao': ['gao'], 'Gua': ['gua'], 'Ben-hur': ['Ben-Hur', 'Ben-hur'], 'Liv': ['liv'], 'Som': ['som'], 'Hund': ['hund'], 'Ans': ['ans'], '3-d': ['3-D'], 'Eine': ['eine'], 'Pas': ['pas'], 'Sommeil': ['sommeil'], 'Vi:': ['VI:'], 'Butt-head': ['Butt-Head'], 'Chaat': ['chaat'], 'Goo': ['goo'], 'Si': ['si', 'Si'], 'Gaan': ['gaan'], 'Daan': ['daan'], 'Yam': ['yam'], 'Mo': ['mo'], "Mchale's": ["McHale's"], 'Plennik': ['plennik'], 'Suburbia': ['Suburbia', 'SubUrbia'], 'Jungle2jungle': ['Jungle2Jungle'], 'B*a*p*s': ['B*A*P*S'], 'N.m.': ['N.M.'], 'Avoir': ['avoir'], 'Cherche': ['cherche'], 'Son': ['son', 'Son'], 'Chat': ['chat'], 'Face/off': ['Face/Off'], 'Mib': ['MIB'], 'G.i.': ['G.I.'], 'Matchmaker,': ['MatchMaker,'], 'Rocketman': ['RocketMan'], 'Fairytale:': ['FairyTale:'], 'Vie': ['vie', 'Vie'], 'Rose': ['rose', 'Rose'], 'Luo': ['luo'], 'U.s.': ['U.S.'], 'Los': ['los', 'Los'], 'Milagros,': ['milagros,'], 'Trémula': ['trémula'], 'Goh': ['goh'], 'Ho': ['Ho', 'ho'], 'Yan': ['yan'], 'Guilass': ['guilass'], 'Bacheha-ye': ['Bacheha-Ye'], 'X-files:': ['X-Files:'], '3d': ['3D'], 'Vii:': ['VII:'], 'Viii:': ['VIII:'], 'Absent-minded': ['Absent-Minded'], 'Samurai': ['samurai', 'Samurai'], "O'gill": ["O'Gill"], 'Gnome-mobile,': ['Gnome-Mobile,'], 'Baseketball': ['BASEketball'], 'Ciel,': ['ciel,'], 'Och': ['och'], 'Di': ['di'], 'Notte,': ['notte,'], 'D.a.,': ['D.A.,'], 'Eighty-four': ['Eighty-Four'], 'Nimh,': ['NIMH,'], 'Da': ['da', 'Da'], 'Un': ['Un', 'un'], 'Insolito': ['insolito'], 'Destino': ['destino'], "Nell'azzurro": ["nell'azzurro"], 'Mare': ['mare'], "D'agosto": ["d'Agosto"], 'Six-string': ['Six-String'], 'È': ['è'], 'Bella': ['bella', 'Bella'], 'Do': ['Do', 'do'], 'Tai': ['Tai', 'tai'], 'Hi-lo': ['Hi-Lo'], 'Pick-up': ['Pick-up', 'Pick-Up'], '¡three': ['¡Three'], 'Sauvage,': ['sauvage,'], "'ha!'": ["'Ha!'"], '8mm': ['8MM'], 'Contre': ['contre'], 'Tous': ['tous'], 'Edtv': ['EDtv'], 'Out-of-towners,': ['Out-of-Towners,'], 'Rêvée': ['rêvée'], 'Anges,': ['anges,'], 'Hui': ['hui'], 'Del': ['del'], 'Ojos': ['ojos'], 'Slc': ['SLC'], 'Existenz': ['eXistenZ'], 'Sent-down': ['Sent-Down'], 'Yu': ['yu'], 'Raifu': ['raifu'], 'Hap': ['hap'], 'Aoniotita': ['aoniotita'], 'Kai': ['kai'], 'Mia': ['mia', 'Mia'], 'Mera': ['mera'], 'Rouge,': ['Rouge,', 'rouge,'], 'Pianista': ['pianista'], "Sull'oceano": ["sull'oceano"], 'Rennt': ['rennt'], 'Cons,': ['cons,'], 'Du': ['du', 'Du'], 'Pont-neuf,': ['Pont-Neuf,'], "D'automne": ["d'automne"], 'Quatre': ['quatre'], 'Cents': ['cents'], 'Coups': ['coups'], 'Et': ['et', 'Et'], 'Ricordo,': ['ricordo,'], 'Sì,': ['sì,'], 'Io': ['io', 'Io'], 'Ricordo': ['ricordo'], 'Aka': ['aka'], 'Do-right': ['Do-Right'], 'Macka,': ['macka,'], 'Beli': ['beli'], 'Macor': ['macor'], 'Monogatari': ['monogatari'], 'Ying': ['Ying', 'ying'], 'Gai': ['gai'], 'Wak': ['wak'], 'Hu': ['hu'], 'Macleane': ['MaCleane'], 'Nave': ['nave'], 'Va': ['va'], 'Paradis': ['paradis'], "'em": ["'Em"], 'Kuen': ['kuen'], 'Pugno': ['pugno'], 'Dollari': ['dollari'], 'Donkey-boy': ['Donkey-Boy'], 'Homme': ['Homme', 'homme'], 'Femme': ['Femme', 'femme'], 'Liang': ['liang'], 'Liebster': ['liebster'], 'Re-animator': ['Re-Animator'], 'Feu,': ['feu,'], 'Al': ['al'], 'Borde': ['borde'], 'Ataque': ['ataque'], 'Nervios': ['nervios'], 'Man-in-the-moon': ['Man-in-the-Moon'], 'Sobre': ['sobre'], 'Madre': ['madre'], 'Biciclette': ['biciclette'], 'Mccabe': ['McCabe'], 'Hitch-hiker,': ['Hitch-Hiker,'], 'Grande': ['grande', 'Grande'], 'Illusion': ['Illusion', 'illusion'], 'Ke': ['ke'], 'Ci': ['ci'], 'Qin': ['qin'], 'Topsy-turvy': ['Topsy-Turvy'], 'It': ['It', 'it'], 'Haben': ['haben'], 'Klein': ['klein'], 'Angefangen': ['angefangen'], 'Maschera': ['maschera'], 'Demonio': ['demonio'], 'Onna': ['onna'], 'Cuba/ya': ['Cuba/Ya'], 'Hard-boiled': ['Hard-Boiled'], 'Sau': ['sau'], 'Taam': ['taam'], 'Arrivé': ['arrivé'], 'Près': ['près'], 'Chez': ['Chez', 'chez'], 'Vous': ['vous'], 'Ge': ['ge'], 'Dou': ['dou', 'Dou'], 'Bu': ['bu'], 'Neng': ['neng'], 'Shao': ['Shao', 'shao'], 'Sidste': ['sidste'], 'Sang': ['sang'], 'East-west': ['East-West'], 'Jfk': ['JFK'], 'She-devil': ['She-Devil'], 'R.n.': ['R.N.'], 'Many-splendored': ['Many-Splendored'], '...and': ['...And'], 'Khoda': ['khoda'], 'Is': ['is', 'Is'], 'Toit': ['toit'], 'Ni': ['Ni', 'ni'], 'Loi': ['loi'], 'Blow-out': ['Blow-Out'], 'Bouffe': ['bouffe'], 'Qualche': ['qualche'], 'Dollaro': ['dollaro'], 'Più': ['più'], 'A.e.': ['A.E.'], 'Lengua': ['lengua'], 'Las': ['Las', 'las'], 'Mariposas': ['mariposas'], 'F/x': ['F/X'], 'F/x2': ['F/X2'], 'X-m': ['X-M'], 'Blow-up': ['Blow-Up'], 'X-men': ['X-Men'], 'H.o.t.s.': ['H.O.T.S.'], 'Historia': ['historia'], 'Oficial': ['oficial'], 'Pont,': ['pont,'], 'Volti': ['volti'], 'Della': ['della'], 'Paura,': ['paura,'], 'Créa': ['créa'], 'Ss': ['SS'], 'Pornographique,': ['pornographique,'], 'Demented': ['DeMented'], 'Ni-sen': ['ni-sen'], 'Mireniamu': ['mireniamu'], 'Weiter': ['weiter'], 'So': ['so', 'So'], 'Nah!': ['nah!'], 'Tu': ['tu'], 'Vivrai': ['vivrai'], 'Nel': ['nel'], 'Terrore': ['terrore'], 'Cang': ['cang'], 'Sajeong': ['sajeong'], 'Bol': ['bol'], 'Geot': ['geot'], 'Eobtda': ['eobtda'], 'Im': ['Im', 'im'], 'Ami': ['ami'], 'Qui': ['qui'], 'Veut': ['veut'], 'Bien': ['bien'], 'Yeung': ['yeung'], 'Nin': ['nin'], 'Wa': ['wa'], 'Goût': ['goût'], 'Autres': ['autres'], 'C.h.u.d.': ['C.H.U.D.'], 'Glaneurs': ['glaneurs'], 'Glaneuse': ['glaneuse'], "Mccool's": ["McCool's"], 'Erobreren': ['erobreren'], 'Rififi': ['Rififi', 'rififi'], 'Les': ['les', 'Les'], 'Hommes': ['hommes'], "L'enfance": ["l'enfance"], "D'un": ["d'un"], 'Chef': ['Chef', 'chef'], "O'clock": ["O'Clock"], 'Pomáhat': ['pomáhat'], 'A.i.': ['A.I.'], 'Crazy/beautiful': ['Crazy/Beautiful'], 'Und': ['und'], 'Die': ['die', 'Die'], 'Pourpres,': ['pourpres,'], 'He': ['He', 'he'], 'Chieu': ['chieu'], 'Thang': ['thang'], 'Dung': ['Dung', 'dung'], "D'une": ["d'une"], 'Chambre,': ['chambre,'], 'X-ray': ['X-Ray'], 'Villa': ['villa', 'Villa'], 'Accanto': ['accanto'], 'Cimitero': ['cimitero'], 'Rop': ['rop'], 'Finzi-continis,': ['Finzi-Continis,'], 'Dei': ['dei'], 'Finzi-contini,': ['Finzi-Contini,'], 'Wu': ['Wu', 'wu'], 'Men': ['men', 'Men'], 'Shan': ['shan'], 'Guo': ['guo'], 'Jiang': ['jiang'], 'T-rex:': ['T-Rex:'], 'Pee-wee': ['Pee-Wee'], 'D.o.a.': ['D.O.A.'], 'All-american': ['All-American'], 'Tulipani': ['tulipani'], 'Uhf': ['UHF'], 'Def-con': ['Def-Con'], 'Aux': ['aux'], 'Lek': ['lek'], 'L.i.e.': ['L.I.E.'], 'Sicarios,': ['sicarios,'], 'Na': ['na'], 'Korze': ['korze'], 'Spacecamp': ['SpaceCamp'], 'Métro,': ['métro,'], 'Ji:': ['ji:'], 'K-pax': ['K-PAX'], 'Diablo,': ['diablo,'], 'Bout': ['bout'], 'Souffle': ['souffle'], 'Obscur': ['obscur'], 'Objet': ['objet'], 'Désir': ['désir'], 'U.s.a.': ['U.S.A.'], 'Destin': ['destin'], "D'amélie": ["d'Amélie"], 'Loups,': ['loups,'], 'Neibian': ['neibian'], 'Jidian': ['jidian'], 'Begyndere': ['begyndere'], 'Für': ['für'], 'Sich': ['sich'], 'M*a*s*h': ['M*A*S*H'], 'Mash': ['MASH'], 'One-eyed': ['One-Eyed'], 'Figlio,': ['figlio,'], 'Vos': ['vos'], 'Mouchoirs': ['mouchoirs'], 'Má': ['má'], 'Panenko': ['panenko'], 'Hantâ': ['hantâ'], 'Oncle': ['oncle', 'Oncle'], "D'amérique": ["d'Amérique"], 'Mamá': ['mamá'], 'También': ['también'], 'Chu': ['chu'], 'Ma': ['ma', 'Ma'], 'Pianiste': ['pianiste'], 'Città': ['città'], 'Aperta': ['aperta'], 'Reinas': ['reinas'], 'Z-boyz': ['Z-Boyz'], 'Coca-cola': ['Coca-Cola'], 'Spider-man': ['Spider-Man'], 'Duc,': ['duc,'], 'Zhuravli': ['zhuravli'], 'M.d.': ['M.D.'], 'Ya-ya': ['Ya-Ya'], 'Scooby-doo': ['Scooby-Doo'], 'Svet': ['svet'], 'Rabbit-proof': ['Rabbit-Proof'], 'Miib': ['MIIB'], 'Est': ['est'], 'El': ['El', 'el'], 'Sexo': ['sexo'], 'Bacio,': ['bacio,'], 'Xxx': ['xXx'], 'Från': ['från'], 'Andra': ['andra'], 'Våningen': ['våningen'], 'Mes': ['mes'], 'Lèvres': ['lèvres'], 'Pour': ['pour'], 'Chocolat': ['chocolat', 'Chocolat'], "J'ai": ["j'ai", "J'ai"], 'Tué': ['tué'], 'Mon': ['mon', 'Mon'], 'Feardotcom': ['FearDotCom'], 'Nous': ['nous'], 'Liberté': ['liberté'], 'Histoires': ['histoires'], 'Novia,': ['novia,'], 'Kamikakushi': ['kamikakushi'], 'Veggietales': ['VeggieTales'], 'Punch-drunk': ['Punch-Drunk'], 'Haka': ['haka'], 'Gritos': ['gritos'], 'Tiene': ['tiene'], 'Noche': ['noche', 'Noche'], 'Professionnel': ['professionnel'], 'Padre': ['Padre', 'padre'], 'Gloire': ['gloire'], 'Père': ['Père', 'père'], 'Mère,': ['mère,'], 'Con': ['Con', 'con'], 'Autres,': ['autres,'], 'För': ['för'], "D'o": ["d'O"], 'Sperduta': ['sperduta'], 'Parco,': ['parco,'], 'Fils': ['fils'], 'Cb4': ['CB4'], 'Toten': ['toten'], 'Folie...': ['folie...'], 'Tout': ['tout'], 'Two-lane': ['Two-Lane'], 'Dalle': ['dalle'], 'Finestre': ['finestre'], 'Ridono,': ['ridono,'], 'Är': ['är'], 'Nyfiken': ['nyfiken'], 'Film': ['Film', 'film'], 'I': ['i', 'I'], 'Gult': ['gult'], 'Dysfunktional': ['DysFunktional'], 'Vailla': ['vailla'], 'Menneisyyttä': ['menneisyyttä'], '4-ever': ['4-ever', '4-Ever'], 'Migrateur,': ['migrateur,'], 'Lygter': ['lygter'], 'Mcguire': ['McGuire'], 'Train,': ['train,'], 'Shiro': ['shiro'], 'O.k.': ['O.K.'], 'Espagnole': ['espagnole'], 'Heng': ['heng'], 'Hai': ['hai', 'Hai'], 'Coupable': ['coupable'], 'Idéal': ['idéal'], 'Bianco,': ['bianco,'], 'Are': ['are', 'Are'], 'S': ['s', 'S'], 'Kino-apparatom': ['kino-apparatom'], 'Époque': ['époque'], 'Jik': ['jik'], 'Sat': ['sat'], 'Essen': ['essen'], 'Auf': ['auf', 'Auf'], 'Lxg': ['LXG'], '3-d:': ['3-D:'], 'Sol,': ['sol,'], 'S.w.a.t.': ['S.W.A.T.'], 'Secondo': ['secondo'], 'Juk': ['juk'], 'Kau': ['kau'], 'Inconnu:': ['inconnu:'], 'Incomplet': ['incomplet'], 'Divers': ['divers'], 'Voyages': ['voyages'], 'Vert,': ['vert,'], 'Thx': ['THX'], 'Discret': ['discret'], 'Bourgeoisie,': ['Bourgeoisie,', 'bourgeoisie,'], 'Os': ['OS'], 'Noticias': ['noticias'], 'Joyû': ['joyû'], 'Yi': ['Yi', 'yi'], 'Dong': ['dong'], 'Keung': ['keung'], 'Tsi': ['tsi'], 'Sam:': ['sam:'], 'Tsangba': ['tsangba'], 'Triplettes': ['triplettes'], 'Règle': ['règle'], 'Jeu': ['jeu'], 'Gæstebud': ['gæstebud'], 'Pcu': ['PCU'], 'Smotri': ['smotri'], 'Dimanche': ['dimanche'], 'À': ['À', 'à'], 'Campagne': ['campagne'], 'Ninpûchô': ['ninpûchô'], 'W': ['W', 'w'], 'Wodzie': ['wodzie'], 'Gwai': ['gwai'], 'Gui': ['gui'], 'Invasions': ['invasions'], 'Barbares': ['barbares'], 'Wargames': ['WarGames'], 'Interdits': ['interdits'], "D'arc,": ["d'Arc,"], 'Ben-hur:': ['Ben-Hur:'], 'Tango': ['Tango', 'tango'], 'Rowaiaru': ['rowaiaru'], 'O': ['O', 'o'], 'Giornate': ['giornate'], 'Matin': ['matin'], 'Sa': ['sa'], 'Vie:': ['vie:'], 'Douze': ['douze'], 'Tableaux': ['tableaux'], 'Belle': ['Belle', 'belle'], 'Bête': ['bête'], 'Degli': ['degli'], 'Spiriti': ['spiriti'], "L'année": ["L'Année"], 'Dernière': ['dernière'], 'Tani': ['tani'], 'Zu': ['zu'], 'Rosso': ['Rosso', 'rosso'], 'Diaboliques': ['diaboliques'], 'Volés': ['volés'], 'Mcnamara,': ['McNamara,'], 'Diament': ['diament'], 'Fleurs': ['fleurs'], 'Eurotrip': ['EuroTrip'], 'Bye,': ['Bye,', 'bye,'], 'Non': ['non'], 'Paura': ['paura'], 'Ur': ['ur'], 'Ett': ['ett'], 'Äktenskap': ['äktenskap'], 'Fail-safe': ['Fail-Safe'], 'Hikari': ['hikari'], 'Van': ['van', 'Van'], 'Peur,': ['peur,'], 'Fou': ['fou'], 'Jô': ['jô'], 'Meglio': ['meglio'], 'Gioventù': ['gioventù'], 'Tie': ['tie', 'Tie'], 'Sai-yuk,': ['Sai-Yuk,'], 'Ken': ['Ken', 'ken'], 'Bi': ['Bi', 'bi'], 'Quan': ['quan'], 'Po': ['po'], 'Zi': ['zi'], 'Sf:': ['SF:'], 'Tenshi': ['tenshi'], 'Papers,the': ['Papers,The'], 'Inu': ['inu'], 'San-akunin': ['san-akunin'], 'Jigoku': ['jigoku'], 'Mot': ['mot'], 'Ansikte': ['ansikte', 'Ansikte'], 'Spegel': ['spegel'], 'Leende': ['leende'], 'Med': ['med'], "'n'": ["'n'", "'N'"], 'Natsu': ['natsu'], 'Yeoreum': ['yeoreum'], 'Gaeul': ['gaeul'], 'Gyeoul': ['gyeoul'], 'Geurigo': ['geurigo'], 'Bom': ['Bom', 'bom'], 'Mizu': ['mizu'], 'Soko': ['soko'], 'Kara': ['kara'], 'Spiser': ['spiser'], 'Hunde': ['hunde'], 'Séduction,': ['séduction,'], 'Revoir': ['revoir'], 'Jin-rô': ['Jin-Rô'], 'Not': ['not', 'Not'], 'Included': ['included'], 'Dayû': ['dayû'], 'Dans': ['Dans', 'dans'], 'Métro': ['métro'], 'Sansei:': ['sansei:'], 'Temps': ['temps'], 'Loup': ['loup'], 'Joken': ['joken'], 'Frères': ['frères'], 'De-lovely': ['De-Lovely'], 'Prophétie': ['prophétie'], "D'ailes": ["d'ailes"], 'Papillon,': ['papillon,'], 'Exterminador,': ['exterminador,'], 'Eres': ['eres'], 'Gracia': ['gracia'], 'Zabijaniu': ['zabijaniu'], 'Condamné': ['condamné'], 'Mort': ['mort', 'Mort'], "S'est": ["s'est"], 'Échappé': ['échappé'], 'Vent': ['vent'], 'Où': ['où'], 'Slaughterhouse-five': ['Slaughterhouse-Five'], 'Bobby-soxer,': ['Bobby-Soxer,'], 'Set-up,': ['Set-Up,'], 'Avp:': ['AVP:'], 'Yu-gi-oh!': ['Yu-Gi-Oh!'], 'Superbabies:': ['SuperBabies:'], 'Motocicleta': ['motocicleta'], 'Benspænd,': ['benspænd,'], "L'empire": ["l'empire"], 'Américain,': ['américain,'], 'Mala': ['Mala', 'mala'], 'Educación': ['educación'], 'Spongebob': ['SpongeBob'], 'Squarepants': ['SquarePants'], 'Mian': ['mian'], 'Mai': ['mai'], 'Fu': ['fu', 'Fu'], 'D.a.r.y.l.': ['D.A.R.Y.L.'], "D'enfants": ["d'enfants"], 'Wie': ['wie'], 'Er': ['er'], 'Kam,': ['kam,'], 'Andalou,': ['andalou,'], "D'or,": ["d'Or,"], 'Miru': ['miru'], 'Ehon': ['ehon'], 'Mita': ['mita'], 'Keredo': ['keredo'], 'Dag': ['dag'], 'Brouillard': ['brouillard'], 'Kettô': ['kettô'], 'Sotilas': ['sotilas'], 'Tategoto': ['tategoto'], 'Kanketsuhen:': ['kanketsuhen:'], 'Daikaijû': ['daikaijû'], 'Rivière': ['rivière'], 'Hibou': ['hibou'], 'Or,': ['or,'], 'Battaglia': ['battaglia'], 'Nome': ['nome'], 'Liberté,': ['liberté,'], 'Sagrada,': ['sagrada,'], 'Cousine': ['cousine'], "D'adèle": ["d'Adèle"], 'Reporter': ['Reporter', 'reporter'], 'Diu': ['diu'], 'In-laws,': ['In-Laws,'], "'round": ["'Round"], 'Hung': ['Hung', 'hung'], 'Boon': ['boon'], 'Sik': ['sik'], 'Deseo,': ['deseo,'], 'Yauwan': ['yauwan'], 'Z': ['Z', 'z'], 'Takkyûbin': ['takkyûbin'], 'Cry-baby': ['Cry-Baby'], 'Keisatsu': ['keisatsu'], 'Patorebâ:': ['patorebâ:'], 'Riki-oh:': ['Riki-Oh:'], 'Buta': ['buta'], 'Guan': ['guan'], 'Cheerleader-murdering': ['Cheerleader-Murdering'], 'Einer': ['einer'], 'Bao': ['bao'], 'Biao': ['biao'], 'Wo': ['Wo', 'wo'], 'Sumaseba': ['sumaseba'], 'Shei': ['shei'], 'Seiki': ['seiki'], 'Air/magokoro': ['Air/Magokoro'], 'Wo,': ['wo,'], 'Kimi': ['kimi'], 'Sorcière': ['sorcière'], 'Ra': ['ra'], 'Khahad': ['khahad'], 'Bord': ['bord'], 'Gyeongbi': ['gyeongbi'], 'Guyeok': ['guyeok'], 'Jsa': ['JSA'], 'Geunyeo': ['geunyeo'], 'Naui': ['naui'], 'Saakuru': ['saakuru'], 'Pourpres': ['pourpres'], 'Anges': ['anges'], "L'apocalypse,": ["l'apocalypse,"], 'Into': ['Into', 'into'], 'Fiançailles': ['fiançailles'], 'Rak': ['rak'], 'Noi': ['noi'], 'Nid': ['nid'], 'Mahasan': ['mahasan'], 'Head-on': ['Head-On'], 'Ongaeshi': ['ongaeshi'], "'salem's": ["'Salem's"], 'Trop': ['trop'], 'Intimes': ['intimes'], 'Partido,': ['partido,'], 'Ari': ['ari'], 'Ong-bak:': ['Ong-Bak:'], 'Adentro': ['adentro'], 'Himmelen': ['himmelen'], 'Hwinalrimyeo': ['hwinalrimyeo'], 'Dig!': ['DiG!'], "'i'm": ["'I'm"], 'Kyôfu': ['kyôfu'], 'Dai-gekijô:': ['dai-gekijô:'], 'Donne': ['donne'], 'Per': ['per', 'Per'], "L'assassino": ["l'assassino"], '3-iron': ['3-Iron'], 'Chueok': ['chueok'], 'Weiße': ['weiße'], "O'shea": ["O'Shea"], 'Shiranai': ['shiranai'], 'Von': ['von', 'Von'], 'Bitteren': ['bitteren'], 'Ugoku': ['ugoku'], 'Winn-dixie': ['Winn-Dixie'], 'Dozor': ['dozor'], 'Seven-per-cent': ['Seven-Per-Cent'], 'Conjugal': ['conjugal'], 'Anno': ['anno'], 'Zero': ['zero', 'Zero'], 'Vs': ['vs', 'VS'], 'Grym': ['grym'], 'Tôge': ['tôge'], 'Tanuki': ['tanuki'], 'Gassen': ['gassen'], 'Pompoko': ['pompoko'], 'De...': ['de...'], 'Image': ['image'], 'Fiore': ['fiore'], 'Mille': ['mille'], 'Notte': ['notte', 'Notte'], 'Chagrin': ['chagrin'], 'Pitié': ['pitié'], 'Detstvo': ['detstvo'], 'Lune,': ['lune,'], 'Tinieblas': ['tinieblas'], 'Napola': ['NaPolA'], 'Den': ['Den', 'den'], 'Xxx:': ['xXx:'], 'Monster-in-law': ['Monster-in-Law'], 'Namja': ['namja'], '3-d,': ['3-D,'], 'Tension': ['Tension', 'tension'], 'Inocentes': ['inocentes'], 'Gaang': ['gaang'], 'Sind': ['sind'], 'Vorbei': ['vorbei'], "L'empereur,": ["l'empereur,"], 'Poupées': ['poupées'], 'Russes': ['russes'], '40-year-old': ['40-Year-Old'], 'Cry_wolf': ['Cry_Wolf'], 'Mirrormask': ['MirrorMask'], 'Were-rabbit': ['Were-Rabbit'], 'C.s.a.:': ['C.S.A.:'], 'Cudo': ['cudo'], 'Fuite,': ['fuite,'], 'Tyttö': ['tyttö'], 'One-way': ['One-Way'], 'Tasca,': ['tasca,'], 'C.r.a.z.y.': ['C.R.A.Z.Y.'], 'Geumjassi': ['geumjassi'], 'Bloodrayne': ['BloodRayne'], 'Zabutykh': ['zabutykh'], 'Predkiv': ['predkiv'], 'Li': ['li'], 'Zou': ['zou'], 'Dan': ['Dan', 'dan'], 'Qi': ['qi'], "'a'": ["'A'"], 'Waak': ['waak'], 'Letzten': ['letzten'], 'Mcphee': ['McPhee'], 'Valot': ['valot'], 'Leben': ['leben'], 'Seishun': ['seishun'], 'Ist': ['ist'], 'Es': ['es'], 'Scheint': ['scheint'], 'Yum': ['yum'], 'Goong': ['goong'], 'Rv': ['RV'], 'X-men:': ['X-Men:'], 'Break-up,': ['Break-Up,'], 'Ex-girlfriend': ['Ex-Girlfriend'], 'Putain,': ['putain,'], 'Oh': ['OH', 'Oh'], 'Ombres': ['ombres'], 'Than': ['Than', 'than'], 'Coeur': ['coeur'], 'Æbler': ['æbler'], 'Sherrybaby': ['SherryBaby'], 'Tigre': ['tigre'], 'Neve': ['neve'], 'Science': ['science', 'Science'], 'Rêves': ['rêves'], 'Siebente': ['siebente'], 'Viii,': ['VIII,'], 'Fauno,': ['fauno,'], 'G.o.r.a.': ['G.O.R.A.'], 'Desierto': ['desierto'], 'Cheng': ['cheng'], 'Jin': ['Jin', 'jin'], 'Dai': ['dai'], 'Huang': ['huang', 'Huang'], 'Jia': ['Jia', 'jia'], 'Mannen,': ['mannen,'], 'Brylluppet': ['brylluppet'], 'Det': ['Det', 'det'], 'Hele': ['hele'], "T'aime": ["t'aime"], 'Loudquietloud:': ['loudQUIETloud:'], 'Liu': ['liu'], 'Fang': ['fang', 'Fang'], 'Racconti': ['racconti'], 'Prix': ['prix'], 'Tmnt': ['TMNT'], 'Maledetto': ['maledetto'], 'Treno': ['treno'], 'Blindato': ['blindato'], 'Yeoin': ['yeoin'], 'Meilleur': ['meilleur'], 'Dis': ['dis'], 'Personne': ['personne'], 'Sen': ['Sen', 'sen'], 'Fost': ['fost'], 'N-a': ['n-a'], 'Fost?': ['fost?'], 'Luni,': ['luni,'], 'Saptamâni': ['saptamâni'], 'Zile': ['zile'], 'Kinkurîto': ['kinkurîto'], 'Anderen': ['Anderen', 'anderen'], 'Xxy': ['XXY'], 'Avpr:': ['AVPR:'], 'Cheiro': ['cheiro'], 'P.s.': ['P.S.'], 'D-war': ['D-War'], 'Ha-tizmoret': ['Ha-Tizmoret'], '[rec]': ['[REC]'], 'Kakeru': ['kakeru'], 'Shôjo': ['shôjo', 'Shôjo'], 'Banat': ['banat'], 'Å': ['å'], 'Tenke': ['tenke'], 'Negativt': ['negativt'], 'Semi-pro': ['Semi-Pro'], 'Bc': ['BC'], 'Dos': ['dos'], 'Luna,': ['luna,', 'Luna,'], "L'intérieur": ["l'intérieur"], 'Happy-go-lucky': ['Happy-Go-Lucky'], 'Young@heart': ['Young@Heart'], 'Das': ['das', 'Das'], 'Contra': ['contra'], 'Wall·e': ['WALL·E'], 'Ypf': ['YPF'], 'Aki': ['aki'], 'Ciudad': ['ciudad'], 'Rätte': ['rätte'], 'Komma': ['komma'], 'A.d.': ['A.D.'], 'Darkbluealmostblack': ['DarkBlueAlmostBlack'], 'Flcl': ['FLCL'], 'Mukau': ['mukau'], 'Ubaguruma': ['ubaguruma'], 'Rocknrolla': ['RocknRolla'], 'Murs': ['murs'], "'a": ["'A"], 'Mir': ['Mir', 'mir'], 'Frost/nixon': ['Frost/Nixon'], 'Hadan': ['hadan'], 'Longtemps': ['longtemps'], 'Nui': ['nui'], 'Yau': ['yau'], 'Senchimêtoru': ['senchimêtoru'], 'Ofrivilliga': ['ofrivilliga'], 'Ue': ['ue'], 'Nabbeunnom': ['nabbeunnom'], 'Isanghannom': ['isanghannom'], 'Rock-a-doodle': ['Rock-A-Doodle'], 'Sing-along': ['Sing-Along'], 'Ong-bak': ['Ong-Bak'], 'Hatar': ['hatar'], 'Kvinnor': ['kvinnor'], 'Baiser': ['baiser'], "S'il": ["s'il"], 'Plait': ['plait'], 'Shinsei': ['shinsei'], 'Hagane': ['hagane'], 'Renkinjutsushi:': ['renkinjutsushi:'], 'Yuku': ['yuku'], 'Mono': ['mono'], "D'été,": ["d'été,"], 'Snø': ['snø'], 'Darakhatan': ['darakhatan'], 'Zeyton': ['zeyton'], 'Half-blood': ['Half-Blood'], "'neath": ["'Neath"], 'Shin': ['shin', 'Shin'], 'Gekijôban:': ['gekijôban:'], 'G-force': ['G-Force'], 'Silence': ['silence', 'Silence'], 'Cinéma': ['cinéma'], 'Petit': ['petit'], 'Coup': ['Coup', 'coup'], 'Quand': ['quand'], 'Lumière': ['lumière'], "S'éteint": ["s'éteint"], 'Commence': ['commence'], 'Sus': ['sus'], 'Padrone': ['padrone'], 'Aruitemo': ['Aruitemo', 'aruitemo'], 'A-haunting': ['A-Haunting'], 'Vj:': ['VJ:'], 'Lukket': ['lukket'], 'Land': ['land', 'Land'], 'Em': ['em'], 'Abrazos': ['abrazos'], 'Rotos': ['rotos'], 'Kapel': ['kapel'], 'Sprängdes': ['sprängdes'], 'Dragons': ['Dragons', 'dragons'], 'Ova': ['OVA'], 'Red-nosed': ['Red-Nosed'], 'Premier': ['premier'], 'Reste': ['reste'], 'Ta': ['ta'], 'Lekte': ['lekte'], 'Elden': ['elden'], 'Udachi': ['udachi'], 'Habitación': ['habitación'], 'Tire-larigot': ['tire-larigot'], 'Kick-ass': ['Kick-Ass'], 'Bis': ['Bis', 'bis'], 'Aufs': ['aufs'], 'Gequält': ['gequält'], 'Vuoro': ['vuoro'], 'Kapel,': ['kapel,'], '41-year-old': ['41-Year-Old'], 'A-team,': ['A-Team,'], 'Timer': ['TiMER'], 'Siège': ['siège'], "'star": ["'Star"], 'Noorderlingen': ['noorderlingen'], 'Bôru': ['bôru'], 'Kaese': ['kaese'], 'Gasland': ['GasLand'], "Ga'hoole": ["Ga'Hoole"], 'Kälter': ['kälter'], 'Als': ['als'], 'Jours': ['jours'], 'Talion': ['talion'], "'superman'": ["'Superman'"], 'Vii': ['VII'], 'Guerrieri': ['guerrieri'], 'Conforme': ['conforme'], 'Prima': ['prima'], 'Cosa': ['cosa'], 'Boatda': ['boatda'], 'Triste': ['triste'], 'Trompeta': ['trompeta'], 'Flowers': ['Flowers', 'flowers'], 'Fougère': ['fougère'], 'All-star': ['All-Star'], 'Wôzu': ['wôzu'], 'Burn-e': ['BURN-E'], 'Shikaku': ['shikaku'], 'C.k.:': ['C.K.:'], 'Socialisme': ['socialisme'], 'Gamin': ['gamin'], 'Vélo': ['vélo'], 'Sôshingeki': ['sôshingeki'], 'Change-up,': ['Change-Up,'], 'Piel': ['piel'], 'Habito': ['habito'], 'Take-out': ['Take-Out'], 'Take-away': ['Take-Away'], 'Cuento': ['cuento'], 'Chino': ['chino'], 'Az': ['az'], 'Mole-men': ['Mole-Men'], 'August': ['august', 'August'], 'Shôshitsu': ['shôshitsu'], 'Five-year': ['Five-Year'], 'M.iii.b.': ['M.III.B.'], 'M.i.b.³': ['M.I.B.³'], "D'artifice": ["d'artifice"], 'Bôru:': ['bôru:'], 'Nemuri': ['nemuri'], 'Hime': ['hime'], 'Yo': ['yo'], 'Ichiban': ['ichiban'], 'Tsuyoi': ['tsuyoi'], 'Yatsu': ['yatsu'], 'Marugoto': ['marugoto'], 'Chô': ['chô'], 'Kessen': ['kessen'], 'Jack-jack': ['Jack-Jack'], 'Pawâ': ['pawâ'], 'Senshi': ['senshi'], 'Saikyô': ['saikyô', 'Saikyô'], 'Retsusen-chô': ['retsusen-chô'], 'Gekisen': ['gekisen'], 'Spider-man,': ['Spider-Man,'], 'Mary-kate': ['Mary-Kate'], 'Usa': ['USA'], 'Bio-broly': ['Bio-Broly'], 'Gekiha!': ['gekiha!'], 'Ore': ['ore'], 'Fyushon!!': ['fyushon!!'], 'Bakuhatsu!!': ['bakuhatsu!!'], 'Ga': ['ga'], 'Yaraneba': ['yaraneba'], 'Dare': ['Dare', 'dare'], 'Yaru': ['yaru'], 'Hitori': ['hitori'], 'Saishuu': ['saishuu'], 'Itonda': ['itonda'], 'Chichi': ['chichi'], 'Hankô!!': ['hankô!!'], 'Gt:': ['GT:'], 'Gaiden!': ['gaiden!'], 'Akashi': ['akashi'], 'Sû-shin-chû': ['sû-shin-chû'], 'Paranorman': ['ParaNorman'], '3dd': ['3DD'], 'Dd': ['DD'], 'V/h/s': ['V/H/S'], 'Affære,': ['affære,'], 'Kon-tiki': ['Kon-Tiki'], 'Shakespeare-wallah': ['Shakespeare-Wallah'], "'hellboy':": ["'Hellboy':"], 'Wreck-it': ['Wreck-It'], 'Capital': ['Capital', 'capital'], 'Tueurs': ['tueurs'], 'Deve': ['deve'], 'Morire': ['morire'], 'Jiao': ['jiao'], 'Zhu': ['zhu'], 'Se': ['se', 'Se'], 'Fue': ['fue'], 'Cielos': ['cielos'], 'Ha-sippur': ['Ha-Sippur'], 'Ao': ['ao'], 'Redor': ['redor'], 'Role/play': ['Role/Play'], 'Sova': ['sova'], 'Dö': ['dö'], 'Tpb': ['TPB'], 'Afk:': ['AFK:'], 'Kodomo': ['kodomo'], 'Ame': ['ame'], 'Yuki': ['yuki'], 'Menyaet': ['menyaet'], 'Professiyu': ['professiyu'], 'Passé': ['passé'], 'Offerta,': ['offerta,'], 'R.i.p.d.': ['R.I.P.D.'], 'Tachinu': ['tachinu'], 'Kenka-tabi': ['kenka-tabi'], 'Plennitsa': ['plennitsa'], 'Eiens': ['eiens'], 'Viel': ['viel'], 'Kurzen': ['kurzen'], 'Superhero': ['Superhero', 'superhero'], 'Naru': ['naru'], 'Ball': ['Ball', 'ball'], 'Michi': ['michi'], "'the": ["'The"], 'Fil': ['fil'], 'Mismo': ['mismo'], 'Amor,': ['amor,'], 'Misma': ['Misma', 'misma'], 'Lluvia': ['lluvia'], 'Ming': ['ming'], 'Fourrure': ['fourrure'], 'Viaje': ['viaje'], 'Non-stop': ['Non-Stop'], 'Bäst!': ['bäst!'], 'Klev': ['klev'], 'Ut': ['ut'], 'Genom': ['genom'], 'Fönstret': ['fönstret'], 'Försvann': ['försvann'], 'Kyôten': ['kyôten'], 'Isten': ['isten'], 'Hundred-foot': ['Hundred-Foot'], 'Jours,': ['jours,'], 'Nuit': ['nuit', 'Nuit'], 'Ssadis': ['SSadis'], 'Dor': ['dor'], 'Lei': ['lei'], 'Ah': ['ah'], 'Yut': ['yut'], 'Ant-man': ['Ant-Man'], 'Duff': ['DUFF'], "'y'": ["'Y'"], 'Mcfarland,': ['McFarland,'], 'V': ['V', 'v'], 'Xxl': ['XXL'], 'U.n.c.l.e.': ['U.N.C.L.E.'], 'Vals': ['Vals', 'vals'], 'Inútiles': ['inútiles'], 'Long-term': ['Long-Term'], '3-day': ['3-Day'], 'Faqs': ['FAQs'], 'Straight-jacket': ['Straight-Jacket'], 'İtirazım': ['İtirazım'], 'A.r.o.g.': ['A.R.O.G.'], 'Somm:': ['SOMM:'], 'Egg-scapade': ['Egg-Scapade'], 'Jt': ['JT'], 'Leroy': ['LeRoy'], 'Xv': ['XV']}

        for i in range(len(words_in_title)):
            if re.match('\(.+', words_in_title[i]) is None:
                standard_capitalized = words_in_title[i].lower().capitalize()
            else:
                # eg. word = '(Guerre'
                standard_capitalized = '(' + words_in_title[i][1:].lower().capitalize()

            # if this word is capitalized in a standard way across whole db, append it to the end of each possible title
            if (standard_capitalized not in non_standard) and \
                    (standard_capitalized + ':' not in non_standard) and \
                    (standard_capitalized + ',' not in non_standard) and \
                    (standard_capitalized + '...' not in non_standard) and \
                    (standard_capitalized + '!' not in non_standard):
                for j in range(len(capitalized_titles)):
                    capitalized_titles[j] += standard_capitalized + ' '

            else:
                spellings_list = []
                if standard_capitalized in non_standard:
                    spellings_list = non_standard[standard_capitalized]
                elif standard_capitalized + '...' in non_standard:
                    spellings_list = non_standard[standard_capitalized + '...']
                elif standard_capitalized + '!' in non_standard:
                    spellings_list = non_standard[standard_capitalized + ':']
                elif standard_capitalized + ':' in non_standard:
                    spellings_list = non_standard[standard_capitalized + ':']
                elif standard_capitalized + ',' in non_standard:
                    spellings_list = non_standard[standard_capitalized + ',']

                # capitalization of word in db is non-standardized so need to account for all possible spellings of it
                current_titles = len(capitalized_titles)
                num_spellings = len(spellings_list)

                # make enough copies of the current strings to make permutations with different spellings
                for j in range(current_titles):
                    for k in range(num_spellings - 1):
                        capitalized_titles.append(capitalized_titles[j])
                # append each spelling to the end of possible permutation
                for g in range(num_spellings):
                    for k in range(current_titles):
                        if re.match(".+,", spellings_list[g]) is None:
                            capitalized_titles[g * current_titles + k] += spellings_list[g] + ' '
                        else:
                            word = spellings_list[g][:-1]
                            # just changed this because of "Anglaise et le duc, L'"
                            capitalized_titles[g * current_titles + k] += word + '[,]* '
        # last space needs to be removed for all the permutations
        pos_titles = []
        for s in capitalized_titles:
            pos_titles.append(s[:-1])
        return pos_titles
    
    def handle_articles(self, article_idx, words_in_title, relist):
        idx = article_idx[0]
        for count in range(len(article_idx) - 1):
            # if there's another alternate / foreign title coming up that uses article
            # if count + 1 < len(article_idx):
            if count == 0:
                for j in range(idx + 1, article_idx[count + 1]):
                    if j == article_idx[count + 1] - 1:
                        relist.append(words_in_title[j] + ',')
                    else:
                        relist.append(words_in_title[j])
                relist.append(words_in_title[idx])
            elif count > 0:
                for j in range(idx + 1, article_idx[count + 1]):
                    if j == idx + 1:
                        relist.append('(' + words_in_title[j])
                    else:
                        relist.append(words_in_title[j])
                    if j == article_idx[count + 1] - 1:
                        relist.append(words_in_title[j][:-1] + ',')
                relist.append(words_in_title[idx][1:] + ')')
            idx = article_idx[count + 1]

        # if there's a year attached to user input:
        if re.match("\([\d]+\)", words_in_title[-1]) is not None and len(article_idx) == 1:
            for j in range(idx + 1, len(words_in_title) - 1):
                if j == len(words_in_title) - 2:
                    relist.append(words_in_title[j] + ',')
                else:
                    relist.append(words_in_title[j])
            relist.append(words_in_title[idx])
            relist.append(words_in_title[-1])

        elif re.match("\([\d]+\)", words_in_title[-1]) is None and len(article_idx) == 1:
            for j in range(idx + 1, len(words_in_title)):
                if j == len(words_in_title) - 1:
                    relist.append(words_in_title[j] + ',')
                else:
                    relist.append(words_in_title[j])
            relist.append(words_in_title[idx])

        elif re.match("\([\d]+\)", words_in_title[-1]) is not None and len(article_idx) > 1:
            for j in range(idx + 1, len(words_in_title) - 1):
                if j == idx + 1 and j != len(words_in_title) - 2:
                    relist.append('(' + words_in_title[j])
                elif j == len(words_in_title) - 2:
                    relist.append(words_in_title[j][:-1] + ',')
                elif j != idx + 1:
                    relist.append(words_in_title[j])
            relist.append(words_in_title[idx][1:] + ')')
            relist.append(words_in_title[-1])

        elif re.match("\([\d]+\)", words_in_title[-1]) is None and len(article_idx) > 1:
            for j in range(idx + 1, len(words_in_title)):
                if j == idx + 1 and j != len(words_in_title) - 1:
                    relist.append('(' + words_in_title[j])
                elif j == len(words_in_title) - 1:
                    relist.append(words_in_title[j][:-1] + ',')
                else:
                    relist.append(words_in_title[j])
            relist.append(words_in_title[idx][1:] + ')')
        return relist

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
        patterns = []
        words_in_title = title.split()
        pos_titles = self.handle_capitalization(words_in_title)

        pos_titles.append(title)
        for title in pos_titles:
            words_in_title = title.split()
            # add valid regex patterns to list
            if re.match("\([\d]+\)", words_in_title[-1]) is None:
                patterns.append('^' + title + " ([\d]+)")
                if self.creative:
                    # eg matches input to "Scream 2" but not "Screamers"
                    patterns.append('^' + title + "[: ].*([\d]+)")
                    # creative mode: alternate film titles (- [ ] "Seven (a.k.a. Se7en) (1995)" should accept "Se7en"
                    patterns.append('.+ ' + '(' + title + ')' + '.+')
                    patterns.append('.+ ' + '(a\.k\.a\. ' + title + ')' + '.+')
                    patterns.append('.+ ' + '(aka ' + title + ')' + '.+')
            else:
                # if there is a year already specified in the back of the title
                patterns.append('^' + title)
                if self.creative:
                    # account for all possible alternate film titles
                    # for instance, "Seven (a.k.a. Se7en) (1995)" is in db, so we should accept "Se7en (1995)"
                    title_without_year = ""
                    for i in range(len(words_in_title) - 2):
                        title_without_year += words_in_title[i] + ' '
                    title_without_year += words_in_title[-2]
                    year = words_in_title[-1]
                    patterns.append('^' + title_without_year + '.*' + year)
                    patterns.append('.+ ' + '(' + title_without_year + ')' + '.+' + year)
                    patterns.append('.+ ' + '(a\.k\.a\. ' + title_without_year + ')' + '.+' + year)
                    patterns.append('.+ ' + '(aka ' + title_without_year + ')' + '.+' + year)

            # handles article(s) for foreign and English language
            articles = ['La', 'la', 'Le', 'le', 'Les', 'les', 'Il', 'il', "L'", "l'", 'A', 'a', 'Die', 'die',
                           'Das', 'das', 'An', 'an', 'The', 'the', 'Der', 'der', 'Den', 'den', 'Dem', 'dem',
                        'Des', 'des', 'El', 'el', 'Los', 'los', 'Las', 'las', 'Lo', 'lo', 'Gli', 'gli']

            translations = title.split('(')
            article_idx = []
            idx = 0
            for translation in translations:
                words_in_translation = translation.split()
                if words_in_translation[0] in articles:
                    article_idx.append(idx)
                idx += len(words_in_translation)

            relist = []
            if article_idx != []:
                relist = self.handle_articles(article_idx, words_in_title, relist)
                restring = ""

                if (not self.creative) and re.match("\([\d]+\)", words_in_title[-1]) is None:
                    for i in range(len(relist) - 1):
                        restring += relist[i] + ' '
                    restring += relist[-1]
                    patterns.append('^' + restring + ' ([\d]+)')

                # An American in Paris (1951)
                elif (not self.creative) and re.match("\([\d]+\)", words_in_title[-1]) is not None:
                    relist.append(words_in_title[-1])
                    for i in range(len(relist) - 1):
                        restring += relist[i] + ' '
                    restring += relist[-1]
                    patterns.append('^' + restring)

                # La Guerre de feu (1981)
                elif self.creative and re.match("\([\d]+\)", words_in_title[-1]) is not None:
                    for i in range(len(relist) - 1):
                        restring += relist[i] + ' '
                    patterns.append('^' + restring + '.*' + words_in_title[-1])
                    patterns.append('.* ' + restring + '.*' + words_in_title[-1])
                    patterns.append('.+ (' + restring + ') .*' + words_in_title[-1])

                # La Guerre de Feu
                elif self.creative and re.match("\([\d]+\)", words_in_title[-1]) is None:
                    for i in range(len(relist) - 1):
                        restring += relist[i] + ' '
                    restring += relist[-1]
                    patterns.append('^' + restring + ' .*([\d]+)')
                    patterns.append('.* ' + restring + ' .*([\d]+)')
                    patterns.append('.+ ' + '(' + restring + ' .*).*([\d]+)')


                # rearranging "An American in Paris (1951)" --> "American in Paris, An (1951)"
                rearranged_list = []
                # eg "La x de la y" --> "x de la y, La"
                if words_in_title[0] in articles:

                    if re.match("\([\d]+\)", words_in_title[-1]) is not None:
                        for i in range(1, len(words_in_title) - 2):
                            rearranged_list.append(words_in_title[i])
                        rearranged_list.append(words_in_title[len(words_in_title) - 2] + ',')
                        rearranged_list.append(words_in_title[0])
                    else:
                        for i in range(1, len(words_in_title) - 1):
                            rearranged_list.append(words_in_title[i])
                        rearranged_list.append(words_in_title[len(words_in_title) - 1] + ',')
                        rearranged_list.append(words_in_title[0])
                    # reconstructing the string
                    rearranged = ""
                    # "An American in Paris" --> "American in Paris, The" (starter)
                    if (not self.creative) and re.match("\([\d]+\)", words_in_title[-1]) is None:
                        for i in range(len(rearranged_list) - 1):
                            rearranged += rearranged_list[i] + ' '
                        rearranged += rearranged_list[-1]
                        patterns.append('^' + rearranged + ' ([\d]+)')

                    # An American in Paris (1951)
                    elif (not self.creative) and re.match("\([\d]+\)", words_in_title[-1]) is not None:
                        rearranged_list.append(words_in_title[-1])
                        for i in range(len(rearranged_list) - 1):
                            rearranged += rearranged_list[i] + ' '
                        rearranged += rearranged_list[-1]
                        patterns.append('^' + rearranged)

                    # La Guerre de feu (1981)
                    elif self.creative and re.match("\([\d]+\)", words_in_title[-1]) is not None:
                        for i in range(len(rearranged_list) - 1):
                            rearranged += rearranged_list[i] + ' '
                        rearranged += rearranged_list[-1]
                        patterns.append('^' + rearranged + ' .*' + words_in_title[-1])
                        patterns.append('.* ' + restring + '.*' + words_in_title[-1])
                        patterns.append('.+ (' + rearranged + ') .*' + words_in_title[-1])

                    # La Guerre de Feu
                    elif self.creative and re.match("\([\d]+\)", words_in_title[-1]) is None:
                        for i in range(len(rearranged_list) - 1):
                            rearranged += rearranged_list[i] + ' '
                        rearranged += rearranged_list[-1]
                        patterns.append('^' + rearranged + ' .*([\d]+)')
                        patterns.append('.* ' + rearranged + ' .*([\d]+)')
                        patterns.append('.+ ' + '(' + rearranged + '.*) .*([\d]+)')

        matches = []
        for pattern in patterns:
            regex = re.sub("\'", r"\'", pattern)
            # replace all the brackets with the regex equivalent
            regex = re.sub("\(", r"\(", regex)
            regex = re.sub("\)", r"\)", regex)

            for i in range(len(self.titles)):
                result = re.findall(regex, self.titles[i][0])
                if result != [] and i not in matches:
                    matches.append(i)

        return matches

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
        p = porter_stemmer.PorterStemmer()  # initialize porter stemmer to stem words
        tokens = preprocessed_input.split()  # extract words from input
        sent_rating = 0  # sentiment rating
        enthus_rating = 0  # enthusiasm rating
        enthus_terms = ['!', 'really', 'reeally', 'so', 'love', 'hate', 'despise', 'very', 'best', 'worst', 'absolutely', 'terrible', 'never', 'always', 'extremely']  # terms that convey strong sentiment
        
        # stem keys in dictionary
        keys = list(self.sentiment.keys())
        stemmed_keys = {}
        
        for key in keys:
            stemmed_key = p.stem(key)
            stemmed_keys[stemmed_key] = key  # map stemmed key to actual key

        # get sentiment for all tokens
        quote = False 
        for token in tokens:
            # token conveys enthusiasm (note we still consider tokens part of movie title in case there's punctuation after title)
            if any(enthus in token for enthus in enthus_terms):
                enthus_rating += 1

            # encountered part of title
            if '\"' in token:
                if '\"' == token[0] and '\"' in token[1:]:  # token contains start and end quotes
                    continue
                quote = not quote  # switch quote states
                continue
            
            # ignore words that are in the middle of a movie title
            if quote:
                continue

            # check if has NOT_ in front of it
            not_ = False
            if 'NOT_' in token:
                not_ = True
                token = token[4:]  # remove NOT_ part of string

            stemmed_token = p.stem(token.strip('.,!;:?'))  # stemmed token
            if stemmed_token in stemmed_keys:  # check if we have a sentiment for stemmed token
                key = stemmed_keys[stemmed_token]

                if self.sentiment[key] == 'neg':  # token has negative sentiment
                    if not_:  # we negate sentiment, so becomes positive
                        sent_rating += 1
                    else:
                        sent_rating -= 1
                else:  # token has positive sentiment
                    if not_:  # we negate sentiment, so becomes negative
                        sent_rating -= 1
                    else:
                        sent_rating += 1
        
        if sent_rating > 0:
            if enthus_rating > 0: # strong positive sentiment
                return 2
            return 1  # normal positive sentiment
        elif sent_rating < 0:
            if enthus_rating > 0:  # strong negative sentiment
                return -2
            return -1  # normal negative sentiment
        else:
            return 0  # neutral sentiment

    def find_verbs(self, preprocessed_input, movies):
        """Helper function for extract_sentiment_for_movies.

        Finds the number of verbs in the input.

        :param preprocessed_input: a user-supplied line of text that has been
        pre-processed with preprocess(); the list of movie titles
        :returns: the number of verbs & a list containing tuples where the first
        item of the tuple is the verb and the second item is the index it starts at
        in the input
        """
        verbs = ['like', 'hate', 'was', 'were', 'love', 'despise', 'dislike', 'enjoy', 'saw', 'watch','view', 'include', 'are', 'is']
        count = 0
        result = []
        modified_input = preprocessed_input

        # remove movie titles to not count verbs in title
        for movie in movies:
            start_quote = modified_input.index('\"')
            end_quote = modified_input.index('\"', start_quote + 1)
            modified_input = modified_input[:start_quote] + modified_input[end_quote + 1:]
        tokens = modified_input.split()

        for token in tokens:
            for verb in verbs:
                if verb in token:  # the token is a relevant verb
                    count += 1
                    result.append((token, preprocessed_input.index(token)))
                    break
        
        return count, result

    def add_quotes(self, title, line):
        """Helper function for extract_sentiment_for_movies.
        Makes sures the movie title has quotes around them.
        :param a movie title and UN-PREPROCESSED line
        :returns: the line with quotes around the given movie
        """
        lc_line = line.lower()
        lc_title = title.lower()
        title_ind = lc_line.index(lc_title)
        
        # check if title already has quotes around it
        if (title_ind - 1 >= 0 and line[title_ind-1]=='\"') and (title_ind + len(title) < len(lc_line) and line[title_ind + len(title)] == '\"'):
            return line
        # missing end quotation mark
        elif (title_ind - 1 >= 0 and line[title_ind-1]=='\"') and not (title_ind + len(title) < len(lc_line) and line[title_ind + len(title)] == '\"'):
            return line[:title_ind+len(title)] + '\"' + line[title_ind+len(title):]
        # missing start quotation mark
        elif not (title_ind - 1 >= 0 and line[title_ind-1]=='\"') and (title_ind + len(title) < len(lc_line) and line[title_ind + len(title)] == '\"'):
            return line[:title_ind] + '\"' + line[title_ind:]
        # missing both quotation marks
        else:
            return line[:title_ind] + '\"' + line[title_ind:title_ind+len(title)] + '\"' + line[title_ind+len(title):]

    def extract_sentiment_for_movies(self, preprocessed_input):
        """Creative Feature: Extracts the sentiments from a line of
        pre-processed text that may contain multiple movies. Note that the
        sentiments toward the movies may be different.
        You should use the same sentiment values as extract_sentiment, described above.
        :param preprocessed_input: a user-supplied line of text that has been
        pre-processed with preprocess()
        :returns: a list of tuples, where the first item in the tuple is a movie
        title, and the second is the sentiment in the text toward that movie
        """
        movies = self.extract_titles(preprocessed_input)
        
        # add quotes around all movies in input
        for movie in movies:
            preprocessed_input = self.add_quotes(movie, preprocessed_input)

        # preprocess input to do negation handling
        preprocessed_input = self.preprocess(preprocessed_input)

        # Case 1: No movies found in input
        if (len(movies) == 0): return []
        
        # Case 2: Single movie found in input
        if (len(movies) == 1):
            sentiment = self.extract_sentiment(preprocessed_input)
            return [(movies[0], sentiment)]

        # Case 3: Multiple movies found in input
        verb_count, verbs = self.find_verbs(preprocessed_input, movies)  # Identify number of verbs in sentence

        if verb_count == 0:  # no verbs, return all neutral sentiment
            result = []
            for movie in movies:
                result.append((movie, 0))
            return result

        if verb_count == 1:  # Single verb
            # 'but' isn't in input or comes before verbs (cases w/o 'but' or second half of split sentence that starts with but)
            if 'but ' not in preprocessed_input.lower() or ('but ' in preprocessed_input.lower() and preprocessed_input.lower().index('but ') < verbs[0][1]):
                sentiment = self.extract_sentiment(preprocessed_input)
                result = []

                for movie in movies:
                    result.append((movie, sentiment))
                
                return result
            else:
                but_ind = preprocessed_input.index('but ')
                first_half_input = preprocessed_input[:but_ind]
                second_half_input = 'NOT_' + verbs[0][0] + preprocessed_input[but_ind + 3:]
                return self.extract_sentiment_for_movies(first_half_input) + self.extract_sentiment_for_movies(second_half_input)
                
        # Multiple verbs (if not a run-on sentence, should be max 2 verbs)
        verb1_ind = verbs[0][1]  # index of first verb
        start_ind = verb1_ind
        verb2_ind = verbs[1][1]  # index of second verb
        end_quote_mark_ind = preprocessed_input.index('\"', preprocessed_input.index('\"') + 1)  # finds second quotation mark in input

        # movie title comes after the verb, e.g. I liked "E.T.", so search for punctuation after movie title
        if end_quote_mark_ind > verb1_ind: start_ind = end_quote_mark_ind
        
        # check if there are any lists of movies within the input, e.g. "E.T.", "The Notebook", and "Love Actually"
        list_pattern = '\"(, (?:and|or)) '  # if list of movies is properly formed, will have '", and/or' in the input
        list_matches = re.findall(list_pattern, preprocessed_input)

        # there is a list in the input
        if len(list_matches) > 1:
            # Splitting punctuation should be after punctuation for first list (assuming each half of input has max 1 list)
            list_ind = preprocessed_input.index(list_matches[0])

            if list_ind > start_ind:  # If list is before the verb, doesn't affect splitting punctuation
                end_quote_mark_ind = preprocessed_input.index('\"', preprocessed_input.index('\"', list_ind) + 1)
                start_ind = end_quote_mark_ind

        if ',' in preprocessed_input[start_ind:]:
            comma_ind = preprocessed_input.index(',', start_ind)
            first_half_input = preprocessed_input[:comma_ind]
            second_half_input = preprocessed_input[comma_ind + 1:]
            return self.extract_sentiment_for_movies(first_half_input) + self.extract_sentiment_for_movies(second_half_input)
        elif '. ' in preprocessed_input[start_ind:]:
            period_ind = preprocessed_input.index('. ', start_ind)
            first_half_input = preprocessed_input[:period_ind]
            second_half_input = preprocessed_input[period_ind + 1:]
            return self.extract_sentiment_for_movies(first_half_input) + self.extract_sentiment_for_movies(second_half_input)
        elif ';' in preprocessed_input[start_ind:]:
            semicolon_ind = preprocessed_input.index(';', start_ind)
            first_half_input = preprocessed_input[:semicolon_ind]
            second_half_input = preprocessed_input[semicolon_ind + 1:]
            return self.extract_sentiment_for_movies(first_half_input) + self.extract_sentiment_for_movies(second_half_input)
        else:  # just assume can't find sentiment for weird non-grammatically correct cases
            result = []
            for movie in movies:
                result.append((movie, 0))
        
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
        closest = [[], -1]

        title_length = len(title)
        # convert the title typed by user into same format as db titles (first letter uppercase, rest lowercase)
        terms_in_title = title.split()
        capitalize_list = []
        for term in terms_in_title:
            lowercase = term.lower()
            capitalize = lowercase.capitalize()
            capitalize_list.append(capitalize)
        t = ""
        for i in range(len(terms_in_title) - 1):
             t += capitalize_list[i] + ' '
        t += capitalize_list[-1]

        pos_titles = self.handle_capitalization(terms_in_title)

        # handles article(s) for foreign and English language
        articles = ['La', 'la', 'Le', 'le', 'Les', 'les', 'Il', 'il', "L'", "l'", 'A', 'a', 'Die', 'die',
                    'Das', 'das', 'An', 'an', 'The', 'the', 'Der', 'der', 'Den', 'den', 'Dem', 'dem',
                    'Des', 'des', 'El', 'el', 'Los', 'los', 'Las', 'las', 'Lo', 'lo', 'Gli', 'gli']

        translations = title.split('(')
        article_idx = []
        idx = 0
        for translation in translations:
            words_in_translation = translation.split()
            if words_in_translation[0] in articles:
                article_idx.append(idx)
            idx += len(words_in_translation)

        relist = []
        if article_idx != []:
            relist = self.handle_articles(article_idx, terms_in_title, relist)
            restring = ""

            if re.match("\([\d]+\)", terms_in_title[-1]) is not None:
                relist.append(terms_in_title[-1])
            for i in range(len(relist) - 1):
                restring += relist[i] + ' '
            restring += relist[-1]
            pos_titles.append(restring)

        # Calculate Levenshtein distance for each (title, candidate) pair
        for pos_title in pos_titles:
            title_length = len(pos_title)
            for title_index in range(len(self.titles)):
                candidate_full = self.titles[title_index][0]
                # Remove the (year) from the back of db title
                # doesn't currently account for foreign films /translated titles in parentheses
                terms_in_candidate = candidate_full.split()
                if re.match("\([\d]+\)", terms_in_candidate[-1]) is not None:
                    terms_in_candidate.pop()
                candidate = ""
                for i in range(len(terms_in_candidate) - 1):
                    candidate += terms_in_candidate[i] + ' '
                candidate += terms_in_candidate[-1]
                candidate_length = len(candidate)

                # initialize dynamic programming table
                d = np.zeros((title_length + 1, candidate_length + 1))
                # the table is 0-indexed with dimensions title_length * candidate_length
                d[0][0] = 0
                for i in range(1, title_length + 1):
                    d[i][0] = i
                for j in range(1, candidate_length + 1):
                    d[0][j] = j
                for i in range(1, title_length + 1):
                    for j in range(1, candidate_length + 1):
                        if pos_title[i - 1] == candidate[j - 1]:
                            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1])
                        else:
                            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + 2)
                # minimum edit distance is stored in the bottom right cell
                min_distance = d[title_length][candidate_length]
                if min_distance <= max_distance:
                    if closest[1] == -1 or min_distance < closest[1]:
                        closest[0] = [title_index]
                        closest[1] = min_distance
                    elif min_distance == closest[1]:
                        closest[0].append(title_index)
        return closest[0]

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
        smaller_list = []
        if clarification == "":
            return candidates

        # if the clarification input contains specifics in double quotes, assume we only want the stuff in the quotes
        if re.findall(r'"', clarification) != []:
            pattern = r'"(.*)"'
            match = re.search(pattern, clarification)
            if match is None:
                return candidates
            clarification = match.group(1)

        # disambiguating via full movie title input (with or without year)
        for candidate in candidates:
            if clarification == self.titles[candidate][0] or clarification == self.titles[candidate][0][:-7]:
                return [clarification]

        clarification = re.sub("\(", r"\(", clarification)
        clarification = re.sub("\)", r"\)", clarification)

        # disambiguating through word input (eg. "Stone" vs "Philosopher's Stone")
        name_pattern = "[.]*(\D+)[.]*"
        name = re.findall(name_pattern, clarification)
        franchise_words = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']
        if name != [] and name[0] != '(':
            # handles Movie "II" vs Movie "III"
            if name[0] in franchise_words:
                for candidate in candidates:
                    if re.findall(' ' + name[0] + '[ :,]', self.titles[candidate][0]) != []:
                        smaller_list.append(candidate)
            else:
                for candidate in candidates:
                    if re.findall(name[0], self.titles[candidate][0]) != []:
                        smaller_list.append(candidate)

        # disambiguating year
        year_pattern = "[.]*([\d]{4})[.]*"
        year = re.findall(year_pattern, clarification)
        if year != []:
            for candidate in candidates:
                if re.findall('\(' + year[0] + '\)', self.titles[candidate][0]) != []:
                    smaller_list.append(candidate)

        # disambiguating movies via a number that isn't a year -- ie. "Scream" vs "Scream 2",
        # or "Hate" vs "10 Things I Hate About You"
        franchise_pattern = "[.]*([\d]+)[.]*"
        franchise = re.findall(franchise_pattern, clarification)
        if franchise != []:
            for candidate in candidates:
                if re.findall(franchise[0] + '[ :,]', self.titles[candidate][0]) != []:
                    smaller_list.append(candidate)

        return smaller_list

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
        binarized_ratings = np.where((ratings > 0) & (ratings <= threshold), -1, ratings)
        binarized_ratings = np.where(binarized_ratings > threshold, 1, binarized_ratings)
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
        # Compute cosine similarity between the two vectors.             #
        ########################################################################
        similarity = np.dot(u,v) / (np.linalg.norm(u) * np.linalg.norm(v))
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
        recommendations = []
        predicted_ratings = []
        not_rated = []
        rated = []
        for i in range(len(user_ratings)):
            if user_ratings[i] == 0:
                not_rated.append(i)
            else:
                rated.append(i)

        for n in not_rated:
            movie_n = ratings_matrix[n]
            similarities = []
            for r in rated: 
                movie_r = ratings_matrix[r]
                if (r not in self.recommended and np.linalg.norm(movie_n) != 0): 
                    similarities.append((self.similarity(movie_n, movie_r), r))
            # Sort by descending order of similarities
            similarities.sort(key=lambda x: x[0], reverse = True)
            predicted = 0
            for s in similarities:
                predicted += (s[0] * user_ratings[s[1]]) # predicted rating is similarity * rating
            predicted_ratings.append((predicted, n))

        # Get top k predicted ratings
        predicted_ratings.sort(key=lambda x: x[0], reverse = True)
        topk_pred = predicted_ratings[:k]
        recommendations = [p[1] for p in topk_pred]  # Only extract the movie indices
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
        Meet our chatbot, Candace! Candace can help recommend a movie to you. Just
        tell her about a few movies you've either liked or disliked, and from that,
        she'll find a movie that you'll hopefully enjoy! A couple tips for talking
        to Candace: when you mention a movie, put it in quotes, such as "The Notebook"
        or "Avatar". If you know the year, that's also helpful for Candace to know! Just
        put it in parentheses after the title in quotes, such as "Titanic (1997)". Hope
        Candace is helpful to you!
        """


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
