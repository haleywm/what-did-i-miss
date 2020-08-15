"""
    CONFIGURATION OPTIONS FOR MODULE: WHATDIDIMISS
"""

ENABLED = True

MAX_TIME = '7d'             # Valid units: m, d, h
DEFAULT_TIME = '6h'         # Setting this value too high or negative can cause overflow errors
MAX_LOOKBACK_TIME = '5d'

COOLDOWN = '30s'            # Per user, per channel

STRIP = '.,!?\'"`'          # Stripped from the front and end of words
IGNORE_MESSAGE_TIME = '2m'  # Recent messages will be left out of the generated wordcloud
STOPWORDS = []              # Create a list of ignored words from the stopwords.txt file in the wordcloud directory

try:
    stopwords_file = open("stopwords.txt")

    for word in stopwords_file:
        STOPWORDS.append(word.strip())
except Exception as e:
    print(e)


"""
    CONFIGURATION OPTIONS FOR MODULE: WORDCLOUD
"""

SCALE = 2
WIDTH = 600
HEIGHT = 300
LIMIT = 0.5
TINT = True
ROTATE = True
CACHE = 'cache/'
FONT_PATH = 'fonts/MergedFonts.ttf'

# Acceptable colour name formats listed at:
# https://pillow.readthedocs.io/en/stable/reference/ImageColor.html#color-names
# None means transparent
BACKGROUND_COLOUR = None
OUTLINE_COLOUR = 'grey'
OUTLINE_THICKNESS = 4
