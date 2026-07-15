from pathlib import Path
import json
import re

target_repo = Path("./target_repo")

def write_file(path: str, text: str) -> str:
    """this tool writes content into the file

    Args:
        path (str): name of the file in which you want to write the content
        text (str): content that you want to write
    """
    
    full_path = target_repo / path
    
    if str(full_path).endswith(".py"):
        # Strip out the tags in case the LLM still leaks them, and remove extra newlines
        clean_text = text.replace("<execute_python>", "").replace("</execute_python>", "").strip()
        
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(clean_text)
            
    elif str(full_path).endswith(".ipynb"):
        # Read the current notebook state
        with open(full_path, "r", encoding="utf-8") as f:
            notebook = json.load(f)
            
        # Parse the custom formatting provided by the LLM
        pattern = r"------ (Code|Markdown) Cell (\d+) ------\n(.*?)(?=\n------ |\Z)"
        matches = re.findall(pattern, text, flags=re.DOTALL)
        
        # Update the notebook cells
        for cell_type, cell_num, source in matches:
            idx = int(cell_num) - 1
            notebook["cells"][idx]["source"] = source.splitlines(keepends=True)
            
        # Write the updated notebook back to disk
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(notebook, f, indent=2)

    # Return an observation string for the LLM to read in the next step
    return f"Successfully updated the file: {path}"

# if I want to test the function            
# print(write_file("test.ipynb","""------ Code Cell 1 ------
# import torch
# import numpy as np
#
# ------ Markdown Cell 2 ------
# # Training
# """ ))