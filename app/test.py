import os
from groq import Groq


client = Groq(

    api_key="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",

)

chat_completion = client.chat.completions.create(

    messages=[

        {

            "role": "user",

            "content": "Explain the importance of fast language models",

        }

    ],

    model="llama-3.1-8b-instant",

)


print(chat_completion.choices[0].message.content)