import asyncio

import aiohttp


async def main():
    async with aiohttp.ClientSession() as session:
        # async with session.post("http://127.0.0.1:8080/user",
        #                         json={
        #                             'name': 'user_1',
        #                             'password': 'password_1',
        #                             'title': 'asdasd',
        #                             'description': '123123123'
        #                             }
        #                         ) as response:
        #
        #     print(response.status)
        #     print(await response.text())

        #
        # async with session.patch("http://127.0.0.1:8080/user/2",
        #
        #                          json={'name': 'new_user_name'}) as response:
        #     print(response.status)
        #     print(await response.text())

        # async with session.get("http://127.0.0.1:8080/user/1") as response:
        #     print(response.status)
        #     print(await response.text())

        async with session.delete("http://127.0.0.1:8080/user/1") as response:
            print(response.status)
            print(await response.text())
        #
        async with session.get("http://127.0.0.1:8080/user/1") as response:
            print(response.status)
            print(await response.text())


asyncio.run(main())