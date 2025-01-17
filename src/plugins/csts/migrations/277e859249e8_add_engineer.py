"""add ENGINEER

迁移 ID: 277e859249e8
父迁移: 6cf56855cbc2
创建时间: 2024-10-21 22:48:54.252970

"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = '277e859249e8'
down_revision: str | Sequence[str] | None = '6cf56855cbc2'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade(name: str = "") -> None:
    if name:
        return
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('csts_engineer',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('engineer_id', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_csts_engineer')),
    sa.UniqueConstraint('engineer_id'),
    info={'bind_key': 'csts'}
    )
    # ### end Alembic commands ###


def downgrade(name: str = "") -> None:
    if name:
        return
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('csts_engineer')
    # ### end Alembic commands ###
