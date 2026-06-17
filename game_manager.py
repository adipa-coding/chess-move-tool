import chess
import chess.pgn
import io
import os
import json

class ChessGameManager:
    def __init__(self, autosave_path="autosave.pgn"):
        self.autosave_path = autosave_path
        self.reset_game()
        
        # Load openings database
        self.openings_db = {}
        openings_json_path = os.path.join(os.path.dirname(__file__), "openings.json")
        if os.path.exists(openings_json_path):
            try:
                with open(openings_json_path, "r", encoding="utf-8") as f:
                    self.openings_db = json.load(f)
            except Exception as e:
                print(f"Error loading openings.json: {e}")
                
        # Try to load autosave on startup if it exists
        if os.path.exists(self.autosave_path) and os.path.getsize(self.autosave_path) > 0:
            self.load_pgn_file(self.autosave_path)

    def reset_game(self):
        """Resets the game to the starting position."""
        self.game = chess.pgn.Game()
        self.game.headers["Event"] = "Casual Chess Move Analysis"
        self.game.headers["Site"] = "Local Desktop"
        self.game.headers["Date"] = "????"
        self.game.headers["White"] = "White Player"
        self.game.headers["Black"] = "Black Player"
        self.game.headers["Result"] = "*"
        self.active_node = self.game
        
    def get_current_board(self):
        """Returns the board object for the current active node."""
        return self.active_node.board()

    def get_parent_board(self):
        """Returns the board object before the last move (parent node)."""
        if self.active_node.parent:
            return self.active_node.parent.board()
        return self.get_current_board()

    def make_move(self, move):
        """
        Attempts to play a move.
        If it's legal:
          - If the move already exists in active_node's variations, traverse to it.
          - If it's a new move, add it as a variation and traverse to it.
          - Triggers autosave.
          - Returns True.
        Otherwise, returns False.
        """
        board = self.get_current_board()
        if move in board.legal_moves:
            # Check if this move is already a variation of the active node
            existing_node = None
            for var in self.active_node.variations:
                if var.move == move:
                    existing_node = var
                    break
            
            if existing_node:
                self.active_node = existing_node
            else:
                self.active_node = self.active_node.add_variation(move)
                
            self.auto_save()
            return True
        return False

    def delete_current_node(self):
        """
        Deletes the active node from the game tree (prunes this variation).
        Sets the active node to its parent.
        Returns True if successful, False if at the root.
        """
        if self.active_node.parent:
            parent = self.active_node.parent
            parent.remove_variation(self.active_node.move)
            self.active_node = parent
            self.auto_save()
            return True
        return False

    def clear_all_variations(self):
        """Clears all moves from the current position onwards."""
        self.active_node.variations.clear()
        self.auto_save()

    # --- Tree Navigation ---
    def go_first(self):
        """Jumps to the starting position."""
        self.active_node = self.game

    def go_prev(self):
        """Goes back one move."""
        if self.active_node.parent:
            self.active_node = self.active_node.parent

    def go_next(self):
        """Goes forward one move along the main line (first variation)."""
        if self.active_node.variations:
            self.active_node = self.active_node.variations[0]

    def go_last(self):
        """Goes forward to the end of the current variation line."""
        while self.active_node.variations:
            self.active_node = self.active_node.variations[0]

    def go_to_node(self, node):
        """Jumps to a specific node in the game tree."""
        self.active_node = node

    # --- Annotations & Comments ---
    def set_comment(self, comment):
        """Sets the comment for the current position (active node)."""
        # Comments on the root node represent game introduction, comments on subsequent nodes are for the move.
        self.active_node.comment = comment.strip()
        self.auto_save()

    def get_comment(self):
        """Returns the comment for the current position."""
        return self.active_node.comment

    def set_annotation_nag(self, nag_value):
        """
        Sets a single NAG (Numeric Annotation Glyph) for the active node.
        If nag_value is None, clears annotations.
        """
        # PGN NAGs represent move evaluations like !!, !, ?, ??, etc.
        # Root node cannot have move annotations.
        if self.active_node.parent:
            self.active_node.nags.clear()
            if nag_value:
                self.active_node.nags.add(nag_value)
            self.auto_save()

    def get_annotation_nag(self):
        """Returns the first NAG value if any, or None."""
        if self.active_node.nags:
            return next(iter(self.active_node.nags))
        return None

    # --- PGN Import / Export ---
    def load_pgn_string(self, pgn_str):
        """Loads a game from a PGN string. Returns True if successful."""
        pgn_io = io.StringIO(pgn_str.strip())
        parsed_game = chess.pgn.read_game(pgn_io)
        if parsed_game:
            self.game = parsed_game
            self.active_node = self.game
            self.auto_save()
            return True
        return False

    def load_pgn_file(self, filepath):
        """Loads a game from a PGN file."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                parsed_game = chess.pgn.read_game(f)
                if parsed_game:
                    self.game = parsed_game
                    self.active_node = self.game
                    return True
        except Exception as e:
            print(f"Error loading PGN file {filepath}: {e}")
        return False

    def get_pgn_string(self):
        """Exports the entire game as a PGN string."""
        exporter = chess.pgn.StringExporter(headers=True, variations=True, comments=True)
        return self.game.accept(exporter)

    def save_pgn_file(self, filepath):
        """Saves the entire game to a PGN file."""
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                exporter = chess.pgn.FileExporter(f)
                self.game.accept(exporter)
            return True
        except Exception as e:
            print(f"Error saving PGN file {filepath}: {e}")
            return False

    def auto_save(self):
        """Saves the current state to the autosave PGN file."""
        if self.autosave_path:
            self.save_pgn_file(self.autosave_path)
            
    def update_headers(self, headers_dict):
        """Updates game headers like Event, Site, Date, White, Black, Result."""
        for key, value in headers_dict.items():
            self.game.headers[key] = value
        self.auto_save()
        
    def get_headers(self):
        """Returns the game headers dict."""
        return dict(self.game.headers)

    def get_current_opening(self):
        """
        Traverses back from the current active node to find the longest matched opening.
        Returns a dictionary with 'eco' and 'name' or None.
        """
        node = self.active_node
        while node is not None:
            board = node.board()
            fen = board.fen()
            normalized_fen = " ".join(fen.split()[:4])
            if normalized_fen in self.openings_db:
                return self.openings_db[normalized_fen]
            node = node.parent
        return None
