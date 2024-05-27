# Summarizer

## Description
A Python application that fetches, summarizes YouTube subtitles, and allows detailed enquiries using GPT-3.5 Turbo.

## Features
- Fetch subtitles from YouTube videos.
- Automatically fallback to other available languages if English subtitles are not found.
- Summarize subtitles into key points.
- Make detailed enquiries based on the fetched subtitles.
- Display the original subtitles in a separate window.
- Keyboard shortcut (Alt+S) to fetch subtitles.

## Usage
1. Ensure you have the required dependencies installed.
2. Set your OpenAI API key in the script.
3. Run the script.
4. Copy a YouTube video URL to your clipboard.
5. Click the "Get Subtitles" button to fetch and summarize subtitles.
6. Click the "Enquiry" button to make a detailed enquiry based on the subtitles.
7. Click the "Show Subtitles" button to view the original subtitles.

## Dependencies
- `tkinter`
- `youtube-transcript-api`
- `pyperclip`
- `openai`
- `keyboard`

Install the required dependencies using:
```bash
pip install tkinter youtube-transcript-api pyperclip openai keyboard