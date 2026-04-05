from openai import OpenAI

OPENROUTER_API_KEY="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"
client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=OPENROUTER_API_KEY,
)

# First API call with reasoni₹ng
response = client.chat.completions.create(
  model="stepfun/step-3.5-flash:free",
  messages=[
          {
            "role": "user",
            "content": "give me a learning paragraph on machine learning"
          }
        ],
  extra_body={"reasoning": {"enabled": True}}
)

# Extract the assistant message with reasoning_details
response = response.choices[0].message.content
print(response)