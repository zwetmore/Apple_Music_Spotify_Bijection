## **Spotify Playlist Transfer Tool**  

### **Overview**  
This project was created to solve a real-world problem: I wanted to switch from Apple Music to Spotify, but I needed to transfer **5,000+ songs and 55+ playlists**. Manually migrating this data would have been an extremely time-consuming process, so I developed this **automated solution** to streamline the transition.  

### **Key Features**  
- **Automates playlist and song migration** in a bidirectional relationship between Spotify and Apple Music
- **Utilizes AppleScripts** to extract and recreate playlists  
- **Optimized for efficiency**, reducing what would have taken weeks to just minutes  

### **Future Improvements**  
While this tool is currently tailored to my needs, it has the potential to be **more portable and user-friendly** with further development. Enhancing cross-platform compatibility and improving setup automation are possible next steps. Additionally, implementing a GUI for those that are unfamiliar with python or lack coding experience. 

### **Setup Instructions**  
Before running the app, some initial setup is required to **authenticate Spotify and Apple Music accounts**. The following commands compile the necessary AppleScripts:  

```sh  
osacompile -o exportApplePlaylist.scpt exportApplePlaylist.applescript  
osacompile -o createApplePlaylist.scpt createApplePlaylist.applescript
```
