from PIL import Image, ImageDraw, ImageFont


def render_fonts(font_sizes, author_size, label_size):
    font_path = "arial.ttf"
    avg_font_size = int(sum(font_sizes) / len(font_sizes))

    # Initialize fonts
    quote_font = ImageFont.truetype(font_path, avg_font_size)
    author_font = (
        ImageFont.truetype(font_path, int(author_size)) if author_size else None
    )
    label_font = ImageFont.truetype(font_path, int(label_size)) if label_size else None

    return quote_font, author_font, label_font


def calc_width_proportions(font, text_lines):
    """Calculate proportional widths of text lines relative to combined text."""
    combined_text = " ".join(text_lines)
    total_width = font.getbbox(combined_text)[2]

    return [round(font.getbbox(line)[2] / total_width * 100) for line in text_lines]


def format_text_by_width(text, target_widths, font):
    """
    Format text into multiple lines based on specified width proportions.

    Args:
        text: Text to format
        target_widths: List of target width percentages for each line
        font: Font object for text measurement

    Returns:
        Dictionary with formatted lines and their width percentages
    """
    words = text.split()
    total_words = len(words)
    total_width = font.getbbox(text)[2]
    result = {}
    word_idx = 0

    for i, target_percent in enumerate(target_widths):
        line_num = i + 1
        current_line = []

        # Add words until we reach target width
        while word_idx < total_words:
            current_line.append(words[word_idx])
            test_line = " ".join(current_line)
            current_percent = round((font.getbbox(test_line)[2] / total_width) * 100)

            # Remove word if we exceeded target (unless it's the only word or last word)
            if (
                current_percent > target_percent
                and word_idx < total_words - 1
                and len(current_line) > 1
            ):
                current_line.pop()
                break

            word_idx += 1

            if word_idx >= total_words:
                break

        result[f"line-{line_num}"] = " ".join(current_line)
        result[f"occupied-{line_num}"] = current_percent

        # Fill remaining lines with empty strings if we've used all words
        if word_idx >= total_words and i < len(target_widths) - 1:
            for j in range(i + 1, len(target_widths)):
                result[f"line-{j+1}"] = ""
                result[f"occupied-{j+1}"] = 0
            break

    return result


def get_text_metrics(draw, text, font, padding_ratio):
    """Calculate text dimensions and related values."""
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    padding = int(height * padding_ratio)
    radius = padding // 2

    return width, height, padding, radius


def calc_bg_rect(x1, y1, text_width, text_height, padding):
    """Calculate background rectangle coordinates."""
    return [
        x1 - padding,
        y1 - padding,
        x1 + text_width + padding,
        y1 + text_height + padding,
    ]


def render_background(
    draw,
    use_background,
    unified_background,
    bg_color,
    till=None,
    text=None,
    font=None,
    padding_ratio=None,
    radius=None,
    bg_rect=None,
    quote_dims=None,
    bg_type=None,
):
    if use_background and not unified_background:
        if bg_type != "regular":
            draw.rounded_rectangle(bg_rect, fill=bg_color, radius=radius)
        elif bg_type == "regular":
            draw.rectangle(bg_rect, fill=bg_color)
    if use_background and unified_background:
        # Combine all quote lines for unified background
        all_lines = "\n".join([text[f"line-{i+1}"] for i in range(len(quote_dims))])

        _, _, padding, radius = get_text_metrics(draw, all_lines, font, padding_ratio)
        # Background covering all quote lines
        till = till if till is not None else quote_dims[-1]["y2"]
        bg_rect = [
            quote_dims[0]["x1"] - padding,
            quote_dims[0]["y1"] - padding,
            quote_dims[-1]["x2"] + padding,
            till + padding,
        ]

        if bg_type != "regular":
            draw.rounded_rectangle(bg_rect, fill=bg_color, radius=radius)
        elif bg_type == "regular":
            draw.rectangle(bg_rect, fill=bg_color)
        return None


def render_text(
    draw,
    lines,
    font,
    boxes,
    color,
    style,
    padding_ratio,
    use_background,
    unified_background,
    bg_color,
    bg_type,
):
    """Render text with appropriate styling and optional background."""
    for text, box in zip(lines, boxes):
        # Apply text style transformations
        if style == "upper":
            text = text.upper()
        elif style == "capitalize":
            text = text.capitalize()

        # Calculate text dimensions
        text_width, text_height, padding, radius = get_text_metrics(
            draw, text, font, padding_ratio
        )

        # Center text in bounding box
        x = box["x1"] + ((box["x2"] - box["x1"]) - text_width) // 2
        y = box["y1"] + ((box["y2"] - box["y1"]) - text_height) // 2

        # Compute the bg rect
        bg_rect = calc_bg_rect(x, y, text_width, text_height, padding)

        # Draw individual text background if needed
        if use_background and not unified_background:
            render_background(
                draw=draw,
                use_background=use_background,
                unified_background=unified_background,
                bg_color=bg_color,
                bg_rect=bg_rect,
                radius=radius,
                bg_type=bg_type,
            )

        # Draw the text
        draw.text((x, y), text, font=font, fill=color)


def render_text_element(
    draw,
    quote_data,
    quote_dims,
    quote_font,
    quote_color,
    quote_style,
    author_data=None,
    author_dims=None,
    author_font=None,
    author_color=None,
    author_style=None,
    label_data=None,
    label_dims=None,
    label_font=None,
    label_color=None,
    label_style=None,
    padding_ratio=0.5,
    use_background=False,
    unified_background=False,
    bg_color=(0, 0, 0, 180),
    bg_type=None,
):
    text_elements = [
        (quote_data, quote_dims, quote_font, quote_color, quote_style),
        (author_data, author_dims, author_font, author_color, author_style),
        (label_data, label_dims, label_font, label_color, label_style),
    ]

    for text_data, dims, font, color, style in text_elements:
        if text_data and dims:
            lines = [
                text_data.get(f"line-{i+1}", "")  # Use .get() with default
                for i in range(len(dims))
            ]
            render_text(
                draw,
                lines,
                font,
                dims,
                color,
                style,
                padding_ratio,
                use_background,
                unified_background,
                bg_color,
                bg_type,
            )
