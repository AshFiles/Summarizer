import tkinter as tk
from tkinter import messagebox, Scrollbar, Text
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import pyperclip
from openai import OpenAI
import keyboard

# Set your OpenAI API key here or use an environment variable
api_key = 'your_openai_api_key'  # Replace with your actual API key

client = OpenAI(api_key=api_key)

# Initialize original_subtitles and last_enquiry_response to empty strings
original_subtitles = ""
last_enquiry_response = ""

# Define colors
bg_color = "#000000"  # black
text_color = "#FFFFFF"  # white

def get_subtitles(video_id, lang):
    """
    Fetch subtitles for a given YouTube video ID and language.
    """
    formatter = TextFormatter()
    transcript = None

    # Try to fetch manually provided subtitles first
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
    except:
        pass

    # If manually provided subtitles are not found, try to fetch auto-generated ones
    if not transcript:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[f'a.{lang}'])
        except:
            return None

    # Format the transcript to plain text
    subtitle_text = formatter.format_transcript(transcript)
    return subtitle_text

def truncate_text(text, max_tokens=16384):
    """
    Truncate text to a specified number of tokens.
    """
    words = text.split()
    truncated_text = ' '.join(words[:max_tokens])
    return truncated_text

def summarize_text(text, language):
    """
    Summarize the given text using GPT-3.5 Turbo.
    """
    prompt = "Please summarize the following text into key points and include any key information:\n\n"
    if language == 'hi':
        prompt = "कृपया निम्नलिखित पाठ को मुख्य बिंदुओं में सारांशित करें और कोई भी महत्वपूर्ण जानकारी शामिल करें:\n\n"
    
    text = truncate_text(text)

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes text."},
                {"role": "user", "content": f"{prompt}{text}"}
            ],
            temperature=0.7,
        )
        summary = response.choices[0].message.content.strip()
        return summary
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
        return None

def fetch_subtitles(language):
    """
    Fetch and display subtitles for the YouTube video URL in the clipboard.
    """
    global original_subtitles
    clipboard_content = pyperclip.paste()
    if "youtube.com/watch?v=" in clipboard_content:
        video_id = clipboard_content.split('v=')[1]
        subtitles = get_subtitles(video_id, language)
        if subtitles:
            summary = summarize_text(subtitles, language)
            if summary:
                original_subtitles = subtitles
                text_box.config(state=tk.NORMAL)
                text_box.delete(1.0, tk.END)
                text_box.insert(tk.END, f"{language.capitalize()} Subtitles Summary:\n\n{summary}")
                text_box.config(state=tk.DISABLED)
                check_scrollbar(text_box, text_scrollbar)
        else:
            messagebox.showerror("Error", f"No {language.capitalize()} subtitles found.")
    else:
        messagebox.showerror("Error", "Clipboard does not contain a valid YouTube URL.")

def check_scrollbar(text_widget, scrollbar):
    """
    Show or hide the scrollbar based on the text content size.
    """
    text_widget.update_idletasks()
    if text_widget.yview()[1] < 1.0:
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    else:
        scrollbar.pack_forget()

def bring_to_front():
    """
    Bring the application window to the front.
    """
    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)

def setup_keyboard_shortcut():
    """
    Set up the keyboard shortcut to fetch English subtitles.
    """
    keyboard.add_hotkey('alt+s', lambda: (bring_to_front(), fetch_subtitles('en')))

def open_enquiry_window(reference_text=""):
    """
    Open a window to allow the user to make an enquiry based on the subtitles.
    """
    def submit_enquiry():
        custom_prompt = enquiry_text.get("1.0", tk.END).strip()
        if custom_prompt:
            if original_subtitles:
                enquiry_response = perform_enquiry(original_subtitles, custom_prompt, reference_text)
            else:
                enquiry_response = ask_without_subtitles(custom_prompt, reference_text)
            show_enquiry_response(enquiry_response)
        enquiry_window.destroy()
    
    enquiry_window = tk.Toplevel(root)
    enquiry_window.title("Enquiry")
    enquiry_window.configure(bg=bg_color)

    enquiry_text_frame = tk.Frame(enquiry_window, bg=bg_color)
    enquiry_text_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    enquiry_scrollbar = Scrollbar(enquiry_text_frame)
    enquiry_text = Text(enquiry_text_frame, wrap=tk.WORD, bg=bg_color, fg=text_color, font=("Arial", 12), yscrollcommand=enquiry_scrollbar.set)
    enquiry_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    enquiry_scrollbar.pack_forget()
    enquiry_scrollbar.config(command=enquiry_text.yview)

    enquiry_text.bind("<KeyRelease>", lambda e: check_scrollbar(enquiry_text, enquiry_scrollbar))

    submit_button = tk.Button(enquiry_window, text="Submit", command=submit_enquiry, bg=bg_color, fg=text_color, font=("Arial", 12))
    submit_button.pack(pady=10)

def show_enquiry_response(response):
    """
    Show the response to an enquiry in a new window with options to make another enquiry or close.
    """
    global last_enquiry_response
    last_enquiry_response = response
    
    response_window = tk.Toplevel(root)
    response_window.title("Enquiry Response")
    response_window.configure(bg=bg_color)

    response_text_frame = tk.Frame(response_window, bg=bg_color)
    response_text_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    response_scrollbar = Scrollbar(response_text_frame)
    response_text = Text(response_text_frame, wrap=tk.WORD, bg=bg_color, fg=text_color, font=("Arial", 12), yscrollcommand=response_scrollbar.set)
    response_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    response_scrollbar.pack_forget()
    response_scrollbar.config(command=response_text.yview)

    response_text.insert(tk.END, response)
    response_text.config(state=tk.DISABLED)
    check_scrollbar(response_text, response_scrollbar)

    button_frame = tk.Frame(response_window, bg=bg_color)
    button_frame.pack(pady=10)

    ok_button = tk.Button(button_frame, text="OK", command=response_window.destroy, bg=bg_color, fg=text_color, font=("Arial", 12))
    ok_button.pack(side=tk.LEFT, padx=5)

    enquiry_button = tk.Button(button_frame, text="Enquiry", command=lambda: open_enquiry_window(response), bg=bg_color, fg=text_color, font=("Arial", 12))
    enquiry_button.pack(side=tk.LEFT, padx=5)

def perform_enquiry(subtitles, custom_prompt, reference_text):
    """
    Perform an enquiry using the provided subtitles and custom prompt.
    """
    try:
        prompt = f"{custom_prompt}\n\nSubtitles:\n{subtitles}"
        if reference_text:
            prompt = f"{custom_prompt}\n\nReference:\n{reference_text}\n\nSubtitles:\n{subtitles}"
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        enquiry_result = response.choices[0].message.content.strip()
        return enquiry_result
    except Exception as e:
        return f"An error occurred: {str(e)}"

def ask_without_subtitles(custom_prompt, reference_text):
    """
    Ask a custom question without using subtitles.
    """
    try:
        prompt = custom_prompt
        if reference_text:
            prompt = f"{custom_prompt}\n\nReference:\n{reference_text}"
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        result = response.choices[0].message.content.strip()
        return result
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Create the main window
root = tk.Tk()
root.title("Summarizer")
root.configure(bg=bg_color)

# Create and place the buttons in a frame
button_frame = tk.Frame(root, bg=bg_color)
button_frame.pack(pady=10)

# Create buttons for fetching subtitles in English and Hindi
english_button = tk.Button(button_frame, text="English", command=lambda: fetch_subtitles('en'), bg=bg_color, fg=text_color, font=("Arial", 12))
english_button.pack(side=tk.LEFT, padx=5)

hindi_button = tk.Button(button_frame, text="Hindi", command=lambda: fetch_subtitles('hi'), bg=bg_color, fg=text_color, font=("Arial", 12))
hindi_button.pack(side=tk.LEFT, padx=5)

# Create and place the text box with a scrollbar
text_frame = tk.Frame(root, bg=bg_color)
text_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

text_scrollbar = Scrollbar(text_frame)
text_box = Text(text_frame, wrap=tk.WORD, state=tk.DISABLED, bg=bg_color, fg=text_color, font=("Arial", 12), yscrollcommand=text_scrollbar.set)
text_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
text_scrollbar.pack_forget()
text_scrollbar.config(command=text_box.yview)

text_box.bind("<KeyRelease>", lambda e: check_scrollbar(text_box, text_scrollbar))

# Place the enquiry button below the text box
enquiry_button = tk.Button(root, text="Enquiry", command=open_enquiry_window, bg=bg_color, fg=text_color, font=("Arial", 12))
enquiry_button.pack(pady=10)

# Setup keyboard shortcut
setup_keyboard_shortcut()

# Run the main loop
root.mainloop()
