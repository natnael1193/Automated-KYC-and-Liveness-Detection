# Compatibility fix for langchain.docstore.document
# This module provides the missing langchain.docstore.document import

import sys
from types import ModuleType

# Create the docstore module
docstore_module = ModuleType('langchain.docstore')
sys.modules['langchain.docstore'] = docstore_module

# Create the document module inside docstore
document_module = ModuleType('langchain.docstore.document')
sys.modules['langchain.docstore.document'] = document_module

# Import Document from the correct location and expose it
from langchain_core.documents import Document

# Add Document to the document module
document_module.Document = Document

# Also add it to the docstore module
docstore_module.document = document_module

# Make it available as a module-level import
sys.modules['langchain.docstore.document'] = Document
