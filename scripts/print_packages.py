import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, Package

with app.app_context():
    packages = Package.query.all()
    if not packages:
        print('No packages found')
    for p in packages:
        print(p.id, p.name, p.image)
