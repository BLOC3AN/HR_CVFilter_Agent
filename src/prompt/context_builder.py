import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.utils.logger import Logger
logger = Logger(__name__)

class ContextBuilder:

    def load_prompt(self, md_file_path: str) -> str:
        """
        Load prompt from markdown file

        Args:
            md_file_path: Path to markdown file

        Returns:
            Prompt content as string
        """
        try:
            with open(md_file_path, 'r', encoding='utf-8') as file:
                prompt_config = file.read()
            return prompt_config

        except Exception as e:
            logger.error(f"❌ Error loading prompt from Markdown: {str(e)}")
            return ""

    def build_context_v1(
        self,
        md_file_path: str,
        custom_rules: str = "",
        job_description: str = "",
        has_cv_data: bool = False
    ) -> ChatPromptTemplate:
        """
        Create prompt template for HR CV Filter Agent with dynamic context

        Args:
            md_file_path: Path to system prompt markdown file
            custom_rules: Custom evaluation rules to add to system prompt
            job_description: Job description context (optional)
            has_cv_data: Whether CV data is available

        Returns:
            ChatPromptTemplate with system prompt and placeholders
        """
        base_system_prompt = self.load_prompt(md_file_path)

        # Add custom rules to system prompt if provided
        if custom_rules:
            base_system_prompt += f"\n\n# Custom Evaluation Rules\n{custom_rules}"

        # Add job description context if provided
        if job_description:
            base_system_prompt += f"\n\n# Job Description Context\nThe following job description is available for reference:\n{job_description}"

        # Add hints if missing information
        hints = []
        if not job_description:
            hints.append("⚠️ No job description provided. Please ask the user to provide a job description for accurate CV evaluation.")
        if not has_cv_data:
            hints.append("⚠️ No CV data available yet. Please ask the user to upload CV files to begin evaluation.")

        if hints:
            base_system_prompt += f"\n\n# Important Notes\n" + "\n".join(hints)

        logger.info(f"[Context Builder] Building prompt template - Custom rules: {len(custom_rules)} chars, Job desc: {len(job_description)} chars, Has CV: {has_cv_data}")

        prompt = ChatPromptTemplate.from_messages([
            ("system", base_system_prompt),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        logger.info(f"✅ Prompt template created successfully")
        return prompt