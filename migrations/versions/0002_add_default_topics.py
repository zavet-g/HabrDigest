"""Add default topics

Revision ID: 0002
Revises: 0001
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Text, Boolean

# revision identifiers, used by Alembic.
revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Создаем временную таблицу для вставки данных
    topics_table = table('topics',
        column('name', String),
        column('slug', String),
        column('description', Text),
        column('is_active', Boolean)
    )
    
    # Добавляем стандартные темы
    op.bulk_insert(topics_table, [
        {
            'name': 'Python',
            'slug': 'python',
            'description': 'Язык программирования Python',
            'is_active': True
        },
        {
            'name': 'JavaScript',
            'slug': 'javascript',
            'description': 'Язык программирования JavaScript',
            'is_active': True
        },
        {
            'name': 'DevOps',
            'slug': 'devops',
            'description': 'DevOps практики и инструменты',
            'is_active': True
        },
        {
            'name': 'Machine Learning',
            'slug': 'machine-learning',
            'description': 'Машинное обучение и ИИ',
            'is_active': True
        },
        {
            'name': 'Web Development',
            'slug': 'web-development',
            'description': 'Веб-разработка',
            'is_active': True
        },
        {
            'name': 'Mobile Development',
            'slug': 'mobile-development',
            'description': 'Мобильная разработка',
            'is_active': True
        },
        {
            'name': 'Database',
            'slug': 'database',
            'description': 'Базы данных и SQL',
            'is_active': True
        },
        {
            'name': 'Security',
            'slug': 'security',
            'description': 'Информационная безопасность',
            'is_active': True
        },
        {
            'name': 'Cloud Computing',
            'slug': 'cloud-computing',
            'description': 'Облачные технологии',
            'is_active': True
        },
        {
            'name': 'Blockchain',
            'slug': 'blockchain',
            'description': 'Блокчейн и криптовалюты',
            'is_active': True
        }
    ])


def downgrade() -> None:
    # Удаляем стандартные темы
    op.execute("DELETE FROM topics WHERE slug IN ('python', 'javascript', 'devops', 'machine-learning', 'web-development', 'mobile-development', 'database', 'security', 'cloud-computing', 'blockchain')") 