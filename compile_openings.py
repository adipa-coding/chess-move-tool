import chess.pgn
import io
import json
import urllib.request
import os

urls = {
    'A': "https://raw.githubusercontent.com/lichess-org/chess-openings/master/a.tsv",
    'B': "https://raw.githubusercontent.com/lichess-org/chess-openings/master/b.tsv",
    'C': "https://raw.githubusercontent.com/lichess-org/chess-openings/master/c.tsv",
    'D': "https://raw.githubusercontent.com/lichess-org/chess-openings/master/d.tsv",
    'E': "https://raw.githubusercontent.com/lichess-org/chess-openings/master/e.tsv"
}

openings_db = {}

# Process each TSV
for letter, url in urls.items():
    print(f"Downloading and parsing {letter}.tsv...")
    try:
        response = urllib.request.urlopen(url)
        data = response.read().decode('utf-8')
        lines = data.strip().split('\n')
        
        # Parse lines
        count = 0
        for line in lines[1:]:
            parts = line.split('\t')
            if len(parts) >= 3:
                eco = parts[0]
                name = parts[1]
                pgn_moves = parts[2]
                
                # Use python-chess to parse the moves and get the FEN
                game = chess.pgn.read_game(io.StringIO(pgn_moves))
                if game:
                    board = game.board()
                    for move in game.mainline_moves():
                        board.push(move)
                    
                    # Get normalized FEN (first 4 fields)
                    fen = board.fen()
                    normalized_fen = " ".join(fen.split()[:4])
                    
                    # Save to database
                    # If multiple entries have the same FEN, keep the one with the longer name/variation detail
                    # or just overwrite it (they are usually the same anyway).
                    openings_db[normalized_fen] = {
                        "eco": eco,
                        "name": name
                    }
                    count += 1
        print(f"Loaded {count} entries from {letter}.tsv")
    except Exception as e:
        print(f"Error processing {letter}.tsv: {e}")

# Save to openings.json
output_path = "openings.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(openings_db, f, indent=2)

print(f"Successfully compiled and saved {len(openings_db)} unique FEN mappings to {output_path}")
print(f"File size: {os.path.getsize(output_path) / 1024:.2f} KB")
