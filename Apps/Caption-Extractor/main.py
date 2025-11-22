import os
import yt_dlp
import shutil
import re
import json
import webvtt
from flask import Flask, render_template, request, jsonify


def download_subtitles(yt_url, subtitle_folder):
    """
    Download subtitles for the given YouTube URL and save them in the specified folder.
    """
    ydl_opts = {
        "writesubtitles": True,
        "subtitleslangs": ["en"],
        "skip_download": True,
        "outtmpl": os.path.join(subtitle_folder, "%(title)s.%(ext)s"),
        "convert_subtitles": "srt",
    }

    if not os.path.exists(subtitle_folder):
        os.makedirs(subtitle_folder)

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([yt_url])

def convert_vtt_to_srt(vtt_file, srt_file):
    """
    Convert VTT subtitles to SRT format.
    """
    if not os.path.exists(srt_file):
        webvtt.read(vtt_file).save_as_srt(srt_file)
    
            

def clean_subtitles(srt_file):
    """
    Clean the vtt subtitles file by removing timecodes, indexes, and empty lines.
    """
    time_pattern = re.compile(r"\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}")
    index_pattern = re.compile(r"^\d+$", re.MULTILINE)

    clean_content = []

    with open(srt_file, "r+") as file:
        content = file.readlines()

        for line in content:
            if (
                time_pattern.match(line)
                or index_pattern.match(line)
                or not line.strip()
            ):
                continue  # Skip lines that match time, index patterns, or are empty
            clean_content.append(line)

        file.seek(0)  # Go to the beginning of the file
        file.truncate()  # Clear the file content
        file.writelines(clean_content)  # Write the filtered content back into the file

    return clean_content


def questions_and_answers(content):
    """
    Extract questions and their corresponding answers from the cleaned vtt file.
    """
    dialogue = []
    podcast = []
    intro = []
    question_pattern = re.compile(r".*\?$", re.IGNORECASE)

    def separation():
        intro_is_over = False
        for line in content:
            clean_line = line.strip()
            if not intro_is_over:
                intro.append(clean_line)
            else:
                dialogue.append(clean_line)

            if line.startswith("Now, let's start."):
                intro_is_over = True

    separation()

    def extract_QAs():
        current_question = None
        current_answers = []

        for line in dialogue:
            clean_line = line.strip()
            if question_pattern.match(clean_line):
                # Start a new question
                current_question = clean_line
                current_answers = []  # Reset answers for the new question
                # If we encounter a new question, save the previous Q&A pair
                if current_question:
                    podcast.append((current_question, current_answers))
            else:
                # Collect answers for the current question
                current_answers.append(clean_line)

        # Add the last Q&A pair after the loop
        if current_question:
            podcast.append((current_question, current_answers))

    extract_QAs()

    return podcast


def clean_caption_extractor(yt_url, subtitle_folder):
    """
    Main function to download, convert, and clean subtitles for the given YouTube video URL.
    """
    # Download subtitles
    if not os.path.exists(subtitle_folder):
        download_subtitles(yt_url, subtitle_folder)

    # Define file paths
    subtitles_vtt = os.path.join(
        subtitle_folder,
        "وائل حلاق： الدولة والحرية وكيف تفكك المجتمع ｜ بودكاست فنجان.en.vtt",
    )

    # Convert VTT to SRT
    if not os.path.exists(subtitles_vtt.replace(".vtt", ".srt")):
        convert_vtt_to_srt(subtitles_vtt, subtitles_vtt.replace(".vtt", ".srt"))

    subtitles_srt = subtitles_vtt.replace(".vtt", ".srt")


    # Clean the SRT file by removing unwanted lines
    content = clean_subtitles(subtitles_srt)
    podcast = questions_and_answers(content)

    return podcast


yt_url = "https://youtu.be/bwi8SZLFe2U"
subtitle_folder = os.path.join(os.path.dirname(__file__), "yt-subtitles")
podcast = clean_caption_extractor(yt_url, subtitle_folder)


if podcast:
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key'

    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/podcast")
    def get_podcast():
        return jsonify(podcast)

    if __name__ == "__main__":
        app.run(debug=True, host='0.0.0.0', port=5000)

        