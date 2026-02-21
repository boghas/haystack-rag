import pathlib


def read_txt_file(file_path: str) -> str:
    """Read the content of a text file.
    
    Args:
        file_path (str): The path to the text file.
    
    Returns:
        str: The content of the text file.
    """
    
    content = ""
    file = pathlib.Path(file_path)
    with file.open("r", encoding="utf-8") as f:
        content = f.read()
    return content