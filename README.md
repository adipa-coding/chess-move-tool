# Chess Move Tool & PGN Analyzer

A desktop application for analyzing chess positions, recording opening variations, annotating moves, and importing/exporting games using PGN files. Built using Python, **CustomTkinter** for a modern dark-themed GUI, and the **python-chess** library for game rules validation.

---

## Features

- **Interactive Chessboard**: Fully-featured board with drag-and-drop support (or clicking start and end squares) for playing moves. Supports flipping the board direction.
- **Dynamic Opening Recognition**: Displays the ECO code and opening/variation name dynamically as you play (e.g., *C50 Giuoco Piano*). Matches the closest book variation if you branch off into custom moves.
- **Interactive Move Tree**: Displays a Lichess-style variation tree showing main lines, nested branches, move numbers, and inline annotations.
- **Move Annotations**: Annotate moves with Chess.com/Lichess-style badges:
  - 🌟 Brilliant (`!!`)
  - ⭐ Great (`!`)
  - 🔍 Interesting (`!?`)
  - ⚠️ Inaccuracy (`?!`)
  - ❌ Mistake (`?`)
  - 🔴 Blunder (`??`)
- **Move Comments**: Enter analysis comments on a position-by-position basis, which are auto-saved and formatted inline within the move tree.
- **Header Metadata Editor**: Edit game details such as Event, Site, Date, Players, and Result, with metadata automatically saved to the output PGN headers.
- **PGN Clipboard & File Support**:
  - Load PGN games from files or paste PGN data directly from your clipboard (Lichess / Chess.com exports).
  - Save your analysis as a standard PGN file, or copy it directly to your clipboard.
- **Keyboard Navigation**: Use arrow keys for fast review:
  - `Left` / `Right`: Go backward / forward by one move.
  - `Up` / `Down`: Jump to the starting position / end of the current variation.
- **Automatic Resume (Autosave)**: Saves your active analysis to `autosave.pgn` on every move, automatically reloading your work when the application restarts.
- **Visual Customization**: Toggle between board colors (Green, Blue, Wood, Grey, etc.) and piece sets (Neo, Classic, Wood) on the fly.

---

## Installation

### Prerequisites
Make sure you have Python installed. The application is compatible with Python 3.10 and above.

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/chess-move-tool.git
cd chess-move-tool
```

### Step 2: Install Dependencies
Install the required python packages:
```bash
pip install chess customtkinter Pillow
```

### Step 3 (Optional): Initialize Openings Database
The project comes with a pre-compiled `openings.json` file. If you ever need to rebuild or update the openings list from the latest Lichess openings repository:
```bash
python compile_openings.py
```

---

## How to Run
Execute the main application file:
```bash
python main.py
```

---

## Project Structure

- `main.py`: The entry point containing the CustomTkinter GUI layout, UI event bindings, and tabs.
- `chess_board.py`: Manages chessboard rendering, square coloring, coordinates, drawing arrows/highlights, and move logic.
- `game_manager.py`: Manages the underlying game state, move trees, variations, PGN imports/exports, autosaving, and opening name resolution.
- `theme.py`: Configures application color palettes, board theme presets, and move annotation NAG styles.
- `compile_openings.py`: Utility script that downloads, parses, and compiles Lichess's open-source ECO database to `openings.json` using normalized FEN keys.
- `openings.json`: The compiled database of 3,700+ opening variants, providing fast, offline opening recognition.

---

## License
This project is open-source and available under the [MIT License](LICENSE).
