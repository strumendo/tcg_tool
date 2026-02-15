"""Initial schema - all tables for TCG Tool backend.

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2026-02-14 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. card_sets
    op.create_table(
        "card_sets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(10), nullable=False),
        sa.Column("tcgdex_id", sa.String(20), nullable=True),
        sa.Column("name_en", sa.String(200), nullable=True),
        sa.Column("name_pt", sa.String(200), nullable=True),
        sa.Column("regulation_mark", sa.String(1), nullable=True),
        sa.Column("release_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("total_cards", sa.Integer(), nullable=True),
        sa.Column("is_legal", sa.Boolean(), server_default="true", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )

    # 2. cards
    op.create_table(
        "cards",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name_en", sa.String(200), nullable=True),
        sa.Column("name_pt", sa.String(200), nullable=True),
        sa.Column("card_type", sa.String(20), nullable=False),
        sa.Column("trainer_subtype", sa.String(20), nullable=True),
        sa.Column("set_id", sa.Integer(), nullable=True),
        sa.Column("set_number", sa.String(10), nullable=True),
        sa.Column("regulation_mark", sa.String(1), nullable=True),
        sa.Column("hp", sa.Integer(), nullable=True),
        sa.Column("energy_type", sa.String(20), nullable=True),
        sa.Column("stage", sa.String(20), nullable=True),
        sa.Column("is_ex", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("image_url", sa.String(500), nullable=True),
        sa.Column("image_url_hires", sa.String(500), nullable=True),
        sa.Column("tcgdex_id", sa.String(50), nullable=True),
        sa.Column("pokemontcg_id", sa.String(50), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["set_id"], ["card_sets.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("set_id", "set_number", name="uq_cards_set_id_set_number"),
    )

    # 3. card_abilities
    op.create_table(
        "card_abilities",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("card_id", sa.Integer(), nullable=False),
        sa.Column("name_en", sa.String(200), nullable=True),
        sa.Column("name_pt", sa.String(200), nullable=True),
        sa.Column("effect_en", sa.Text(), nullable=True),
        sa.Column("effect_pt", sa.Text(), nullable=True),
        sa.Column("category", sa.String(30), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["card_id"], ["cards.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # 4. card_attacks
    op.create_table(
        "card_attacks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("card_id", sa.Integer(), nullable=False),
        sa.Column("name_en", sa.String(200), nullable=True),
        sa.Column("name_pt", sa.String(200), nullable=True),
        sa.Column("damage", sa.String(20), nullable=True),
        sa.Column("energy_cost", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("effect_en", sa.Text(), nullable=True),
        sa.Column("effect_pt", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["card_id"], ["cards.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # 5. card_functions
    op.create_table(
        "card_functions",
        sa.Column("card_id", sa.Integer(), nullable=False),
        sa.Column("function", sa.String(20), nullable=False),
        sa.ForeignKeyConstraint(
            ["card_id"], ["cards.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("card_id", "function"),
    )

    # 6. users
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(50), nullable=False),
        sa.Column("email", sa.String(200), nullable=True),
        sa.Column("language", sa.String(2), server_default="en", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
        sa.UniqueConstraint("email"),
    )

    # 7. decks
    op.create_table(
        "decks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("archetype", sa.String(50), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("is_valid", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("total_cards", sa.Integer(), server_default="0", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # 8. deck_cards
    op.create_table(
        "deck_cards",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("deck_id", sa.Integer(), nullable=False),
        sa.Column("card_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["deck_id"], ["decks.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["card_id"], ["cards.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("deck_id", "card_id", name="uq_deck_cards_deck_id_card_id"),
        sa.CheckConstraint(
            "quantity >= 1 AND quantity <= 60", name="ck_deck_cards_quantity"
        ),
    )

    # 9. meta_decks
    op.create_table(
        "meta_decks",
        sa.Column("id", sa.String(50), nullable=False),
        sa.Column("name_en", sa.String(200), nullable=True),
        sa.Column("name_pt", sa.String(200), nullable=True),
        sa.Column("tier", sa.Integer(), nullable=True),
        sa.Column("description_en", sa.Text(), nullable=True),
        sa.Column("description_pt", sa.Text(), nullable=True),
        sa.Column("strategy_en", sa.Text(), nullable=True),
        sa.Column("strategy_pt", sa.Text(), nullable=True),
        sa.Column("difficulty", sa.String(20), nullable=True),
        sa.Column("meta_share", sa.Numeric(5, 2), nullable=True),
        sa.Column("key_pokemon", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("energy_types", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("strengths_en", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("strengths_pt", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("weaknesses_en", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("weaknesses_pt", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("snapshot_date", sa.Date(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("tier >= 1 AND tier <= 3", name="ck_meta_decks_tier"),
    )

    # 10. meta_deck_cards
    op.create_table(
        "meta_deck_cards",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("meta_deck_id", sa.String(50), nullable=False),
        sa.Column("card_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["meta_deck_id"], ["meta_decks.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["card_id"], ["cards.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "meta_deck_id", "card_id", name="uq_meta_deck_cards_meta_deck_id_card_id"
        ),
    )

    # 11. meta_matchups
    op.create_table(
        "meta_matchups",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("deck_a_id", sa.String(50), nullable=False),
        sa.Column("deck_b_id", sa.String(50), nullable=False),
        sa.Column("win_rate_a", sa.Numeric(5, 2), nullable=True),
        sa.Column("notes_en", sa.Text(), nullable=True),
        sa.Column("notes_pt", sa.Text(), nullable=True),
        sa.Column("snapshot_date", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(
            ["deck_a_id"], ["meta_decks.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["deck_b_id"], ["meta_decks.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "deck_a_id", "deck_b_id", name="uq_meta_matchups_deck_a_id_deck_b_id"
        ),
    )

    # 12. user_collection
    op.create_table(
        "user_collection",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("card_id", sa.Integer(), nullable=False),
        sa.Column("quantity_owned", sa.Integer(), server_default="0", nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["card_id"], ["cards.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id", "card_id", name="uq_user_collection_user_id_card_id"
        ),
    )

    # 13. battles
    op.create_table(
        "battles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("deck_id", sa.Integer(), nullable=True),
        sa.Column("opponent_deck_name", sa.String(200), nullable=True),
        sa.Column("opponent_meta_deck_id", sa.String(50), nullable=True),
        sa.Column("result", sa.String(10), nullable=True),
        sa.Column("total_turns", sa.Integer(), nullable=True),
        sa.Column("went_first", sa.Boolean(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("source", sa.String(20), server_default="manual", nullable=False),
        sa.Column("source_url", sa.String(500), nullable=True),
        sa.Column(
            "played_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["deck_id"], ["decks.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["opponent_meta_deck_id"], ["meta_decks.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # 14. battle_actions
    op.create_table(
        "battle_actions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("battle_id", sa.Integer(), nullable=False),
        sa.Column("turn", sa.Integer(), nullable=False),
        sa.Column("player", sa.String(10), nullable=False),
        sa.Column("action_type", sa.String(30), nullable=False),
        sa.Column("card_name", sa.String(200), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("sequence_order", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["battle_id"], ["battles.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # 15. tournaments
    op.create_table(
        "tournaments",
        sa.Column("id", sa.String(50), nullable=False),
        sa.Column("name", sa.String(300), nullable=False),
        sa.Column("date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("location", sa.String(200), nullable=True),
        sa.Column("country", sa.String(100), nullable=True),
        sa.Column("format", sa.String(20), server_default="Standard", nullable=False),
        sa.Column("event_type", sa.String(30), nullable=True),
        sa.Column("url", sa.String(500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # 16. news_articles
    op.create_table(
        "news_articles",
        sa.Column("id", sa.String(100), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("url", sa.String(500), nullable=True),
        sa.Column("image_url", sa.String(500), nullable=True),
        sa.Column("source", sa.String(50), server_default="PokeBeach", nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # 17. card_usage_stats
    op.create_table(
        "card_usage_stats",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("card_id", sa.Integer(), nullable=False),
        sa.Column("format", sa.String(20), server_default="Standard", nullable=False),
        sa.Column("usage_percentage", sa.Numeric(5, 2), nullable=True),
        sa.Column("avg_copies", sa.Numeric(3, 1), nullable=True),
        sa.Column("sample_size", sa.Integer(), nullable=True),
        sa.Column("snapshot_date", sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(["card_id"], ["cards.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "card_id",
            "format",
            "snapshot_date",
            name="uq_card_usage_stats_card_id_format_snapshot_date",
        ),
    )

    # 18. deck_usage_stats
    op.create_table(
        "deck_usage_stats",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("archetype", sa.String(100), nullable=False),
        sa.Column("meta_share", sa.Numeric(5, 2), nullable=True),
        sa.Column("avg_placement", sa.Numeric(5, 1), nullable=True),
        sa.Column("sample_size", sa.Integer(), nullable=True),
        sa.Column("format", sa.String(20), server_default="Standard", nullable=False),
        sa.Column("snapshot_date", sa.Date(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "archetype",
            "format",
            "snapshot_date",
            name="uq_deck_usage_stats_archetype_format_snapshot_date",
        ),
    )


def downgrade() -> None:
    # Drop tables in reverse dependency order
    op.drop_table("deck_usage_stats")
    op.drop_table("card_usage_stats")
    op.drop_table("news_articles")
    op.drop_table("tournaments")
    op.drop_table("battle_actions")
    op.drop_table("battles")
    op.drop_table("user_collection")
    op.drop_table("meta_matchups")
    op.drop_table("meta_deck_cards")
    op.drop_table("meta_decks")
    op.drop_table("deck_cards")
    op.drop_table("decks")
    op.drop_table("users")
    op.drop_table("card_functions")
    op.drop_table("card_attacks")
    op.drop_table("card_abilities")
    op.drop_table("cards")
    op.drop_table("card_sets")
