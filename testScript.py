import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import spotipy.util as util
import os
import datetime


date_time = datetime.datetime.today() - datetime.timedelta(days=7)

def processAlbum(newAlbums, results, spotify):
    albums = results['items']
    while results['next']:
        results = spotify.next(results)
        albums.extend(results['items'])

    for album in albums:
        if (album['release_date'] > str(date_time)):
            newAlbums.append(album['id'])
        else:
            return newAlbums
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


def generateFollowingArtistIdList(sp):
    followedArtistsId = []
    
    results = sp.current_user_followed_artists(limit=50)
    listOfA = results['artists']
    next = listOfA['cursors']['after']
    x = listOfA['items']
    for i in x:
        followedArtistsId.append(i['id'])
    
    while next != None:
        results = sp.current_user_followed_artists(limit=50, after=next)
        listOfA = results['artists']
        next = listOfA['cursors']['after']
        x = listOfA['items']
        for i in x:
            followedArtistsId.append(i['id'])
            
    return followedArtistsId

def createNewPlaylist(sp):
    user_id = sp.me()['id']
    playlistId = sp.user_playlist_create(user_id, 'Extended Release Radar')
    return playlistId

def makeSurePlaylistExists(sp, username):
    user_id = sp.me()['id']
    allPlaylists = []

    playlistId = None
    playlists = sp.user_playlists(username, limit = 50)

    for playlist in playlists['items']:
        allPlaylists.append(playlist['name'])
        if playlist['name'] == 'Extended Release Radar':
            playlistId = playlist

    while(len(playlists['items']) != 0 ):
        playlists = sp.user_playlists(username, limit = 50, offset = len(allPlaylists))

        for playlist in playlists['items']:
            allPlaylists.append(playlist['name'])
            if (playlist['name'] == 'Extended Release Radar'):
                playlistId = playlist
    if (playlistId != None):
        sp.current_user_unfollow_playlist(playlistId['id'])
    playlistId = createNewPlaylist(sp)
        
    return playlistId

def fillPlaylist(playlistId, albumId, artistId, sp):
    songArray = []
    # print("Hello")
    
    results = sp.album_tracks(albumId)
    songs = results['items']

    while results['next']:
        results = sp.next(results)
        songs.extend(results['items'])

#         Makes sure that only songs with the artist are added to the playlist
    for song in songs:
        for artist in song['artists']:
            if(artist['id'] == artistId):
                songArray.append(song['id'])
    
    sp.playlist_add_items(playlistId, songArray)



def runScript(username):

    # username = "mr_q_5" # INSERT YOUR USERNAME HERE
    print(username)



    scope = 'playlist-modify-private playlist-modify-public user-follow-read user-library-read' # scope needed for your programme 
    token = util.prompt_for_user_token(username, scope)
    
    if token:
        sp = spotipy.Spotify(auth=token)
    else:
      return("Can't get token for " + username)
      quit()

    playlist = makeSurePlaylistExists(sp, username)
    playlistId = playlist["id"]

    artistId = '2AfU5LYBVCiCtuCCfM7uVX'

    followedArtistsId = generateFollowingArtistIdList(sp)
    for artistId in followedArtistsId:
      albumId = checkIfNewAlbums(artistId)
      # print(albumId)
      for album in albumId:
          fillPlaylist(playlistId, album, artistId, sp)
    print("Done")

def test(username):
    return username
