import unittest

from textnode import TextNode, TextType
from markdown_to_node import *

class TestConverter(unittest.TestCase):
    def test_paragraphs(self):
        md = """
#Heading1

##Heading2

This is **bolded** paragraph text in a p tag here

This is another paragraph with _italic_ text and `code` here

- This is an
- Unordered list

1. This is an
2. Ordered list

```
This is text that _should_ remain
the **same** even with inline stuff
```

> These are
> quotes

"""

        node = markdown_to_html_node(md)
        html = node.to_html()

    def test_extract_h1(self):
        md = """
## This is heading two
## This is heading one
"""
        

if __name__ == "__main__":
    unittest.main()