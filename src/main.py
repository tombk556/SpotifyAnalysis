import requests
import base64
import urllib.parse
from config import settings

CLIENT_ID = settings.client_id
CLIENT_SECRET = settings.client_secret

def get_access_token(client_id, client_secret):
    auth_url = "https://accounts.spotify.com/api/token"
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_header}"
    }
    data = {
        "grant_type": "client_credentials"
    }
    response = requests.post(auth_url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

def search_playlists(query, access_token, limit=50):
    api_url = "https://api.spotify.com/v1/search"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "q": query,
        "type": "playlist",
        "limit": limit
    }
    response = requests.get(api_url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def extract_playlist_urls(playlists_data):
    playlist_urls = []
    for item in playlists_data["playlists"]["items"]:
        playlist_id = item["id"]
        playlist_url = f"https://open.spotify.com/playlist/{playlist_id}"
        playlist_name = item["name"]
        print(f"Playlist Name: {playlist_name}")
        print(f"Playlist URL: {playlist_url}\n")
        playlist_urls.append({"name": playlist_name, "url": playlist_url})
    return playlist_urls

def main():
    access_token = get_access_token(CLIENT_ID, CLIENT_SECRET)
    
    search_query = "Top Hits of 1988"
    playlists_data = search_playlists(search_query, access_token)
    
    playlist_urls = extract_playlist_urls(playlists_data)
    
    with open("top_songs_playlists.txt", "w", encoding="utf-8") as f:
        for playlist in playlist_urls:
            f.write(f"{playlist["name"]}: {playlist["url"]}\n")
    print("Playlist URLs have been saved to top_songs_playlists.txt.")

if __name__ == "__main__":
    main()
