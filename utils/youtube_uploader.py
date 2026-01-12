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
                self.creds = flow.run_local_server(port=0)

            with open("token.pickle", "wb") as f:
                pickle.dump(self.creds, f)

        return build("youtube", "v3", credentials=self.creds)

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
                "title": title,
                "description": description,
                "tags": tags or [],
                "categoryId": "22"  # People & Blogs
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
