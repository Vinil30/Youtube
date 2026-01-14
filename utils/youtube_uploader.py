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

    def authenticate(self):
        """
        Handles one-time OAuth and token reuse.
        """
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
    def clean_title(self, title: str) -> str:
        title = title.strip()
        if len(title.split()) < 5:
            title = f"{title} | A Calm AI Podcast Discussion"
        return title[:100]


    def clean_description(self, description: str) -> str:
        base_disclaimer = (
            "This video features an AI-generated podcast-style discussion created "
            "for educational and informational purposes.\n\n"
            "The voices and conversation are generated using artificial intelligence "
            "and do not represent real individuals or opinions.\n\n"
            "This content is intended to encourage learning and thoughtful discussion."
        )

        description = description.strip()
        if len(description) < 40:
            description = base_disclaimer

        return description


    def upload_video(
        self,
        video_path,
        title,
        description,
        tags=None,
        privacy_status="unlisted"
    ):
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
