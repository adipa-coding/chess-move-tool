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
        
        self.setup_moves_tab()
        self.setup_pgn_tab()

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

    # --- UI Synchronization ---
    def update_ui(self):
        """Redraws the board, refreshes the moves tree list, and refreshes the metadata panel."""
        self.board.draw_board()
        self.refresh_moves_tree()
        self.refresh_comment_box()
        self.refresh_headers_panel()
        self.refresh_raw_pgn()
        self.update_opening_display()

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

if __name__ == "__main__":
    app = ChessMoveToolApp()
    app.mainloop()
