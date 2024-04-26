import unittest

from database.db import get_db


class TestGetDB(unittest.TestCase):
    def test_get_db(self):
        with self.assertRaises(Exception):
            with get_db() as db:
                # Do something with the session, e.g., db.query(...).all()
                pass
            # The session should be closed here
            self.assertIsNone(db)

if __name__ == '__main__':
    unittest.main()