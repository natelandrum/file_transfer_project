import os
import socket
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from urllib.parse import quote

# Function to clear the console
def clear_console(console):
    console.delete(1.0, tk.END)

# Function to send a file to the server
def send_file(server_address, console, progress_bar, upload_button, list_button, download_button, exit_button):
    clear_console(console)  # Clear console for a new action
    download_button.pack_forget()  # Hide the download button

    filename = filedialog.askopenfilename()
    if not filename:
        return

    # Disable buttons while the upload is in progress
    upload_button.config(state=tk.DISABLED)
    list_button.config(state=tk.DISABLED)
    exit_button.config(state=tk.DISABLED)

    file_size = os.path.getsize(filename)  # Get the total file size
    progress_bar["value"] = 0  # Reset progress bar
    progress_bar["maximum"] = file_size  # Set the progress bar maximum to the file size

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(server_address)

        # Use `quote` to encode the file name to handle spaces and special characters
        client_socket.send(f"UPLOAD {quote(filename.split('/')[-1])}".encode())  # Send the encoded filename

        # Check server response to see if the file exists
        response = client_socket.recv(1024).decode()
        if response == "File already exists. Overwrite?":
            overwrite = messagebox.askyesno("File Exists", "File already exists on the server. Overwrite?")
            if overwrite:
                client_socket.send(b"yes")  # Send overwrite confirmation
            else:
                client_socket.send(b"no")  # Send cancel message
                console.insert(tk.END, "Upload canceled by user.\n")
                client_socket.close()
                return  # Skip the upload

        # Proceed with the file upload
        total_sent = 0
        with open(filename, "rb") as f:
            data = f.read(1024)
            while data:
                client_socket.send(data)
                total_sent += len(data)
                progress_bar["value"] = total_sent  # Update the progress bar
                progress_bar.update()  # Force the GUI to update
                data = f.read(1024)

        client_socket.shutdown(socket.SHUT_WR)  # Gracefully shut down the write side of the socket

        # Now, receive the confirmation message from the server
        response = client_socket.recv(1024).decode()  # Only decode control messages (not file content)
        console.insert(tk.END, f"Upload Status: {response}\n")

    except Exception as e:
        console.insert(tk.END, f"Error: {str(e)}\n")
    finally:
        client_socket.close()

        # Re-enable the buttons once the upload is complete
        upload_button.config(state=tk.NORMAL)
        list_button.config(state=tk.NORMAL)
        exit_button.config(state=tk.NORMAL)


# Function to download a file from the server
def download_file(server_address, console, filename, download_button, progress_bar, upload_button, list_button, exit_button):
    clear_console(console)  # Clear console for a new action
    download_path = filedialog.askdirectory()  # Ask for the download location
    if not download_path:
        return

    # Disable buttons while the download is in progress
    download_button.config(state=tk.DISABLED)
    upload_button.config(state=tk.DISABLED)
    list_button.config(state=tk.DISABLED)
    exit_button.config(state=tk.DISABLED)

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(server_address)

        client_socket.send(f"DOWNLOAD {quote(filename)}".encode())  # Send the encoded filename

        # Receive the file size as a control message
        file_size_message = client_socket.recv(1024).decode()  # Expect the file size as a string
        file_size = int(file_size_message)  # Convert the file size to integer

        progress_bar["value"] = 0  # Reset progress bar
        progress_bar["maximum"] = file_size  # Set the progress bar maximum to the file size

        total_received = 0

        # Write file to the selected directory
        full_path = f"{download_path}/{filename}"
        client_socket.send(b"Ready to receive")  # Signal to the server that the client is ready to receive the file
        with open(full_path, "wb") as f:
            while True:
                data = client_socket.recv(1024)
                if b"<EOF>" in data:  # End of file signal
                    break
                f.write(data)
                total_received += len(data)
                progress_bar["value"] = total_received  # Update the progress bar
                progress_bar.update()  # Force the GUI to update

        console.insert(tk.END, f"Download Status: File downloaded successfully to {full_path}\n")

        # Hide the download button after completion
        download_button.pack_forget()

    except Exception as e:
        console.insert(tk.END, f"Error: {str(e)}\n")
    finally:
        client_socket.close()

        # Re-enable the buttons once the download is complete
        download_button.config(state=tk.NORMAL)
        upload_button.config(state=tk.NORMAL)
        list_button.config(state=tk.NORMAL)
        exit_button.config(state=tk.NORMAL)




# Function to list files on the server and make them clickable
def list_files(server_address, console, button_frame, download_button, selected_file):
    clear_console(console)  # Clear console for a new action
    download_button.pack_forget()  # Hide the download button
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(server_address)
        client_socket.send(b"LIST")
        
        files = client_socket.recv(4096).decode()
        console.insert(tk.END, "Available Files (click to select):\n")

        # Add clickable files
        for filename in files.split("\n"):
            if filename.strip():  # Ignore empty lines
                label = tk.Label(console, text=filename, fg="blue", cursor="hand2")
                label.bind("<Button-1>", lambda e, fname=filename: select_file(fname, download_button, selected_file))
                console.window_create(tk.END, window=label)
                console.insert(tk.END, "\n")
    except Exception as e:
        console.insert(tk.END, f"Error: {str(e)}\n")
    finally:
        client_socket.close()

# Function to select a file and show the download button
def select_file(filename, download_button, selected_file):
    selected_file.set(filename)
    download_button.pack(side=tk.LEFT, padx=10)  # Show download button

# Tkinter GUI setup
def setup_gui():
    root = tk.Tk()
    root.title("File Transfer Client")
    root.geometry("600x400")

    # Server address (can be customized)
    server_address = ("172.28.93.80", 5000)

    # Create a frame for the buttons
    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    # Create a text console for output logs
    console_frame = tk.Frame(root)
    console_frame.pack(pady=10, fill=tk.BOTH, expand=True)

    console = scrolledtext.ScrolledText(console_frame, wrap=tk.WORD, height=10, state="normal")
    console.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # Progress bar
    progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
    progress_bar.pack(pady=10)

    # Styled Buttons
    button_style = {"padx": 10, "pady": 5, "font": ("Arial", 12)}

    download_button = tk.Button(button_frame, text="Download File", **button_style)
    download_button.pack_forget()

    selected_file = tk.StringVar()

    download_button.config(command=lambda: download_file(server_address, console, selected_file.get(), download_button, progress_bar, upload_button, list_button, exit_button))

    upload_button = tk.Button(button_frame, text="Upload File", command=lambda: send_file(server_address, console, progress_bar, upload_button, list_button, download_button, exit_button), **button_style)
    upload_button.pack(side=tk.LEFT, padx=10)

    list_button = tk.Button(button_frame, text="List Files", command=lambda: list_files(server_address, console, button_frame, download_button, selected_file), **button_style)
    list_button.pack(side=tk.LEFT, padx=10)

    exit_button = tk.Button(button_frame, text="Exit", command=root.quit, **button_style)
    exit_button.pack(side=tk.LEFT, padx=10)

    root.mainloop()


if __name__ == "__main__":
    setup_gui()
