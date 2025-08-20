"""
Simple web server to keep the deployment alive while running the Telegram bot.
This serves a basic status page and runs the bot in the background.
"""

import os
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from bot_enhanced import main as run_bot

class StatusHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Telegram Time Zone Bot</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                    .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                    .status { color: #28a745; font-weight: bold; }
                    .bot-info { background: #e9ecef; padding: 15px; border-radius: 5px; margin: 20px 0; }
                    .instructions { background: #d1ecf1; padding: 15px; border-radius: 5px; border-left: 4px solid #bee5eb; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🤖 Telegram Time Zone Bot</h1>
                    <p class="status">✅ Bot Status: Running</p>
                    
                    <div class="bot-info">
                        <h3>📱 How to Use:</h3>
                        <ol>
                            <li>Open Telegram</li>
                            <li>Search for your bot using its username</li>
                            <li>Send <code>/start</code> to begin</li>
                            <li>Select any city to get current local time</li>
                        </ol>
                    </div>
                    
                    <div class="instructions">
                        <h3>🌍 Features:</h3>
                        <ul>
                            <li>Real-time local times for 100+ cities</li>
                            <li>Major US and Canadian cities supported</li>
                            <li>Easy-to-use inline keyboard interface</li>
                            <li>Pagination for browsing all cities</li>
                        </ul>
                    </div>
                    
                    <p><strong>Bot Commands:</strong></p>
                    <ul>
                        <li><code>/start</code> - Show city selection menu</li>
                        <li><code>/help</code> - Show help information</li>
                        <li><code>/about</code> - About this bot</li>
                    </ul>
                    
                    <p><em>Last updated: """ + time.strftime("%Y-%m-%d %H:%M:%S UTC") + """</em></p>
                </div>
            </body>
            </html>
            """
            
            self.wfile.write(html_content.encode())
            
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "healthy", "bot": "running"}')
            
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def log_message(self, format, *args):
        # Suppress default HTTP server logs
        pass

def start_web_server():
    """Start the web server."""
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), StatusHandler)
    print(f"🌐 Web server running on port {port}")
    server.serve_forever()

def start_bot():
    """Start the Telegram bot."""
    time.sleep(2)  # Give web server time to start
    print("🤖 Starting Telegram bot...")
    run_bot()

if __name__ == "__main__":
    # Start web server in a separate thread
    web_thread = threading.Thread(target=start_web_server, daemon=True)
    web_thread.start()
    
    # Start the bot in the main thread
    start_bot()