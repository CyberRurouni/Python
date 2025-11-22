from PIL import Image, ImageDraw, ImageFont
from utils import (
    render_background,
    render_text_element,
)
def load_images(base_img_path, overlay_img_path=None):
    """Load the main image and optional overlay image."""
    base_img = Image.open(base_img_path)

    if overlay_img_path:
        overlay_img = Image.open(overlay_img_path)
        overlay_img = overlay_img.resize(base_img.size)
        return base_img, overlay_img

    return base_img, None


def add_text_to_image(
    image,
    quote_data,
    quote_dims,
    quote_font,
    quote_style,
    quote_color,
    author_data=None,
    author_dims=None,
    author_font=None,
    author_style=None,
    author_color=None,
    label_data=None,
    label_dims=None,
    label_font=None,
    label_style=None,
    label_color=None,
    use_background=False,
    till = None,
    bg_color=(0, 0, 0, 180),
    bg_type = None,
    padding_ratio=0.5,
    corner_radius=10,
):
    draw = ImageDraw.Draw(image, "RGBA")

    # Discern Background Mode
    if use_background == "unified":
        unified_background = True
    elif use_background == "highlight_box":
        unified_background = False
    else:
        unified_background = False
        use_background = False

    if use_background and unified_background:
        render_background(
            draw=draw,
            use_background=use_background,
            unified_background=unified_background,
            bg_color=bg_color,
            padding_ratio=padding_ratio,
            font=quote_font,
            text=quote_data,
            till= till,
            bg_type = bg_type,
            quote_dims=quote_dims,
        )

    render_text_element(
        draw,
        quote_data,
        quote_dims,
        quote_font,
        quote_color,
        quote_style,
        author_data,
        author_dims,
        author_font,
        author_color,
        author_style,
        label_data,
        label_dims,
        label_font,
        label_color,
        label_style,
        padding_ratio,
        use_background,
        unified_background,
        bg_color,
        bg_type,
    )
    return image
