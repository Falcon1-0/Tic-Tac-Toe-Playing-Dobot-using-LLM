import cv2
import base64
import requests
import time
import os
import json

def detect_player_symbol():
    # --- Setup ---
    api_key = "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"  # set this env var or replace line below
    # api_key = "sk-or-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # <-- for quick test only

    if not api_key:
        raise RuntimeError("Missing OPENROUTER_API_KEY environment variable.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # --- Open camera ---
    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        raise RuntimeError("Cannot open camera")

    print("Camera preview started. Press 'q' when ready to capture the frame.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break

        # Show live feed
        cv2.imshow("Camera Preview", frame)

        # Press 'q' to capture

        if cv2.waitKey(1):
            time.sleep(5)
            print("Frame captured!")
            break

    # Close the preview window
    cap.release()
    cv2.destroyAllWindows()

    if frame is None:
        raise RuntimeError("No frame captured.")

    # --- Encode frame to base64 ---
    _, buffer = cv2.imencode(".png", frame)
    image_b64 = base64.b64encode(buffer).decode("utf-8")

    # --- Prepare LLM request ---
    prompt = (
        "You are analyzing a photo of a tic-tac-toe board. "
        "Tell me whether the human user has played X or O. "
        "Respond with only one word: 'X', 'O', or 'unknown'."
    )

    payload = {
        "model": "google/gemini-2.5-flash-preview-09-2025",
        "messages": [
            {"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": f"data:image/png;base64,{image_b64}"}
            ]}
        ],
        "max_tokens": 10
    }

    # --- Send to Gemini via OpenRouter ---
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", 
                             headers=headers, json=payload)

    if response.status_code != 200:
        raise RuntimeError(f"Request failed: {response.status_code} {response.text}")

    # --- Parse response safely ---
    data = response.json()
    choice = data.get("choices", [{}])[0]
    msg = choice.get("message", {})
    content = msg.get("content", "")

    def to_text(content):
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for p in content:
                if isinstance(p, dict):
                    if "text" in p:
                        parts.append(p["text"])
                    elif "content" in p:
                        parts.append(p["content"])
            return " ".join(parts)
        return str(content)

    result_text = to_text(content).strip().upper()

    # --- Interpret result ---
    if "X" in result_text:
        user_symbol = "X"
    elif "O" in result_text:
        user_symbol = "O"
    else:
        user_symbol = "UNKNOWN"

    print(f"\n🧩 User played: {user_symbol}")
    return user_symbol


# --- Example usage ---
if __name__ == "__main__":
    symbol = detect_player_symbol()
    print("\nDetected player symbol variable:", symbol)
