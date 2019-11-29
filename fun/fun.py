import logging
from enum import Enum
from random import randint,choice
import discord
from discord.ext import commands
from dadjokes import Dadjoke
from core import checks
import box
import json
import string
from core.models import PermissionLevel

Cog = getattr(commands, "Cog", object)

logger = logging.getLogger("Modmail")


def escape(text: str, *, mass_mentions: bool = False, formatting: bool = False) -> str:
    """Get text with all mass mentions or markdown escaped.

    Parameters
    ----------
    text : str
        The text to be escaped.
    mass_mentions : `bool`, optional
        Set to :code:`True` to escape mass mentions in the text.
    formatting : `bool`, optional
        Set to :code:`True` to escpae any markdown formatting in the text.

    Returns
    -------
    str
        The escaped text.

    """
    if mass_mentions:
        text = text.replace("@everyone", "@\u200beveryone")
        text = text.replace("@here", "@\u200bhere")
    if formatting:
        text = text.replace("`", "\\`").replace("*", "\\*").replace("_", "\\_").replace("~", "\\~")
    return text

class RPS(Enum):
    rock = "\N{MOYAI}"
    paper = "\N{PAGE FACING UP}"
    scissors = "\N{BLACK SCISSORS}"

class RPSParser:
    def __init__(self, argument):
        argument = argument.lower()
        if argument == "sasso":
            self.choice = RPS.rock
        elif argument == "carta":
            self.choice = RPS.paper
        elif argument == "forbici":
            self.choice = RPS.scissors
        else:
            self.choice = None
class Divertimento(Cog):
    """Alcuni comandi divertenti"""
  
    ball = [
        "Come lo vedo, sì",
        "È certo",
        "È molto deciso",
        "Quasi piacevole",
        "Il tempo fuori è bello",
        "I segni dicono sì",
        "Non ho dubiti",
        "Sì",
        "Sì - definitivamente",
        "Puoi contarci",
        "Non ho capito bene, ritenta di nuovo",
        "Domanda di nuovo dopo",
        "È meglio se non te lo dico ora",
        "Non posso prevedere ora",
        "Concentrati e domanda di nuovo",
        "Non contarci",
        "La mia risposta è no",
        "Le mie fonti dicono di no",
        "Il tempo fuori non è tanto bello",
        "Molto dubitevole"
    ]
    def __init__(self,bot):
        super().__init__()
        self.bot = bot
        #self.db = bot.plugin_db.get_partition(self)
        
    @commands.command()
    async def choose(self, ctx, *choices):
        """Scegli tra multiple opzioni.
		
		Per denotare opzioni che includono spazi, devi usare
		le virgolette.
        """
        choices = [escape(c, mass_mentions=True) for c in choices]
        if len(choices) < 2:
            await ctx.send(_("Le opzioni necessarie non sono abbastanza per essere prese."))
        else:
            await ctx.send(choice(choices))
            
    @commands.command()
    async def roll(self, ctx, number: int = 6):
        """Lancia i dadi e ottieni un numero.

        Il risultato sarà tra 1 e `<numero>`.

        `<numero>` è impostato a 6 come predefinito.
        """
        author = ctx.author
        if number > 1:
            n = randint(1, number)
            await ctx.send("{author.mention} :game_die: {n} :game_die:".format(author=author, n=n))
        else:
            await ctx.send(_("{author.mention} Forse più alto di uno? ;P").format(author=author))
            
    @commands.command()
    async def flip(self,ctx):
        """Gira una moneta!"""
        answer = choice(["TESTA!*","CROCE!*"])
        await ctx.send(f"*Gira una moneta e...{answer}")
        
    @commands.command()
    async def rps(self,ctx,your_choice:RPSParser):
        """Gioca a Sasso, Carta, Forbici"""
        author = ctx.author
        player_choice = your_choice.choice
        if not player_choice:
            return await ctx.send("Questa non è un'opzione valida. Prova sasso, carta, forbici.")
        bot_choice = choice((RPS.rock, RPS.paper, RPS.scissors))
        cond = {
            (RPS.rock, RPS.paper): False,
            (RPS.rock, RPS.scissors): True,
            (RPS.paper, RPS.rock): True,
            (RPS.paper, RPS.scissors): False,
            (RPS.scissors, RPS.rock): False,
            (RPS.scissors, RPS.paper): True,
        }
        if bot_choice == player_choice:
            outcome = None  # Tie
        else:
            outcome = cond[(player_choice, bot_choice)]
        if outcome is True:
            await ctx.send(f"{bot_choice.value} Hai vinto {author.mention}!")
        elif outcome is False:
            await ctx.send(f"{bot_choice.value} Hai perso {author.mention}!")
        else:
            await ctx.send(f"{bot_choice.value} Siamo pari {author.mention}!")
    @commands.command(name="8ball",aliases=["8"])
    async def _8ball(self, ctx, *, question: str):
        """Domanda alla 8ball una domanda.

        La domanda deve per forza terminare con un punto interrogativo.
        """
        if question.endswith("?") and question != "?":
            await ctx.send((choice(self.ball)))
        else:
            await ctx.send("Questa non sembra una domanda.")
	
    @commands.command()
    async def lmgtfy(self, ctx, *, search_terms: str):
        """Crea un link lmgtfy."""
        search_terms = escape(
            search_terms.replace("+", "%2B").replace(" ", "+"), mass_mentions=True
        )
        await ctx.send("<https://lmgtfy.com/?q={}>".format(search_terms))
        
    @commands.command()
    async def say(self,ctx,* ,message):
        """Fai dire qualcosa al bot"""
        msg = escape(message,mass_mentions=True)
        await ctx.send(msg)
    @commands.command()
    async def reverse(self, ctx, *, text):
        """!oirartnoc la otset out li amrofsarT"""
        text =  escape("".join(list(reversed(str(text)))),mass_mentions=True)
        await ctx.send(text)
        
    @commands.command()
    async def meme(self, ctx):
        """Ottieni un meme a caso."""
        r = await self.bot.session.get("https://www.reddit.com/r/dankmemes/top.json?sort=top&t=day&limit=500")
        r = await r.json()
        r = box.Box(r)
        data = choice(r.data.children).data
        img = data.url
        title = data.title
        upvotes = data.ups
        downvotes = data.downs
        em = discord.Embed(color=ctx.author.color, title=title)
        em.set_image(url=img)
        em.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        em.set_footer(text=f"👍{upvotes} | 👎 {downvotes}")
        await ctx.send(embed=em)
    @commands.command()
    async def emojify(self, ctx, *, text: str):
        """Trasforma il tuo testo in emoji!"""
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        to_send = ""
        for char in text:
            if char == " ":
                to_send += " "
            elif char.lower() in 'qwertyuiopasdfghjklzxcvbnm':
                to_send += f":regional_indicator_{char.lower()}:  "
            elif char in '1234567890':
                numbers = {
                    "1": "one",
                    "2": "two",
                    "3": "three",
                    "4": "four",
                    "5": "five",
                    "6": "six",
                    "7": "seven",
                    "8": "eight",
                    "9": "nine",
                    "0": "zero"
                }
                to_send += f":{numbers[char]}: "
            else:
                return await ctx.send("I caratteri devono essere per forza o una lettera o un numero.")
        if len(to_send) > 2000:
            return await ctx.send("L'emoji è molto grande per entrare in un messaggio!")
        await ctx.send(to_send)
        
    @commands.command()
    @commands.guild_only()
    async def roast(self, ctx,*, user: discord.Member = None):
        '''Insulta qualcuno! Se fai pena a insultare.'''
   
        msg = f"Ehi, {user.mention}! " if user is not None else ""
        roasts = ["Ti vorrei dare un aspetto cattivo ma ne hai già uno.", "Se diventerai un uomo a due facce, almeno rendine una carina.", "L'unico modo per essere licenziato è prendere un culo di pollo e aspettare.", "Sembra che la tua faccia abbia preso fuoco e qualcuno ha provato a rimuoverlo con un martello.", "Gli scienziati dicono che l'universo è fatto di neutroni, protoni ed elettroni. Si erano dimenticati di menzionare maroni.", "Perché è accettabile per te essere un idiota, ma non per me segnalarlo?", "Solo perché ne hai uno non hai bisogno di recitare come uno.", "Un giorno andrai lontano... e spero tu rimanga lì.", "Tu non hai permesso di accedere a- anzi, io non ho permesso di accedere a te nel tuo server!", "No, quei pantaloni non ti faranno sembrare più grasso - come potrebbero?", "Se vuoi veramente sapere errori, dovresti chiedere ai tuoi genitori.", "Ehi, hai qualcosa nel tuo mento... no, la terza in basso.", "Tu sei la prova che l'evoluzione può andare al contrario.", "I cervelli non sono tutto. Nel tuo caso non sono niente.", "Sei così brutto che quando ti guardi allo specchio i tuoi riflessi sono persi.", "Veloce - controlla la tua faccia! Ho già trovato il tuo naso nei miei affari.", "È meglio lasciare a qualcuno pensare che tu sia stupido piuttosto che aprire bocca e dimostrarlo.", "Tu sei una persona così bella, intelligente, stupenda. Oh scusa, pensavo avessimo una competizione di bugie.", "Hai il diritto di rimanere in silenzio perché qualsiasi cosa tu dica potrà anche essere stupida."]
        if str(user.id) == str(ctx.bot.user.id):
            return await ctx.send(f"Uh?!! Bel tentativo! Non andrò a insultare me stesso. Piuttosto insulterò te ora.\n\n {ctx.author.mention} {choice(roasts)}")
        await ctx.send(f"{msg} {choice(roasts)}")

    @commands.command(aliases=['sc'])
    @commands.guild_only()
    async def smallcaps(self,ctx,*,message):
        """ᴄᴏɴᴠᴇʀᴛɪ ɪʟ ᴛᴜᴏ ᴛᴇꜱᴛᴏ ɪɴ ꜱᴛᴀᴍᴘᴀᴛᴇʟʟᴏ ᴍɪɴᴜꜱᴄᴏʟᴏ!!"""
        alpha = list(string.ascii_lowercase)     
        converter = ['ᴀ', 'ʙ', 'ᴄ', 'ᴅ', 'ᴇ', 'ꜰ', 'ɢ', 'ʜ', 'ɪ', 'ᴊ', 'ᴋ', 'ʟ', 'ᴍ', 'ɴ', 'ᴏ', 'ᴘ', 'ǫ', 'ʀ', 'ꜱ', 'ᴛ', 'ᴜ', 'ᴠ', 'ᴡ', 'x', 'ʏ', 'ᴢ']
        new = ""
        exact = message.lower()
        for letter in exact:
            if letter in alpha:
                index = alpha.index(letter)
                new += converter[index]
            else:
                new += letter
        await ctx.send(new)
    
            
    @commands.command()
    async def cringe(self,ctx,* ,message):
        """rEnDi iL TeStO CrInGe!!"""
        text_list = list(message) #convert string to list to be able to edit it
        for i in range(0,len(message)):
            if i % 2 == 0:
                text_list[i]= text_list[i].lower()
            else:
                text_list[i]=text_list[i].upper()
        message ="".join(text_list) #convert list back to string(message) to print it as a word
        await ctx.send(message)
        await ctx.message.delete()

      
def setup(bot):
    bot.add_cog(Divertimento(bot))    





        
    
    

    
    
