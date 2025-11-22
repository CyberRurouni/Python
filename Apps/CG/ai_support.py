import os
import cv2
import numpy as np
import base64
import json
import re
import asyncio
import google.generativeai as genai
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont


# Necessary
# Configure API Key
def recieve_api_key(api_key):
    if api_key:
        genai.configure(api_key=api_key)
        return True
    else:
        return False


# Recieve the expected quote along with author or label (If not None)
expected_data = ''
def recieve_expected_data(expected):
    expected_data = expected
    return expected_data


# requests
text_extraction_req = """
{
  "task": "Analyze image text elements with geometric/typographic precision",
  "requirements": {
    "output_format": "Single JSON array containing objects with keys: text/author/label, bounding_box, font_size",
    "precision_rules": {
      "author": {
        "must": [
          "Plausible human name (2-3 Initial-Capped words)",
          "Adjacent to main text",
          "Font_size ≤ 75% of main text"
        ],
        "must_not": [
          "Contain numbers/special chars",
          "All-caps formatting",
          "Corner positioning"
        ]
      },
      "label": {
        "must": [
          "Alphanumerics + _/#",
          "Margins/corners/footer placement",
          "Non-standard typography"
        ],
        "must_not": [
          "Complete sentences",
          "Name capitalization"
        ]
      },
      "text": {
        "must": [
          "Complete phrases/sentences",
          "Central/dominant position",
          "Largest font size hierarchy",
          "Element count MUST equal exact line count in image",
          "Treat hyphenated-wrapped text as single line"
        ],
        "must_not": ["Partial line fragments"]
      }
      for example:
      {
        "text": "The extracted text line",
        "bounding_box": {
          "x1": x1_coordinate,
          "y1": y1_coordinate,
          "x2": x2_coordinate,
          "y2": y2_coordinate
        },
        "font_size": estimated_font_size_in_pixels (if possible)
      }
    },
    "validation": {
      "mutually_exclusive": true,
      "completeness": "All visible text MUST be included",
      "count_verification": [
        "OCR-confirmed line count = JSON element count",
        "Reject output on mismatch",
        "Prioritize line count over classification conflicts"
      ]
    },
    "failure_conditions": [
      "Element count ≠ visible lines",
      "Text truncation",
      "Multiple elements per line"
    ]
  },
  "strict_instructions": [
    "Label detection > author detection",
    "Borderline cases → 'text' classification",
    "Absolute JSON syntax compliance",
    "No explanatory text - only JSON array"
  ],
  "examples": {
    "valid_line_count": "4 lines in image → 4 elements in JSON array"
  }
}
"""

text_detection_req = """Check if any visible text exists in this frame.
Return ONLY 1 if text is present, 0 if no text at any cost. No explanations.
Make sure the response is just a binary digit (0/1).
Make sure the response is of correct type (int) as it would break the system if you don't.
As per my program's response, the posssible text you would find is as follows:
{0}""".format(
    expected_data
)


async def extract_text_from_image(image_path):
    """
    Extracts text from an image using Gemini's multimodal capabilities asynchronously.
    """
    try:
        with Image.open(image_path) as img:
            img_format = img.format.lower()
            if not img_format:
                return "Error: Could not determine image format."

            buffered = BytesIO()
            img.save(buffered, format=img.format)
            base64_encoded_image = base64.b64encode(buffered.getvalue()).decode("utf-8")
            buffered.close()  # Close buffer to free resources

        image_part = {
            "mime_type": f"image/{img_format}",
            "data": base64_encoded_image,
        }

        model = genai.GenerativeModel("gemini-2.0-flash")

        # Use asyncio to handle the API request
        response = await asyncio.to_thread(
            model.generate_content,
            {"parts": [{"text": text_extraction_req}, image_part]},
        )

        result = response.text
        match = re.search(r"\[\s*{.*}\s*\]", result, re.DOTALL)
        if match:
            json_text = match.group(0)
            return json.loads(json_text), result
        else:
            return None, "Not Found"
    except FileNotFoundError:
        return "Error: Image file not found."
    except Exception as e:
        return f"An error occurred: {e}"



