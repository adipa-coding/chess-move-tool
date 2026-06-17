import tkinter as tk
import chess
import math
from download_assets import load_pieces_images
from theme import BOARD_THEMES, HIGHLIGHTS, ANNOTATION_THEMES

class ChessBoard(tk.Canvas):
    def __init__(self, parent, game_manager, theme_name="Green (Chess.com)", piece_theme="neo", move_callback=None, **kwargs):
        self.game_manager = game_manager
        self.theme_name = theme_name
        self.piece_theme = piece_theme
        self.move_callback = move_callback
        self.flipped = False
        
        # UI sizing defaults
        self.square_size = 64
        self.board_size = 8 * self.square_size
        
        # Tkinter canvas initialization
        super().__init__(
            parent, 
            width=self.board_size, 
            height=self.board_size, 
            highlightthickness=0, 
            bg="#2c2c2c",
            **kwargs
        )
        
        # Interaction state
        self.selected_square = None
        self.drag_data = {"x": 0, "y": 0, "square": None, "item": None}
        
        # Right-click drawings (circles and arrows)
        # circles: set of (square, color)
        self.drawn_circles = {}
        # arrows: set of (start_square, end_square, color)
        self.drawn_arrows = {}
        self.right_click_start_square = None
        
        # Promotion state
        self.pending_promotion_move = None  # (from_sq, to_sq)
        self.promotion_overlay_items = []
        
        # Load pieces
        self.load_pieces()
        
        # Event bindings
        self.bind("<Configure>", self.on_resize)
        self.bind("<Button-1>", self.on_left_click)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_release)
        
        # Right-click bindings
        self.bind("<Button-3>", self.on_right_click)
        self.bind("<ButtonRelease-3>", self.on_right_release)
        
        self.draw_board()

    def load_pieces(self):
        """Loads or reloads piece images based on active theme and size."""
        self.piece_images = load_pieces_images(self.piece_theme, (self.square_size, self.square_size))

    def on_resize(self, event):
        """Handles canvas resizing to keep the board responsive."""
        size = min(event.width, event.height)
        if size < 200:
            return  # Don't resize too small
            
        new_square_size = size // 8
        if new_square_size != self.square_size:
            self.square_size = new_square_size
            self.board_size = 8 * self.square_size
            self.config(width=self.board_size, height=self.board_size)
            self.load_pieces()
            self.draw_board()

    def flip(self):
        """Flips the board orientation."""
        self.flipped = not self.flipped
        self.draw_board()

    def set_theme(self, theme_name):
        """Sets the board square colors theme."""
        if theme_name in BOARD_THEMES:
            self.theme_name = theme_name
            self.draw_board()

    def set_piece_theme(self, piece_theme):
        """Sets the piece graphics style."""
        self.piece_theme = piece_theme
        self.load_pieces()
        self.draw_board()

    def clear_drawings(self):
        """Clears all right-click arrows and circles."""
        self.drawn_circles.clear()
        self.drawn_arrows.clear()
        self.draw_board()

    # --- Coordinate Mapping ---
    def get_square_under_mouse(self, x, y):
        """Returns the chess.Square under the (x, y) canvas coordinate."""
        file_idx = x // self.square_size
        rank_idx = y // self.square_size
        
        if self.flipped:
            file_idx = 7 - file_idx
        else:
            rank_idx = 7 - rank_idx
            
        if 0 <= file_idx < 8 and 0 <= rank_idx < 8:
            return chess.square(file_idx, rank_idx)
        return None

    def get_square_coords(self, square):
        """Returns the top-left (x1, y1) and bottom-right (x2, y2) coords for a square."""
        file_idx = chess.square_file(square)
        rank_idx = chess.square_rank(square)
        
        if self.flipped:
            file_idx = 7 - file_idx
        else:
            rank_idx = 7 - rank_idx
            
        x1 = file_idx * self.square_size
        y1 = rank_idx * self.square_size
        x2 = x1 + self.square_size
        y2 = y1 + self.square_size
        return x1, y1, x2, y2

    def get_square_center(self, square):
        """Returns the center (x, y) of a square."""
        x1, y1, x2, y2 = self.get_square_coords(square)
        return (x1 + x2) // 2, (y1 + y2) // 2

    # --- Mouse Event Handlers ---
    def on_left_click(self, event):
        # Clear right-click drawings on any left click
        if self.drawn_circles or self.drawn_arrows:
            self.clear_drawings()
            return

        if self.pending_promotion_move:
            self.handle_promotion_click(event.x, event.y)
            return

        square = self.get_square_under_mouse(event.x, event.y)
        if square is None:
            return

        board = self.game_manager.get_current_board()
        piece = board.piece_at(square)
        
        # Clicked on already selected square: deselect
        if self.selected_square == square:
            self.selected_square = None
            self.draw_board()
            return
            
        # Clicked on a valid destination square (making a move)
        if self.selected_square is not None:
            move = chess.Move(self.selected_square, square)
            # Check for pawn promotion
            if board.piece_at(self.selected_square) and board.piece_at(self.selected_square).piece_type == chess.PAWN:
                if chess.square_rank(square) in (0, 7):
                    # Check if it's a legal pseudo-move ignoring promotion
                    promo_moves = [chess.Move(self.selected_square, square, promo) for promo in [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]]
                    if any(m in board.legal_moves for m in promo_moves):
                        self.pending_promotion_move = (self.selected_square, square)
                        self.draw_board()
                        return

            if self.game_manager.make_move(move):
                self.selected_square = None
                if self.move_callback:
                    self.move_callback()
                self.draw_board()
                return

        # Select a piece
        if piece:
            self.selected_square = square
            self.drag_data["square"] = square
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
            
            # Create a temporary canvas item for dragging
            symbol = piece.symbol()
            img = self.piece_images.get(symbol)
            if img:
                cx, cy = self.get_square_center(square)
                self.drag_data["item"] = self.create_image(cx, cy, image=img, tags="drag")
            
            self.draw_board()
        else:
            self.selected_square = None
            self.draw_board()

    def on_drag(self, event):
        if self.drag_data["item"]:
            self.coords(self.drag_data["item"], event.x, event.y)

    def on_release(self, event):
        if self.drag_data["item"]:
            self.delete(self.drag_data["item"])
            self.drag_data["item"] = None
            
            from_sq = self.drag_data["square"]
            to_sq = self.get_square_under_mouse(event.x, event.y)
            
            if to_sq is not None and from_sq != to_sq:
                board = self.game_manager.get_current_board()
                piece = board.piece_at(from_sq)
                
                # Check promotion
                if piece and piece.piece_type == chess.PAWN and chess.square_rank(to_sq) in (0, 7):
                    promo_moves = [chess.Move(from_sq, to_sq, promo) for promo in [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]]
                    if any(m in board.legal_moves for m in promo_moves):
                        self.pending_promotion_move = (from_sq, to_sq)
                        self.selected_square = None
                        self.draw_board()
                        return
                
                move = chess.Move(from_sq, to_sq)
                if self.game_manager.make_move(move):
                    self.selected_square = None
                    if self.move_callback:
                        self.move_callback()
            
            self.drag_data["square"] = None
            self.draw_board()

    # --- Right Click Drawings (Circles & Arrows) ---
    def get_drawing_color(self, event):
        """Returns drawing color based on keyboard modifiers."""
        # Check shift/ctrl/alt
        state = event.state
        shift = (state & 0x0001) != 0
        ctrl = (state & 0x0004) != 0
        alt = (state & 0x1ffff) & 0x20000 != 0 # Alt on windows
        
        # Check standard Tkinter alt state or other mods
        # state is bitwise mask: 1=Shift, 4=Ctrl, 8=Alt/Mod2, 131072=Alt
        if shift:
            return HIGHLIGHTS["drawings"]["red"]
        elif ctrl:
            return HIGHLIGHTS["drawings"]["blue"]
        elif alt:
            return HIGHLIGHTS["drawings"]["orange"]
        else:
            return HIGHLIGHTS["drawings"]["green"]

    def on_right_click(self, event):
        square = self.get_square_under_mouse(event.x, event.y)
        if square is not None:
            self.right_click_start_square = square

    def on_right_release(self, event):
        if self.right_click_start_square is None:
            return
            
        end_square = self.get_square_under_mouse(event.x, event.y)
        if end_square is None:
            self.right_click_start_square = None
            return
            
        color = self.get_drawing_color(event)
        
        if self.right_click_start_square == end_square:
            # Draw/Toggle Circle
            key = end_square
            if key in self.drawn_circles and self.drawn_circles[key] == color:
                del self.drawn_circles[key]
            else:
                self.drawn_circles[key] = color
        else:
            # Draw/Toggle Arrow
            key = (self.right_click_start_square, end_square)
            if key in self.drawn_arrows and self.drawn_arrows[key] == color:
                del self.drawn_arrows[key]
            else:
                self.drawn_arrows[key] = color
                
        self.right_click_start_square = None
        self.draw_board()

    # --- Promotion Handling ---
    def handle_promotion_click(self, x, y):
        """Handles selecting a piece from the promotion overlay."""
        if not self.pending_promotion_move:
            return
            
        # Draw board will define where the overlay buttons are
        from_sq, to_sq = self.pending_promotion_move
        file_idx = chess.square_file(to_sq)
        rank_idx = chess.square_rank(to_sq)
        
        if self.flipped:
            file_idx = 7 - file_idx
            # White promotes on rank 7 (bottom from black perspective)
            # Black promotes on rank 0 (top from black perspective)
            is_top = (rank_idx == 7)
        else:
            # White promotes on rank 7 (top from white perspective)
            # Black promotes on rank 0 (bottom from white perspective)
            is_top = (rank_idx == 7)
            
        # The overlay is drawn vertically on the promotion file
        promo_x = file_idx * self.square_size
        
        # Calculate Y start for the 4 squares
        if is_top:
            y_start = 0
            direction = 1
        else:
            y_start = self.board_size - 4 * self.square_size
            direction = 1
            
        # Overlay options ordered: Queen, Rook, Bishop, Knight
        options = [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]
        
        for idx, piece_type in enumerate(options):
            ox1 = promo_x
            oy1 = y_start + idx * self.square_size * direction
            ox2 = ox1 + self.square_size
            oy2 = oy1 + self.square_size
            
            if ox1 <= x <= ox2 and oy1 <= y <= oy2:
                # Make the move
                move = chess.Move(from_sq, to_sq, piece_type)
                self.game_manager.make_move(move)
                self.pending_promotion_move = None
                if self.move_callback:
                    self.move_callback()
                self.draw_board()
                return
                
        # Clicked outside promotion choices: cancel promotion
        self.pending_promotion_move = None
        self.draw_board()

    # --- Drawing Logic ---
    def draw_board(self):
        """Main rendering method. Redraws all elements on the canvas."""
        self.delete("all")
        
        theme = BOARD_THEMES.get(self.theme_name, BOARD_THEMES["Green (Chess.com)"])
        board = self.game_manager.get_current_board()
        active_node = self.game_manager.active_node
        
        # 1. Draw Squares & Coordinates
        for rank in range(8):
            for file in range(8):
                square = chess.square(file, rank)
                x1, y1, x2, y2 = self.get_square_coords(square)
                
                is_light = (file + rank) % 2 != 0
                color = theme["light"] if is_light else theme["dark"]
                self.create_rectangle(x1, y1, x2, y2, fill=color, outline="", tags="square")
                
                # Draw inline coordinates like Chess.com/Lichess
                text_color = theme["dark"] if is_light else theme["light"]
                
                # Rank labels on file 'a' (or 'h' if flipped)
                left_file = 7 if self.flipped else 0
                if file == left_file:
                    rank_char = str(rank + 1)
                    self.create_text(
                        x1 + 6, 
                        y1 + 8, 
                        text=rank_char, 
                        fill=text_color, 
                        font=("Inter", 9, "bold"), 
                        anchor="nw"
                    )
                    
                # File labels on rank 1 (or rank 8 if flipped)
                bottom_rank = 7 if self.flipped else 0
                if rank == bottom_rank:
                    file_char = chr(ord('a') + file)
                    self.create_text(
                        x2 - 6, 
                        y2 - 6, 
                        text=file_char, 
                        fill=text_color, 
                        font=("Inter", 9, "bold"), 
                        anchor="se"
                    )

        # 2. Highlight Last Move
        # Get last move from active node
        if active_node.move:
            from_sq = active_node.move.from_square
            to_sq = active_node.move.to_square
            
            for sq in (from_sq, to_sq):
                x1, y1, x2, y2 = self.get_square_coords(sq)
                # Draw semi-transparent highlight
                # Tkinter canvas doesn't easily support alpha transparency for fill colors.
                # To simulate, we can draw a dotted/dashed line or outline, or use a custom color.
                # Let's use a nice soft yellow/green overlay outline or tinted squares.
                # Actually, a thin dashed yellow border or soft yellow background fill is easiest.
                # Let's use a nice visual overlay.
                self.create_rectangle(
                    x1 + 1, y1 + 1, x2 - 1, y2 - 1,
                    outline="#baca44" if (chess.square_file(sq) + chess.square_rank(sq)) % 2 == 0 else "#f7f785",
                    width=2,
                    tags="highlight"
                )

        # 3. Highlight Selected Square
        if self.selected_square is not None:
            x1, y1, x2, y2 = self.get_square_coords(self.selected_square)
            self.create_rectangle(
                x1, y1, x2, y2, 
                outline=HIGHLIGHTS["selected"]["color"], 
                width=HIGHLIGHTS["selected"]["width"],
                tags="highlight"
            )
            
            # Highlight Legal Destination Squares
            for move in board.legal_moves:
                if move.from_square == self.selected_square:
                    dest_sq = move.to_square
                    cx, cy = self.get_square_center(dest_sq)
                    
                    # Draw dot or circle
                    if board.piece_at(dest_sq):
                        # Capture destination: circle outline
                        r = self.square_size // 2 - 4
                        self.create_oval(
                            cx - r, cy - r, cx + r, cy + r,
                            outline="#155f15", width=3, tags="dest_dot"
                        )
                    else:
                        # Empty destination: solid dot
                        r = self.square_size // 6
                        self.create_oval(
                            cx - r, cy - r, cx + r, cy + r,
                            fill="#155f15", outline="", tags="dest_dot"
                        )

        # 4. Draw Chess Pieces
        # (Skip drag piece since it is drawn dynamically on mouse move)
        drag_sq = self.drag_data["square"]
        for square in chess.SQUARES:
            if square == drag_sq:
                continue
                
            piece = board.piece_at(square)
            if piece:
                symbol = piece.symbol()
                img = self.piece_images.get(symbol)
                if img:
                    cx, cy = self.get_square_center(square)
                    self.create_image(cx, cy, image=img, tags="piece")

        # 5. Draw Move Annotation Badge (Chess.com style)
        # Check active node NAG (numeric annotation glyph)
        nag = self.game_manager.get_annotation_nag()
        if nag in ANNOTATION_THEMES and active_node.move:
            dest_sq = active_node.move.to_square
            badge = ANNOTATION_THEMES[nag]
            
            # Position at top-right corner of destination square
            bx2, by1, _, _ = self.get_square_coords(dest_sq)
            # Adjust to be top-right of that square
            bx = bx2 + self.square_size - 10
            by = by1 + 10
            r = 10  # Badge radius
            
            # Draw badge circle
            self.create_oval(
                bx - r, by - r, bx + r, by + r,
                fill=badge["bg"], outline="#ffffff", width=1.5,
                tags="badge"
            )
            # Draw badge text (!!, !, etc.)
            self.create_text(
                bx, by,
                text=badge["symbol"],
                fill=badge["fg"],
                font=("Inter", 8, "bold"),
                tags="badge"
            )

        # 6. Draw Right-Click Circles
        for square, color in self.drawn_circles.items():
            cx, cy = self.get_square_center(square)
            r = self.square_size // 2 - 4
            self.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                outline=color, width=3, tags="drawing"
            )

        # 7. Draw Right-Click Arrows
        for (start, end), color in self.drawn_arrows.items():
            x1, y1 = self.get_square_center(start)
            x2, y2 = self.get_square_center(end)
            
            # Vector calculations to shorten arrow slightly so it doesn't overlap circle centers
            dx = x2 - x1
            dy = y2 - y1
            dist = math.hypot(dx, dy)
            if dist > 0:
                # Shrink back from destination square center slightly
                shrink = self.square_size // 3
                x2_arrow = x2 - (dx / dist) * shrink
                y2_arrow = y2 - (dy / dist) * shrink
                
                # Create arrow
                self.create_line(
                    x1, y1, x2_arrow, y2_arrow,
                    fill=color, width=6, arrow=tk.LAST,
                    arrowshape=(16, 20, 8), tags="drawing"
                )

        # 8. Draw Promotion Overlay (if active)
        if self.pending_promotion_move:
            self.draw_promotion_overlay()

    def draw_promotion_overlay(self):
        """Draws a vertical promotion select overlay on the destination file."""
        from_sq, to_sq = self.pending_promotion_move
        file_idx = chess.square_file(to_sq)
        rank_idx = chess.square_rank(to_sq)
        
        board = self.game_manager.get_current_board()
        # White promotes if the moving pawn is white (uppercase symbol in chess)
        is_white = board.color_at(from_sq) == chess.WHITE
        color_prefix = 'w' if is_white else 'b'
        
        if self.flipped:
            file_idx = 7 - file_idx
            is_top = (rank_idx == 7)
        else:
            is_top = (rank_idx == 7)
            
        promo_x = file_idx * self.square_size
        
        if is_top:
            y_start = 0
            direction = 1
        else:
            y_start = self.board_size - 4 * self.square_size
            direction = 1
            
        # Draw translucent background behind the entire board to focus on promotion
        self.create_rectangle(
            0, 0, self.board_size, self.board_size,
            fill="#000000", stipple="gray50" if tk.TkVersion >= 8.5 else "",
            outline="", tags="promo_overlay"
        )
        
        # Overlay options: Queen, Rook, Bishop, Knight
        options = ['q', 'r', 'b', 'n'] if not is_white else ['Q', 'R', 'B', 'N']
        
        for idx, piece_symbol in enumerate(options):
            ox1 = promo_x
            oy1 = y_start + idx * self.square_size * direction
            ox2 = ox1 + self.square_size
            oy2 = oy1 + self.square_size
            
            # White card background for options
            self.create_rectangle(
                ox1, oy1, ox2, oy2,
                fill="#ffffff", outline="#cccccc", width=1,
                tags="promo_overlay"
            )
            
            # Draw piece image
            img = self.piece_images.get(piece_symbol)
            if img:
                self.create_image(
                    (ox1 + ox2) // 2, (oy1 + oy2) // 2,
                    image=img, tags="promo_overlay"
                )
