import re
import os
import sys
from unicodedata import category
from yelp_uri.encoding import recode_uri
from urllib.request import urlopen
from bs4 import BeautifulSoup

oropuare = "AĀEĒIĪOŌUŪaāeēiīoōuū"
orokati = "HKMNPRTWŊƑhkmnprtwŋƒ"
kūare_tohutō = ''.maketrans({'ā': 'a', 'ē': 'e', 'ī': 'i', 'ō': 'o', 'ū': 'u'})
arapū_pūmatua = 'AĀEĒIĪOŌUŪHKMNPRTWŊƑ'
arapū_pūriki = 'aāeēiīoōuūhkmnprtwŋƒ'
arapū = arapū_pūmatua + arapū_pūriki + "-"

kupu_kino = ['aa', 'aaa', 'ae', 'aero', 'aere', 'aura', 'aurora', 'auto', 'automate', 'amature', 'ami', 'amino', 'anemia', 'anime', 'anita', 'ape', 'api', 'apo', 'area', 'arena', 'aria', 'aroma', 'atari', 'awake', 'aware', 'angie', 'eau', 'ee', 'ei', 'eia', 'eine', 'eo', 'eu', 'eureka', 'euro', 'europa', 'europe', 'emo', 'emu', 'era', 'erie', 'eta', 'engine', 'ie', 'ieee', 'ii', 'iii', 'iowa', 'iu', 'imo', 'initiate', 'ipo', 'ire', 'irene', 'itu', 'oa', 'oahu', 'oe', 'oo', 'ooo', 'ou', 'ohio', 'oki', 'omaha', 'opera', 'operate', 'orange', 'owe', 'u', 'uae', 'uu', 'uma', 'una', 'unaware', 'une', 'uni', 'unite', 'uno', 'urine', 'utopia', 'haiti', 'hanoi', 'hate', 'hawaii', 'hee', 'hehe', 'hero', 'hi', 'hike', 'hipaa', 'hire', 'hinge', 'ho', 'home', 'homo', 'howe', 'hu', 'humane', 'kauai', 'kane', 'karaoke', 'karate', 'kate', 'katie', 'kangaroo', 'ke', 'keno', 'korea', 'ku', 'ma', 'maine', 'maui', 'mauritania', 'manure', 'maria', 'mariana', 'marie', 'mario', 'marina', 'marine', 'maritime', 'mateo', 'mature', 'mango', 'memo', 'menu', 'meta', 'mi', 'mia', 'miami', 'mio', 'mike', 'mime', 'mini', 'miniature', 'minute', 'moo', 'moore', 'mona', 'mono', 'moto', 'mu', 'murakami', 'mute', 'na', 'naomi', 'nauru', 'name', 'nano', 'napa', 'nate', 'nato', 'nature', 'ne', 'neo', 'neu', 'nemo', 'nero', 'ni', 'nie', 'niue', 'nike', 'nina', 'nine', 'nite', 'no', 'noaa', 'nokia', 'nominate', 'nominee', 'nope', 'nora', 'note', 'nowhere', 'nu', 'nuke', 'pa', 'panama', 'panorama', 'patio', 'pe', 'pee', 'peoria', 'pete', 'petite', 'pi', 'piano', 'pie', 'pike', 'pipe', 'pirate', 'po', 'poe', 'pope', 'potato', 'pu', 'puma', 'ra', 'rao', 'ratio', 'range', 're', 'reiki', 'remake', 'remote', 'rename', 'rene', 'renee', 'reno', 'retire', 'ri', 'rio', 'ripe', 'rita', 'ro', 'roanoke', 'roe', 'roi', 'rookie', 'route', 'routine', 'romania', 'rome', 'romeo', 'rope', 'rotate', 'rowe', 'ru', 'rue', 'rupee', 'ta', 'taipei', 'tahoe', 'tape', 'tate', 'tee', 'tenure', 'ti', 'tie', 'time', 'to', 'too', 'tome', 'tone', 'toni', 'topeka', 'torino', 'tongue', 'tu', 'tue', 'tune', 'wa', 'we', 'wee', 'wei', 'were', 'wi', 'wie', 'wine', 'wipe', 'wire', 'wo', 'woo', 'woke', 'wore', 'wu', 'ngo', 'white', 'who', 'whore']

kupu_kino_kūare_tohutō = ['a', 'au', 'auto', 'aka', 'ami', 'amino', 'ana', 'apo', 'are', 'ari', 'aria', 'ate', 'ati', 'awe', 'e', 'eo', 'emi', 'epa', 'era', 'i', 'ia', 'io', 'ipo', 'ira', 'ita', 'o', 'oi', 'ou', 'oki', 'one', 'ora', 'ore', 'oro', 'u', 'ui', 'uma', 'ha', 'hai', 'haute', 'haha', 'hama', 'hare', 'hate', 'hawaii', 'he', 'hee', 'hehe', 'here', 'hi', 'ho', 'hope', 'hu', 'hua', 'ka', 'kai', 'kara', 'ki', 'kia', 'kite', 'ko', 'korea', 'ma', 'mae', 'mao', 'mauritania', 'make', 'mama', 'mania', 'mara', 'mare', 'marie', 'marino', 'mate', 'manga', 'mango', 'me', 'mere', 'mimi', 'mine', 'mira', 'mo', 'moe', 'moi', 'moo', 'moore', 'mona', 'more', 'moto', 'mu', 'na', 'no', 'none', 'nuke', 'pa', 'panama', 'pane', 'papa', 'papua', 'para', 'patio', 'pe', 'pea', 'pee', 'pei', 'peru', 'pi', 'pine', 'puma', 'pure', 'ra', 'rae', 'rai', 'rao', 'rake', 'rama', 'rape', 'rare', 'rate', 're', 'rea', 'rei', 'rene', 'renee', 'ri', 'rita', 'rite', 'ro', 'roi', 'roma', 'romeo', 'rupee', 'ta', 'tai', 'tao', 'tau', 'take', 'tara', 'tata', 'tate', 'tango', 'tea', 'tee', 'tia', 'tina', 'tire', 'to', 'toe', 'too', 'tomato', 'tone', 'tori', 'torino', 'tote', 'tu', 'wake', 'ware', 'we', 'wee', 'wiki', 'wo', 'woo', 'ngo', 'where']

kupu_rangirua = ['a', 'au', 'aka', 'amino', 'ana', 'apo', 'are', 'ari', 'ate', 'ati', 'awe', 'e', 'eo', 'emi', 'epa', 'i', 'ia', 'io', 'ipo', 'ira', 'ita', 'o', 'oi', 'one', 'ora', 'ore', 'oro', 'ui', 'uma', 'ha', 'hai', 'haute', 'haha', 'hama', 'hare', 'hawaii', 'he', 'hee', 'here', 'hope', 'hua', 'ka', 'kai', 'kara', 'ki', 'kia', 'kite', 'ko', 'mae', 'mao', 'make', 'mama', 'mania', 'mara', 'mare', 'marino', 'mate', 'manga', 'me', 'mere', 'mimi', 'mine', 'mira', 'mo', 'moe', 'moi', 'moo', 'moore', 'more', 'moto', 'none', 'nuke', 'panama', 'pane', 'papa', 'papua', 'para', 'pea', 'pei', 'peru', 'pine', 'pure', 'rae', 'rai', 'rake', 'rama', 'rape', 'rare', 'rate', 'rea', 'rei', 'rita', 'rite', 'roi', 'roma', 'rupee', 'tai', 'tao', 'tau', 'take', 'tara', 'tata', 'tango', 'tea', 'tee', 'tia', 'tina', 'tire', 'toe', 'tomato', 'tori', 'tote', 'wake', 'ware', 'wiki', 'where']

kupu_rangirua_kūare_tohutō = ['a', 'au', 'auto', 'aka', 'ami', 'amino', 'ana', 'apo', 'are', 'ari', 'aria', 'ate', 'ati', 'awe', 'e', 'eo', 'emi', 'epa', 'era', 'i', 'ia', 'io', 'ipo', 'ira', 'ita', 'o', 'oi', 'ou', 'oki', 'one', 'ora', 'ore', 'oro', 'u', 'ui', 'uma', 'ha', 'hai', 'haute', 'haha', 'hama', 'hare', 'hate', 'hawaii', 'he', 'hee', 'hehe', 'here', 'hi', 'ho', 'hope', 'hu', 'hua', 'ka', 'kai', 'kara', 'ki', 'kia', 'kite', 'ko', 'korea', 'ma', 'mae', 'mao', 'mauritania', 'make', 'mama', 'mania', 'mara', 'mare', 'marie', 'marino', 'mate', 'manga', 'mango', 'me', 'mere', 'mimi', 'mine', 'mira', 'mo', 'moe', 'moi', 'moo', 'moore', 'mona', 'more', 'moto', 'mu', 'na', 'no', 'none', 'nuke', 'pa', 'panama', 'pane', 'papa', 'papua', 'para', 'patio', 'pe', 'pea', 'pee', 'pei', 'peru', 'pi', 'pine', 'puma', 'pure', 'ra', 'rae', 'rai', 'rao', 'rake', 'rama', 'rape', 'rare', 'rate', 're', 'rea', 'rei', 'rene', 'renee', 'ri', 'rita', 'rite', 'ro', 'roi', 'roma', 'romeo', 'rupee', 'ta', 'tai', 'tao', 'tau', 'take', 'tara', 'tata', 'tate', 'tango', 'tea', 'tee', 'tia', 'tina', 'tire', 'to', 'toe', 'too', 'tomato', 'tone', 'tori', 'torino', 'tote', 'tu', 'wake', 'ware', 'we', 'wee', 'wiki', 'wo', 'woo', 'ngo', 'where']

stop_words = ['te', 'i', 'o', 'ngā', 'ki', 'a', 'ka', 'ko', 'e', 'he', 'me', 'ana', 'ia', 'atu', 'mai', 'mō', 'nō', 'ai', 'hei', 'ā', 'anō', 'nā', 'nei', 'kia', 'kei', 'ake', 'rā', 'wā', 'nui', 'mea', 'kua', 'mā', 'kē', 'ōna', 'noa', 'tae', 'tū', 'arā', 'tā', 'iho', 'mau', 'reo', 'tō', 'rua', 'mua', 'tōna', 'tōna', 'rātou', 'tana',  'tētahi', 'rāua', 'tēnei', 'noho', 'ētahi', 'roto', 'taua',  'rawa', 'runga', 'tērā', 'kāore', 'ēnei', 'rānei', 'tuatahi', 'reira']

def nahanaha(tūtira):
    # Takes a list of strings (e.g. output of kōmiri_kupu) and returns the
    # list in Māori alphabetical order
    return sorted(tūtira, key=lambda kupu: [arapū.index(pūriki) if pūriki in arapū else len(arapū) + 1 for pūriki in
                                            hōputu(kupu)])


def hōputu(kupu, normalize=True):
    # Replaces ng and wh, w', w’ with ŋ and ƒ respectively, since Māori
    # consonants are easier to deal with in unicode format. It may be passed
    # A list, dictionary, or string, and uses if statements to determine how
    # To replace the consonants of the constituent words, and wheter to return
    # A string or a list. The Boolean variable determines whether it's encoding
    # Or decoding (set False if decoding)

    if normalize:
        kupu = ''.join(ch for ch in kupu if category(ch)[0] != 'P')

    return re.sub(r'(w\')|(w’)|(wh)|(ng)|(W\')|(W’)|(Wh)|(Ng)|(WH)|(NG)', whakatakitahi, kupu)


def hōputu_whakahou(kupu, normalize=True):

    if normalize:
        kupu = ''.join(ch for ch in kupu if category(ch)[0] != 'P')

    def whakahou(tauriterite):
        oro = tauriterite.group(0)
        if oro[0] == ("Ŋ"):
            if oro[1] == oro[1].upper():
                return "NG" + oro[1]
            else:
                return "Ng" + oro[1]
        elif oro == "ŋ":
            return "ng"
        elif oro[0] == "Ƒ":
            if oro[1] == oro[1].upper():
                return "WH" + oro[1]
            else:
                return "Wh" + oro[1]
        else:
            return "wh"

    return re.sub(r'(Ŋ[{oropuare}])|(ŋ)|(Ƒ[{oropuare}])|(ƒ)'.format(oropuare=oropuare), whakahou, kupu)


def whakatakitahi(tauriterite):
    # If passed the appropriate letters, return the corresponding symbol
    oro = tauriterite.group(0)
    if oro == 'ng':
        return 'ŋ'
    elif oro == 'w\'' or oro == 'w’' or oro == 'wh':
        return 'ƒ'
    elif oro == 'Ng' or oro == 'NG':
        return 'Ŋ'
    else:
        return 'Ƒ'


# Keys to the kupu_list dictionary:
keys = ['pākehā', 'rangirua', 'pākehā_kūare_tohutō', 'rangirua_kūare_tohutō']
kupu_lists = {}

def kupu_māori(kupu_tōkau, tohutō=True):
    '''
    Returns a set of kupu pākehā found in a given plaintext.

    Set tohutō = True to become sensitive to the presence of macrons when making the match
    '''

    # Splits the raw text along characters that a
    kupu_hou = re.findall('(?!-)(?!{p}*--{p}*)({p}+)(?<!-)'.format(p='[a-zāēīōū\-’\']'), kupu_tōkau,
                          flags=re.IGNORECASE)

    # Gets the preferred word lists from the preloaded files, depending on
    # The Boolean variable, as macronised and demacronised texts have different
    # Stoplists (files that need to be accessed)
    kupu_rangirua = kupu_lists[keys[1]] if tohutō else kupu_lists[keys[3]]
    kupu_pākehā = kupu_lists[keys[0]] if tohutō else kupu_lists[keys[2]]

    # Setting up the dictionaries in which the words in the text will be placed
    huinga_māori = set()

    # Puts each word through tests to determine which word frequency dictionary
    # it should be referred to. Goes to the ambiguous dictionary if it's in the
    # ambiguous list, goes to the Māori dictionary if it doesn't have consecutive
    # consonants, doesn't end in a consnant, doesn't have any english letters
    # and isn't one of the provided stop words. Otherwise it goes to the non-Māori
    # dictionary. If this word hasn't been added to the dictionary, it does so,
    # and adds a count for every time the corresponding word gets passed to the
    # dictionary.

    for kupu in kupu_hou:
        hōputu_kupu = hōputu(kupu)
        if ((kupu.lower() or kupu.lower().translate(kūare_tohutō)) in kupu_rangirua) or len(kupu) == 1:
            continue
        elif not (re.compile("[{o}][{o}]".format(o=orokati)).search(hōputu_kupu.lower()) or (
                hōputu_kupu[-1].lower() in orokati) or any(pūriki not in arapū for pūriki in hōputu_kupu.lower()) or (
                          (kupu.lower() or whakatakitahi_oropuare(kupu)) in kupu_pākehā)):
            if kupu not in huinga_māori:
                huinga_māori.add(kupu)
            continue

    return huinga_māori

def kupu_pākehā(kupu_tōkau, tohutō=True):
    '''
    Returns a set of kupu pākehā found in a given plaintext
    '''

    # Splits the raw text along characters that a
    kupu_hou = re.findall('(?!-)(?!{p}*--{p}*)({p}+)(?<!-)'.format(p='[a-zāēīōū\-’\']'), kupu_tōkau,
                          flags=re.IGNORECASE)

    # Gets the preferred word lists from the preloaded files, depending on
    # The Boolean variable, as macronised and demacronised texts have different
    # Stoplists (files that need to be accessed)
    kupu_rangirua = kupu_lists[keys[1]] if tohutō else kupu_lists[keys[3]]
    kupu_pākehā = kupu_lists[keys[0]] if tohutō else kupu_lists[keys[2]]

    # Puts each word through tests to determine which word frequency dictionary
    # it should be referred to. Goes to the ambiguous dictionary if it's in the
    # ambiguous list, goes to the Māori dictionary if it doesn't have consecutive
    # consonants, doesn't end in a consnant, doesn't have any english letters
    # and isn't one of the provided stop words. Otherwise it goes to the non-Māori
    # dictionary. If this word hasn't been added to the dictionary, it does so,
    # and adds a count for every time the corresponding word gets passed to the
    # dictionary.

    huinga_pākehā = set()
    for kupu in kupu_hou:
        hōputu_kupu = hōputu(kupu)
        if kupu in orokati:
            huinga_pākehā.add(kupu)
        elif ((kupu.lower() or kupu.lower().translate(kūare_tohutō)) in kupu_rangirua) \
            or len(hōputu_kupu) == 0:
            continue
        elif not (re.compile("[{o}][{o}]".format(o=orokati)).search(hōputu_kupu.lower()) \
            or (hōputu_kupu[-1].lower() in orokati)
            or any(pūriki not in arapū for pūriki in hōputu_kupu.lower())
            or ((kupu.lower() or whakatakitahi_oropuare(kupu)) in kupu_pākehā)):
            continue
        else:
            if not kupu in huinga_pākehā:
                huinga_pākehā.add(kupu)
    return huinga_pākehā


def kōmiri_kupu(kupu_tōkau, tohutō=True):
    # Removes words that contain any English characters from the string above,
    # returns dictionaries of word counts for three categories of Māori words:
    # Māori, ambiguous, non-Māori (Pākehā)
    # Set tohutō = True to become sensitive to the presence of macrons when making the match

    # Splits the raw text along characters that a
    kupu_hou = re.findall('(?!-)(?!{p}*--{p}*)({p}+)(?<!-)'.format(p='[a-zāēīōū\-’\']'), kupu_tōkau,
                          flags=re.IGNORECASE)

    # Gets the preferred word lists from the preloaded files, depending on
    # The Boolean variable, as macronised and demacronised texts have different
    # Stoplists (files that need to be accessed)
    kupu_rangirua = kupu_lists[keys[1]] if tohutō else kupu_lists[keys[3]]
    kupu_pākehā = kupu_lists[keys[0]] if tohutō else kupu_lists[keys[2]]

    # Setting up the dictionaries in which the words in the text will be placed
    raupapa_māori, raupapa_rangirua, raupapa_pākehā = {}, {}, {}

    # Puts each word through tests to determine which word frequency dictionary
    # it should be referred to. Goes to the ambiguous dictionary if it's in the
    # ambiguous list, goes to the Māori dictionary if it doesn't have consecutive
    # consonants, doesn't end in a consnant, doesn't have any english letters
    # and isn't one of the provided stop words. Otherwise it goes to the non-Māori
    # dictionary. If this word hasn't been added to the dictionary, it does so,
    # and adds a count for every time the corresponding word gets passed to the
    # dictionary.

    for kupu in kupu_hou:
        hōputu_kupu = hōputu(kupu)
        if ((kupu.lower() or \
            kupu.lower().translate(kūare_tohutō)) in kupu_rangirua) or \
            len(kupu) == 1 or \
            len(hōputu_kupu) == 0:
            if kupu not in raupapa_rangirua:
                raupapa_rangirua[kupu] = 0
            raupapa_rangirua[kupu] += 1
            continue
        elif not (re.compile("[{o}][{o}]".format(o=orokati)).search(hōputu_kupu.lower()) or (
                hōputu_kupu[-1].lower() in orokati) or any(pūriki not in arapū for pūriki in hōputu_kupu.lower()) or (
                          (kupu.lower() or whakatakitahi_oropuare(kupu)) in kupu_pākehā)):
            if kupu not in raupapa_māori:
                raupapa_māori[kupu] = 0
            raupapa_māori[kupu] += 1
            continue
        else:
            if kupu not in raupapa_pākehā:
                raupapa_pākehā[kupu] = 0
            raupapa_pākehā[kupu] += 1

    return raupapa_māori, raupapa_rangirua, raupapa_pākehā


def whakatakitahi_oropuare(kupu):
    # Replaces doubled vowels with a single vowel. It is passed a string, and returns a string.
    return re.sub(r'uu', 'u', re.sub(r'oo', 'o', re.sub(r'ii', 'i', re.sub(r'ee', 'e', re.sub(r'aa', 'a', kupu)))))


def hihira_raupapa_kupu(kupu_hou, tohutō):
    # Looks up a single word to see if it is defined in maoridictionary.co.nz
    # Set tohutō = False to not ignore macrons when making the match
    # Returns True or False

    kupu_huarua = kupu_hou.lower()
    # If the macrons are not strict, they are removed for the best possibility of finding a match
    if tohutō:
        kupu_huarua = kupu_huarua.translate(kūare_tohutō)
    # Sets up an iterable of the word, and the word without double vowels to be searched.
    # This is because some texts use double vowels instead of macrons, and they return different search results.
    taurua = [kupu_huarua, whakatakitahi_oropuare(kupu_huarua)]
    # Sets up the variable to be returned, it is changed if a result is found
    wāriutanga = False

    for kupu in taurua:
        taukaea = recode_uri(
            'http://maoridictionary.co.nz/search?idiom=&phrase=&proverb=&loan=&histLoanWords=&keywords=' + kupu)
        hupa = BeautifulSoup(urlopen(taukaea), 'html.parser', from_encoding='utf8')

        tohu = hupa.find_all('h2')

        # The last two entries are not search results, due to the format of the website.
        for taitara in tohu[:-2]:
            taitara = taitara.text.lower()
            # Removes capitals and macrons for the best chance of making a match
            if kupu in (taitara.translate(kūare_tohutō).split() if tohutō else taitara.split()):
                wāriutanga = True
                break
            else:
                pass

    print("Found " + kupu + ": " + str(wāriutanga))
    return wāriutanga


def hihira_raupapa(kupu_hou, tohutō=False):
    # Looks up a list of words to see if they are defined in maoridictionary.co.nz
    # Set tohutō = False to become sensitive to the presence of macrons when making the match
    # Returns a list of words that are defined, and a list of words that are not defined from the input list.

    # Associates each word with a dictionary check result
    hihira = [hihira_raupapa_kupu(kupu, tohutō) for kupu in kupu_hou]

    # Adds it to the good word list if it passed the check
    kupu_pai = [tokorua[1] for tokorua in zip(hihira, kupu_hou) if tokorua[0]]
    # Adds it to the bad word list if it failed the check
    kupu_kino = [tokorua[1] for tokorua in zip(hihira, kupu_hou) if not tokorua[0]]
    return kupu_pai, kupu_kino


def kupu_ratios(text, tohutō=True):
    map_Māori, map_ambiguous, map_other = kōmiri_kupu(text, tohutō)

    nums = {'reo': sum(map_Māori.values()),
            'ambiguous': sum(map_ambiguous.values()),
            'other': sum(map_other.values()) + len(re.findall('[\d]+([,.][\d]+)*', text))}

    nums['percent'] = get_percentage(**nums)
    save_corpus = nums['percent'] >= 50

    return save_corpus, nums


def get_percentage(reo, ambiguous, other):
    if reo:
        return round(100 * reo / (reo + other), 2)
    elif other:
        return 0
    elif ambiguous:
        return 51
    else:
        return 0


def auaha_raupapa_tū(kupu_tōkau, tohutō=True):
    # This function is used for making stoplists as it does not depend on any stoplists.
    # It finds all words in a string, and adds them to a dictionary depending on
    # Whether they look like Māori words or not, and counts their frequency.
    # Set tohutō = True to become sensitive to the presence of macrons when making the match

    # Splits the raw text along characters that a
    kupu_hou = re.findall('(?!-)(?!{p}*--{p}*)({p}+)(?<!-)'.format(p='[a-zāēīōū\-’\']'), kupu_tōkau,
                          flags=re.IGNORECASE)

    # Setting up the dictionaries in which the words in the text will be placed
    raupapa_māori, raupapa_pākehā = {}, {}

    # Puts each word through tests to determine which word frequency dictionary
    # it should be referred to. Goes to the Māori dictionary if it doesn't have
    # consecutive consonants, doesn't end in a consnant, or doesn't have any
    # English letters. Otherwise it goes to the non-Māori dictionary. If this
    # word hasn't been added to the dictionary, it does so, and adds a count for
    # every time the corresponding word gets passed to the dictionary.

    for kupu in kupu_hou:
        hōputu_kupu = hōputu(kupu)
        if not (re.compile("[{o}][{o}]".format(o=orokati)).search(hōputu_kupu.lower()) or (
                hōputu_kupu[-1].lower() in orokati) or any(pūriki not in arapū for pūriki in hōputu_kupu.lower())):
            if kupu not in raupapa_māori:
                raupapa_māori[kupu] = 0
            raupapa_māori[kupu] += 1
            continue
        else:
            if kupu not in raupapa_pākehā:
                raupapa_pākehā[kupu] = 0
            raupapa_pākehā[kupu] += 1

    return raupapa_māori, raupapa_pākehā


def tiki_ōrau(kōwae):
    # Uses the kōmiri_kupu function from the taumahi module to estimate how
    # Much of the text is Māori. Input is a string of text, output is a percentage string

    # Gets the word frequency dictionaries for the input text
    raupapa_māori, raupapa_rangirua, raupapa_pākehā = kōmiri_kupu(kōwae, False)

    # Calculates how many words of the Māori and English dictionary there are
    tatau_māori = sum(raupapa_māori.values())
    tatau_rangirua = sum(raupapa_rangirua.values())
    tatau_pākehā = sum(raupapa_pākehā.values())
    tatau_kapa = tatau_māori + tatau_pākehā
    tatau_tapeke = tatau_kapa + tatau_rangirua

    # Provided there are some words that are categorised as Māori or English,
    # It calculates how many Māori words there are compared to the sum, and
    # Returns the percentage as a string
    ōrau = 0.00 if (not tatau_kapa != 0) else round((tatau_māori / tatau_kapa) * 100, 2)

    return tatau_māori, tatau_rangirua, tatau_pākehā, tatau_tapeke, ōrau


tūtira_kupu = [kupu_kino, kupu_rangirua, kupu_kino_kūare_tohutō, 
               kupu_rangirua_kūare_tohutō]
for key, tūtira in zip(keys, tūtira_kupu):
    kupu_lists[key] = tūtira

# All following script is for cleaning raw text strings:

apostrophes = '‘’\'"“”\s'
sentence_end = ['([.!?:—"“]+[\)\]]*|,\s*[\'"“”])', '[{}]+'.format(apostrophes)]

# Regex for splitting paragraphs, detecting a p end and beginning of another
new_paragraph = re.compile('({}+|-+){}\n'.format(sentence_end[0], sentence_end[1]))
# Version 2:
paragraph_pattern = re.compile('(?<=([.!?]|[\-—:]))[\-—.!? ‘’\'"•]*\n["\']*(?=[A-Z])')

# Regex to detect the end of a sentence
new_sentence = re.compile('{}{}|["“”]—?'.format(sentence_end[0], sentence_end[1]))


def get_paragraph(txt):
    paragraph_end = paragraph_pattern.search(txt)
    if paragraph_end:
        return txt[:paragraph_end.start()], txt[paragraph_end.end():]
    return txt, ''


def clean_whitespace(paragraph):
    return re.sub(r'\s+', ' ', paragraph).strip()


# Regex to replace all ~|[A macron] vowels with macron vowels
vowels = re.compile(r'(A?~|\[A macron\])([aeiouAEIOU])')
vowel_map = {'a': 'ā', 'e': 'ē', 'i': 'ī', 'o': 'ō', 'u': 'ū'}


def sub_vowels(txt):
    return vowels.sub(lambda x: vowel_map[x.group(2).lower()], txt)