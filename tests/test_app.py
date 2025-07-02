import unittest
import app
import sqlite3
import os

class FlaskCRUDTestCase(unittest.TestCase):

    def setUp(self):
        # Configura ambiente de teste
        app.DATABASE = 'test_database.db'
        self.app = app.app.test_client()
        app.init_db()

    def tearDown(self):
        # Remove banco de teste após os testes
        if os.path.exists('test_database.db'):
            os.remove('test_database.db')

    def test_home_page_loads(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Usu', response.data)

    def test_create_user(self):
        response = self.app.post('/create', data=dict(
            name='Joao',
            email='joao@example.com'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        conn = sqlite3.connect(app.DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE name='Joao'")
        user = cursor.fetchone()
        conn.close()
        self.assertIsNotNone(user)

    def test_update_user(self):
        # Primeiro cria um usuário
        conn = sqlite3.connect(app.DATABASE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", ('Maria', 'maria@example.com'))
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Atualiza o usuário
        response = self.app.post(f'/update/{user_id}', data=dict(
            name='Maria Atualizada',
            email='mariaatualizada@example.com'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        conn = sqlite3.connect(app.DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        self.assertEqual(user[1], 'Maria Atualizada')

    def test_delete_user(self):
        # Primeiro cria um usuário
        conn = sqlite3.connect(app.DATABASE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", ('Carlos', 'carlos@example.com'))
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Deleta o usuário
        response = self.app.get(f'/delete/{user_id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        conn = sqlite3.connect(app.DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        self.assertIsNone(user)

if __name__ == '__main__':
    unittest.main()
