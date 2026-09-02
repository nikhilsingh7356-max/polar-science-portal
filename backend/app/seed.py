from .database import Base, engine, SessionLocal
from .models import User, Expedition, Resource, Media
from .auth import hash_password

def seed_database():
    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        if not db.query(User).filter_by(email="admin@polar.local").first():
            db.add(User(name="Portal Admin", email="admin@polar.local", password_hash=hash_password("Admin@123"), role="admin"))
        if not db.query(User).filter_by(email="researcher@polar.local").first():
            db.add(User(name="Demo Researcher", email="researcher@polar.local", password_hash=hash_password("Research@123"), role="researcher"))
        if db.query(Expedition).count() == 0:
            ex = [
                Expedition(name="Indian Antarctic Expedition 2024", year=2024, region="Antarctica", latitude=-70.7, longitude=11.9, description="Sample expedition record for the prototype. Replace or augment with authorized institutional metadata."),
                Expedition(name="Indian Arctic Expedition 2023", year=2023, region="Arctic", latitude=78.9, longitude=11.9, description="Sample Arctic expedition record demonstrating connected repository content."),
                Expedition(name="Polar Observation Demonstration 2022", year=2022, region="Antarctica", latitude=-68.0, longitude=20.0, description="Demonstration expedition record for the SIH prototype."),
            ]
            db.add_all(ex); db.flush()
            db.add_all([
                Resource(title="Antarctic Expedition Research Report", description="Sample metadata describing field observations, logistics and scientific activities during an Antarctic expedition.", resource_type="report", year=2024, author="Demo NCPOR Research Team", keywords="Antarctica, expedition, polar science", expedition_id=ex[0].id, status="approved"),
                Resource(title="Polar Science Publication", description="Sample publication record demonstrating searchable scientific knowledge and linked expedition context.", resource_type="publication", year=2023, author="Demo Research Team", keywords="climate, polar research, Arctic", expedition_id=ex[1].id, status="approved"),
                Resource(title="Antarctic Observation Dataset", description="Sample dataset description for testing repository search and metadata workflows.", resource_type="dataset", year=2024, author="Demo Research Team", keywords="dataset, observations, Antarctica", expedition_id=ex[0].id, status="approved"),
                Resource(title="Student Guide to Polar Research", description="A demonstration educational resource explaining why polar regions matter to Earth-system science.", resource_type="education", year=2025, author="Polar Science Portal Demo Team", keywords="education, students, climate, polar science", expedition_id=ex[0].id, status="approved"),
            ])
            db.add_all([
                Media(title="Antarctic Field Activity", media_type="image", caption="Sample media record for the prototype.", expedition_id=ex[0].id),
                Media(title="Arctic Expedition Video", media_type="video", caption="Sample media record for the prototype.", expedition_id=ex[1].id),
            ])
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
    print("Seed complete")
