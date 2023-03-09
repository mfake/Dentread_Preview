import json
import requests
headers = {"Authorization": "Bearer ya29.a0AVA9y1uxElRXnQyT9nFdxgFVpBA5P7xrTJvMJh2JfpPe_-OdhyYwMkBfI-XbrTXY5-w4GziJhfFbXNoLQyzKH360G5g6IXFCjdVFvjo17749zo1W6NbQvt5-QtwTB6yjWFFAVQcJzFwqgfyQFyzZkIG2mcJe"}
para = {
    "name": "rzp.csv",
}
files = {
    'data': ('metadata', json.dumps(para), 'application/json; charset=UTF-8'),
    'file': open("./rzp.csv", "rb")
}
r = requests.post(
    "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
    headers=headers,
    files=files
)
print(r.text)