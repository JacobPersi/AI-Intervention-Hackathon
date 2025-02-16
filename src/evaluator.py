import base64
import re
import json
from dataclasses import dataclass
from typing import Optional
import google.generativeai as gemini

@dataclass
class DistractionAnalysis:
    """Structured response for distraction analysis."""
    is_distracted: bool
    rationale: str
    response: str

class GoogleGeminiEvaluator:
    """Handles interactions with Google's Gemini API for content analysis."""
    
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        gemini.configure(api_key=api_key)
        self.model = gemini.GenerativeModel('gemini-1.5-flash')

    def analyze_screenshot(self, screenshot_path: str) -> Optional[DistractionAnalysis]:
        """Analyze a screenshot using Gemini vision capabilities."""
        try:
            with open(screenshot_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

            structured_prompt = """
            Analyze this screenshot and provide a structured response in the following JSON format:
            {
                "is_distracted": boolean indicating if non-work activities are present,
                "rationale": detailed explanation of why this assessment was made,
                "response": encouraging and concise first-person message to help user stay focused
            }

            Focus on identifying:
            - Social media usage
            - Entertainment websites
            - Video streaming
            - Gaming applications
            - Other non-work applications

            Your response must be valid JSON with these exact keys and appropriate value types.
            The 'response' should be written in first person, as if speaking directly to the user.
            """

            contents = [{
                "parts": [
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": encoded_image
                        }
                    },
                    {"text": structured_prompt}
                ]
            }]

            response = self.model.generate_content(contents)
            
            try:
                json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    analysis_dict = json.loads(json_str)
                    
                    return DistractionAnalysis(
                        is_distracted=analysis_dict['is_distracted'],
                        rationale=analysis_dict['rationale'],
                        response=analysis_dict['response']
                    )
                else:
                    print("No valid JSON found in response")
                    return None
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON response: {e}")
                return None

        except FileNotFoundError:
            print("Error: Image not found.")
        except Exception as e:
            print(f"Error in Gemini analysis: {e}")
        
        return None