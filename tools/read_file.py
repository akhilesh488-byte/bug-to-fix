from pathlib import Path
import json

target_repo = Path("./target_repo")

def read_file(path : str) -> str:
    """this tool reads the content in the file 

    Args:
        path (str): name of the file you want to read 

    Returns:
        str: contents of the file as string
    """
    
    full_path = target_repo / path
    
    if str(full_path).endswith(".ipynb"):
        with open(full_path, "r", encoding = "utf-8") as f: #encoding ensures smooth operation between different os
            notebook = json.load(f)
            content = []
            
            for i, cell in enumerate(notebook["cells"], start = 1):
                if cell["cell_type"] == "code":
                    content.append(f"------ code cell {i} ------")
                    content.append("".join(cell["source"]))
                elif cell["cell_type"] == "markdown":
                    content.append(f"------ markdown cell {i} ------")
                    content.append("".join(cell["source"]))
            result = "\n\n".join(content)
            
        return result
        
    else:
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
        