import streamlit as st
import random
import numpy as np
import matplotlib.pyplot as plt
import time

st.set_page_config(page_title="Snake and Ladder - 2 Players", layout="centered")

# --- GAME SETTINGS ---
BOARD_SIZE = 10
SNAKES = {99: 54, 70: 55, 52: 42, 25: 2}
LADDERS = {6: 25, 11: 40, 60: 85, 46: 90}

# --- SESSION STATE ---
if "positions" not in st.session_state:
    st.session_state.positions = {"P1": 1, "P2": 1}
if "last_roll" not in st.session_state:
    st.session_state.last_roll = None
if "message" not in st.session_state:
    st.session_state.message = "🎲 Player 1 starts!"
if "turn" not in st.session_state:
    st.session_state.turn = "P1"
if "winner" not in st.session_state:
    st.session_state.winner = None
if "turn_count" not in st.session_state:
    st.session_state.turn_count = {"P1": 0, "P2": 0}
if "wins" not in st.session_state:
    st.session_state.wins = {"P1": 0, "P2": 0}

# --- FUNCTIONS ---
def roll_dice():
    if st.session_state.winner:
        return  # Game over, stop

    dice_placeholder = st.empty()

    # Simulate dice rolling animation
    for _ in range(8):  
        temp_roll = random.randint(1, 6)
        dice_placeholder.image(f"https://raw.githubusercontent.com/rodrigorgs/dice-emoji/main/png/{temp_roll}.png", width=80)
        time.sleep(0.15)

    roll = random.randint(1, 6)
    st.session_state.last_roll = roll
    dice_placeholder.image(f"https://raw.githubusercontent.com/rodrigorgs/dice-emoji/main/png/{roll}.png", width=80)

    player = st.session_state.turn
    st.session_state.turn_count[player] += 1  # track turns

    pos = st.session_state.positions[player] + roll

    if pos > 100:
        pos = st.session_state.positions[player]  # Can't move if overshoots

    # Check snakes
    if pos in SNAKES:
        st.session_state.message = f"😱 {player} got bitten by a snake at {pos}, down to {SNAKES[pos]}"
        pos = SNAKES[pos]
    # Check ladders
    elif pos in LADDERS:
        st.session_state.message = f"🎉 {player} climbed a ladder at {pos}, up to {LADDERS[pos]}"
        pos = LADDERS[pos]
    else:
        st.session_state.message = f"{player} moved to {pos}"

    st.session_state.positions[player] = pos

    if pos == 100:
        st.session_state.message = f"🏆 {player} WINS the game!"
        st.session_state.winner = player
        st.session_state.wins[player] += 1  # track wins
        return
    
    # Alternate turn
    st.session_state.turn = "P2" if player == "P1" else "P1"
    st.session_state.message += f" | 👉 {st.session_state.turn}'s turn."

def reset_game():
    st.session_state.positions = {"P1": 1, "P2": 1}
    st.session_state.last_roll = None
    st.session_state.message = "🎲 Player 1 starts!"
    st.session_state.turn = "P1"
    st.session_state.winner = None
    st.session_state.turn_count = {"P1": 0, "P2": 0}

# --- UI ---
st.title("🐍 Snake and Ladder 🎲 - 2 Players")
st.write("Player 1 (🔵) vs Player 2 (🔴)")

col1, col2 = st.columns(2)
with col1:
    if st.button("🎲 Roll Dice", use_container_width=True):
        roll_dice()
with col2:
    if st.button("🔄 Reset Game", use_container_width=True):
        reset_game()

st.info(st.session_state.message)

# --- SCOREBOARD ---
st.subheader("📊 Scoreboard")
col1, col2 = st.columns(2)

with col1:
    st.metric("Player 1 Turns", st.session_state.turn_count["P1"])
    st.metric("Player 1 Wins", st.session_state.wins["P1"])
with col2:
    st.metric("Player 2 Turns", st.session_state.turn_count["P2"])
    st.metric("Player 2 Wins", st.session_state.wins["P2"])

# --- BOARD CREATION (zig-zag) ---
def create_snake_board(size):
    board = np.zeros((size, size), dtype=int)
    num = 1
    for i in range(size):
        row = size - 1 - i  # start from bottom row
        if i % 2 == 0:  # left to right
            for col in range(size):
                board[row, col] = num
                num += 1
        else:  # right to left
            for col in range(size-1, -1, -1):
                board[row, col] = num
                num += 1
    return board

def get_coordinates(num, board):
    coords = np.argwhere(board == num)
    if coords.size > 0:
        y, x = coords[0]
        return x, y
    return None

# --- PLOT ---
def plot_board(pos1, pos2):
    board = create_snake_board(BOARD_SIZE)

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xticks([])
    ax.set_yticks([])
    ax.imshow(np.ones_like(board), cmap="Pastel1")
    
    # Draw numbers
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            num = board[i, j]
            ax.text(j, i, str(num), ha="center", va="center", fontsize=8)
    
    # Draw ladders (green arrows)
    for start, end in LADDERS.items():
        start_xy = get_coordinates(start, board)
        end_xy = get_coordinates(end, board)
        if start_xy and end_xy:
            ax.annotate("",
                        xy=end_xy, xycoords="data",
                        xytext=start_xy, textcoords="data",
                        arrowprops=dict(arrowstyle="->", color="green", lw=2))
    
    # Draw snakes (red arrows)
    for start, end in SNAKES.items():
        start_xy = get_coordinates(start, board)
        end_xy = get_coordinates(end, board)
        if start_xy and end_xy:
            ax.annotate("",
                        xy=end_xy, xycoords="data",
                        xytext=start_xy, textcoords="data",
                        arrowprops=dict(arrowstyle="->", color="red", lw=2))
    
    # Player 1 (Blue)
    coords1 = get_coordinates(pos1, board)
    if coords1:
        ax.plot(coords1[0], coords1[1], "bo", markersize=15, label="P1")
    
    # Player 2 (Red)
    coords2 = get_coordinates(pos2, board)
    if coords2:
        ax.plot(coords2[0], coords2[1], "ro", markersize=15, label="P2")
    
    st.pyplot(fig)

# Show board
plot_board(st.session_state.positions["P1"], st.session_state.positions["P2"])
