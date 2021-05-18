import discum
import re
import asyncio
import json
import time
import logging
import threading

jsonf = open("Settings_Mudae.json")
settings = json.load(jsonf)
jsonf.close()

bot = discum.Client(token=settings["token"],log={"console":False, "file":False})
mudae = 432610292342587392
chid = settings["channel_id"]
mhids = [int(mh) for mh in settings["multichannel"]]

series_list = settings["series_list"]
chars = [charsv.lower() for charsv in settings["namelist"]]
kak_min = settings["min_kak"]
claim_delay = settings["claim_delay"]
kak_delay = settings["kak_delay"]
roll_prefix = settings["roll_this"]


kak_finder = re.compile(r'\*\*??([0-9]+)\*\*<:kakera:469835869059153940>')
like_finder = re.compile(r'Likes\: \#??([0-9]+)')
claim_finder = re.compile(r'Claims\: \#??([0-9]+)')
poke_finder = re.compile(r'\*\*(?:([0-9+])h )?([0-9]+)\*\* min')
wait_finder = re.compile(r'\*\*(?:([0-9+])h )?([0-9]+)\*\* min \w')
waitk_finder = re.compile(r'\*\*(?:([0-9+])h )?([0-9]+)\*\* min')
ser_finder = re.compile(r'.*.')

KakeraVari = [kakerav.lower() for kakerav in settings["emoji_list"]]
eventlist = ["🕯️","😆"]


kakera_wall = {}

#logging settings
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

def get_kak(text):
    k_value = kak_finder.findall(text)
    like_value = like_finder.findall(text)
    claim_value=claim_finder.findall(text)
    if len(k_value):
        return k_value[0]
    elif len(like_value) or len(claim_value):
        LR = 0
        CR = 0 
        CA= 1
        if(len(like_value)):
            LR = like_value[0]
        if(len(claim_value)):
            CR = claim_value[0]
        pkak = (int(LR) + int(CR)) /2
        multi = 1 + (CA/5500)
        return((25000 *(pkak+70)**-.75+20)*multi+.5)     
    return 0
    
def get_wait(text):
    waits = wait_finder.findall(text)
    if len(waits):
        hours = int(waits[0][0]) if waits[0][0] != '' else 0
        return (hours*60+int(waits[0][1]))*60
    return 0
    
def get_pwait(text):
    waits = poke_finder.findall(text)
    if len(waits):
        hours = int(waits[0][0]) if waits[0][0] != '' else 0
        return (hours*60+int(waits[0][1]))*60
    return 0
def get_serial(text):
    serk = ser_finder.findall(text)
    return serk[0]

_resp = dict()
def wait_for(bot, predicate, timeout=None):
    ev = threading.Event()
    ident = threading.get_ident()
    def evt_check(resp):
        if predicate(resp):
            _resp[ident] = resp.parsed.auto()
            ev.set()
    bot.gateway._after_message_hooks.insert(0,evt_check)
    ev.wait(timeout)
    bot.gateway.removeCommand(evt_check)
    obj = _resp.pop(ident,None)
    
    return obj

#wait_for(bot,lambda r: r.event.message and r.parsed.auto()['author']['id'] == mudae)
#wait_for(bot,lambda r: r.event.reaction_added and r.parsed.auto()['user_id'] == mudae)

def mudae_warning(tide,StartwithUser=True):
    # build check func
    def c(r):
        if r.event.message:
            r = r.parsed.auto()
            # must be from relevant channel id, and start with username
            if StartwithUser == True:
                return r['author']['id'] == str(mudae) and r['channel_id'] == tide and r['content'].startswith(f"**{bot.gateway.session.user['username']}")
            elif StartwithUser == False:
                return r['author']['id'] == str(mudae) and r['channel_id'] == tide
        return False
    return c

@bot.gateway.command
def on_message(resp):
    if resp.event.ready_supplemental:
        global user
        user = bot.gateway.session.user
        
    if resp.event.message:
        m = resp.parsed.auto()
        aId = m['author']['id']
        content = m['content']
        embeds = m['embeds']
        messageid = m['id']
        channelid = m['channel_id']
        guildid = m['guild_id'] if 'guild_id' in m else None
        #print(f"{messageid} and {channelid}")
        
        
        if int(aId) == mudae and int(channelid) in mhids:
            #print("Yes")

            if embeds != []:
                charpop = m['embeds'][0]
                charname = charpop["author"]["name"]
                chardes = charpop["description"]
                charcolor = int(charpop['color'])

                #print(charcolor)

                if str(user['id']) in content:
                    
                    logger.info(f"Wished {charname} from {get_serial(chardes)} with {get_kak(chardes)} Value in Server id:{guildid}")
                    time.sleep(claim_delay)
                    if "reactions" in bot.getMessage(channelid, messageid).json()[0] and bot.getMessage(channelid, messageid).json()[0]["reactions"][0]["emoji"]['id'] == None:
                        bot.addReaction(channelid, messageid, bot.getMessage(channelid, messageid).json()[0]["reactions"][0]["emoji"]["name"])
                    else:
                        bot.addReaction(channelid, messageid, "❤")
                
                if charname.lower() in chars:
                    
                    logger.info(f"{charname} appeared attempting to Snipe Server id:{guildid}")
                    time.sleep(claim_delay)
                    
                    if "reactions" in bot.getMessage(channelid, messageid).json()[0] and bot.getMessage(channelid, messageid).json()[0]["reactions"][0]["emoji"]['id'] == None:
                        bot.addReaction(channelid, messageid, bot.getMessage(channelid, messageid).json()[0]["reactions"][0]["emoji"]["name"])
                    else:
                        bot.addReaction(channelid, messageid, "❤")
                
                for ser in series_list:
                    if ser in chardes and charcolor == 16751916:
                        
                        
                        logger.info(f"{charname} from {ser} appeared attempting to snipe in {guildid}")
                        time.sleep(claim_delay)
                        if "reactions" in bot.getMessage(channelid, messageid).json()[0] and bot.getMessage(channelid, messageid).json()[0]["reactions"][0]["emoji"]['id'] == None:
                            bot.addReaction(channelid, messageid, bot.getMessage(channelid, messageid).json()[0]["reactions"][0]["emoji"]["name"])
                            break
                        else:
                            bot.addReaction(channelid, messageid, "❤")
                            break

                if "<:kakera:469835869059153940>" in chardes or ("Claims:" in chardes or "Likes:" in chardes) :
                    kak_value = get_kak(chardes)
                    if int(kak_value) >= kak_min and charcolor == 16751916:
                        
                        
                        logger.info(f"{charname} with a {kak_value} Kakera Value appeared Server:{guildid}")
                        time.sleep(claim_delay)
                        if "reactions" in bot.getMessage(channelid, messageid).json()[0] and bot.getMessage(channelid, messageid).json()[0]["reactions"][0]["emoji"]['id'] == None:
                            bot.addReaction(channelid, messageid, bot.getMessage(channelid, messageid).json()[0]["reactions"][0]["emoji"]["name"])
                        else:
                            bot.addReaction(channelid, messageid, "❤")
                
                if str(user['id']) not in content and charname.lower() not in chars and get_serial(chardes) not in series_list and int(get_kak(chardes)) < kak_min:
                    logger.debug(f"Ignoring {charname} from {get_serial(chardes)} with {get_kak(chardes)} Kakera Value in Server id:{guildid}")
                    
                    
    if resp.event.reaction_added:
        r = resp.parsed.auto()
        #print(r)
        reactionid = int(r['user_id'])
        rchannelid = r["channel_id"]
        rmessageid = r["message_id"]
        rguildid = r["guild_id"]
        emoji = r["emoji"]["name"]
        emojiid = r["emoji"]['id']
        
        if reactionid == mudae and int(rchannelid) in mhids:
            
            if emojiid != None and emoji.lower() in KakeraVari:
                sendEmoji = emoji + ":" +emojiid
                react_m = bot.getMessage(rchannelid, rmessageid).json()[0]['embeds'][0]
                
                
                cooldown = kakera_wall.get(rguildid,0) - time.time()
                if cooldown <= 1:
                    logger.info(f"{emoji} was detected on {react_m['author']['name']}:{get_serial(react_m['description'])} in Server: {rguildid}")
                    time.sleep(kak_delay)
                    bot.addReaction(rchannelid,rmessageid,sendEmoji)
                else:
                    logger.info(f"Skipped {emoji} found on {react_m['author']['name']}:{get_serial(react_m['description'])} in Server: {rguildid}")
                    return 

                warn_check = mudae_warning(rchannelid)
                kakerawallwait = wait_for(bot,lambda r: warn_check(r) and 'kakera' in r.parsed.auto()['content'],timeout=5)

                if kakerawallwait != None:
                    time_to_wait = waitk_finder.findall(kakerawallwait['content'])
                else:
                    time_to_wait = []
                
                if len(time_to_wait):
                    timegetter = (int(time_to_wait[0][0] or "0")*60+int(time_to_wait[0][1] or "0"))*60
                    print(f"{timegetter} for kakera_wall was set for Server : {rguildid}")
                    kakera_wall[rguildid] = timegetter + time.time()
            
            if emojiid == None:
                if emoji in eventlist:
                    print(f"{emoji} was detected in Server: {rguildid}")
                    time.sleep(kak_delay)
                    bot.addReaction(rchannelid,rmessageid,emoji)

def poke_roll(tide):
    logger.debug(f"Pokemon Rolling Started in channel {tide}")
    tides = str(tide)
    pwait = 0
    while True:
        while pwait == 0:
            time.sleep(2)
            bot.sendMessage(tides,"$p")

            warn_check = mudae_warning(tides,False)
            varwait = wait_for(bot,lambda r: warn_check(r) and "$p" in r.parsed.auto()['content'] and "min" in r.parsed.auto()['content'],timeout=5)
            
            if varwait != None:
                pwait = get_pwait(varwait['content'])
                print(f"{pwait} : pokerolling : {tide}")
        time.sleep(pwait)
        pwait = 0

def waifu_roll(tide):
    logger.debug(f"waifu rolling Started in channel {tide}")
    tides = str(tide)
    waifuwait = 0
    while True:
        while waifuwait == 0:
            time.sleep(2)
            bot.sendMessage(tides,roll_prefix)
            
            varwait = wait_for(bot,mudae_warning(tides),timeout=5)
            
            if varwait != None:
                waifuwait = get_wait(varwait['content'])
                print(f"{waifuwait}: Waifu rolling : {tide}")
        time.sleep(waifuwait)
        waifuwait = 0

if settings['pkmrolling'].lower().strip() == "true":
    p = threading.Thread(target=poke_roll,args=(chid,))   
    p.start()
if settings['rolling'].lower().strip() == "true":
    waifus = threading.Timer(10.0,waifu_roll,args=[chid])
    waifus.start()
bot.gateway.run(auto_reconnect=True)
