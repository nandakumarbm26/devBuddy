import openai
import os, json
from typing import List, Dict, Any

from dotenv import load_dotenv
load_dotenv() 



NEXSUS_API_ENDPOINT, NEXSUS_API_KEY, NEXSUS_DEPLOYMENT_NAME = os.getenv("NEXSUS_API_ENDPOINT"), os.getenv("NEXSUS_API_KEY"), os.getenv("NEXSUS_DEPLOYMENT_NAME")
if not NEXSUS_API_ENDPOINT or not NEXSUS_API_KEY or not NEXSUS_DEPLOYMENT_NAME: 
    raise ValueError("Please set the NEXSUS_API_ENDPOINT, NEXSUS_API_KEY, and NEXSUS_DEPLOYMENT_NAME environment variables")


nexus_api_key = NEXSUS_API_KEY
azure_endpoint = NEXSUS_API_ENDPOINT
deployment_name = NEXSUS_DEPLOYMENT_NAME

if not nexus_api_key or not azure_endpoint or not deployment_name:
    raise ValueError("Please set the NEXSUS_API_KEY, NEXSUS_API_ENDPOINT, and NEXSUS_DEPLOYMENT_NAME environment variables")

class Nexus:
    def __init__(self, api_key: str=nexus_api_key, endpoint: str=azure_endpoint, deployment_name: str=deployment_name, api_version: str = "2023-03-15-preview"):
        """
        Initializes the Azure OpenAI wrapper.

        :param api_key: Azure OpenAI API Key
        :param endpoint: Azure OpenAI endpoint URL
        :param deployment_name: The model deployment name in Azure OpenAI
        :param api_version: API version (default: "2023-03-15-preview")
        """
        self.client = openai.AzureOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=api_version
        )
        self.deployment_name = deployment_name
    
    def chat_completion(self, messages: List[Dict[str, str]], max_tokens: int = 4096, temperature: float = 0.7) -> Dict[str, Any]:
        """
        Generates a chat response using Azure OpenAI.

        :param messages: List of messages in the format [{'role': 'user', 'content': 'Hello'}]
        :param max_tokens: Maximum tokens to generate
        :param temperature: Controls randomness (0: deterministic, 1: creative)
        :return: API response as a dictionary
        """
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.model_dump()
        except Exception as e:
            return {"error": str(e)}
    
    def generate_embedding(self, input_text: str) -> Dict[str, Any]:
        """
        Generates an embedding for the given text.

        :param input_text: The input text to embed
        :return: API response as a dictionary
        """
        try:
            response = self.client.embeddings.create(
                model=self.deployment_name,
                input=input_text
            )
            return response.model_dump()
        except Exception as e:
            return {"error": str(e)}


def generate_text(prompt):
    ai = Nexus()

    response = ai.chat_completion([
        {"role": "system", "content": "You are a useful agent. Answer concisely and up to the point."},
        {"role": "user", "content": prompt}
    ])
    return response['choices'][0]['message']['content']

def generate_code_change(issue_title, issue_body, files_tree, file_content):
    prompt = f"""
    You are a helpful and experienced developer assistant. Your task is to generate code updates based on the issue provided below.

    Issue Title:
    {issue_title}

    Issue Description:
    {issue_body}

    Instructions:
    - Based on the provided issue, suggest relevant code updates.
    - Your response should strictly follow the specified JSON format.
    - Do not include any explanations or additional text—only the valid JSON output.

    Format:
    Return a list of objects, each with the following keys:
    - "filename": Name of the file to be created or modified.
    - "content": Full content of the file after applying the necessary changes.
    - "path": File path relative to the project root.

    Example:
    [
    {{
        "filename": "example.py",
        "content": "# updated file content here",
        "path": "src/utils"
    }}
    ]

    Please ensure all changes are consistent with the existing file tree and contents provided.
    """
    ai = Nexus()

    response = ai.chat_completion([
        {"role": "system", "content": "You write Python code updates."},
        {"role": "system", "content": f"Here is the file tree:\n{files_tree}"},
        {"role": "system", "content": f"Here are the file contents:\n{file_content}"},
        {"role": "system", "content": "Respond only in valid JSON format as described in the prompt."},
        {"role": "user", "content": prompt}
    ])
    print(response)
    return response['choices'][0]['message']['content']
