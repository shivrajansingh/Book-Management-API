import os 
from groq import Groq


def summarize(prompt):
    try:
        print(os.environ.get("GROQ_API_KEY"))
        client = Groq(
            api_key=os.environ.get("GROQ_API_KEY"),
        )
        messages = [
            { "role" : "system", "content" : "You are a summarizer, which creates the equivalent summary of the given text, omit the introductory text" },
            { "role": "user", "content": prompt}
            ]
                
        chat_completion = client.chat.completions.create(
            messages=messages,model="llama-3.1-8b-instant")
        print(chat_completion)
        return chat_completion.choices[0].message.content
    except Exception as e:
        return False
