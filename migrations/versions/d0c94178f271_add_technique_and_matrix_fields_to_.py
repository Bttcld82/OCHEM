"""add_technique_and_matrix_fields_to_parameter

Revision ID: d0c94178f271
Revises: 4bc03b77ff77
Create Date: 2025-10-14 16:43:24.036214

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd0c94178f271'
down_revision = '4bc03b77ff77'
branch_labels = None
depends_on = None


def upgrade():
    # Add technique_id and matrix fields to parameter table
    with op.batch_alter_table('parameter', schema=None) as batch_op:
        batch_op.add_column(sa.Column('technique_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('matrix', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('min_value', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('max_value', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('precision_digits', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('description', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('active', sa.Boolean(), nullable=True, default=True))
        batch_op.create_foreign_key('fk_parameter_technique_id', 'technique', ['technique_id'], ['id'])


def downgrade():
    # Remove the added fields
    with op.batch_alter_table('parameter', schema=None) as batch_op:
        batch_op.drop_constraint('fk_parameter_technique_id', type_='foreignkey')
        batch_op.drop_column('active')
        batch_op.drop_column('description')
        batch_op.drop_column('precision_digits')
        batch_op.drop_column('max_value')
        batch_op.drop_column('min_value')
        batch_op.drop_column('matrix')
        batch_op.drop_column('technique_id')
