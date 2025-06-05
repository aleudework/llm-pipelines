from pdf2image import convert_from_path
import os
import logging

def find_pdf(name, root_folder):
    """
    Retrieve a PDF file in a folder based on its name
    """
    name_str = str(name)
    for dirpath, dirnames, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.lower().endswith('.pdf'):
                file_base, ext = os.path.splitext(filename)
                if file_base == name_str:
                    return os.path.join(dirpath, filename)
    return None


def pdf_base_name(pdf_path):
    try:
        return os.path.splitext(os.path.basename(pdf_path))[0]
    except:
        logging.error("Could not find basename of pdf")


def pdf_to_images(pdf_path, folder_images):
    """
    """
    try:
        images = convert_from_path(pdf_path)
    except Exception as e:
        print(f"Fejl i convert_from_path: {e}")

    image_paths = []

    # Get PDF-name without .pdf
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    pdf_name_str = str(pdf_name)
    # Create output folder if it does not exist
    os.makedirs(folder_images, exist_ok=True)


    for i, image in enumerate(images, 1):
        image_path = os.path.join(folder_images, f"{pdf_name_str}_{i}.png")
        image.save(image_path)
        image_paths.append(image_path)
    
    return image_paths

def remove_images(image_paths):
    for path in image_paths:
        if os.path.exists(path):
            os.remove(path)