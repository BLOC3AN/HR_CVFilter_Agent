import os
import ssl
from datetime import datetime
from typing import List, Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, DuplicateKeyError
from dotenv import load_dotenv
from src.models.rule_model import RuleModel
from src.utils.logger import Logger

# Load environment variables from project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
env_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path=env_path)

logger = Logger(__name__)

class RuleService:
    """Service for managing Custom Evaluation Rules in MongoDB"""
    
    def __init__(self):
        self.mongo_uri = os.getenv("MONGO_URI")
        self.db_name = os.getenv("MONGO_DB", "hr_cv_filter_agent")
        self.collection_name = os.getenv("MONGO_COLLECTION", "rules")
        
        logger.info(f"MONGO_URI: {self.mongo_uri}")
        if not self.mongo_uri:
            error_msg = "MONGO_URI not found in environment variables"
            logger.error(f"❌ {error_msg}")
            raise ValueError(error_msg)
        
        try:
            # Try multiple connection strategies for better compatibility
            connection_params = {
                'serverSelectionTimeoutMS': 10000,
                'connectTimeoutMS': 10000,
                'socketTimeoutMS': 10000,
            }

            # Strategy 1: Try with default settings (URI already has SSL params)
            try:
                logger.info("Attempting MongoDB connection...")
                self.client = MongoClient(self.mongo_uri, **connection_params)
                self.client.admin.command('ping')
                logger.info("✅ MongoDB connection successful")
            except Exception as e1:
                logger.warning(f"First connection attempt failed: {str(e1)[:100]}")

                # Strategy 2: Try with explicit TLS settings
                try:
                    logger.info("Retrying with explicit TLS settings...")
                    connection_params['tls'] = True
                    connection_params['tlsAllowInvalidCertificates'] = True
                    self.client = MongoClient(self.mongo_uri, **connection_params)
                    self.client.admin.command('ping')
                    logger.info("✅ MongoDB connection successful with TLS")
                except Exception as e2:
                    logger.error(f"Second connection attempt failed: {str(e2)[:100]}")
                    raise ConnectionFailure(f"All MongoDB connection attempts failed. Last error: {str(e2)}")

            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]

            # Create unique index on name
            self.collection.create_index("name", unique=True)

            logger.info(f"✅ Connected to MongoDB: {self.db_name}.{self.collection_name}")
        except ConnectionFailure as e:
            logger.error(f"❌ Failed to connect to MongoDB: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error connecting to MongoDB: {str(e)}")
            raise
    
    def create_rule(self, name: str, rules: str, description: str = "") -> Optional[RuleModel]:
        """Create a new rule"""
        try:
            rule = RuleModel(name=name, rules=rules, description=description)
            result = self.collection.insert_one(rule.to_dict())
            rule._id = result.inserted_id
            logger.info(f"✅ Created rule: {name}")
            return rule
        except DuplicateKeyError:
            logger.error(f"❌ Rule with name '{name}' already exists")
            return None
        except Exception as e:
            logger.error(f"❌ Error creating rule: {str(e)}")
            return None
    
    def get_rule_by_name(self, name: str) -> Optional[RuleModel]:
        """Get a rule by name"""
        try:
            doc = self.collection.find_one({"name": name})
            if doc:
                return RuleModel.from_dict(doc)
            return None
        except Exception as e:
            logger.error(f"❌ Error getting rule: {str(e)}")
            return None
    
    def get_all_rules(self) -> List[RuleModel]:
        """Get all rules"""
        try:
            docs = self.collection.find().sort("created_at", -1)
            return [RuleModel.from_dict(doc) for doc in docs]
        except Exception as e:
            logger.error(f"❌ Error getting all rules: {str(e)}")
            return []
    
    def get_all_rule_names(self) -> List[str]:
        """Get all rule names"""
        try:
            rules = self.get_all_rules()
            return [rule.name for rule in rules]
        except Exception as e:
            logger.error(f"❌ Error getting rule names: {str(e)}")
            return []
    
    def update_rule(self, name: str, rules: str, description: str = "") -> bool:
        """Update an existing rule"""
        try:
            result = self.collection.update_one(
                {"name": name},
                {
                    "$set": {
                        "rules": rules,
                        "description": description,
                        "updated_at": datetime.now()
                    }
                }
            )
            if result.modified_count > 0:
                logger.info(f"✅ Updated rule: {name}")
                return True
            else:
                logger.warning(f"⚠️ No changes made to rule: {name}")
                return False
        except Exception as e:
            logger.error(f"❌ Error updating rule: {str(e)}")
            return False
    
    def delete_rule(self, name: str) -> bool:
        """Delete a rule by name"""
        try:
            result = self.collection.delete_one({"name": name})
            if result.deleted_count > 0:
                logger.info(f"✅ Deleted rule: {name}")
                return True
            else:
                logger.warning(f"⚠️ Rule not found: {name}")
                return False
        except Exception as e:
            logger.error(f"❌ Error deleting rule: {str(e)}")
            return False
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("✅ MongoDB connection closed")

