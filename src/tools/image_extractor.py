import fitz
import os


def extract_images(pdf_path: str, output_dir: str):
    """
    Extract all embedded images from a PDF.
    """

    os.makedirs(output_dir, exist_ok=True)

    document = fitz.open(pdf_path)

    images = []

    image_count = 0

    for page_index in range(len(document)):

        page = document[page_index]

        image_list = page.get_images(full=True)

        for image in image_list:

            xref = image[0]

            base_image = document.extract_image(xref)

            image_bytes = base_image["image"]

            extension = base_image["ext"]

            filename = f"page_{page_index+1}_{image_count}.{extension}"

            filepath = os.path.join(output_dir, filename)

            with open(filepath, "wb") as file:
                file.write(image_bytes)

            images.append({
                "page": page_index + 1,
                "image_path": filepath
            })

            image_count += 1

    document.close()

    return images