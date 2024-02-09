import redis
import json
import discord
import aiohttp
import asyncio
import os
# from AutoTasks_backend import secrets_manager
# For now, use os.env to get the secrets in order to decouple the discord bot from the Django app


class CustomDiscordClient(discord.Client):
    def __init__(self, *args, **kwargs):
        intents = discord.Intents.default()  # Use the default Intents. Discord Intents are used to specify which events your bot is subscribed to. By default, the bot is only subscribed to the events it needs to function.
        intents.messages = True  # Allows the bot to receive message events (and read messages)
        super().__init__(*args, **kwargs, intents=intents)
        self.redis_url = os.environ.get('DISCORD_BOT_BROKER_URL', 'redis://localhost:6379/1')
        self.redis_client = redis.Redis.from_url(self.redis_url)

    async def on_ready(self):
        print(f'Logged in as {self.user}')
        self.loop.create_task(self.check_redis_queue())

    async def on_message(self, message):
        if message.author == self.user:
            return
        await self.send_to_django(message)

    async def send_to_django(self, message):
        async with aiohttp.ClientSession() as session:
            endpoint_url = 'https://lemming-feasible-monitor.ngrok-free.app/api/discord_webhook/'
            headers = {'Authorization': f'Token {os.environ.get('INTERNAL_TOKEN')}'}
            data = {'content': message.content, 'user_id': str(message.author.id)}

            async with session.post(endpoint_url, data=data, headers=headers) as response:
                if response.status == 200:
                    response_data = await response.json()
                    reply = response_data.get("body", "No response from server.")
                    await message.author.send(reply)
                else:
                    await message.author.send(f"Error communicating with the server, status code: {response.status}")

    async def check_redis_queue(self):
        while True:
            message = self.redis_client.blpop('discord_queue', timeout=1)
            if message:
                data = json.loads(message[1])  # Use json.loads to deserialize the JSON string back into a Python dictionary. Use message[1] because blpop returns a tuple, ('discord_queue', 'message_data')
                discord_user_id = data['discord_user_id']
                content = data['body']
                user = await self.fetch_user(discord_user_id)
                await user.send(content)
            await asyncio.sleep(1)  # Prevents the loop from running too fast


client = CustomDiscordClient()
client.run(os.environ.get('DISCORD_BOT_TOKEN'))
