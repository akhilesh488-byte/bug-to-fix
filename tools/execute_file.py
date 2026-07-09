import subprocess
from pathlib import Path
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor, CellExecutionError

target_repo = Path("./target_repo")

def execute_file(path: str, timeout: int = 60) -> str:
    """
    This tool executes an existing Python file (.py) or Jupyter Notebook (.ipynb)
    and returns the standard output, print statements, or error tracebacks.
    
    Args:
        path (str): The relative path of the file to execute inside target_repo.
        timeout (int): Maximum execution time in seconds before a timeout occurs.
        
    Returns:
        str: Raw text output or detailed execution logs/errors.
    """
    full_path = target_repo / path
    
    if not full_path.exists():
        return f"Error: File not found at {path}"

    # --- Handling Standard Python Files ---
    if str(full_path).endswith(".py"):
        try:
            result = subprocess.run(
                ["python", str(full_path)],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            # Combine standard output and standard error for the LLM to analyze
            output = []
            if result.stdout:
                output.append(f"--- Standard Output ---\n{result.stdout}")
            if result.stderr:
                output.append(f"--- Standard Error / Exceptions ---\n{result.stderr}")
                
            return "\n\n".join(output) if output else "Execution successful with no output."
            
        except subprocess.TimeoutExpired as e:
            # Captures partial output up until the timeout occurred
            stdout = e.stdout.decode('utf-8', errors='ignore') if e.stdout else ""
            stderr = e.stderr.decode('utf-8', errors='ignore') if e.stderr else ""
            return (
                f"[TIMEOUT GUARDRAIL ENFORCED] File execution exceeded the maximum limit of {timeout} seconds.\n"
                f"Partial stdout captured:\n{stdout}\n"
                f"Partial stderr captured:\n{stderr}"
            )

    # --- Handling Jupyter Notebooks ---
    elif str(full_path).endswith(".ipynb"):
        try:
            # Load the notebook structure
            with open(full_path, "r", encoding="utf-8") as f:
                nb = nbformat.read(f, as_version=4)
            
            # Configure the programmatic execution engine
            ep = ExecutePreprocessor(timeout=timeout, kernel_name='python3')
            
            # Execute all cells sequentially within the workspace directory
            ep.preprocess(nb, {'metadata': {'path': str(target_repo)}})
            
            # Extract and format the results from the executed notebook structure
            output_report = []
            for i, cell in enumerate(nb.cells, start=1):
                if cell.cell_type == "code":
                    output_report.append(f"--- Output Cell {i} ---")
                    cell_outputs = []
                    for out in cell.get('outputs', []):
                        if out.output_type == 'stream':
                            cell_outputs.append(out.text)
                        elif out.output_type in ('execute_result', 'display_data'):
                            if 'text/plain' in out.data:
                                cell_outputs.append(out.data['text/plain'])
                    
                    if cell_outputs:
                        output_report.append("".join(cell_outputs))
                    else:
                        output_report.append("[No Output]")
                        
            return "\n\n".join(output_report)

        except CellExecutionError as e:
            # If any cell throws a runtime error, catch it and hand the traceback to the LLM
            return f"Runtime Error during notebook execution:\n{str(e)}"
            
        except TimeoutError:
            return (
                f"[TIMEOUT GUARDRAIL ENFORCED] Notebook execution was cut short because a cell "
                f"took longer than the allocated {timeout} seconds. This typically indicates an "
                f"unoptimized or heavy machine learning training block."
            )
            
    else:
        return f"Error: Unsupported file type for execution '{path}'."