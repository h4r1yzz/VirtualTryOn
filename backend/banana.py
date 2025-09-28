# To run this code you need to install the following dependencies:
# pip install google-genai python-dotenv

import mimetypes
import os
import argparse
from google import genai
from google.genai import types

from dotenv import load_dotenv
load_dotenv()


def save_binary_file(file_name, data):
    f = open(file_name, "wb")
    f.write(data)
    f.close()
    print(f"File saved to: {file_name}")


def load_image_as_bytes(image_path):
    """Load an image file and return bytes data and mime type for the API."""
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
        mime_type = mimetypes.guess_type(image_path)[0]
        if mime_type is None:
            mime_type = "image/jpeg"  # Default fallback
        return image_data, mime_type


def generate_fashion_product_images(clothing_image_path, model_image_path, output_prefix="product"):
    """
    Generate fashion product listing images showing a model wearing clothing from 4 different angles.

    Args:
        clothing_image_path (str): Path to the clothing item image
        model_image_path (str): Path to the model image
        output_prefix (str): Prefix for output image files
    """
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    # Load images
    clothing_bytes, clothing_mime = load_image_as_bytes(clothing_image_path)
    model_bytes, model_mime = load_image_as_bytes(model_image_path)

    model = "gemini-2.5-flash-image-preview"

    prompt = """Create a professional fashion product listing image showing the model wearing the provided clothing item.
    Generate a single composite image that shows the model wearing the clothing from 4 different angles:
    1. Front view - model facing forward
    2. Back view - model facing away
    3. Side view (left profile)
    4. Side view (right profile)

    Arrange these 4 views in a clean, professional grid layout suitable for an e-commerce product listing.
    The background should be clean and neutral (white or light gray).
    Ensure the clothing fits naturally on the model and maintain consistent lighting across all angles.
    The style should be professional fashion photography suitable for online retail."""

    contents = [
        prompt,
        types.Part.from_bytes(
            data=clothing_bytes,
            mime_type=clothing_mime
        ),
        types.Part.from_bytes(
            data=model_bytes,
            mime_type=model_mime
        )
    ]

    generate_content_config = types.GenerateContentConfig(
        response_modalities=[
            "IMAGE",
            "TEXT",
        ],
    )

    print("Generating fashion product images...")
    file_index = 0

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if (
            chunk.candidates is None
            or chunk.candidates[0].content is None
            or chunk.candidates[0].content.parts is None
        ):
            continue

        for part in chunk.candidates[0].content.parts:
            if part.inline_data and part.inline_data.data:
                file_name = f"{output_prefix}_{file_index}"
                file_index += 1
                inline_data = part.inline_data
                data_buffer = inline_data.data
                file_extension = mimetypes.guess_extension(inline_data.mime_type)
                if file_extension is None:
                    file_extension = ".png"
                save_binary_file(f"{file_name}{file_extension}", data_buffer)
            elif part.text:
                print(part.text)


def get_first_image_in_folder(folder_path):
    """Get the first image file found in the specified folder."""
    if not os.path.exists(folder_path):
        return None

    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}

    for filename in os.listdir(folder_path):
        if any(filename.lower().endswith(ext) for ext in image_extensions):
            return os.path.join(folder_path, filename)

    return None


def main():
    parser = argparse.ArgumentParser(description="Generate fashion product listing images")
    parser.add_argument("--clothing-image", help="Filename of the clothing item image (will look in apparels/ folder)")
    parser.add_argument("--model-image", help="Filename of the model image (will look in model/ folder)")
    parser.add_argument("--output-prefix", default="product", help="Prefix for output image files")

    args = parser.parse_args()

    # Define folder paths relative to the script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    apparels_folder = os.path.join(script_dir, "apparels")
    model_folder = os.path.join(script_dir, "model")

    # If no specific images provided, use the first image found in each folder
    if args.clothing_image:
        clothing_path = os.path.join(apparels_folder, args.clothing_image)
    else:
        clothing_path = get_first_image_in_folder(apparels_folder)
        if clothing_path:
            print(f"Using clothing image: {clothing_path}")

    if args.model_image:
        model_path = os.path.join(model_folder, args.model_image)
    else:
        model_path = get_first_image_in_folder(model_folder)
        if model_path:
            print(f"Using model image: {model_path}")

    # Check if we found valid images
    if not clothing_path or not os.path.exists(clothing_path):
        print("Error: No clothing image found.")
        print(f"Either specify --clothing-image or place an image file in the '{apparels_folder}' folder.")
        return

    if not model_path or not os.path.exists(model_path):
        print("Error: No model image found.")
        print(f"Either specify --model-image or place an image file in the '{model_folder}' folder.")
        return

    generate_fashion_product_images(clothing_path, model_path, args.output_prefix)


if __name__ == "__main__":
    main()
