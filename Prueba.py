import requests
from PIL import Image
import io

response = requests.get('http://localhost:5099/retrotrack/api/GameSessions/1/screenshot')

if response.status_code == 200:
    image = Image.open(io.BytesIO(response.content))
    image.show()
else:
    print("No se pudo recuperar la imagen")