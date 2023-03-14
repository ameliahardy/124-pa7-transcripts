# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util

import numpy as np
import re
import string


# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.

        self.creative = creative
        if self.creative:
            self.name = 'Tony Hawk'
        else:
            self.name = 'Oscar'

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')
        self.user_ratings = np.zeros((ratings.shape[0],))
        self.movie_count = 0
        self.recommendations = []
        self.processed_titles = self.process_titles()

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
            greeting_message = "Yo what's up? It's Tony Hawk. I have some \
gnarly movie recs for you, dude. Just hit me with what you thought about a movie?"
        else:
            greeting_message = "Hey! My name is Oscar! I'm your personal assistant \
for giving personalized movie recommendations! Can you tell me about a movie that \
you liked?"

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
            goodbye_message = "It's been real man. Catch ya later!"
        else:
            goodbye_message = "Thanks for chatting wtih me! Talk to you soon!"

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
        import random
        if self.creative:
            movie_titles = self.extract_titles(line)
            movies_found = []
            for title in movie_titles:
                movies_found += self.find_movies_by_title(title)
            sentiment = self.extract_sentiment(line)

            if self.movie_count >= 5 and ("yes" in line.lower() or "yeah" in line.lower() or "yep" in line.lower()):
                if self.recommendations == []:
                    response = "Sorry dude! I'm all out of recs. If you would like another rec, \
tell me about another movie!"
                    self.movie_count = 0
                    return response
                responses = [
                    "Sweet! Given what you've told me, I think you would like " +
                    self.recommendations[0] + ". Would you like another rec?",
                    "Alright. Based on your responses, I recommend watching " + self.recommendations[0] + ". Would you like another \
rec?",
                    "Sure thing! I think you would like " +
                    self.recommendations[0] +
                    ". Would you like a different rec?",
                    "Of course! I think you would enjoy " +
                    self.recommendations[0] +
                    ". Would you like another movie rec?",
                    "I also recommend " + self.recommendations[0] + ". How about another one?"]
                response = random.choice(responses)
                self.recommendations.pop(0)
                return response
            elif self.movie_count >= 5 and ("no" == line.lower() or "nope" in line.lower()):
                response = "Ok dude. Thanks for hangin'! Type :quit to say goodbye."
                return response

            # case where the user types in at least one movie title - no quotes or correct caps needed
            if movie_titles:
                # case where user talks about more than one movie - extract sentiment for movies
                if len(movie_titles) > 1:
                    movie_list = self.extract_sentiment_for_movies(line)
                    liked_movies = []
                    disliked_movies = []
                    neutral_movies = []
                    for movie in movie_list:
                        if 1 in movie or 2 in movie:
                            liked_movies.append(movie[0])
                        elif -1 in movie or -2 in movie:
                            disliked_movies.append(movie[0])
                        else:
                            neutral_movies.append(movie[0])
                    response = "Got ya man, "
                    for i in range(len(liked_movies)):
                        response += "you liked " + liked_movies[i] + ", and "
                        self.movie_count += 1
                    for i in range(len(disliked_movies)):
                        response += "you didn't like " + \
                            disliked_movies[i] + ', and '
                        self.movie_count += 1
                    for i in range(len(neutral_movies)):
                        response += "you were ambivalent toward " + \
                            neutral_movies[i] + ', and '
                        self.movie_count += 1
                    if self.movie_count >= 5:
                        recommendation_idx = self.recommend(self.user_ratings, self.ratings)
                        self.recommendations = [self.titles[i][0] for i in recommendation_idx]
                        responses = ["I recommend you watch " + self.recommendations[0] + "! Would you like another rec?",
                                "you should totally watch " + self.recommendations[0] + ". Do you want another rec?",
                                "I think you would totally vibe with " + self.recommendations[0] + ". Would you like another rec?",
                                "I bet you would like " + self.recommendations[0] + ". Let me know if you would like another rec!"]
                        response += random.choice(responses)
                        self.recommendations.pop(0)
                    else: 
                        responses = ["I totally agree dude. What did you think about another movie?", 
                                     "I'm right there with you homie. Tell me about another movie.",
                                     "I feel that way too man. What did you think of another movie?"]
                        response += random.choice(responses)
                # case where the movie's in our database
                elif movies_found:
                    # case where there are multiple movies with that title found in database
                    if len(movies_found) > 1:
                        responses = [
                            "I think there are a couple versions of, " +
                            movie_titles[0] + ". Which one did you mean? ",
                            "I think there are multiple versions of " + movie_titles[0] + " Can you specify which one \
you are talkin' about?"]
                        response = random.choice(responses)
                    # case where the user likes the movie
                    elif sentiment >= 1:
                        responses = [
                            "Ahhh yeah man! I see you liked " +
                            movie_titles[0] +
                            "! Can you tell me about another movie?",
                            "Sick! You liked " +
                            movie_titles[0] +
                            ". Can you tell me what you thought of another movie?",
                            "Yo. You liked " +
                            movie_titles[0] +
                            ". What did ya think of another movie?",
                            "Yeah! " +
                            movie_titles[0] +
                            " is super dope. Can you tell me what you thought about another movie?",
                            "Oooo " +
                            movie_titles[0] +
                            " was gnarly bro! What did you think of another movie?",
                            "Dude... " + movie_titles[0] + " was INSANE! Let me know what you thought of another movie."]
                        response = random.choice(responses)
                        self.user_ratings[movies_found[0]] = 1
                        self.movie_count += 1
                        # recommend after 5 movies
                        if self.movie_count == 5:
                            recommendation_idx = self.recommend(
                                self.user_ratings, self.ratings, 5)
                            self.recommendations = [
                                self.titles[i][0] for i in recommendation_idx]
                            responses = [
                                "Bet. You liked " + movie_titles[0] + "! I recommend you watch " + self.recommendations[0] +
                                "! Would you like another rec?",
                                "Sweet! You liked " + movie_titles[0] + ". Dope. You should totally watch " + self.recommendations[0] +
                                ". Do you want another rec?",
                                "I see you liked " + movie_titles[0] + "! Based on what you've told me, I think you would totally vibe with " +
                                self.recommendations[0] +
                                ". Would you like another rec?",
                                "Yeah! " + movie_titles[0] + " was a great one! I bet you would like " + self.recommendations[0] +
                                ". Let me know if you would like another rec!"]
                            response = random.choice(responses)
                            self.recommendations.pop(0)
                    # case where the user dislikes the movie
                    elif sentiment <= -1:
                        responses = [
                            "Ahhh dude. I see you didn't like " +
                            movie_titles[0] +
                            ". Can you tell me about another movie?",
                            "I didn't like " +
                            movie_titles[0] +
                            " either, man. What did you think of another movie?",
                            "You didn't like " +
                            movie_titles[0] +
                            ". Can you tell me about another movie?",
                            "You weren't a fan of " +
                            movie_titles[0] +
                            ". Can you tell me what you thought of another movie?",
                            "Ahh yeah. I didn't like " +
                            movie_titles[0] +
                            " either. Let me know what you thought of another movie.",
                            "Yeah " + movie_titles[0] + " was a little sketchy. I gotchu. What'd you think about other movies?"]
                        response = random.choice(responses)
                        self.user_ratings[movies_found[0]] = -1
                        self.movie_count += 1
                        # recommend after 5 movies
                        if self.movie_count == 5:
                            recommendation_idx = self.recommend(
                                self.user_ratings, self.ratings, 5)
                            self.recommendations = [
                                self.titles[i][0] for i in recommendation_idx]
                            responses = [
                                "You weren't feelin' " + movie_titles[0] + "! You should totally watch " + self.recommendations[0] +
                                "! Do you wanna hear another rec?",
                                "You weren't vibing with " + movie_titles[0] + ". Maybe you should watch " + self.recommendations[0] +
                                ". I bet you would like it! Do you want another rec?",
                                "I thought " + movie_titles[0] + " was a bit sketchy too. I think you should watch " + self.recommendations[0] +
                                " instead. Want another rec man?"]
                            response = random.choice(responses)
                            self.recommendations.pop(0)
                    # case where the user neither likes nor dislikes the movie
                    elif sentiment == 0:
                        responses = [
                            "Ahh dude. It seems that you were ambivalent toward " +
                            movie_titles[0] +
                            ". Can you tell me how you felt about another movie?",
                            "You were neutral toward " + movie_titles[0] + ". I felt the same, dude. Can you tell me about another movie?"]
                        response = random.choice(responses)
                # case where the movie isn't in our database
                else:
                        responses = [
                            "Sorry man, I haven't seen " +
                            movie_titles[0] +
                            ". Can you tell me about another movie?",
                            "Sorry dude. I've never heard of " +
                            movie_titles[0] +
                            ". How'd you feel about another movie?",
                            "Shoot. I haven't heard of " + movie_titles[0] + ". Tell me about another movie."]
                        response = random.choice(responses)
            # case where the user doesn't mention any movies
            else:
                responses = [
                    "Sorry dude, I didn't catch any movies mentioned there. Can ya tell me a movie that you liked?",
                    "Hmmmm. Don't know if I caught any movies. Could ya tell me what you thought of another movie?"]
                response = random.choice(responses)

        # starter mode
        else:
            movie_titles = self.extract_titles(line)
            movies_found = []
            for title in movie_titles:
                movies_found += self.find_movies_by_title(title)
            sentiment = self.extract_sentiment(line)

            if self.movie_count == 5 and ("yes" in line.lower() or "yeah" in line.lower() or "yep" in line.lower()):
                if self.recommendations == []:
                    response = "Sorry! I'm all out of recommendations. If you would like another recommendation, \
tell me about another movie!"
                    self.movie_count = 0
                    return response
                responses = [
                    "Ok! Given what you've told me, I think you would like " +
                    self.recommendations[0] +
                    ". Would you like more recommendations?",
                    "Alright. Based on your responses, I recommend watching " + self.recommendations[0] + ". Would you like another \
recommendation?",
                    "Sure thing! I think you would like " +
                    self.recommendations[0] +
                    ". Would you like a different recommendation?",
                    "Of course! I think you would enjoy " +
                    self.recommendations[0] +
                    ". Would you like another movie recommendation?",
                    "I also recommend " + self.recommendations[0] + ". How about another one?"]
                response = random.choice(responses)
                self.recommendations.pop(0)
                return response
            elif self.movie_count == 5 and ("no" in line.lower() or "nope" in line.lower()):
                response = "Ok! I hope you liked your recommendations! Type :quit to say goodbye."
                return response

            # case where the user types in at least one movie title
            if movie_titles:
                # case where user talks about more than one movie
                if len(movie_titles) > 1:
                    responses = [
                        "Sorry, can you tell me about one movie at a time?",
                        "Sorry, I can only handle one movie at a time. Could you tell about one movie again please?",
                        "Ah I'm sorry. I can only process one movie at a time. Please tell me about one movie again."]
                    response = random.choice(responses)
                # case where the movie's in our database
                elif movies_found:
                    # case where there are multiple movies with that title found in database
                    if len(movies_found) > 1:
                        responses = [
                            "I found more than one movie titled, " +
                            movie_titles[0] + ". Can you clarify?",
                            "I think there are multiple versions of " + movie_titles[0] + " in my database. \
Can you specify which one you are referring to?",
                            "There are two movies titled, " + movie_titles[0] + ". Which one did you mean?"]
                        response = random.choice(responses)
                    # case where the user likes the movie
                    elif sentiment >= 1:
                        responses = [
                            "I see you liked " +
                            movie_titles[0] +
                            "! Can you tell me about another movie?",
                            "Ok! You liked " +
                            movie_titles[0] +
                            ". Can you tell me what you thought of another movie?",
                            "Got it. You liked " +
                            movie_titles[0] +
                            ". What did you think of another movie?",
                            "Yeah! " +
                            movie_titles[0] +
                            " is such a good movie. Can you tell me what you thought about another movie?",
                            "Oooo I liked " +
                            movie_titles[0] +
                            " too! What did you think of another movie?",
                            "For sure! " + movie_titles[0] + " was a good movie. Please tell me what you thought of another movie."]
                        response = random.choice(responses)
                        self.user_ratings[movies_found[0]] = 1
                        self.movie_count += 1
                        # recommend after 5 movies
                        if self.movie_count == 5:
                            recommendation_idx = self.recommend(
                                self.user_ratings, self.ratings, 5)
                            self.recommendations = [
                                self.titles[i][0] for i in recommendation_idx]
                            responses = [
                                "You liked " + movie_titles[0] + "! Got it! I recommend you watch " + self.recommendations[0] +
                                "! Would you like more recommendations?",
                                "Sweet! You liked " + movie_titles[0] + ". Dope. You should totally watch " + self.recommendations[0] +
                                ". Do you want another recommendation?",
                                "I see you liked " + movie_titles[0] + "! Based on what you've told me, I think you would like " +
                                self.recommendations[0] +
                                ". Would you like another recommendation?",
                                "Yeah! " + movie_titles[0] + " was a great one! I bet you would like " + self.recommendations[0] +
                                ". Let me know if you would like another recommendation!"]
                            response = random.choice(responses)
                            self.recommendations.pop(0)
                    # case where the user dislikes the movie
                    elif sentiment <= -1:
                        responses = [
                            "I see you didn't like " +
                            movie_titles[0] +
                            ". Can you tell me about another movie?",
                            "I didn't like " +
                            movie_titles[0] +
                            " either. What did you think of another movie?",
                            "Got it. You didn't like " +
                            movie_titles[0] +
                            ". Can you tell me about another movie?",
                            "Got it. You weren't a fan of " +
                            movie_titles[0] +
                            ". Can you tell me what you thought of another movie?",
                            "Ahh yeah. I didn't like " + movie_titles[0] + " either. Please tell me what you thought of another movie."]
                        response = random.choice(responses)
                        self.user_ratings[movies_found[0]] = -1
                        self.movie_count += 1
                        # recommend after 5 movies
                        if self.movie_count == 5:
                            recommendation_idx = self.recommend(
                                self.user_ratings, self.ratings, 5)
                            self.recommendations = [
                                self.titles[i][0] for i in recommendation_idx]
                            responses = [
                                "You didn't like " + movie_titles[0] + "! Got it! I recommend you watch " + self.recommendations[0] +
                                "! Would you like more recommendations?",
                                "Gotcha! You didn't like " + movie_titles[0] + ". Maybe you should watch " + self.recommendations[0] +
                                ". I bet you would like it! Do you want another recommendation?"]
                            response = random.choice(responses)
                            self.recommendations.pop(0)
                    # case where the user neither likes nor dislikes the movie
                    elif sentiment == 0:
                        responses = [
                            "I didn't catch if you liked or disliked " + movie_titles[
                                0] + ". Can you tell me more about it?",
                            "I'm sorry. I'm not sure if you liked " + movie_titles[0] + ". Tell me about it."]
                        response = random.choice(responses)
                # case where the movie isn't in our database
                else:
                    responses = [
                        "Sorry, " +
                        movie_titles[0] +
                        " is not in our database. Can you tell me about another movie?",
                        "I'm sorry. I've never heard of " + movie_titles[
                            0] + ". Could you tell me about another movie?",
                        "I haven't heard of " + movie_titles[0] + ", sorry...Tell me about another movie."]
                    response = random.choice(responses)
            # case where the user doesn't mention any movies
            else:
                responses = [
                    "Sorry, I didn't catch any movies mentioned there. Can you tell me a movie that you liked?",
                    "Hmmmm. I'm not sure I caught any movies. Could you tell me what you thought of another movie?"]
                response = random.choice(responses)

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

    def process_titles(self):
        """
        Processes the movie titles in self.titles
        Creates a dictionary where:
        key: Title of Movie
        Value: list if tuples [(year, index)]

        Example Title from self.titles: "Woman in the Fifth, The (Femme du Vème, La) (2011)"
        Alternate representations:
        "The Woman in the Fifth (2011)"
        "La Femme du Vème (2011)"
        """
        processed = {}

        # List of just the movie titles -> not the genres
        just_titles = [title[0] for title in self.titles]

        for i in range(len(just_titles)):

            title = just_titles[i]

            # 1. Split Title and Year

            # Find the year
            year_pattern = r'\(\d{4}\)'
            year_list = re.findall(year_pattern, title)
            year = ""
            if year_list:
                year = year_list[0]

            # Remove The Year from the Title
            title = re.sub(year_pattern, '', title).strip()

            # 2. Get any alternative Title representation from parenthesis
            alternate_title = ""
            start = title.find('(')
            if start != -1:
                end = title.find(')')
                if (end != -1):
                    alternate_title = title[start + 1: end].strip()
                    title = title[: start].strip()

            # If title has article at the end, rewrite it with article at start
            end_article_pattern = r"^(.*),\s(The|A|An|L'|Le|La|Il|Les|Die|Das|Der|Det|En|El)$"
            # Check end articles in main title
            main_match = re.match(end_article_pattern, title)
            # Check end articles in alternate title
            alternate_match = re.match(end_article_pattern, alternate_title)
            # Reformat main title if needed
            if main_match:
                # if article has an apostrophe -> No space between article and word
                if main_match.group(2) == "L'":
                    title = main_match.group(2) + main_match.group(1)
                else:
                    title = main_match.group(2) + " " + main_match.group(1)
            # Reformat alternate title if needed
            if alternate_match:
                # if article has an apostrophe -> No space between article and word
                if alternate_match.group(2) == "L'":
                    alternate_title = alternate_match.group(
                        2) + alternate_match.group(1)
                else:
                    alternate_title = alternate_match.group(
                        2) + " " + alternate_match.group(1)

            title = title.strip()
            alternate_title = alternate_title.strip()

            # 3. Remove a.k.a. from alternate
            alternate_title = alternate_title.replace("a.k.a. ", "")

            # 4. Add titles to dict with their years

            if title not in processed:
                processed[title] = []
            processed[title].append((year, i))

            if alternate_title:
                if alternate_title not in processed:
                    processed[alternate_title] = []
                processed[alternate_title].append((year, i))

        return processed

    def extract_titles(self, user_input):
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
        user_input = user_input.strip()
        if self.creative:

            matches = re.findall('"([^"]*)"', user_input)
            if len(matches) != 0:
                return matches

            # Titles are from a dict of processed titles
            titles = list(self.processed_titles.keys())
            # Remov problematic words
            temp = user_input
            user_input = user_input.lower().replace("not good", "nottgood")
            user_input = user_input.lower().replace("not bad", "nottbad")
            user_input = user_input.lower().replace("not nice", "nottnice")
            user_input = user_input.lower().replace("but not", "buttnot")
            user_input = user_input.lower().replace("did not", "diddnot")
            user_input = user_input.lower().replace("i hated", "iihated")
            s = ''
            for i in range(len(temp)):
                if temp[i].isupper():
                    s += user_input[i].upper()
                else:
                    s += user_input[i]
            user_input = s

            low_titles = [title.lower() for title in titles]

            # Build a regular expression that matches any of the titles
            pattern = r'(?:^|[\s"])(' + '|'.join(re.escape(title) + r'(?:\s+\d+)?' for title in titles) + r')(?=[,\s"]|$)'

            # Find all matches in the review
            result = re.findall(pattern, user_input,
                                flags=re.IGNORECASE | re.UNICODE)

            # Build a regular expression that matches any of the titles
            pattern2 = r"(?:^|\s|\")(" + "|".join(re.escape(title) + r"(?:\s+\d+)?" for title in titles) + r")\b"

            # Find all matches in the review
            result2 = re.findall(pattern2, user_input, flags=re.IGNORECASE | re.UNICODE)

            for item in result2:
                if item not in result:
                    result.append(item)

            # remove all empty strings
            result = [match for match in result if (
                match != "" and match != " ")]
            # Dict mapping each match to a possible title
            # Eg {'titanic': ['Titanic (1997)', 'Titanic (1953)']}
            matches_with_years = {}

            for match in result:
                # The match will be in whatever format the user gave us in
                # So we need to turn it into a format we can use to index into dictionary
                if match.lower() not in low_titles:
                    continue
                # Add the match to matches with years dictionary
                matches_with_years[match] = []

                # Add years to dict
                index = low_titles.index(match.lower())
                formatted_match = titles[index]
                for tpl in self.processed_titles[formatted_match]:
                    if tpl:
                        year = tpl[0]
                        if year:
                            matches_with_years[match].append(
                                formatted_match + " " + year)
                        else:
                            matches_with_years[match].append(formatted_match)

            # Go through dict. If user specified a year, give title with year. otherwise, give just the title
            for match in matches_with_years:
                # Did the user specify a title with a year?
                found = False
                # if they did -> Yay, we take the title with the year
                for title in matches_with_years[match]:
                    if title.lower() in user_input.lower():
                        matches.append(title)
                        found = True
                # If they did not: (this does not currently account for the user having a false year)
                if not found:
                    # Extract the year after the title: If the year is not valid (don't count title)
                    if "(" in user_input and ")" in user_input:
                        match_start = user_input.lower().find(match.lower())
                        match_end = match_start + len(match) - 1
                        year_start = match_end + 2
                        year_end = year_start + 5
                        if year_end < len(user_input):
                            year = user_input[year_start: year_end + 1]
                            if year[0] == "(" and year[-1] == ")":
                                if year[1:5].isnumeric():
                                    continue
                    matches.append(match)
            # Remove movies like Not and hated


        else:
            matches = re.findall('"([^"]*)"', user_input)
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
        movie_titles = []

        # creative Mode for extract movie by titles
        if self.creative:

            # First extract the year from the movie title
            year_pattern = r'\(\d{4}\)'
            year_list = re.findall(year_pattern, title)
            year = ""
            if year_list:
                year = year_list[0]

            # Remove The Year from the Title
            title = re.sub(year_pattern, '', title).strip()

            # Now, we need to deal with capitalization issues
            # So we can index into our processsed titles dict properly
            titles = list(self.processed_titles.keys())
            low_titles = [title.lower() for title in titles]

            # We do not recognize the movie title
            if title.lower() not in low_titles:
                return movie_titles

            # Otherwise, it is in the dict, so we need to get the title
            index = low_titles.index(title.lower())
            formatted_match = titles[index]
            # Years will be a tuple of (year, index) for each title
            years = self.processed_titles[formatted_match]

            # See if user gave a valid year
            for tpl in years:
                if year == tpl[0] or year == "":
                    movie_titles.append(tpl[1])

        else:
            paren_idx = title.find('(')
            # case where the user specifies the year in parentheses
            if paren_idx != -1:
                for i, pair in enumerate(self.titles):
                    movie_title = pair[0]
                    if movie_title == title:
                        movie_titles.append(i)
                        break
                    else:
                        # case where there's an article after a comma
                        comma_idx = movie_title.find(',')
                        if comma_idx != -1:
                            for article in ["A", "An", "The"]:
                                movie_title_rearranged = article + " " + \
                                    movie_title[:comma_idx] + \
                                    movie_title[comma_idx + len(article) + 2:]
                                if movie_title_rearranged == title:
                                    movie_titles.append(i)
                                    break
            # case where the user doesn't specify the year
            else:
                for i, pair in enumerate(self.titles):
                    movie_title = pair[0]
                    year_idx = movie_title.find('(')
                    # get the movie title without the year in parentheses
                    movie_title_without_year = movie_title[:year_idx - 1]
                    if movie_title_without_year == title:
                        movie_titles.append(i)
                    else:
                        # case where there's an article after a comma
                        comma_idx = movie_title.find(',')
                        if comma_idx != -1:
                            for article in ["A", "An", "The"]:
                                movie_title_rearranged = article + " " + \
                                    movie_title[:comma_idx]
                                if movie_title_rearranged == title:
                                    movie_titles.append(i)
                                    break

        return movie_titles

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
        import porter_stemmer
        p = porter_stemmer.PorterStemmer()

        # add stemmed words to the sentiment dictionary
        words = list(self.sentiment.keys())
        for word in words:
            self.sentiment[p.stem(word)] = self.sentiment[word]

        if not self.creative:
            # count the number of positive and negative sentiment words in the input
            pos_count = 0
            neg_count = 0
            manual_negation = ["don't", "didn't", "not", "never", "no"]
            input = preprocessed_input.split(' ')

            for idx in range(len(input)):
                word = input[idx]
                if len(input) < 3:
                    prev = input[0]
                    prev_prev = input[0]
                else:
                    prev = input[idx - 1]
                    prev_prev = input[idx - 2]
                stemmed_word = p.stem(word)
                # ignore words that aren't in the sentiment dictionary
                if not self.sentiment.get(stemmed_word):
                    continue
                # negate sentiment value if negation words come before sentiment word
                if self.sentiment[stemmed_word] == "pos" and prev in manual_negation or prev_prev in manual_negation:
                    neg_count += 1
                elif self.sentiment[stemmed_word] == "neg" and prev in manual_negation or prev_prev in manual_negation:
                    pos_count += 1
                elif self.sentiment[stemmed_word] == "pos":
                    pos_count += 1
                elif self.sentiment[stemmed_word] == "neg":
                    neg_count += 1

            # return 1, -1, or 0 based on sentiment count
            if pos_count > neg_count:
                return 1
            elif neg_count > pos_count:
                return -1
            return 0
        else:
            # count the number of positive and negative sentiment words in the input
            pos_count = 0
            neg_count = 0
            manual_negation = ["don't", "didn't", "not", "never", "no"]
            pos_mult = 1
            neg_mult = 1
            pos_strong = ["love", "adore", "heavenly", "amazing", "fantastic", "incredible", "spectacular", "terrific", "phenomenal", "astounding", "brilliant", "wonderful"]
            neg_strong = ["hate", "terrible", "garbage", "horrible", "detest", "abhor", "awful", "disastrous"]
            enhancers = ["really", "greatly", "profoundly", "deeply", "sincerely", "truly"]
            input = preprocessed_input.split(' ')
            neutral = 1

            for idx in range(len(input)):
                word = input[idx]
                if len(input) < 3:
                    prev = input[0]
                    prev_prev = input[0]
                else:
                    prev = input[idx - 1]
                    prev_prev = input[idx - 2]
                stemmed_word = p.stem(word)
                # ignore words that aren't in the sentiment dictionary
                if not self.sentiment.get(stemmed_word):
                    continue
                # negate sentiment value if negation words come before sentiment word
                if ((stemmed_word in pos_strong or stemmed_word in neg_strong or word.lower() in pos_strong or word.lower() in neg_strong) and (prev in manual_negation or prev_prev in manual_negation)):
                    neutral = 0

                if (self.sentiment[stemmed_word] == "pos") and prev in manual_negation or prev_prev in manual_negation:
                    neg_count += 1
                elif self.sentiment[stemmed_word] == "neg" and prev in manual_negation or prev_prev in manual_negation:
                    pos_count += 1
                elif self.sentiment[stemmed_word] == "pos":
                    pos_count += 1
                elif self.sentiment[stemmed_word] == "neg":
                    neg_count += 1


                # conditions to check if we need to increase the weight of pos/neg sentiment
                if (self.sentiment[stemmed_word] == "pos") and prev in enhancers:
                    pos_mult = 2
                    continue
                if (self.sentiment[stemmed_word] == "neg") and prev in enhancers:
                    neg_mult = 2
                    continue
                if word.lower() in pos_strong or stemmed_word in pos_strong:
                    pos_mult = 2
                    continue
                if word.lower() in neg_strong or stemmed_word in neg_strong:
                    neg_mult = 2
                    continue
            # return 1, -1, 2, -2, or 0 based on sentiment count
            senti = 0
            if pos_count > neg_count:
                senti = 1 * pos_mult * neutral
            elif neg_count > pos_count:
                senti = -1 * neg_mult * neutral
            return senti

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
        sentiments = []
        negation_words = ['but', 'although', 'however', 'yet']

        titles = self.extract_titles(preprocessed_input)
        for title in titles:
            negation_idx = -1
            for word in negation_words:
                negation_idx = preprocessed_input.find(word)
                if negation_idx != -1:
                    break
            title_idx = preprocessed_input.find(title)
            sentiment = self.extract_sentiment(preprocessed_input)
            if negation_idx != -1 and negation_idx < title_idx:
                sentiment *= -1
            sentiments.append((title, sentiment))

        return sentiments

    def minimum_distance(self, s, t):
        """
        Takes in two strings, s, t
        Calculates minimum edit distance between them
        """

        # Create a matrix of zeros with dimensions (len(s)+1) x (len(t)+1)
        d = [[0 for j in range(len(t) + 1)] for i in range(len(s) + 1)]

        # Initialization
        for i in range(len(s) + 1):
            d[i][0] = i
        for j in range(len(t) + 1):
            d[0][j] = j

        # Iterate over the matrix to compute the distances
        for j in range(1, len(t) + 1):
            for i in range(1, len(s) + 1):

                if s[i - 1] == t[j - 1]:
                    d[i][j] = d[i - 1][j - 1]
                else:
                    d[i][j] = min(d[i - 1][j] + 1,  # deletion
                                  d[i][j - 1] + 1,  # insertion
                                  d[i - 1][j - 1] + 2)  # substitution

        # Return the distance between the two strings
        return d[len(s)][len(t)]

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
        """
        from collections import deque

        # initialize a set to keep track of visited titles
        visited = set()
        # initialize a queue and enqueue the starting title
        queue = deque([(title, 0)])
        movies = []
        """
        result = []
        closest_movies = []
        min_distance = max_distance

        for movie in self.processed_titles:
            if not movie:
                continue
            # Remove the year of the movie if there is one
            year_pattern = r'\(\d{4}\)'
            title = re.sub(year_pattern, '', title).strip()

            # Find edit distance between year and title
            edit_dist = self.minimum_distance(movie.lower(), title.lower())

            # keep track of movies with the minimum edit distance
            if edit_dist < min_distance:

                closest_movies = [movie]
                min_distance = edit_dist
            elif edit_dist == min_distance:
                closest_movies.append(movie)
        # get indexes of those movies
        for movie in closest_movies:
            for tpl in self.processed_titles[movie]:
                result.append(tpl[1])

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
        clarified_candidates = []
        # find what type of clarification the user gave

        # if the clarification is a year
        if re.search('\d{4}', clarification):
            for candidate in candidates:
                if self.titles[candidate][0].find(clarification) != -1:
                    clarified_candidates.append(candidate)

        # if the clarification is which number in the series it is
        elif re.search('\d{1}', clarification):
            for candidate in candidates:
                if self.titles[candidate][0].find(' ' + clarification) != -1:
                    clarified_candidates.append(candidate)

            # if the number in the series isn't directly in the title, sort
            # by date and return the correct one
            if not clarified_candidates:
                candidates_with_year = []
                for candidate in candidates:
                    year = re.search(
                        '\d{4}', self.titles[candidate][0]).group(0)
                    candidates_with_year.append((candidate, year))
                sorted_candidates = sorted(
                    candidates_with_year, key=lambda x: x[1])
                clarified_candidates.append(
                    sorted_candidates[int(clarification) - 1][0])

        # if the clarification specifies which one in the series it is
        elif re.search('(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth)', clarification):
            candidates_with_year = []
            for candidate in candidates:
                year = re.search('\d{4}', self.titles[candidate][0]).group(0)
                candidates_with_year.append((candidate, year))
            sorted_candidates = sorted(
                candidates_with_year, key=lambda x: x[1])
            match = re.search(
                '(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth)', clarification).group(0)

            numbers = ['first', 'second', 'third', 'fourth', 'fifth',
                       'sixth', 'seventh', 'eighth', 'ninth', 'tenth']
            clarified_candidates.append(
                sorted_candidates[numbers.index(match)][0])

        # if the clarification is a word or phrase indicating it's the first movie
        elif re.search('(oldest|original|classic)', clarification):
            candidates_with_year = []
            for candidate in candidates:
                year = re.search(
                    '\d{4}', self.titles[candidate][0]).group(0)
                candidates_with_year.append((candidate, year))
            sorted_candidates = sorted(
                candidates_with_year, key=lambda x: x[1])
            clarified_candidates.append(
                sorted_candidates[0][0])

        # if the clarification is a word or phrase indicating it's the last movie
        # in the series
        elif re.search('(most\srecent|latest|last|final)', clarification):
            candidates_with_year = []
            for candidate in candidates:
                year = re.search(
                    '\d{4}', self.titles[candidate][0]).group(0)
                candidates_with_year.append((candidate, year))
            sorted_candidates = sorted(
                candidates_with_year, key=lambda x: x[1])
            clarified_candidates.append(
                sorted_candidates[-1][0])

        # if the clarification is a word in the title of one or more of the movies
        else:
            clarification_words = clarification.split(' ')
            # only check substantive words in the clarification
            relevant_clarification_words = []
            irrelevant_word_list = ['the', 'and',
                                    'or', 'one', 'of', 'by', 'an', 'a']
            for word in clarification_words:
                if word not in irrelevant_word_list:
                    relevant_clarification_words.append(word)
            for candidate in candidates:
                matched = True
                # check and see if all substantive words in the clarification are in
                # a candidate title
                for word in relevant_clarification_words:
                    if self.titles[candidate][0].find(word) == -1:
                        matched = False
                if matched:
                    clarified_candidates.append(candidate)

        return clarified_candidates

        ############################################################################
        # 3. Movie Recommendation helper functions                                 #
        ############################################################################

    @ staticmethod
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
        for i in range(len(ratings)):
            for j in range(len(ratings[i])):
                entry = ratings[i][j]
                if entry == 0:
                    binarized_ratings[i][j] = 0
                elif entry > threshold:
                    binarized_ratings[i][j] = 1
                else:
                    binarized_ratings[i][j] = -1
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
        # user_ratings and matrix ratings_matrix and outputs a list of movies  #
        # recommended by the chatbot.                                          #
        #                                                                      #
        # WARNING: Do not use the self.ratings matrix directly in this         #
        # function.                                                            #
        #                                                                      #
        # For starter mode, you should use item-item collaborative filtering   #
        # with cosine similarity, no mean-centering, and no normalization of   #
        # scores.                                                              #
        #######################################################################

        recommendations = []

        if not creative:
            # Compute norm of each row in ratings_matrix -> 1D array with shape (num_movies, )
            epsilon = 1e-9  # avoid division by zero
            row_norms = np.linalg.norm(ratings_matrix, axis=1)
            # Normalize the ratings matrix by dividing each row by its norm -> 2D array with shape (num_movies, num_users)
            normalized_matrix = ratings_matrix / \
                (row_norms[:, np.newaxis] + epsilon)
            # Get similarities between pairs of movies -> Diagonal matrix where i, j entry is similarity of movies i and j
            similarities = normalized_matrix @ np.transpose(normalized_matrix)

            # get indexes of rated in the similarities matrix
            rated_indxs = np.where(user_ratings != 0)[0]
            # Get indexes of unrated movies in similarities matrix
            unrated_indxs = np.where(user_ratings == 0)[0]

            # Matrix where rows are all movies that have not been rated by User
            # Columns are all movies that have been rated
            # So we have similarities between rated and unrated movies
            sim_unrated_rated = similarities[unrated_indxs][:, rated_indxs]

            # Get only the ratings for movies user has rated
            user_rated_movies = user_ratings[rated_indxs]

            # Predict user ratings by
            # calculating weighted similarity between rated and unrated movies
            predicted_ratings = sim_unrated_rated.dot(user_rated_movies)

            # Sort in descending order to get indexes of top k movies with the highest rating
            top_k_indxs = np.argsort(predicted_ratings)[::-1][:k]

            # Map indexes of top k movies back to the unrated movies
            recommendations = list(unrated_indxs[top_k_indxs])

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
        debug_info = [self.movie_count, self.recommendations, line]
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
            description = """
            Yo! I'm Tony Hawk, a pretty famous skateboarder dude. I also give sick movie recs,
            so if you gimme 5 movies that you've seen and let me know how you felt about them, I can
            hit you with some fire movie recs. I'm so stoked to help ya out.
            """
        else:
            description = """
                Hi! I'm an interactive chatbot named Oscar! I can give you movie recommendations
                if you tell me 5 movies that you've seen and how you felt about them. This can
                be anything ranging from "I like this movie" to "I despised this movie" and
                anything in between. You can also specify how many movie recommendations you
                would like, and I can tell you that many movies that I think you'll like!
                """
        return description


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
