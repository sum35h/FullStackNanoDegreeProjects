from app import Genre,db

genre_list = ['Alternative', 'Blues', 'Classical', 'Country', 'Electronic', 'Folk', 'Funk', 'Hip-Hop', 'Heavy Metal', 'Instrumental', 'Jazz', 'Musical Theatre', 'Pop', 'Punk', 'R&B', 'Reggae', 'Rock n Roll', 'Soul', 'Other']


for genre in genre_list:
    g = Genre(name=genre)
    db.session.add(g)
try:
    db.session.commit()
except:
    db.session.rollback()
finally:
    db.session.close()
