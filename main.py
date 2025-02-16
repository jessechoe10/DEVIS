from voice_agent import VoiceAgent
from frontend_agent import FrontendAgent
from deployment_agent import DeploymentAgent
import os
from dotenv import load_dotenv
import subprocess
import webbrowser
from pathlib import Path

load_dotenv()

class DEVIS:
    def __init__(self):
        """Initialize DEVIS with voice, frontend and deployment capabilities"""
        self.voice_agent = VoiceAgent()
        self.frontend_agent = FrontendAgent()
        self.deployment_agent = DeploymentAgent()
        self.project_dir = None
        
    def setup_local_project(self):
        """Set up local React project"""
        self.voice_agent.speak("Setting up your React project...")
        self.project_dir = Path(os.path.expanduser("~/Documents/devis-ui"))
        if not self.project_dir.exists():
            subprocess.run(["npx", "create-react-app", str(self.project_dir)])

        self.voice_agent.speak("Project setup complete!")
        
    def run_local_dev_server(self):
        """Run local development server"""
        if self.project_dir:
            self.voice_agent.speak("Starting development server...")
            subprocess.Popen(["npm", "start"], cwd=self.project_dir)
            webbrowser.open("http://localhost:3000")
            self.voice_agent.speak("Development server is running. You can see your app in the browser.")
            
    def update_local_code(self, generated_code, generated_styles):
        """Update local project with new code"""
        if self.project_dir:
            self.voice_agent.speak("Updating your code...")
            app_file = self.project_dir / "src" / "App.js"
            styles_file = self.project_dir / "src" / "App.css"
            
            with open(app_file, "w") as f:
                f.write(generated_code)
            with open(styles_file, "w") as f:
                f.write(generated_styles)
            self.voice_agent.speak("Code updated! Check the browser to see your changes.")
        
    def run(self):
        """Main loop for voice-controlled software development"""
        welcome_msg = """
        Welcome to DEVIS - Your Voice Controlled Software Development Assistant!
        
        I'll help you build and deploy a web application through voice commands.
        Let's start getting everything set up.
        """
        self.voice_agent.speak(welcome_msg)

        
        try:
            # Initial setup
            self.setup_local_project()
            
            # Get initial requirements
            initial_requirements = self.voice_agent.listen_for_input("What kind of web app would you like to create?")
            
            if initial_requirements:
                self.voice_agent.speak("Great! I'll create a baseline app based on your requirements.")
                baseline_code = self.frontend_agent.generate_code(initial_requirements, self.project_dir)
                baseline_styles = self.frontend_agent.generate_styles(initial_requirements, self.project_dir)
                self.update_local_code(baseline_code, baseline_styles)
            
            # Start development server
            self.run_local_dev_server()
            
            
            while True:
                # Listen for command
                command = self.voice_agent.listen_for_input("What changes would you like to make?")
                
                if not command:
                    break
                
                # Check if user is satisfied
                if "looks good" in command.lower():
                    self.voice_agent.speak("Great! Would you like to deploy your application now?")
                    deploy_command = self.voice_agent.listen_for_input("Say 'yes' to deploy or 'no' to continue development.")
                    
                    if deploy_command and "yes" in deploy_command.lower():
                        # Deployment phase
                        self.voice_agent.speak("Starting deployment process...")
                        
                        # Create GitHub repository
                        self.voice_agent.speak("Creating GitHub repository...")
                        repo_name = "devis-generated-ui"
                        repo = self.deployment_agent.create_github_repo(repo_name)
                        
                        if repo:
                            self.voice_agent.speak(f"Created GitHub repository: {repo['html_url']}")
                            
                            # Push code to GitHub
                            if self.project_dir:
                                self.voice_agent.speak("Pushing your code to GitHub...")
                                files = {
                                    "src/App.js": (self.project_dir / "src" / "App.js").read_text(),
                                    "src/App.css": (self.project_dir / "src" / "App.css").read_text(),
                                    "package.json": (self.project_dir / "package.json").read_text()
                                }
                                self.deployment_agent.push_to_github(repo["full_name"], files)
                                self.voice_agent.speak("Code pushed to GitHub successfully!")
                                
                                # Deploy to Vercel
                                self.voice_agent.speak("Deploying to Vercel...")
                                deployment = self.deployment_agent.deploy_to_vercel(self.project_dir)
                                if deployment:
                                    self.voice_agent.speak(f"Your web app is now live at: {deployment['url']}")
                                    break
                        
                        self.voice_agent.speak("Deployment complete! Thank you for using DEVIS.")
                        break
                    
                    else:
                        self.voice_agent.speak("Okay, let's continue development. What changes would you like to make?")
                        continue
                
                # Process frontend changes
                elif any(keyword in command.lower() for keyword in ['create', 'add', 'update', 'change', 'style']):
                    self.voice_agent.speak("Processing your frontend request...")
                    generated_code = self.frontend_agent.generate_code(command, self.project_dir)
                    generated_styles = self.frontend_agent.generate_styles(command, self.project_dir)
                    self.update_local_code(generated_code, generated_styles)
                
                # Exit command
                elif "exit" in command.lower():
                    self.voice_agent.speak("Thank you for using DEVIS! Goodbye.")
                    break
                
        except KeyboardInterrupt:
            self.voice_agent.speak("Thank you for using DEVIS! Goodbye.")
        except Exception as e:
            self.voice_agent.speak(f"An error occurred: {str(e)}")
            print("DEVIS is shutting down...")
        finally:
            self.cleanup()
            
    def cleanup(self):
        """Clean up resources"""
        try:
            self.voice_agent.cleanup()
            self.frontend_agent.cleanup()
            self.deployment_agent.cleanup()
        except:
            pass

if __name__ == "__main__":
    devis = DEVIS()
    devis.run()
