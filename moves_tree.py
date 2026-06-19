import tkinter as tk
import customtkinter as ctk
import chess
import re
from theme import ANNOTATION_THEMES

def clean_comment(comment):
    if not comment:
        return ""
    # Remove all [%...] command annotations
    cleaned = re.sub(r'\[%[^\]]*\]', '', comment)
    # Strip any extra spaces
    cleaned = cleaned.strip()
    return cleaned

class ChessMoveTree(ctk.CTkScrollableFrame):
    def __init__(self, master, select_callback=None, **kwargs):
        # Configure default styling matching dark theme
        kwargs.setdefault("fg_color", "#18181b")
        kwargs.setdefault("label_text", "")
        super().__init__(master, **kwargs)
        
        self.select_callback = select_callback
        
        # Configure columns of the main scrollable frame container
        self.grid_columnconfigure(0, weight=1)
        
        # Track widget mapping for active node highlighting and scrolling
        # Maps node -> widget (CTkButton for mainline, tk.Text for subline)
        self.node_widgets = {}
        self.active_widget = None

    def update_moves(self, game, active_node):
        """Clears and rebuilds the move list UI based on the game tree."""
        # Clear existing widgets
        for widget in self.winfo_children():
            widget.destroy()
            
        self.node_widgets.clear()
        self.active_widget = None
        
        if not game.variations:
            # Placeholder label when no moves have been played
            lbl = ctk.CTkLabel(
                self, 
                text="No moves played yet. Use the board to make moves.", 
                font=("Inter", 10, "italic"),
                text_color="#71717a"
            )
            lbl.grid(row=0, column=0, padx=15, pady=15, sticky="w")
            return
            
        # 1. Traverse game tree to collect mainline move pairs and sidelines
        elements = self._traverse_game_tree(game)
        
        # 2. Render each element in order
        row_idx = 0
        for elem_type, *args in elements:
            if elem_type == 'main':
                row_data = args[0]
                self._render_main_row(row_idx, row_data, active_node)
                row_idx += 1
            elif elem_type == 'sideline':
                parent_node, sidelines, is_black_turn = args
                self._render_sideline_row(row_idx, parent_node, sidelines, is_black_turn, active_node)
                row_idx += 1
            elif elem_type == 'comment':
                node, comment_text = args
                self._render_comment_row(row_idx, node, comment_text)
                row_idx += 1
                
        # 3. Scroll viewport to active node widget
        if active_node in self.node_widgets:
            widget = self.node_widgets[active_node]
            self.scroll_to_widget(widget)

    def _traverse_game_tree(self, game):
        """Flat-traverses the game tree to group moves and capture sidelines/comments."""
        board = game.board()
        node = game
        elements = []
        current_row = None
        
        while node.variations:
            main_child = node.variations[0]
            sidelines = node.variations[1:]
            
            turn = board.turn
            fullmove = board.fullmove_number
            
            if turn == chess.WHITE:
                current_row = {'num': fullmove, 'white': main_child, 'black': None}
                elements.append(('main', current_row))
                
                if sidelines:
                    elements.append(('sideline', node, sidelines, False))
            else:
                if current_row and current_row['num'] == fullmove:
                    current_row['black'] = main_child
                else:
                    current_row = {'num': fullmove, 'white': None, 'black': main_child}
                    elements.append(('main', current_row))
                    
                if sidelines:
                    elements.append(('sideline', node, sidelines, True))
                    
            if main_child.comment:
                elements.append(('comment', main_child, main_child.comment))
                
            board.push(main_child.move)
            node = main_child
            
        return elements

    def _render_main_row(self, row_idx, row_data, active_node):
        """Renders a standard mainline row with alternating background."""
        row_bg = "#18181b" if row_idx % 2 == 0 else "#202024"
        row_frame = ctk.CTkFrame(self, fg_color=row_bg, corner_radius=0, height=28)
        row_frame.grid(row=row_idx, column=0, columnspan=3, sticky="ew")
        
        row_frame.grid_columnconfigure(0, minsize=45, weight=0)
        row_frame.grid_columnconfigure(1, minsize=100, weight=1)
        row_frame.grid_columnconfigure(2, minsize=100, weight=1)
        
        # Column 0: Move number
        num_lbl = ctk.CTkLabel(
            row_frame, 
            text=f"{row_data['num']}.", 
            font=("Inter", 11, "bold"), 
            text_color="#71717a", 
            anchor="e"
        )
        num_lbl.grid(row=0, column=0, sticky="e", padx=(10, 5), pady=2)
        
        # Column 1: White Move button
        w_node = row_data['white']
        if w_node:
            board_before = w_node.parent.board()
            san = board_before.san(w_node.move)
            nag = next(iter(w_node.nags)) if w_node.nags else None
            nag_symbol = ANNOTATION_THEMES[nag]["symbol"] if nag in ANNOTATION_THEMES else ""
            display_str = f"{san}{nag_symbol}"
            
            is_active = (w_node == active_node)
            btn_fg = "#1e3a8a" if is_active else "transparent"
            btn_text_color = "#3b82f6" if is_active else "#e4e4e7"
            
            btn_white = ctk.CTkButton(
                row_frame,
                text=display_str,
                font=("Inter", 11, "bold"),
                anchor="w",
                fg_color=btn_fg,
                hover_color="#2d2d30",
                text_color=btn_text_color,
                corner_radius=4,
                height=24,
                width=90,
                command=lambda n=w_node: self._on_move_clicked(n)
            )
            btn_white.grid(row=0, column=1, sticky="w", padx=5, pady=2)
            self.node_widgets[w_node] = btn_white
            if is_active:
                self.active_widget = btn_white
                
        # Column 2: Black Move button
        b_node = row_data['black']
        if b_node:
            board_before = b_node.parent.board()
            san = board_before.san(b_node.move)
            nag = next(iter(b_node.nags)) if b_node.nags else None
            nag_symbol = ANNOTATION_THEMES[nag]["symbol"] if nag in ANNOTATION_THEMES else ""
            display_str = f"{san}{nag_symbol}"
            
            is_active = (b_node == active_node)
            btn_fg = "#1e3a8a" if is_active else "transparent"
            btn_text_color = "#3b82f6" if is_active else "#e4e4e7"
            
            btn_black = ctk.CTkButton(
                row_frame,
                text=display_str,
                font=("Inter", 11, "bold"),
                anchor="w",
                fg_color=btn_fg,
                hover_color="#2d2d30",
                text_color=btn_text_color,
                corner_radius=4,
                height=24,
                width=90,
                command=lambda n=b_node: self._on_move_clicked(n)
            )
            btn_black.grid(row=0, column=2, sticky="w", padx=5, pady=2)
            self.node_widgets[b_node] = btn_black
            if is_active:
                self.active_widget = btn_black

    def _render_sideline_row(self, row_idx, parent_node, sidelines, is_black_turn, active_node):
        """Renders sidelines in a full-width row with clickable text tags."""
        sub_frame = ctk.CTkFrame(self, fg_color="transparent")
        sub_frame.grid(row=row_idx, column=0, columnspan=3, sticky="ew", padx=(20, 10), pady=2)
        
        # Word-wrapped flat text box styled as label
        txt_widget = tk.Text(
            sub_frame,
            wrap=tk.WORD,
            bg="#18181b",
            fg="#cbd5e1",
            font=("Inter", 10),
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0,
            height=1
        )
        txt_widget.pack(fill=tk.BOTH, expand=True)
        
        # Compile segments (prefix, move text, sub-parentheses)
        segments = []
        for i, sideline in enumerate(sidelines):
            if i > 0:
                segments.append(("; ", None))
            board_state = parent_node.board()
            segments.extend(self._format_variation(sideline, board_state, need_number=True))
            
        txt_widget.config(state="normal")
        txt_widget.delete("1.0", tk.END)
        
        # Default tag for structural symbols (brackets, separators)
        txt_widget.tag_config("muted", foreground="#71717a", font=("Inter", 10))
        
        for text, node in segments:
            if node:
                tag_name = f"node_{id(node)}"
                txt_widget.insert(tk.END, text, tag_name)
                
                is_active = (node == active_node)
                fg_color = "#3b82f6" if is_active else "#cbd5e1"
                weight = "bold" if is_active else "normal"
                
                txt_widget.tag_config(tag_name, foreground=fg_color, font=("Inter", 10, weight))
                
                # Dynamic hover/click events
                txt_widget.tag_bind(tag_name, "<Button-1>", lambda e, n=node: self._on_move_clicked(n))
                txt_widget.tag_bind(tag_name, "<Enter>", lambda e, t=tag_name: txt_widget.tag_config(t, underline=True))
                txt_widget.tag_bind(tag_name, "<Leave>", lambda e, t=tag_name: txt_widget.tag_config(t, underline=False))
                
                if is_active:
                    self.node_widgets[node] = txt_widget
            else:
                txt_widget.insert(tk.END, text, "muted")
                
        txt_widget.config(state="disabled")
        
        # Dynamically set height of Text widget to fit lines
        self.update_idletasks()
        num_lines = int(txt_widget.index('end-1c').split('.')[0])
        txt_widget.config(height=num_lines)

    def _render_comment_row(self, row_idx, node, comment_text):
        """Renders an inline comment row in green italics."""
        cleaned_comment = clean_comment(comment_text)
        if not cleaned_comment:
            return
            
        comment_frame = ctk.CTkFrame(self, fg_color="transparent")
        comment_frame.grid(row=row_idx, column=0, columnspan=3, sticky="ew", padx=(25, 10), pady=1)
        
        lbl = ctk.CTkLabel(
            comment_frame, 
            text=f"{{ {cleaned_comment} }}", 
            font=("Inter", 10, "italic"), 
            text_color="#10b981", 
            justify="left", 
            anchor="w"
        )
        lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _format_variation(self, node, board, need_number=True):
        """Recursively formats a variation subtree to segments of (text, node_ref)."""
        segments = []
        board_before = board.copy()
        
        san = board_before.san(node.move)
        nag = next(iter(node.nags)) if node.nags else None
        nag_symbol = ANNOTATION_THEMES[nag]["symbol"] if nag in ANNOTATION_THEMES else ""
        display_str = f"{san}{nag_symbol}"
        
        if board_before.turn == chess.WHITE:
            prefix = f"{board_before.fullmove_number}. "
            next_need_number = False
        else:
            prefix = f"{board_before.fullmove_number}... " if need_number else ""
            next_need_number = True
            
        if prefix:
            segments.append((prefix, None))
            
        segments.append((display_str, node))
        
        cleaned_comment = clean_comment(node.comment) if node.comment else ""
        if cleaned_comment:
            segments.append((f" {{ {cleaned_comment} }} ", None))
            next_need_number = True
            
        board_before.push(node.move)
        
        main_child = node.variations[0] if node.variations else None
        sub_children = node.variations[1:] if node.variations else []
        
        if sub_children:
            for sub in sub_children:
                segments.append((" (", None))
                segments.extend(self._format_variation(sub, board_before, need_number=True))
                segments.append((")", None))
            next_need_number = True
            
        if main_child:
            segments.append((" ", None))
            segments.extend(self._format_variation(main_child, board_before, next_need_number))
            
        return segments

    def _on_move_clicked(self, node):
        if self.select_callback:
            self.select_callback(node)

    def scroll_to_widget(self, widget):
        """Autoscrolls the frame to center the active move's widget in the viewport."""
        self.update_idletasks()
        try:
            total_height = self.winfo_height()
            if total_height <= 0:
                return
                
            widget_y = widget.winfo_y()
            widget_height = widget.winfo_height()
            viewport_height = self._parent_canvas.winfo_height()
            
            # Center alignment logic
            scroll_y = widget_y - (viewport_height - widget_height) / 2
            fraction = max(0.0, min(1.0, scroll_y / total_height))
            
            self._parent_canvas.yview_moveto(fraction)
        except Exception:
            pass
