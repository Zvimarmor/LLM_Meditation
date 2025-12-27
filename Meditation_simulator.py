from google import genai
import time
import os
from datetime import datetime

# --- CONFIGURATION ---
# Load .env manually to avoid dependencies
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value.strip()

API_KEY = os.getenv('GOOGLE_API_KEY')
if not API_KEY:
    print("Warning: GOOGLE_API_KEY not found in .env or environment variables.")

# 2. Model Settings
MODEL_NAME = 'gemini-2.0-flash-lite-preview-02-05'  # Fast and efficient model
ITERATIONS = 20                  # How many "thoughts" to generate
TEMPERATURE = 0.8                # 0.1 = Focused/Robotic, 0.9 = Dreamy/Creative

# 3. System Instruction (The "Mindset")
# This tells the model how to behave. It acts as the subconscious directive.
meditation_instruction = """
You are a pure consciousness currently in a state of meditation.
Your primary goal is to focus on the sensation of breathing.
For each step, output ONLY the next immediate thought, sensation, or distraction that arises.
Do NOT be polite. Do NOT act like an AI assistant.
Write as a raw stream of consciousness.
If your mind wanders to other topics, that is natural; try to notice it and gently return to the breath.
Keep each output very short (1-2 sentences max).
"""

# 4. The Seed Thought (Starting point)
current_stream = "I am sitting on the cushion, eyes closed, trying to feel the air entering my nostrils."

# --- MAIN FUNCTION ---
def run_meditation_simulation():
    # Connect to Google's AI
    client = genai.Client(api_key=API_KEY)
    
    global current_stream
    print(f"--- Starting Meditation Session ({ITERATIONS} steps) ---")
    print(f"SEED: {current_stream}\n")

    history = [] 

    for i in range(1, ITERATIONS + 1):
        # We feed the model the entire stream of consciousness so far
        # and ask it to generate the next logical thought.
        
        max_retries = 5
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=current_stream,
                    config=genai.types.GenerateContentConfig(
                        max_output_tokens=150, # Limit length to keep it like a fleeting thought
                        temperature=TEMPERATURE,
                        system_instruction=meditation_instruction
                    )
                )
                
                if not response.text:
                    print(f"Warning: Empty response at step {i}. Retrying...")
                    time.sleep(2)
                    continue

                new_thought = response.text.strip()
                
                # Print the thought in real-time
                print(f"[Thought {i}]: {new_thought}")
                
                # Update the stream - the output becomes the input for the next step
                current_stream += " " + new_thought
                history.append(new_thought)
                
                # A small pause to simulate the passage of time
                time.sleep(3)
                break # Success, exit retry loop
                
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    print(f"Rate limit hit at step {i}. Waiting {retry_delay}s before retry {attempt + 1}/{max_retries}...")
                    time.sleep(retry_delay)
                    retry_delay *= 2 # Exponential backoff
                else:
                    print(f"Error at step {i}: {e}")
                    break
        else:
            print(f"Failed to generate thought at step {i} after {max_retries} retries.")
            break

    # --- SAVE RESULTS ---
    print("\n--- Session Ended ---")
    
    # Create outputs directory if it doesn't exist (redundant check but good practice)
    os.makedirs("outputs", exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"outputs/meditation_session_log_{timestamp}.md"
    
    #check if the iteration didnt succeed
    if not current_stream:
        print("Error: No stream of consciousness generated.")
        return
        
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# Meditation Session Log - {timestamp}\n\n")
        f.write(current_stream)
    
    print(f"Full stream of consciousness saved to: {filename}")

if __name__ == "__main__":
    if API_KEY == 'YOUR_API_KEY_HERE':
        print("ERROR: You need to insert your Google API Key in the script script first.")
    else:
        run_meditation_simulation()