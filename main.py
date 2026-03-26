from graph import app

print("🚀 Starting the Agentic-Cleanse Factory...\n")

initial_state = {
    "dataset_path": "data/messy_sales_data_2026.csv", 
    "cleaning_plan": "",
    "python_code": "",
    "errors": [],
    "is_cleaned": False
}

# 1. We need a "Thread ID" so the memory knows which run this is
thread_config = {"configurable": {"thread_id": "1"}}

# 2. Run the machine. It will hit the 'interrupt_before' and PAUSE.
for event in app.stream(initial_state, config=thread_config):
    pass

# 3. Get the current state from memory to show the user
current_state = app.get_state(thread_config)
generated_code = current_state.values.get("python_code", "")

print("\n🛑 PAUSED FOR HUMAN REVIEW 🛑")
print("Agent 2 wrote this code. Do you approve it for execution?")
print("-------------------------------------------------")
print(generated_code)
print("-------------------------------------------------\n")

# 4. Ask you for permission!
user_input = input("Type 'y' to execute, or 'n' to cancel: ")

if user_input.lower() == 'y':
    print("\n✅ Human Approved! Resuming factory line...")
    # Resume the graph with no new data (None) using the exact same thread
    for event in app.stream(None, config=thread_config):
        pass
    print("\n🎉 FACTORY RUN COMPLETE.")
else:
    print("\n❌ Execution Cancelled by Human.")