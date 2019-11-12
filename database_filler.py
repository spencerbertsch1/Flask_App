from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, CategoryItem, User
engine = create_engine('postgresql://catalog:catalog12345@localhost/catalog')
# engine = create_engine('postgresql://catalog:password@localhost/catalog')
# engine = create_engine('sqlite:///WinterSports.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
User1 = User(name="Jonny Snowboard", email="jonnysnowboard@udacity.com",
             picture="https://images.unsplash.com/photo-1472099645785-"
             "5658abf4ff4e?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd"
             "9&auto=format&fit=crop&w=2250&q=80")
session.add(User1)
session.commit()

# ================ Items for Skiing category ================
category1 = Category(user_id=1, name="Skiing")

session.add(category1)
session.commit()

Item1 = CategoryItem(user_id=1,
                     name="Ski Poles",
                     description="Keeps you upright on the mountain",
                     category=category1)

session.add(Item1)
session.commit()

Item2 = CategoryItem(user_id=1,
                     name='Skis',
                     description='By far the best investments you can make!',
                     category=category1)

session.add(Item2)
session.commit()


Item3 = CategoryItem(user_id=1,
                     name="Ski_Boots",
                     description="Might be uncomfortable, but worth it!",
                     category=category1)

session.add(Item3)
session.commit()


# ================ Items for Snowboarding category ================
category2 = Category(user_id=1, name="Snowboarding")

session.add(category2)
session.commit()

Item1 = CategoryItem(user_id=1,
                     name='Snowboard',
                     description='fun on the mountain for all ages!',
                     category=category2)

session.add(Item1)
session.commit()


Item2 = CategoryItem(user_id=1,
                     name="Snowboard_Boots",
                     description="Strap into your new snowboard with ease!",
                     category=category2)

session.add(Item2)
session.commit()


# ================ Items for Hockey category ================
category3 = Category(user_id=1, name="Hockey")

session.add(category3)
session.commit()

Item1 = CategoryItem(user_id=1,
                     name='Hockey_Skates',
                     description='Skate fast, win some hockey games!',
                     category=category3)

session.add(Item1)
session.commit()


Item2 = CategoryItem(user_id=1,
                     name="Hockey_Stick",
                     description="Perfect for pond hockey!",
                     category=category3)

session.add(Item2)
session.commit()


# ================ Items for Skating category ================
category4 = Category(user_id=1, name="Skating")

session.add(category4)
session.commit()

Item1 = CategoryItem(user_id=1,
                     name='Ice_Skates',
                     description='Great for ice skating at all experience!',
                     category=category4)

session.add(Item1)
session.commit()


Item2 = CategoryItem(user_id=1,
                     name="Hot_coco",
                     description="Perfect on a cold day",
                     category=category4)

session.add(Item2)
session.commit()


print "added new items!"
