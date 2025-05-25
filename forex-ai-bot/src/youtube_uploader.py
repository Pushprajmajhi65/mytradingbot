# youtube_uploader.py (updated)
from google_auth_oauthlib.flow import InstalledAppFlow  
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
from dotenv import load_dotenv
from telegram_notifier import TelegramNotifier

load_dotenv()

class YouTubeUploader:
    def __init__(self):
        print("\nInitializing YouTube Uploader...")
        self.client_secrets_path = "client_secret_856674676214-i1lqu72uvh5hh84ppntc2ihn02upme6t.apps.googleusercontent.com.json"
        self.creds = self._authenticate()
        self.notifier = TelegramNotifier()
        print("✅ YouTube Uploader ready")

    def _authenticate(self):
        print("Authenticating with YouTube...")
        token_path = "token.json"
        
        if os.path.exists(token_path):
            print("Using existing credentials")
            from google.oauth2.credentials import Credentials
            return Credentials.from_authorized_user_file(token_path)
        
        print("Starting OAuth flow...")
        flow = InstalledAppFlow.from_client_secrets_file(
            self.client_secrets_path,
            scopes=["https://www.googleapis.com/auth/youtube.upload"],
            redirect_uri='http://localhost:8080'
        )
        
        print("Please authenticate in the browser window...")
        creds = flow.run_local_server(
            port=8080,
            authorization_prompt_message='Please visit this URL: {url}',
            success_message='Authentication complete! You may close this tab.',
            open_browser=True
        )
        
        with open(token_path, "w") as token:
            token.write(creds.to_json())
        print("✅ Authentication successful")
        return creds

    def upload(self, video_path: str, metadata: dict):
        print(f"\n📤 Uploading video: {video_path}")
        print(f"Title: {metadata['title']}")
        
        youtube = build('youtube', 'v3', credentials=self.creds)
        
        print("Preparing upload request...")
        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": metadata["title"],
                    "description": f"{metadata['script']}\n\n{metadata['hashtags']}",
                    "tags": [tag.strip("#") for tag in metadata["hashtags"].split()],
                    "categoryId": "22"
                },
                "status": {
                    "privacyStatus": "public",
                    "selfDeclaredMadeForKids": False
                }
            },
            media_body=MediaFileUpload(video_path)
        )
        
        print("Uploading to YouTube...")
        response = request.execute()
        print(f"✅ Upload successful! Video ID: {response['id']}")
        
        # Send Telegram notification
        self.notifier.send_alert(response['id'])
        
        return response