from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import settings
import json
import re

class LLMService:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.1,  # Low temperature for consistent extraction
            max_tokens=4096
        )
    
    def generate(self, prompt: str) -> str:
        """Generate response and extract JSON."""
        response = self.llm.invoke(prompt)
        content = str(response.content)
        
        # Extract JSON from response (handle markdown code blocks)
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
        if json_match:
            return json_match.group(1)
        
        # Try to find raw JSON
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            return json_match.group(0)
        
        return content
    
    def validate_json(self, json_str: str) -> dict:
        """Parse and validate JSON string."""
        return json.loads(json_str)