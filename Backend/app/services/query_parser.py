class QueryParser_pre():
    
    def __init__(self):
        pass
    
    def extract_keywords(self):
        # Think about the user input, what keywords should be present within it...
        # street name, 
        # action/intent
        # damage level
        # comparison keyword, what exactly does it want me to do? compare locations, analyze specific locations
        # also think about the return schema, I want it to be an object I can easily read and handle so like {"locations": [], "action": "", "damageLevel": ""}
        pass
    
    def classify_intent(self):
        # This one should be a bit easier, I just need to determine the actions my chatbot can handle and plan accordingly, the idea is that I can either 
        # A) use some semantic search to compare input to the desired action and select the most similar one, and if distances exceed threshold then prompt the user which action to take
        # B) use a language model to map the input to one of my actions, also add to the prompt if none of them fit the input to return Null.
        
        
        # To test this out I will create a mock function that has the dataset of questions with the correct answer and then compare the results of both methods.
        # Will then use the accuracy to determine which one to choose.
        # Also I need to be sure I use async calls so it runs faster AND
        # I need to make a good prompt for it to judge and to improve result consistency, If I were to run it 100 times then I should get the same results 100 times.
        
        # I will probably use a structured output with the following schema
        # {
        #     "intent": "",
        #     "reasoning": ""
        # }
        # For every failure I will then examine the reasoning and improve my prompt based on the LLM' miunderstanding
        pass

# I need to plan out the actions the chatbot can do so far I have
# Analyze based on location (get general info for some street name, avg damage level, # of building damaged, etc)
# Compare two locations (Given 2 locations I need to be able to compare them)
# Also I can't expect the input to always be in the same format
# for example if asked "Is maple street more damaged than oak avenue" or "compare maple street and oak avenue" I should get 2 differnt answers the first one comparing the specific "damaged" buildings while the other one provides the gneral statistics of both locations.

import json
from enum import Enum
from typing import Dict, Any

from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate


class ChatIntent(Enum):
    GET_BUILDING_DAMAGE = "GET_BUILDING_DAMAGE"
    GET_STREET_SUMMARY = "GET_STREET_SUMMARY"
    GET_AREA_SUMMARY = "GET_AREA_SUMMARY"
    COMPARE_AREAS = "COMPARE_AREAS"
    GET_TOP_K = "GET_TOP_K"
    GET_OVERALL_STATS = "GET_OVERALL_STATS"
    GET_MODEL_EXPLANATION = "GET_MODEL_EXPLANATION"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"


class QueryParser:

    def __init__(self, model_name: str = "llama3.1:8b"):

        self.llm = ChatOllama(
            model=model_name,
            temperature=0
        )

        self.prompt = PromptTemplate(
            input_variables=["query"],
            template="""
You are a query parser for a disaster damage analysis chatbot.

Your job is to extract the user intent and parameters.

Valid intents:

GET_BUILDING_DAMAGE
GET_STREET_SUMMARY
GET_AREA_SUMMARY
COMPARE_AREAS
GET_TOP_K
GET_OVERALL_STATS
GET_MODEL_EXPLANATION
OUT_OF_SCOPE


Extraction rules:

Building Address:
- number + street name
Example: 123 Pine Street

Street:
Example: Maple Street, Oak Ave

Area:
Example: Zone A, Downtown, Neighborhood R

Damage levels:
destroyed
major
minor
none


Return JSON using this schema:

{{
  "intent": "",
  "addresses": [],
  "streets": [],
  "areas": [],
  "comparison_targets": [],
  "top_k": null,
  "damage_level": null
}}


Examples:

Query: What happened at 123 Pine Street?
Output:
{{
  "intent": "GET_BUILDING_DAMAGE",
  "addresses": ["123 Pine Street"],
  "streets": [],
  "areas": [],
  "comparison_targets": [],
  "top_k": null,
  "damage_level": null
}}

Query: Compare Zone A and Zone B
Output:
{{
  "intent": "COMPARE_AREAS",
  "addresses": [],
  "streets": [],
  "areas": [],
  "comparison_targets": ["Zone A", "Zone B"],
  "top_k": null,
  "damage_level": null
}}

Query: Top 5 hardest hit streets
Output:
{{
  "intent": "GET_TOP_K",
  "addresses": [],
  "streets": [],
  "areas": [],
  "comparison_targets": [],
  "top_k": 5,
  "damage_level": null
}}

Query: Why was 123 Pine Street classified as destroyed?
Output:
{{
  "intent": "GET_MODEL_EXPLANATION",
  "addresses": ["123 Pine Street"],
  "streets": [],
  "areas": [],
  "comparison_targets": [],
  "top_k": null,
  "damage_level": "destroyed"
}}

Now parse this query:

Query: {query}

Return ONLY JSON.
"""
        )

        self.chain = self.prompt | self.llm

    def parse(self, query: str) -> Dict[str, Any]:
        # TODO: I should try to use the LLM's strcuctured output rather than forcing it manually.
        raw = self._llm_parse(query)
        return self._normalize_output(raw)

    def _llm_parse(self, query: str) -> Dict[str, Any]:

        response = self.chain.invoke({"query": query})

        raw = response.content
        raw = raw.replace("```json", "").replace("```", "").strip()

        try:
            return json.loads(raw)
        except:
            return {"intent": "OUT_OF_SCOPE"}

    def _normalize_output(self, result: Dict[str, Any]) -> Dict[str, Any]:

        schema = {
            "intent": "OUT_OF_SCOPE",
            "addresses": [],
            "streets": [],
            "areas": [],
            "comparison_targets": [],
            "top_k": None,
            "damage_level": None
        }

        for key in schema:
            if key not in result:
                result[key] = schema[key]

        try:
            intent = ChatIntent(result["intent"])
        except:
            intent = ChatIntent.OUT_OF_SCOPE

        result["intent"] = intent.value

        if result["top_k"] is not None:
            try:
                result["top_k"] = int(result["top_k"])
            except:
                result["top_k"] = None

        return result