# Overview

This project is a file transfer application created to deepen my understanding of network programming and socket communication. Using a client-server architecture, the application allows a client to upload, download, and list files on a remote server. This software showcases TCP-based communication with reliable data transmission and GUI interaction for file management.

The client-server setup involves starting the server on a separate environment (e.g., WSL or Linux) while the client runs on Windows, demonstrating cross-platform communication.

[Software Demo Video](https://youtu.be/kOAFxnDJr_o)

# Network Communication

- **Architecture**: Client-Server
- **Protocol**: TCP for reliable data transfer, using port `5000`
- **Message Format**: Plain text commands (`UPLOAD`, `DOWNLOAD`, `LIST`) and encoded filenames are exchanged between client and server. The server sends response messages to indicate the status of each operation, such as successful uploads or errors.

# Development Environment

- **IDE**: Visual Studio Code
- **Tools**: Python (for both client and server), Tkinter (for the client’s GUI), WSL (for running the server on Linux)
- **Language**: Python with `socket` library for networking and `tkinter` for GUI

# Useful Websites

- [Python Socket Programming](https://docs.python.org/3/library/socket.html)
- [Tkinter Documentation](https://docs.python.org/3/library/tkinter.html)

# Future Work

- Enhance error handling for network interruptions
- Implement authentication for file access
- Add encryption for secure file transfers
- Visually show which file has been clicked on
- Switch code block for choices in the server code
- Delete files from the server