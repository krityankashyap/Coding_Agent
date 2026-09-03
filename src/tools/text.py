from pathlib import Path

_ESCAPED_MAP= {
  "\\n": "\n",
  "\\t": "\t",
  "\\r": "\r",
  "\\\\": "\\",
}

_HTML_ENTITIES= {
  "&lt;": "<",
  "&gt;": ">",
  "&amp;": "&",
  "&quot;": '"',
  "&apos;": "'",
}

_MARKDOWN_SUFFIXES= {".md", ".markdown", ".mdown", ".mkdn", ".mkd", ".mdwn", ".mdtxt", ".mdtext"}
_MARKUP_SUFFIXES= {".html", ".htm", ".xhtml", ".xml", ".xsl", ".xsd", ".svg", ".rss", ".atom"}


def looks_like_escape_src(txt: str) -> bool:
  """return true-> When they payload is one logical line stuffed with \\n sequences"""

  if "\\n" not in txt:
    return False
  
  return txt.count("\\n") <= 1

def normalized_source_txt(txt: str) -> str:
  """Turn double escaped lines/tabs into real ones. """
  if not looks_like_escape_src(txt):
    return txt
  
  normalized= txt
  for escaped, raw in _ESCAPED_MAP:
    normalized= normalized.replace(escaped, raw)

  return normalized


def unescape_html_entities(txt: str) -> str:
  """Turn HTML entities into real characters. """
  unescaped= txt

  if "&" not in txt:
    return txt
  
  for entity, raw in _HTML_ENTITIES:
    unescaped= unescaped.replace(entity, raw)

    return unescaped
  

def strip_markdown_fence(txt: str)-> str:
  """Strip markdown code fences from the text. """
  
  if "```" not in txt:
    return txt
  
  lines= txt.split("\n")
  if lines and lines[0].lstrip().startswith("```"):
    lines= lines[1:]  # Remove the opening fence line

  if lines and lines[-1].strip().startswith("```"):
    lines= lines[:-1]  # Remove the closing fence line

  return "\n".join(lines)

def prepare_file_content(path: str, txt: str) -> str:
  """
   Normalised the file content based on the file type. For markdown files, it strips code fences. For markup files, it unescapes HTML entities.
  """
  suffix= Path(path).suffix.lower()
  prepared= normalized_source_txt(txt)

  if suffix not in _MARKDOWN_SUFFIXES:
    prepared= strip_markdown_fence(prepared)
  if suffix not in _MARKUP_SUFFIXES:
    prepared= unescape_html_entities(prepared)

  return prepared



   