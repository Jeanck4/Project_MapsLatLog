import requests
import json

def get_location_by_address(rua, uf, cep):
    base_url = f"https://nominatim.openstreetmap.org/search?q={cep}%20{uf}%20{rua}&format=json&addressdetails=1"
    
    headers = {
     'User-Agent': 'MyAppName/1.0 (contact@example.com)'
    }
    response = requests.get(base_url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")
    if response.status_code == 200:
        try:
            return response.json()
        except json.JSONDecodeError:
            print("Erro ao decodificar a resposta JSON.")
            return None
    else:
        print(f"Erro na requisição: {response.status_code}")
        return None

# Função para salvar os dados em um arquivo JSON
def save_to_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

# Dados do endereço
rua = "ivo petters"
uf = "SC"
cep = "89135-000"

# Obter dados da API
location_data = get_location_by_address(rua, uf, cep)

if location_data:
    save_to_json(location_data, "C:/location_data.json")
else:
    print("Erro ao obter os dados da API.")
