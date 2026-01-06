# Entry point for running the Flask app
from app.main import create_app

app = create_app()
if __name__ == "__main__":
    app.run()
