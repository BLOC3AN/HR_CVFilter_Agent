"""
API Client for Frontend to communicate with Backend API
"""

import requests
from typing import List, Optional, Dict
import os

class APIClient:
    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize API client
        
        Args:
            base_url: Backend API base URL (default: from env or localhost:8000)
        """
        self.base_url = base_url or os.getenv("BACKEND_API_URL", "http://localhost:8000")
    
    def health_check(self) -> Dict:
        """Check if backend API is healthy"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    def evaluate_cv(
        self,
        cv_content: str,
        job_description: str,
        custom_rules: str = "",
        llm_model: str = "gemini-2.0-flash"
    ) -> Dict:
        """
        Evaluate CV against job description
        
        Args:
            cv_content: CV text content
            job_description: Job description text
            custom_rules: Custom evaluation rules
            llm_model: LLM model name
            
        Returns:
            Dict with evaluation result
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/evaluate-cv",
                json={
                    "cv_content": cv_content,
                    "job_description": job_description,
                    "custom_rules": custom_rules,
                    "llm_model": llm_model
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
    
    def chat(
        self,
        message: str,
        job_description: str,
        custom_rules: str = "",
        cv_evaluations: Optional[List[Dict]] = None,
        chat_history: Optional[List[Dict]] = None,
        llm_model: str = "gemini-2.0-flash"
    ) -> Dict:
        """
        Chat with agent
        
        Args:
            message: User message
            job_description: Job description text
            custom_rules: Custom evaluation rules
            cv_evaluations: List of CV evaluations
            chat_history: Chat history
            llm_model: LLM model name
            
        Returns:
            Dict with chat response
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "message": message,
                    "job_description": job_description,
                    "custom_rules": custom_rules,
                    "cv_evaluations": cv_evaluations or [],
                    "chat_history": chat_history or [],
                    "llm_model": llm_model
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
    
    # Rules CRUD methods
    def get_all_rules(self) -> Dict:
        """Get all rules"""
        try:
            response = requests.get(f"{self.base_url}/api/rules", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
    
    def get_rule_names(self) -> Dict:
        """Get all rule names"""
        try:
            response = requests.get(f"{self.base_url}/api/rules/names", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
    
    def get_rule(self, name: str) -> Dict:
        """Get rule by name"""
        try:
            response = requests.get(f"{self.base_url}/api/rules/{name}", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
    
    def create_rule(self, name: str, rules: str, description: str = "") -> Dict:
        """Create new rule"""
        try:
            response = requests.post(
                f"{self.base_url}/api/rules",
                json={
                    "name": name,
                    "rules": rules,
                    "description": description
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
    
    def update_rule(self, name: str, rules: str, description: str = "") -> Dict:
        """Update existing rule"""
        try:
            response = requests.put(
                f"{self.base_url}/api/rules/{name}",
                json={
                    "rules": rules,
                    "description": description
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
    
    def delete_rule(self, name: str) -> Dict:
        """Delete rule"""
        try:
            response = requests.delete(f"{self.base_url}/api/rules/{name}", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

