import http.server
import socketserver
import json
import os
import time
import gzip
from urllib.parse import urlparse

import socket

PORT = 8080
REVIEWS_DIR = 'reviews'
COMMENTS_FILE = os.path.join(REVIEWS_DIR, 'comments.json')
CHAT_FILE = 'chat_messages.json'
CHAT_TTL = 24 * 60 * 60  # 24 hours in seconds

def get_local_ip():
    try:
        # Create a dummy socket to connect to an external address (doesn't actually connect)
        # This helps to find the preferred local IP used for routing
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

class GzipSimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add Cache-Control for static files to improve performance
        # Check if 'path' attribute exists before accessing it (avoids AttributeError on bad requests)
        if hasattr(self, 'path'):
            if self.path.endswith(('.css', '.js', '.png', '.jpg', '.md', '.bin', '.wasm')):
                self.send_header('Cache-Control', 'public, max-age=3600')
            elif self.path.endswith('.html'):
                 # Cache HTML for a short time, or verify
                self.send_header('Cache-Control', 'no-cache')
            else:
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        else:
            # Fallback for error responses or when path is not set
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            
        super().end_headers()

    def do_GET(self):
        # Handle API routes first (no compression needed for small JSONs usually, but could add if big)
        parsed_path = urlparse(self.path)
        if parsed_path.path.startswith('/api/'):
            return self.handle_api_get(parsed_path)

        # Handle static files with GZIP
        # Check if client supports gzip
        accept_encoding = self.headers.get('Accept-Encoding', '')
        if 'gzip' in accept_encoding and not self.path.endswith(('.png', '.jpg', '.gif', '.zip', '.mp3', '.mp4', '.wasm')):
            # Compressible types
            # We need to read the file, compress it, and send it.
            # SimpleHTTPRequestHandler.do_GET sends the file. We need to override or intercept.
            # Intercepting is hard without rewriting do_GET. 
            # Easier approach: Let's just implement a simple in-memory compression for small files (html/css/js)
            
            # Construct the file path
            path = self.translate_path(self.path)
            if os.path.isdir(path):
                # Let standard handler deal with directories (index.html redirection etc)
                return super().do_GET()
            
            if os.path.exists(path):
                try:
                    with open(path, 'rb') as f:
                        content = f.read()
                    
                    compressed_content = gzip.compress(content)
                    
                    self.send_response(200)
                    self.send_header("Content-type", self.guess_type(path))
                    self.send_header("Content-Encoding", "gzip")
                    self.send_header("Content-Length", str(len(compressed_content)))
                    self.end_headers()
                    self.wfile.write(compressed_content)
                    return
                except Exception as e:
                    # Fallback to standard if anything goes wrong
                    pass
        
        super().do_GET()

    def handle_api_get(self, parsed_path):
        # API to get local IP
        if parsed_path.path == '/api/ip':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            ip = get_local_ip()
            self.wfile.write(json.dumps({"ip": ip}).encode('utf-8'))
            return

        # API to get comments
        if parsed_path.path == '/api/comments':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            if os.path.exists(COMMENTS_FILE):
                with open(COMMENTS_FILE, 'r', encoding='utf-8') as f:
                    try:
                        comments = json.load(f)
                    except json.JSONDecodeError:
                        comments = []
            else:
                comments = []
                
            self.wfile.write(json.dumps(comments).encode('utf-8'))
            return
            
        # API to get chat messages
        if parsed_path.path == '/api/chat':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            messages = []
            if os.path.exists(CHAT_FILE):
                try:
                    with open(CHAT_FILE, 'r', encoding='utf-8') as f:
                        messages = json.load(f)
                except json.JSONDecodeError:
                    messages = []
            
            # Filter messages older than 24 hours
            current_time = time.time()
            valid_messages = [m for m in messages if current_time - m.get('timestamp', 0) < CHAT_TTL]
            
            # Save if we filtered anything (or just to keep it clean)
            if len(messages) != len(valid_messages):
                with open(CHAT_FILE, 'w', encoding='utf-8') as f:
                    json.dump(valid_messages, f, ensure_ascii=False, indent=2)
            
            self.wfile.write(json.dumps(valid_messages).encode('utf-8'))
            return

        self.send_error(404, "API endpoint not found")

    def log_message(self, format, *args):
        # Suppress scary logs when someone tries to access via HTTPS
        
        # Case 1: Standard log_request (format="%s" %s %s)
        # args: (requestline, code, size)
        if len(args) == 3:
            status_code = str(args[1])
            request_line = str(args[0])
            if status_code == '400' and ('\x16\x03' in request_line or '\\x16\\x03' in request_line):
                print(f"[{self.log_date_time_string()}] {self.client_address[0]} попытался зайти через HTTPS. Используйте http://")
                return

        # Case 2: log_error (format="code %d, message %s")
        # args: (code, message)
        if len(args) == 2:
            status_code = str(args[0])
            message = str(args[1])
            if status_code == '400' and 'Bad request version' in message:
                # Often accompanied by binary data in the message
                return

        super().log_message(format, *args)

    # Removed original do_GET here because we moved logic into do_GET and handle_api_get above
    # Kept do_POST as is

    def do_POST(self):
        parsed_path = urlparse(self.path)
        
        # API to add a comment
        if parsed_path.path == '/api/comments':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                new_comment = json.loads(post_data.decode('utf-8'))
                
                # Validation
                if not new_comment.get('name') or not new_comment.get('text'):
                    self.send_response(400)
                    self.end_headers()
                    return

                # Read existing
                if os.path.exists(COMMENTS_FILE):
                    with open(COMMENTS_FILE, 'r', encoding='utf-8') as f:
                        try:
                            comments = json.load(f)
                        except json.JSONDecodeError:
                            comments = []
                else:
                    comments = []

                # Add timestamp (optional, or just order)
                comments.insert(0, new_comment) # Add to top

                # Ensure directory exists
                if not os.path.exists(REVIEWS_DIR):
                    os.makedirs(REVIEWS_DIR)

                # Save to main list file
                with open(COMMENTS_FILE, 'w', encoding='utf-8') as f:
                    json.dump(comments, f, ensure_ascii=False, indent=2)

                # Save individual file for easier viewing in folder
                timestamp = int(time.time())
                safe_name = "".join([c for c in new_comment.get('name', 'user') if c.isalnum() or c in (' ', '-', '_')]).strip()
                individual_filename = f"review_{timestamp}_{safe_name}.txt"
                individual_filepath = os.path.join(REVIEWS_DIR, individual_filename)
                
                try:
                    with open(individual_filepath, 'w', encoding='utf-8') as f:
                        f.write(f"Дата: {time.ctime(timestamp)}\n")
                        f.write(f"Имя: {new_comment.get('name')}\n")
                        f.write(f"Отзыв:\n{new_comment.get('text')}\n")
                except Exception as e:
                    print(f"Error saving individual file: {e}")

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))
                
            except Exception as e:
                print(f"Error: {e}")
                self.send_response(500)
                self.end_headers()
            return

        # API to send chat message
        if parsed_path.path == '/api/chat':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                new_msg = json.loads(post_data.decode('utf-8'))
                
                if not new_msg.get('name') or not new_msg.get('text'):
                    self.send_response(400)
                    self.end_headers()
                    return

                messages = []
                if os.path.exists(CHAT_FILE):
                    try:
                        with open(CHAT_FILE, 'r', encoding='utf-8') as f:
                            messages = json.load(f)
                    except json.JSONDecodeError:
                        messages = []
                
                # Add timestamp
                new_msg['timestamp'] = time.time()
                messages.append(new_msg) # Add to end

                # Filter old messages while we are here
                current_time = time.time()
                messages = [m for m in messages if current_time - m.get('timestamp', 0) < CHAT_TTL]

                # Save
                with open(CHAT_FILE, 'w', encoding='utf-8') as f:
                    json.dump(messages, f, ensure_ascii=False, indent=2)

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))
                
            except Exception as e:
                print(f"Error saving chat message: {e}")
                self.send_response(500)
                self.end_headers()
            return

        # Default behavior
        super().do_POST()

print(f"Starting server at http://localhost:{PORT}")
print(f"Local access: http://{get_local_ip()}:{PORT}")

# Use ThreadingHTTPServer to handle multiple requests (better for mobile/slow connections)
with ThreadingHTTPServer(("", PORT), GzipSimpleHTTPRequestHandler) as httpd:
    httpd.serve_forever()
