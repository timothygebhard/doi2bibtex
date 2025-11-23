
import lazy_loader as lazy
from typing import List, Dict, Optional, Any

# Tous les imports sont lazy
_bs4 = lazy.load('bs4')
_re = lazy.load('re')
_rapidocr = lazy.load('rapidocr_onnxruntime')
_np = lazy.load('numpy')
_pyperclip = lazy.load('pyperclip')

def normalize_text(text):
    # remove control char
    text = _re.sub(r'[\x00-\x1f\x7f]', ' ', text)
    # remove extra space line break, tabulation, ect
    text = _re.sub(r'\s+', ' ', text)

    return text

def parse_jats_text(text: str) -> str:
    """
    Parse JATS  (Journal Article Tag Suite) XML text (without adding external library) and convert to clean text.
    """
    if not text:
        return text

    # Check if it contains JATS XML tags
    if '<jats:' not in text and '<' not in text:
        return text

    try:
        # Parse with BeautifulSoup (use html.parser for better namespace handling)
        soup = _bs4.BeautifulSoup(text, 'html.parser')

        # Remove <jats:title> tags (usually "Abstract")
        for title in soup.find_all(['jats:title', 'title']):
            title.decompose()

        # Get text from all paragraph tags
        paragraphs = soup.find_all(['jats:p', 'p'])
        if paragraphs:
            # Extract text from each paragraph and join with double newline
            text_parts = []
            for p in paragraphs:
                text = p.get_text(separator=' ', strip=True)
                if text:
                    text_parts.append(text)
            text = '\n\n'.join(text_parts)
        else:
            # No paragraph tags, get all text
            text = soup.get_text(separator=' ', strip=True)

        # Clean up extra whitespace
        text = _re.sub(r'\s+', ' ', text)
        text = _re.sub(r'\n\s+\n', '\n\n', text)

        return text.strip()

    except Exception:
        # If parsing fails, try simple regex cleanup
        text = _re.sub(r'<jats:[^>]+>', '', text)
        text = _re.sub(r'</?[^>]+>', '', text)
        text = _re.sub(r'\s+', ' ', text)
        return text.strip()


def get_clipboard_image():
    """
    Get image from clipboard if available.
    Returns PIL Image or None.
    """
    from PIL import ImageGrab
    # Try to get image from clipboard
    img = ImageGrab.grabclipboard()
    if img is not None and hasattr(img, 'save'):
        return img
    return None

def copy_to_clipboard(obj):
    try :
        _pyperclip.copy(obj)
        return True
    except Exception as e:
        return False

def ocr(image_source) -> str:
    """
    Perform OCR on an image to extract text using RapidOCR.
    image_source can be a file path (str) or PIL Image object.
    """
    # Initialize RapidOCR engine
    engine = _rapidocr.RapidOCR()

    # Convert image to numpy array if needed
    if isinstance(image_source, str):
    # RapidOCR can handle file paths directly
        img_input = image_source
    else:
        # Convert PIL Image to numpy array
        img_input = _np.array(image_source)

    # Perform OCR
    result, elapse = engine(img_input)

    # Extract text from results
    # result is a list of [bbox, text, score] or None if no text detected
    if result is None or len(result) == 0:
        return ""

    text_lines = [detection[1] for detection in result]
    text = '\n'.join(text_lines)

    return normalize_text(text)


def format_authors(authors: List[Dict[str, str]], max_authors: int = 3) -> str:
    """
    Format author list for display, showing only first N authors.
    """
    if not authors:
        return "Unknown authors"

    formatted = []
    for author in authors[:max_authors]:
        given = author.get("given", "")
        family = author.get("family", "")
        if given and family:
            formatted.append(f"{given} {family}")
        elif family:
            formatted.append(family)

    if len(authors) > max_authors:
        formatted.append("et al.")

    return ", ".join(formatted)
