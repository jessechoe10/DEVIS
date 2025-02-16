from scrapybara import Scrapybara
from scrapybara.core.api_error import ApiError
from scrapybara.tools import BrowserTool
from dotenv import load_dotenv
import os
from google import genai
from PIL import Image
import base64
import io

load_dotenv()

class ScreenshotAgent:
    def __init__(self):
        self.client = Scrapybara(api_key=os.getenv("SCRAPYBARA_API_KEY"))
        self.instance = None
        self.genai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        
    def capture_screenshot(self, url):
        """Capture screenshot of a webpage"""
        try:
            # Start Ubuntu instance
            self.instance = self.client.start_ubuntu()
            
            # Start browser and get CDP URL
            cdp_url = self.instance.browser.start().cdp_url
            
            # Create browser tool
            browser_tool = BrowserTool(self.instance)
            
            # Navigate to URL
            browser_tool(command="go_to", url=url)
            
            # Take screenshot
            screenshot_result = browser_tool(command="screenshot")
            
            # Save to screenshot.png in the current directory
            output_path = os.path.join(os.path.dirname(__file__), "screenshot.png")
            with open(output_path, "wb") as f:
                f.write(base64.b64decode(screenshot_result.base_64_image))
            
            # Cleanup
            self.instance.browser.stop()
            self.instance.stop()
            self.instance = None
            
            return output_path
            
        except ApiError as e:
            print(f"Scrapybara API Error {e.status_code}: {e.body}")
            if self.instance:
                self.instance.stop()
                self.instance = None
            return None
        except Exception as e:
            print(f"Error capturing screenshot: {e}")
            if self.instance:
                self.instance.stop()
                self.instance = None
            return None
            
    def analyze_screenshot(self, screenshot_path):
        """Analyze screenshot using Google Gemini"""
        try:
            if not screenshot_path:
                return None
                
            with Image.open(screenshot_path) as img:
                response = self.genai_client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=[{
                        "role": "user",
                        "parts": [{
                            "text": "Analyze this UI screenshot and describe the layout, colors, components, and design patterns used. Focus on actionable details that could be used to recreate a similar design.",
                            "inline_data": {
                                "mime_type": "image/png",
                                "data": img
                            }
                        }]
                    }]
                )
                return response.text
                
        except Exception as e:
            print(f"Error analyzing screenshot: {e}")
            return None
            
    def cleanup(self):
        """Clean up resources"""
        if self.instance:
            try:
                self.instance.browser.stop()
                self.instance.stop()
            except:
                pass
            finally:
                self.instance = None

if __name__ == "__main__":
    # Test the screenshot agent
    agent = ScreenshotAgent()
    test_urls = [
        "https://www.google.com",
        "https://github.com",
        "https://news.ycombinator.com"
    ]
    
    for url in test_urls:
        print(f"\nTesting with {url}")
        screenshot_path = agent.capture_screenshot(url)
        if screenshot_path:
            print(f"Screenshot saved to: {screenshot_path}")
            if os.path.exists(screenshot_path):
                size = os.path.getsize(screenshot_path)
                print(f"Screenshot size: {size} bytes")
                if size > 1000:  # Basic validation that file has content
                    print(" Success!")
                else:
                    print(" Screenshot seems too small")
            else:
                print(" Screenshot file not found")
        else:
            print(" Failed to capture screenshot")
        
        # Cleanup between tests
        agent.cleanup()
