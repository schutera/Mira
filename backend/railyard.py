import pandas as pd
from llm_interface import query_gpt

def load_all_responses():
    filename = "datasets/synthesis_qid16.csv"
    df = pd.read_csv(filename)
    # Try to find the column with responses (commonly 'English Responses')
    response_col = None
    for col in df.columns:
        if "response" in col.lower():
            response_col = col
            break
    if response_col is None:
        raise ValueError("No response column found in the CSV.")
    all_responses = df[response_col].dropna().tolist()
    return all_responses

def derive_guardrail_prompt(responses):
    joined_responses = "\n".join([f"- {resp}" for resp in responses])
    prompt = (
        "Analyze the following user inputs to identify the underlying values and principles that should guide an AI assistant's behavior. "
        "Based on these values, create a detailed and actionable prompt for another LLM. "
        "This prompt must include explicit instructions, constraints, and examples to ensure the LLM's outputs are consistently aligned with the identified values and principles. "
        "The actionable prompt should be structured in a way that clearly influences the LLM's behavior and decision-making process.\n\n"
        "User inputs:\n"
        f"{joined_responses}\n\n"
        "Your task: Provide the actionable LLM prompt, ensuring it is specific, clear, and enforceable."
    )
    return query_gpt(prompt)


if __name__ == "__main__":
    # Example usage
    responses = load_all_responses()
    prompt = derive_guardrail_prompt(responses)
    output_filename = "backend/guardrail_prompt.csv"
    pd.DataFrame({"Prompt": [prompt]}).to_csv(output_filename, index=False)
    print(f"Prompt saved to {output_filename}")
