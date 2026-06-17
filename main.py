import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import chess
import chess.pgn
import os

from game_manager import ChessGameManager
from chess_board import ChessBoard
from theme import ANNOTATION_THEMES, ANNOTATION_STR_TO_NAG, BOARD_THEMES

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ChessMoveToolApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Chess Move Tool & PGN Analyzer")
        self.geometry("1200x750")
        self.minsize(1000, 650)
        
        # Load state manager
        self.game_manager = ChessGameManager()
        self.active_tag = None
        
        self.setup_ui()
        self.update_ui()
        
        # Ensure scroll to active tag works on startup
        self.after(500, self.scroll_to_active_move)

    def setup_ui(self):
        # Configure layout grids
        self.grid_columnconfigure(0, weight=6, minsize=550) # Left side: Board
        self.grid_columnconfigure(1, weight=4, minsize=400) # Right side: Panels
        self.grid_rowconfigure(0, weight=1)
        
        # --- LEFT SIDE: CHESSBOARD FRAME ---
        self.left_frame = ctk.CTkFrame(self, corner_radius=0)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.left_frame.grid_columnconfigure(0, weight=1)
        self.left_frame.grid_rowconfigure(0, weight=0) # Opening label
        self.left_frame.grid_rowconfigure(1, weight=1) # Board container
        self.left_frame.grid_rowconfigure(2, weight=0) # Controls
        self.left_frame.grid_rowconfigure(3, weight=0) # Themes selector
        
        # Opening Header Frame
        self.opening_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        self.opening_frame.grid(row=0, column=0, pady=(10, 5), padx=10, sticky="ew")
        
        self.lbl_opening_eco = ctk.CTkLabel(
            self.opening_frame, 
            text="", 
            font=("Inter", 11, "bold"),
            fg_color="#3b82f6", # Blue badge
            text_color="#ffffff",
            corner_radius=4,
            width=40,
            height=22
        )
        
        self.lbl_opening_name = ctk.CTkLabel(
            self.opening_frame, 
            text="Starting Position", 
            font=("Inter", 14, "bold"),
            text_color="#f8fafc",
            anchor="w"
        )
        self.lbl_opening_name.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Board Container to maintain aspect ratio
        self.board_container = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        self.board_container.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.board_container.grid_columnconfigure(0, weight=1)
        self.board_container.grid_rowconfigure(0, weight=1)
        
        # Chessboard widget
        self.board = ChessBoard(
            self.board_container, 
            self.game_manager, 
            move_callback=self.on_move_made
        )
        self.board.grid(row=0, column=0, sticky="")
        
        # Game Navigation & Action Controls
        self.controls_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        self.controls_frame.grid(row=2, column=0, pady=10, sticky="ew")
        
        self.controls_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)
        
        # Navigate buttons
        self.btn_first = ctk.CTkButton(self.controls_frame, text="<<", width=50, command=self.go_first)
        self.btn_first.grid(row=0, column=0, padx=2, sticky="ew")
        
        self.btn_prev = ctk.CTkButton(self.controls_frame, text="<", width=50, command=self.go_prev)
        self.btn_prev.grid(row=0, column=1, padx=2, sticky="ew")
        
        self.btn_next = ctk.CTkButton(self.controls_frame, text=">", width=50, command=self.go_next)
        self.btn_next.grid(row=0, column=2, padx=2, sticky="ew")
        
        self.btn_last = ctk.CTkButton(self.controls_frame, text=">>", width=50, command=self.go_last)
        self.btn_last.grid(row=0, column=3, padx=2, sticky="ew")
        
        # Actions
        self.btn_flip = ctk.CTkButton(self.controls_frame, text="Flip Board", width=80, fg_color="#475569", hover_color="#334155", command=self.flip_board)
        self.btn_flip.grid(row=0, column=4, padx=2, sticky="ew")
        
        self.btn_delete = ctk.CTkButton(self.controls_frame, text="Delete Move", width=90, fg_color="#991b1b", hover_color="#7f1d1d", command=self.delete_move)
        self.btn_delete.grid(row=0, column=5, padx=2, sticky="ew")
        
        self.btn_clear = ctk.CTkButton(self.controls_frame, text="Reset Board", width=90, fg_color="#374151", hover_color="#1f2937", command=self.reset_board)
        self.btn_clear.grid(row=0, column=6, padx=2, sticky="ew")
        
        # Board Theme Selectors
        self.theme_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        self.theme_frame.grid(row=3, column=0, pady=5, sticky="ew")
        
        ctk.CTkLabel(self.theme_frame, text="Board Theme:").pack(side=tk.LEFT, padx=5)
        self.combo_board_theme = ctk.CTkComboBox(
            self.theme_frame, 
            values=list(BOARD_THEMES.keys()), 
            command=self.change_board_theme,
            width=160
        )
        self.combo_board_theme.set("Green (Chess.com)")
        self.combo_board_theme.pack(side=tk.LEFT, padx=5)
        
        ctk.CTkLabel(self.theme_frame, text="Piece Set:").pack(side=tk.LEFT, padx=5)
        self.combo_piece_theme = ctk.CTkComboBox(
            self.theme_frame, 
            values=["neo", "classic", "wood"], 
            command=self.change_piece_theme,
            width=100
        )
        self.combo_piece_theme.set("neo")
        self.combo_piece_theme.pack(side=tk.LEFT, padx=5)
        
        # Keyboard Navigation bindings on root window
        self.bind("<Left>", lambda e: self.go_prev())
        self.bind("<Right>", lambda e: self.go_next())
        self.bind("<Up>", lambda e: self.go_first())
        self.bind("<Down>", lambda e: self.go_last())

        # --- RIGHT SIDE: ANALYZE PANELS ---
        self.right_frame = ctk.CTkTabview(self)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        self.tab_moves = self.right_frame.add("Moves Tree")
        self.tab_pgn = self.right_frame.add("Game Info / PGN")
        self.tab_features = self.right_frame.add("Upcoming Features")
        
        self.setup_moves_tab()
        self.setup_pgn_tab()
        self.setup_features_tab()

    def setup_moves_tab(self):
        # Configure layout for Moves Tree Tab
        self.tab_moves.grid_columnconfigure(0, weight=1)
        self.tab_moves.grid_rowconfigure(0, weight=6) # Interactive Moves List
        self.tab_moves.grid_rowconfigure(1, weight=0) # Annotation badges row
        self.tab_moves.grid_rowconfigure(2, weight=2) # Comment box
        
        # 1. Interactive Moves text pane (Lichess style)
        self.moves_container = ctk.CTkFrame(self.tab_moves)
        self.moves_container.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        self.moves_container.grid_columnconfigure(0, weight=1)
        self.moves_container.grid_rowconfigure(0, weight=1)
        
        # Scrollbar for Moves
        self.moves_scrollbar = tk.Scrollbar(self.moves_container)
        self.moves_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Raw text widget for formatting tree structure
        self.move_text = tk.Text(
            self.moves_container,
            wrap=tk.WORD,
            yscrollcommand=self.moves_scrollbar.set,
            bg="#18181b",
            fg="#e4e4e7",
            font=("Inter", 11),
            insertbackground="white",
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.move_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.moves_scrollbar.config(command=self.move_text.yview)
        
        # Make read-only except when drawing
        self.move_text.config(state="disabled")
        
        # 2. Annotation badges panel (Chess.com badges)
        self.anno_frame = ctk.CTkFrame(self.tab_moves, fg_color="transparent")
        self.anno_frame.grid(row=1, column=0, pady=5, sticky="ew")
        
        ctk.CTkLabel(self.anno_frame, text="Mark Move:", font=("Inter", 11, "bold")).pack(side=tk.LEFT, padx=5)
        
        # Draw buttons for each NAG annotation badge
        # Order: Brilliant, Great, Interesting, Inaccuracy, Mistake, Blunder, Clear
        for nag, info in ANNOTATION_THEMES.items():
            btn = ctk.CTkButton(
                self.anno_frame,
                text=info["symbol"],
                font=("Inter", 10, "bold"),
                fg_color=info["bg"],
                hover_color=self.darken_color(info["bg"]),
                text_color=info["fg"],
                width=32,
                height=24,
                corner_radius=4,
                command=lambda n=nag: self.add_move_annotation(n)
            )
            btn.pack(side=tk.LEFT, padx=3)
            
        # Clear badge button
        btn_clear_anno = ctk.CTkButton(
            self.anno_frame,
            text="Clear",
            font=("Inter", 10),
            fg_color="#3f3f46",
            hover_color="#27272a",
            width=50,
            height=24,
            corner_radius=4,
            command=lambda: self.add_move_annotation(None)
        )
        btn_clear_anno.pack(side=tk.LEFT, padx=8)
        
        # 3. Comment box section
        self.comment_frame = ctk.CTkFrame(self.tab_moves)
        self.comment_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        
        self.comment_frame.grid_columnconfigure(0, weight=1)
        self.comment_frame.grid_rowconfigure(0, weight=0) # label
        self.comment_frame.grid_rowconfigure(1, weight=1) # text
        
        ctk.CTkLabel(self.comment_frame, text="Position/Move Comment:", font=("Inter", 11, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=4)
        
        self.comment_box = ctk.CTkTextbox(
            self.comment_frame,
            font=("Inter", 11),
            activate_scrollbars=True
        )
        self.comment_box.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        # Auto-save comment on focus out
        self.comment_box.bind("<FocusOut>", self.on_comment_focus_out)

    def setup_pgn_tab(self):
        # Configure layout for Game Info / PGN Tab
        self.tab_pgn.grid_columnconfigure(0, weight=1)
        self.tab_pgn.grid_rowconfigure(0, weight=0) # Headers editor
        self.tab_pgn.grid_rowconfigure(1, weight=1) # Raw PGN text box
        self.tab_pgn.grid_rowconfigure(2, weight=0) # Action buttons
        
        # 1. PGN headers input editor
        self.headers_frame = ctk.CTkFrame(self.tab_pgn)
        self.headers_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        self.headers_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Row 1: Event & Site
        ctk.CTkLabel(self.headers_frame, text="Event:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.ent_event = ctk.CTkEntry(self.headers_frame)
        self.ent_event.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        
        ctk.CTkLabel(self.headers_frame, text="Site:").grid(row=0, column=2, padx=5, pady=2, sticky="w")
        self.ent_site = ctk.CTkEntry(self.headers_frame)
        self.ent_site.grid(row=0, column=3, padx=5, pady=2, sticky="ew")
        
        # Row 2: White & Black
        ctk.CTkLabel(self.headers_frame, text="White:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.ent_white = ctk.CTkEntry(self.headers_frame)
        self.ent_white.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        
        ctk.CTkLabel(self.headers_frame, text="Black:").grid(row=1, column=2, padx=5, pady=2, sticky="w")
        self.ent_black = ctk.CTkEntry(self.headers_frame)
        self.ent_black.grid(row=1, column=3, padx=5, pady=2, sticky="ew")
        
        # Row 3: Date & Result
        ctk.CTkLabel(self.headers_frame, text="Date:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.ent_date = ctk.CTkEntry(self.headers_frame)
        self.ent_date.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        
        ctk.CTkLabel(self.headers_frame, text="Result:").grid(row=2, column=2, padx=5, pady=2, sticky="w")
        self.ent_result = ctk.CTkComboBox(self.headers_frame, values=["*", "1-0", "0-1", "1/2-1/2"])
        self.ent_result.grid(row=2, column=3, padx=5, pady=2, sticky="ew")
        
        # Update button
        self.btn_update_headers = ctk.CTkButton(
            self.headers_frame, 
            text="Update Info", 
            command=self.update_headers,
            fg_color="#10b981", 
            hover_color="#059669"
        )
        self.btn_update_headers.grid(row=3, column=0, columnspan=4, pady=8, padx=10, sticky="ew")
        
        # 2. Raw PGN viewer/editor
        self.raw_pgn_frame = ctk.CTkFrame(self.tab_pgn)
        self.raw_pgn_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        self.raw_pgn_frame.grid_columnconfigure(0, weight=1)
        self.raw_pgn_frame.grid_rowconfigure(0, weight=1)
        
        self.pgn_textbox = ctk.CTkTextbox(
            self.raw_pgn_frame,
            font=("Consolas", 10),
            activate_scrollbars=True
        )
        self.pgn_textbox.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # 3. Actions
        self.pgn_actions_frame = ctk.CTkFrame(self.tab_pgn, fg_color="transparent")
        self.pgn_actions_frame.grid(row=2, column=0, pady=10, sticky="ew")
        self.pgn_actions_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        self.btn_load_file = ctk.CTkButton(self.pgn_actions_frame, text="Load File", command=self.load_pgn_file)
        self.btn_load_file.grid(row=0, column=0, padx=5, sticky="ew")
        
        self.btn_save_file = ctk.CTkButton(self.pgn_actions_frame, text="Save File", command=self.save_pgn_file)
        self.btn_save_file.grid(row=0, column=1, padx=5, sticky="ew")
        
        self.btn_import_clip = ctk.CTkButton(self.pgn_actions_frame, text="Import Clip", fg_color="#4f46e5", hover_color="#4338ca", command=self.import_pgn_clipboard)
        self.btn_import_clip.grid(row=0, column=2, padx=5, sticky="ew")
        
        self.btn_export_clip = ctk.CTkButton(self.pgn_actions_frame, text="Copy PGN", fg_color="#1d4ed8", hover_color="#1e40af", command=self.copy_pgn_clipboard)
        self.btn_export_clip.grid(row=0, column=3, padx=5, sticky="ew")

    def setup_features_tab(self):
        # Configure layout for Features Tab
        self.tab_features.grid_columnconfigure(0, weight=1)
        self.tab_features.grid_rowconfigure(0, weight=1) # Scrollable frame for cards
        
        # Scrollable container for features list
        self.features_scroll = ctk.CTkScrollableFrame(self.tab_features, fg_color="transparent")
        self.features_scroll.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.features_scroll.grid_columnconfigure(0, weight=1)
        
        # Header title
        lbl_title = ctk.CTkLabel(
            self.features_scroll,
            text="💡 Future Feature Lab & Roadmap",
            font=("Inter", 16, "bold"),
            text_color="#38bdf8",
            anchor="w"
        )
        lbl_title.grid(row=0, column=0, pady=(10, 5), padx=10, sticky="w")
        
        lbl_desc = ctk.CTkLabel(
            self.features_scroll,
            text="Preview and track upcoming features. Cast your vote to prioritize development!",
            font=("Inter", 11),
            text_color="#94a3b8",
            wraplength=350,
            justify=tk.LEFT,
            anchor="w"
        )
        lbl_desc.grid(row=1, column=0, pady=(0, 15), padx=10, sticky="w")
        
        # --- FEATURE CARD 1: STOCKFISH ENGINE PREVIEW ---
        self.card_stockfish = ctk.CTkFrame(self.features_scroll, fg_color="#1e293b", border_width=1, border_color="#334155")
        self.card_stockfish.grid(row=2, column=0, pady=10, padx=5, sticky="ew")
        
        # Title & Badge
        header_stockfish = ctk.CTkFrame(self.card_stockfish, fg_color="transparent")
        header_stockfish.pack(fill=tk.X, padx=10, pady=8)
        
        lbl_sf_name = ctk.CTkLabel(header_stockfish, text="🤖 Stockfish Engine Integration", font=("Inter", 13, "bold"), text_color="#f8fafc")
        lbl_sf_name.pack(side=tk.LEFT)
        
        badge_sf = ctk.CTkLabel(
            header_stockfish,
            text="Active Preview (75%)",
            font=("Inter", 9, "bold"),
            fg_color="#0369a1",
            text_color="#e0f2fe",
            corner_radius=4,
            padx=5
        )
        badge_sf.pack(side=tk.RIGHT)
        
        # Interactive Live Engine Mockup
        self.engine_mock_frame = ctk.CTkFrame(self.card_stockfish, fg_color="#0f172a", corner_radius=6)
        self.engine_mock_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Mock Engine stats
        stats_frame = ctk.CTkFrame(self.engine_mock_frame, fg_color="transparent")
        stats_frame.pack(fill=tk.X, padx=10, pady=(8, 4))
        
        self.lbl_sf_eval = ctk.CTkLabel(stats_frame, text="Eval: +0.25", font=("Consolas", 11, "bold"), text_color="#10b981")
        self.lbl_sf_eval.pack(side=tk.LEFT)
        
        self.lbl_sf_depth = ctk.CTkLabel(stats_frame, text="Depth: 18/20", font=("Consolas", 10), text_color="#94a3b8")
        self.lbl_sf_depth.pack(side=tk.RIGHT)
        
        # Best move suggestion
        self.lbl_sf_best = ctk.CTkLabel(self.engine_mock_frame, text="Suggested best move: --", font=("Inter", 10, "italic"), text_color="#cbd5e1", anchor="w")
        self.lbl_sf_best.pack(fill=tk.X, padx=10, pady=(0, 8))
        
        # Simulated Progress/Evaluation Bar
        self.eval_bar = ctk.CTkProgressBar(self.card_stockfish, height=8, progress_color="#10b981", fg_color="#ef4444")
        self.eval_bar.pack(fill=tk.X, padx=10, pady=(5, 10))
        self.eval_bar.set(0.5) # Neutral center
        
        # Vote Button
        self.btn_vote_sf = ctk.CTkButton(
            self.card_stockfish,
            text="Vote for this feature",
            font=("Inter", 11),
            fg_color="#334155",
            hover_color="#475569",
            height=26,
            command=lambda: self.vote_feature("Stockfish Engine")
        )
        self.btn_vote_sf.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # --- FEATURE CARD 2: INTERACTIVE TRAINER ---
        self.card_trainer = ctk.CTkFrame(self.features_scroll, fg_color="#1e293b", border_width=1, border_color="#334155")
        self.card_trainer.grid(row=3, column=0, pady=10, padx=5, sticky="ew")
        
        header_trainer = ctk.CTkFrame(self.card_trainer, fg_color="transparent")
        header_trainer.pack(fill=tk.X, padx=10, pady=8)
        
        lbl_tr_name = ctk.CTkLabel(header_trainer, text="🎓 Opening Repertoire Trainer", font=("Inter", 13, "bold"), text_color="#f8fafc")
        lbl_tr_name.pack(side=tk.LEFT)
        
        badge_tr = ctk.CTkLabel(
            header_trainer,
            text="Planned (40%)",
            font=("Inter", 9, "bold"),
            fg_color="#c2410c",
            text_color="#ffedd5",
            corner_radius=4,
            padx=5
        )
        badge_tr.pack(side=tk.RIGHT)
        
        lbl_tr_desc = ctk.CTkLabel(
            self.card_trainer,
            text="Train variations flashcard-style! The app will guide you through moves and alert you if you deviate from your saved book.",
            font=("Inter", 11),
            text_color="#94a3b8",
            wraplength=340,
            justify=tk.LEFT,
            anchor="w"
        )
        lbl_tr_desc.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.btn_vote_tr = ctk.CTkButton(
            self.card_trainer,
            text="Vote for this feature",
            font=("Inter", 11),
            fg_color="#334155",
            hover_color="#475569",
            height=26,
            command=lambda: self.vote_feature("Repertoire Trainer")
        )
        self.btn_vote_tr.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # --- FEATURE CARD 3: MASTERS EXPLORER ---
        self.card_explorer = ctk.CTkFrame(self.features_scroll, fg_color="#1e293b", border_width=1, border_color="#334155")
        self.card_explorer.grid(row=4, column=0, pady=10, padx=5, sticky="ew")
        
        header_explorer = ctk.CTkFrame(self.card_explorer, fg_color="transparent")
        header_explorer.pack(fill=tk.X, padx=10, pady=8)
        
        lbl_ex_name = ctk.CTkLabel(header_explorer, text="🌐 Masters Database Explorer", font=("Inter", 13, "bold"), text_color="#f8fafc")
        lbl_ex_name.pack(side=tk.LEFT)
        
        badge_ex = ctk.CTkLabel(
            header_explorer,
            text="Planned (15%)",
            font=("Inter", 9, "bold"),
            fg_color="#4b5563",
            text_color="#f3f4f6",
            corner_radius=4,
            padx=5
        )
        badge_ex.pack(side=tk.RIGHT)
        
        lbl_ex_desc = ctk.CTkLabel(
            self.card_explorer,
            text="Directly view and analyze historical games played by grandmasters from the exact same position via online APIs.",
            font=("Inter", 11),
            text_color="#94a3b8",
            wraplength=340,
            justify=tk.LEFT,
            anchor="w"
        )
        lbl_ex_desc.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.btn_vote_ex = ctk.CTkButton(
            self.card_explorer,
            text="Vote for this feature",
            font=("Inter", 11),
            fg_color="#334155",
            hover_color="#475569",
            height=26,
            command=lambda: self.vote_feature("Masters Explorer")
        )
        self.btn_vote_ex.pack(fill=tk.X, padx=10, pady=(0, 10))

    def vote_feature(self, feature_name):
        messagebox.showinfo("Voted!", f"Thank you for voting for '{feature_name}'! Your vote has been recorded.")

    # --- UI Synchronization ---
    def update_ui(self):
        """Redraws the board, refreshes the moves tree list, and refreshes the metadata panel."""
        self.board.draw_board()
        self.refresh_moves_tree()
        self.refresh_comment_box()
        self.refresh_headers_panel()
        self.refresh_raw_pgn()
        self.update_opening_display()
        self.update_mock_engine()

    def update_opening_display(self):
        """Fetches and shows the current opening name and ECO badge in the header."""
        opening = self.game_manager.get_current_opening()
        if opening:
            eco = opening.get("eco", "")
            name = opening.get("name", "")
            if eco:
                self.lbl_opening_eco.configure(text=eco)
                self.lbl_opening_eco.pack(side=tk.LEFT, padx=(0, 5))
            else:
                self.lbl_opening_eco.pack_forget()
            self.lbl_opening_name.configure(text=name)
        else:
            self.lbl_opening_eco.pack_forget()
            if self.game_manager.active_node.parent is None:
                self.lbl_opening_name.configure(text="Starting Position")
            else:
                self.lbl_opening_name.configure(text="Custom / Unknown Opening")

    def update_mock_engine(self):
        """Updates the mock engine card with semi-realistic stats based on the board state."""
        board = self.game_manager.get_current_board()
        
        # Check if game is over
        if board.is_checkmate():
            if board.turn == chess.WHITE:
                # White is mated, so score is mate for Black (-M0)
                self.lbl_sf_eval.configure(text="Score: -M0", text_color="#ef4444")
                self.eval_bar.set(0.0)
            else:
                self.lbl_sf_eval.configure(text="Score: +M0", text_color="#10b981")
                self.eval_bar.set(1.0)
            self.lbl_sf_best.configure(text="Suggested best move: None")
            return
        elif board.is_game_over():
            self.lbl_sf_eval.configure(text="Score: 0.00", text_color="#e2e8f0")
            self.eval_bar.set(0.5)
            self.lbl_sf_best.configure(text="Suggested best move: None")
            return
            
        # Run a fast depth 2 minimax search to get actual evaluation and move
        try:
            raw_score, best_move = minimax(board, 2, -999999, 999999, board.turn == chess.WHITE)
            
            # The score is returned from minimax in centipawns.
            # To get decimal pawns relative to White:
            # The score is returned from minimax in centipawns.
            # To get decimal pawns relative to White, we divide by 100.0.
            val_score = raw_score / 100.0
            
            # Format evaluation score relative to White
            if val_score >= 0:
                score_str = f"Score: +{val_score:.2f}"
                self.lbl_sf_eval.configure(text=score_str, text_color="#10b981")
            else:
                score_str = f"Score: {val_score:.2f}"
                self.lbl_sf_eval.configure(text=score_str, text_color="#ef4444")
                
            # Update evaluation bar (range from -8.0 to +8.0, centered at 0.5)
            clipped_score = max(-8.0, min(8.0, val_score))
            progress_val = (clipped_score + 8.0) / 16.0
            self.eval_bar.set(progress_val)
            
            # Display best move suggestion
            if best_move:
                san_move = board.san(best_move)
                self.lbl_sf_best.configure(text=f"Suggested best move: {san_move}")
            else:
                self.lbl_sf_best.configure(text="Suggested best move: None")
        except Exception as e:
            print(f"Error in mock engine calculation: {e}")
            self.lbl_sf_eval.configure(text="Score: --", text_color="#e2e8f0")
            self.eval_bar.set(0.5)
            self.lbl_sf_best.configure(text="Suggested best move: --")

    def refresh_moves_tree(self):
        """Re-generates the interactive moves list view with nested variations and highlights."""
        # Record scroll position before refresh
        y_scroll = self.move_text.yview()
        
        self.move_text.config(state="normal")
        self.move_text.delete("1.0", tk.END)
        self.active_tag = None
        
        # Traverse and render starting from root Variations
        self.render_tree(self.game_manager.game, need_number=True, is_sub=False)
        
        if not self.game_manager.game.variations:
            self.move_text.insert(tk.END, "No moves played yet. Use the board to make moves.", "placeholder")
            self.move_text.tag_config("placeholder", foreground="#71717a", font=("Inter", 10, "italic"))
            
        self.move_text.config(state="disabled")
        
        # Restore scroll position
        self.move_text.yview_moveto(y_scroll[0])
        
        # Scroll to active node
        self.scroll_to_active_move()

    def render_node_only(self, node, need_number, is_sub):
        """Formats and inserts a single move node with annotations/comments into the text widget."""
        board_before = node.parent.board()
        move_str = board_before.san(node.move)
        
        # Get evaluation NAG annotation badge
        nag = next(iter(node.nags)) if node.nags else None
        nag_str = ""
        if nag in ANNOTATION_THEMES:
            nag_str = ANNOTATION_THEMES[nag]["symbol"]
            
        display_str = f"{move_str}{nag_str}"
        
        # Prefix with numbers (White moves get 'N. ', Black moves get 'N... ' if preceded by variation)
        if board_before.turn == chess.WHITE:
            prefix = f"{board_before.fullmove_number}. "
            next_need_number = False
        else:
            if need_number:
                prefix = f"{board_before.fullmove_number}... "
            else:
                prefix = ""
            next_need_number = True
            
        if prefix:
            self.move_text.insert(tk.END, prefix)
            
        # Clickable move text insert
        start_idx = self.move_text.index("end-1c")
        self.move_text.insert(tk.END, display_str)
        end_idx = self.move_text.index("end-1c")
        
        tag_name = f"node_{id(node)}"
        self.move_text.tag_add(tag_name, start_idx, end_idx)
        
        # Check if active move
        is_active = (node == self.game_manager.active_node)
        
        # Apply themes to main and variation nodes
        if is_active:
            self.active_tag = tag_name
            bg_color = "#1e3a8a" if not is_sub else "#581c87" # Deep blue / Deep purple for variations
            fg_color = "#ffffff"
            font_style = ("Inter", 11, "bold") if not is_sub else ("Inter", 10, "bold italic")
            self.move_text.tag_config(tag_name, background=bg_color, foreground=fg_color, font=font_style)
        else:
            fg_color = "#e4e4e7" if not is_sub else "#a1a1aa"
            font_style = ("Inter", 11, "bold") if not is_sub else ("Inter", 10, "italic")
            self.move_text.tag_config(tag_name, foreground=fg_color, font=font_style, background="")
            
        # Bind events
        self.move_text.tag_bind(tag_name, "<Button-1>", lambda e, n=node: self.select_node(n))
        self.move_text.tag_bind(tag_name, "<Enter>", lambda e, t=tag_name: self.move_text.tag_config(t, underline=True))
        self.move_text.tag_bind(tag_name, "<Leave>", lambda e, t=tag_name: self.move_text.tag_config(t, underline=False))
        
        # Render inline comment if present
        if node.comment:
            comment_str = f" {{ {node.comment} }} "
            self.move_text.insert(tk.END, comment_str, "comment")
            self.move_text.tag_config("comment", foreground="#10b981", font=("Inter", 10, "italic"))
            next_need_number = True
            
        self.move_text.insert(tk.END, " ")
        return next_need_number

    def render_tree(self, node, need_number=True, is_sub=False):
        """Recursively renders the entire variations tree structure."""
        if not node.variations:
            return
            
        main_child = node.variations[0]
        sub_children = node.variations[1:]
        
        # 1. Draw main continuation move
        next_need_number = self.render_node_only(main_child, need_number, is_sub)
        
        # 2. Draw sub-variations inside nested parentheses (recursively)
        if sub_children:
            for sub_child in sub_children:
                self.move_text.insert(tk.END, "(")
                sub_need_num = self.render_node_only(sub_child, True, True)
                self.render_tree(sub_child, sub_need_num, True)
                self.move_text.insert(tk.END, ") ")
                
            next_need_number = True
            
        # 3. Recursively continue main line continuation
        self.render_tree(main_child, next_need_number, is_sub)

    def scroll_to_active_move(self):
        """Autoscrolls the moves list to show the currently selected move node."""
        if self.active_tag:
            try:
                self.move_text.see(self.active_tag)
            except Exception:
                pass

    def refresh_comment_box(self):
        """Reloads current position comments into the comment textbox."""
        self.comment_box.delete("1.0", tk.END)
        comment = self.game_manager.get_comment()
        if comment:
            self.comment_box.insert(tk.END, comment)

    def refresh_headers_panel(self):
        """Updates input header fields with current game metadata."""
        headers = self.game_manager.get_headers()
        
        self.ent_event.delete(0, tk.END)
        self.ent_event.insert(0, headers.get("Event", ""))
        
        self.ent_white.delete(0, tk.END)
        self.ent_white.insert(0, headers.get("White", ""))
        
        self.ent_black.delete(0, tk.END)
        self.ent_black.insert(0, headers.get("Black", ""))
        
        self.ent_site.delete(0, tk.END)
        self.ent_site.insert(0, headers.get("Site", ""))
        
        self.ent_date.delete(0, tk.END)
        self.ent_date.insert(0, headers.get("Date", ""))
        
        result = headers.get("Result", "*")
        if result in ["*", "1-0", "0-1", "1/2-1/2"]:
            self.ent_result.set(result)
        else:
            self.ent_result.set("*")

    def refresh_raw_pgn(self):
        """Fills raw PGN output pane."""
        self.pgn_textbox.delete("1.0", tk.END)
        self.pgn_textbox.insert(tk.END, self.game_manager.get_pgn_string())

    # --- Actions / Handlers ---
    def select_node(self, node):
        """Jumps directly to a given position node in the game history tree."""
        self.board.clear_drawings()
        self.game_manager.go_to_node(node)
        self.update_ui()

    def on_move_made(self):
        """Callback when a move is successfully played on the board."""
        self.board.clear_drawings()
        self.update_ui()

    def go_first(self):
        self.board.clear_drawings()
        self.game_manager.go_first()
        self.update_ui()

    def go_prev(self):
        self.board.clear_drawings()
        self.game_manager.go_prev()
        self.update_ui()

    def go_next(self):
        self.board.clear_drawings()
        self.game_manager.go_next()
        self.update_ui()

    def go_last(self):
        self.board.clear_drawings()
        self.game_manager.go_last()
        self.update_ui()

    def flip_board(self):
        self.board.flip()

    def delete_move(self):
        active_node = self.game_manager.active_node
        if active_node.parent:
            move_san = active_node.parent.board().san(active_node.move)
            confirm = messagebox.askyesno(
                "Delete Move",
                f"Are you sure you want to delete the move '{move_san}' and all subsequent variations/moves?"
            )
            if confirm:
                self.board.clear_drawings()
                self.game_manager.delete_current_node()
                self.update_ui()
        else:
            messagebox.showinfo("Delete Move", "Cannot delete the starting position.")

    def reset_board(self):
        confirm = messagebox.askyesno(
            "Reset Board",
            "Are you sure you want to completely reset the board and clear all moves?"
        )
        if confirm:
            self.board.clear_drawings()
            self.game_manager.reset_game()
            self.update_ui()

    def on_comment_focus_out(self, event):
        """Saves edited comments and updates the moves tree list when leaving textbox focus."""
        comment = self.comment_box.get("1.0", tk.END).strip()
        current_comment = self.game_manager.get_comment()
        if comment != current_comment:
            self.game_manager.set_comment(comment)
            self.refresh_moves_tree()
            self.refresh_raw_pgn()

    def add_move_annotation(self, nag):
        """Adds a move annotation badge (Brilliant, Blunder, etc.) to the active move."""
        if not self.game_manager.active_node.parent:
            messagebox.showinfo("Annotation", "Cannot annotate the starting position.")
            return
            
        self.game_manager.set_annotation_nag(nag)
        self.update_ui()

    def update_headers(self):
        """Saves game metadata details from input fields."""
        headers_dict = {
            "Event": self.ent_event.get(),
            "Site": self.ent_site.get(),
            "White": self.ent_white.get(),
            "Black": self.ent_black.get(),
            "Date": self.ent_date.get(),
            "Result": self.ent_result.get()
        }
        self.game_manager.update_headers(headers_dict)
        self.refresh_raw_pgn()
        messagebox.showinfo("Game Info", "Game details updated successfully!")

    def change_board_theme(self, theme_name):
        self.board.set_theme(theme_name)

    def change_piece_theme(self, piece_theme):
        self.board.set_piece_theme(piece_theme)

    # --- PGN File/Clipboard Handlers ---
    def load_pgn_file(self):
        filepath = filedialog.askopenfilename(
            title="Open PGN File",
            filetypes=[("PGN Files", "*.pgn"), ("All Files", "*.*")]
        )
        if filepath:
            self.board.clear_drawings()
            if self.game_manager.load_pgn_file(filepath):
                self.game_manager.autosave_path = filepath # Update active file target
                self.update_ui()
                messagebox.showinfo("Load PGN", f"Successfully loaded game from {os.path.basename(filepath)}")
            else:
                messagebox.showerror("Load PGN", "Failed to parse the PGN file. Make sure it is valid.")

    def save_pgn_file(self):
        filepath = filedialog.asksaveasfilename(
            title="Save PGN File",
            defaultextension=".pgn",
            filetypes=[("PGN Files", "*.pgn"), ("All Files", "*.*")]
        )
        if filepath:
            if self.game_manager.save_pgn_file(filepath):
                # Update current active file to this path
                self.game_manager.autosave_path = filepath
                messagebox.showinfo("Save PGN", f"Game saved successfully to {os.path.basename(filepath)}")
            else:
                messagebox.showerror("Save PGN", "Failed to save the PGN file.")

    def import_pgn_clipboard(self):
        try:
            clipboard_text = self.clipboard_get()
            if not clipboard_text.strip():
                raise Exception("Clipboard is empty.")
                
            self.board.clear_drawings()
            if self.game_manager.load_pgn_string(clipboard_text):
                self.update_ui()
                messagebox.showinfo("Import Clipboard", "Successfully imported PGN from clipboard!")
            else:
                messagebox.showerror("Import Clipboard", "Could not parse clipboard text as a valid PGN.")
        except Exception as e:
            messagebox.showerror("Import Clipboard", f"Failed to import from clipboard: {e}")

    def copy_pgn_clipboard(self):
        pgn_str = self.game_manager.get_pgn_string()
        self.clipboard_clear()
        self.clipboard_append(pgn_str)
        messagebox.showinfo("Copy PGN", "PGN copied to clipboard!")

    # --- Helpers ---
    def darken_color(self, hex_color):
        """Helper to darken badge colors slightly on hover."""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        dark_rgb = tuple(max(0, int(c * 0.8)) for c in rgb)
        return '#{:02x}{:02x}{:02x}'.format(*dark_rgb)

# ==========================================
# CUSTOM CHESS ENGINE HEURISTICS & MINIMAX
# ==========================================

# Piece-Square Tables (from White's perspective)
PAWN_PST = [
    0,  0,  0,  0,  0,  0,  0,  0,
    5, 10, 10,-20,-20, 10, 10,  5,
    5, -5,-10,  0,  0,-10, -5,  5,
    0,  0,  0, 20, 20,  0,  0,  0,
    5,  5, 10, 25, 25, 10,  5,  5,
   10, 10, 20, 30, 30, 20, 10, 10,
   50, 50, 50, 50, 50, 50, 50, 50,
    0,  0,  0,  0,  0,  0,  0,  0
]

KNIGHT_PST = [
   -50,-40,-30,-30,-30,-30,-40,-50,
   -40,-20,  0,  5,  5,  0,-20,-40,
   -30,  5, 10, 15, 15, 10,  5,-30,
   -30,  0, 15, 20, 20, 15,  0,-30,
   -30,  5, 15, 20, 20, 15,  5,-30,
   -30,  0, 10, 15, 15, 10,  0,-30,
   -40,-20,  0,  0,  0,  0,-20,-40,
   -50,-40,-30,-30,-30,-30,-40,-50
]

BISHOP_PST = [
   -20,-10,-10,-10,-10,-10,-10,-20,
   -10,  5,  0,  0,  0,  0,  5,-10,
   -10, 10, 10, 10, 10, 10, 10,-10,
   -10,  0, 10, 10, 10, 10,  0,-10,
   -10,  5,  5, 10, 10,  5,  5,-10,
   -10,  0,  0, 10, 10,  0,  0,-10,
   -10,  0,  0,  0,  0,  0,  0,-10,
   -20,-10,-10,-10,-10,-10,-10,-20
]

ROOK_PST = [
     0,  0,  0,  5,  5,  0,  0,  0,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
     5, 10, 10, 10, 10, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0
]

QUEEN_PST = [
   -20,-10,-10, -5, -5,-10,-10,-20,
   -10,  0,  5,  0,  0,  0,  0,-10,
   -10,  5,  5,  5,  5,  5,  0,-10,
     0,  0,  5,  5,  5,  5,  0, -5,
    -5,  0,  5,  5,  5,  5,  0, -5,
   -10,  0,  5,  5,  5,  5,  0,-10,
   -10,  0,  0,  0,  0,  0,  0,-10,
   -20,-10,-10, -5, -5,-10,-10,-20
]

KING_PST = [
    20, 30, 10,  0,  0, 10, 30, 20,
    20, 20,  0,  0,  0,  0, 20, 20,
   -10,-20,-20,-20,-20,-20,-20,-10,
   -20,-30,-30,-40,-40,-30,-30,-20,
   -30,-40,-40,-50,-50,-40,-40,-30,
   -30,-40,-40,-50,-50,-40,-40,-30,
   -30,-40,-40,-50,-50,-40,-40,-30,
   -30,-40,-40,-50,-50,-40,-40,-30
]

def evaluate_board(board):
    if board.is_checkmate():
        return -99999 if board.turn == chess.WHITE else 99999
    if board.is_stalemate() or board.is_insufficient_material():
        return 0
        
    score = 0
    piece_vals = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 20000
    }
    
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            val = piece_vals[piece.piece_type]
            sq_idx = square if piece.color == chess.WHITE else chess.square_mirror(square)
            
            pst_val = 0
            if piece.piece_type == chess.PAWN:
                pst_val = PAWN_PST[sq_idx]
            elif piece.piece_type == chess.KNIGHT:
                pst_val = KNIGHT_PST[sq_idx]
            elif piece.piece_type == chess.BISHOP:
                pst_val = BISHOP_PST[sq_idx]
            elif piece.piece_type == chess.ROOK:
                pst_val = ROOK_PST[sq_idx]
            elif piece.piece_type == chess.QUEEN:
                pst_val = QUEEN_PST[sq_idx]
            elif piece.piece_type == chess.KING:
                pst_val = KING_PST[sq_idx]
                
            scaled_pst = pst_val / 10.0
            if piece.color == chess.WHITE:
                score += (val + scaled_pst)
            else:
                score -= (val + scaled_pst)
                
    return score

def quiescence_search(board, alpha, beta, maximizing_player):
    stand_pat = evaluate_board(board)
    
    if maximizing_player:
        if stand_pat >= beta:
            return beta
        if alpha < stand_pat:
            alpha = stand_pat
            
        moves = [m for m in board.legal_moves if board.is_capture(m)]
        moves.sort(key=lambda m: board.is_capture(m), reverse=True)
        
        for move in moves:
            board.push(move)
            score = quiescence_search(board, alpha, beta, False)
            board.pop()
            
            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
        return alpha
    else:
        if stand_pat <= alpha:
            return alpha
        if beta > stand_pat:
            beta = stand_pat
            
        moves = [m for m in board.legal_moves if board.is_capture(m)]
        moves.sort(key=lambda m: board.is_capture(m), reverse=True)
        
        for move in moves:
            board.push(move)
            score = quiescence_search(board, alpha, beta, True)
            board.pop()
            
            if score <= alpha:
                return alpha
            if score < beta:
                beta = score
        return beta

def minimax(board, depth, alpha, beta, maximizing_player):
    if board.is_game_over():
        return evaluate_board(board), None
        
    if depth == 0:
        return quiescence_search(board, alpha, beta, maximizing_player), None
        
    best_move = None
    if maximizing_player:
        max_eval = -999999
        moves = list(board.legal_moves)
        moves.sort(key=lambda m: board.is_capture(m), reverse=True)
        
        for move in moves:
            board.push(move)
            eval_score, _ = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = 999999
        moves = list(board.legal_moves)
        moves.sort(key=lambda m: board.is_capture(m), reverse=True)
        
        for move in moves:
            board.push(move)
            eval_score, _ = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval, best_move

if __name__ == "__main__":
    app = ChessMoveToolApp()
    app.mainloop()
