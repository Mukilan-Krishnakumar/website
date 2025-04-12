import re
from collections import Counter

from mkdwn2html.nodes import LeafNode, ParentNode
from mkdwn2html.constants import MARKDOWN_BLOCK_SEPERATOR, NEWLINE_CHARACTER, BlockType
from mkdwn2html.utils import text_to_textnode, text_to_children, text_node_to_html_node


class ConvertBlockToBlockType:
    def __init__(self, block):
        self.block = block
        self.lines = self.block.splitlines()
        self.initial_characters = [word[0] for word in self.lines if len(word) > 0]

    def is_heading_block(self):
        match = re.match(r"(?<!#)#{1,6} \w*", self.block)
        if match:
            return True
        return False

    def is_ordered_list_block(self):
        num_list = [str(n) for n in range(1, len(self.lines) + 1)]
        created_num_list = []
        for line in self.lines:
            num_search = re.search(f"^(\d). ", line)
            if num_search:
                created_num_list.append(num_search.group(1))
        if created_num_list == num_list:
            return True
        return False

    def is_code_block(self):
        prefix_chars = self.block[:3]
        suffix_chars = self.block[-3:]
        if prefix_chars == suffix_chars == "```":
            return True
        return False

    def is_quote_block(self):
        if all(flag == ">" for flag in self.initial_characters):
            return True
        return False

    def is_unordered_list_block(self):
        if all(flag in ["*", "-"] for flag in self.initial_characters):
            return True
        return False

    def get_block_mapper(self):
        MAPPING = {
            "is_heading_block": BlockType.heading,
            "is_ordered_list_block": BlockType.ordered_list,
            "is_unordered_list_block": BlockType.unordered_list,
            "is_code_block": BlockType.code,
            "is_quote_block": BlockType.quote,
        }
        return MAPPING

    def execute(self):
        mapper = self.get_block_mapper()
        for check_fn, block_type in mapper.items():
            success = False
            check_method = getattr(self, check_fn, None)
            if callable(check_method):
                success = check_method()
            if success:
                return block_type
        return BlockType.paragraph


class ConvertMarkdownContentToHtml:
    def __init__(self, mkdwn_content):
        self.mkdwn_content = mkdwn_content
        self.converted_html = None

    def convert_markdown_to_blocks(self):
        split_content = re.split(MARKDOWN_BLOCK_SEPERATOR, self.mkdwn_content)
        mkdwn_blocks = []
        for split_text in split_content:
            text = ""
            individual_blocks = split_text.split(NEWLINE_CHARACTER)
            for element in individual_blocks:
                if element not in ["", NEWLINE_CHARACTER]:
                    text += " ".join(element.split()) + NEWLINE_CHARACTER
            if len(text) > 0:
                if text[-1] == NEWLINE_CHARACTER:
                    text = text[:-1]
                mkdwn_blocks.append(text)
        return mkdwn_blocks

    def convert_to_quote(self, block):
        "Remove the first `>`"
        quote = ""
        for text in block.splitlines():
            # Remove the >
            filtered_text = text[1:]
            if len(filtered_text) > 0:
                if filtered_text[1] == " ":
                    filtered_text = filtered_text[1:]
                quote += filtered_text + "\n"

        if quote[-1] == "\n":
            quote = quote[:-1]
        quote_node = LeafNode("blockquote", quote)

        return quote_node

    def convert_to_paragraph(self, block):
        paragraph = " ".join(block.split("\n"))
        text_nodes = text_to_textnode(paragraph)
        children = text_to_children(text_nodes)
        paragraph_node = ParentNode("p", children)
        return paragraph_node

    def convert_to_heading(self, block):
        heading_dict = {1: "h1", 2: "h2", 3: "h3", 4: "h4", 5: "h5", 6: "h6"}
        for text in block.splitlines():
            heading_hash = text.split(" ")[0]
            heading_text = " ".join(text.split(" ")[1:])
            heading_count = Counter(heading_hash)["#"]
            if heading_count in heading_dict:
                htmlnodes = []
                for text_nodes in text_to_textnode(heading_text):
                    htmlnodes.append(text_node_to_html_node(text_nodes))
                return ParentNode(heading_dict[heading_count], htmlnodes)
            else:
                return LeafNode("p", text)

    def convert_to_code(self, block):
        # Remove the first code lines
        block = block[3:]
        # Remove the last code lines
        block = block[:-3]
        code = ""
        for text in block.splitlines():
            code += text + "\n"
        code = code[:-1]
        code_node = LeafNode("code", code)
        pre_node = ParentNode("pre", [code_node])
        return pre_node

    def convert_to_unordered_list(self, block):
        unordered_list_children = []
        for text in block.splitlines():
            sub_children_nodes = []
            for text_node in text_to_textnode(text[2:]):
                sub_children_nodes.append(text_node_to_html_node(text_node))
            unordered_list_children.append(ParentNode("li", sub_children_nodes))
        unordered_list = ParentNode("ul", unordered_list_children)
        return unordered_list

    def convert_to_ordered_list(self, block):
        ordered_list_children = []
        for text in block.splitlines():
            sub_children_nodes = []
            for text_node in text_to_textnode(text[3:]):
                sub_children_nodes.append(text_node_to_html_node(text_node))
            ordered_list_children.append(ParentNode("li", sub_children_nodes))
        ordered_list = ParentNode("ol", ordered_list_children)
        return ordered_list

    def get_conversion_mapper(self):
        MAPPING = {
            BlockType.quote: "convert_to_quote",
            BlockType.paragraph: "convert_to_paragraph",
            BlockType.code: "convert_to_code",
            BlockType.heading: "convert_to_heading",
            BlockType.unordered_list: "convert_to_unordered_list",
            BlockType.ordered_list: "convert_to_ordered_list",
        }
        return MAPPING

    def execute(self):
        blocks = self.convert_markdown_to_blocks()
        block_types = []
        for block in blocks:
            block_types.append(ConvertBlockToBlockType(block).execute())
        block_tuples = zip(blocks, block_types)
        children_nodes = []
        block_type_to_function = self.get_conversion_mapper()
        for block, block_type in block_tuples:
            fn_name = block_type_to_function.get(block_type)
            check_method = getattr(self, fn_name, None)
            if callable(check_method):
                children_nodes.append(check_method(block))
        div_node = ParentNode("div", children_nodes)
        return div_node
