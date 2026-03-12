import os
from dotenv import load_dotenv

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()


class LLMService:
    """
    LangChain-based LLM service using Ollama.
    Returns plain text responses.
    """

    def __init__(self, model: str | None = None, temperature: float = 0.3, max_tokens: int = 300):
        self.model_name = model or os.getenv("LLM_MODEL", "llama3.1:8b")

        self.llm = ChatOllama(
            model=self.model_name,
            temperature=temperature,
            # num_predict=max_tokens,
        )

        self.system_prompt = (
            "You are a disaster damage assessment assistant. "
            "You have access to a database of building damage assessments. "
            "Answer user questions using ONLY the provided context. "
            "If the context does not contain relevant information, say so clearly. "
            "Be concise but informative. Include statistics when possible."
        )

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "Context:\n{context}\n\nQuestion:\n{question}")
        ])

        self.chain = self.prompt | self.llm

    async def call_with_context(self, user_query: str, context: str) -> str:
        """
        Returns plain text response from Ollama.
        """

        try:
            response = await self.chain.ainvoke({
                "context": context,
                "question": user_query
            })

            return response.content

        except Exception as e:
            print(f"LLM call failed: {e}")
            return "Sorry, I encountered an error processing your request."