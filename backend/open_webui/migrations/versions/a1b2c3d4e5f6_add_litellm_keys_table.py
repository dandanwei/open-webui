"""Add litellm keys table

Revision ID: a1b2c3d4e5f6
Revises: 018012973d35
Create Date: 2024-12-15 10:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

revision = "a1b2c3d4e5f6"
down_revision = "018012973d35"
branch_labels = None
depends_on = None


def upgrade():
    # Create the litellm_key table
    op.create_table(
        "litellm_key",
        sa.Column("id", sa.String(), nullable=False, primary_key=True),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("key_name", sa.Text(), nullable=False),
        sa.Column("api_key", sa.Text(), nullable=False),
        sa.Column("key_type", sa.String(), nullable=True, default="api_key"),
        sa.Column("group_ids", sa.JSON(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True, default=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=True),
        sa.Column("updated_at", sa.BigInteger(), nullable=True),
        sa.Column("last_used_at", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ),
    )

    # Create indexes for better performance
    op.create_index("ix_litellm_key_user_id", "litellm_key", ["user_id"])
    op.create_index("ix_litellm_key_key_name", "litellm_key", ["key_name"])
    op.create_index("ix_litellm_key_is_active", "litellm_key", ["is_active"])


def downgrade():
    # Drop indexes
    op.drop_index("ix_litellm_key_is_active", table_name="litellm_key")
    op.drop_index("ix_litellm_key_key_name", table_name="litellm_key")
    op.drop_index("ix_litellm_key_user_id", table_name="litellm_key")
    
    # Drop the table
    op.drop_table("litellm_key")