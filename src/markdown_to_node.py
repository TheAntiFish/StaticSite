from textnode import TextType, TextNode
from htmlnode import HTMLNode, ParentNode, LeafNode
import re
from enum import Enum

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered list"
    ORDERED_LIST = "ordered list"

def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)

    parent_node = ParentNode(tag="div", children=[])

    for block in blocks:
        block_type = block_to_blocktype(block)
        
        children = []
        if block_type != BlockType.CODE:
            children = text_to_textnodes(block)
        else:
            children = [TextNode(block, TextType.CODE)]

        node_children = list(map(text_node_to_html_node, children))
        new_node = ParentNode("", node_children)

        if block_type == BlockType.PARAGRAPH:
            new_node.tag = "p"
        if block_type == BlockType.HEADING:
            new_node.tag = f"h{block.count("#")}"
            new_node.children[0].value = new_node.children[0].value.lstrip("#").lstrip()
        if block_type == BlockType.CODE:
            new_node.tag = "pre"
        if block_type == BlockType.QUOTE:
            new_node.tag = "blockquote"
            for child in new_node.children:
                child.value = child.value.replace(">", "").strip()
        if block_type == BlockType.UNORDERED_LIST:
            new_node.tag = "ul"
            
            new_node.children = []
            items = block.split("\n")
            for item in items:
                stripped_item = item.lstrip("-").strip()
                text_nodes = text_to_textnodes(stripped_item)
                html_nodes = list(map(text_node_to_html_node, text_nodes))
                new_node.children.append(ParentNode("li", html_nodes))

        if block_type == BlockType.ORDERED_LIST:
            new_node.tag = "ol"

            new_node.children = []
            items = block.split("\n")
            for item in items:
                stripped_item = item[3:]
                text_nodes = text_to_textnodes(stripped_item)
                html_nodes = list(map(text_node_to_html_node, text_nodes))
                new_node.children.append(ParentNode("li", html_nodes))

        parent_node.children.append(new_node)

    return parent_node


def text_node_to_html_node(text_node):
    match text_node.text_type:
        case TextType.TEXT:
            return LeafNode(None, text_node.text)
        case TextType.BOLD:
            return LeafNode("b", text_node.text)
        case TextType.ITALIC:
            return LeafNode("i", text_node.text)
        case TextType.CODE:
            return LeafNode("code", text_node.text)
        case TextType.LINK:
            return LeafNode("a", text_node.text, {"href": text_node.url})
        case TextType.IMAGE:
            return LeafNode("img", "", {"src": text_node.url, "alt": text_node.text})

def markdown_to_blocks(markdown):
    to_return = []
    blocks = markdown.split("\n\n")

    for block in blocks:
        if block == "":
            continue
        
        to_return.append(block.strip())

    return to_return

def extract_title(markdown):
    for line in markdown.split("\n"):
        if len(line) < 2:
            continue
        if line[0] == "#" and line[1] != "#":
            return line.lstrip("#").strip()
    raise Exception("No h1 found")

def block_to_blocktype(block):
    if block[0] == "#":
        return BlockType.HEADING

    if block[:3] == "```" and block[-3:] == "```":
        return BlockType.CODE

    is_quote = True
    is_unordered = True
    is_ordered = True
    next_num = 2
    
    for line in block.split("\n"):
        if line[0] != ">":
            is_quote = False
        if line[:2] != "- ":
            is_unordered = False

        line_num = line.split(".")[0]
        if not line_num.isnumeric():
            is_ordered = False
        else:
            if int(line_num) + 1 == next_num:
                next_num += 1
            else:
                is_ordered = False
        if line[1:3] != ". ":
            is_ordered = False

    if is_quote:
        return BlockType.QUOTE
    if is_unordered:
        return BlockType.UNORDERED_LIST
    if is_ordered:
        return BlockType.ORDERED_LIST

    return BlockType.PARAGRAPH

def text_to_textnodes(text):
    bolded = split_nodes_delimiter([TextNode(text, TextType.TEXT)], "**", TextType.BOLD)
    italic = split_nodes_delimiter(bolded, "_", TextType.ITALIC)
    code = split_nodes_delimiter(italic, "`", TextType.CODE)
    images = split_nodes_image(code)
    links = split_nodes_link(images)

    return links

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []

    for old_node in old_nodes:
        if not old_node.text_type is TextType.TEXT:
            new_nodes.append(old_node)
            continue

        if old_node.text.count(delimiter) % 2 == 1:
            raise Exception(f"For text: '{old_node.text}'. No closing '{delimiter}' found")

        if delimiter in old_node.text:
            nodes = old_node.text.split(delimiter)
            node_is_delimited = True

            for node in nodes:
                node_is_delimited = not node_is_delimited

                if node == "":
                    continue

                if node_is_delimited:
                    new_nodes.append(TextNode(node, text_type))
                else:
                    new_nodes.append(TextNode(node, TextType.TEXT))
        else:
            new_nodes.append(TextNode(old_node.text, TextType.TEXT))

    return new_nodes

def split_nodes_image(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        extracted_images = extract_markdown_images(old_node.text)

        if len(extracted_images) == 0:
            new_nodes.append(old_node)
            continue

        current_text = old_node.text

        for image in extracted_images:
            sections = current_text.split(f"![{image[0]}]({image[1]})", 1)
            
            if sections[0] != "":
                new_nodes.append(TextNode(sections[0], TextType.TEXT))

            new_nodes.append(TextNode(image[0], TextType.IMAGE, image[1]))

            current_text = sections[1]

        if current_text != "":
            new_nodes.append(TextNode(current_text, TextType.TEXT))

    return new_nodes

def split_nodes_link(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        extracted_links = extract_markdown_links(old_node.text)

        if len(extracted_links) == 0:
            new_nodes.append(old_node)
            continue

        current_text = old_node.text

        for link in extracted_links:
            sections = current_text.split(f"[{link[0]}]({link[1]})", 1)
            
            if sections[0] != "":
                new_nodes.append(TextNode(sections[0], TextType.TEXT))
                
            new_nodes.append(TextNode(link[0], TextType.LINK, link[1]))

            current_text = sections[1]

        if current_text != "":
            new_nodes.append(TextNode(current_text, TextType.TEXT))

    return new_nodes

def extract_markdown_images(text):
    return re.findall(r"!\[(.*?)\]\((.*?)\)", text)

def extract_markdown_links(text):
    return re.findall(r"(?<!!)\[(.*?)\]\((.*?)\)", text)
