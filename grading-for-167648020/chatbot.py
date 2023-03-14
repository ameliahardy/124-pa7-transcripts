import util
import numpy as np
import re
import math
import string
from itertools import product, tee
import gzip
import functools


# noinspection PyMethodMayBeStatic
class Chatbot:
    def __init__(self, creative=False):
        self.name = 'DanimuraBot'
        self.creative = creative
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')
        self.pset_titles = {}
        with open('data/movies.txt', 'r') as db:
            for line in db:
                index, title, genres = line.strip().split('%')
                genres = genres.split('|')
                self.pset_titles[title] = {'index': int(index), 'genres': genres}
        self.indices_to_titles = {title_dict['index']: title for title, title_dict in self.pset_titles.items()}
        self.count = 0
        self.uprof = np.zeros(len(ratings))
        self.rec = []
        self.index = 0
        self.ratings = self.binarize(ratings)
        self.clarify = 'OFF'
        self.SPELL_CHECKING = 'OFF'
        self.recommend_mode = 'OFF'

    def greeting(self):
        if self.creative:
            greeting_message = "Hi, Yoda Moviebot, I am! About your taste in movies, tell me you will. Recommend a movie for you, I shall! A movie you like, tell me (and please the title in quotation marks put!)"
        else:
            greeting_message = "HELLO I AM HERE TO ASSIST YOU IN SELECTION OF FINE FILMS"
        return greeting_message

    def goodbye(self):
        if self.creative:
            goodbye_message = "May the Force be with you!"
        else:
            goodbye_message = "Have a nice day!"
        return goodbye_message

    def process(self, line):
        if self.creative:
            l = line.lower()

            if self.clarify == 'ON':
                ret = self.disambiguate(line, self.candidates)
                if ret:
                    index = ret[0]
                    title = self.indices_to_titles[ret[0]]
                else:
                    return 'Clarification does not seem to match any movies, Yodabot is afraid. Try again I request.'
                self.clarify = 'OFF'
                sent = self.disamb_sent
                if sent > 0:
                    response = "Glad to hear that you liked '"+ title+ ", am I.'"
                    self.count += 1
                    self.uprof[index] = sent

                elif sent == 0:
                    response = "I apologize! I'm new to the world, and still trying to figure out how to process emotions (my own and other people's). Based on what you said, I'm not sure if you liked '"""+ title +".' Tell me more about it."
                else:
                    response = "Oh, so you didn't like '"+ title+ ".' It happens!"
                    self.count += 1
                    self.uprof[index] = sent
                if self.count == 5:
                    self.rec = self.recommend(self.uprof, self.ratings, len(self.pset_titles) - 5)
                    self.recommend_mode = 'ON'
                    response += " All right, that's enough for me to make a recommendation! I recommend '" + self.indices_to_titles[self.rec[self.index]] + ".' Would you like to hear another recommendation? (Please say 'yes' if you want one, or enter :quit if you're done)."
                    self.index += 1
                else:
                    response += " Tell me about another movie."

                return response




            if self.SPELL_CHECKING == 'OFF' and l in ["yes", "y", "yeah", "yup" , "yeh"] and self.count == 5:
                response = "Make a recommendation, I can! 'All right, enough for me that is. Recommend, I do '" + self.indices_to_titles[self.rec[self.index]] + ".' Another recommendation, you want to hear? Say 'yes', if one more you desire. If done, enter ':quit'."
                return response
            elif self.count == 5:
                return "Understand, I did not. Say 'yes', if one more you desire. If done, enter ':quit'."

            title = self.extract_titles(line)
            if self.SPELL_CHECKING == 'ON':
                title = ['blank']
            if len(title) > 1:
                response = "One movie at a time, list, can I. Sorry, I am. Patience you must have, hmmm."

            elif title == []:
                response = "Sorry, I am! Understand, I do not. About a movie, please tell me -- put the title in quotation marks, you must!"

            else:
                movies = self.find_movies_by_title(title[0])

                if self.SPELL_CHECKING == 'ON':
                    if l == 'no':
                        self.SPELL_CHECKING = 'OFF'
                        return 'Mistake is mine then afraid I am, please continue telling me about your movie preferences!'
                    elif l == 'yes':
                        movies = [self.nearest_index]
                        title = [self.indices_to_titles[self.nearest_index]]
                        self.SPELL_CHECKING = 'OFF'
                    else:
                        return "Not understand you did I. Please write 'yes' or 'no'."


                if movies == []:
                    sketchy_title = title[0]
                    nearest_indices = self.find_movies_closest_to_title(sketchy_title)
                    if nearest_indices:
                        self.nearest_index = nearest_indices[0]
                        self.SPELL_CHECKING = 'ON'
                        response = f"Seen {self.indices_to_titles[self.nearest_index]} you have, wondering am I? Please write 'yes' or 'no', I am hoping you will."
                    else:
                        response = "Hmm, interesting that is. Never heard of '" + title[0] + ",' I have. Watch it with you, would love to at some point! Another movie that you liked, please tell me."
                    return response

                if len(movies) > 1:
                    self.clarify = 'ON'
                    self.candidates = movies
                    self.disamb_sent = self.extract_sentiment(line)
                    response = "Hmm, found more than one movie called '" + title[0] + "' have I. Which one did you mean, I am wondering?\n"
                    for movie in movies:
                        response += f"- {self.indices_to_titles[movie]}\n"
                    response += "Clarify the specific version you liked, I am hoping you will."

                else:
                    sent = self.extract_sentiment(line)
                    if sent > 0:
                        response = "Glad to hear that you liked, '" + title[0] + "' I am."
                        self.count += 1
                        self.uprof[movies[0]] = sent

                    elif sent == 0:
                        response = "Process emotions, it takes time. About '" + title[0] + "' tell me more, you must. Like it, did you?"
                    else:
                        response = "Oh, liked '" + title[0] + "' you did not. Happens, it does! Yes, hmmm."
                        self.count += 1
                        self.uprof[movies[0]] = sent

                    if self.count == 5:
                        self.recommend_mode == 'ON'
                        self.rec = self.recommend(self.uprof, self.ratings, len(self.pset_titles))
                        response += " All right, enough for me that is. A recommendation, I can make - '" + self.indices_to_titles[self.rec[self.index]] + ".' Another recommendation, you want to hear? Say 'yes', if one you desire. If done, enter ':quit', hmmm."
                        self.index += 1

                    else:
                        response += " Force I have, but need I must to hear about another movie."

        else:  # starter mode
            l = line.lower()
            if l in ['yes', 'y', 'yeah', 'yup', 'yeh'] and self.count == 5:
                response = "All right, that's enough for me to make a recommendation! I recommend '" + self.indices_to_titles[self.rec[self.index]] + ".' Would you like to hear another recommendation? (Please say 'yes' if you want one, or enter :quit if you're done)."
                self.index += 1
                return response

            title = self.extract_titles(line)
            if len(title) > 1:
                response = "Sorry, could you list one movie at a time, please?"

            elif title == []:
                response = "Sorry! I'm not sure I understand. Please tell me about what you thought about a movie (and please put the movie title in quotation marks)"

            else:
                movies = self.find_movies_by_title(title[0])

                if movies == []:
                    response = "Hmm, interesting. I've never heard of '"+ title[0] + ",' but would love to watch it with you at some point! In the meantime, tell me about another movie that you liked."

                elif len(movies) > 1:
                    response = "I found more than one movie called '"+ title[0] +".' Could you clarify the specific version you liked?"

                else:
                    sent = self.extract_sentiment(line)
                    if sent > 0:
                        response = "Glad to hear that you liked '"+ title[0]+ ".'"
                        self.count += 1
                        self.uprof[movies[0]] = sent

                    elif sent == 0:
                        response = "I apologize! I'm new to the world, and still trying to figure out how to process emotions (my own and other people's). Based on what you said, I'm not sure if you liked '"""+ title[0] +".' Tell me more about it."
                    else:
                        response = "Oh, so you didn't like '"+ title[0]+ ".' It happens!"
                        self.count += 1
                        self.uprof[movies[0]] = sent

                    if self.count == 5:
                        self.rec = self.recommend(self.uprof, self.ratings, len(self.pset_titles) - 5)
                        response += " All right, that's enough for me to make a recommendation! I recommend '" + self.indices_to_titles[self.rec[self.index]] + ".' Would you like to hear another recommendation? (Please say 'yes' if you want one, or enter :quit if you're done)."
                        self.index += 1
                    else:
                        response += " Tell me about another movie."
        return response

    @staticmethod
    def preprocess(text):
        return text

    def extract_titles(self, preprocessed_input):
        titles = re.findall('"([^"]+)"', preprocessed_input)
        if self.creative:
            preprocessed_input = preprocessed_input.lower()
            for t in self.pset_titles:
                clean_t = clean_title(t)
                if f' {clean_t} ' in preprocessed_input or (len(clean_t) > 6 and clean_t in preprocessed_input):
                    titles.append(t[:-7])
        return list(set(titles))

    def find_movies_by_title(self, title):
        ARTICLES = ['The', 'An', 'A', 'El', 'La', 'Las', 'Los', 'Le', 'Les', 'Der', 'Das',
                    'Die']
        query_title = title
        query_year = re.findall(r'\d{4}', query_title)
        if query_year:
            query_year = query_year[0]
            if '(' in query_title:
                query_title = query_title[:query_title.index('(')]
        for article in ARTICLES:
            query_title = removeprefix(query_title, article + ' ')
            query_title = removesuffix(query_title, ', ' + article)
        query_title = query_title.strip()

        indices = []
        for db_title in self.pset_titles:
            try:
                if self.creative:
                    query_title = query_title.lower()
                    orig_title = db_title
                    db_title = db_title.lower()
                    if (query_title in db_title and (not query_year or query_year in db_title) and re.findall(rf'{query_title}(?:[^a-z]|$)', db_title)):
                        indices.append(self.pset_titles[orig_title]['index'])
                else:
                    if (query_title in db_title and (not query_year or query_year in db_title) and re.findall(rf'{query_title}(?:,| \(|$)', db_title)):
                        indices.append(self.pset_titles[db_title]['index'])
            except:
                pass
        return indices

    def extract_sentiment(self, preprocessed_input):
        sia = Sia()
        scores = sia.polarity_scores(re.sub(r'"[A-Za-z0-9 ]+"', '', preprocessed_input))
        scores = [scores['neg'], scores['neu'] - 0.5, scores['pos']]
        sent_diff = scores[0] - scores[2]
        if sent_diff > 0.55 and self.creative:
            return -2
        elif sent_diff < -0.55 and self.creative:  # misses: "I really really really really loved "Titanic (1997)"
            return 2
        else:
            return np.argmax(scores) - 1

    def extract_sentiment_for_movies(self, preprocessed_input):
        pass

    def find_movies_closest_to_title(self, title, max_distance=3):
        min_distance = max_distance
        title = clean_title(title)
        close_movies = []
        for database_title in self.pset_titles:
            db_title = clean_title(database_title)
            curr_distance = edit_distance(title, db_title)
            if curr_distance < min_distance:
                close_movies.clear()
                min_distance = curr_distance
            if curr_distance == min_distance:
                close_movies.append(self.pset_titles[database_title]['index'])
        return close_movies

    def disambiguate(self, clarification, candidates):
        relevant = []
        clarification = clarification.lower()
        for candidate in candidates:
            title = self.indices_to_titles[candidate].lower()
            if clarification.isnumeric():
                w_space = " " + clarification + " "
                w_comma = " " + clarification + ","
                w_paren = "(" + clarification + ")"
                if w_space in title or w_comma in title or w_paren in title:
                    relevant.append(candidate)
            else:
                if clarification in title:
                    relevant.append(candidate)
        return relevant

    @staticmethod
    def binarize(ratings, threshold=2.5):
        bin_ratings = np.where(np.logical_and(ratings <= threshold, ratings != 0), -1, ratings)
        bin_ratings = np.where(bin_ratings > threshold, 1, bin_ratings)
        return bin_ratings

    def similarity(self, u, v):
        similarity = u @ v / (np.linalg.norm(u) * np.linalg.norm(v))
        return similarity

    def recommend(self, user_ratings, ratings_matrix, k=10):
        A = ratings_matrix
        unrated_indices = np.asarray(user_ratings == 0).nonzero()[0]
        rated_indices = user_ratings.nonzero()[0]

        unrated_movie_scores = np.empty((0, 2))
        for i in unrated_indices:
            score = 0
            for j in rated_indices:
                if np.linalg.norm(A[i]) == 0 or np.linalg.norm(A[j]) == 0:
                    cos_sim = 0
                else:
                    cos_sim = A[i] @ A[j] / (np.linalg.norm(A[i]) * np.linalg.norm(A[j]))
                score += cos_sim * user_ratings[j]
            unrated_movie_scores = np.vstack([unrated_movie_scores, [i, score]])
        recs = unrated_movie_scores[unrated_movie_scores[:, 1].argsort()][-k:][:, 0]
        recommendations = list(reversed(recs.astype('int')))
        return recommendations

    def debug(self, line):
        debug_info = 'debug info'
        return debug_info

    def intro(self):
        return """
        Our chatbot is warm and fuzzy and loves movies. Have fun with
        general version or yoda-version :-)
        """


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')


# ED implementation: leetcode.com/problems/edit-distance/solutions/3230538/python3-easy-solution/
def edit_distance(word1, word2):
    m, n = len(word1), len(word2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        dp[i][0] = i
    for j in range(1, n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i - 1] == word2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = min(
                    dp[i - 1][j] + 1,
                    dp[i][j - 1] + 1,
                    dp[i - 1][j - 1] + 1
                )
    return dp[m][n]


def clean_title(title):
    title = title.lower()
    ARTICLES = ['The', 'An', 'A', 'El', 'La', 'Las', 'Los', 'Le', 'Les', 'Der', 'Das',
                'Die', 'the']
    if re.findall(r'\d{4}', title):
        try:
            title = title[:-6]
        except:
            pass
    title = title.strip(', "')
    for article in ARTICLES:
        title = removeprefix(title, article + ' ')
        title = removesuffix(title, ', ' + article)
    title = title.strip(', "')
    return title


def removeprefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


def removesuffix(text, prefix):
    if text.endswith(prefix):
        return text[:-len(prefix)]
    return text


def pairwise(iterable):
    """s -> (s0,s1), (s1,s2), (s2, s3), ..."""
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


"""
Credit NLTK (sentiment classes: VaderConstants, ST, Sia)
Before using:
    - Checked NLTK restrictions on Ed
    - Attended Angela/Jennifer OH and received confirmation that all use of NLTK is
      accepted for this assignment given proper citation and assuming risk for potential
      autograder errors
    - Directly asked Dan & he approved


Hutto, C.J. & Gilbert, E.E. (2014). VADER: A Parsimonious Rule-based Model for
Sentiment Analysis of Social Media Text. Eighth International Conference on
Weblogs and Social Media (ICWSM-14). Ann Arbor, MI, June 2014.
"""
class VaderConstants:
    B_INCR = 0.293
    B_DECR = -0.293
    C_INCR = 0.733
    N_SCALAR = -0.74

    NEGATE = {
        "aint",
        "arent",
        "cannot",
        "cant",
        "couldnt",
        "darent",
        "didnt",
        "doesnt",
        "ain't",
        "aren't",
        "can't",
        "couldn't",
        "daren't",
        "didn't",
        "doesn't",
        "dont",
        "hadnt",
        "hasnt",
        "havent",
        "isnt",
        "mightnt",
        "mustnt",
        "neither",
        "don't",
        "hadn't",
        "hasn't",
        "haven't",
        "isn't",
        "mightn't",
        "mustn't",
        "neednt",
        "needn't",
        "never",
        "none",
        "nope",
        "nor",
        "not",
        "nothing",
        "nowhere",
        "oughtnt",
        "shant",
        "shouldnt",
        "uhuh",
        "wasnt",
        "werent",
        "oughtn't",
        "shan't",
        "shouldn't",
        "uh-uh",
        "wasn't",
        "weren't",
        "without",
        "wont",
        "wouldnt",
        "won't",
        "wouldn't",
        "rarely",
        "seldom",
        "despite",
    }

    BOOSTER_DICT = {
        "absolutely": B_INCR,
        "amazingly": B_INCR,
        "awfully": B_INCR,
        "completely": B_INCR,
        "considerably": B_INCR,
        "decidedly": B_INCR,
        "deeply": B_INCR,
        "effing": B_INCR,
        "enormously": B_INCR,
        "entirely": B_INCR,
        "especially": B_INCR,
        "exceptionally": B_INCR,
        "extremely": B_INCR,
        "fabulously": B_INCR,
        "flipping": B_INCR,
        "flippin": B_INCR,
        "fricking": B_INCR,
        "frickin": B_INCR,
        "frigging": B_INCR,
        "friggin": B_INCR,
        "fully": B_INCR,
        "fucking": B_INCR,
        "greatly": B_INCR,
        "hella": B_INCR,
        "highly": B_INCR,
        "hugely": B_INCR,
        "incredibly": B_INCR,
        "intensely": B_INCR,
        "majorly": B_INCR,
        "more": B_INCR,
        "most": B_INCR,
        "particularly": B_INCR,
        "purely": B_INCR,
        "quite": B_INCR,
        "really": B_INCR,
        "remarkably": B_INCR,
        "so": B_INCR,
        "substantially": B_INCR,
        "thoroughly": B_INCR,
        "totally": B_INCR,
        "tremendously": B_INCR,
        "uber": B_INCR,
        "unbelievably": B_INCR,
        "unusually": B_INCR,
        "utterly": B_INCR,
        "very": B_INCR,
        "almost": B_DECR,
        "barely": B_DECR,
        "hardly": B_DECR,
        "just enough": B_DECR,
        "kind of": B_DECR,
        "kinda": B_DECR,
        "kindof": B_DECR,
        "kind-of": B_DECR,
        "less": B_DECR,
        "little": B_DECR,
        "marginally": B_DECR,
        "occasionally": B_DECR,
        "partly": B_DECR,
        "scarcely": B_DECR,
        "slightly": B_DECR,
        "somewhat": B_DECR,
        "sort of": B_DECR,
        "sorta": B_DECR,
        "sortof": B_DECR,
        "sort-of": B_DECR,
    }

    SPECIAL_CASE_IDIOMS = {
        "the shit": 3,
        "the bomb": 3,
        "bad ass": 1.5,
        "yeah right": -2,
        "cut the mustard": 2,
        "kiss of death": -1.5,
        "hand to mouth": -2,
    }

    REGEX_REMOVE_PUNCTUATION = re.compile(f"[{re.escape(string.punctuation)}]")

    PUNC_LIST = [
        ".",
        "!",
        "?",
        ",",
        ";",
        ":",
        "-",
        "'",
        '"',
        "!!",
        "!!!",
        "??",
        "???",
        "?!?",
        "!?!",
        "?!?!",
        "!?!?",
    ]

    def __init__(self):
        pass

    def negated(self, input_words, include_nt=True):
        neg_words = self.NEGATE
        if any(word.lower() in neg_words for word in input_words):
            return True
        if include_nt:
            if any("n't" in word.lower() for word in input_words):
                return True
        for first, second in pairwise(input_words):
            if second.lower() == "least" and first.lower() != "at":
                return True
        return False

    def normalize(self, score, alpha=15):
        norm_score = score / math.sqrt((score * score) + alpha)
        return norm_score

    def scalar_inc_dec(self, word, valence, is_cap_diff):
        scalar = 0.0
        word_lower = word.lower()
        if word_lower in self.BOOSTER_DICT:
            scalar = self.BOOSTER_DICT[word_lower]
            if valence < 0:
                scalar *= -1
            # check if booster/dampener word is in ALLCAPS (while others aren't)
            if word.isupper() and is_cap_diff:
                if valence > 0:
                    scalar += self.C_INCR
                else:
                    scalar -= self.C_INCR
        return scalar


class ST:
    def __init__(self, text, punc_list, regex_remove_punctuation):
        if not isinstance(text, str):
            text = str(text.encode("utf-8"))
        self.text = text
        self.PUNC_LIST = punc_list
        self.REGEX_REMOVE_PUNCTUATION = regex_remove_punctuation
        self.words_and_emoticons = self._words_and_emoticons()
        self.is_cap_diff = self.allcap_differential(self.words_and_emoticons)

    def _words_plus_punc(self):
        no_punc_text = self.REGEX_REMOVE_PUNCTUATION.sub("", self.text)
        words_only = no_punc_text.split()
        words_only = {w for w in words_only if len(w) > 1}
        punc_before = {"".join(p): p[1] for p in product(self.PUNC_LIST, words_only)}
        punc_after = {"".join(p): p[0] for p in product(words_only, self.PUNC_LIST)}
        words_punc_dict = punc_before
        words_punc_dict.update(punc_after)
        return words_punc_dict

    def _words_and_emoticons(self):
        wes = self.text.split()
        words_punc_dict = self._words_plus_punc()
        wes = [we for we in wes if len(we) > 1]
        for i, we in enumerate(wes):
            if we in words_punc_dict:
                wes[i] = words_punc_dict[we]
        return wes

    def allcap_differential(self, words):
        is_different = False
        allcap_words = 0
        for word in words:
            if word.isupper():
                allcap_words += 1
        cap_differential = len(words) - allcap_words
        if 0 < cap_differential < len(words):
            is_different = True
        return is_different


class Sia:
    def __init__(
        self,
        lexicon_file="./deps/vader_lexicon.txt.gz",
    ):
        with gzip.open(lexicon_file, 'r') as lex_file:
            self.lexicon_file = lex_file.read().decode().strip()
        self.lexicon = self.make_lex_dict()
        self.constants = VaderConstants()

    def make_lex_dict(self):
        lex_dict = {}
        for i, line in enumerate(self.lexicon_file.split("\n")):
            (word, measure) = line.strip().split("\t")[0:2]
            lex_dict[word] = float(measure)
        return lex_dict

    def polarity_scores(self, text):
        st = ST(
            text, self.constants.PUNC_LIST, self.constants.REGEX_REMOVE_PUNCTUATION
        )
        sentiments = []
        words_and_emoticons = st.words_and_emoticons
        for item in words_and_emoticons:
            valence = 0
            i = words_and_emoticons.index(item)
            if (
                i < len(words_and_emoticons) - 1
                and item.lower() == "kind"
                and words_and_emoticons[i + 1].lower() == "of"
            ) or item.lower() in self.constants.BOOSTER_DICT:
                sentiments.append(valence)
                continue

            sentiments = self.sentiment_valence(valence, st, item, i, sentiments)

        sentiments = self._but_check(words_and_emoticons, sentiments)

        return self.score_valence(sentiments, text)

    def sentiment_valence(self, valence, st, item, i, sentiments):
        is_cap_diff = st.is_cap_diff
        words_and_emoticons = st.words_and_emoticons
        item_lowercase = item.lower()
        if item_lowercase in self.lexicon:
            # get the sentiment valence
            valence = self.lexicon[item_lowercase]

            # check if sentiment laden word is in ALL CAPS (while others aren't)
            if item.isupper() and is_cap_diff:
                if valence > 0:
                    valence += self.constants.C_INCR
                else:
                    valence -= self.constants.C_INCR

            for start_i in range(0, 3):
                if (
                    i > start_i
                    and words_and_emoticons[i - (start_i + 1)].lower()
                    not in self.lexicon
                ):
                    s = self.constants.scalar_inc_dec(
                        words_and_emoticons[i - (start_i + 1)], valence, is_cap_diff
                    )
                    if start_i == 1 and s != 0:
                        s = s * 0.95
                    if start_i == 2 and s != 0:
                        s = s * 0.9
                    valence = valence + s
                    valence = self._never_check(
                        valence, words_and_emoticons, start_i, i
                    )
                    if start_i == 2:
                        valence = self._idioms_check(valence, words_and_emoticons, i)

            valence = self._least_check(valence, words_and_emoticons, i)

        sentiments.append(valence)
        return sentiments

    def _least_check(self, valence, words_and_emoticons, i):
        if (
            i > 1
            and words_and_emoticons[i - 1].lower() not in self.lexicon
            and words_and_emoticons[i - 1].lower() == "least"
        ):
            if (
                words_and_emoticons[i - 2].lower() != "at"
                and words_and_emoticons[i - 2].lower() != "very"
            ):
                valence = valence * self.constants.N_SCALAR
        elif (
            i > 0
            and words_and_emoticons[i - 1].lower() not in self.lexicon
            and words_and_emoticons[i - 1].lower() == "least"
        ):
            valence = valence * self.constants.N_SCALAR
        return valence

    def _but_check(self, words_and_emoticons, sentiments):
        words_and_emoticons = [w_e.lower() for w_e in words_and_emoticons]
        but = {"but"} & set(words_and_emoticons)
        if but:
            bi = words_and_emoticons.index(next(iter(but)))
            for sidx, sentiment in enumerate(sentiments):
                if sidx < bi:
                    sentiments[sidx] = sentiment * 0.5
                elif sidx > bi:
                    sentiments[sidx] = sentiment * 1.5
        return sentiments

    def _idioms_check(self, valence, words_and_emoticons, i):
        onezero = f"{words_and_emoticons[i - 1]} {words_and_emoticons[i]}"

        twoonezero = "{} {} {}".format(
            words_and_emoticons[i - 2],
            words_and_emoticons[i - 1],
            words_and_emoticons[i],
        )

        twoone = f"{words_and_emoticons[i - 2]} {words_and_emoticons[i - 1]}"

        threetwoone = "{} {} {}".format(
            words_and_emoticons[i - 3],
            words_and_emoticons[i - 2],
            words_and_emoticons[i - 1],
        )

        threetwo = "{} {}".format(
            words_and_emoticons[i - 3], words_and_emoticons[i - 2]
        )

        sequences = [onezero, twoonezero, twoone, threetwoone, threetwo]

        for seq in sequences:
            if seq in self.constants.SPECIAL_CASE_IDIOMS:
                valence = self.constants.SPECIAL_CASE_IDIOMS[seq]
                break

        if len(words_and_emoticons) - 1 > i:
            zeroone = f"{words_and_emoticons[i]} {words_and_emoticons[i + 1]}"
            if zeroone in self.constants.SPECIAL_CASE_IDIOMS:
                valence = self.constants.SPECIAL_CASE_IDIOMS[zeroone]
        if len(words_and_emoticons) - 1 > i + 1:
            zeroonetwo = "{} {} {}".format(
                words_and_emoticons[i],
                words_and_emoticons[i + 1],
                words_and_emoticons[i + 2],
            )
            if zeroonetwo in self.constants.SPECIAL_CASE_IDIOMS:
                valence = self.constants.SPECIAL_CASE_IDIOMS[zeroonetwo]

        if (
            threetwo in self.constants.BOOSTER_DICT
            or twoone in self.constants.BOOSTER_DICT
        ):
            valence = valence + self.constants.B_DECR
        return valence

    def _never_check(self, valence, words_and_emoticons, start_i, i):
        if start_i == 0:
            if self.constants.negated([words_and_emoticons[i - 1]]):
                valence = valence * self.constants.N_SCALAR
        if start_i == 1:
            if words_and_emoticons[i - 2] == "never" and (
                words_and_emoticons[i - 1] == "so"
                or words_and_emoticons[i - 1] == "this"
            ):
                valence = valence * 1.5
            elif self.constants.negated([words_and_emoticons[i - (start_i + 1)]]):
                valence = valence * self.constants.N_SCALAR
        if start_i == 2:
            if (
                words_and_emoticons[i - 3] == "never"
                and (
                    words_and_emoticons[i - 2] == "so"
                    or words_and_emoticons[i - 2] == "this"
                )
                or (
                    words_and_emoticons[i - 1] == "so"
                    or words_and_emoticons[i - 1] == "this"
                )
            ):
                valence = valence * 1.25
            elif self.constants.negated([words_and_emoticons[i - (start_i + 1)]]):
                valence = valence * self.constants.N_SCALAR
        return valence

    def _punctuation_emphasis(self, sum_s, text):
        ep_amplifier = self._amplify_ep(text)
        qm_amplifier = self._amplify_qm(text)
        punct_emph_amplifier = ep_amplifier + qm_amplifier
        return punct_emph_amplifier

    def _amplify_ep(self, text):
        ep_count = text.count("!")
        if ep_count > 4:
            ep_count = 4
        ep_amplifier = ep_count * 0.292
        return ep_amplifier

    def _amplify_qm(self, text):
        qm_count = text.count("?")
        qm_amplifier = 0
        if qm_count > 1:
            if qm_count <= 3:
                qm_amplifier = qm_count * 0.18
            else:
                qm_amplifier = 0.96
        return qm_amplifier

    def _sift_sentiment_scores(self, sentiments):
        pos_sum = 0.0
        neg_sum = 0.0
        neu_count = 0
        for sentiment_score in sentiments:
            if sentiment_score > 0:
                pos_sum += (
                    float(sentiment_score) + 1
                )
            if sentiment_score < 0:
                neg_sum += (
                    float(sentiment_score) - 1
                )
            if sentiment_score == 0:
                neu_count += 1
        return pos_sum, neg_sum, neu_count

    def score_valence(self, sentiments, text):
        if sentiments:
            sum_s = float(sum(sentiments))
            punct_emph_amplifier = self._punctuation_emphasis(sum_s, text)
            if sum_s > 0:
                sum_s += punct_emph_amplifier
            elif sum_s < 0:
                sum_s -= punct_emph_amplifier

            compound = self.constants.normalize(sum_s)
            pos_sum, neg_sum, neu_count = self._sift_sentiment_scores(sentiments)

            if pos_sum > math.fabs(neg_sum):
                pos_sum += punct_emph_amplifier
            elif pos_sum < math.fabs(neg_sum):
                neg_sum -= punct_emph_amplifier

            total = pos_sum + math.fabs(neg_sum) + neu_count
            pos = math.fabs(pos_sum / total)
            neg = math.fabs(neg_sum / total)
            neu = math.fabs(neu_count / total)

        else:
            compound = 0.0
            pos = 0.0
            neg = 0.0
            neu = 0.0

        sentiment_dict = {
            "neg": round(neg, 3),
            "neu": round(neu, 3),
            "pos": round(pos, 3),
            "compound": round(compound, 4),
        }

        return sentiment_dict
