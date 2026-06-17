# Color themes for the Chessboard and UI annotations

# Chessboard Square Colors (light, dark)
BOARD_THEMES = {
    "Green (Chess.com)": {
        "light": "#eeeed2",
        "dark": "#769656",
        "name": "Green"
    },
    "Tournament (Lichess)": {
        "light": "#f0d9b5",
        "dark": "#b58863",
        "name": "Brown"
    },
    "Blue (Modern)": {
        "light": "#dee3e6",
        "dark": "#8ca2ad",
        "name": "Blue"
    },
    "Sleek Dark": {
        "light": "#474747",
        "dark": "#2b2b2b",
        "name": "Dark"
    }
}

# Highlights
HIGHLIGHTS = {
    "selected": {
        "color": "#1e90ff",       # Dodger Blue
        "width": 3
    },
    "last_move": {
        "light": "#f7f785",      # Translucent yellow on light
        "dark": "#baca44"        # Translucent olive on dark
    },
    "valid_move": {
        "color": "#155f15",      # Green dot
        "alpha": 0.3
    },
    "drawings": {
        "green": "#15a850",
        "red": "#e23a3a",
        "blue": "#3592e8",
        "orange": "#f39c12"
    }
}

# Move Annotations (Chess.com style badges)
# Maps NAG value to label, circle color, and text color
# NAG values:
# 3 = Brilliant (!!)
# 1 = Great Move (!)  (Note: NAG 1 in PGN is technically 'good move', but we can display it as Great/Good. Let's make it Great '!' and have separate Book/Good)
# 5 = Interesting (!?)
# 6 = Dubious (?!)
# 2 = Mistake (?)
# 4 = Blunder (??)
ANNOTATION_THEMES = {
    3: {
        "symbol": "!!",
        "name": "Brilliant",
        "bg": "#11b5e4",         # Electric bright blue
        "fg": "#ffffff",
        "desc": "Brilliant Move"
    },
    1: {
        "symbol": "!",
        "name": "Great",
        "bg": "#10b981",         # Emerald green
        "fg": "#ffffff",
        "desc": "Great Move"
    },
    5: {
        "symbol": "!?",
        "name": "Interesting",
        "bg": "#a855f7",         # Purple
        "fg": "#ffffff",
        "desc": "Interesting Move"
    },
    6: {
        "symbol": "?!",
        "name": "Inaccuracy",
        "bg": "#eab308",         # Yellow
        "fg": "#ffffff",
        "desc": "Inaccuracy"
    },
    2: {
        "symbol": "?",
        "name": "Mistake",
        "bg": "#f97316",         # Orange
        "fg": "#ffffff",
        "desc": "Mistake"
    },
    4: {
        "symbol": "??",
        "name": "Blunder",
        "bg": "#ef4444",         # Red
        "fg": "#ffffff",
        "desc": "Blunder"
    }
}

# Map strings to NAG numbers
ANNOTATION_STR_TO_NAG = {
    "!!": 3,
    "!": 1,
    "!?": 5,
    "?!": 6,
    "?": 2,
    "??": 4
}
