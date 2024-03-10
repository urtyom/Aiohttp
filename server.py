import json

import bcrypt
from aiohttp import web
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models import Base, Session, User, engine

app = web.Application()


def hash_password(password: str):
    password = password.encode()
    password = bcrypt.hashpw(password, bcrypt.gensalt())
    password = password.decode()
    return password


def check_password(password: str, hashed_password: str):
    password = password.encode()
    hashed_password = hashed_password.encode()
    return bcrypt.checkpw(password, hashed_password)


async def orm_context(app):
    print("START")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
    print("FINISH")

app.cleanup_ctx.append(orm_context)


def get_http_error(error_class, message):
    response = json.dumps({'errors': message})
    http_error = error_class(text=response, content_type='application/json')
    return http_error


async def get_user_by_id(session, user_id):
    user = await session.get(User, user_id)
    if user is None:
        raise get_http_error(web.HTTPNotFound, f'User with id {user_id} not found')
    return user


async def add_user(session, user):
    try:
        session.add(user)
        await session.commit()
    except IntegrityError:
        raise get_http_error(
            web.HTTPConflict, f"User with name {user.name} already exists"
        )


@web.middleware
async def session_middleware(request, handler):
    async with Session() as session:
        request.session = session
        response = await handler(request)
        return response


app.middlewares.append(session_middleware)


class UserView(web.View):

    @property
    def user_id(self):
        return int(self.request.match_info['user_id'])

    @property
    def session(self) -> AsyncSession:
        return self.request.session

    async def get_user(self):
        user = await get_user_by_id(self.session, self.user_id)
        return user

    async def get(self):
        user = await self.get_user()
        return web.json_response(user.dict)

    async def post(self):
        json_data = await self.request.json()
        json_data["password"] = hash_password(json_data["password"])
        user = User(**json_data)
        await add_user(self.session, user)
        return web.json_response(
            {
                'id': user.id,
            }
        )

    async def patch(self):
        json_data = await self.request.json()
        if "password" in json_data:
            json_data["password"] = hash_password(json_data["password"])
        user = await self.get_user()
        for field, value in json_data.items():
            setattr(user, field, value)
        await add_user(self.session, user)
        return web.json_response(
            {
                'id': user.id,
            }
        )

    async def delete(self):
        user = await self.get_user()
        await self.session.delete(user)
        await self.session.commit()
        return web.json_response({'status': 'deleted'})


app.add_routes(
    [
        web.get("/user/{user_id:\d+}", UserView),
        web.patch("/user/{user_id:\d+}", UserView),
        web.delete("/user/{user_id:\d+}", UserView),
        web.post("/user", UserView),
    ]
)

web.run_app(app)
