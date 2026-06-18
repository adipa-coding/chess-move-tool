import os
import urllib.request
import urllib.error
from PIL import Image, ImageTk

# Base URLs for Chess.com themes
THEME_URLS = {
    "neo": "https://images.chesscomfiles.com/chess-themes/pieces/neo/150/",
    "classic": "https://images.chesscomfiles.com/chess-themes/pieces/classic/150/",
    "wood": "https://images.chesscomfiles.com/chess-themes/pieces/wood/150/",
    "light": "https://images.chesscomfiles.com/chess-themes/pieces/light/150/"
}

PIECES = ["wp", "wn", "wb", "wr", "wq", "wk", "bp", "bn", "bb", "br", "bq", "bk"]

def get_assets_dir():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(current_dir, "assets")
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
    return assets_dir

def download_theme_pieces(theme_name="neo"):
    """Downloads all 12 chess pieces for a given theme if they do not exist locally."""
    assets_dir = get_assets_dir()
    theme_dir = os.path.join(assets_dir, theme_name)
    if not os.path.exists(theme_dir):
        os.makedirs(theme_dir)
    
    base_url = THEME_URLS.get(theme_name, THEME_URLS["neo"])
    
    downloaded = 0
    errors = 0
    
    for piece in PIECES:
        filename = f"{piece}.png"
        filepath = os.path.join(theme_dir, filename)
        
        if not os.path.exists(filepath):
            url = f"{base_url}{filename}"
            try:
                # Add headers to avoid user-agent blocking
                req = urllib.request.Request(
                    url, 
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                )
                with urllib.request.urlopen(req) as response:
                    with open(filepath, 'wb') as out_file:
                        out_file.write(response.read())
                downloaded += 1
            except urllib.error.URLError as e:
                print(f"Error downloading {piece} from {url}: {e}")
                errors += 1
                
    return downloaded, errors

def load_pieces_images(theme_name="neo", size=(64, 64)):
    """Loads piece images and returns a dict mapping piece code (e.g. 'P', 'n') to PhotoImage."""
    # Ensure they are downloaded
    download_theme_pieces(theme_name)
    
    assets_dir = get_assets_dir()
    theme_dir = os.path.join(assets_dir, theme_name)
    
    images = {}
    
    # Map python-chess piece symbols to filenames
    # White pieces are uppercase, black are lowercase
    symbol_to_file = {
        'P': 'wp', 'N': 'wn', 'B': 'wb', 'R': 'wr', 'Q': 'wq', 'K': 'wk',
        'p': 'bp', 'n': 'bn', 'b': 'bb', 'r': 'br', 'q': 'bq', 'k': 'bk'
    }
    
    for symbol, filename in symbol_to_file.items():
        filepath = os.path.join(theme_dir, f"{filename}.png")
        if os.path.exists(filepath):
            try:
                img = Image.open(filepath)
                img = img.resize(size, Image.Resampling.LANCZOS)
                images[symbol] = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Error loading image {filepath}: {e}")
                # Fallback to empty image or draw a letter
                images[symbol] = None
        else:
            images[symbol] = None
            
    return images

if __name__ == "__main__":
    print("Testing asset downloader...")
    dl, err = download_theme_pieces("neo")
    print(f"Downloaded: {dl}, Errors: {err}")
    dl, err = download_theme_pieces("classic")
    print(f"Classic - Downloaded: {dl}, Errors: {err}")
    dl, err = download_theme_pieces("wood")
    print(f"Wood - Downloaded: {dl}, Errors: {err}")
    dl, err = download_theme_pieces("light")
    print(f"Light - Downloaded: {dl}, Errors: {err}")
