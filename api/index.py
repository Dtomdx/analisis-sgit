from http.server import BaseHTTPRequestHandler
import json
import os

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Analisis SGIT</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
                .btn { background: #0070f3; color: white; padding: 12px 24px; 
                       text-decoration: none; border-radius: 5px; display: inline-block; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 Análisis SGIT</h1>
                <p>Esta aplicación de Streamlit es muy grande para Vercel.</p>
                <p>Recomendamos usar Streamlit Community Cloud para el mejor rendimiento.</p>
                <br>
                <a href="https://share.streamlit.io/deploy" class="btn">
                  Desplegar en Streamlit Cloud
                </a>
                <br><br>
                <p><small>O modifica la aplicación para usar menos dependencias.</small></p>
            </div>
        </body>
        </html>
        """
        
        self.wfile.write(html_content.encode())

def main():
    print("Servidor iniciado...")