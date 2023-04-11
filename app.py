from flask import Flask, request, url_for, session, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
from collections import Counter


app = Flask(__name__)

app.secret_key = "726HAJ278a"
app.config['SESSION_COOKIE_NAME'] = 'Thran Cookie'
TOKEN_INFO = "token_info"

@app.route('/')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    print(auth_url)
    return redirect(auth_url)


@app.route('/redirect')
def redirectPage():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('getTracks', _external=True))

key_map = {
    0: "C",
    1: "C#",
    2: "D",
    3: "D#",
    4: "E",
    5: "F",
    6: "F#",
    7: "G",
    8: "G#",
    9: "A",
    10: "A#",
    11: "B"
}

@app.route('/getTracks')
def getTracks():
    try:
        token_info = get_token()
    except:
        print("user not logged in")
        return redirect("/")
    sp = spotipy.Spotify(auth=token_info['access_token'])
    all_songs = []
    for i in range(0, 5): # 5 requests to get 250 songs (50 songs per request)
        results = sp.current_user_top_tracks(limit=50, offset=i*50, time_range='medium_term')
        all_songs += results['items']
        if len(results['items']) == 0:
            break
    tempos = []
    keys = []
    track_tempo_map = {}
    for item in all_songs:
        track = item
        track_info = sp.audio_features(track['id'])[0]
        tempo = track_info['tempo']
        tempos.append(tempo)
        keys.append(track_info['key'])
        track_tempo_map[track['name'] + " - " + track['artists'][0]['name']] = tempo
    avg_tempo = sum(tempos) / len(tempos)
    most_common_key_num = Counter(keys).most_common(1)[0][0]
    most_common_key_letter = key_map[most_common_key_num]
    least_common_key_num = Counter(keys).most_common()[-1][0]
    least_common_key_letter = key_map[least_common_key_num]
    slowest_track = min(track_tempo_map, key=track_tempo_map.get)
    fastest_track = max(track_tempo_map, key=track_tempo_map.get)
    tracks = []
    for item in all_songs:
        track = item
        track_info = sp.audio_features(track['id'])[0]
        key_num = track_info['key']
        key_letter = key_map[key_num]
        tracks.append(track['name'] + " - " + track['artists'][0]['name'] + " (" + key_letter + ") " + "tempo: " + str(track_info['tempo']))

    return "<br>".join(tracks) + "<br><br>" + "Average tempo: " + str(avg_tempo) + "<br>" + "Most common key: " + most_common_key_letter + "<br>" + "Least common key: " + least_common_key_letter + "<br>" + "Slowest track: " + slowest_track + "<br>" + "Fastest track: " + fastest_track

def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        raise "exception"
    now = int(time.time())

    is_expired = token_info['expires_at'] - now < 60
    if (is_expired):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info


def create_spotify_oauth():
    return SpotifyOAuth(
            client_id = "d3b9d0f9971740c78967e8efa66d9f6a",
            client_secret = "369405ab4ddf4c1ba2f055d04aeb1cd5",
            redirect_uri = "https://35.91.236.86//redirect",
            scope = "user-library-read user-top-read")

if __name__ == '__main__':
    app.run()
    