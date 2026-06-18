import tkinter as tk
import customtkinter as ctk
import chess
import time
import sys
import traceback

from main import ChessMoveToolApp

def test_gui():
    print("Initializing GUI app...")
    app = ChessMoveToolApp()
    
    # Hide window so it doesn't pop up during test
    app.withdraw()
    
    # Enable engine and toggle switch
    app.engine_switch.select()
    app.toggle_engine()
    
    def run_moves_and_check():
        # Check if engine is ready
        if app.engine is None:
            print("Engine is still starting... waiting 200ms")
            app.after(200, run_moves_and_check)
            return
            
        try:
            print(f"Engine status: Enabled={app.engine_enabled}, EngineObject={app.engine}")
            
            # Play moves: e4 f5 Nc3 g5
            moves = ["e4", "f5", "Nc3", "g5"]
            for m in moves:
                board = app.game_manager.get_current_board()
                move = board.parse_san(m)
                print(f"Playing move: {m}")
                app.game_manager.make_move(move)
                app.on_move_made()
                app.update()
                
            print("Waiting for engine calculations to process...")
            
            def poll_results(attempts=0):
                app.update()
                score_text = app.lbl_sf_eval.cget('text')
                print(f"Polling attempt {attempts}: {score_text}")
                # We expect score_text to become something like "+M1"
                if ("Calculating" not in score_text and "Starting" not in score_text) or attempts >= 20:
                    print("\n--- Final GUI Engine Card Labels ---")
                    print(f"Score Label: {app.lbl_sf_eval.cget('text')}")
                    print(f"Best Move Label: {app.lbl_sf_best.cget('text')}")
                    print(f"Depth Label: {app.lbl_sf_depth.cget('text')}")
                    print(f"Speed Label: {app.lbl_sf_speed.cget('text')}")
                    print(f"PV Line Label: {app.lbl_sf_pv.cget('text')}")
                    app.on_closing()
                else:
                    app.after(200, lambda: poll_results(attempts + 1))
            
            app.after(500, poll_results)
        except Exception as e:
            traceback.print_exc()
            app.on_closing()
            
    app.after(100, run_moves_and_check)
    app.mainloop()
    print("Test finished.")

if __name__ == "__main__":
    try:
        test_gui()
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)

