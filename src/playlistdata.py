import base64
import requests
import pandas as pd

class PlaylistDataSong:
    def __init__(self, client_id: str, client_secret: str, playlist_url: str):
        """
        Initializes the PlaylistData object with Spotify API credentials and playlist URL.
        Caches the access token for subsequent API calls.
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.playlist_url = playlist_url
        self.access_token = self._get_access_token()

    def get_full_track_data(self) -> pd.DataFrame:
        """
        Retrieves the full track data, including metadata and audio features,
        and returns it as a pandas DataFrame.
        """
        track_metadata_df = self.extract_track_metadata()
        audio_features_df = self.extract_audio_features(track_metadata_df['track_id'].tolist())
        full_df = pd.merge(track_metadata_df, audio_features_df, left_on='track_id', right_on='id')
        
        return full_df

    def extract_track_metadata(self) -> pd.DataFrame:
        """
        Extracts track metadata from the specified Spotify playlist.
        Returns a pandas DataFrame containing track metadata.
        """
        tracks = self._get_playlist_tracks()
        titles = []
        artists = []
        albums = []
        release_dates = []
        durations = []
        track_ids = []
        track_uris = []

        for item in tracks:
            track = item['track']
            if track:
                title = track.get('name')
                artist = ', '.join([artist['name'] for artist in track.get('artists', [])])
                album = track.get('album', {}).get('name')
                release_date = track.get('album', {}).get('release_date')
                duration_ms = track.get('duration_ms')
                track_id = track.get('id')
                track_uri = track.get('uri')

                titles.append(title)
                artists.append(artist)
                albums.append(album)
                release_dates.append(release_date)
                durations.append(duration_ms)
                track_ids.append(track_id)
                track_uris.append(track_uri)

        df = pd.DataFrame({
            "title": titles,
            "artist": artists,
            "album": albums,
            "release_date": release_dates,
            "duration_ms": durations,
            "track_id": track_ids,
            "track_uri": track_uris
        })

        return df

    def extract_audio_features(self, track_ids: list) -> pd.DataFrame:
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        audio_features_list = []
        for i in range(0, len(track_ids), 100):
            ids = ','.join(track_ids[i:i+100])
            api_url = 'https://api.spotify.com/v1/audio-features'
            params = {'ids': ids}
            response = requests.get(api_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            # Extend the list with audio features
            audio_features_list.extend(data['audio_features'])
        # Filter out None values
        audio_features_list = [af for af in audio_features_list if af is not None]
        audio_features_df = pd.DataFrame(audio_features_list)
        return audio_features_df


    def _get_playlist_tracks(self) -> list:
        """
        Retrieves all track items from the specified Spotify playlist.
        Handles pagination to fetch playlists with more than 100 tracks.
        Returns a list of track items.
        """
        playlist_id = self._extract_playlist_id()
        api_url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
        headers = {
            'Authorization': f'Bearer {self.access_token}'
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
        """
        Extracts the playlist ID from the playlist URL.
        """
        if 'playlist/' in self.playlist_url:
            playlist_id = self.playlist_url.split('playlist/')[1].split('?')[0]
            return playlist_id
        else:
            raise ValueError("Invalid playlist URL.")

    def _get_access_token(self) -> str:
        """
        Obtains an access token from Spotify using Client Credentials Flow.
        """
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
