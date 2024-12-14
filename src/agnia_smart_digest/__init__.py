import asyncio
import importlib

import uvicorn
import yaml

import agnia_smart_digest.servers.http.server as http_server
import agnia_smart_digest.servers.socket.server as socket_server


def main():
    config = yaml.load(open("config.yml"), Loader=yaml.FullLoader)

    for module in config["load_actions"]:
        importlib.import_module(module)

    config = uvicorn.Config(http_server.build_app(), port=8845, log_level="info")
    server = uvicorn.Server(config)

    async def launch():
        await asyncio.gather(server.serve(), socket_server.run())

    asyncio.run(launch())
