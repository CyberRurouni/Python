import traceback
import os
import asyncio
from PIL import Image
from media import process_media
from ai_support import (
    recieve_api_key,
    extract_text_from_image,
)

from dotenv import load_dotenv
load_dotenv()



async def process_image():
    try:
        # Load and validate API key
        api_key = (
            os.getenv("GEMINI_API_KEY")
        )
        if not api_key or not recieve_api_key(api_key):
            raise ValueError("API key missing or configuration failed")

        # File paths configuration
        source_img = "mid_frame-3.jpg"
        target_img = "sample/vinland.jfif"
        target_video = "sample/vid-background-1.mp4"
        is_video = True

        # Extract text data from image
        parsed_data, result = await extract_text_from_image(source_img)

        if not parsed_data:
            print("⚠️ Warning: No text data found in the image.")
            return

        # Validate required fields
        if not all(
            "bounding_box" in item and "font_size" in item for item in parsed_data
        ):
            raise ValueError("Missing required fields in parsed data")

        # Content configuration
        quote = " ".join([item["text"] for item in parsed_data if "text" in item])
        author = "~Rurouni"  # Can be replaced with input("Enter the author's name: ").lower()
        label = (
            "enlightment_369"  # Can be replaced with input("Enter the label: ").lower()
        )

        # Step 1: Initialize style configuration
        style_config = {
            "quote": {"mode": "normal", "color": (255, 255, 255)},
            "author": {"mode": "normal", "color": (255, 255, 255)},
            "label": {"mode": "normal", "color": (255, 255, 255)},
            "background": {
                "mode": "unified", # "unified" or "highlight_box"
                "type": "regular",
                "color": (0, 0, 0),
                "padding_ratio": 0.2,
            },
        }

        # Step 2: Extract data from parsed results
        extracted = {
            "quote": {
                "dims": [
                    item["bounding_box"] for item in parsed_data if "text" in item
                ],
                "sizes": [item["font_size"] for item in parsed_data if "text" in item],
                "text": [item["text"] for item in parsed_data if "text" in item],
                "styles": style_config["quote"],  # Add styles here for consistency
            },
            "author": {
                "dims": [
                    item["bounding_box"] for item in parsed_data if "author" in item
                ],
                "sizes": [
                    item["font_size"] for item in parsed_data if "author" in item
                ],
                "text": [item["author"] for item in parsed_data if "author" in item],
                "styles": style_config["author"],  # Fixed: was using quote styles
            },
            "label": {
                "dims": [
                    item["bounding_box"] for item in parsed_data if "label" in item
                ],
                "sizes": [item["font_size"] for item in parsed_data if "label" in item],
                "text": [item["label"] for item in parsed_data if "label" in item],
                "styles": style_config["label"],  # Add styles here for consistency
            },
        }

        # Step 3: Validate essential data
        if len(extracted["quote"]["dims"]) < 1 or len(extracted["quote"]["sizes"]) < 1:
            raise ValueError("Insufficient quote data extracted")

        # Step 4: Process author and label configurations
        config = process_metadata(author, label, extracted, style_config)

        # Step 5: Complete background configuration
        style_config["background"]["till"] = (
            config["author"]["dims"][-1]["y2"]
            if (
                style_config["background"]["mode"] == "unified"
                and author != "none"
                and config["author"]["dims"]
            )
            else extracted["quote"]["dims"][-1]["y2"]  # Fallback to quote's Y2
        )

        # Step 6: Create final params object for process_media
        params = {
            "quote_data": extracted["quote"],
            "new_quote_text": quote,
            "author_data": config["author"],
            "new_author_text": author,
            "label_data": config["label"],
            "new_label_text": label,
            "background": style_config["background"],
        }

        # Lastly, Apply modifications
        if is_video:
            process_media(
                is_video=True, media_path=target_video, **params
            )  # Explicit is_video
        else:
            process_media(
                is_video=False,
                media_path=source_img,
                overlay_img_path=target_img,
                **params,
            )

    except ValueError as ve:
        print(f"❌ ValueError: {ve}")
        traceback.print_exc()
    except FileNotFoundError as fnf:
        print(f"❌ FileNotFoundError: {fnf}. Check if source files exist.")
        traceback.print_exc()
    except KeyError as ke:
        print(f"❌ KeyError: Missing expected key - {ke}")
        traceback.print_exc()
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        traceback.print_exc()


def process_metadata(author, label, extracted, style_config):
    """Process author and label metadata based on availability"""
    config = {
        "author": {
            "text": None,
            "dims": None,
            "size": None,
            "mode": None,
            "color": None,
        },
        "label": {
            "text": None,
            "dims": None,
            "size": None,
            "mode": None,
            "color": None,
        },
    }

    # Handle author configuration
    if author != "none":
        config["author"]["text"] = [author]
        config["author"]["dims"] = (
            extracted["author"]["dims"] or extracted["label"]["dims"]
        )
        config["author"]["size"] = (
            extracted["author"]["sizes"][0]
            if extracted["author"]["sizes"]
            else (
                extracted["label"]["sizes"][0] if extracted["label"]["sizes"] else None
            )
        )
        config["author"]["mode"] = style_config["author"]["mode"]
        config["author"]["color"] = style_config["author"]["color"]

    # Handle label configuration
    if label != "none":
        config["label"]["text"] = [label]
        config["label"]["dims"] = (
            extracted["label"]["dims"] or extracted["author"]["dims"]
        )
        config["label"]["size"] = (
            extracted["label"]["sizes"][0]
            if extracted["label"]["sizes"]
            else (
                extracted["author"]["sizes"][0]
                if extracted["author"]["sizes"]
                else None
            )
        )
        config["label"]["mode"] = style_config["label"]["mode"]
        config["label"]["color"] = style_config["label"]["color"]

    # Handle case where both author and label exist but one is missing dimensions
    if author != "none" and label != "none":
        if not extracted["author"]["dims"] and extracted["label"]["dims"]:
            config["author"]["dims"] = [
                {
                    "x1": extracted["label"]["dims"][0]["x1"],
                    "y1": extracted["label"]["dims"][0]["y1"] + 30,
                    "x2": extracted["label"]["dims"][0]["x2"],
                    "y2": extracted["label"]["dims"][0]["y2"] + 30,
                }
            ]
        elif not extracted["label"]["dims"] and extracted["author"]["dims"]:
            config["label"]["dims"] = [
                {
                    "x1": extracted["author"]["dims"][0]["x1"],
                    "y1": extracted["author"]["dims"][0]["y1"] + 30,
                    "x2": extracted["author"]["dims"][0]["x2"],
                    "y2": extracted["author"]["dims"][0]["y2"] + 30,
                }
            ]

    return config


# Run the function safely
if __name__ == "__main__":
    asyncio.run(process_image())
