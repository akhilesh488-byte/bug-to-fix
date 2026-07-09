from pathlib import Path
import json
import re

target_repo = Path("./target_repo")

def write_file(path : str, text : str) -> str:
    """this tool writes content into the file

    Args:
        path (str): name of the file in which you want to write the content
        text (str): content that you want to write
    """
    
    full_path = target_repo / path
    
    if str(full_path).endswith(".py"):
        with open(full_path, "w", encoding="utf-8") as f: #if the file is just python then i want LLM to output only code and nothing else
            f.write(text)
            
    elif str(full_path).endswith(".ipynb"):
        #for now i am going to read the whole file again for state management, later on for v2 i will create notebook class
        with open(full_path, "r", encoding = "utf-8") as f:
            notebook = json.load(f)
        
            
        with open(full_path, "w", encoding="utf-8") as f:
            pattern = r"------ (Code|Markdown) Cell (\d+) ------\n(.*?)(?=\n------ |\Z)"
            matches = re.findall(pattern, text, flags=re.DOTALL)
            
            # print(notebook["cells"][0]["source"])
            for cell_type, cell_num, source in matches:
                idx = int(cell_num) - 1
                notebook["cells"][idx]["source"] = source.splitlines(keepends=True)
            # print(notebook["cells"][0]["source"])
            json.dump(notebook, f, indent=2)

#if i want to test the function            
# write_file("test.ipynb","""------ Code Cell 1 ------
# import torch
# import numpy as np

# ------ Markdown Cell 2 ------
# # Training
# """ )
 
    