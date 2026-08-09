import json
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from .config import settings

LANGUAGES = {
    "hi": "\u0939\u093f\u0928\u094d\u0926\u0940",
    "kn": "\u0c95\u0ca8\u0ccd\u0ca8\u0ca1",
    "ta": "\u0ba4\u0bae\u0bbf\u0bb4\u0bcd",
    "te": "\u0c24\u0c46\u0c32\u0c41\u0c17\u0c41",
    "mr": "\u092e\u0930\u093e\u0920\u0940",
    "or": "\u0b13\u0b21\u0b3c\u0b3f\u0b06",
    "bn": "\u09ac\u09be\u0982\u09b2\u09be",
    "as": "\u0985\u09b8\u09ae\u09c0\u09af\u09bc\u09be",
    "pa": "\u0a2a\u0a70\u0a1c\u0a3e\u0a2c\u0a40",
    "gu": "\u0a97\u0ac1\u0a9c\u0ab0\u0abe\u0aa4\u0ac0",
    "ml": "\u0d2e\u0d32\u0d2f\u0d3e\u0d33\u0d02",
}

# 0-based Vedic rashi metadata (Mesha … Meena)
RASHI_META = [
    {"sign": "aries", "planet": "Mars", "element": "Fire"},
    {"sign": "taurus", "planet": "Venus", "element": "Earth"},
    {"sign": "gemini", "planet": "Mercury", "element": "Air"},
    {"sign": "cancer", "planet": "Moon", "element": "Water"},
    {"sign": "leo", "planet": "Sun", "element": "Fire"},
    {"sign": "virgo", "planet": "Mercury", "element": "Earth"},
    {"sign": "libra", "planet": "Venus", "element": "Air"},
    {"sign": "scorpio", "planet": "Mars", "element": "Water"},
    {"sign": "sagittarius", "planet": "Jupiter", "element": "Fire"},
    {"sign": "capricorn", "planet": "Saturn", "element": "Earth"},
    {"sign": "aquarius", "planet": "Saturn", "element": "Air"},
    {"sign": "pisces", "planet": "Jupiter", "element": "Water"},
]

_TERMS_PATH = Path(__file__).resolve().parents[1] / "scripts" / "terms.json"
_TERMS = json.loads(_TERMS_PATH.read_text(encoding="utf-8"))

HOROSCOPE_URL = "https://freehoroscopeapi.com/api/v1/get-horoscope/daily"
HOROSCOPE_WEEKLY_URL = "https://freehoroscopeapi.com/api/v1/get-horoscope/weekly"
HOROSCOPE_MONTHLY_URL = "https://freehoroscopeapi.com/api/v1/get-horoscope/monthly"

# Longer area write-ups (index-cycled) for expand panels — regional scripts.
_DETAIL_AREAS = {
    "hi": {
        "work": [
            "कार्यक्षेत्र में आज योजनाबद्ध कदम उठाएँ; जल्दबाज़ी से बचें और सहयोगियों से स्पष्ट संवाद रखें।",
            "दफ़्तर या व्यवसाय में धैर्य फलदायी रहेगा। छोटी जिम्मेदारियाँ पूरी कर बड़े लक्ष्य की नींव मज़बूत करें।",
            "नए प्रस्ताव पर दो बार सोचें। अनुभवी सलाह से निर्णय सरल हो सकते हैं।",
        ],
        "family": [
            "परिवार में सामंजस्य बनाए रखने के लिए सुनने का अभ्यास करें; छोटे विवादों को शांत स्वर में सुलझाएँ।",
            "घर के सदस्यों के साथ समय निकालना मानसिक शांति देगा। घरेलू व्यवस्था में सुधार शुभ।",
            "बुज़ुर्गों का आशीर्वाद लें। पारिवारिक निर्णयों में सबकी राय लें।",
        ],
        "health": [
            "नियमित जलपान, हल्की व्यायाम और पर्याप्त विश्राम स्वास्थ्य बनाए रखने में सहायक।",
            "तनाव कम करने के लिए श्वास-अभ्यास या छोटी सैर लाभदायक रहेगी।",
            "अति भोजन और देर रात जागने से बचें; शरीर की थकान पर ध्यान दें।",
        ],
        "remedy": [
            "स्वंय के राशि स्वामी की कृपा हेतु सात्विक आहार और दान-पुण्य का संकल्प रखें।",
            "सूर्योदय के बाद कुछ क्षण शांत ध्यान या प्रार्थना दिन का स्वर स्थिर कर सकती है।",
            "जल से तुलसी या पीपल के समीप कृतज्ञता व्यक्त करना पारंपरिक रूप से शुभ माना जाता है।",
        ],
        "daily": [
            "आज मन को शांत रखें, ज़रूरी काम पहले पूरे करें और अनावश्यक विवाद से बचें। संतुलित दिनचर्या लाभदायक रहेगी।",
            "आज सहयोग और स्पष्ट संवाद से काम आसान होंगे। छोटी यात्रा या मुलाक़ात शुभ संकेत दे सकती है।",
            "आज आत्म-संयम रखें। खर्च नियंत्रित रखें और स्वास्थ्य पर विशेष ध्यान दें।",
        ],
        "weekly": [
            "इस सप्ताह धैर्य और योजना से प्रगति संभव है। परिवार के साथ समय निकालना मानसिक स्थिरता देगा।",
            "सप्ताह भर नए अवसरों पर सोच-समझकर निर्णय लें। पुराने काम निपटाने पर बल दें।",
            "इस सप्ताह स्वास्थ्य और दिनचर्या सुधारने का अच्छा समय है। अधिक वचन देने से बचें।",
        ],
        "monthly": [
            "इस माह दीर्घकालिक लक्ष्यों पर ध्यान केंद्रित करें। बचत और सीखने की आदतें फलदायी रहेंगी।",
            "माह के मध्य तक सहयोगी संबंध मज़बूत हो सकते हैं। घर-परिवार संबंधी निर्णयों में सावधानी रखें।",
            "महीने भर संतुलन बनाए रखें—काम, विश्राम और साधना का समन्वय शुभ रहेगा।",
        ],
        "state_note": "इस राज्य की पंचांग परंपरा {system} कैलेंडर और {muhurat} मुहूर्त पद्धति पर आधारित है। आज का नक्षत्र {nakshatra}, तिथि {tithi}।",
    },
    "ml": {
        "work": [
            "ജോലിയിൽ ഇന്ന് ക്രമീകൃതമായ നടപടികൾ സ്വീകരിക്കുക; തിടുക്കം ഒഴിവാക്കി സഹപ്രവർത്തകരുമായി വ്യക്തമായി സംസാരിക്കുക.",
            "ക്ഷമയോടെയുള്ള ശ്രമങ്ങൾ ഫലം ചെയ്യും. ചെറിയ ജോലികൾ പൂർത്തിയാക്കി വലിയ ലക്ഷ്യത്തിന് അടിത്തറയിടുക.",
            "പുതിയ ഓഫറുകൾ രണ്ടുതവണ ആലോചിച്ച ശേഷം തീരുമാനിക്കുക. പരിചയസമ്പന്നരുടെ ഉപദേശം സഹായകമാകും.",
        ],
        "family": [
            "കുടുംബത്തിൽ ഐക്യം നിലനിർത്താൻ ശ്രദ്ധയോടെ കേൾക്കുക; ചെറിയ തർക്കങ്ങൾ ശാന്തമായി പരിഹരിക്കുക.",
            "വീട്ടുകാരുമായി സമയം ചിലവഴിക്കുന്നത് മനസ്സിന് ആശ്വാസം നൽകും.",
            "മുതിർന്നവരുടെ അനുഗ്രഹം തേടുക. കുടുംബ തീരുമാനങ്ങളിൽ എല്ലാവരുടെയും അഭിപ്രായം പരിഗണിക്കുക.",
        ],
        "health": [
            "വെള്ളം കുടിക്കുക, ലഘുവായ വ്യായാമം, മതിയായ വിശ്രമം എന്നിവ ആരോഗ്യത്തിന് അനുകൂലം.",
            "സമ്മർദ്ദം കുറയ്ക്കാൻ ശ്വാസവ്യായാമം അല്ലെങ്കിൽ ചെറിയ നടത്തം സഹായകം.",
            "അമിതഭക്ഷണവും രാത്രി വൈകിയുള്ള ഉണർവും ഒഴിവാക്കുക.",
        ],
        "remedy": [
            "രാശ്യധിപന്റെ അനുഗ്രഹത്തിനായി സാത്വിക ഭക്ഷണവും ദാനവും സ്വീകരിക്കുക.",
            "സൂര്യോദയത്തിന് ശേഷം ചെറിയ ധ്യാനം അല്ലെങ്കിൽ പ്രാർത്ഥന ദിനം സ്ഥിരപ്പെടുത്തും.",
            "നന്ദിയോടെയുള്ള ചെറിയ പൂജാകർമ്മങ്ങൾ പരമ്പരാഗതമായി ശുഭമായി കണക്കാക്കപ്പെടുന്നു.",
        ],
        "daily": [
            "ഇന്ന് മനസ്സ് ശാന്തമായി വയ്ക്കുക; പ്രധാന ജോലികൾ ആദ്യം തീർക്കുക. അനാവശ്യ തർക്കങ്ങൾ ഒഴിവാക്കുക.",
            "ഇന്ന് സഹകരണവും വ്യക്തമായ സംഭാഷണവും ഗുണം ചെയ്യും. ചെറിയ യാത്രയോ കൂടിക്കാഴ്ചയോ ശുഭസൂചന നൽകാം.",
            "ഇന്ന് ആത്മനിയന്ത്രണം പാലിക്കുക. ചെലവ് നിയന്ത്രിക്കുകയും ആരോഗ്യത്തിൽ ശ്രദ്ധിക്കുകയും ചെയ്യുക.",
        ],
        "weekly": [
            "ഈ ആഴ്ച ക്ഷമയും ആസൂത്രണവും പുരോഗതി നൽകും. കുടുംബത്തോടൊപ്പം സമയം ചിലവഴിക്കുന്നത് മനസ്സിന് സ്ഥിരത നൽകും.",
            "ആഴ്ചയിൽ പുതിയ അവസരങ്ങൾ ശ്രദ്ധാപൂർവം വിലയിരുത്തുക. പഴയ ജോലികൾ പൂർത്തിയാക്കാൻ മുൻഗണന നൽകുക.",
            "ഈ ആഴ്ച ആരോഗ്യവും ദിനചര്യയും മെച്ചപ്പെടുത്താൻ നല്ല സമയം. അമിതമായ വാഗ്ദാനങ്ങൾ ഒഴിവാക്കുക.",
        ],
        "monthly": [
            "ഈ മാസം ദീർഘകാല ലക്ഷ്യങ്ങളിൽ ശ്രദ്ധ കേന്ദ്രീകരിക്കുക. സമ്പാദ്യവും പഠനവും ഫലപ്രദമാകും.",
            "മാസമധ്യത്തോടെ ബന്ധങ്ങൾ ശക്തിപ്പെടാം. വീട്-കുടുംബ തീരുമാനങ്ങളിൽ ജാഗ്രത പാലിക്കുക.",
            "മാസം മുഴുവൻ ജോലി, വിശ്രമം, ആത്മീയ അഭ്യാസം എന്നിവയുടെ സന്തുലനം ശുഭകരം.",
        ],
        "state_note": "ഈ സംസ്ഥാനത്തെ പഞ്ചാംഗ പാരമ്പര്യം {system} കലണ്ടറും {muhurat} മുഹൂർത്ത രീതിയും അടിസ്ഥാനമാക്കിയതാണ്. ഇന്നത്തെ നക്ഷത്രം {nakshatra}, തിഥി {tithi}.",
    },
    "ta": {
        "work": [
            "பணியில் இன்று திட்டமிட்ட நடவடிக்கை எடுங்கள்; அவசரத்தை தவிர்த்து தெளிவாக பேசுங்கள்.",
            "பொறுமையுடன் செயல்பட்டால் பலன் கிடைக்கும். சிறு பணிகளை முடித்து பெரிய இலக்குக்கு அடித்தளம் அமைக்கவும்.",
            "புதிய வாய்ப்புகளை இருமுறை சிந்தித்து முடிவு செய்யுங்கள்.",
        ],
        "family": [
            "குடும்பத்தில் இணக்கத்திற்கு கவனமாகக் கேளுங்கள்; சிறு தகராறுகளை அமைதியாக தீர்க்கவும்.",
            "குடும்பத்தினருடன் நேரம் செலவிடுவது மன அமைதி தரும்.",
            "மூத்தோர் ஆசியைப் பெறுங்கள். குடும்ப முடிவுகளில் அனைவரின் கருத்தும் கேளுங்கள்.",
        ],
        "health": [
            "நீர் அருந்துதல், இலகு உடற்பயிற்சி, போதிய ஓய்வு ஆரோக்கியத்திற்கு உதவும்.",
            "மன அழுத்தத்தைக் குறைக்க மூச்சுப் பயிற்சி அல்லது நடைபயிற்சி நல்லது.",
            "அதிக உணவு மற்றும் தாமத உறக்கத்தைத் தவிர்க்கவும்.",
        ],
        "remedy": [
            "ராசி அதிபதி அருளுக்கு சாத்விக உணவும் தானமும் உதவும்.",
            "சூரிய உதயத்திற்குப் பின் சிறு தியானம் நாளை நிலைப்படுத்தும்.",
            "நன்றியுடன் செய்யும் சிறு வழிபாடு பாரம்பரியமாக நல்லதாகக் கருதப்படுகிறது.",
        ],
        "daily": [
            "இன்று மனதை அமைதியாக வையுங்கள்; முக்கிய பணிகளை முதலில் முடியுங்கள். தேவையற்ற வாக்குவாதத்தைத் தவிர்க்கவும்.",
            "இன்று ஒத்துழைப்பும் தெளிவான பேச்சும் நன்மை தரும். சிறு பயணம் அல்லது சந்திப்பு நல்ல அறிகுறியாகும்.",
            "இன்று தன்னடக்கம் அவசியம். செலவைக் கட்டுப்படுத்தி உடல்நலத்தில் கவனம் செலுத்துங்கள்.",
        ],
        "weekly": [
            "இந்த வாரம் பொறுமையும் திட்டமிடலும் முன்னேற்றம் தரும். குடும்பத்துடன் நேரம் செலவிடுவது மன நிலைத்தன்மை தரும்.",
            "வாரத்தில் புதிய வாய்ப்புகளை கவனமாக ஆராயுங்கள். பழைய பணிகளை முடிக்க முன்னுரிமை அளியுங்கள்.",
            "இந்த வாரம் உடல்நலம் மற்றும் அன்றாட ஒழுங்கை மேம்படுத்த நல்ல நேரம். அதிக வாக்குறுதி தவிர்க்கவும்.",
        ],
        "monthly": [
            "இந்த மாதம் நீண்டகால இலக்குகளில் கவனம் செலுத்துங்கள். சேமிப்பும் கற்றலும் பயனளிக்கும்.",
            "மாத நடுப்பகுதியில் உறவுகள் வலுப்பெறலாம். வீடு-குடும்ப முடிவுகளில் எச்சரிக்கையாக இருங்கள்.",
            "மாதம் முழுவதும் வேலை, ஓய்வு, ஆன்மீகப் பயிற்சி ஆகியவற்றின் சமநிலை நல்லது.",
        ],
        "state_note": "இம்மாநில பஞ்சாங்க மரபு {system} நாட்காட்டி மற்றும் {muhurat} முகூர்த்த முறையை அடிப்படையாகக் கொண்டது. இன்றைய நட்சத்திரம் {nakshatra}, திதி {tithi}.",
    },
    "kn": {
        "work": [
            "ಕೆಲಸದಲ್ಲಿ ಇಂದು ಯೋಜಿತ ಹೆಜ್ಜೆಗಳನ್ನು ಇಡಿ; ಆತುರ ತಪ್ಪಿಸಿ ಸ್ಪಷ್ಟ ಸಂವಾದ ಇರಲಿ.",
            "ತಾಳ್ಮೆಯಿಂದ ಕೆಲಸ ಮಾಡಿದರೆ ಫಲ ಸಿಗುತ್ತದೆ. ಸಣ್ಣ ಕಾರ್ಯಗಳನ್ನು ಪೂರೈಸಿ ದೊಡ್ಡ ಗುರಿಗೆ ಅಡಿಪಾಯ ಹಾಕಿ.",
            "ಹೊಸ ಪ್ರಸ್ತಾವನೆಗಳನ್ನು ಎರಡು ಬಾರಿ ಯೋಚಿಸಿ ನಿರ್ಧರಿಸಿ.",
        ],
        "family": [
            "ಕುಟುಂಬದಲ್ಲಿ ಸಾಮರಸ್ಯಕ್ಕಾಗಿ ಗಮನವಿಟ್ಟು ಕೇಳಿ; ಸಣ್ಣ ವಿವಾದಗಳನ್ನು ಶಾಂತವಾಗಿ ಬಗೆಹರಿಸಿ.",
            "ಮನೆಯವರೊಂದಿಗೆ ಸಮಯ ಕಳೆಯುವುದು ಮನಶ್ಶಾಂತಿ ನೀಡುತ್ತದೆ.",
            "ಹಿರಿಯರ ಆಶೀರ್ವಾದ ಪಡೆಯಿರಿ. ಕುಟುಂಬ ನಿರ್ಧಾರಗಳಲ್ಲಿ ಎಲ್ಲರ ಅಭಿಪ್ರಾಯ ಪಡೆಯಿರಿ.",
        ],
        "health": [
            "ನೀರು ಕುಡಿಯುವುದು, ಹಗುರ ವ್ಯಾಯಾಮ, ಸಾಕಷ್ಟು ವಿಶ್ರಾಂತಿ ಆರೋಗ್ಯಕ್ಕೆ ಸಹಾಯಕ.",
            "ಒತ್ತಡ ಕಡಿಮೆ ಮಾಡಲು ಉಸಿರಾಟ ಅಭ್ಯಾಸ ಅಥವಾ ನಡಿಗೆ ಉತ್ತಮ.",
            "ಅತಿಯಾದ ಆಹಾರ ಮತ್ತು ರಾತ್ರಿ ತಡವಾಗಿ ಎಚ್ಚರವಿರುವುದನ್ನು ತಪ್ಪಿಸಿ.",
        ],
        "remedy": [
            "ರಾಶ್ಯಧಿಪತಿ ಅನುಗ್ರಹಕ್ಕಾಗಿ ಸಾತ್ವಿಕ ಆಹಾರ ಮತ್ತು ದಾನ ಅಭ್ಯಾಸ ಮಾಡಿ.",
            "ಸೂರ್ಯೋದಯದ ನಂತರ ಸಣ್ಣ ಧ್ಯಾನ ದಿನವನ್ನು ಸ್ಥಿರಗೊಳಿಸಬಹುದು.",
            "ಕೃತಜ್ಞತೆಯ ಸಣ್ಣ ಪೂಜಾ ಕಾರ್ಯಗಳು ಪಾರಂಪರಿಕವಾಗಿ ಶುಭ.",
        ],
        "daily": [
            "ಇಂದು ಮನಸ್ಸನ್ನು ಶಾಂತವಾಗಿರಿಸಿ; ಮುಖ್ಯ ಕೆಲಸಗಳನ್ನು ಮೊದಲು ಮುಗಿಸಿ. ಅನಗತ್ಯ ವಾದಗಳನ್ನು ತಪ್ಪಿಸಿ.",
            "ಇಂದು ಸಹಕಾರ ಮತ್ತು ಸ್ಪಷ್ಟ ಮಾತು ಲಾಭಕರ. ಸಣ್ಣ ಪ್ರಯಾಣ ಅಥವಾ ಭೇಟಿ ಶುಭ ಸೂಚನೆ ನೀಡಬಹುದು.",
            "ಇಂದು ಆತ್ಮಸಂಯಮ ಅಗತ್ಯ. ಖರ್ಚು ನಿಯಂತ್ರಿಸಿ ಆರೋಗ್ಯಕ್ಕೆ ಗಮನ ಕೊಡಿ.",
        ],
        "weekly": [
            "ಈ ವಾರ ತಾಳ್ಮೆ ಮತ್ತು ಯೋಜನೆಯಿಂದ ಪ್ರಗತಿ ಸಾಧ್ಯ. ಕುಟುಂಬದೊಂದಿಗೆ ಸಮಯ ಕಳೆಯುವುದು ಮಾನಸಿಕ ಸ್ಥಿರತೆ ನೀಡುತ್ತದೆ.",
            "ವಾರದಲ್ಲಿ ಹೊಸ ಅವಕಾಶಗಳನ್ನು ಎಚ್ಚರಿಕೆಯಿಂದ ಪರಿಗಣಿಸಿ. ಹಳೆಯ ಕೆಲಸಗಳನ್ನು ಮುಗಿಸಲು ಆದ್ಯತೆ ನೀಡಿ.",
            "ಈ ವಾರ ಆರೋಗ್ಯ ಮತ್ತು ದಿನಚರಿ ಸುಧಾರಿಸಲು ಒಳ್ಳೆಯ ಸಮಯ. ಅತಿಯಾದ ಭರವಸೆಗಳನ್ನು ತಪ್ಪಿಸಿ.",
        ],
        "monthly": [
            "ಈ ತಿಂಗಳು ದೀರ್ಘಕಾಲೀನ ಗುರಿಗಳ ಮೇಲೆ ಗಮನ ಹರಿಸಿ. ಉಳಿತಾಯ ಮತ್ತು ಕಲಿಕೆ ಫಲಕಾರಿ.",
            "ತಿಂಗಳ ಮಧ್ಯದಲ್ಲಿ ಸಂಬಂಧಗಳು ಬಲಗೊಳ್ಳಬಹುದು. ಮನೆ-ಕುಟುಂಬ ನಿರ್ಧಾರಗಳಲ್ಲಿ ಎಚ್ಚರಿಕೆ ವಹಿಸಿ.",
            "ತಿಂಗಳಿನಾದ್ಯಂತ ಕೆಲಸ, ವಿಶ್ರಾಂತಿ ಮತ್ತು ಆಧ್ಯಾತ್ಮಿಕ ಅಭ್ಯಾಸದ ಸಮತೋಲನ ಶುಭ.",
        ],
        "state_note": "ಈ ರಾಜ್ಯದ ಪಂಚಾಂಗ ಪರಂಪರೆ {system} ಕ್ಯಾಲೆಂಡರ್ ಮತ್ತು {muhurat} ಮುಹೂರ್ತ ವಿಧಾನವನ್ನು ಆಧರಿಸಿದೆ. ಇಂದಿನ ನಕ್ಷತ್ರ {nakshatra}, ತಿಥಿ {tithi}.",
    },
    "te": {
        "work": [
            "ఈరోజు పనిలో ప్రణాళికతో ముందుకు సాగండి; తొందరపాటు మాని స్పష్టంగా మాట్లాడండి.",
            "ఓర్పుతో చేసిన ప్రయత్నాలు ఫలిస్తాయి. చిన్న పనులు పూర్తి చేసి పెద్ద లక్ష్యానికి పునాది వేయండి.",
            "కొత్త ప్రతిపాదనలపై రెండుసార్లు ఆలోచించి నిర్ణయం తీసుకోండి.",
        ],
        "family": [
            "కుటుంబంలో సామరస్యం కోసం శ్రద్ధగా వినండి; చిన్న వివాదాలను ప్రశాంతంగా పరిష్కరించండి.",
            "ఇంటివారితో సమయం గడపడం మానసిక శాంతినిస్తుంది.",
            "పెద్దల ఆశీస్సులు పొందండి. కుటుంబ నిర్ణయాల్లో అందరి అభిప్రాయం తీసుకోండి.",
        ],
        "health": [
            "నీరు తాగడం, తేలికపాటి వ్యాయామం, తగిన విశ్రాంతి ఆరోగ్యానికి మేలు చేస్తాయి.",
            "ఒత్తిడి తగ్గించడానికి శ్వాస వ్యాయామం లేదా నడక ఉపయోగపడుతుంది.",
            "అధిక భోజనం మరియు ఆలస్య నిద్రను నివారించండి.",
        ],
        "remedy": [
            "రాశ్యధిపతి అనుగ్రహం కోసం సాత్విక ఆహారం మరియు దానం చేయండి.",
            "సూర్యోదయం తర్వాత కొద్ది ధ్యానం రోజును స్థిరపరుస్తుంది.",
            "కృతజ్ఞతతో చేసే చిన్న పూజా కార్యాలు సాంప్రదాయంగా శుభం.",
        ],
        "daily": [
            "ఈరోజు మనసు ప్రశాంతంగా ఉంచండి; ముఖ్య పనులు ముందుగా పూర్తి చేయండి. అనవసర వాదాలు మానండి.",
            "ఈరోజు సహకారం మరియు స్పష్ట సంభాషణ లాభదాయకం. చిన్న ప్రయాణం లేదా కలయిక శుభసూచన.",
            "ఈరోజు ఆత్మనియంత్రణ అవసరం. ఖర్చులు నియంత్రించి ఆరోగ్యంపై దృష్టి పెట్టండి.",
        ],
        "weekly": [
            "ఈ వారం ఓర్పు మరియు ప్రణాళికతో పురోగతి సాధ్యం. కుటుంబంతో సమయం గడపడం మానసిక స్థిరత్వం ఇస్తుంది.",
            "వారంలో కొత్త అవకాశాలను జాగ్రత్తగా పరిశీలించండి. పాత పనులు పూర్తి చేయడానికి ప్రాధాన్యత ఇవ్వండి.",
            "ఈ వారం ఆరోగ్యం మరియు దినచర్య మెరుగుపరచడానికి మంచి సమయం. అధిక వాగ్దానాలు మానండి.",
        ],
        "monthly": [
            "ఈ నెల దీర్ఘకాలిక లక్ష్యాలపై దృష్టి పెట్టండి. పొదుపు మరియు నేర్చుకోవడం ఫలిస్తాయి.",
            "నెల మధ్యలో సంబంధాలు బలపడవచ్చు. ఇల్లు-కుటుంబ నిర్ణయాల్లో జాగ్రత్త వహించండి.",
            "నెలంతా పని, విశ్రాంతి, ఆధ్యాత్మిక అభ్యాసం మధ్య సమతుల్యత శుభం.",
        ],
        "state_note": "ఈ రాష్ట్ర పంచాంగ సంప్రదాయం {system} క్యాలెండర్ మరియు {muhurat} ముహూర్త పద్ధతిపై ఆధారపడి ఉంది. నేటి నక్షత్రం {nakshatra}, తిథి {tithi}.",
    },
    "mr": {
        "work": [
            "आज कामात नियोजित पावले उचला; घाई टाळा आणि स्पष्ट संवाद साधा.",
            "धीराने केलेले प्रयत्न फलदायी ठरतील. छोटी कामे पूर्ण करून मोठ्या ध्येयाचा पाया भक्कम करा.",
            "नवीन प्रस्ताव दोनदा विचारून ठरवा.",
        ],
        "family": [
            "कुटुंबात सामंजस्य राखण्यासाठी लक्ष देऊन ऐका; छोटे वाद शांतपणे मिटवा.",
            "घरातील मंडळींसोबत वेळ घालवणे मानसिक शांती देईल.",
            "वडीलधाऱ्यांचे आशीर्वाद घ्या. कौटुंबिक निर्णयांमध्ये सर्वांचे मत विचारात घ्या.",
        ],
        "health": [
            "पाणी पिणे, हलका व्यायाम आणि पुरेशी विश्रांती आरोग्यासाठी हितकारक.",
            "तणाव कमी करण्यासाठी श्वसन अभ्यास किंवा छोटी चाला उपयुक्त.",
            "अतिभोजन आणि उशिरा जागणे टाळा.",
        ],
        "remedy": [
            "राशीस्वामीच्या कृपेसाठी सात्त्विक आहार व दान करण्याचा संकल्प ठेवा.",
            "सूर्योदयानंतर थोडा ध्यानकिंवा प्रार्थना दिवस स्थिर करते.",
            "कृतज्ञतेने केलेली छोटी पूजा परंपरेने शुभ मानली जाते.",
        ],
        "daily": [
            "आज मन शांत ठेवा; महत्त्वाची कामे आधी पूर्ण करा. अनावश्यक वादांपासून दूर रहा.",
            "आज सहयोग आणि स्पष्ट संभाषण फायदेशीर. छोटी यात्रा किंवा भेट शुभ संकेत देऊ शकते.",
            "आज आत्मसंयम आवश्यक. खर्च नियंत्रित ठेवा आणि आरोग्याकडे लक्ष द्या.",
        ],
        "weekly": [
            "या आठवड्यात धीर व नियोजनाने प्रगती शक्य. कुटुंबासोबत वेळ घालवणे मानसिक स्थैर्य देईल.",
            "आठवड्यात नवीन संधी सावधपणे तपासा. जुनी कामे पूर्ण करण्यास प्राधान्य द्या.",
            "या आठवड्यात आरोग्य व दिनचर्या सुधारण्याची चांगली वेळ. जास्त वचन देणे टाळा.",
        ],
        "monthly": [
            "या महिन्यात दीर्घकालीन उद्दिष्टांवर लक्ष केंद्रित करा. बचत व अध्ययन फलदायी ठरेल.",
            "महिन्याच्या मध्यात नाती मजबूत होऊ शकतात. घर-कुटुंबातील निर्णयांमध्ये सावध रहा.",
            "महिनाभर काम, विश्रांती आणि आध्यात्मिक अभ्यासाचा समतोल शुभ.",
        ],
        "state_note": "या राज्याची पंचांग परंपरा {system} दिनदर्शिका आणि {muhurat} मुहूर्त पद्धतीवर आधारित आहे. आजचा नक्षत्र {nakshatra}, तिथि {tithi}.",
    },
    "gu": {
        "work": [
            "આજે કામમાં યોજના સાથે આગળ વધો; ઉતાવળ ટાળો અને સ્પષ્ટ સંવાદ રાખો.",
            "ધીરજથી કરેલા પ્રયત્નો ફળ આપશે. નાનાં કામ પૂરાં કરી મોટા લક્ષ્યનો પાયો મજબૂત કરો.",
            "નવી દરખાસ્તો પર બે વાર વિચારીને નિર્ણય લો.",
        ],
        "family": [
            "કુટુંબમાં સુમેળ માટે ધ્યાનથી સાંભળો; નાના વિવાદો શાંતિથી ઉકેલો.",
            "ઘરના સભ્યો સાથે સમય પસાર કરવો માનસિક શાંતિ આપે.",
            "વડીલોના આશીર્વાદ લો. કૌટુંબિક નિર્ણયોમાં સૌની સલાહ ધ્યાને લો.",
        ],
        "health": [
            "પાણી પીવું, હળવી કસરત અને પૂરતી આરામ આરોગ્ય માટે હિતકારક.",
            "તણાવ ઘટાડવા શ્વાસની કસરત કે ટૂંકી ચાલ ઉપયોગી.",
            "અતિભોજન અને મોડી ઊંઘ ટાળો.",
        ],
        "remedy": [
            "રાશિસ્વામીની કૃપા માટે સાત્વિક આહાર અને દાનનો સંકલ્પ રાખો.",
            "સૂર્યોદય પછી થોડું ધ્યાન દિવસને સ્થિર કરે.",
            "કૃતજ્ઞતાથી કરેલી નાની પૂજા પરંપરાગત રીતે શુભ.",
        ],
        "daily": [
            "આજે મન શાંત રાખો; મહત્વનાં કામ પહેલાં પૂરાં કરો. અનાવશ્યક વાદથી દૂર રહો.",
            "આજે સહકાર અને સ્પષ્ટ વાતચીત લાભદાયક. ટૂંકી મુલાકાત શુભ સંકેત આપી શકે.",
            "આજે આત્મનિયંત્રણ જરૂરી. ખર્ચ કાબૂમાં રાખો અને સ્વાસ્થ્ય પર ધ્યાન આપો.",
        ],
        "weekly": [
            "આ અઠવાડિયે ધીરજ અને આયોજનથી પ્રગતિ શક્ય. કુટુંબ સાથે સમય માનસિક સ્થિરતા આપે.",
            "અઠવાડિયે નવી તકો કાળજીપૂર્વક તપાસો. જૂનાં કામ પૂરાં કરવાને પ્રાધાન્ય આપો.",
            "આ અઠવાડિયે આરોગ્ય અને દિનચર્યા સુધારવાનો સારો સમય. વધુ વચનો ટાળો.",
        ],
        "monthly": [
            "આ મહિને લાંબા ગાળાના લક્ષ્યો પર ધ્યાન કેન્દ્રિત કરો. બચત અને અભ્યાસ ફળદાયી.",
            "મહિનાના મધ્યમાં સંબંધો મજબૂત થઈ શકે. ઘર-કુટુંબના નિર્ણયોમાં સાવધાન રહો.",
            "મહિના ભર કામ, આરામ અને આધ્યાત્મિક અભ્યાસનું સંતુલન શુભ.",
        ],
        "state_note": "આ રાજ્યની પંચાંગ પરંપરા {system} કેલેન્ડર અને {muhurat} મુહૂર્ત પદ્ધતિ પર આધારિત છે. આજનું નક્ષત્ર {nakshatra}, તિથિ {tithi}.",
    },
    "pa": {
        "work": [
            "ਅੱਜ ਕੰਮ ਵਿੱਚ ਯੋਜਨਾਬੱਧ ਕਦਮ ਚੁੱਕੋ; ਜਲਦਬਾਜ਼ੀ ਤੋਂ ਬਚੋ ਅਤੇ ਸਪਸ਼ਟ ਗੱਲਬਾਤ ਰੱਖੋ.",
            "ਧੀਰਜ ਨਾਲ ਕੀਤੀ ਮਿਹਨਤ ਫਲ ਦੇਵੇਗੀ। ਛੋਟੇ ਕੰਮ ਪੂਰੇ ਕਰਕੇ ਵੱਡੇ ਟੀਚੇ ਦੀ ਨੀਂਹ ਮਜ਼ਬੂਤ ਕਰੋ.",
            "ਨਵੀਆਂ ਪੇਸ਼ਕਸ਼ਾਂ ਬਾਰੇ ਦੋ ਵਾਰ ਸੋਚ ਕੇ ਫੈਸਲਾ ਲਓ.",
        ],
        "family": [
            "ਪਰਿਵਾਰ ਵਿੱਚ ਸੁਮੇਲ ਲਈ ਧਿਆਨ ਨਾਲ ਸੁਣੋ; ਛੋਟੇ ਝਗੜੇ ਸ਼ਾਂਤੀ ਨਾਲ ਹੱਲ ਕਰੋ.",
            "ਘਰ ਵਾਲਿਆਂ ਨਾਲ ਸਮਾਂ ਬਿਤਾਉਣਾ ਮਾਨਸਿਕ ਸ਼ਾਂਤੀ ਦੇਵੇਗਾ.",
            "ਬਜ਼ੁਰਗਾਂ ਦਾ ਅਸ਼ੀਰਵਾਦ ਲਓ. ਪਰਿਵਾਰਕ ਫੈਸਲਿਆਂ ਵਿੱਚ ਸਭ ਦੀ ਰਾਏ ਲਓ.",
        ],
        "health": [
            "ਪਾਣੀ ਪੀਣਾ, ਹਲਕੀ ਕਸਰਤ ਅਤੇ ਢੁਕਵੀਂ ਆਰਾਮ ਸਿਹਤ ਲਈ ਲਾਭਦਾਇਕ.",
            "ਤਣਾਅ ਘਟਾਉਣ ਲਈ ਸਾਹ ਦੀ ਕਸਰਤ ਜਾਂ ਛੋਟੀ ਸੈਰ ਲਾਹੇਵੰਦ.",
            "ਜ਼ਿਆਦਾ ਖਾਣਾ ਅਤੇ ਦੇਰ ਨਾਲ ਸੌਣ ਤੋਂ ਬਚੋ.",
        ],
        "remedy": [
            "ਰਾਸ਼ੀ ਸੁਆਮੀ ਦੀ ਕਿਰਪਾ ਲਈ ਸਾਤਵਿਕ ਖੁਰਾਕ ਅਤੇ ਦਾਨ ਦਾ ਸੰਕਲਪ ਰੱਖੋ.",
            "ਸੂਰਜ ਚੜ੍ਹਨ ਤੋਂ ਬਾਅਦ ਥੋੜ੍ਹਾ ਧਿਆਨ ਦਿਨ ਨੂੰ ਸਥਿਰ ਕਰਦਾ ਹੈ.",
            "ਧੰਨਵਾਦ ਨਾਲ ਕੀਤੀ ਛੋਟੀ ਪੂਜਾ ਰਵਾਇਤੀ ਤੌਰ ਤੇ ਸ਼ੁਭ ਮੰਨੀ ਜਾਂਦੀ ਹੈ.",
        ],
        "daily": [
            "ਅੱਜ ਮਨ ਸ਼ਾਂਤ ਰੱਖੋ; ਮਹੱਤਵਪੂਰਨ ਕੰਮ ਪਹਿਲਾਂ ਪੂਰੇ ਕਰੋ. ਬੇਲੋੜੀਆਂ ਬਹਿਸਾਂ ਤੋਂ ਦੂਰ ਰਹੋ.",
            "ਅੱਜ ਸਹਿਯੋਗ ਅਤੇ ਸਪਸ਼ਟ ਗੱਲਬਾਤ ਲਾਭਦਾਇਕ. ਛੋਟੀ ਮੁਲਾਕਾਤ ਸ਼ੁਭ ਸੰਕੇਤ ਦੇ ਸਕਦੀ ਹੈ.",
            "ਅੱਜ ਆਤਮ-ਨਿਯੰਤਰਣ ਲੋੜੀਂਦਾ ਹੈ. ਖਰਚ ਕਾਬੂ ਵਿੱਚ ਰੱਖੋ ਅਤੇ ਸਿਹਤ ਵੱਲ ਧਿਆਨ ਦਿਓ.",
        ],
        "weekly": [
            "ਇਸ ਹਫ਼ਤੇ ਧੀਰਜ ਅਤੇ ਯੋਜਨਾ ਨਾਲ ਤਰੱਕੀ ਸੰਭਵ. ਪਰਿਵਾਰ ਨਾਲ ਸਮਾਂ ਮਾਨਸਿਕ ਸਥਿਰਤਾ ਦੇਵੇਗਾ.",
            "ਹਫ਼ਤੇ ਵਿੱਚ ਨਵੀਆਂ ਮੌਕਿਆਂ ਨੂੰ ਧਿਆਨ ਨਾਲ ਵੇਖੋ. ਪੁਰਾਣੇ ਕੰਮ ਪਹਿਲਾਂ ਪੂਰੇ ਕਰੋ.",
            "ਇਸ ਹਫ਼ਤੇ ਸਿਹਤ ਅਤੇ ਰੁਟੀਨ ਸੁਧਾਰਨ ਦਾ ਚੰਗਾ ਸਮਾਂ. ਵਾਅਦੇ ਘੱਟ ਕਰੋ.",
        ],
        "monthly": [
            "ਇਸ ਮਹੀਨੇ ਲੰਬੇ ਸਮੇਂ ਦੇ ਟੀਚਿਆਂ ਤੇ ਧਿਆਨ ਕੇਂਦਰਿਤ ਕਰੋ. ਬਚਤ ਅਤੇ ਸਿੱਖਣਾ ਫਲਦਾਇਕ.",
            "ਮਹੀਨੇ ਦੇ ਵਿਚਕਾਰ ਰਿਸ਼ਤੇ ਮਜ਼ਬੂਤ ਹੋ ਸਕਦੇ ਹਨ. ਘਰ-ਪਰਿਵਾਰ ਦੇ ਫੈਸਲਿਆਂ ਵਿੱਚ ਸਾਵਧਾਨ ਰਹੋ.",
            "ਮਹੀਨੇ ਭਰ ਕੰਮ, ਆਰਾਮ ਅਤੇ ਅਧਿਆਤਮਿਕ ਅਭਿਆਸ ਦਾ ਸੰਤੁਲਨ ਸ਼ੁਭ.",
        ],
        "state_note": "ਇਸ ਰਾਜ ਦੀ ਪੰਚਾਂਗ ਪਰੰਪਰਾ {system} ਕੈਲੰਡਰ ਅਤੇ {muhurat} ਮੁਹੂਰਤ ਵਿਧੀ ਤੇ ਆਧਾਰਿਤ ਹੈ. ਅੱਜ ਦਾ ਨਖੱਤਰ {nakshatra}, ਤਿੱਥੀ {tithi}.",
    },
    "or": {
        "work": [
            "ଆଜି କାର୍ଯ୍ୟରେ ଯୋଜନା ସହିତ ଆଗକୁ ବଢନ୍ତୁ; ତରବର ଏଡ଼ାନ୍ତୁ ଏବଂ ସ୍ପଷ୍ଟ କଥାବାର୍ତ୍ତା ରଖନ୍ତୁ।",
            "ଧୈର୍ଯ୍ୟରେ କରାଯାଇଥିବା ପ୍ରୟାସ ଫଳପ୍ରଦ ହେବ। ଛୋଟ କାମ ସାରି ବଡ଼ ଲକ୍ଷ୍ୟର ଭିତ୍ତି ମଜବୁତ କରନ୍ତୁ।",
            "ନୂଆ ପ୍ରସ୍ତାବ ଉପରେ ଦୁଇଥର ଭାବି ନିଷ୍ପତ୍ତି ନିଅନ୍ତୁ।",
        ],
        "family": [
            "ପରିବାରରେ ସାମଞ୍ଜସ୍ୟ ପାଇଁ ଧ୍ୟାନରେ ଶୁଣନ୍ତୁ; ଛୋଟ ବିବାଦ ଶାନ୍ତିରେ ସମାଧାନ କରନ୍ତୁ।",
            "ଘରର ଲୋକଙ୍କ ସହିତ ସମୟ କଟାଇବା ମାନସିକ ଶାନ୍ତି ଦେବ।",
            "ବଡ଼ମାନଙ୍କ ଆଶୀର୍ବାଦ ନିଅନ୍ତୁ। ପାରିବାରିକ ନିଷ୍ପତ୍ତିରେ ସମସ୍ତଙ୍କ ମତ ନିଅନ୍ତୁ।",
        ],
        "health": [
            "ପାଣି ପିଇବା, ହାଲୁକା ବ୍ୟାୟାମ ଏବଂ ପର୍ଯ୍ୟାପ୍ତ ବିଶ୍ରାମ ସ୍ୱାସ୍ଥ୍ୟ ପାଇଁ ଲାଭଦାୟକ।",
            "ଚାପ କମାଇବାକୁ ଶ୍ୱାସ ଅଭ୍ୟାସ କିମ୍ବା ଛୋଟ ଚାଲିବା ଉପଯୋଗୀ।",
            "ଅତିଭୋଜନ ଏବଂ ବିଳମ୍ବରେ ଶୋଇବା ଏଡ଼ାନ୍ତୁ।",
        ],
        "remedy": [
            "ରାଶି ସ୍ୱାମୀଙ୍କ କୃପା ପାଇଁ ସାତ୍ତ୍ୱିକ ଆହାର ଏବଂ ଦାନର ସଙ୍କଳ୍ପ ରଖନ୍ତୁ।",
            "ସୂର୍ଯ୍ୟୋଦୟ ପରେ ଅଳ୍ପ ଧ୍ୟାନ ଦିନକୁ ସ୍ଥିର କରେ।",
            "କୃତଜ୍ଞତାରେ କରାଯାଇଥିବା ଛୋଟ ପୂଜା ପରମ୍ପରାରେ ଶୁଭ।",
        ],
        "daily": [
            "ଆଜି ମନ ଶାନ୍ତ ରଖନ୍ତୁ; ଗୁରୁତ୍ୱପୂର୍ଣ୍ଣ କାମ ପ୍ରଥମେ ସାରନ୍ତୁ। ଅନାବଶ୍ୟକ ବାଦାନୁବାଦରୁ ଦୂରେ ରୁହନ୍ତୁ।",
            "ଆଜି ସହଯୋଗ ଏବଂ ସ୍ପଷ୍ଟ କଥା ଲାଭଦାୟକ। ଛୋଟ ସାକ୍ଷାତ ଶୁଭ ସଙ୍କେତ ଦେଇପାରେ।",
            "ଆଜି ଆତ୍ମନିୟନ୍ତ୍ରଣ ଦରକାର। ଖର୍ଚ୍ଚ ନିୟନ୍ତ୍ରଣ କରନ୍ତୁ ଏବଂ ସ୍ୱାସ୍ଥ୍ୟ ପ୍ରତି ଧ୍ୟାନ ଦିଅନ୍ତୁ।",
        ],
        "weekly": [
            "ଏହି ସପ୍ତାହରେ ଧୈର୍ଯ୍ୟ ଓ ଯୋଜନାରେ ପ୍ରଗତି ସମ୍ଭବ। ପରିବାର ସହିତ ସମୟ ମାନସିକ ସ୍ଥିରତା ଦେବ।",
            "ସପ୍ତାହରେ ନୂଆ ସୁଯୋଗ ସାବଧାନତାର ସହିତ ଦେଖନ୍ତୁ। ପୁରୁଣା କାମ ପ୍ରଥମେ ସାରନ୍ତୁ।",
            "ଏହି ସପ୍ତାହରେ ସ୍ୱାସ୍ଥ୍ୟ ଓ ଦିନଚର୍ଯ୍ୟା ସୁଧାରିବାର ଭଲ ସମୟ। ଅଧିକ ପ୍ରତିଜ୍ଞା ଏଡ଼ାନ୍ତୁ।",
        ],
        "monthly": [
            "ଏହି ମାସରେ ଦୀର୍ଘକାଳୀନ ଲକ୍ଷ୍ୟ ଉପରେ ଧ୍ୟାନ ଦିଅନ୍ତୁ। ସଞ୍ଚୟ ଓ ଶିକ୍ଷା ଫଳପ୍ରଦ।",
            "ମାସ ମଧ୍ୟରେ ସମ୍ପର୍କ ମଜବୁତ ହୋଇପାରେ। ଘର-ପରିବାର ନିଷ୍ପତ୍ତିରେ ସାବଧାନ ରୁହନ୍ତୁ।",
            "ମାସ ସାରା କାମ, ବିଶ୍ରାମ ଓ ଆଧ୍ୟାତ୍ମିକ ଅଭ୍ୟାସର ସନ୍ତୁଳନ ଶୁଭ।",
        ],
        "state_note": "ଏହି ରାଜ୍ୟର ପଞ୍ଚାଙ୍ଗ ପରମ୍ପରା {system} କ୍ୟାଲେଣ୍ଡର ଏବଂ {muhurat} ମୁହୂର୍ତ୍ତ ପଦ୍ଧତି ଉପରେ ଆଧାରିତ। ଆଜିର ନକ୍ଷତ୍ର {nakshatra}, ତିଥି {tithi}।",
    },
    "bn": {
        "work": [
            "আজ কাজে পরিকল্পিত পদক্ষেপ নিন; তাড়াহুড়ো এড়িয়ে স্পষ্ট কথা বলুন।",
            "ধৈর্যের সঙ্গে করা চেষ্টা ফলদায়ক হবে। ছোট কাজ শেষ করে বড় লক্ষ্যের ভিত মজবুত করুন।",
            "নতুন প্রস্তাব দুবার ভেবে সিদ্ধান্ত নিন।",
        ],
        "family": [
            "পরিবারে মিল রাখতে মনোযোগ দিয়ে শুনুন; ছোট বিবাদ শান্তভাবে মেটান।",
            "পরিবারের সঙ্গে সময় কাটানো মানসিক শান্তি দেয়।",
            "বড়দের আশীর্বাদ নিন। পারিবারিক সিদ্ধান্তে সবার মত নিন।",
        ],
        "health": [
            "জলপান, হালকা ব্যায়াম ও পর্যাপ্ত বিশ্রাম স্বাস্থ্যের জন্য সহায়ক।",
            "চাপ কমাতে শ্বাসঅভ্যাস বা হাঁটা উপকারী।",
            "অতিভোজন ও দেরিতে ঘুম এড়িয়ে চলুন।",
        ],
        "remedy": [
            "রাশিস্বামীর কৃপার জন্য সাত্ত্বিক আহার ও দানের সংকল্প রাখুন।",
            "সূর্যোদয়ের পর কিছুক্ষণ ধ্যান দিনটিকে স্থির করে।",
            "কৃতজ্ঞতায় করা ছোট পূজা ঐতিহ্যগত শুভ।",
        ],
        "daily": [
            "আজ মন শান্ত রাখুন; গুরুত্বপূর্ণ কাজ আগে শেষ করুন। অপ্রয়োজনীয় তর্ক এড়িয়ে চলুন।",
            "আজ সহযোগিতা ও স্পষ্ট কথা লাভজনক। ছোট সাক্ষাৎ শুভ ইঙ্গিত দিতে পারে।",
            "আজ আত্মসংযম দরকার। খরচ নিয়ন্ত্রণে রাখুন ও স্বাস্থ্যে মনোযোগ দিন।",
        ],
        "weekly": [
            "এই সপ্তাহে ধৈর্য ও পরিকল্পনায় অগ্রগতি সম্ভব। পরিবারের সঙ্গে সময় মানসিক স্থিরতা দেয়।",
            "সপ্তাহে নতুন সুযোগ সাবধানে দেখুন। পুরোনো কাজ আগে শেষ করুন।",
            "এই সপ্তাহে স্বাস্থ্য ও দিনচর্যা উন্নতির ভালো সময়। অতিরিক্ত প্রতিশ্রুতি এড়ান।",
        ],
        "monthly": [
            "এই মাসে দীর্ঘমেয়াদি লক্ষ্যে মনোযোগ দিন। সঞ্চয় ও শিক্ষা ফলদায়ক।",
            "মাসের মাঝামাঝি সম্পর্ক মজবুত হতে পারে। ঘর-পরিবারের সিদ্ধান্তে সাবধান থাকুন।",
            "মাসজুড়ে কাজ, বিশ্রাম ও আধ্যাত্মিক অনুশীলনের ভারসাম্য শুভ।",
        ],
        "state_note": "এই রাজ্যের পঞ্জিকা ঐতিহ্য {system} ক্যালেন্ডার ও {muhurat} মুহূর্ত পদ্ধতির উপর ভিত্তি করে। আজকের নক্ষত্র {nakshatra}, তিথি {tithi}।",
    },
    "as": {
        "work": [
            "আজি কামত পৰিকল্পিত পদক্ষেপ লওক; খৰখেদা এৰাই স্পষ্ট কথা পাতক।",
            "ধৈৰ্যৰে কৰা চেষ্টা ফলপ্ৰসূ হ’ব। সৰু কাম শেষ কৰি ডাঙৰ লক্ষ্যৰ ভেটি মজবুত কৰক।",
            "নতুন প্ৰস্তাৱ দুবাৰ ভাবি সিদ্ধান্ত লওক।",
        ],
        "family": [
            "পৰিয়ালত মিল ৰাখিবলৈ মনযোগেৰে শুনক; সৰু বিবাদ শান্তভাৱে মীমাংসা কৰক।",
            "পৰিয়ালৰ সৈতে সময় কটোৱা মানসিক শান্তি দিয়ে।",
            "ডাঙৰসকলৰ আশীৰ্বাদ লওক। পৰিয়ালৰ সিদ্ধান্তত সকলোৰে মত লওক।",
        ],
        "health": [
            "পানী খোৱা, লঘু ব্যায়াম আৰু পৰ্যাপ্ত জিৰণি স্বাস্থ্যৰ বাবে সহায়ক।",
            "চাপ কমাবলৈ শ্বাস অভ্যাস বা খোজ কঢ়া উপকাৰী।",
            "অতিভোজন আৰু দেৰিকৈ শোৱা এৰক।",
        ],
        "remedy": [
            "ৰাশি স্বামীৰ কৃপাৰ বাবে সাত্ত্বিক আহাৰ আৰু দানৰ সংকল্প ৰাখক।",
            "সূৰ্যোদয়ৰ পাছত অলপ ধ্যান দিনটো স্থিৰ কৰে।",
            "কৃতজ্ঞতাৰে কৰা সৰু পূজা পৰম্পৰাগত শুভ।",
        ],
        "daily": [
            "আজি মন শান্ত ৰাখক; গুৰুত্বপূৰ্ণ কাম আগতে শেষ কৰক। অপ্ৰয়োজনীয় তৰ্ক এৰক।",
            "আজি সহযোগিতা আৰু স্পষ্ট কথা লাভদায়ক। সৰু সাক্ষাৎ শুভ ইংগিত দিব পাৰে।",
            "আজি আত্মসংযম প্ৰয়োজন। খৰচ নিয়ন্ত্ৰণত ৰাখক আৰু স্বাস্থ্যলৈ মন দিয়ক।",
        ],
        "weekly": [
            "এই সপ্তাহত ধৈৰ্য আৰু পৰিকল্পনাৰে অগ্ৰগতি সম্ভৱ। পৰিয়ালৰ সৈতে সময় মানসিক স্থিৰতা দিয়ে।",
            "সপ্তাহত নতুন সুযোগ সাৱধানে চাওক। পুৰণি কাম আগতে শেষ কৰক।",
            "এই সপ্তাহত স্বাস্থ্য আৰু দিনচৰ্যা উন্নতিৰ ভাল সময়। বেছি প্ৰতিশ্ৰুতি এৰক।",
        ],
        "monthly": [
            "এই মাহত দীৰ্ঘম্যাদী লক্ষ্যত মনোযোগ দিয়ক। সঞ্চয় আৰু শিক্ষা ফলপ্ৰসূ।",
            "মাহৰ মাজভাগত সম্পৰ্ক মজবুত হ’ব পাৰে। ঘৰ-পৰিয়ালৰ সিদ্ধান্তত সাৱধান থাকক।",
            "মাহজুৰি কাম, জিৰণি আৰু আধ্যাত্মিক অভ্যাসৰ ভাৰসাম্য শুভ।",
        ],
        "state_note": "এই ৰাজ্যৰ পঞ্জিকা পৰম্পৰা {system} কেলেণ্ডাৰ আৰু {muhurat} মুহূৰ্ত পদ্ধতিৰ ওপৰত আধাৰিত। আজিকৰ নক্ষত্ৰ {nakshatra}, তিথি {tithi}।",
    },
    "en": {
        "work": [
            "Take planned steps at work today; avoid haste and keep communication clear.",
            "Patience at work brings results. Finish small tasks to build toward larger goals.",
            "Weigh new offers carefully before deciding; experienced advice can help.",
        ],
        "family": [
            "Listen carefully at home and settle small disputes calmly.",
            "Time with family brings mental ease; improve a small household routine.",
            "Seek elders' blessings and include everyone in family decisions.",
        ],
        "health": [
            "Hydration, light exercise, and rest support wellbeing today.",
            "Breathing practice or a short walk can ease stress.",
            "Avoid overeating and late nights; notice bodily fatigue.",
        ],
        "remedy": [
            "Keep a simple sattvic diet and a small act of charity for balance.",
            "A few quiet minutes after sunrise can steady the day.",
            "A brief gratitude prayer is traditionally considered auspicious.",
        ],
        "daily": [
            "Stay calm, finish priorities first, and avoid needless arguments today.",
            "Cooperation and clear talk help today; a short visit may bring a good signal.",
            "Practice self-restraint today; watch spending and health.",
        ],
        "weekly": [
            "Patience and planning support progress this week; family time steadies the mind.",
            "Review new chances carefully this week; clear pending work first.",
            "A good week to improve health routines; avoid over-promising.",
        ],
        "monthly": [
            "Focus on long-term goals this month; saving and learning pay off.",
            "Relationships may strengthen mid-month; be careful with home decisions.",
            "Balance work, rest, and quiet practice through the month.",
        ],
        "state_note": "This region's panchang uses the {system} calendar and {muhurat} muhurat system. Today's nakshatra is {nakshatra}, tithi {tithi}.",
    },
}


def _areas_for(lang: str) -> dict:
    """Never mix scripts: prefer exact lang, else English (not Hindi) for other languages."""
    lang = (lang or "en").lower()
    if lang in _DETAIL_AREAS:
        return _DETAIL_AREAS[lang]
    return _DETAIL_AREAS["en"]


def _normalize_lang(language: str) -> str:
    code = (language or "kn").lower()
    if code == "en" or code not in LANGUAGES:
        return "kn"
    return code


def enrich_rows(rows: list, lang: str) -> list:
    native = _TERMS.get("rashi", {}).get(lang) or _TERMS["rashi"]["hi"]
    out = []
    for i, row in enumerate(rows[:12]):
        meta = RASHI_META[i % 12]
        item = dict(row)
        item["index"] = i + 1
        item["sign"] = meta["sign"]
        item["planet"] = meta["planet"]
        item["element"] = meta["element"]
        if not item.get("rashi") and i < len(native):
            item["rashi"] = native[i]
        out.append(item)
    return out


def _script_range(lang: str) -> tuple[int, int] | None:
    ranges = {
        "hi": (0x0900, 0x097F),
        "mr": (0x0900, 0x097F),
        "bn": (0x0980, 0x09FF),
        "as": (0x0980, 0x09FF),
        "pa": (0x0A00, 0x0A7F),
        "gu": (0x0A80, 0x0AFF),
        "or": (0x0B00, 0x0B7F),
        "ta": (0x0B80, 0x0BFF),
        "te": (0x0C00, 0x0C7F),
        "kn": (0x0C80, 0x0CFF),
        "ml": (0x0D00, 0x0D7F),
        "en": (0x0041, 0x007A),
    }
    return ranges.get((lang or "").lower())


def _same_script(text: str, lang: str) -> bool:
    """True if text contains letters from the target language script (blocks Hindi mix-ins)."""
    if not text:
        return False
    rng = _script_range(lang)
    if rng is None:
        return True
    lo, hi = rng
    for ch in text:
        o = ord(ch)
        if lo <= o <= hi:
            return True
        # Latin letters count for English only
        if lang == "en" and (("A" <= ch <= "Z") or ("a" <= ch <= "z")):
            return True
    return False


def expand_row_writeup(row: dict, lang: str, index: int) -> dict:
    """Attach longer multi-section write-up — keep a single language (no Hindi mix-ins)."""
    from .translate import looks_english, translate_to

    areas = _areas_for(lang)
    i = index % 3
    base = (row.get("prediction") or "").strip()
    if base and not _same_script(base, lang):
        base = translate_to(base, lang) if looks_english(base) else ""

    def pick(field: str, template: str) -> str:
        val = (row.get(field) or "").strip()
        if val and _same_script(val, lang):
            return val
        if val and looks_english(val):
            out = translate_to(val, lang)
            if out and _same_script(out, lang):
                return out
        return template

    work = pick("work", areas["work"][i])
    family = pick("family", areas["family"][i])
    health = pick("health", areas["health"][i])
    remedy = pick("remedy", areas["remedy"][i])
    # Overview = prediction only when it matches the UI language script.
    overview = base if (base and _same_script(base, lang)) else work
    item = {k: v for k, v in row.items() if k not in {"overview", "work", "family", "health", "remedy", "prediction_long"}}
    item["overview"] = overview
    item["work"] = work
    item["family"] = family
    item["health"] = health
    item["remedy"] = remedy
    item["prediction_long"] = " ".join(x for x in [overview, work, family, health, remedy] if x)
    return item


def enrich_rows_detailed(rows: list, lang: str) -> list:
    enriched = enrich_rows(rows, lang)
    return [expand_row_writeup(row, lang, i) for i, row in enumerate(enriched)]


def fallback(language: str, target_date):
    lang = _normalize_lang(language)
    colors = _TERMS["colors"][lang]
    preds = _TERMS["predictions"][lang]
    rashis = _TERMS["rashi"][lang]
    rows = []
    for i, name in enumerate(rashis):
        rows.append({
            "rashi": name,
            "prediction": preds[i % len(preds)],
            "lucky_number": str((i + target_date.day) % 9 + 1),
            "lucky_color": colors[i % len(colors)],
        })
    return {
        "date": target_date.isoformat(),
        "language": LANGUAGES[lang],
        "lang": lang,
        "provider": "deterministic-fallback",
        # Store raw predictions only; enrich on every API response so lang fixes apply.
        "rashifal": rows,
    }


def extract_json(text):
    text = text.strip()
    text = re.sub(r"^```(?:json)?", "", text, flags=re.I).strip()
    text = re.sub(r"```$", "", text).strip()
    m = re.search(r"\{.*\}", text, flags=re.S)
    if not m:
        raise ValueError("No JSON found")
    return json.loads(m.group(0))


def generate_rashifal(language, target_date):
    lang = _normalize_lang(language)
    if not settings.gemini_api_key:
        return fallback(lang, target_date)
    try:
        from google import genai
        client = genai.Client(api_key=settings.gemini_api_key)
        lang_name = LANGUAGES[lang]
        prompt = (
            "Generate a culturally respectful daily Vedic astrology-style Rashifal. "
            f"Date: {target_date.isoformat()}. Write entirely in {lang_name} script. "
            "Do not use English words. Generate all 12 Rashis with native names. "
            "For each rashi provide: prediction (2-3 sentences overview), "
            "work (1-2 sentences), family (1-2 sentences), health (1-2 sentences), "
            "remedy (1 short traditional tip). "
            'Return ONLY JSON {"rashifal":[{"rashi":"...","prediction":"...",'
            '"work":"...","family":"...","health":"...","remedy":"...",'
            '"lucky_number":"7","lucky_color":"..."}]}. '
            "lucky_color must also be in the same regional language. "
            "Do not use markdown. Do not make medical, legal, financial, or guaranteed outcome claims."
        )
        response = client.models.generate_content(model=settings.gemini_model, contents=prompt)
        data = extract_json(response.text)
        if not isinstance(data.get("rashifal"), list):
            raise ValueError("Invalid JSON")
        rows = enrich_rows(data["rashifal"], lang)
        # Cache raw+meta only; expand_row_writeup runs on each API response.
        return {
            "date": target_date.isoformat(),
            "language": lang_name,
            "lang": lang,
            "provider": f"gemini:{settings.gemini_model}",
            "rashifal": rows,
        }
    except Exception:
        return fallback(lang, target_date)


def _fetch_horoscope_period(sign: str, period: str) -> dict:
    key = (sign or "aries").strip().lower()
    valid = {m["sign"] for m in RASHI_META}
    if key not in valid:
        key = "aries"
    meta = next(m for m in RASHI_META if m["sign"] == key)
    urls = {
        "daily": HOROSCOPE_URL,
        "weekly": HOROSCOPE_WEEKLY_URL,
        "monthly": HOROSCOPE_MONTHLY_URL,
    }
    url = f"{urls.get(period, HOROSCOPE_URL)}?{urllib.parse.urlencode({'sign': key})}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "panchang-platform/1.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        data = payload.get("data") or {}
        return {
            "sign": key,
            "planet": meta["planet"],
            "element": meta["element"],
            "date": data.get("date"),
            "period": data.get("period") or period,
            "horoscope": data.get("horoscope") or "",
            "provider": "freehoroscopeapi",
        }
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError) as exc:
        return {
            "sign": key,
            "planet": meta["planet"],
            "element": meta["element"],
            "date": None,
            "period": period,
            "horoscope": "",
            "provider": "unavailable",
            "error": str(exc),
        }


def fetch_daily_horoscope(sign: str) -> dict:
    return _fetch_horoscope_period(sign, "daily")


def _term_lang(lang: str) -> str:
    lang = _normalize_lang(lang)
    # Prefer exact lang; fall back to hi for missing buckets
    return lang


def _localize_label(bag: dict | list | None, key, lang: str, fallback: str = "") -> str:
    """Look up localized label from terms.json. Prefer UI lang, then English key, never force Hindi mix-in."""
    L = _term_lang(lang)
    if not isinstance(bag, dict):
        return fallback or (str(key) if key is not None else "")
    src = bag.get(L)
    if src is None and L != "hi":
        # Prefer English bucket if present; otherwise leave English API name — do not inject Hindi.
        src = bag.get("en")
    if src is None and L == "hi":
        src = bag.get("hi")
    if src is None:
        return fallback or (str(key) if key is not None else "")
    if isinstance(src, dict):
        return src.get(key) or src.get(str(key)) or fallback or str(key)
    if isinstance(src, list):
        try:
            # Nakshatra/tithi lists are 0-based; API index is often 1-based.
            raw = int(key)
            candidates = [raw - 1 if raw >= 1 else raw, raw]
            for i in candidates:
                if 0 <= i < len(src):
                    return src[i]
        except (TypeError, ValueError):
            pass
        return fallback or str(key)
    return fallback or str(key)


def _localized_state_context(lang: str, cfg: dict, pan: dict) -> dict:
    from .panchang import NAKSHATRAS, TITHI_NAMES, VAAR
    from .translate import translate_if_english

    systems = _TERMS.get("systems") or {}
    nak_bag = _TERMS.get("nakshatra") or {}
    tithi_bag = _TERMS.get("tithi") or {}
    vaar_bag = _TERMS.get("vaar") or {}

    system_en = cfg.get("system") or "Amanta"
    muhurat_en = cfg.get("muhurat") or "Choghadiya"
    system = _localize_label(systems, system_en, lang, system_en)
    muhurat = _localize_label(systems, muhurat_en, lang, muhurat_en)

    nak_i = (pan.get("nakshatra") or {}).get("index")
    tithi_i = (pan.get("tithi") or {}).get("index")
    vaar_i = (pan.get("vaar") or {}).get("index")
    nak_name = (pan.get("nakshatra") or {}).get("name") or ""
    tithi_name = (pan.get("tithi") or {}).get("name") or ""
    vaar_name = (pan.get("vaar") or {}).get("name") or ""

    # Resolve missing indexes from English engine names (Somavara / Ardra / …).
    if nak_i is None and nak_name:
        try:
            nak_i = NAKSHATRAS.index(nak_name) + 1
        except ValueError:
            pass
    if tithi_i is None and tithi_name:
        try:
            tithi_i = TITHI_NAMES.index(tithi_name) + 1
        except ValueError:
            pass
    if vaar_i is None and vaar_name:
        try:
            vaar_i = VAAR.index(vaar_name)
        except ValueError:
            pass

    nak = _localize_label(nak_bag, nak_i, lang, nak_name or "—")
    tithi = _localize_label(tithi_bag, tithi_i, lang, tithi_name or "—")
    vaar = _localize_label(vaar_bag, vaar_i, lang, vaar_name or "—")
    if isinstance(vaar_bag.get(_term_lang(lang)) or vaar_bag.get("hi"), list) and vaar_i is not None:
        lst = vaar_bag.get(_term_lang(lang)) or vaar_bag.get("hi")
        if 0 <= int(vaar_i) < len(lst):
            vaar = lst[int(vaar_i)]

    # Last resort: translate leftover English labels into the UI language.
    system = translate_if_english(system, lang)
    muhurat = translate_if_english(muhurat, lang)
    nak = translate_if_english(nak, lang)
    tithi = translate_if_english(tithi, lang)
    vaar = translate_if_english(vaar, lang)

    areas = _areas_for(lang)
    note = areas["state_note"].format(
        system=system,
        muhurat=muhurat,
        nakshatra=nak,
        tithi=tithi,
    )
    return {
        "system": system,
        "system_en": system_en,
        "muhurat": muhurat,
        "muhurat_en": muhurat_en,
        "nakshatra": nak,
        "tithi": tithi,
        "vaar": vaar,
        "note": note,
    }


def _period_outlook(sign: str, period: str, lang: str, fallback: str) -> dict:
    """English freehoroscope → Google/MyMemory translation, else regional template."""
    from .translate import looks_english, translate_to

    key = (sign or "aries").strip().lower()
    fetched = _fetch_horoscope_period(key, period)
    eng = (fetched.get("horoscope") or "").strip()
    if eng and looks_english(eng):
        localized = translate_to(eng, lang, source="en")
        if localized and not looks_english(localized):
            return {
                "period": period,
                "horoscope": localized,
                "provider": f"translate:{fetched.get('provider') or 'freehoroscopeapi'}",
                "lang": lang,
                "sign": key,
                "source_lang": "en",
            }
        if localized:
            return {
                "period": period,
                "horoscope": localized,
                "provider": f"translate:{fetched.get('provider') or 'freehoroscopeapi'}",
                "lang": lang,
                "sign": key,
                "source_lang": "en",
            }
    return {
        "period": period,
        "horoscope": fallback,
        "provider": "regional",
        "lang": lang,
        "sign": key,
    }


def build_rashi_detail(
    sign: str,
    lang: str,
    state_code: str,
    target_date,
    row: dict | None = None,
    panchang: dict | None = None,
) -> dict:
    """Full expand payload: regional write-up + state context + daily/weekly/monthly."""
    from .regional_v2 import config

    lang = _normalize_lang(lang)
    key = (sign or "aries").strip().lower()
    idx = next((i for i, m in enumerate(RASHI_META) if m["sign"] == key), 0)
    meta = RASHI_META[idx]
    native = (_TERMS.get("rashi", {}).get(lang) or _TERMS["rashi"]["hi"])[idx]
    base = row or {
        "rashi": native,
        "prediction": (_TERMS["predictions"][lang][idx % len(_TERMS["predictions"][lang])]),
        "lucky_number": str((idx + target_date.day) % 9 + 1),
        "lucky_color": _TERMS["colors"][lang][idx % len(_TERMS["colors"][lang])],
    }
    writeup = expand_row_writeup({**base, **meta, "index": idx + 1, "sign": key, "rashi": base.get("rashi") or native}, lang, idx)

    cfg = config(state_code or "KA")
    pan = (panchang or {}).get("panchang") or {}
    ast = (panchang or {}).get("astronomy") or {}
    moon_i = int(ast.get("moon_rashi_index") or (int(float(ast.get("moon_sidereal_longitude") or 0) // 30) + 1))
    sun_i = int(ast.get("sun_rashi_index") or (int(float(ast.get("sun_sidereal_longitude") or 0) // 30) + 1))
    areas = _areas_for(lang)
    loc = _localized_state_context(lang, cfg, pan)

    daily_fb = (areas.get("daily") or _DETAIL_AREAS["en"]["daily"])[idx % 3]
    weekly_fb = (areas.get("weekly") or _DETAIL_AREAS["en"]["weekly"])[idx % 3]
    monthly_fb = (areas.get("monthly") or _DETAIL_AREAS["en"]["monthly"])[idx % 3]

    daily = _period_outlook(key, "daily", lang, daily_fb)
    weekly = _period_outlook(key, "weekly", lang, weekly_fb)
    monthly = _period_outlook(key, "monthly", lang, monthly_fb)

    return {
        "date": target_date.isoformat(),
        "lang": lang,
        "sign": key,
        "rashi": writeup.get("rashi") or native,
        "planet": meta["planet"],
        "element": meta["element"],
        "lucky_number": writeup.get("lucky_number"),
        "lucky_color": writeup.get("lucky_color"),
        "overview": writeup.get("overview") or writeup.get("prediction"),
        "work": writeup.get("work"),
        "family": writeup.get("family"),
        "health": writeup.get("health"),
        "remedy": writeup.get("remedy"),
        "prediction_long": writeup.get("prediction_long"),
        "is_moon_sign": moon_i == idx + 1,
        "is_sun_sign": sun_i == idx + 1,
        "state": {
            "code": (state_code or "KA").upper(),
            "system": loc["system"],
            "system_en": loc["system_en"],
            "muhurat": loc["muhurat"],
            "muhurat_en": loc["muhurat_en"],
            "style": cfg.get("style"),
            "accent": cfg.get("accent"),
            "note": loc["note"],
            "nakshatra": loc["nakshatra"],
            "tithi": loc["tithi"],
            "vaar": loc["vaar"],
        },
        "daily": daily,
        "weekly": weekly,
        "monthly": monthly,
    }
