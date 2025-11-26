# Emmits Blog

A borderless, draggable blog application with real-time comment syncing using Firebase.

## Features

- 🎨 Borderless and draggable window
- 💬 Real-time comments that sync across devices
- 📱 Comments saved to Firebase database
- 💾 Local backup storage as fallback
- ⏰ Timestamps on all comments

## Setup Instructions

### 1. Clone or Download the Project
```bash
git clone <your-repo-url>
cd BlogComments
```

### 2. Install Dependencies
```powershell
python -m pip install -r requirements.txt
```

### 3. Set Up Firebase

1. Go to https://firebase.google.com/
2. Create a new project
3. Set up a Realtime Database
4. Generate a service account key:
   - Go to Project Settings → Service Accounts
   - Click "Generate New Private Key"
   - Save the JSON file as `firebase_credentials.json` in this folder

5. Update the database URL in `window.py`:
   - Find line ~153: `'databaseURL': 'https://...'`
   - Replace with your actual Firebase URL

6. Set database security rules to:
```json
{
  "rules": {
    "comments": {
      ".read": true,
      ".write": true
    }
  }
}
```

### 4. Run the App
```powershell
python window.py
```

## How to Use

1. Type a comment in the text box
2. Click "Comment" to post
3. Comments appear instantly and sync to all devices using the app
4. Close the window with the ✕ button

## Important

⚠️ **Never share your `firebase_credentials.json` file!** It contains secret keys that should only be in your Firebase account.

## Files

- `window.py` - Main application
- `requirements.txt` - Python dependencies
- `firebase_credentials.json` - Your Firebase credentials (add this yourself)
- `.gitignore` - Files to exclude from version control

## Troubleshooting

**"firebase_credentials.json not found"**
- Make sure the file is in the same folder as `window.py`
- Check the filename spelling

**Comments not syncing**
- Check your internet connection
- Verify Firebase database URL is correct in the code
- Make sure database rules allow read/write

**App won't start**
- Run: `python -m pip install -r requirements.txt`
- Restart your terminal and try again

Enjoy your blog! 🎉
