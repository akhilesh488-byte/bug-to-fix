from pathlib import Path

target_repo = Path("./target_repo")
def scan_repo():
    """this tool scans for the files present in target_repo

    Returns:
        list: this contains all the file names relative to the target_repo
    """
    files = []
    for path in target_repo.rglob("*"):
        files.append(str(path.relative_to(target_repo).as_posix()))
    return files
