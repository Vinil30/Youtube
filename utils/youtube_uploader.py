import os
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


class YouTubeUploader:
    def __init__(self):
        self.creds = None

    # --------------------------------------------------
    # Authentication
    # --------------------------------------------------
    def authenticate(self):
        if os.path.exists("token.pickle"):
            with open("token.pickle", "rb") as f:
                self.creds = pickle.load(f)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "client_secret.json",
                    SCOPES
                )
                self.creds = flow.run_local_server(port=8080)

            with open("token.pickle", "wb") as f:
                pickle.dump(self.creds, f)

        return build("youtube", "v3", credentials=self.creds)

    # --------------------------------------------------
    # Safety cleaners
    # --------------------------------------------------
    def clean_title(self, title: str) -> str:
        if not title:
            raise ValueError("Title is required for YouTube upload")

        title = title.replace("\n", " ").strip()

        if len(title.split()) < 5:
            title = f"{title} | Horror Story"

        return title[:100]

    def clean_description(self, description: str) -> str:
        if not description:
            raise ValueError("Description is required for YouTube upload")

        description = description.strip()

        # YouTube max length safety
        return description[:5000]

    # --------------------------------------------------
    # Upload
    # --------------------------------------------------
    def upload_video(
        self,
        video_path: str,
        title: str,
        description: str,
        tags=None,
        privacy_status="public"
    ):
        if not os.path.exists(video_path):
            raise FileNotFoundError("Video file not found")

        youtube = self.authenticate()

        request_body = {
            "snippet": {
                "title": self.clean_title(title),
                "description": self.clean_description(description),
                "tags": tags or [],
                "categoryId": "22"
            },
            "status": {
                "privacyStatus": privacy_status
            }
        }

        media = MediaFileUpload(
            video_path,
            mimetype="video/mp4",
            resumable=True
        )

        request = youtube.videos().insert(
            part="snippet,status",
            body=request_body,
            media_body=media
        )

        response = request.execute()
        return response
