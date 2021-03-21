import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import spotipy.util as util
import os
import datetime
import json


date_time = datetime.datetime.today() - datetime.timedelta(days=7)

def processAlbum(newAlbums, results, spotify):
    albums = results['items']
    while results['next']:
        results = spotify.next(results)
        albums.extend(results['items'])

    for album in albums:
        if (album['release_date'] > str(date_time)):
            newAlbums.append(album['id'])
    return newAlbums

def checkIfNewAlbums(artistId):
    artist = 'spotify:artist:' + artistId
    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

    newAlbums = []
    
    results = spotify.artist_albums(artist, album_type='album')
    newAlbums = processAlbum(newAlbums, results, spotify)
    
    results = spotify.artist_albums(artist, album_type='single')
    newAlbums = processAlbum(newAlbums, results, spotify)
    
    return newAlbums


def generateFollowingArtistIdList(scope):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    results = sp.current_user_followed_artists(limit=50)
    resultString = json.dumps(results)
    split = resultString.split('https://open.spotify.com/artist/')
    followedArtistsId = []


    for i in range (1, len(split)):
        id = split[i].split('\"')
        followedArtistsId.append(id[0])

    while len(split) > 1: 
        results = sp.current_user_followed_artists(limit=50, after=followedArtistsId[len(followedArtistsId) - 1])
        resultString = json.dumps(results)
        split = resultString.split('https://open.spotify.com/artist/')
        for i in range (1, len(split)):
            id = split[i].split('\"')
            followedArtistsId.append(id[0])
    return followedArtistsId

def createNewPlaylist(scope):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    user_id = sp.me()['id']
    playlistId = sp.user_playlist_create(user_id, 'New Songs for the Week')
    return playlistId

def makeSurePlaylistExists(scope, username):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    user_id = sp.me()['id']
    allPlaylists = []

    playlistId = None
    playlists = sp.user_playlists(username, limit = 50)

    for playlist in playlists['items']:
        allPlaylists.append(playlist['name'])
        if playlist['name'] == 'New Songs for the Week':
            playlistId = playlist

    while(len(playlists['items']) != 0 ):
        playlists = sp.user_playlists(username, limit = 50, offset = len(allPlaylists))

        for playlist in playlists['items']:
            allPlaylists.append(playlist['name'])
            if (playlist['name'] == 'New Songs for the Week'):
                playlistId = playlist
    if (playlistId != None):
        sp.current_user_unfollow_playlist(playlistId['id'])
    playlistId = createNewPlaylist(scope)
        
    return playlistId

def fillPlaylist(playlistId, albumId, artistId, scope):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    songArray = []

    results = sp.album_tracks(albumId)
    songs = results['items']

    while results['next']:
        results = sp.next(results)
        songs.extend(results['items'])

    for song in songs:
        songString = json.dumps(song)
        if str(artistId) in songString:
            songArray.append(song['id'])
    sp.playlist_add_items(playlistId, songArray)



def runScript(username):

    # username = "mr_q_5" # INSERT YOUR USERNAME HERE
    print(username)

    os.environ["SPOTIPY_CLIENT_ID"] = '67bafffe4ec743408a81a7ceb10106b5' # client id
    os.environ["SPOTIPY_CLIENT_SECRET"] = 'ac001e1fac7944e5a786637484adb5d1' # Secret ID
    os.environ["SPOTIPY_REDIRECT_URI"] = 'http://localhost:7777/callback' # Redirect URI

    client_credentials_manager = SpotifyClientCredentials(client_id="SPOTIPY_CLIENT_ID",client_secret="SPOTIPY_CLIENT_SECRET")
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    scope = 'playlist-modify-private playlist-modify-public user-follow-read user-library-read' # scope needed for your programme 
    token = util.prompt_for_user_token(username, scope)
    if token:
      sp = spotipy.Spotify(auth=token)
    else:
      return("Can't get token for " + username)
      quit()

    playlist = makeSurePlaylistExists(scope, username)
    playlistId = playlist["id"]

    artistId = '2AfU5LYBVCiCtuCCfM7uVX'

    followedArtistsId = generateFollowingArtistIdList(scope)
    for artistId in followedArtistsId:
      albumId = checkIfNewAlbums(artistId)
      # print(albumId)
      for album in albumId:
          fillPlaylist(playlistId, album, artistId, scope)
    print("Done")