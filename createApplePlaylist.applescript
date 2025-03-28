on run argv
    -- Get arguments: new playlist name and path to text file
    set playlistName to item 1 of argv
    set txtFilePath to item 2 of argv

    -- Open the text file
    set txtFile to open for access txtFilePath
    set txtContents to read txtFile
    close access txtFile

    -- Split text file into lines
    set txtLines to paragraphs of txtContents

    -- Create a new playlist in the Music app
    tell application "Music"
        -- Check if the playlist exists, create if not
        if not (exists playlist playlistName) then
            set newPlaylist to make new playlist with properties {name:playlistName}
        else
            set newPlaylist to playlist playlistName
        end if

        -- Process songs in chunks of 3 lines (Track, Album, Artist)
        repeat with i from 1 to (count of txtLines) by 2
            try
                -- Extract track, album, and artist from the current 3 lines
                set trackName to item i of txtLines
                set artistName to item (i + 1) of txtLines

                -- Find the track in the Music library
                set foundTrack to first track of library playlist 1 whose name contains trackName and artist contains artistName
                
                -- Duplicate the found track to the new playlist
                duplicate foundTrack to newPlaylist
            on error errMsg
                log "Error with song: Track=" & trackName & ", Artist=" & artistName & " - " & errMsg
            end try
        end repeat
    end tell
end run
