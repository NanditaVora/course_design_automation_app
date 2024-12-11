import ollama

def get_response(prompt):
    response = ollama.chat(model='llama3.1',
                           messages=[
        {
            'role': 'user',
            'content': prompt,
        },

    ])
    return response['message']['content']

if __name__ == "main":
    get_response('what is rgb')