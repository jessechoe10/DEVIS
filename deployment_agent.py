import docker
from typing import Dict, List, Optional
import yaml
import os
from dataclasses import dataclass
from datetime import datetime

@dataclass
class DeploymentConfig:
    app_name: str
    environment: str
    docker_image: str
    ports: Dict[str, str]
    env_vars: Dict[str, str]
    volumes: Optional[List[str]] = None

@dataclass
class DeploymentStatus:
    status: str
    timestamp: datetime
    details: Dict[str, any]

class DeploymentAgent:
    def __init__(self):
        self.docker_client = docker.from_env()
        self.deployments: Dict[str, DeploymentStatus] = {}
        self.environments = ['development', 'staging', 'production']
        self.current_configs: Dict[str, DeploymentConfig] = {}

    def process_request(self, prompt: str):
        print(f"DeploymentAgent processing request: {prompt}")
        return "DeploymentAgent response"

    def load_deployment_config(self, config_path: str) -> DeploymentConfig:
        """Load deployment configuration from a YAML file"""
        try:
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
                return DeploymentConfig(**config_data)
        except Exception as e:
            raise ValueError(f"Error loading deployment config: {e}")

    def deploy_container(self, config: DeploymentConfig) -> DeploymentStatus:
        """Deploy a Docker container based on the configuration"""
        try:
            # Pull the Docker image
            self.docker_client.images.pull(config.docker_image)

            # Create and start the container
            container = self.docker_client.containers.run(
                config.docker_image,
                name=f"{config.app_name}-{config.environment}",
                ports=config.ports,
                environment=config.env_vars,
                volumes=config.volumes,
                detach=True
            )

            status = DeploymentStatus(
                status="deployed",
                timestamp=datetime.utcnow(),
                details={"container_id": container.id}
            )
            self.deployments[config.app_name] = status
            return status
        except Exception as e:
            status = DeploymentStatus(
                status="failed",
                timestamp=datetime.utcnow(),
                details={"error": str(e)}
            )
            self.deployments[config.app_name] = status
            raise RuntimeError(f"Deployment failed: {e}")

    def get_deployment_status(self, app_name: str) -> Optional[DeploymentStatus]:
        """Get the current deployment status of an application"""
        return self.deployments.get(app_name)

    def stop_deployment(self, app_name: str) -> DeploymentStatus:
        """Stop a deployed application"""
        try:
            container_name = f"{app_name}-{self.current_configs[app_name].environment}"
            container = self.docker_client.containers.get(container_name)
            container.stop()
            
            status = DeploymentStatus(
                status="stopped",
                timestamp=datetime.utcnow(),
                details={"container_id": container.id}
            )
            self.deployments[app_name] = status
            return status
        except Exception as e:
            status = DeploymentStatus(
                status="error",
                timestamp=datetime.utcnow(),
                details={"error": str(e)}
            )
            self.deployments[app_name] = status
            raise RuntimeError(f"Failed to stop deployment: {e}")

    def validate_environment(self, environment: str) -> bool:
        """Validate if the environment is supported"""
        return environment in self.environments

    def get_logs(self, app_name: str, tail: int = 100) -> str:
        """Get logs from a deployed application"""
        try:
            container_name = f"{app_name}-{self.current_configs[app_name].environment}"
            container = self.docker_client.containers.get(container_name)
            return container.logs(tail=tail).decode('utf-8')
        except Exception as e:
            raise RuntimeError(f"Failed to get logs: {e}")

    def create_backup(self, app_name: str) -> str:
        """Create a backup of the application state"""
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backups/{app_name}_{timestamp}"
            os.makedirs(backup_path, exist_ok=True)
            
            # Save current configuration
            config = self.current_configs.get(app_name)
            if config:
                with open(f"{backup_path}/config.yaml", 'w') as f:
                    yaml.dump(config.__dict__, f)
            
            return backup_path
        except Exception as e:
            raise RuntimeError(f"Failed to create backup: {e}")
