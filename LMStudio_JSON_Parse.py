import json
import tkinter as tk
from tkinter import filedialog, messagebox

def parse_chat_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    title = data.get('name', 'Untitled Chat')
    
    # Extract system prompt from perChatPredictionConfig
    system_prompt = "No system prompt"
    prediction_config = data.get('perChatPredictionConfig', {}).get('fields', [])
    for field in prediction_config:
        if field.get('key') == 'llm.prediction.systemPrompt':
            system_prompt = field.get('value', "No system prompt")
            break

    # Extract LLM model information
    llm_model = "Unknown Model"
    messages = []
    for msg in data.get('messages', []):
        version = msg.get('versions', [{}])[msg.get('currentlySelected', 0)]
        role = version.get('role', 'unknown')
        
        if role == 'user':
            content = version.get('content', [{}])[0].get('text', '')
        elif role == 'assistant':
            steps = version.get('steps', [])
            content_block = next((step for step in steps if step['type'] == 'contentBlock'), None)
            if content_block:
                content = content_block['content'][0]['text']
                # Extract LLM model info from the first assistant message
                if not llm_model or llm_model == "Unknown Model":
                    gen_info = content_block.get('genInfo', {})
                    llm_model = gen_info.get('identifier', "Unknown Model")
        else:
            content = ''

        if content:
            messages.append(f"{role.capitalize()}: {content}\n")  # Add newline after each message

    formatted_output = f"Title: {title}\nLLM Model: {llm_model}\nSystem Prompt: {system_prompt}\n\n" + "\n".join(messages)
    return formatted_output

def browse_input():
    input_file = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    entry_input.delete(0, tk.END)
    entry_input.insert(tk.END, input_file)

def browse_output():
    output_file = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    entry_output.delete(0, tk.END)
    entry_output.insert(tk.END, output_file)

def parse():
    input_file = entry_input.get()
    output_file = entry_output.get()
    if not input_file or not output_file:
        messagebox.showerror("Error", "Please select both input and output files.")
        return
    try:
        formatted_data = parse_chat_json(input_file)
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(formatted_data)
        messagebox.showinfo("Success", "Parsing completed successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Create the GUI window
root = tk.Tk()
root.title("Chat JSON Parser")

# Input field for selecting the input JSON file
label_input = tk.Label(root, text="Input JSON File:")
entry_input = tk.Entry(root, width=50)
button_browse_input = tk.Button(root, text="Browse", command=browse_input)

# Output field for selecting the output text file
label_output = tk.Label(root, text="Output Text File:")
entry_output = tk.Entry(root, width=50)
button_browse_output = tk.Button(root, text="Browse", command=browse_output)

# Parse button
button_parse = tk.Button(root, text="Parse", command=parse)

# Add widgets to the window
label_input.pack()
entry_input.pack()
button_browse_input.pack()
label_output.pack()
entry_output.pack()
button_browse_output.pack()
button_parse.pack()

# Run the main loop
root.mainloop()