import pygame
import chess
import chess.engine
import random
import os

# === SETTINGS ===
SQUARE_SIZE = 80
BOARD_SIZE = 8 * SQUARE_SIZE
FPS = 30

# Path to Stockfish
STOCKFISH_PATH = r"C:\Users\Hiten Vashistha\Downloads\stockfish-windows-x86-64-avx2\stockfish\stockfish-windows-x86-64-avx2.exe"

# Piece images
PIECE_IMAGES = {}
PIECE_FILES = {
    'P': 'wp.png', 'N': 'wn.png', 'B': 'wb.png', 'R': 'wr.png', 'Q': 'wq.png', 'K': 'wk.png',
    'p': 'bp.png', 'n': 'bn.png', 'b': 'bb.png', 'r': 'br.png', 'q': 'bq.png', 'k': 'bk.png'
}

# === INIT ===
pygame.init()
screen = pygame.display.set_mode((BOARD_SIZE, BOARD_SIZE))
pygame.display.set_caption("Python Chess (Player vs AI / Player vs Player)")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 38, bold=True)

# Load images
for symbol, filename in PIECE_FILES.items():
    img = pygame.image.load("chesspieces/" + filename)
    PIECE_IMAGES[symbol] = pygame.transform.smoothscale(img, (SQUARE_SIZE, SQUARE_SIZE))

# Colors
LIGHT = (240, 217, 181)
DARK = (181, 136, 99)
HIGHLIGHT = (186, 202, 68)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BG_COLOR = (30, 30, 30)

# === GAME STATE ===
board = chess.Board()
selected_square = None
legal_moves_from_selected = []
frame_counter = 0
game_mode = None
AI_DEPTH = 15
engine = None
game_over = False
winner_text = ""

# === ENGINE SETUP ===
def load_engine(strength_level):
    """Load Stockfish and set depth."""
    global engine, AI_DEPTH
    if os.path.exists(STOCKFISH_PATH):
        try:
            engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
            engine.configure({"Skill Level": 20})
            if strength_level == "beginner":
                AI_DEPTH = 6
            elif strength_level == "intermediate":
                AI_DEPTH = 12
            elif strength_level == "master":
                AI_DEPTH = 18
            print(f"✅ Stockfish loaded (Depth {AI_DEPTH})")
        except Exception as e:
            print("⚠ Engine load error:", e)
            engine = None
    else:
        print("⚠ Stockfish not found. Using random AI.")
        engine = None

# === DRAW FUNCTIONS ===
def draw_board():
    for rank in range(8):
        for file in range(8):
            color = LIGHT if (rank + file) % 2 == 0 else DARK
            x = file * SQUARE_SIZE
            y = (7 - rank) * SQUARE_SIZE
            pygame.draw.rect(screen, color, (x, y, SQUARE_SIZE, SQUARE_SIZE))

    if selected_square is not None:
        for move in legal_moves_from_selected:
            file = chess.square_file(move.to_square)
            rank = chess.square_rank(move.to_square)
            x = file * SQUARE_SIZE
            y = (7 - rank) * SQUARE_SIZE
            pygame.draw.rect(screen, HIGHLIGHT, (x, y, SQUARE_SIZE, SQUARE_SIZE), 4)

def draw_pieces():
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            symbol = piece.symbol()
            file = chess.square_file(square)
            rank = chess.square_rank(square)
            x = file * SQUARE_SIZE
            y = (7 - rank) * SQUARE_SIZE
            screen.blit(PIECE_IMAGES[symbol], (x, y))

def draw_check():
    if board.is_check():
        king_square = board.king(board.turn)
        if king_square is not None:
            file = chess.square_file(king_square)
            rank = chess.square_rank(king_square)
            x = file * SQUARE_SIZE
            y = (7 - rank) * SQUARE_SIZE
            pygame.draw.rect(screen, RED, (x, y, SQUARE_SIZE, SQUARE_SIZE), 5)

def get_square_under_mouse(pos):
    x, y = pos
    file = x // SQUARE_SIZE
    rank = 7 - (y // SQUARE_SIZE)
    if 0 <= file < 8 and 0 <= rank < 8:
        return chess.square(file, rank)
    return None

# === AI MOVE ===
def ai_move():
    global board, engine
    if engine is None:
        move = random.choice(list(board.legal_moves))
        board.push(move)
        return
    try:
        result = engine.play(board, chess.engine.Limit(depth=AI_DEPTH))
        board.push(result.move)
    except Exception as e:
        print("⚠ AI failed:", e)
        move = random.choice(list(board.legal_moves))
        board.push(move)

# === GAME OVER SCREEN ===
def draw_game_over(result_text):
    screen.fill(BG_COLOR)
    title = font.render("Game Over", True, WHITE)
    result = font.render(result_text, True, WHITE)
    restart = font.render("Press R to Restart", True, WHITE)
    quit_text = font.render("Press Q to Quit", True, WHITE)
    screen.blit(title, (BOARD_SIZE//2 - title.get_width()//2, 150))
    screen.blit(result, (BOARD_SIZE//2 - result.get_width()//2, 240))
    screen.blit(restart, (BOARD_SIZE//2 - restart.get_width()//2, 340))
    screen.blit(quit_text, (BOARD_SIZE//2 - quit_text.get_width()//2, 400))
    pygame.display.flip()

# === MENUS ===
def draw_menu():
    screen.fill(BG_COLOR)
    title = font.render("Choose Game Mode", True, WHITE)
    text1 = font.render("1. Player vs Player", True, WHITE)
    text2 = font.render("2. Player vs AI", True, WHITE)
    screen.blit(title, (BOARD_SIZE//2 - title.get_width()//2, 150))
    screen.blit(text1, (BOARD_SIZE//2 - text1.get_width()//2, 280))
    screen.blit(text2, (BOARD_SIZE//2 - text2.get_width()//2, 340))
    pygame.display.flip()

def draw_strength_menu():
    screen.fill(BG_COLOR)
    title = font.render("Select AI Strength", True, WHITE)
    s1 = font.render("1. Beginner (Depth 6)", True, WHITE)
    s2 = font.render("2. Intermediate (Depth 12)", True, WHITE)
    s3 = font.render("3. Master (Depth 18)", True, WHITE)
    screen.blit(title, (BOARD_SIZE//2 - title.get_width()//2, 150))
    screen.blit(s1, (BOARD_SIZE//2 - s1.get_width()//2, 260))
    screen.blit(s2, (BOARD_SIZE//2 - s2.get_width()//2, 320))
    screen.blit(s3, (BOARD_SIZE//2 - s3.get_width()//2, 380))
    pygame.display.flip()

# === MAIN LOOP ===
running = True
in_menu = True
in_strength_menu = False

def reset_game():
    global board, selected_square, legal_moves_from_selected, game_over, winner_text
    board.reset()
    selected_square = None
    legal_moves_from_selected = []
    game_over = False
    winner_text = ""

while running:
    clock.tick(FPS)
    frame_counter = (frame_counter + 1) % 30

    # MENU
    if in_menu:
        draw_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    game_mode = "pvp"
                    in_menu = False
                elif event.key == pygame.K_2:
                    game_mode = "ai"
                    in_menu = False
                    in_strength_menu = True
        continue

    # STRENGTH MENU
    if in_strength_menu:
        draw_strength_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    load_engine("beginner")
                elif event.key == pygame.K_2:
                    load_engine("intermediate")
                elif event.key == pygame.K_3:
                    load_engine("master")
                in_strength_menu = False
        continue

    # GAME OVER SCREEN
    if game_over:
        draw_game_over(winner_text)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game()
                elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                    running = False
        continue

    # GAME LOOP
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and not board.is_game_over():
            clicked = get_square_under_mouse(event.pos)
            if clicked is not None:
                if selected_square is None:
                    piece = board.piece_at(clicked)
                    if piece and piece.color == board.turn:
                        selected_square = clicked
                        legal_moves_from_selected = [
                            move for move in board.legal_moves if move.from_square == selected_square
                        ]
                else:
                    move = chess.Move(selected_square, clicked)
                    if move.promotion is None and board.piece_at(selected_square) and \
                            board.piece_at(selected_square).piece_type == chess.PAWN:
                        if chess.square_rank(clicked) in (0, 7):
                            move = chess.Move(selected_square, clicked, promotion=chess.QUEEN)

                    if move in board.legal_moves:
                        board.push(move)
                        if board.is_game_over():
                            game_over = True
                            result = board.result()
                            if result == "1-0":
                                winner_text = "White Wins!"
                            elif result == "0-1":
                                winner_text = "Black Wins!"
                            else:
                                winner_text = "Draw!"
                        elif game_mode == "ai" and not board.is_game_over() and board.turn == chess.BLACK:
                            ai_move()
                            if board.is_game_over():
                                game_over = True
                                result = board.result()
                                if result == "1-0":
                                    winner_text = "White Wins!"
                                elif result == "0-1":
                                    winner_text = "Black Wins!"
                                else:
                                    winner_text = "Draw!"
                    selected_square = None
                    legal_moves_from_selected = []

    # DRAW
    draw_board()
    draw_pieces()
    if board.is_check() and frame_counter < 15:
        draw_check()
    pygame.display.flip()

# CLEANUP
if engine:
    engine.quit()
pygame.quit()