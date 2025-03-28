from functions import *
def main():
    while True:
        # prompt user for desired action
        prompt = f'\nWhat would you like to do?\n 1 = import apple playlist\n 2 = import spotify playlist\n'
        prompt += f' 3 = create apple playlist\n 4 = create spotify playlist\n 5 = like songs within playlist\n 6 = exit\n\nEnter your choice: '
        action = input(prompt)

        if action == '1':
            while True:
                importApplePlaylist()
                if int(input('Import another playlist? \n1 = Yes\n 2 = No \n')) == 2:
                    break
        elif action == '2':
            importSpotifyPlaylist()
        elif action == '3':
            createApplePlaylist()
        elif action == '4':
            while True:
                createSpotifyPlaylist()
                poll = int(input('Create another playlist? \n1 = Yes\n2 = No \n'))
                if poll == 2:
                    break
        elif action == '5':
            likeSongsWithinPlaylist()
        elif action == '6':
            Clean_Created_Playlists()
            return

if __name__ == '__main__':
    main()
