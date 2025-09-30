from app import app, db, Package, Bus, Booking
import os

with app.app_context():
    pkgs = Package.query.filter(db.func.lower(Package.name) == 'testpkg').all()
    if not pkgs:
        print('No TESTPKG package found')
    else:
        for pkg in pkgs:
            print('Removing package', pkg.id, pkg.name)
            Booking.query.filter_by(package_id=pkg.id).delete()
            Bus.query.filter_by(package_id=pkg.id).delete()
            db.session.delete(pkg)
        db.session.commit()
        print('Removal complete')

# check img.jpg usage
images_dir = os.path.join(os.getcwd(), 'static', 'images')
img_path = os.path.join(images_dir, 'img.jpg')
if os.path.exists(img_path):
    with app.app_context():
        used = Package.query.filter_by(image='img.jpg').count()
    if used == 0:
        try:
            os.remove(img_path)
            print('Removed placeholder image img.jpg')
        except Exception as e:
            print('Failed to remove img.jpg', e)
    else:
        print('img.jpg still referenced by', used, 'packages')
else:
    print('img.jpg not present')
