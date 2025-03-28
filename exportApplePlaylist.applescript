-- Get the playlist name from the command line argument
on run argv
    try
        set playlistName to item 1 of argv
        set filePath to item 2 of argv

        -- Open the file for writing
        set txtFile to open for access file filePath with write permission

        -- Access the Music app
        tell application "Music"
            -- Find the playlist by name
            set targetPlaylist to first playlist whose name contains playlistName
            
            -- Iterate over all tracks in the playlist
            repeat with trackItem in (tracks of targetPlaylist)
                set trackName to name of trackItem
                set trackArtist to artist of trackItem

                -- Write the track info to the TXT file
                write trackName & linefeed & trackArtist & linefeed to txtFile
            end repeat
        end tell
        
        -- Close the file
        close access txtFile
    on error errMsg number errNum
        -- Log the error message and number to the console
        do shell script "echo 'Error: " & errMsg & " (Error Number: " & errNum & ")' >&2"
        try
            close access txtFile
        end try
    end try
end run