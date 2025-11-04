from datetime import datetime
from typing import Optional
from bson import ObjectId

class RuleModel:
    """Model for Custom Evaluation Rules"""
    
    def __init__(
        self,
        name: str,
        rules: str,
        description: str = "",
        _id: Optional[ObjectId] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self._id = _id
        self.name = name
        self.description = description
        self.rules = rules
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    def to_dict(self) -> dict:
        """Convert model to dictionary for MongoDB"""
        data = {
            "name": self.name,
            "description": self.description,
            "rules": self.rules,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
        if self._id:
            data["_id"] = self._id
        return data
    
    @staticmethod
    def from_dict(data: dict) -> 'RuleModel':
        """Create model from MongoDB document"""
        return RuleModel(
            _id=data.get("_id"),
            name=data.get("name", ""),
            description=data.get("description", ""),
            rules=data.get("rules", ""),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )
    
    def __repr__(self):
        return f"RuleModel(name='{self.name}', rules_length={len(self.rules)})"

