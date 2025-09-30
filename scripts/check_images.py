from app import app
from app import Package
import os

root = os.getcwd()
images_dir = os.path.join(root, 'static', 'images')
missing = []
with app.app_context():
    packages = Package.query.all()
    print(f'Found {len(packages)} packages to check')
    for p in packages:
        img = getattr(p, 'image', None)
        if not img:
            missing.append((p.id, p.name, img, 'no-image-field'))
            continue
        path = os.path.join(images_dir, img)
        if not os.path.exists(path):
            missing.append((p.id, p.name, img, path))

if missing:
    print('Missing images:')
    for m in missing:
        print(f'  id={m[0]} name={m[1]} image={m[2]} expected_path={m[3]}')
else:
    print('All package image files exist in static/images')
