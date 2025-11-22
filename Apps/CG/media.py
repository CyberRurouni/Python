from utils import (
    render_background,
    render_text_element,
    render_fonts,
    calc_width_proportions,
    format_text_by_width,
)
from image import *
from video import insert_quote_on_video


def process_media(
    is_video,
    media_path,  # Can be an image or video file path
    quote_data,
    new_quote_text,
    author_data=None,
    new_author_text=None,
    label_data=None,
    new_label_text=None,
    background=None,
    overlay_img_path=None,  # Optional for images
):
    """Process image or video by adding text elements."""

    # Load fonts
    quote_font, author_font, label_font = render_fonts(
        quote_data["sizes"],
        author_data["size"] if author_data else None,
        label_data["size"] if label_data else None,
    )

    # Calculate width proportions
    quote_widths = calc_width_proportions(quote_font, quote_data["text"])
    author_widths = (
        calc_width_proportions(author_font, author_data["text"])
        if author_data and author_font
        else None
    )
    label_widths = (
        calc_width_proportions(label_font, label_data["text"])
        if label_data and label_font
        else None
    )

    # Format text elements
    formatted_quote = format_text_by_width(new_quote_text, quote_widths, quote_font)
    formatted_author = (
        format_text_by_width(new_author_text, author_widths, author_font)
        if author_data and author_widths
        else None
    )
    formatted_label = (
        format_text_by_width(new_label_text, label_widths, label_font)
        if label_data and label_widths
        else None
    )

    # Extract necessary parameters from the data structures
    quote_dims = quote_data["dims"]

    # Extract styles and colors from the structured data
    quote_style = quote_data.get("styles", {}).get("mode", "normal")
    quote_color = quote_data.get("styles", {}).get("color", (255, 255, 255))

    author_dims = author_data["dims"] if author_data else None
    author_style = author_data.get("mode", "normal") if author_data else None
    author_color = author_data.get("color", (255, 255, 255)) if author_data else None

    label_dims = label_data["dims"] if label_data else None
    label_style = label_data.get("mode", "normal") if label_data else None
    label_color = label_data.get("color", (255, 255, 255)) if label_data else None

    # Background settings
    use_background = background.get("mode", False) if background else False
    till = background.get("till", None) if background else None
    bg_color = background.get("color", (0, 0, 0)) if background else (0, 0, 0)
    bg_type = background.get("type", None) if background else None
    padding_ratio = background.get("padding_ratio", 0.2) if background else None

    # Process Media
    if is_video:
        # In the video processing block of process_media():
        result_video = insert_quote_on_video(
            media_path,
            formatted_quote,
            quote_dims,
            quote_font,
            quote_style,
            quote_color,
            formatted_author,
            author_dims,
            author_font,
            author_style,
            author_color,
            formatted_label,
            label_dims,
            label_font,
            label_style,
            label_color,
            use_background,
            till=till,
            bg_color=bg_color,
            bg_type=bg_type,
            padding_ratio=padding_ratio,
        )
        return result_video
    else:
        # Load images
        _, overlay_img = load_images(media_path, overlay_img_path)
        # Add text to images
        result_img = add_text_to_image(
            overlay_img,
            formatted_quote,
            quote_dims,
            quote_font,
            quote_style,
            quote_color,
            formatted_author,
            author_dims,
            author_font,
            author_style,
            author_color,
            formatted_label,
            label_dims,
            label_font,
            label_style,
            label_color,
            use_background,
            till=till,
            bg_color=bg_color,
            bg_type=bg_type,
            padding_ratio=padding_ratio,
        )
        result_path = "result.jpg"
        result_img.save(result_path)
        return result_path
