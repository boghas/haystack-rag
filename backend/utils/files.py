
import os
import pathlib
import tempfile
from typing import List, Dict
from fastapi import UploadFile


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


async def save_uploaded_files(files: List[UploadFile], local_dir: str) -> List[pathlib.Path]:
    """Save files uploaded via request and stores them in local_dir.
    
    Args:
        files (List[UploadFile]): The files received via request to store them locally.
        local_dir (str): The local directory where to save the files.
    
    Returns:
        List[pathlib.Path]: The file paths of the files saved locally.
    """
    file_paths = []

    for file in files:
        file_path = os.path.join(local_dir, file.filename)
        file_data = await file.read()
        try:
            with open(file_path, "wb") as local_file:
                local_file.write(file_data)
            print(f"File: {file.filename} saved successfully!")
            
            file_paths.append(pathlib.Path(file_path))
        except Exception as ex:
            print(f"ERROR: Failed to save file: {file.filename}")
            print(ex)
            await file.close()
        finally:
            await file.close()
    
    return file_paths
        