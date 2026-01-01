import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode
from textnode import TextNode, TextType
from markdown_to_node import text_node_to_html_node

class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = HTMLNode(props={
            "href": "https://www.google.com",
            "target": "_blank",
        })

    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")

        node1 = LeafNode("a", "Click me!", {"href": "https://www.google.com"})

    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
    
    def test_img(self):
        node = TextNode("This is an image node", TextType.IMAGE, "image.com")
        html_node = text_node_to_html_node(node)

if __name__ == "__main__":
    unittest.main()