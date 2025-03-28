import logging
import fitz  # PyMuPDF
from llama_index.core.schema import Document
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


# ===== Config Section (mock config) =====
CHUNKING_OPTIONS_DEFAULTS = {
    "semantic": {
        "SEMANTIC_BREAKPOINT_THRESHOLD": 90,
        "SEMANTIC_EMBED_MODEL": HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
    }
}
SEMANTIC = "semantic"
SEMANTIC_EMBED_MODEL = "SEMANTIC_EMBED_MODEL"
SEMANTIC_BREAKPOINT_THRESHOLD = "SEMANTIC_BREAKPOINT_THRESHOLD"
# ========================================

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# import fitz  # PyMuPDF

def read_pdf_text(uploaded_file):
    """Extract text from uploaded PDF."""
    full_text = ""
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page in doc:
            full_text += page.get_text()
    return full_text



def semantic_chunking(text_content, data_chunking_options=None):
    """Split content into semantic chunks and return the list of chunks."""
    logger.info("Starting semantic chunking of content.")

    if data_chunking_options is None:
        data_chunking_options = CHUNKING_OPTIONS_DEFAULTS[SEMANTIC]

    semantic_breakpoint_threshold = data_chunking_options.get(
        SEMANTIC_BREAKPOINT_THRESHOLD,
        CHUNKING_OPTIONS_DEFAULTS[SEMANTIC][SEMANTIC_BREAKPOINT_THRESHOLD]
    )

    splitter = SemanticSplitterNodeParser(
        buffer_size=1,
        breakpoint_percentile_threshold=semantic_breakpoint_threshold,
        embed_model=data_chunking_options[SEMANTIC_EMBED_MODEL]
    )

    # Perform chunking
    node_contents = [node.get_content() for node in splitter.get_nodes_from_documents([Document(text=text_content)])]

    logger.info(
        f"Chunking completed with semantic-{semantic_breakpoint_threshold}. Generated {len(node_contents)} chunks."
    )

    return node_contents


# if __name__ == "__main__":
#     # === Path to your PDF file ===
#     pdf_file = "freddy_fazbears_pizza_contract.pdf" 

#     # === Extract text from PDF ===
#     text = read_pdf_text(pdf_file)
#     print(f"Extracted {len(text)} characters from PDF.")

#     # === Chunk the text ===
#     chunks = semantic_chunking(text)

#     # === Print the chunks ===
#     print("\n--- Chunks ---\n")
#     for i, chunk in enumerate(chunks):
#         print(f"Chunk {i + 1}:\n{chunk}\n{'-' * 40}")
