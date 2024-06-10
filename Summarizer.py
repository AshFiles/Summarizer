import customtkinter as ctk
from tkinter import messagebox
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
bg_color = "#1a1a1a"  # Dark background
text_color = "#e0e0e0"  # Light text color

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
        prompt = "कृपया निम्नलिखित प्रतिलिपि को मुख्य बिंदुओं में सारांशित करें और कोई भी महत्वपूर्ण जानकारी शामिल करें:\n\n"
    
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
                text_box.configure(state=ctk.NORMAL)
                text_box.delete(1.0, ctk.END)
                text_box.insert(ctk.END, f"{language.capitalize()} Subtitles Summary:\n\n{summary}")
                text_box.configure(state=ctk.DISABLED)
        else:
            # If no English subtitles are found, try other languages
            if language == 'en':
                other_langs = ['hi', 'es', 'fr', 'de', 'it', 'ja', 'ko', 'pt', 'ru', 'zh']
                for lang in other_langs:
                    subtitles = get_subtitles(video_id, lang)
                    if subtitles:
                        summary = summarize_text(subtitles, lang)
                        if summary:
                            original_subtitles = subtitles
                            text_box.configure(state=ctk.NORMAL)
                            text_box.delete(1.0, ctk.END)
                            text_box.insert(ctk.END, f"{lang.capitalize()} Subtitles Summary:\n\n{summary}")
                            text_box.configure(state=ctk.DISABLED)
                            return
            messagebox.showerror("Error", f"No subtitles found in any language.")
    else:
        messagebox.showerror("Error", "Clipboard does not contain a valid YouTube URL.")

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
        custom_prompt = enquiry_text.get("1.0", ctk.END).strip()
        if custom_prompt:
            if original_subtitles:
                enquiry_response = perform_enquiry(original_subtitles, custom_prompt, reference_text)
            else:
                enquiry_response = ask_without_subtitles(custom_prompt, reference_text)
            show_enquiry_response(enquiry_response)
        enquiry_window.destroy()
    
    enquiry_window = ctk.CTkToplevel(root)
    enquiry_window.title("Enquiry")
    enquiry_window.configure(bg=bg_color)

    enquiry_text_frame = ctk.CTkFrame(enquiry_window)
    enquiry_text_frame.pack(padx=10, pady=10, fill=ctk.BOTH, expand=True)

    enquiry_text = ctk.CTkTextbox(enquiry_text_frame, wrap=ctk.WORD, font=("Arial", 12))
    enquiry_text.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)

    submit_button = ctk.CTkButton(enquiry_window, text="Submit", command=submit_enquiry, font=("Arial", 12))
    submit_button.pack(pady=10)

def show_enquiry_response(response):
    """
    Show the response to an enquiry in a new window with options to make another enquiry or close.
    """
    global last_enquiry_response
    last_enquiry_response = response
    
    response_window = ctk.CTkToplevel(root)
    response_window.title("Enquiry Response")
    response_window.configure(bg=bg_color)

    response_text_frame = ctk.CTkFrame(response_window)
    response_text_frame.pack(padx=10, pady=10, fill=ctk.BOTH, expand=True)

    response_text = ctk.CTkTextbox(response_text_frame, wrap=ctk.WORD, font=("Arial", 12))
    response_text.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)

    response_text.insert(ctk.END, response)
    response_text.configure(state=ctk.DISABLED)

    button_frame = ctk.CTkFrame(response_window)
    button_frame.pack(pady=10)

    ok_button = ctk.CTkButton(button_frame, text="OK", command=response_window.destroy, font=("Arial", 12))
    ok_button.pack(side=ctk.LEFT, padx=5)

    enquiry_button = ctk.CTkButton(button_frame, text="Enquiry", command=lambda: open_enquiry_window(response), font=("Arial", 12))
    enquiry_button.pack(side=ctk.LEFT, padx=5)

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

def show_original_subtitles():
    """
    Show the original subtitles in a new popup window.
    """
    if not original_subtitles:
        messagebox.showerror("Error", "No subtitles available.")
        return

    def copy_subtitles():
        pyperclip.copy(original_subtitles)
        messagebox.showinfo("Copied", "Subtitles copied to clipboard.")

    subtitles_window = ctk.CTkToplevel(root)
    subtitles_window.title("Original Subtitles")
    subtitles_window.configure(bg=bg_color)

    subtitles_text_frame = ctk.CTkFrame(subtitles_window)
    subtitles_text_frame.pack(padx=10, pady=10, fill=ctk.BOTH, expand=True)

    subtitles_text = ctk.CTkTextbox(subtitles_text_frame, wrap=ctk.WORD, font=("Arial", 12))
    subtitles_text.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)

    subtitles_text.insert(ctk.END, original_subtitles)
    subtitles_text.configure(state=ctk.DISABLED)

    copy_button = ctk.CTkButton(subtitles_window, text="Copy", command=copy_subtitles, font=("Arial", 12))
    copy_button.pack(pady=10)

# Initialize the main window
ctk.set_appearance_mode("dark")  # Modes: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("dark-blue")  # Themes: "blue" (default), "green", "dark-blue"

root = ctk.CTk()
root.title("Summarizer")
root.geometry("500x500")
root.configure(bg=bg_color)

# Create and place the buttons in a frame
button_frame = ctk.CTkFrame(root)
button_frame.pack(pady=10)

# Create buttons for fetching subtitles in English
english_button = ctk.CTkButton(button_frame, text="Get Subtitles", command=lambda: fetch_subtitles('en'), font=("Arial", 12))
english_button.pack(side=ctk.LEFT, padx=5)

# Create and place the text box
text_frame = ctk.CTkFrame(root)
text_frame.pack(padx=10, pady=10, fill=ctk.BOTH, expand=True)

text_box = ctk.CTkTextbox(text_frame, wrap=ctk.WORD, state=ctk.DISABLED, font=("Arial", 12))
text_box.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)

# Place the enquiry button and show subtitles button in the same row
button_row_frame = ctk.CTkFrame(root)
button_row_frame.pack(pady=10)

enquiry_button = ctk.CTkButton(button_row_frame, text="Enquiry", command=open_enquiry_window, font=("Arial", 12))
enquiry_button.pack(side=ctk.LEFT, padx=5)

show_subtitles_button = ctk.CTkButton(button_row_frame, text="Show Subtitles", command=show_original_subtitles, font=("Arial", 12))
show_subtitles_button.pack(side=ctk.LEFT, padx=5)

# Setup keyboard shortcut
setup_keyboard_shortcut()

# Run the main loop
root.mainloop()
