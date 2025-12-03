"""
Entry point for the EReceipt Flask application
"""
from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    
    print(f"""
    ╔══════════════════════════════════════════════════════╗
    ║          🧾 EReceipt Backend Server                  ║
    ╠══════════════════════════════════════════════════════╣
    ║  Running on: http://localhost:{port}                   ║
    ║  Debug mode: {debug}                                  ║
    ║  API Docs:   http://localhost:{port}/api/health        ║
    ╚══════════════════════════════════════════════════════╝
    """)
    
    app.run(host='0.0.0.0', port=port, debug=debug)

