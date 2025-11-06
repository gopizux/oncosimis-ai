import os
import logging
from pathlib import Path
from typing import Tuple, List

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    logging.warning("python-docx not installed. .docx files will be skipped.")

logger = logging.getLogger(__name__)

def load_documents(directory: str) -> Tuple[str, List[str]]:
    """
    Load all documents from the specified directory.
    Returns: (combined_content, list_of_filenames)
    """
    directory_path = Path(directory)
    
    if not directory_path.exists():
        logger.warning(f"Directory not found: {directory}")
        return "", []
    
    combined_content = ""
    filenames = []
    
    # Load all .docx and .txt files
    for file_path in directory_path.iterdir():
        if file_path.is_file():
            try:
                if file_path.suffix.lower() == '.docx' and DOCX_AVAILABLE:
                    content = load_docx(file_path)
                    if content:
                        combined_content += f"\n\n=== {file_path.name} ===\n{content}"
                        filenames.append(file_path.name)
                        logger.info(f"Loaded: {file_path.name}")
                
                elif file_path.suffix.lower() == '.txt':
                    content = load_txt(file_path)
                    if content:
                        combined_content += f"\n\n=== {file_path.name} ===\n{content}"
                        filenames.append(file_path.name)
                        logger.info(f"Loaded: {file_path.name}")
                        
            except Exception as e:
                logger.error(f"Error loading {file_path.name}: {e}")
    
    return combined_content, filenames

def load_docx(file_path: Path) -> str:
    """Load content from a .docx file."""
    try:
        doc = Document(file_path)
        content = "\n".join([paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()])
        return content
    except Exception as e:
        logger.error(f"Error reading .docx file {file_path}: {e}")
        return ""

def load_txt(file_path: Path) -> str:
    """Load content from a .txt file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading .txt file {file_path}: {e}")
        return ""

