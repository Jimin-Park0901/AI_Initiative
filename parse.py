import os
from langchain.chat_models import ChatOpenAI
from langchain_ollama import OllamaLLM
from langchain.prompts.chat import ChatPromptTemplate
from langchain_core.prompts import ChatPromptTemplate

api_key = os.getenv("OPENAI_API_KEY")

template = (
    "You are tasked with extracting specific information from the following text content: {dom_content}. "
    "Please follow these instructions carefully: \n\n"
    "1. **Extract Information:** Only extract the information that directly matches the provided description: {parse_description}. "
    "2. **No Extra Content:** Do not include any additional text, comments, or explanations in your response. "
    "3. **Empty Response:** If no information matches the description, return an empty string ('')."
    "4. **Direct Data Only:** Your output should contain only the data that is explicitly requested, with no other text."
    "5. **Include every data** Try to include every data on website"
    # "6. **Add a column for engine code** Try to obtain engine code based on the engine information given."
)

model = ChatOpenAI(
    model="gpt-4o-mini",
    openai_api_key=api_key
)

def parse_with_chatgpt(dom_chunks, parse_description):
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model

    parsed_results = []
    for i, chunk in enumerate(dom_chunks, start=1):
        response = chain.invoke(
            {"dom_content": chunk, "parse_description": parse_description}
        )
        print(f"Parsed batch: {i} of {len(dom_chunks)}")
        parsed_results.append(response)

    return "\n".join(parsed_results)