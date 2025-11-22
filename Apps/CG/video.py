from moviepy import (
    VideoFileClip,
    VideoClip,
    concatenate_audioclips,
    TextClip,
    CompositeVideoClip,
    ColorClip,
    ImageClip,
    AudioFileClip,
)
from PIL import Image, ImageDraw, ImageFont
from utils import render_background, render_text_element
import os
import numpy as np
import contextlib


# Helper function to safely close MoviePy clips
@contextlib.contextmanager
def safe_clip_handling(*clips):
    try:
        yield clips
    finally:
        for clip in clips:
            if clip is not None:
                try:
                    clip.close()
                except Exception as e:
                    print(f"Warning: Error closing clip: {e}")


def process_video(
    video_path,
    formatted_quote,
    quote_dims,
    quote_font,
    text_style,
    text_color,
    formatted_author=None,
    author_dims=None,
    author_font=None,
    author_style=None,
    author_color=None,
    formatted_label=None,
    label_dims=None,
    label_font=None,
    label_style=None,
    label_color=None,
):
    return insert_quote_on_video(
        video_path,
        formatted_quote,
        quote_dims,
        quote_font,
        text_style,
        text_color,
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
    )


def insert_quote_on_video(
    video_path,
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
    till=None,
    start_time=0.5,  # When text should start appearing
    end_time=3.5,  # When text should stop appearing
    fade_in_duration=1.5,  # Duration of fade in effect in seconds
    fade_out_duration=1.5,  # Duration of fade out effect in seconds
    bg_color=(0, 0, 0, 180),
    bg_type=None,
    padding_ratio=0.5,
    audio_path="",
):
    if use_background == "unified":
        unified_background = True
    elif use_background == "highlight_box":
        unified_background = False
    else:
        unified_background = False
        use_background = False

    def insert_text_on_frame(frame, alpha=1.0):
        image = Image.fromarray(frame)
        draw = ImageDraw.Draw(image, "RGBA")  # Add RGBA mode here

        # Create adjusted text color with alpha
        adjusted_quote_color = list(quote_color)
        if len(adjusted_quote_color) == 4:  # If quote_color has alpha channel
            adjusted_quote_color[3] = int(adjusted_quote_color[3] * alpha)
        else:
            adjusted_quote_color = (*adjusted_quote_color, int(255 * alpha))

        # Same for author color if provided
        adjusted_author_color = None
        if author_color:
            adjusted_author_color = list(author_color)
            if len(adjusted_author_color) == 4:
                adjusted_author_color[3] = int(adjusted_author_color[3] * alpha)
            else:
                adjusted_author_color = (*adjusted_author_color, int(255 * alpha))

        # Same for label color if provided
        adjusted_label_color = None
        if label_color:
            adjusted_label_color = list(label_color)
            if len(adjusted_label_color) == 4:
                adjusted_label_color[3] = int(adjusted_label_color[3] * alpha)
            else:
                adjusted_label_color = (*adjusted_label_color, int(255 * alpha))

        # Handle background rendering with adjusted alpha
        if use_background and unified_background:
            render_background(
                draw=draw,
                use_background=use_background,
                unified_background=unified_background,
                bg_color=bg_color,
                padding_ratio=padding_ratio,
                font=quote_font,
                text=quote_data,
                quote_dims=quote_dims,
                till=till,
                bg_type=bg_type,
            )

        # Render text with adjusted alpha
        render_text_element(
            draw,
            quote_data,
            quote_dims,
            quote_font,
            tuple(adjusted_quote_color),
            quote_style,
            author_data,
            author_dims,
            author_font,
            tuple(adjusted_author_color),
            author_style,
            label_data,
            label_dims,
            label_font,
            tuple(adjusted_label_color),
            label_style,
            padding_ratio,
            use_background,
            unified_background,
            bg_color,
            bg_type,
        )

        return np.array(image)

    clip = None
    audio_clip = None
    modified_clip = None

    try:
        clip = VideoFileClip(video_path)

        # Set default end_time if not provided
        if end_time is None:
            end_time = clip.duration

        def make_frame(t):
            frame = clip.get_frame(t)

            # Calculate alpha based on fade in/out
            alpha = 1.0

            # Before start time or after end time
            if t < start_time or t > end_time:
                alpha = 0.0
            # During fade in
            elif t < start_time + fade_in_duration:
                alpha = min(1, (t - start_time) / fade_in_duration)
            # During fade out
            elif t > end_time - fade_out_duration:
                alpha = max(0, (end_time - t) / fade_out_duration)

            # Only process frame if there's some visibility
            if alpha > 0:
                return insert_text_on_frame(frame, alpha)
            else:
                return frame

        modified_clip = VideoClip(make_frame, duration=clip.duration)

        # Audio processing
        with safe_clip_handling() as _:
            try:
                if audio_path != "":
                    # Load external audio file
                    audio_clip = AudioFileClip(audio_path)
                else:
                    # extract audio from video
                    sample_vid = VideoFileClip("sample/sample-vid-6.mp4")
                    audio_clip = sample_vid.audio
                if audio_clip is None:
                    # Don't add audio if audio_clip is None
                    print("No audio found in the video.")
                    return None
                if audio_clip.duration < clip.duration:
                    loop_count = int(clip.duration // audio_clip.duration) + 1
                    audio_clips = [audio_clip] * loop_count

                    # Properly handle concatenated audio clips
                    concatenated_audio = concatenate_audioclips(audio_clips)
                    with safe_clip_handling(concatenated_audio) as _:
                        concatenated_audio = concatenated_audio.with_duration(
                            clip.duration
                        )
                        modified_clip = modified_clip.with_audio(concatenated_audio)
                else:
                    audio_clip = audio_clip.with_duration(clip.duration)
                    modified_clip = modified_clip.with_audio(audio_clip)

                print("Audio added successfully and synced with video duration.")
            except Exception as e:
                print(f"Error adding audio: {str(e)}")

        output_path = "result.mp4"
        modified_clip.write_videofile(output_path, fps=24)

        return output_path

    except Exception as e:
        print(f"Error in video processing: {str(e)}")
        return None
    finally:
        # Ensure all resources are properly closed
        for resource in [clip, audio_clip, modified_clip]:
            if resource is not None:
                try:
                    resource.close()
                except Exception as e:
                    print(f"Warning: Error closing resource: {e}")


def forge_video(catch):
    clip = None
    audio = None

    try:
        clip = ImageClip(catch)
        audio = AudioFileClip("sample/sample-audio.mp3")
        clip = clip.with_duration(audio.duration)
        clip = clip.with_audio(audio)
        clip = CompositeVideoClip([clip])
        clip.write_videofile("result.mp4", fps=24)
        return "result.mp4"
    finally:
        # Properly close all resources
        for resource in [clip, audio]:
            if resource is not None:
                try:
                    resource.close()
                except Exception as e:
                    print(f"Warning: Error closing resource: {e}")
