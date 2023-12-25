import requests

base_url = 'http://localhost:8000'

process_images_url = f'{base_url}/process-images'
add_user_tag_url = f'{base_url}/add-user-tag'
feedback_on_tags_url = f'{base_url}/feedback-on-tags'
add_description_url = f'{base_url}/add-description'

image_paths = ["C:\\Users\\Erykoo\\Downloads\\eryk.jpg",
               "C:\\Users\\Erykoo\\Downloads\\krzys.jpg",
               "C:\\Users\\Erykoo\\Downloads\\jake.jpg"]

files = [('images', (path.split('\\')[-1], open(path, 'rb'))) for path in image_paths]

response = requests.post(process_images_url, files=files)
inserted_ids = response.json().get('inserted_ids', [])
print(inserted_ids)

for inserted_id in inserted_ids:
    tag_data = {
        'inserted_id': inserted_id,
        'tags': ['example_tag1', 'example_tag2']
    }
    response = requests.post(add_user_tag_url, data=tag_data)
    print(f'Add Tag Response for {inserted_id}: {response.json()}')

for inserted_id in inserted_ids:
    feedback_data = {
        'inserted_id': inserted_id,
        'feedback': {'example_tag1': True, 'example_tag2': False}
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f'{base_url}/feedback-on-tags', json=feedback_data, headers=headers)
    print(f'Feedback Response for {inserted_id}: {response.json()}')


for inserted_id in inserted_ids:
    description_data = {
        'inserted_id': inserted_id,
        'description': 'This is a description'
    }
    response = requests.post(add_description_url, data=description_data)
    print(f'Add Description Response for {inserted_id}: {response.json()}')
