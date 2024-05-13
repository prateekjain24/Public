from groq import Groq
from fastapi import HTTPException
import os

def call_groq_api(prompt, model, max_tokens, temperature, system_instructions):
    client = Groq(
    # This is the default and can be omitted
    api_key=os.environ.get("GROQ_API_KEY"),
    )

    try:
        messages=[
        {"role": "system", "content": f"{system_instructions}. You are working for PropertyGuru."},
        {"role": "user", "content": f"{prompt}"}
          ]
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            # user="your-user-id"  # Replace 'your-user-id' with appropriate user identification if necessary
        )
        return response.choices[0].message.content, int(response.usage.prompt_tokens), int(response.usage.completion_tokens)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API call failed: {str(e)}")
