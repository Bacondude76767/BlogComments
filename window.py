import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from datetime import datetime
import json
import os
import firebase_admin
from firebase_admin import db
from threading import Thread
import getpass
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string

class Window:
    def __init__(self, root):
        self.root = root
        self.root.title("My Window")
        self.root.geometry("800x600")
        
        # Get the current system username and capitalize first letter
        self.username = getpass.getuser().capitalize()
        
        # File path for saving comments and user profiles
        self.comments_file = "comments.json"
        self.profiles_file = "profiles.json"
        
        # Load user profiles
        self.user_profiles = self.load_profiles()
        # Ensure current user profile exists and has required fields
        if self.username not in self.user_profiles:
            self.user_profiles[self.username] = {
                "bio": "",
                "status": "",
                "favorite": "",
                "location": "",
                "interests": "",
                "email": "",
                "verified": False,
                "verification_code": ""
            }
            self.save_profiles()
        
        # Initialize Firebase
        self.firebase_initialized = False
        self.init_firebase()
        
        # Make window borderless
        self.root.overrideredirect(True)
        
        # Variables for dragging
        self.drag_data = {"x": 0, "y": 0}
        
        # Create title bar for dragging
        title_bar = tk.Frame(root, bg="#2b2b2b", height=30)
        title_bar.pack(fill=tk.X)
        title_bar.pack_propagate(False)
        
        # Title bar label
        title_bar_label = tk.Label(title_bar, text="Emmits Blog", bg="#2b2b2b", fg="white", font=("Arial", 10))
        title_bar_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Close button on title bar
        close_btn = tk.Button(title_bar, text="✕", bg="#2b2b2b", fg="white", bd=0, command=self.root.quit, font=("Arial", 12))
        close_btn.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Bind dragging events to title bar
        title_bar.bind("<Button-1>", self.on_drag_start)
        title_bar.bind("<B1-Motion>", self.on_drag_motion)
        title_bar_label.bind("<Button-1>", self.on_drag_start)
        title_bar_label.bind("<B1-Motion>", self.on_drag_motion)
        
        # Create a main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add a title label
        title_label = ttk.Label(main_frame, text="Welcome to My Window", font=("Arial", 24, "bold"))
        title_label.pack(pady=20)
        
        # Add some content
        content_label = ttk.Label(main_frame, text="This is a simple window template.", font=("Arial", 12))
        content_label.pack(pady=10)
        
        # Create button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        # Change to Comment button
        button = ttk.Button(button_frame, text="Comment", command=self.on_comment_click)
        button.pack(side=tk.LEFT, padx=10)
        
        # Add description button
        desc_button = ttk.Button(button_frame, text="Edit Profile", command=self.open_profile_editor)
        desc_button.pack(side=tk.LEFT, padx=10)
        
        # Add another button
        close_button = ttk.Button(button_frame, text="Close", command=self.root.quit)
        close_button.pack(side=tk.LEFT, padx=10)
        
        # Create entry frame
        entry_frame = ttk.Frame(main_frame)
        entry_frame.pack(pady=10, fill=tk.X)
        
        ttk.Label(entry_frame, text="Enter text:").pack(side=tk.LEFT, padx=5)
        self.entry = ttk.Entry(entry_frame, width=30)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Add a status label
        self.status_label = ttk.Label(main_frame, text="Status: Ready", relief=tk.SUNKEN)
        self.status_label.pack(pady=20, fill=tk.X)
        
        # Create a horizontal frame for blog and comments
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # Blog content textbox (read-only) on the left
        blog_frame = ttk.Frame(content_frame)
        blog_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        ttk.Label(blog_frame, text="Blog Content:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        self.blog_text = tk.Text(blog_frame, height=10, width=40, state=tk.DISABLED, bg="#f0f0f0", fg="#333333")
        self.blog_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Comments listbox on the right
        comments_frame = ttk.Frame(content_frame)
        comments_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        ttk.Label(comments_frame, text="Comments:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        self.comments_listbox = tk.Text(comments_frame, bg="#f0f0f0", fg="#333333", height=10, width=30, state=tk.DISABLED, wrap=tk.WORD)
        self.comments_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.comments_listbox.tag_config("username", foreground="blue", underline=True)
        self.comments_listbox.bind("<Button-1>", self.on_comment_click_text)
        
        # EDIT YOUR BLOG CONTENT HERE:
        self.set_blog_content("""Welcom to my Blog! i add random things here, i dont update it cause once this goes on github i cant really update it, but i am working on it! 9:44:22 AM""")
        
        # Load comments from Firebase or local file
        self.load_comments_from_firebase()
        
        # Handle window close event to save comments
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def on_drag_start(self, event):
        self.drag_data["x"] = event.x_root - self.root.winfo_x()
        self.drag_data["y"] = event.y_root - self.root.winfo_y()
    
    def on_drag_motion(self, event):
        x = event.x_root - self.drag_data["x"]
        y = event.y_root - self.drag_data["y"]
        self.root.geometry(f"+{x}+{y}")
    
    def on_button_click(self):
        text = self.entry.get()
        if text:
            self.status_label.config(text=f"Status: You entered '{text}'")
        else:
            self.status_label.config(text="Status: Please enter some text")
    
    def on_comment_click(self):
        """Add comment with username to listbox."""
        text = self.entry.get()
        if text:
            comment = f"{self.username}: {text}\n"
            self.comments_listbox.config(state=tk.NORMAL)
            # Insert username with tag
            self.comments_listbox.insert(tk.END, f"{self.username}", "username")
            self.comments_listbox.insert(tk.END, f": {text}\n")
            self.comments_listbox.config(state=tk.DISABLED)
            self.entry.delete(0, tk.END)
            self.save_comments()
            self.sync_comments_to_firebase()
            self.status_label.config(text="Status: Comment added!")
        else:
            self.status_label.config(text="Status: Please enter a comment")
    
    def on_comment_click_text(self, event):
        """Handle clicks on usernames in comments."""
        try:
            index = self.comments_listbox.index(f"@{event.x},{event.y}")
            line_start = self.comments_listbox.index(f"{index} linestart")
            line_end = self.comments_listbox.index(f"{index} lineend")
            line_text = self.comments_listbox.get(line_start, line_end)
            
            # Extract username (everything before the first colon)
            if ":" in line_text:
                username = line_text.split(":")[0].strip()
                self.view_profile(username)
        except:
            pass
    
    def save_comments(self):
        """Save all comments from listbox to JSON file."""
        comments = self.comments_listbox.get(1.0, tk.END).strip().split('\n')
        comments = [c for c in comments if c.strip()]
        try:
            with open(self.comments_file, 'w') as f:
                json.dump(comments, f, indent=2)
        except Exception as e:
            print(f"Error saving comments: {e}")
    
    def load_comments(self):
        """Load comments from JSON file into listbox."""
        if os.path.exists(self.comments_file):
            try:
                with open(self.comments_file, 'r') as f:
                    comments = json.load(f)
                self.comments_listbox.config(state=tk.NORMAL)
                for comment in comments:
                    self.comments_listbox.insert(tk.END, comment + "\n")
                self.comments_listbox.config(state=tk.DISABLED)
            except Exception as e:
                print(f"Error loading comments: {e}")
    
    def on_closing(self):
        """Handle window closing event."""
        self.save_comments()
        self.root.destroy()

    def init_firebase(self):
        """Initialize Firebase connection."""
        try:
            if os.path.exists('firebase_credentials.json'):
                cred = firebase_admin.credentials.Certificate('firebase_credentials.json')
                firebase_admin.initialize_app(cred, {
                    'databaseURL': 'https://emmits-blog-default-rtdb.firebaseio.com'
                })
                self.firebase_initialized = True
                print("Firebase initialized successfully!")
            else:
                print("firebase_credentials.json not found. Using local storage only.")
                self.firebase_initialized = False
        except Exception as e:
            print(f"Firebase initialization failed: {e}. Using local storage only.")
            self.firebase_initialized = False
    
    def sync_comments_to_firebase(self):
        """Upload comments to Firebase in background thread."""
        if not self.firebase_initialized:
            return
        
        def upload():
            try:
                comments_text = self.comments_listbox.get(1.0, tk.END).strip()
                comments = [c.strip() for c in comments_text.split('\n') if c.strip()]
                db.reference('comments').set(comments)
            except Exception as e:
                print(f"Error syncing to Firebase: {e}")
        
        thread = Thread(target=upload, daemon=True)
        thread.start()
    
    def load_comments_from_firebase(self):
        """Load comments from Firebase in background thread."""
        if not self.firebase_initialized:
            self.load_comments()
            return
        
        def download():
            try:
                data = db.reference('comments').get().val()  # type: ignore
                if data:
                    self.comments_listbox.config(state=tk.NORMAL)
                    self.comments_listbox.delete(1.0, tk.END)
                    for comment in data:
                        self.comments_listbox.insert(tk.END, comment + "\n")
                    self.comments_listbox.config(state=tk.DISABLED)
            except Exception as e:
                print(f"Error loading from Firebase: {e}")
                self.load_comments()
        
        thread = Thread(target=download, daemon=True)
        thread.start()
    
    def set_blog_content(self, content):
        """Set the blog content. Enable editing, insert text, then disable."""
        self.blog_text.config(state=tk.NORMAL)
        self.blog_text.insert(tk.END, content)
        self.blog_text.config(state=tk.DISABLED)
    
    def load_profiles(self):
        """Load user profiles from JSON file."""
        if os.path.exists(self.profiles_file):
            try:
                with open(self.profiles_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading profiles: {e}")
                return {}
        return {}
    
    def save_profiles(self):
        """Save user profiles to JSON file and Firebase."""
        try:
            with open(self.profiles_file, 'w') as f:
                json.dump(self.user_profiles, f, indent=2)
            # Sync to Firebase
            self.sync_profiles_to_firebase()
        except Exception as e:
            print(f"Error saving profiles: {e}")
    
    def open_profile_editor(self):
        """Open a window to edit the current user's profile."""
        profile_window = tk.Toplevel(self.root)
        profile_window.title(f"Edit Profile - {self.username}")
        profile_window.geometry("400x400")
        profile_window.configure(bg="#f0f0f0")
        
        # Header frame with username and moderator badge
        header_frame = ttk.Frame(profile_window)
        header_frame.pack(pady=10, padx=10, fill=tk.X)
        
        ttk.Label(header_frame, text=f"{self.username}", font=("Arial", 14, "bold")).pack(side=tk.LEFT)
        ttk.Label(header_frame, text="🛡️ MODERATOR", font=("Arial", 10, "bold"), foreground="gold").pack(side=tk.RIGHT)
        
        # Get current profile or create empty one
        current_profile = self.user_profiles.get(self.username, {
            "bio": "",
            "status": "",
            "favorite": "",
            "location": "",
            "interests": ""
        })
        
        # Bio
        ttk.Label(profile_window, text="Bio:", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=10, pady=(10, 0))
        bio_text = tk.Text(profile_window, height=4, width=45)
        bio_text.pack(padx=10, pady=(0, 10))
        bio_text.insert(1.0, current_profile.get("bio", ""))
        
        # Status
        ttk.Label(profile_window, text="Status:", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=10, pady=(10, 0))
        status_entry = ttk.Entry(profile_window, width=45)
        status_entry.pack(padx=10, pady=(0, 10))
        status_entry.insert(0, current_profile.get("status", ""))
        
        # Favorite
        ttk.Label(profile_window, text="Favorite:", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=10, pady=(10, 0))
        favorite_entry = ttk.Entry(profile_window, width=45)
        favorite_entry.pack(padx=10, pady=(0, 10))
        favorite_entry.insert(0, current_profile.get("favorite", ""))
        
        # Location
        ttk.Label(profile_window, text="Location:", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=10, pady=(10, 0))
        location_entry = ttk.Entry(profile_window, width=45)
        location_entry.pack(padx=10, pady=(0, 10))
        location_entry.insert(0, current_profile.get("location", ""))
        
        # Interests
        ttk.Label(profile_window, text="Interests:", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=10, pady=(10, 0))
        interests_entry = ttk.Entry(profile_window, width=45)
        interests_entry.pack(padx=10, pady=(0, 10))
        interests_entry.insert(0, current_profile.get("interests", ""))
        
        # Email / Verification
        ttk.Label(profile_window, text="Email:", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=10, pady=(10, 0))
        email_entry = ttk.Entry(profile_window, width=45)
        email_entry.pack(padx=10, pady=(0, 10))
        email_entry.insert(0, current_profile.get("email", ""))
        
        verified_var = tk.BooleanVar(value=current_profile.get("verified", False))
        verified_label = ttk.Label(profile_window, text=("Verified" if verified_var.get() else "Not Verified"), foreground=("green" if verified_var.get() else "red"))
        verified_label.pack(padx=10, pady=(0, 10))
        
        # Save and Verify buttons
        def save_profile():
            # Update profile fields
            self.user_profiles[self.username] = {
                "bio": bio_text.get(1.0, tk.END).strip(),
                "status": status_entry.get(),
                "favorite": favorite_entry.get(),
                "location": location_entry.get(),
                "interests": interests_entry.get(),
                "email": email_entry.get(),
                "verified": verified_var.get(),
                "verification_code": current_profile.get("verification_code", "")
            }
            self.save_profiles()
            profile_window.destroy()
            self.status_label.config(text="Status: Profile saved!")
        
        action_frame = ttk.Frame(profile_window)
        action_frame.pack(pady=8)
        ttk.Button(action_frame, text="Save Profile", command=save_profile).pack(side=tk.LEFT, padx=6)
        ttk.Button(action_frame, text="Send Verify Email", command=lambda: self.open_verify_window(email_entry.get(), verified_label, verified_var)).pack(side=tk.LEFT, padx=6)
    
    def view_profile(self, username):
        """Open a window to view a user's profile."""
        profile = self.user_profiles.get(username, {
            "bio": "No bio set",
            "status": "No status",
            "favorite": "Not set",
            "location": "Not set",
            "interests": "Not set"
        })
        
        view_window = tk.Toplevel(self.root)
        view_window.title(f"{username}'s Profile")
        view_window.geometry("400x350")
        view_window.configure(bg="#f0f0f0")
        
        # Header frame with username and moderator badge (only for Emmit)
        header_frame = ttk.Frame(view_window)
        header_frame.pack(pady=10, padx=10, fill=tk.X)
        
        ttk.Label(header_frame, text=username, font=("Arial", 16, "bold")).pack(side=tk.LEFT)
        
        # Show verified badge if user is verified
        if profile.get("verified"):
            ttk.Label(header_frame, text="✅ VERIFIED", font=("Arial", 10, "bold"), foreground="green").pack(side=tk.RIGHT, padx=(0,6))
        # Show moderator badge only for Emmit
        if username == self.username:
            ttk.Label(header_frame, text="🛡️ MODERATOR", font=("Arial", 10, "bold"), foreground="gold").pack(side=tk.RIGHT)
        
        # Bio frame
        ttk.Label(view_window, text="Bio:", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=10)
        ttk.Label(view_window, text=profile.get("bio", "No bio set"), font=("Arial", 9), wraplength=350, justify=tk.LEFT).pack(anchor=tk.W, padx=10, pady=(0, 10))
        
        # Status
        ttk.Label(view_window, text=f"Status: {profile.get('status', 'No status')}", font=("Arial", 10)).pack(anchor=tk.W, padx=10, pady=5)
        
        # Favorite
        ttk.Label(view_window, text=f"Favorite: {profile.get('favorite', 'Not set')}", font=("Arial", 10)).pack(anchor=tk.W, padx=10, pady=5)
        
        # Location
        ttk.Label(view_window, text=f"Location: {profile.get('location', 'Not set')}", font=("Arial", 10)).pack(anchor=tk.W, padx=10, pady=5)
        
        # Interests
        ttk.Label(view_window, text=f"Interests: {profile.get('interests', 'Not set')}", font=("Arial", 10)).pack(anchor=tk.W, padx=10, pady=5)

    def open_verify_window(self, email, verified_label, verified_var):
        """Open a small dialog to send verification email to the supplied address."""
        if not email or "@" not in email:
            messagebox.showerror("Error", "Please enter a valid email in your profile first.")
            return

        # generate code
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        # store code and email in profile
        profile = self.user_profiles.get(self.username, {})
        profile["email"] = email
        profile["verification_code"] = code
        profile["verified"] = False
        self.user_profiles[self.username] = profile
        self.save_profiles()

        # send email in background to avoid blocking UI
        def do_send():
            try:
                self.send_email(email, code)
                # prompt for code after send
                self.root.after(100, lambda: self.ask_for_verification_code(verified_label, verified_var))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to send verification email: {e}")

        Thread(target=do_send, daemon=True).start()

    def ask_for_verification_code(self, verified_label=None, verified_var=None):
        """Prompt user for the verification code and mark verified if matches."""
        entered = simpledialog.askstring("Email Verification", "Enter the verification code sent to your email:")
        if not entered:
            return
        stored = self.user_profiles.get(self.username, {}).get("verification_code", "")
        if entered.strip() == stored:
            self.user_profiles[self.username]["verified"] = True
            self.user_profiles[self.username]["verification_code"] = ""
            self.save_profiles()
            if verified_label is not None and verified_var is not None:
                verified_var.set(True)
                verified_label.config(text="Verified", foreground="green")
            messagebox.showinfo("Verified", "Email verified! You are now a verified member.")
        else:
            messagebox.showerror("Invalid", "The code you entered is incorrect.")

    def send_email(self, recipient_email, code):
        """Send verification email. You must configure SENDER_EMAIL and SENDER_PASSWORD below.

        NOTE: For Gmail you must use an App Password and enable SMTP access.
        """
        # --- Configure these with your sending account credentials ---
        SENDER_EMAIL = "your_email@example.com"
        SENDER_PASSWORD = "your_email_password_or_app_password"
        SMTP_SERVER = "smtp.gmail.com"
        SMTP_PORT = 465

        if SENDER_EMAIL.startswith("your_"):
            raise RuntimeError("Please configure SENDER_EMAIL and SENDER_PASSWORD in window.py to send email.")

        message = MIMEMultipart()
        message["From"] = SENDER_EMAIL
        message["To"] = recipient_email
        message["Subject"] = "Emmit's Blog - Email Verification"
        body = f"Your verification code is: {code}\n\nEnter this code in the app to verify your email."
        message.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, recipient_email, message.as_string())
        server.quit()
    
    def sync_profiles_to_firebase(self):
        """Upload profiles to Firebase in background thread."""
        if not self.firebase_initialized:
            return
        
        def upload():
            try:
                db.reference('profiles').set(self.user_profiles)
            except Exception as e:
                print(f"Error syncing profiles to Firebase: {e}")
        
        thread = Thread(target=upload, daemon=True)
        thread.start()
    
    def load_profiles_from_firebase(self):
        """Load profiles from Firebase in background thread."""
        if not self.firebase_initialized:
            return
        
        def download():
            try:
                data = db.reference('profiles').get().val()  # type: ignore
                if data:
                    self.user_profiles = data
            except Exception as e:
                print(f"Error loading profiles from Firebase: {e}")
        
        thread = Thread(target=download, daemon=True)
        thread.start()

def main():
    root = tk.Tk()
    app = Window(root)
    # Load profiles from Firebase after initialization
    app.load_profiles_from_firebase()
    root.mainloop()

if __name__ == "__main__":
    main()
