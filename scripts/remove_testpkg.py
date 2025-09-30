from app import app, db, Package, Bus, Booking

with app.app_context():
    pkg = Package.query.filter_by(name='TESTPKG').first()
    if not pkg:
        print('TESTPKG not found; nothing to remove')
    else:
        print('Removing TESTPKG id=', pkg.id)
        # delete bookings referencing this package
        Booking.query.filter_by(package_id=pkg.id).delete()
        # delete buses
        Bus.query.filter_by(package_id=pkg.id).delete()
        # delete package
        db.session.delete(pkg)
        db.session.commit()
        print('Removed TESTPKG and related buses/bookings')
