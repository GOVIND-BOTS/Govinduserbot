# Offline Shayari Repository for ICC Userbot
# Adapted for Pyrogram; shayari text is stored locally.

import random

from pyrogram import Client, filters
from ICC.modules.help import add_command_help


SHAYARI_DB = {
    "love": [
        "Aapki muskurahat meri pehchaan ban gayi,\nAapki khushi meri jaan ban gayi. ❤️",
        "Nazron se shuru hui jo chhoti si baat thi,\nAb har dua mein bas aapka hi naam hai. 🌹",
        "Zindagi khoobsurat thi, magar khaas nahi,\nAap mile toh laga ab kisi cheez ki talaash nahi. ✨",
        "Aap paas ho toh har mausam bahaar lagta hai,\nAapka saath hi mujhe mera sansaar lagta hai. 💗",
        "Na chaand ki khwahish, na sitaaron ki farmaish,\nBas aap muskura do, poori ho jaaye har khwahish. 🌙",
        "Aapki aankhon mein ek sukoon sa milta hai,\nJaise bheed mein apna koi apna sa milta hai. 🥰",
        "Mohabbat lafzon ki mohtaaj nahi hoti,\nAap saamne ho toh kisi baat ki zaroorat nahi hoti. ❤️",
        "Har roz aapko dekh kar ye ehsaas hota hai,\nKhuda ki khoobsurat rachna par yakeen aur gehra hota hai. 🌸",
        "Dil ne har dhadkan par aapka naam likha hai,\nAapko sochna hi ab mera sabse haseen silsila hai. 💞",
        "Aapki hansi se roshan meri shaam ho jaati hai,\nAapki ek baat se din ke saare gham kho jaate hain. 😊",
        "Koi wajah nahi chahiye aapko yaad karne ki,\nAap aadat nahi, wajah ho mere muskuraane ki. 💘",
        "Aap mile toh jaana khushi kise kehte hain,\nKisi ke hone se zindagi haseen kaise lagti hai. 🌷",
        "Aapke saath khamoshi bhi geet si lagti hai,\nAapki maujoodgi har kami ko poora karti hai. 💓",
        "Na vaade bade, na iraade dikhave ke,\nBas saath nibhaana hai dil se, har aane wale kal mein. 🤍",
        "Aap chaand ho ya chaandni, ye faisla mushkil hai,\nPar itna sach hai, aap se hi meri duniya mukammal hai. 🌙",
        "Aapki ek jhalak ka asar kuch yun hota hai,\nBechain dil bhi pal bhar mein shaant sa hota hai. 💝",
        "Meri har achhi dua mein aapka zikr rehta hai,\nDil ko aapka khayal sabse azeez rehta hai. 🫶",
        "Aapko paana hi mohabbat nahi hoti,\nAapki khushi chahna bhi ibaadat se kam nahi hoti. 🌹",
    ],
    "crush": [
        "Aapse baat ho jaaye toh din ban jaata hai,\nWarna achha khaasa din bhi adhoora reh jaata hai. 🙈",
        "Pata nahi aap mein kya khaas baat hai,\nAap online aao toh chehre par alag hi muskaan hai. 💗",
        "Naam aapka sunte hi muskurana aadat ban gayi,\nYe chhoti si pasand kab dil ki chahat ban gayi. 😊",
        "Kehna toh bahut kuch hai aapse,\nBas himmat har baar muskura kar reh jaati hai. 🌸",
        "Aap saamne aate ho toh alfaaz kho jaate hain,\nDil ki baatein bas aankhon mein reh jaati hain. 💕",
    ],
    "propose": [
        "Ek sawaal hai, jawaab dil se dena,\nKya meri har subah ki wajah aap banogi? ❤️",
        "Koi badi si khwahish nahi meri,\nBas har khushi mein aapka saath chahiye. 🌷",
        "Aap pasand ho, ye baat chhupana nahi chahta,\nAapka jawaab jo bhi ho, izzat se apnaana chahta. 🤍",
        "Dosti se shuru karke ek haseen safar banana hai,\nAgar aap chaho toh har mod par saath nibhana hai. 💍",
        "Dil ki ek seedhi si guzarish hai,\nKya aap meri kahaani ka khoobsurat hissa banogi? 💖",
    ],
    "sad": [
        "Khamoshi se bikharna aa gaya hai,\nHumein ab khud mein rehna aa gaya hai. 💔",
        "Dard ki mehfil mein ek naya fasaana likhenge,\nTere bina zindagi ka har lamha purana likhenge. 🥀",
        "Jisko chaha tha dil se wo door ho gaya,\nMera dil toot kar choor choor ho gaya. 🌧️",
        "Kuch yaadein muskurane nahi deti,\nKuch dooriyan bhulane nahi deti. 🖤",
    ],
    "attitude": [
        "Hukumat wo hi karta hai jiska dilon par raaj hota hai,\nYun toh har kisi ke sar par taj hota hai. 🔥",
        "Hum wo nahi jo duniya ke hisaab se chalein,\nHum apne usoolon ke saath aage badhein. 👑",
        "Khamosh zaroor hain, kamzor nahi,\nApni pehchaan ke liye kisi ke mohtaaj nahi. 🦅",
    ],
    "dosti": [
        "Dosti ka rishta sabse pyara hota hai,\nIsme har dard ka sahara hota hai. 🤝",
        "Dost wo nahi jo sirf khushi mein saath de,\nDost wo hai jo mushkil mein hausla de. 🫂",
        "Zindagi ki raahon mein bohot dost milenge,\nKuch yaadon mein, kuch dil mein rahenge. 😜",
    ],
    "motivational": [
        "Manzil unhi ko milti hai jinke sapno mein jaan hoti hai,\nPankhon se kuch nahi hota, hauslon se udaan hoti hai. 🕊️",
        "Waqt se ladkar jo naseeb badal de,\nInsaan wahi jo apni taqdeer badal de. ⏳",
        "Gir kar sambhalna hi jeet ki pehli nishaani hai,\nMehnat karte rehna, manzil abhi baaki hai. 💪",
    ],
}


def _category_list():
    return ", ".join(SHAYARI_DB)


@Client.on_message(filters.command("shayari", ".") & filters.me)
async def random_shayari(_, message):
    category = " ".join(message.command[1:]).strip().lower()
    if not category or category not in SHAYARI_DB:
        await message.edit(
            "❌ **Bhai, sahi category batao!**\n\n"
            f"📂 **Available Categories:**\n`{_category_list()}`\n\n"
            "**Usage:** `.shayari love` or `.shayari crush`"
        )
        return

    selected = random.choice(SHAYARI_DB[category])
    await message.edit(
        f"╭───〔 🎭 **{category.capitalize()} Shayari** 〕───╮\n\n"
        f"**{selected}**\n\n"
        "╰───〔 ✍️ **ICC USERBOT** 〕───╯"
    )


add_command_help(
    "shayari",
    [
        [".shayari <category>", "Send a random offline shayari."],
        [".shayari love", "Romantic shayari."],
        [".shayari crush", "Cute crush shayari."],
        [".shayari propose", "Respectful proposal shayari."],
        [".shayari sad", "Sad shayari."],
        [".shayari attitude", "Attitude shayari."],
        [".shayari dosti", "Friendship shayari."],
        [".shayari motivational", "Motivational shayari."],
    ],
)
