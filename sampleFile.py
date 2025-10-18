import cv2
import numpy as np
import requests
import base64
from PIL import Image
import io
import re
import math
import pydobot as dobot
import XNO as x
import time
class OpenRouterTicTacToeDetector:
    def __init__(self, api_key):
        # Initialize webcam
        self.cap = cv2.VideoCapture(1)
        if not self.cap.isOpened():
            print("Error: Could not open camera")
            exit()
        
        # OpenRouter API configuration
        self.api_key = api_key
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        
        # Player and AI symbols (will be set by user choice)
        self.player_symbol = None
        self.ai_symbol = None
        
        print("OpenRouter Tic-Tac-Toe Detector with AI Strategy")
        print("Press 'c' to capture and analyze with Gemini")
        print("Press 'q' to quit")
    
    def get_player_choice(self, symbol):
        """Prompt user to choose X or O and set AI accordingly"""
        if symbol=='X':
            self.player_symbol = 'X'
            self.ai_symbol = 'O'
            print("You are playing as X. AI will play as O.")
        if symbol=='O':
            self.player_symbol = 'O'
            self.ai_symbol = 'X'
            print("You are playing as O. AI will play as X.")
        """while True:
            choice = input("\nChoose your symbol (X or O): ").strip().upper()
            if choice in ['X', 'O']:
                if choice == 'X':
                    self.player_symbol = 'X'
                    self.ai_symbol = 'O'
                    print("You are playing as X. AI will play as O.")
                else:
                    self.player_symbol = 'O' 
                    self.ai_symbol = 'X'
                    print("You are playing as O. AI will play as X.")
                return
            else:
                print("Invalid choice. Please enter 'X' or 'O'.")"""
    
    def capture_frame(self):
        """Capture current frame from webcam"""
        ret, frame = self.cap.read()
        if ret:
            return cv2.flip(frame, 1)  # Mirror effect
        return None
    
    def image_to_base64(self, image):
        """Convert OpenCV image to base64 string"""
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_image)
        
        # Convert to base64
        buffered = io.BytesIO()
        pil_image.save(buffered, format="JPEG", quality=95)
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return img_str
    
    def extract_coordinates_from_text(self, text):
        """Extract X and O coordinates from Qwen's text response"""
        x_positions = []
        o_positions = []
        
        # Convert to uppercase for consistent parsing
        text = text.upper()
        
        # Pattern for coordinates in format (row,col)
        coord_pattern = r'\((\d),\s*(\d)\)'
        
        # Find all coordinate pairs
        all_coords = re.findall(coord_pattern, text)
        
        # Look for X and O mentions near coordinates
        lines = text.split('\n')
        current_symbol = None
        
        for line in lines:
            line_upper = line.upper()
            
            # Check if line mentions X or O
            if 'X:' in line_upper or 'X AT' in line_upper or 'X POSITIONS' in line_upper:
                current_symbol = 'X'
            elif 'O:' in line_upper or 'O AT' in line_upper or 'O POSITIONS' in line_upper:
                current_symbol = 'O'
            elif 'X' in line_upper and 'O' not in line_upper:
                current_symbol = 'X'
            elif 'O' in line_upper and 'X' not in line_upper:
                current_symbol = 'O'
            
            # Extract coordinates from this line
            line_coords = re.findall(coord_pattern, line)
            for row, col in line_coords:
                coord = (int(row), int(col))
                if current_symbol == 'X' and coord not in x_positions:
                    x_positions.append(coord)
                elif current_symbol == 'O' and coord not in o_positions:
                    o_positions.append(coord)
        
        # If we didn't find organized lists, check the entire text
        if not x_positions and not o_positions:
            # Try to find all X and O coordinates by context
            words = text.split()
            for i, word in enumerate(words):
                if word == 'X' or word == 'O':
                    # Check next few words for coordinates
                    for j in range(1, min(4, len(words) - i)):
                        next_word = words[i + j]
                        coords = re.findall(coord_pattern, next_word)
                        if coords:
                            row, col = coords[0]
                            coord = (int(row), int(col))
                            if word == 'X' and coord not in x_positions:
                                x_positions.append(coord)
                            elif word == 'O' and coord not in o_positions:
                                o_positions.append(coord)
        
        return x_positions, o_positions
    
    def create_board_from_positions(self, x_positions, o_positions):
        """Create a 3x3 board from X and O positions"""
        board = [[' ' for _ in range(3)] for _ in range(3)]
        
        for row, col in x_positions:
            if 0 <= row < 3 and 0 <= col < 3:
                board[row][col] = 'X'
        
        for row, col in o_positions:
            if 0 <= row < 3 and 0 <= col < 3:
                board[row][col] = 'O'
                
        return board


    def minimax(self, board, depth, is_maximizing):
        """Minimax (AI maximizes)"""
        # Terminal check
        winner = self.check_winner(board)
        if winner == self.ai_symbol:
            return 10 - depth
        elif winner == self.player_symbol:
            return depth - 10
        elif self.is_board_full(board):
            return 0

        if is_maximizing:
            # AI's turn: try all AI moves and maximize
            best_score = -float('inf')
            for r in range(3):
                for c in range(3):
                    if board[r][c] == ' ':
                        board[r][c] = self.ai_symbol
                        score = self.minimax(board, depth + 1, False)  # next: player's turn
                        board[r][c] = ' '
                        best_score = max(best_score, score)
            return best_score
        else:
            # Player's turn: try all player moves and minimize
            best_score = float('inf')
            for r in range(3):
                for c in range(3):
                    if board[r][c] == ' ':
                        board[r][c] = self.player_symbol
                        score = self.minimax(board, depth + 1, True)  # next: AI's turn
                        board[r][c] = ' '
                        best_score = min(best_score, score)
            return best_score

    def find_best_move(self, board):
        """Find best AI move; AI ALWAYS maximizes, regardless of X or O"""
        # Optional opening book: take center if AI is X and board empty
        if self.is_board_empty(board) and self.ai_symbol == 'X':
            return (1, 1)

        best_score = -float('inf')
        best_move = None

        for r in range(3):
            for c in range(3):
                if board[r][c] == ' ':
                    # Try AI move
                    board[r][c] = self.ai_symbol

                    # After AI moves, it's the player's turn -> is_maximizing=False
                    score = self.minimax(board, depth=0, is_maximizing=False)

                    # Undo
                    board[r][c] = ' '

                    if score > best_score:
                        best_score = score
                        best_move = (r, c)

        return best_move

    
    """def minimax(self, board, depth, is_maximizing):"""
        #Minimax algorithm with alpha-beta pruning"""
        # Check for terminal states
    """ winner = self.check_winner(board)
        if winner == self.ai_symbol:
            return 10 - depth
        elif winner == self.player_symbol:
            return depth - 10
        elif self.is_board_full(board):
            return 0
        
        if is_maximizing:
            # AI's turn (maximizing player)
            best_score = -float('inf')
            for row in range(3):
                for col in range(3):
                    if board[row][col] == ' ':
                        board[row][col] = self.ai_symbol
                        score = self.minimax(board, depth + 1, False)
                        board[row][col] = ' '
                        best_score = max(score, best_score)
            return best_score
        else:
            # Player's turn (minimizing player)
            best_score = float('inf')
            for row in range(3):
                for col in range(3):
                    if board[row][col] == ' ':
                        board[row][col] = self.player_symbol
                        score = self.minimax(board, depth + 1, True)
                        board[row][col] = ' '
                        best_score = min(score, best_score)
            return best_score
    
    def find_best_move(self, board):"""
        #Find the best move for the AI using minimax"""
        # If AI is X, use maximizing logic; if AI is O, use minimizing logic
    """ is_maximizing = (self.ai_symbol == 'X')
        
        best_score = -float('inf') if is_maximizing else float('inf')
        best_move = None
        
        # If board is empty and AI is X, start with center
        if self.is_board_empty(board) and self.ai_symbol == 'X':
            return (1, 1)
        
        for row in range(3):
            for col in range(3):
                if board[row][col] == ' ':
                    # Try the move
                    board[row][col] = self.ai_symbol
                    
                    # Calculate score based on whether AI is X or O
                    if self.ai_symbol == 'X':
                        score = self.minimax(board, 0, False)  # O's turn next
                    else:
                        score = self.minimax(board, 0, True)   # X's turn next
                    
                    # Undo the move
                    board[row][col] = ' '
                    
                    # Update best move based on whether we're maximizing or minimizing
                    if (is_maximizing and score > best_score) or (not is_maximizing and score < best_score):
                        best_score = score
                        best_move = (row, col)
        
        return best_move"""
    
    def check_winner(self, board):
        """Check if there's a winner on the board"""
        # Check rows
        for row in range(3):
            if board[row][0] == board[row][1] == board[row][2] != ' ':
                return board[row][0]
        
        # Check columns
        for col in range(3):
            if board[0][col] == board[1][col] == board[2][col] != ' ':
                return board[0][col]
        
        # Check diagonals
        if board[0][0] == board[1][1] == board[2][2] != ' ':
            return board[0][0]
        if board[0][2] == board[1][1] == board[2][0] != ' ':
            return board[0][2]
        
        return None
    
    def is_board_full(self, board):
        """Check if the board is completely filled"""
        for row in range(3):
            for col in range(3):
                if board[row][col] == ' ':
                    return False
        return True
    
    def is_board_empty(self, board):
        """Check if the board is completely empty"""
        for row in range(3):
            for col in range(3):
                if board[row][col] != ' ':
                    return False
        return True
    
    def get_game_state(self, board):
        """Get the current game state description"""
        winner = self.check_winner(board)
        if winner:
            return f"{winner} wins!"
        elif self.is_board_full(board):
            return "Game is a draw!"
        else:
            return "Game in progress"
    
    def analyze_with_qwen(self, image_base64):
        """Send image to Qwen VL and get coordinate analysis"""
        try:
            prompt = """Look at this tic-tac-toe board image. 
            The board is a 3x3 grid. Find all X and O symbols and tell me their positions.
            
            Please respond in this exact format:
            X positions: (row,col), (row,col), ...
            O positions: (row,col), (row,col), ...
            
            Use 0-based indexing for rows and columns (0,1,2).
            Only include positions that actually have X or O.
            If a cell is empty, don't include it."""

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            payload = {
                "model": "google/gemini-2.5-flash-preview-09-2025",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 500
            }

            print("Sending to Qwen VL via OpenRouter...")
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                print(f"Qwen's full response:\n{content}")
                
                # Extract coordinates from the text response
                x_positions, o_positions = self.extract_coordinates_from_text(content)
                
                # Create board and find best move
                board = self.create_board_from_positions(x_positions, o_positions)
                best_move = self.find_best_move(board)
                game_state = self.get_game_state(board)
                
                return {
                    'x_positions': x_positions,
                    'o_positions': o_positions,
                    'board': board,
                    'best_move': best_move,
                    'game_state': game_state,
                    'raw_response': content
                }
            else:
                print(f"API request failed with status {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"Error analyzing with Qwen: {e}")
            return None
    
    def display_results(self, frame, analysis_result):
        """Display the analysis results on the frame"""
        if not analysis_result:
            cv2.putText(frame, "Analysis failed - check console", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            return frame
        
        # Display player and AI info
        y_offset = 30
        
        cv2.putText(frame, f"Player: {self.player_symbol}, AI: {self.ai_symbol}", (10, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        y_offset += 30
        
        cv2.putText(frame, "Qwen Analysis + AI Strategy:", (10, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        y_offset += 30
        
        # Display current board state
        cv2.putText(frame, "Current Board:", (10, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        y_offset += 25
        
        for row in analysis_result['board']:
            row_text = " | ".join([cell if cell != ' ' else ' ' for cell in row])
            cv2.putText(frame, row_text, (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            y_offset += 25
        
        # Display positions
        cv2.putText(frame, f"X positions: {analysis_result['x_positions']}", 
                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        y_offset += 25
        
        cv2.putText(frame, f"O positions: {analysis_result['o_positions']}", 
                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
        y_offset += 30
        
        # Display AI recommendation
        if analysis_result['best_move']:
            row, col = analysis_result['best_move']
            cv2.putText(frame, f"AI recommends {self.ai_symbol} at: ({row}, {col})", 
                       (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            y_offset += 30
        
        # Display game state
        cv2.putText(frame, f"Game State: {analysis_result['game_state']}", 
                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        return frame
    
    def save_captured_image(self, image, filename="captured_grid.jpg"):
        """Save the captured image for reference"""
        cv2.imwrite(filename, image)
        print(f"Image saved as {filename}")
    
    def run(self,device):
        """Main loop"""
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Error: Failed to capture frame")
                break
            
            frame = cv2.flip(frame, 1)
            
            # Display instructions
            cv2.putText(frame, "Press 'q' to quit", 
                       (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            cv2.imshow('Tic-Tac-Toe Qwen + AI Analyzer', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            #elif key == ord('c'):
            else:
                time.sleep(20)
                # Capture and analyze
                captured_frame = self.capture_frame()
                if captured_frame is not None:
                    print("\n" + "="*50)
                    print("CAPTURING IMAGE FOR QWEN + AI ANALYSIS...")
                    
                    # Show capturing message
                    display_frame = captured_frame.copy()
                    cv2.putText(display_frame, "CAPTURING...", 
                               (display_frame.shape[1]//2 - 100, display_frame.shape[0]//2), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3)
                    cv2.imshow('Tic-Tac-Toe Qwen + AI Analyzer', display_frame)
                    cv2.waitKey(1)
                    
                    # Save image for reference
                    self.save_captured_image(captured_frame)
                    
                    # Convert to base64 for API
                    image_base64 = self.image_to_base64(captured_frame)
                    
                    # Analyze with Qwen
                    print("Sending to Qwen VL...")
                    analysis_result = self.analyze_with_qwen(image_base64)
                    while len(analysis_result['x_positions']) == len(analysis_result['o_positions']): 
                        print("Play your move first")
                        time.sleep(10)
                        analysis_result = self.analyze_with_qwen(image_base64)
                        
                    if analysis_result:
                        print("\n✅ ANALYSIS SUCCESSFUL!")
                        print(f"X positions: {analysis_result['x_positions']}")
                        print(f"O positions: {analysis_result['o_positions']}")
                        print(f"Game State: {analysis_result['game_state']}")
                        
                        if(analysis_result['game_state']=="X wins!" or analysis_result['game_state']=="O wins!" or analysis_result['game_state']=="Game is a draw!"):
                            break
                        
                        if analysis_result['best_move']:
                            row, col = analysis_result['best_move']
                            print(f"🤖 AI recommends placing {self.ai_symbol} at position: ({row}, {col})")
                            if self.ai_symbol == 'X':
                                if row==0 and col == 0:
                                    x.draw_X(device, 275, 15)
                                if row==0 and col == 1:
                                    x.draw_X(device, 275, 45)
                                if row==0 and col == 2:
                                    x.draw_X(device, 275, 75)
                                if row==1 and col == 0:
                                    x.draw_X(device, 245, 15)
                                if row==1 and col == 1:
                                    x.draw_X(device, 245, 45)
                                if row==1 and col == 2:
                                    x.draw_X(device, 245, 75)
                                if row==2 and col == 0:
                                    x.draw_X(device, 215, 15)
                                if row==2 and col == 1:
                                    x.draw_X(device, 215, 45)
                                if row==2 and col == 2:
                                    x.draw_X(device, 215, 75)

                            if self.ai_symbol == 'O':
                                if row==0 and col == 0:
                                    x.draw_O(device, 275, 15)
                                if row==0 and col == 1:
                                    x.draw_O(device, 275, 45)
                                if row==0 and col == 2:
                                    x.draw_O(device, 275, 75)
                                if row==1 and col == 0:
                                    x.draw_O(device, 245, 15)
                                if row==1 and col == 1:
                                    x.draw_O(device, 245, 45)
                                if row==1 and col == 2:
                                    x.draw_O(device, 245, 75)
                                if row==2 and col == 0:
                                    x.draw_O(device, 215, 15)
                                if row==2 and col == 1:
                                    x.draw_O(device, 215, 45)
                                if row==2 and col == 2:
                                    x.draw_O(device, 215, 75)
                        
                        # Display results
                        result_frame = captured_frame.copy()
                        result_frame = self.display_results(result_frame, analysis_result)
                        cv2.imshow('Tic-Tac-Toe Qwen + AI Analyzer', result_frame)
                        time.sleep(2)
                        cv2.putText(frame, "Press 'q' to quit", (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                        cv2.imshow('Tic-Tac-Toe Qwen + AI Analyzer', frame)
                        """print("Press any key to continue live view...")
                        cv2.waitKey(0)"""
                    else:
                        print("❌ ANALYSIS FAILED!")
                        error_frame = captured_frame.copy()
                        cv2.putText(error_frame, "ANALYSIS FAILED - Check console", 
                                   (50, error_frame.shape[0]//2), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        cv2.imshow('Tic-Tac-Toe Qwen + AI Analyzer', error_frame)
                        cv2.waitKey(2000)  # Show error for 2 seconds
        
        self.cap.release()
        cv2.destroyAllWindows()


# Mock detector for testing without API
class MockDetector(OpenRouterTicTacToeDetector):
    def __init__(self):
        # Initialize without API key
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open camera")
            exit()
        
        # Player and AI symbols (will be set by user choice)
        self.player_symbol = None
        self.ai_symbol = None
        
        print("Mock Detector - No API calls")
    
    def get_player_choice(self):
        """Prompt user to choose X or O and set AI accordingly"""
        while True:
            choice = input("\nChoose your symbol (X or O): ").strip().upper()
            if choice in ['X', 'O']:
                if choice == 'X':
                    self.player_symbol = 'X'
                    self.ai_symbol = 'O'
                    print("You are playing as X. AI will play as O.")
                else:
                    self.player_symbol = 'O' 
                    self.ai_symbol = 'X'
                    print("You are playing as O. AI will play as X.")
                return
            else:
                print("Invalid choice. Please enter 'X' or 'O'.")
    
    def analyze_with_qwen(self, image_base64):
        """Mock analysis for testing"""
        print("Mock analysis - simulating Qwen VL response")
        
        import random
        # Return random coordinates for testing
        all_positions = [(r, c) for r in range(3) for c in range(3)]
        x_count = random.randint(1, 3)
        o_count = random.randint(1, 3)
        
        x_positions = random.sample(all_positions, x_count)
        remaining = [pos for pos in all_positions if pos not in x_positions]
        o_positions = random.sample(remaining, min(o_count, len(remaining)))
        
        # Create board and find best move
        board = self.create_board_from_positions(x_positions, o_positions)
        best_move = self.find_best_move(board)
        game_state = self.get_game_state(board)
        
        mock_response = f"""
        X positions: {', '.join(f'({r},{c})' for r,c in x_positions)}
        O positions: {', '.join(f'({r},{c})' for r,c in o_positions)}
        """
        
        print(f"Mock response:\n{mock_response}")
        
        return {
            'x_positions': x_positions,
            'o_positions': o_positions,
            'board': board,
            'best_move': best_move,
            'game_state': game_state,
            'raw_response': mock_response
        }


def main(device, symbol):
    print("Tic-Tac-Toe AI Strategy Detector")

    api_key = "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"
    detector = OpenRouterTicTacToeDetector(api_key)
    
    # Add this line to prompt for player choice
    detector.get_player_choice(symbol)
    
    # Run the detector
    detector.run(device)

#if __name__ == "__main__":
   # main()
    
