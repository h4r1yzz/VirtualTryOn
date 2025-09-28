import mimetypes
import os
import json
from typing import List
from google import genai
from google.genai import types
from pydantic import BaseModel

from dotenv import load_dotenv
load_dotenv()

class ClothingAnalysis(BaseModel):
    """Structured output for clothing item analysis."""
    description: str
    tags: List[str]
    clothing_type: str
    color: str
    texture: str
    material: str
    style: str
    season: str

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
    
def analyze_clothing_item(image_path):
    """
    Analyze a clothing item image and return structured information about it.

    Args:
        image_path (str): Path to the clothing item image

    Returns:
        ClothingAnalysis: Structured analysis of the clothing item
    """
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    # Load the clothing image
    image_bytes, mime_type = load_image_as_bytes(image_path)

    image = types.Part.from_bytes(
        data=image_bytes,
        mime_type=mime_type
    )

    prompt = """Analyze this clothing item image and provide detailed information about it.

    Please provide the following information in JSON format:
    {
        "description": "A detailed description of the clothing item",
        "tags": ["list", "of", "relevant", "tags", "about", "characteristics"],
        "clothing_type": "type of clothing (e.g., shirt, pants, dress, hat, etc.)",
        "color": "primary color of the item",
        "texture": "texture description (e.g., smooth, rough, knitted, woven)",
        "material": "material type (e.g., cotton, wool, denim, leather)",
        "style": "style description (e.g., casual, formal, vintage, modern)",
        "season": "suitable season (e.g., summer, winter, all-season)"
    }

    Focus on visible characteristics and provide specific, descriptive tags that would be useful for fashion categorization and search."""

    model = "gemini-2.5-flash"

    response = client.models.generate_content(
        model=model,
        contents=[prompt, image],
    )

    try:
        # Parse the JSON response
        response_text = response.text.strip()
        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]

        analysis_data = json.loads(response_text.strip())
        return ClothingAnalysis(**analysis_data)
    except (json.JSONDecodeError, Exception) as e:
        print(f"Error parsing response: {e}")
        print(f"Raw response: {response.text}")
        # Return a fallback analysis
        return ClothingAnalysis(
            description="Unable to analyze clothing item",
            tags=["unknown"],
            clothing_type="unknown",
            color="unknown",
            texture="unknown",
            material="unknown",
            style="unknown",
            season="unknown"
        )

def generate_fashion_product_images(apparel_image_paths, model_image_path, output_prefix="product"):
    """
    Generate fashion product listing images showing a model wearing multiple apparel items from 4 different angles.

    Args:
        apparel_image_paths (list): List of paths to apparel item images (clothing, accessories, etc.)
        model_image_path (str): Path to the model image
        output_prefix (str): Prefix for output image files
    """
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    # Load images
    # Load all apparel images
    apparel_parts = []
    for apparel_path in apparel_image_paths:
        apparel_bytes, apparel_mime = load_image_as_bytes(apparel_path)
        apparel_parts.append(types.Part.from_bytes(
            data=apparel_bytes,
            mime_type=apparel_mime
        ))

    # Load model image
    model_bytes, model_mime = load_image_as_bytes(model_image_path)

    model = "gemini-2.5-flash-image-preview"

    prompt = """Using the provided images, place [apparel items from the apparel images] onto [model from the model image].
    Ensure that the features of [model from the model image] remain completely unchanged. The added [apparel items] should integrate naturally and realistically, with proper layering and positioning appropriate for each type of item (clothing, accessories, shoes, etc.).

    Generate a single composite image that shows the model wearing the clothing from 4 different angles:
    1. Front view - model facing forward
    2. Back view - model facing away
    3. Side view (left profile)
    4. Side view (right profile)

    Arrange these 4 views in a clean, professional grid layout suitable for an e-commerce product listing.
    The background should be clean and neutral (white or light gray).
    Ensure the clothing fits naturally on the model and maintain consistent lighting across all angles.
    The style should be professional fashion photography suitable for online retail.

    Important: Only follow the exact appearance and characteristics shown in the provided images - do not add any additional features or modifications."""

    # Build contents array with prompt, all apparel images, and model image
    contents = [prompt]
    contents.extend(apparel_parts)  # Add all apparel image parts
    contents.append(types.Part.from_bytes(  # Add model image
        data=model_bytes,
        mime_type=model_mime
    ))

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

# FOR MODEL
def get_first_image_in_folder(folder_path):
    """Get the first image file found in the specified folder."""
    if not os.path.exists(folder_path):
        return None

    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}

    for filename in os.listdir(folder_path):
        if any(filename.lower().endswith(ext) for ext in image_extensions):
            return os.path.join(folder_path, filename)

    return None

# FOR APPARELS
def get_all_images_in_folder(folder_path):
    """Get all image files found in the specified folder."""
    if not os.path.exists(folder_path):
        return []

    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    image_files = []

    for filename in os.listdir(folder_path):
        if any(filename.lower().endswith(ext) for ext in image_extensions):
            image_files.append(os.path.join(folder_path, filename))

    return sorted(image_files)  # Sort for consistent ordering


def main():
    # Define folder paths relative to the script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    apparels_folder = os.path.join(script_dir, "apparels")
    model_folder = os.path.join(script_dir, "model")

    # Get all apparel images from the apparels folder
    apparel_paths = get_all_images_in_folder(apparels_folder)
    if apparel_paths:
        print(f"Found {len(apparel_paths)} apparel item(s):")
        for i, path in enumerate(apparel_paths, 1):
            print(f"  {i}. {path}")

    model_path = get_first_image_in_folder(model_folder)
    if model_path:
        print(f"Using model image: {model_path}")

    # Check if we found valid apparel images
    if not apparel_paths:
        print("Error: No apparel images found.")
        print(f"Place image files in the '{apparels_folder}' folder.")
        return

    # Step 1: Analyze the apparel items (always do this first)
    print("=" * 60)
    print("STEP 1: ANALYZING APPAREL ITEMS")
    print("=" * 60)

    apparel_analyses = []
    for i, apparel_path in enumerate(apparel_paths, 1):
        print(f"\nAnalyzing apparel item {i}: {apparel_path}")
        try:
            apparel_analysis = analyze_clothing_item(apparel_path)
            apparel_analyses.append(apparel_analysis)
            print(f"\n🔍 APPAREL ITEM {i} ANALYSIS RESULTS:")
            print("-" * 40)
            print(f"📝 Description: {apparel_analysis.description}")
            print(f"🏷️  Type: {apparel_analysis.clothing_type}")
            print(f"🎨 Color: {apparel_analysis.color}")
            print(f"🧵 Material: {apparel_analysis.material}")
            print(f"✨ Texture: {apparel_analysis.texture}")
            print(f"👔 Style: {apparel_analysis.style}")
            print(f"🌤️  Season: {apparel_analysis.season}")
            print(f"🏷️  Tags: {', '.join(apparel_analysis.tags)}")
            print("-" * 40)
        except Exception as e:
            print(f"Error analyzing apparel item {i}: {e}")
            return

    # Step 2: Generate product images
    if not model_path or not os.path.exists(model_path):
        print("Error: No model image found for product generation.")
        print(f"Place an image file in the '{model_folder}' folder.")
        return

    print("\n" + "=" * 60)
    print("STEP 2: GENERATING PRODUCT IMAGES")
    print("=" * 60)

    generate_fashion_product_images(apparel_paths, model_path, "product")


if __name__ == "__main__":
    main()
