import os

from openai import AzureOpenAI

from dotenv import load_dotenv

def get_response(prompt):

    load_dotenv()

    client = AzureOpenAI(
        api_key=os.environ.get('AZURE_OPENAI_API_KEY_POC'),
        api_version= os.environ.get('API_VERSION_POC'),
        azure_endpoint=os.environ.get('AZURE_OPENAI_ENDPOINT_POC'),
    )

    response = client.chat.completions.create(
        model=os.environ.get('DEPLOYMENT_NAME_POC'),
        temperature=0.5,
        messages=[
            {
                "role": "user",  # Specify the role
                "content": prompt  # Pass the generated prompt here
            }]
    )

    response_content = response.choices[0].message.content

    return response_content