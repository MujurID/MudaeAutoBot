import discord
import asyncio
import re




token = ""

mudae = 432610292342587392
channelid = 333

claim_delay = 8
kak_delay = 8
wait_finder = re.compile(r'\*\*(?:([0-9+])h )?([0-9]+)\*\* min left')
kak_finder = re.compile(r'\*\*??([0-9]+)\*\*<:kakera:469835869059153940>')
#use_emoji = "<:keqing_love:795077041761288214>"
use_emoji = "❤️"

series_list = ["Honkai Impact 3rd","Senran Kagura"]


def get_wait(text):
    waits = wait_finder.findall(text)
    if len(waits):
        hours = int(waits[0][0]) if waits[0][0] != '' else 0
        return (hours*60+int(waits[0][1]))*60
    return 0
    
def get_kak(text):
    k_value = kak_finder.findall(text)
    if len(k_value):
        return k_value[0]
    return 0

class MyClient(discord.Client):

        
        
    async def on_ready(self):
        print('Logged on as', self.user)
        
        self.loop.create_task(self.bg_task())

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
           return

        
        if message.author.id == mudae:
            print(message.content)

                             
            if message.embeds != []:
                objects = message.embeds[0].to_dict()
                print(objects['author'])
                
                
                
                for ser in series_list:
                    if ser in objects['description'] or self.user.name in message.content:               
                        
                        emoji = use_emoji
                        await asyncio.sleep(claim_delay)
                        await message.add_reaction(emoji)
                        
                if "<:kakera:469835869059153940>" in objects['description'] :
                    kak_value = get_kak(objects['description'])
                    print(kak_value)
                    if int(kak_value) >= 100 and "Belongs" not in objects['footer']['text'] :
                        emoji = use_emoji
                        await asyncio.sleep(claim_delay)
                        await message.add_reaction(emoji)
                        print("Possible Claim")
                        
                    
    

    async def on_reaction_add(self,reaction,user):
        if(reaction.custom_emoji and "kakera" in reaction.emoji.name):
            await asyncio.sleep(kak_delay)
            await reaction.message.add_reaction(reaction.emoji)
            
            
            
    async def bg_task(self):
        rollingchannel = self.get_channel(channelid)
        wait = 0
        def msg_check(message):
            return message.author.id == mudae and message.channel.id == channelid
        
        while True:
            while wait == 0:
                wait_for_mudae = self.loop.create_task(self.wait_for('message',timeout=10.0,check=msg_check))
                await asyncio.sleep(2)
                await rollingchannel.send("$wg")
                try:
                    msg = await wait_for_mudae
                    if msg.content.startswith(f"**{self.user.name}") and "roulette" in msg.content:
                        
                        wait = get_wait(msg.content)
                        
                except asyncio.TimeoutError:
                    print(f"mudae ded.")
                    return
            await asyncio.sleep(wait)
            wait = 0

                    
client = MyClient()
client.run(token,bot=False)
