import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI #type:ignore
from src.utils.logger import Logger

# Load environment variables
load_dotenv()

logger = Logger(__name__)

class LLMGemini:
    def __init__(self, llm_model_name:str = "gemini-2.0-flash"):
        # Get API key from environment
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            error_msg = "GOOGLE_API_KEY not found in environment variables. Please create a .env file with GOOGLE_API_KEY=your_api_key"
            logger.error(f"❌ {error_msg}")
            raise ValueError(error_msg)

        self.model_name = llm_model_name
        self.llm = ChatGoogleGenerativeAI(
            model=llm_model_name,
            google_api_key=api_key,
            temperature=0.0,
            top_p=0.85,
            top_k=20,
            max_tokens=None,
            max_output_tokens=250,
            verbose=True,
            disable_streaming=False,
            convert_system_message_to_human=True
        )
        self.name = self.llm.model
        logger.info(f"✅ LLM Gemini initialized with model: {llm_model_name}")


