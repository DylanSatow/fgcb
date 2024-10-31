import time
import google.generativeai as genai
import os
import typing_extensions as typing
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import ast

PROMPT = """
You are to watch a video and provide a score rating between 0 and 1, where
the score is completely based on your prescribed identity's preferences. A 0 indicates
that the video is terrible and you would never want to even look at it, and a
1 indicates that you are really invested and want to watch the whole thing.
Try to avoid giving a full 0 or a full 1, as you should have some nuance in your answer.
Provide an explanation for your rating, and give an explanation of the video
"""

class Video(typing.TypedDict):
    rating: float
    rating_reasoning: str
    description: str

class LLM:
    def __init__(self):
        genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
        self.model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        self.prompt = PROMPT

    def setIdentity(self,desc: str):
        self.prompt = desc + self.prompt
    
    def score(self,video_file_name):
        print("Making LLM inference request...")
        video_file = uploadVideo(video_file_name)
        response = self.model.generate_content(
            [video_file, self.prompt],
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=Video
            ),
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )

        return ast.literal_eval(response.text)

def uploadVideo(video_file_name):
    print(f"Uploading file...")
    video_file = genai.upload_file(path=video_file_name)
    print(f"Completed upload: {video_file.uri}")

    # Check whether the file is ready to be used.
    while video_file.state.name == "PROCESSING":
        video_file = genai.get_file(video_file.name)

    if video_file.state.name == "FAILED":
        raise ValueError(video_file.state.name)
    return video_file