import logging
from app import create_app, init_database, seed_data

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
)

app = create_app()

# Auto-create database tables + seed data on startup
init_database(app)
seed_data(app)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
