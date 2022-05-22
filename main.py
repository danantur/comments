import argparse
import asyncio
import json
import os

import aiohttp_cors
import aiohttp_jinja2
import jinja2
from aiohttp import web
from aiohttp.abc import Request
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker, selectinload

from db import Base, Comments, Files, new_alchemy_encoder


async def handle(request: Request):
    if request.method == "GET":
        return aiohttp_jinja2.render_template('index.jinja2', request, {})


async def comments_api(request: Request):
    async_session = sessionmaker(
        request.app["mysql_engine"], expire_on_commit=False, class_=AsyncSession
    )
    if request.method == "GET":
        stmt = select(Comments).options(selectinload(Comments.files))
        async with async_session.begin() as session:
            result = (await session.execute(stmt)).scalars()
        result = [json.loads(json.dumps(s, cls=new_alchemy_encoder(False, ["files"]), check_circular=False)) for s in result]
        return web.json_response(result)

    elif request.method == "POST":

        reader = await request.multipart()

        last_is_None = False

        files = []
        email = ""
        text = ""

        while True:
            field = await reader.next()
            if field is None and not last_is_None:
                last_is_None = True
                continue
            elif field is None and last_is_None:
                break
            if field.name == 'files':
                filename = field.filename
                files.append(Files(uri=f"static/files/{filename}"))

                size = 0
                with open(os.path.join('static/files/', filename), 'wb') as f:
                    while True:
                        chunk = await field.read_chunk()  # 8192 bytes by default.
                        if not chunk:
                            break
                        size += len(chunk)
                        f.write(chunk)
            elif field.name == "email":
                email = await field.text(encoding="utf-8")
            elif field.name == "text":
                text = await field.text(encoding="utf-8")

        async with async_session.begin() as session:
            session.add_all([
                Comments(files=files, email=email, text=text)
            ])

            await session.commit()

        raise web.HTTPFound('/comments')


async def on_startup(appl):
    async with appl["mysql_engine"].begin() as con:
        await con.run_sync(Base.metadata.create_all)


async def on_cleanup(appl):
    await appl["mysql_engine"].dispose()


app = web.Application()
app.add_routes([web.get('/comments', handle),
                web.post('/api/comments', comments_api),
                web.get("/api/comments", comments_api)])

if __name__ == '__main__':
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates'))

    parser = argparse.ArgumentParser(description="aiohttp server example")
    parser.add_argument('--path')
    parser.add_argument('--port')

    app["mysql_engine"] = create_async_engine("mysql+aiomysql://root:1234@localhost:3306/comments", echo=True)
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    args = parser.parse_args()
    web.run_app(app, path=args.path, port=args.port)
