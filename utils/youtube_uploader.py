import os
import pickle
from utils.title_desc_generator import TitleAndDescGenerator
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

        # Ensure minimum clarity
        if len(title.split()) < 5:
            title = f"{title} | AI Horror Story"


        # Avoid trailing punctuation issues
        title = title.replace("\n", " ").strip()

        # YouTube hard limit
        return title[:100]



    def clean_description(self, description: str) -> str:
        description = description.strip()

        disclaimer = (
    "\n\n---\n"
    "This video features an AI-generated fictional horror story created for "
    "entertainment purposes only.\n\n"
    "The narration voice is synthetic and generated using artificial intelligence. "
    "No real incidents are claimed as factual.\n\n"
    "#Shorts"
)


        # If LLM already handled disclaimers, don't duplicate
        if "AI-generated" in description.lower():
            return description[:5000]

        return f"{description}{disclaimer}"[:5000]


    def upload_video(
        self,
        video_path,
        title=None,
        description=None,
        tags=None,
        privacy_status="public",
        context=None
    ):
        youtube = self.authenticate()

        thumbnail_path = None

        # If context is provided, auto-generate everything
        if context:
            generator = TitleAndDescGenerator(context=context)
            data = generator.generate()
            title = data["title"]
            description = data["description"]


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
