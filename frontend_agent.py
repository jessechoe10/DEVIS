import openai
import os
from pathlib import Path

class FrontendAgent:
    def __init__(self):
        self.client = openai.Client()
        
    def _read_current_code(self, project_dir):
        """Read current App.js and App.css content"""
        try:
            app_js = (Path(project_dir) / "src" / "App.js").read_text()
            app_css = (Path(project_dir) / "src" / "App.css").read_text()
            return app_js, app_css
        except:
            return None, None
        
    def generate_code(self, requirements, project_dir=None):
        """Generate or update App.js based on requirements"""
        current_code = None
        if project_dir:
            current_code, _ = self._read_current_code(project_dir)
            
        prompt = f"""You are generating a complete React App.js file. Output ONLY the code, no markdown, no explanations.
        Requirements: {requirements}
        
        Rules:
        1. Include all necessary imports
        2. Use modern React practices
        3. Output a complete, working App.js file
        4. Use normal CSS for styling
        5. DO NOT include any markdown or code fences
        6. DO NOT include any explanations
        7. Output ONLY the code that should be in App.js
        8. Just use pure CSS. Don't use any frameworks. Import relevant css files like App.css/index.css.
        
        Current code to iterate on:
        {current_code if current_code else 'No existing code'}
        """
        
        response = self.client.chat.completions.create(
            model="o1-mini",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content.strip()
        
    def generate_styles(self, component_description, project_dir=None):
        """Generate or update App.css based on requirements"""
        _, current_css = None, None
        if project_dir:
            _, current_css = self._read_current_code(project_dir)
            
        prompt = f"""You are generating a complete App.css file. Output ONLY the CSS code, no markdown, no explanations.
        Component description: {component_description}
        
        Rules:
        1. Include all necessary styles
        2. Use modern CSS practices
        3. Output a complete, working App.css file
        4. DO NOT USE ANY CSS FRAMEWORKS.
        5. DO NOT include any markdown or code fences
        6. DO NOT include any explanations
        7. Output ONLY the code that should be in App.css
        8. Just use pure CSS. Don't use any frameworks like Tailwind.
        
        Current CSS to iterate on:
        {current_css if current_css else 'No existing CSS'}
        """
        
        response = self.client.chat.completions.create(
            model="o1-mini",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content.strip()
        
    def cleanup(self):
        """Clean up resources"""
        pass

if __name__ == "__main__":
    agent = FrontendAgent()
    sample_req = "Create a modern navigation bar with a logo, links, and a search bar"
    code = agent.generate_code(sample_req)
    styles = agent.generate_styles(sample_req)
    print("Generated Code:", code)
    print("Generated Styles:", styles)
