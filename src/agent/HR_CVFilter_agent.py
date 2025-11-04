from src.utils.logger import Logger
logger = Logger(__name__)

import sys
import os
sys.path.append('../')
from src.llms.geminiLLM import LLMGemini
from src.prompt.context_builder import ContextBuilder
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.messages import HumanMessage, AIMessage


class HRCVFilterAgent:
    def __init__(self, llm_model_name: str = "gemini-2.0-flash"):
        self.llm = LLMGemini(llm_model_name)
        self.context_builder = ContextBuilder()
        self.chat_history = []
        self.tools = []
        logger.info("✅ HR CV Filter Agent initialized")

    def _create_agent_for_context(
        self,
        custom_rules: str = "",
        job_description: str = "",
        has_cv_data: bool = False
    ) -> AgentExecutor:
        """
        Create agent executor with dynamic context

        Args:
            custom_rules: Custom evaluation rules
            job_description: Job description context
            has_cv_data: Whether CV data is available

        Returns:
            AgentExecutor configured with current context
        """
        try:
            # Build prompt template with full context
            # Use absolute path to avoid file not found errors
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            prompt_path = os.path.join(base_dir, "prompt", "system_prompt.md")

            prompt = self.context_builder.build_context_v1(
                md_file_path=prompt_path,
                custom_rules=custom_rules,
                job_description=job_description,
                has_cv_data=has_cv_data
            )

            # Create tool calling agent
            agent = create_tool_calling_agent(self.llm.llm, self.tools, prompt)

            # Create agent executor
            agent_executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                verbose=False,
                handle_parsing_errors=True,
                max_iterations=3,
                return_intermediate_steps=True
            )

            logger.info("✅ Agent executor created with current context")
            return agent_executor

        except Exception as e:
            logger.error(f"❌ Error creating agent executor: {str(e)}")
            raise e

    def _convert_history_to_messages(self):
        """Convert chat history to LangChain messages format"""
        messages = []
        for item in self.chat_history:
            messages.append(HumanMessage(content=f"Evaluate CV: {item['cv_filename']}"))
            messages.append(AIMessage(content=item['evaluation']))
        return messages

    def evaluate_cv(
        self,
        cv_content: str,
        cv_filename: str = "",
        job_description: str = "",
        custom_rules: str = ""
    ) -> str:
        """
        Evaluate CV against job description

        Agent automatically reads all available fields and provides hints if missing.

        Args:
            cv_content: Extracted CV content
            cv_filename: Name of CV file
            job_description: Job description text (optional)
            custom_rules: Custom evaluation rules (optional)

        Returns:
            Evaluation result from agent
        """
        try:
            # Create agent with full context
            agent_executor = self._create_agent_for_context(
                custom_rules=custom_rules,
                job_description=job_description,
                has_cv_data=bool(cv_content)
            )

            # Format input with CV content
            input_text = f"""# Candidate CV
{cv_content}

Please evaluate this CV."""

            if job_description:
                input_text = f"""# Job Description
{job_description}

# Candidate CV
{cv_content}

Please evaluate this CV against the job description."""

            # Invoke agent executor
            result = agent_executor.invoke({
                "input": input_text,
                "chat_history": self._convert_history_to_messages()
            })
            response_content = result.get("output", "")

            # Add to chat history
            self.chat_history.append({
                "cv_filename": cv_filename,
                "evaluation": response_content
            })

            logger.info(f"✅ CV evaluation completed for {cv_filename}")
            return response_content

        except Exception as e:
            logger.error(f"❌ Error evaluating CV: {str(e)}")
            return f"Error evaluating CV: {str(e)}"

    def chat(
        self,
        message: str,
        job_description: str = "",
        custom_rules: str = ""
    ) -> str:
        """
        Chat with agent about CV evaluations

        Agent automatically reads all available fields and provides hints if missing.

        Args:
            message: User message
            job_description: Job description context (optional)
            custom_rules: Custom evaluation rules (optional)

        Returns:
            Agent response
        """
        try:
            # Create agent with full context
            agent_executor = self._create_agent_for_context(
                custom_rules=custom_rules,
                job_description=job_description,
                has_cv_data=bool(self.chat_history)
            )

            # Format input with context about previous evaluations
            input_text = message
            if self.chat_history:
                context = "Previous CV Evaluations:\n\n"
                for idx, item in enumerate(self.chat_history, 1):
                    cv_name = item.get('cv_filename', f'CV {idx}')
                    evaluation = item.get('evaluation', '')
                    context += f"CV {idx}: {cv_name}\n{evaluation[:200]}...\n\n"
                input_text = f"{context}\nUser Question: {message}"

            # Invoke agent executor
            result = agent_executor.invoke({
                "input": input_text,
                "chat_history": self._convert_history_to_messages()
            })
            response_content = result.get("output", "")

            logger.info(f"✅ Chat response generated \n {response_content}")
            return response_content

        except Exception as e:
            logger.error(f"❌ Error in chat: {str(e)}")
            return f"Error: {str(e)}"

    def clear_history(self):
        """Clear chat history"""
        self.chat_history = []
        logger.info("✅ Chat history cleared")
        