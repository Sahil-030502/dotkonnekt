from src.tools.pdf_parser import extract_text
from src.tools.image_extractor import extract_images
from src.tools.trace import create_trace


IMAGE_DIR = "uploads/images"


def parser_node(state):

    pages = extract_text(state["pdf_path"])

    images = extract_images(state["pdf_path"], IMAGE_DIR)

    state["pages"] = pages
    state["images"] = images

    state["trace"].append(
        create_trace(
            "Parser",
            "parser_node",
            "SUCCESS",
            f"{len(pages)} pages | {len(images)} images extracted"
        )
    )

    return state
