from jinja2 import Template
import json

class FrontendAgent:
    def __init__(self):
        self.components = {}
        self.current_styles = {}

    def process_request(self, prompt: str):
        print(f"FrontendAgent processing request: {prompt}")
        return "FrontendAgent response"

    def generate_html(self, template_str: str, context: dict) -> str:
        """Generate HTML using Jinja2 templating engine"""
        try:
            template = Template(template_str)
            return template.render(**context)
        except Exception as e:
            return f"Error generating HTML: {e}"

    def create_component(self, name: str, html_template: str):
        """Create a reusable component with a template"""
        self.components[name] = html_template

    def add_styles(self, styles: dict):
        """Add CSS styles to the current stylesheet"""
        self.current_styles.update(styles)

    def generate_css(self) -> str:
        """Generate CSS from the current styles"""
        css = ""
        for selector, properties in self.current_styles.items():
            css += f"{selector} {{\n"
            for prop, value in properties.items():
                css += f"    {prop}: {value};\n"
            css += "}\n"
        return css

    def create_interactive_element(self, element_type: str, properties: dict) -> str:
        """Create an interactive HTML element with JavaScript event handlers"""
        if element_type == "button":
            onclick = properties.get('onclick', '')
            text = properties.get('text', 'Button')
            return f'<button onclick="{onclick}">{text}</button>'
        elif element_type == "input":
            input_type = properties.get('type', 'text')
            placeholder = properties.get('placeholder', '')
            onchange = properties.get('onchange', '')
            return f'<input type="{input_type}" placeholder="{placeholder}" onchange="{onchange}">'
        else:
            return f"Unsupported element type: {element_type}"
