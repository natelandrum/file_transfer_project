import socket
import threading
import os
from urllib.parse import unquote

# Ensure the server_files directory exists
if not os.path.exists("server_files"):
    os.makedirs("server_files")

def handle_client(connection):
    try:
        request = connection.recv(1024).decode()

        if not request:
            return

        command_parts = request.split(maxsplit=1)
        command = command_parts[0]
        filename = unquote(command_parts[1]) if len(command_parts) > 1 else ""

        if command == "UPLOAD":
            file_path = f"server_files/{filename}"

            # Check if the file already exists
            if os.path.exists(file_path):
                connection.send(b"File already exists. Overwrite?")
                overwrite_response = connection.recv(1024).decode()

                if overwrite_response.lower() != "yes":
                    connection.send(b"Upload canceled")
                    return

            # Notify client to start upload
            connection.send(b"Ready for upload")

            # Receive file data
            with open(file_path, "wb") as f:
                while True:
                    data = connection.recv(1024)
                    if not data:
                        break
                    f.write(data)

            connection.send(b"File uploaded successfully")

        elif command == "DOWNLOAD":
            file_path = f"server_files/{filename}"

            if os.path.exists(file_path):
                # Send the file size first
                file_size = os.path.getsize(file_path)
                connection.send(str(file_size).encode())

                # Wait for client's ready signal
                client_ready = connection.recv(1024).decode()
                if client_ready != "Ready to receive":
                    connection.send(b"Download canceled")
                    return

                # Send file data
                with open(file_path, "rb") as f:
                    while (data := f.read(1024)):
                        connection.send(data)
                connection.send(b"<EOF>")  # End of file signal
            else:
                connection.send(b"File not found")

        elif command == "DELETE":
            file_path = f"server_files/{filename}"

            if os.path.exists(file_path):
                os.remove(file_path)
                connection.send(b"File deleted successfully")
            else:
                connection.send(b"File not found")

        elif command == "LIST":
            files = os.listdir("server_files/")
            if files:
                file_list = "\n".join(files)
                connection.send(file_list.encode())
            else:
                connection.send(b"No files available")

        else:
            connection.send(b"Invalid request")

    except (ConnectionAbortedError, ConnectionResetError):
        print("Connection with client was lost.")
    except Exception as e:
        print(f"Server Error: {str(e)}")
    finally:
        connection.close()

def start_server(host='localhost', port=5000):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()

    print(f"Server listening on {host}:{port}")

    try:
        while True:
            connection, address = server_socket.accept()
            threading.Thread(target=handle_client, args=(connection,)).start()
    except KeyboardInterrupt:
        print("\nServer shutting down.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()
