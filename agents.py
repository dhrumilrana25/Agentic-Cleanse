import os
import subprocess
import sys
import pandas as pd
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load environment variables for API keys
load_dotenv()

# Initialize the AI Brain (Llama 3.3 Versatile)
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0 
)

# --- NODE 1: THE ANALYZER (Gives the Factory "Eyes") ---
def analyze_data_node(state):
    print("--- 🤖 AGENT 1: PROFILING & ANALYZING DATA ---")
    dataset_path = state.get("dataset_path", "")
    user_instructions = state.get("user_instructions", "")
    
    # The AI physically opens the file to see the structure
    try:
        df = pd.read_csv(dataset_path)
        data_profile = f"Columns detected: {df.columns.tolist()}\nSample Data:\n{df.head(2).to_markdown()}"
    except Exception as e:
        data_profile = f"Could not read the file. Error: {e}"

    # Inject your specific instructions into the prompt
    instruction_text = f"\nUSER'S MANDATORY REQUEST: '{user_instructions}'" if user_instructions else ""

    prompt = f"""You are a Lead Data Scientist. 
    DATA PROFILE:
    {data_profile}
    {instruction_text}

    TASK:
    1. Acknowledge the user's request: '{user_instructions}'.
    2. Write a 3-step strategy to clean this data.
    3. STEP 1 MUST focus on fulfilling the user's request.
    4. Do not write code yet. Just the bullet-point plan.
    """
    
    response = llm.invoke(prompt)
    return {"cleaning_plan": response.content}


# --- NODE 2: THE ENGINEER (The Coder) ---
import os
import subprocess
import sys
import pandas as pd
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()

# Initialize the AI Brain
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0 # Keep it at 0 for consistent, logical code generation
)

# --- NODE 1: THE ANALYZER ---
def analyze_data_node(state):
    print("--- 🤖 AGENT 1: PROFILING & ANALYZING DATA ---")
    dataset_path = state.get("dataset_path", "")
    user_instructions = state.get("user_instructions", "")
    
    # Peek at the data
    try:
        df = pd.read_csv(dataset_path)
        data_profile = f"Columns: {df.columns.tolist()}\nSample Data:\n{df.head(2).to_markdown()}"
    except Exception as e:
        data_profile = f"Error reading file: {e}"

    # Priority Instructions
    instruction_text = f"\nUSER'S MANDATORY REQUEST: '{user_instructions}'" if user_instructions else ""

    prompt = f"""You are a Lead Data Scientist. 
    DATA PROFILE:
    {data_profile}
    {instruction_text}

    TASK:
    1. Analyze the data structure and the user's request.
    2. Write a 3-step strategy to clean this data.
    3. STEP 1 MUST be the implementation of: '{user_instructions}'.
    4. Be highly specific. Do not write code yet.
    """
    
    response = llm.invoke(prompt)
    return {"cleaning_plan": response.content}


# --- NODE 2: THE ENGINEER (With Retry Awareness) ---
def write_code_node(state):
    print("--- 🤖 AGENT 2: WRITING CUSTOM PYTHON CODE ---")
    plan = state.get("cleaning_plan", "")
    dataset_path = state.get("dataset_path", "")
    user_instructions = state.get("user_instructions", "")
    errors = state.get("errors", [])
    retry_count = state.get("retry_count", 0)
    
    # Context for fixing mistakes
    error_context = ""
    if errors:
        print(f"-> ⚠️ Repairing code (Attempt {retry_count}/3). Error: {errors[-1].splitlines()[-1]}")
        error_context = f"""
        CRITICAL: Your previous attempt failed. 
        ERROR MESSAGE: {errors[-1]}
        You must fix this error. If the error was a 'FileNotFoundError', check your save path.
        If it was a 'TypeError', check your data types.
        """

    prompt = f"""You are a Senior Data Engineer.
    FILE TO CLEAN: '{dataset_path}'
    USER'S MANDATORY REQUEST: "{user_instructions}"
    CLEANING PLAN:
    {plan}
    {error_context}

    MANDATORY CODING RULES:
    1. Use 'import pandas as pd' and 'import numpy as np'.
    2. YOU MUST implement the user's request: "{user_instructions}".
    3. Load data directly from '{dataset_path}'.
    4. SAVE THE FINAL RESULT AS 'final_cleaned_data.csv' IN THE CURRENT DIRECTORY.
    5. ONLY OUTPUT THE RAW PYTHON CODE. NO MARKDOWN (no ```python). 
    6. If this is Attempt #{retry_count}, use a different logical approach to avoid repeating the same error.
    """
    
    response = llm.invoke(prompt)
    raw_code = response.content.replace("```python", "").replace("```", "").strip()
    return {"python_code": raw_code}


# --- NODE 3: THE EXECUTOR (With Verification & Counter) ---
def execute_code_node(state):
    print("--- 🤖 AGENT 3: EXECUTING & VERIFYING ---")
    code = state.get("python_code", "")
    target_file = "final_cleaned_data.csv"
    current_retries = state.get("retry_count", 0)
    
    # 1. Housekeeping: Remove old result if it exists
    if os.path.exists(target_file):
        os.remove(target_file)

    # 2. Save the code
    with open("workspace_cleaner.py", "w") as f:
        f.write(code)
        
    try:
        # 3. Execute
        result = subprocess.run(
            [sys.executable, "workspace_cleaner.py"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # 4. VERIFICATION: Did it actually work?
        if result.returncode == 0 and os.path.exists(target_file):
            print(f"-> ✅ Success! (Total Retries: {current_retries})")
            return {"is_cleaned": True, "errors": []}
        else:
            # Capture the failure details
            error_msg = result.stderr if result.returncode != 0 else "Execution finished but 'final_cleaned_data.csv' was not created."
            print(f"-> ❌ Execution Failed. Incrementing retry count.")
            
            # We return the incremented retry count to the state
            return {
                "is_cleaned": False, 
                "errors": [error_msg], 
                "retry_count": current_retries + 1
            }
            
    except Exception as e:
        print(f"-> ❌ System failure: {str(e)}")
        return {
            "is_cleaned": False, 
            "errors": [str(e)], 
            "retry_count": current_retries + 1
        }
    
def security_critic_node(state):
    print("--- 🛡️ AGENT 4: SECURITY REVIEW ---")
    code = state.get("python_code", "")
    
    # We ask the LLM to look for malicious patterns
    prompt = f"""You are a Cyber Security Expert. 
    Review this AI-generated Python code for dangerous operations:
    
    CODE:
    {code}
    
    CHECK FOR:
    1. System commands (os.system, subprocess.Popen with shell=True).
    2. File deletions (os.remove, shutil.rmtree) UNLESS it is deleting 'workspace_cleaner.py'.
    3. Network requests to unknown URLs.
    
    If the code is safe, reply with 'SAFE'.
    If it is dangerous, reply with 'DANGER: [reason]'.
    """
    
    response = llm.invoke(prompt)
    
    if "DANGER" in response.content.upper():
        # If it's dangerous, we treat it as an error and send it back to the engineer
        return {"is_cleaned": False, "errors": [f"SECURITY VETO: {response.content}"]}
    
    return {"errors": []} # No news is good news