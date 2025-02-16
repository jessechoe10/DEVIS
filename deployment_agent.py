import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()

class DeploymentAgent:
    def __init__(self):
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.vercel_token = os.getenv("VERCEL_TOKEN")
        self.github_headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.vercel_headers = {
            "Authorization": f"Bearer {self.vercel_token}"
        }
        
    def create_github_repo(self, repo_name, description=""):
        """Create a new GitHub repository"""
        url = "https://api.github.com/user/repos"
        data = {
            "name": repo_name,
            "description": description,
            "private": False
        }
        
        response = requests.post(url, headers=self.github_headers, json=data)
        return response.json() if response.status_code == 201 else None
        
    def push_to_github(self, repo_name, files):
        """Push generated files to GitHub"""
        base_url = f"https://api.github.com/repos/{repo_name}/contents"
        
        for file_path, content in files.items():
            data = {
                "message": f"Add {file_path}",
                "content": content.encode('utf-8').hex(),
                "branch": "main"
            }
            
            response = requests.put(f"{base_url}/{file_path}", 
                                  headers=self.github_headers, 
                                  json=data)
            
            if response.status_code not in [201, 200]:
                print(f"Error pushing {file_path}: {response.json()}")
                
    def deploy_to_vercel(self, github_repo_url):
        """Deploy the GitHub repository to Vercel"""
        url = "https://api.vercel.com/v9/projects"
        
        # Create project
        project_data = {
            "name": github_repo_url.split("/")[-1],
            "gitRepository": {
                "type": "github",
                "repo": github_repo_url
            }
        }
        
        response = requests.post(url, headers=self.vercel_headers, json=project_data)
        if response.status_code != 201:
            print(f"Error creating Vercel project: {response.json()}")
            return None
            
        project_id = response.json()["id"]
        
        # Trigger deployment
        deploy_url = f"https://api.vercel.com/v13/deployments"
        deploy_data = {
            "projectId": project_id,
            "target": "production"
        }
        
        response = requests.post(deploy_url, headers=self.vercel_headers, json=deploy_data)
        return response.json() if response.status_code == 201 else None

if __name__ == "__main__":
    agent = DeploymentAgent()
    # Example usage
    repo = agent.create_github_repo("test-ui-project")
    if repo:
        files = {
            "index.js": "console.log('Hello World')",
            "styles.css": "body { margin: 0; }"
        }
        agent.push_to_github(repo["full_name"], files)
        deployment = agent.deploy_to_vercel(repo["html_url"])
        print("Deployment status:", deployment)
