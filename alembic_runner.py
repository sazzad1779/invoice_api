from alembic.config import Config
from alembic import command
from api_test.database import engine  # Update with your project details

alembic_cfg = Config("alembic.ini")

def upgrade():
    command.upgrade(alembic_cfg, "head")

def downgrade():
    command.downgrade(alembic_cfg, "base")

def revision(message):
    command.revision(alembic_cfg, message=message, autogenerate=True)
