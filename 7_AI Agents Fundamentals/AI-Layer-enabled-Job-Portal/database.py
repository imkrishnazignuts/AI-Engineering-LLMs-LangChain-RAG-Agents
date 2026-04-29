from sqlmodel import create_engine

engine = create_engine('sqlite:///major-project.db',echo=True)

