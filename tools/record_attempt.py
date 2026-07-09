import json
from pathlib import Path

target_repo = Path("./target_repo")

def record_attempt(hypothesis: str, code_changed: str, result: str, why_it_failed: str) -> str:
    """
    Logs a failed debugging attempt to a central JSON ledger so the agent does not repeat mistakes.
    """
    ledger_path = target_repo / "debug_ledger.json"
    
    if ledger_path.exists():
        with open(ledger_path, "r", encoding="utf-8") as f:
            ledger = json.load(f)
    else:
        ledger = []
        
    attempt_entry = {
        "attempt_number": len(ledger) + 1,
        "hypothesis": hypothesis,
        "code_changed": code_changed,
        "result": result,
        "why_it_failed": why_it_failed
    }
    
    ledger.append(attempt_entry)
    
    with open(ledger_path, "w", encoding="utf-8") as f:
        json.dump(ledger, f, indent=4)
        
    return f"Attempt {attempt_entry['attempt_number']} logged successfully. Review this ledger before your next try."