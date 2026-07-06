import logging

from google import genai

from app.config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

GEMINI_MODEL = "gemini-2.5-flash"


class GeminiClient:
    def __init__(
        self, api_key: str = GEMINI_API_KEY, model: str = GEMINI_MODEL
    ) -> None:
        self.model = model
        self._client = genai.Client(api_key=api_key)

    def generate_content(self, prompt: str) -> str:
        logger.info("Calling Gemini API model=%s", self.model)

        response = self._client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        logger.info("Gemini API call succeeded model=%s", self.model)

        return response.text
