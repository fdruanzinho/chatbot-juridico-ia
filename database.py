import psycopg2
from psycopg2 import sql
from datetime import datetime

class Database:
    def __init__(self, dbname, user, password, host='localhost', port=5432):
        self.conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.cursor = self.conn.cursor()

    def inserir_usuario(self, telegram_id, username=None, nome=None):
        """Insere ou atualiza um usuário. Retorna o id do usuário."""
        query = """
            INSERT INTO usuarios (telegram_id, username, nome)
            VALUES (%s, %s, %s)
            ON CONFLICT (telegram_id) DO UPDATE
                SET username = EXCLUDED.username,
                    nome = EXCLUDED.nome
            RETURNING id;
        """
        self.cursor.execute(query, (telegram_id, username, nome))
        self.conn.commit()
        return self.cursor.fetchone()[0]

    def criar_atendimento(self, usuario_id):
        """Cria um novo atendimento e retorna seu id."""
        query = """
            INSERT INTO atendimentos (usuario_id, status, data_inicio)
            VALUES (%s, 'em_andamento', %s)
            RETURNING id;
        """
        self.cursor.execute(query, (usuario_id, datetime.now()))
        self.conn.commit()
        return self.cursor.fetchone()[0]

    def registrar_mensagem(self, atendimento_id, remetente, conteudo):
        """Armazena uma mensagem na tabela mensagens."""
        query = """
            INSERT INTO mensagens (atendimento_id, remetente, conteudo, data_envio)
            VALUES (%s, %s, %s, %s);
        """
        self.cursor.execute(query, (atendimento_id, remetente, conteudo, datetime.now()))
        self.conn.commit()

    def fechar(self):
        self.cursor.close()
        self.conn.close()