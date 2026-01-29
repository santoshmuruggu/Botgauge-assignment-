from client.kv_client import KVClient

client = KVClient("http://127.0.0.1:8000")

# Create
client.create("client_test", "hello")

# Get
client.get("client_test")

# Update
client.update("client_test", "updated")

# List
client.list(page=1, page_size=5)

# Delete
client.delete("client_test")

for _ in range(100):
    try:
        print(client.get("app_name"))
    except Exception as e:
        print("Error:", e)
