# Summarizer

Summarizer is a Python-based application that fetches YouTube video subtitles, summarizes them using OpenAI's GPT-3.5 Turbo model, and allows users to make specific enquiries based on the summarized content.

## Features

- **Fetch Subtitles**: Fetch English or Hindi subtitles for any YouTube video.
- **Summarize Subtitles**: Summarize subtitles into key points.
- **Enquiry**: Make specific enquiries based on summarized content.
- **Keyboard Shortcut**: Use Alt+S to fetch English subtitles.
- **Dark Theme**: Customizable text and background colors.


**Set Up OpenAI API Key**:
    Replace `your_openai_api_key` in the script with your actual OpenAI API key or set it as an environment variable.

## Dependencies

The following libraries are required and should be installed using the `requirements.txt` file:

- `tkinter` (included with Python)
- `youtube-transcript-api`
- `pyperclip`
- `openai`
- `keyboard`

These can be installed using the following command:

```bash
pip install youtube-transcript-api pyperclip openai keyboard
