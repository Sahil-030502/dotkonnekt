import fitz


def extract_text(pdf_path: str):
    """
    Extract text page by page from a PDF.
    """

    document = fitz.open(pdf_path)

    pages = []

    for page_number, page in enumerate(document):

        text = page.get_text("text")

        pages.append({
            "page": page_number + 1,
            "text": text
        })

    document.close()

    return pages