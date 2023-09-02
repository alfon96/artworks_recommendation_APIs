import asyncio
import httpx
import itertools

jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyIiwiZXhwIjoxNjg5MjM4OTU5fQ.cE6DlPsuy8cJhVjljRlTL3cpz2LK-evvnWIfvSCtNwM"
# List of user IDs and content IDs
user_ids = [i for i in range(1, 10)]
content_ids = [i for i in range(1, 400)]
ports = [i for i in range(80, 90)]

def save_list_of_tuples(filename, data):
    with open(filename, 'w') as file:
        for item in data:
            line = ','.join(str(element) for element in item)
            file.write(line + '\n')
    print(f"The data has been saved to {filename}.")


async def make_api_call(client, url, params,port):
    headers = {'Authorization': f'Bearer {jwt}'}
    try:
        response = await client.get(url, params=params, headers=headers)
        return response.status_code, params['user_id'], params['content_id'], port
    except Exception :
         print(f"User: {params['user_id']}, content: {params['content_id']}, failed assertion")
         return [(f"User: {params['user_id']}, content: {params['content_id']}, failed assertion")]

async def run_api_calls():
    tasks = []
    async with httpx.AsyncClient(timeout=30.0, limits=httpx.Limits(max_connections=100, max_keepalive_connections=150)) as client:
        for idx, (user_id, content_id) in enumerate(itertools.product(user_ids, content_ids)):
            port = ports[idx % len(ports)]
            url = f'http://127.0.0.1:{port}/mdl/recommendation_by_content'
            params = {
                'n_rcm': 3,
                'user_id': user_id,
                'content_id': content_id
            }
            task = asyncio.create_task(make_api_call(client, url, params,port))
            tasks.append(task)

            results = await asyncio.gather(*tasks)
            await asyncio.sleep(0.001) 

        # Process the results
        save_list_of_tuples(filename="log_api_responses.txt", data=results)

asyncio.run(run_api_calls())

print("Done")


# 3 369

# import os

# # List of port values
# port_values = [i for i in range(80,90)]  # Add or modify the port values as needed

# # Base Dockerfile content
# dockerfile_content = '''
# FROM python:3.9.4

# WORKDIR /app

# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# COPY . .

# RUN apt-get update && \\
#     apt-get install -y fontconfig

# RUN fc-cache -f -v

# ENV debug=false
# ENV PORT={port}

# EXPOSE {port}

# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "{port}"]
# '''

# # Create Dockerfiles with different port values
# for port in port_values:
#     dockerfile = dockerfile_content.format(port=port)
#     with open(f'Dockerfile_{port}', 'w') as file:
#         file.write(dockerfile)

#     print(f'Dockerfile-{port} created.')

# print('Dockerfiles created successfully.')
