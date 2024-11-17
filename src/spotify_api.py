import base64
import requests
import pandas as pd



class PlaylistData:
    def __init__(self, client_id: str, client_secret: str, playlist_url: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.playlist_url = playlist_url

    def extract_track_metadata(self) -> pd.DataFrame:
        tracks = self._get_playlist_tracks()
        titles = []
        artists = []
        albums = []
        release_dates = []
        durations = []

        for item in tracks:
            track = item['track']
            if track:
                title = track.get('name')
                artist = ', '.join([artist['name']
                                   for artist in track.get('artists', [])])
                album = track.get('album', {}).get('name')
                release_date = track.get('album', {}).get('release_date')
                duration_ms = track.get('duration_ms')

                titles.append(title)
                artists.append(artist)
                albums.append(album)
                release_dates.append(release_date)
                durations.append(duration_ms)

        df = pd.DataFrame({
            "title": titles,
            "artist": artists,
            "album": albums,
            "release_date": release_dates,
            "duration": durations
        })

        return df

    def _get_playlist_tracks(self) -> list:
        playlist_id = self._extract_playlist_id()
        access_token = self._get_access_token()
        api_url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        params = {
            'limit': 100,
            'offset': 0
        }
        tracks = []
        while True:
            response = requests.get(api_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            tracks.extend(data['items'])
            if data['next']:
                api_url = data['next']
            else:
                break
        return tracks

    def _extract_playlist_id(self) -> str:
        if 'playlist/' in self.playlist_url:
            playlist_id = self.playlist_url.split('playlist/')[1].split('?')[0]
            return playlist_id
        else:
            raise ValueError("Invalid playlist URL.")

    def _get_access_token(self) -> str:
        auth_url = 'https://accounts.spotify.com/api/token'
        auth_header = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()).decode()
        headers = {
            'Authorization': f'Basic {auth_header}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'grant_type': 'client_credentials'
        }
        response = requests.post(auth_url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()['access_token']
