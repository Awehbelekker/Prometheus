"""Initialize / migrate hedge-fund multi-investor schema locally.

Safe to run multiple times; only creates missing tables.
This is a lightweight bootstrap (not Alembic) for local pilot.
"""
from __future__ import annotations
import sys
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))  # add project root

from core.models import Base  # noqa: E402
from core import models as mdl  # noqa: E402

TARGET_TABLES = [
	mdl.Invitation.__tablename__,
	mdl.CapitalAccount.__tablename__,
	mdl.Contribution.__tablename__,
	mdl.TradeLedger.__tablename__,
	mdl.Position.__tablename__,
	mdl.NAVHistory.__tablename__,
	mdl.UserPerformance.__tablename__,
	mdl.RiskEvent.__tablename__,
	mdl.FeatureFlag.__tablename__,
	mdl.SystemState.__tablename__,
	mdl.RiskLimit.__tablename__,
]

def main(db_url: str = 'sqlite:///prometheus_trading.db') -> None:
	engine = create_engine(db_url, future=True)
	insp = inspect(engine)
	existing = set(insp.get_table_names())

	missing = [t for t in TARGET_TABLES if t not in existing]
	if not missing:
		print("[CHECK] All hedge-fund extension tables already exist.")
		return

	print("🛠  Creating missing tables:", ", ".join(missing))
	# Create only the metadata for missing tables (simplify: create all; SQLAlchemy will ignore existing)
	Base.metadata.create_all(bind=engine, tables=[tbl for tbl in Base.metadata.sorted_tables if tbl.name in missing])

	# Verify
	insp2 = inspect(engine)
	after = set(insp2.get_table_names())
	not_created = [t for t in missing if t not in after]
	if not_created:
		print("[ERROR] Failed to create:", not_created)
		sys.exit(1)
	print("[CHECK] Created:", ", ".join(missing))

	# Seed feature flags (idempotent)
	Session = sessionmaker(bind=engine, future=True)
	with Session() as session:
		from core.models import FeatureFlag, RiskLimit  # local import
		def upsert_flag(k: str, v: str):
			ff = session.get(FeatureFlag, k)
			if ff is None:
				session.add(FeatureFlag(key=k, value=v))
		upsert_flag('INVITE_REQUIRED', 'true')
		upsert_flag('DEMO_MODE_DISABLED', 'true')
		# Seed global risk limit if absent
		if not session.query(RiskLimit).filter(RiskLimit.user_id.is_(None)).first():
			session.add(RiskLimit(id='risk_default', user_id=None, daily_loss_pct=5.0, max_position_pct=20.0))
		session.commit()
	print("[CHECK] Seeded default feature flags.")

if __name__ == '__main__':
	main()

