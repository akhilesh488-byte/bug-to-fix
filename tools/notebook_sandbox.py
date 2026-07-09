import queue
from jupyter_client import KernelManager

class NotebookSandbox:
    def __init__(self):
        """Spins up an isolated background kernel and initializes an empty virtual notebook."""
        print("[SANDBOX] Initializing persistent Python kernel...")
        self.km = KernelManager(kernel_name='python3')
        self.km.start_kernel()
        self.kc = self.km.client()
        self.kc.start_channels()
        self.kc.wait_for_ready(timeout=10)
        
        # In-memory virtual cells: list of dicts [{"cell_id": 1, "source": "...", "output": "..."}]
        self.cells = []
        print("[SANDBOX] Isolated playground environment ready.")

    def add_cell(self, code: str) -> str:
        """Allows the LLM to append a new code block to the scratchpad."""
        cell_id = len(self.cells) + 1
        self.cells.append({
            "cell_id": cell_id,
            "source": code,
            "output": "Not executed yet."
        })
        return f"Successfully added Code Cell {cell_id}."

    def edit_cell(self, cell_id: int, new_code: str) -> str:
        """Allows the LLM to rewrite the contents of an existing sandbox cell."""
        idx = cell_id - 1
        if 0 <= idx < len(self.cells):
            self.cells[idx]["source"] = new_code
            self.cells[idx]["output"] = "Modified (Requires re-execution)."
            return f"Successfully modified Code Cell {cell_id}."
        return f"Error: Cell {cell_id} does not exist in the sandbox."

    def execute_cell(self, cell_id: int, timeout: int = 30) -> str:
        """
        Executes a specific cell within the persistent environment state.
        Variables defined in previous executions remain live in memory.
        """
        idx = cell_id - 1
        if not (0 <= idx < len(self.cells)):
            return f"Error: Cell {cell_id} out of bounds."

        code_to_run = self.cells[idx]["source"]
        msg_id = self.kc.execute(code_to_run)
        
        output = []
        error = None
        
        try:
            # Wait for execution acknowledgement
            self.kc.get_shell_msg(timeout=timeout)
            
            while True:
                try:
                    iopub_msg = self.kc.get_iopub_msg(timeout=0.5)
                    if iopub_msg['parent_header'].get('msg_id') != msg_id:
                        continue
                        
                    msg_type = iopub_msg['header']['msg_type']
                    content = iopub_msg['content']
                    
                    if msg_type == 'stream':
                        output.append(content['text'])
                    elif msg_type in ('execute_result', 'display_data'):
                        if 'data' in content and 'text/plain' in content['data']:
                            output.append(content['data']['text/plain'] + '\n')
                    elif msg_type == 'error':
                        error = "\n".join(content['traceback'])
                    elif msg_type == 'status' and content['execution_state'] == 'idle':
                        break
                except queue.Empty:
                    break
                    
        except queue.Empty:
            self.km.interrupt_kernel()
            result_str = f"[TIMEOUT] Cell execution forced to stop after {timeout} seconds."
            self.cells[idx]["output"] = result_str
            return result_str

        if error:
            final_output = f"Runtime Error:\n{error}"
        else:
            final_output = "".join(output) if output else "Execution successful (No stdout)."

        # Save result to the cell's state history
        self.cells[idx]["output"] = final_output
        return final_output

    def get_sandbox_state(self) -> str:
        """Returns a compiled text view of the current sandbox cells and their last outputs."""
        if not self.cells:
            return "Sandbox is empty."
            
        report = []
        for cell in self.cells:
            report.append(f"=== Code Cell {cell['cell_id']} ===")
            report.append(cell['source'])
            report.append("--- Last Output ---")
            report.append(cell['output'])
            report.append("\n" + "="*30 + "\n")
        return "\n".join(report)

    def shutdown(self):
        """Terminates the background execution process cleanly."""
        self.kc.stop_channels()
        self.km.shutdown_kernel()