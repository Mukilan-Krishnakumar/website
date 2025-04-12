import re

from mkdwn2html.nodes import TextNode, LeafNode
from mkdwn2html.constants import allowed_delimiter, TextType


def extract_title(markdown):
    line = markdown.splitlines()[0]
    match = re.match(r"(?<!#)# (.*)", line)
    if match:
        return match.group(1)
    else:
        raise Exception("No Title given")


def extract_markdown_images(text):
    matches = re.findall(r"!\[(.*?)\]\((.*?)\)", text, re.MULTILINE)
    return matches


def extract_markdown_links(text):
    matches = re.findall(r"(?<!\!)\[(.*?)\]\((.*?)\)", text, re.MULTILINE)
    return matches


def split_nodes_delimiter(old_nodes, delimiter):
    new_nodes = []
    for node in old_nodes:
        if type(node) != TextNode:
            new_nodes.append(node)
        else:
            if node.text_type != TextType.text:
                new_nodes.append(node)
                continue
            if delimiter in allowed_delimiter.keys():
                split_nodes = node.text.split(delimiter)
                if len(split_nodes) % 2 == 0:
                    raise ValueError(f"Closing {delimiter} not found")
                node_list = []
                for num, i in enumerate(split_nodes):
                    if num % 2 != 0:
                        node_list.append(TextNode(i, allowed_delimiter[delimiter]))
                    else:
                        node_list.append(TextNode(i, TextType.text))
                new_nodes.extend(node_list)
    return new_nodes


def split_nodes_image(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if type(node) == TextNode:
            if node.text_type != TextType.text:
                new_nodes.append(node)
                continue
        extracted_images = extract_markdown_images(node.text)
        if extracted_images == None:
            new_nodes.append(node)
        else:
            text_val = node.text
            for extracted_image in extracted_images:
                split_text = text_val.split(
                    f"![{extracted_image[0]}]({extracted_image[1]})", 1
                )
                if len(split_text) < 1:
                    continue
                new_nodes.append(TextNode(split_text[0], TextType.text))
                new_nodes.append(
                    TextNode(
                        extracted_image[0],
                        TextType.image,
                        extracted_image[1],
                    )
                )
                text_val = split_text[1]
            if len(text_val) > 0:
                new_nodes.append(TextNode(text_val, TextType.text))
    return new_nodes


def split_nodes_link(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if type(node) == TextNode:
            if node.text_type != TextType.text:
                new_nodes.append(node)
                continue
        extracted_links = extract_markdown_links(node.text)
        if extracted_links == None:
            new_nodes.append(node)
        else:
            text_val = node.text
            for extracted_link in extracted_links:
                split_text = text_val.split(
                    f"[{extracted_link[0]}]({extracted_link[1]})", 1
                )
                if len(split_text) < 1:
                    continue
                new_nodes.append(TextNode(split_text[0], TextType.text))
                new_nodes.append(
                    TextNode(extracted_link[0], TextType.link, extracted_link[1])
                )
                text_val = split_text[1]
            if len(text_val) > 0:
                new_nodes.append(TextNode(text_val, TextType.text))
    return new_nodes


def text_to_textnode(text):
    node = TextNode(text, TextType.text)
    bold_split = split_nodes_delimiter([node], "**")
    italic_split = split_nodes_delimiter(bold_split, "*")
    code_split = split_nodes_delimiter(italic_split, "`")
    image_split = split_nodes_image(code_split)
    link_split = split_nodes_link(image_split)
    return link_split


def text_node_to_html_node(text_node):
    if text_node.text_type == TextType.text:
        return LeafNode(value=text_node.text)
    elif text_node.text_type == TextType.bold:
        return LeafNode("b", text_node.text)
    elif text_node.text_type == TextType.italic:
        return LeafNode("i", text_node.text)
    elif text_node.text_type == TextType.code:
        return LeafNode("code", text_node.text)
    elif text_node.text_type == TextType.link:
        return LeafNode("a", text_node.text, {"href": text_node.url})
    elif text_node.text_type == TextType.image:
        return LeafNode("img", "", {"src": text_node.url, "alt": text_node.text})
    else:
        raise Exception("Not a valid text type")


def text_to_children(text_nodes):
    children = []
    for text_node in text_nodes:
        html_node = text_node_to_html_node(text_node)
        children.append(html_node)
    return children
