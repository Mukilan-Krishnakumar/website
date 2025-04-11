from enum import Enum


class BlockType(Enum):
    paragraph = "paragraph"
    heading = "heading"
    code = "code"
    quote = "quote"
    unordered_list = "unordered_list"
    ordered_list = "ordered_list"
    horizontal_rule = "horizontal_rule"


class TextType(Enum):
    text = "text"
    bold = "bold"
    italic = "italic"
    code = "code"
    link = "link"
    image = "image"


allowed_delimiter = {
    "`": TextType.code,
    "**": TextType.bold,
    "*": TextType.italic,
}


MARKDOWN_BLOCK_SEPERATOR = "\r\n\r\n"
NEWLINE_CHARACTER = "\n"
