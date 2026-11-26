import requests

urls = [
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg/1280px-Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/e/ea/Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg",
    "https://commons.wikimedia.org/wiki/Special:FilePath/Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg",
    "https://commons.wikimedia.org/wiki/Special:Redirect/file/Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg",
]
uas = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "LETI-Coursework/1.0 (https://etu.ru; student@etu.ru) requests/2.32",
]
for url in urls:
    for ua in uas:
        try:
            r = requests.get(url, headers={"User-Agent": ua, "Accept": "image/*,*/*"},
                             timeout=90, allow_redirects=True)
            print(f"{r.status_code} {len(r.content):>9} ua={ua[:28]!r} {url[:80]}")
            if r.ok and r.content[:2] == b"\xff\xd8":
                print("   JPEG OK")
        except Exception as exc:  # noqa: BLE001
            print("ERR", exc)
