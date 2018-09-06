'''
import orm,asyncio
from models import User,Blog,Comment

async def test():
    await orm.create_pool(loop=loop,user='www-data',password='www-data',db='awesome')
    u = Blog(name='test3',email='test4@test.com',passwd='test',image='about:blank')
    #u = User(name='Test',email='test@example.com',passwd='1234567890',image='about:blank')
    await u.save()

loop = asyncio.get_event_loop()
loop.run_until_complete(test())
loop.close()


    __table__ = 'blogs'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    name = StringField(ddl='varchar(50)')
    summary = StringField(ddl='varchar(200)')
    content = TextField()
    created_at = FloatField(default=time.time)
'''