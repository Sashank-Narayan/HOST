# -*- coding: utf-8 -*-
"""gnews-Copy.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/13o-QHhdlZuj_JRboVCfQsmGIO51t-vay
"""

# !pip install GoogleNews
# !pip install client
# !pip install rake_nltk
# !pip install GoogleNews

import pandas as pd
# from newsapi import NewsApiClient
import requests
from GoogleNews import GoogleNews
from datetime import datetime, date
import json
import numpy as np
import pandas as pd
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from string import punctuation
import re
import numpy as np
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA

start_date = []
end_date = []

sources = ["bbc-news", "the-telegraph", "the-guardian-uk", "cnn", "abc-news-au",
           "dailymail.co.uk", "metro.co.uk", "mirror.co.uk", "news.google.com"]

all_keywords = ['strike', 'holiday', 'lockdown',
            'inflation', 'grocery sales', 'carnival', 'festival', 'party', 'Walmart', "Tesco", "Sainsbury's", "supply chain", "flood", "wendys", "lidl", "homebase"]

# all_keywords = ['tesco', 'holiday']

# all_keywords = ['autumn', 'bank']

keywords = []

events = ['autumn bank holiday']

all_events = ['autumn bank holiday']

final_prod_events = pd.DataFrame()

counter = 6000

gnews_client_topics = ['Top Stories',
                       'World',
                       'Nation',
                       'Business',
                       'Technology',
                       'Entertainment',
                       'Sports',
                       'Science',
                       'Health']

# branch_keyword_bu_num = {'Esher' : 1, 'Dorchester' : 2}
branch_keyword_bu_num = {
'Peterborough': 103,
'Gillingham': 105,
'Dorking': 107,
'St Ives': 108,
'Brighton': 114,
'Brent Cross': 119,
'Dorchester': 120,
'Esher': 121,
'Hall Green': 122,
'Whetstone': 124,
'Coulsdon': 129,
'New Malden': 131,
'Allington Park': 137,
'Bury St Edmunds': 140,
'Blaby': 141,
'Marlow': 146,
'Kingsthorpe': 148,
'East Sheen': 149,
'Four Oaks': 150,
'Westbury Park': 151,
'Leighton Buzzard': 154,
'Stourbridge': 155,
'Bromley': 158,
'Birch Hill': 159,
'Ramsgate': 160,
'Huntingdon': 163,
'Marlborough': 164,
'Green Street Green': 165,
'St Albans': 166,
'Stevenage': 167,
'Havant': 171,
'John Barnes': 174,
'Hertford': 175,
'Beaconsfield': 177,
'Enfield': 179,
'Goldsworth Park': 181,
'Sevenoaks': 182,
'St Neots': 185,
'Ruislip': 197,
'Banstead': 202,
'Ringwood': 203,
'Welwyn Garden City': 204,
'Ely': 205,
'Thame': 206,
'Chichester': 208,
'Southend': 213,
'Henley': 214,
'Finchley': 215,
'Godalming': 216,
'Monmouth': 217,
'Reading': 218,
'Cirencester': 220,
'Berkhamsted': 223,
'Putney': 225,
'Salisbury': 226,
'Billericay': 229,
'Horley': 233,
'Okehampton': 234,
'Waterlooville': 239,
'Biggin Hill': 240,
'Banstead': 324,
'Horsham New': 580,
'Heathfield': 595,
'Cambridge': 651,
'Hailsham': 653,
'Hythe': 654,
'Paddock Wood': 655,
'Saltash': 656,
'Sidmouth': 657,
'Sudbury': 658,
'Thatcham': 659,
'Worcester Park': 661,
'Wymondham': 662,
'Cheltenham': 663,
'Belgravia': 665,
'Tonbridge': 667,
'Chandlers Ford': 668,
'Portishead': 669,
'Romsey': 671,
'Wandsworth': 673,
'Newmarket': 674,
'Sandbach': 680,
'Fulham': 681,
'Towcester': 682,
'Abergavenny': 683,
'Hitchin': 685,
'Swaffham': 686,
'Newport': 687,
'Barry': 688,
'Worthing': 689,
'Otley': 691,
'Farnham': 692,
'Dartford': 693,
'Sheffield': 695,
'Wolverhampton': 696,
'Willerby': 697,
'Lichfield': 699,
'Wilmslow': 711,
'Lewes': 727,
'East Grinstead': 741,
'Buxton': 748,
'St Katharine Docks': 753,
'West Ealing': 764,
'Hersham': 765,
'Bishop s Stortford': 101,
'Buckhurst Hill': 102,
'Epsom': 104,
'Longfield': 109,
'Crowborough': 110,
'Holloway Road': 112,
'Milton Keynes': 115,
'Dibden': 118,
'Burgess Hill': 123,
'Temple Fortune': 125,
'Saffron Walden': 135,
'Evington': 136,
'Witney': 142,
'Harrow Weald': 143,
'Gosport': 152,
'Wantage': 153,
'Daventry': 156,
'Weybridge': 157,
'Winton': 161,
'Andover': 168,
'Southsea': 170,
'Kings Road': 173,
'Cobham': 176,
'Caterham': 178,
'Woodley': 180,
'Harpenden': 183,
'Caversham': 184,
'Northwood': 186,
'Richmond': 188,
'West Byfleet': 189,
'Sunningdale': 190,
'Barnet': 191,
'Chesham': 192,
'Bath': 193,
'Maidenhead': 194,
'Kingston': 195,
'Fleet': 196,
'Yateley': 198,
'Horsham': 200,
'Tenterden': 201,
'Bloomsbury': 207,
'Petersfield': 209,
'Stroud': 210,
'Abingdon': 211,
'Beckenham': 212,
'South Harrow': 219,
'Wokingham': 221,
'Norwich': 222,
'Bromley South': 224,
'Newark': 227,
'Gloucester Road': 230,
'South Woodford': 231,
'Surbiton': 232,
'Staines': 235,
'Marylebone': 236,
'Great Malvern': 237,
'Twyford': 238,
'Byres Road': 308,
'Weston Super Mare': 309,
'Wellington': 315,
'Ashbourne': 316,
'Storrington': 317,
'Menai Bridge': 318,
'Melksham': 319,
'Colchester': 455,
'JL Foodhall Oxford Street': 456,
'Pontprennau': 457,
'Crewkerne': 458,
'Kenilworth': 460,
'Eldon Square': 461,
'Westfield London': 462,
'Winchester': 463,
'Alcester': 474,
'Bridport': 475,
'Caldicot': 476,
'Croydon': 477,
'Haslemere': 478,
'Headington': 479,
'Holsworthy': 480,
'Leigh On Sea': 481,
'Ponteland': 482,
'Saxmundham': 483,
'Stamford': 484,
'Torquay': 485,
'Upminster': 486,
'Lutterworth': 487,
'Clerkenwell': 492,
'JL Foodhall Bluewater': 493,
'Altrincham': 494,
'Frimley': 652,
'Twickenham': 660,
'Canary Wharf': 664,
'Mill Hill': 670,
'Droitwich': 672,
'Wallingford': 675,
'Newbury': 676,
'Sanderstead': 677,
'Kensington': 678,
'Harrogate': 684,
'Rushden': 690,
'Lincoln': 694,
'Rickmansworth': 698,
'Ashford': 705,
'Cheadle Hulme': 710,
'Balham': 719,
'Southampton New': 720,
'Ampthill': 722,
'Durham': 730,
'Barbican': 732,
'Formby': 749,
'Comely Bank': 750,
'Christchurch': 754,
'Bayswater': 756,
'Eastbourne': 757,
'Chiswick': 760,
'Morningside': 761,
'Parkstone': 766,
'Clapham Junction': 767,
'Edgware Road': 768,
'Buckingham': 769,
'Windsor New': 772,
'Islington': 780,
'Hexham': 782,
'Harborne': 796,
'Brackley': 797,
'Lymington New': 798,
'Sandhurst': 799,
'Trinity Square': 833,
'Clifton': 834,
'Crouch End': 835,
'Oxted': 838,
'Enfield CFC': 199,
'Greenford CFC': 259,
'Evesham': 303,
'York': 311,
'Poynton': 312,
'East Cowes': 313,
'Wimbledon': 314,
'Knutsford': 326,
'Newton Mearns': 327,
'Stratford City': 328,
'Alton': 329,
'St Saviour (Jersey)': 332,
'Rohais (Guernsey)': 333,
'St Helier (Jersey)': 334,
'Admiral Park (Guernsey)': 335,
'Red Houses (Jersey)': 336,
'MOUNTSORREL': 403,
'Gerrards Cross': 459,
'Sevenoaks': 464,
'Marlow': 465,
'Cardiff Queen Street': 501,
'Acton': 502,
'Swindon': 504,
'Littlehampton': 505,
'Uckfield': 506,
'Hereford': 507,
'Malmesbury': 511,
'Coulsdon DFC': 513,
'Bagshot': 514,
'Nailsea': 515,
'Parsons Green': 516,
'Egham': 519,
'Jesmond': 520,
'Enfield Chase': 521,
'Sutton Coldfield': 522,
'Chippenham': 523,
'West Hampstead': 524,
'Shrewsbury': 525,
'Tottenham Court Road': 526,
'Dorking': 527,
'Wimbledon Hill': 528,
'Hawkhurst': 529,
'Fulham Palace Road': 530,
'Peterborough': 531,
'Canterbury': 533,
'Sceptre (Watford)': 534,
'Kensington Gardens': 535,
'Camden': 536,
'Addlestone': 542,
'Fitzroy Street': 552,
'Teignmouth': 554,
'Hornchurch': 555,
'Edenbridge': 556,
'Keynsham': 557,
'Spinningfields': 558,
'Cheam': 559,
'Alderley Edge': 560,
'Walton-on-Thames': 562,
'Locks Heath': 563,
'Burgh Heath': 567,
'Petts Wood': 568,
'Portman Square': 569,
'Burnt Common': 571,
'Walbrook': 573,
'Leeds': 574,
'Broxbourne': 575,
'Amersham': 578,
'Bayswater Temp': 579,
'Oxford Botley Road': 581,
'BASINGSTOKE': 582,
'Old Brompton Road': 583,
'Hazlemere': 584,
'Ealing': 586,
'West Kensington': 587,
'Palmers Green': 588,
'Guildford': 589,
'Kings Cross': 590,
'Wollaton': 591,
'Rustington': 596,
'BATTERSEA NINE ELMS': 598,
'UTTOXETER': 599,
'High Holborn': 601,
'Alderley Old': 602,
'Sherborne': 604,
'Hove': 605,
'Leek': 606,
'High Wycombe': 607,
'Hampton': 612,
'Pimlico': 614,
'Foregate Street': 615,
'Clapham Common': 616,
'Kings Cross Station': 619,
'Stirling': 620,
'North Walsham': 622,
'Aylesbury': 625,
'Milngavie': 630,
'Ipswich': 632,
'Manchester Piccadilly': 636,
'Highbury Corner': 637,
'Muswell Hill': 639,
'Knightsbridge': 641,
'Solihull': 642,
'Sidcup': 643,
'Notting Hill Gate': 644,
'Truro': 648,
'Worcester': 700,
'Warminster': 701,
'Exeter': 702,
'South Bank Tower': 703,
'Bracknell': 706,
'Stratford Upon Avon': 708,
'Walton-le-Dale': 721,
'Bedford': 725,
'Wootton': 726,
'Market Harborough': 728,
'Wells': 729,
'Poundbury': 733,
'Cowbridge': 735,
'ROEHAMPTON': 736,
'Battersea': 737,
'Bagshot Road': 738,
'Tubs Hill': 739,
'Greenwich': 740,
'Colmore Row (Birmingham)': 742,
'Ipswich (Corn Exchange)': 743,
'Kings Hill': 744,
'Chipping Sodbury': 751,
'Oakgrove': 752,
'Dorking': 755,
'Oundle': 758,
'Northwich': 759,
'Helensburgh': 771,
'Monument': 773,
'Little Waitrose at John Lewis Watford': 781,
'Victoria Street': 783,
'Vauxhall': 789,
'Horley - Brighton Road': 802,
'Wimborne': 805,
'Headington - London Road': 806,
'Guildford Worplesdon Road': 808,
'Little Waitrose John Lewis Southampton': 815,
'East Putney': 820,
'Meanwood': 828,
'Chester': 842,
'Raynes Park': 846,
'Oadby': 847,
'Leatherhead': 859,
'Victoria Bressenden Place': 860,
'SKY (OSTERLEY)': 865,
'Faringdon': 871,
'Haywards Heath': 873,
'Banbury': 874,
'Finchley Central': 876,
'Bromsgrove': 877,
'Winchmore Hill': 878,
}

# England = ['Avon', 'Bedfordshire', 'Berkshire', 'Buckinghamshire', 'Cambridgeshire', 'Cheshire', 'Cleveland',
#            'Cornwall', 'Cumbria', 'Derbyshire', 'Devon', 'Dorset', 'Durham', 'East-Sussex', 'Essex', 'Gloucestershire',
#            'Hampshire', 'Herefordshire', 'Hertfordshire', 'Isle-of-Wight', 'Kent', 'Lancashire', 'Leice stershire',
#            'Lincolnshire', 'London', 'Merseyside',
#            'Middlesex', 'Norfolk', 'Northamptonshire', 'Northumberland', 'North-Humberside', 'North-Yorkshire',
#            'Nottinghamshire', 'Oxfordshire', 'Rutland', 'Shropshire', 'Somerset', 'South-Humberside', 'South-Yorkshire',
#            'Staffordshire', 'Suffolk', 'Surrey', 'Tyne-and-Wear', 'Warwickshire', 'West-Midlands', 'West-Sussex',
#            'West-Yorkshire', 'Wiltshire', 'Worcestershire']
England = ['London']
Wales = ['Clwyd', 'Dyfed', 'Gwent', 'Gwynedd', 'Mid-Glamorgan',
         'Powys', 'South-Glamorgan', 'West-Glamorgan']
# Wales = ['South-Glamorgan']
Scotland = ['Aberdeenshire', 'Angus', 'Argyll', 'Ayrshire', 'Banffshire', 'Berwickshire', 'Bute', 'Caithness',
            'Clackmannanshire', 'Dumfriesshire', 'Dunbartonshire', 'East-Lothian', 'Fife', 'Inverness-shire',
            'Kincardineshire', 'Kinross-shire',
            'Kirkcudbrightshire', 'Lanarkshire', 'Midlothian', 'Moray', 'Nairnshire', 'Orkney', 'Peeblesshire',
            'Perthshire', 'Renfrewshire', 'Ross-shire', 'Roxburghshire', 'Selkirkshire', 'Shetland', 'Stirlingshire',
            'Sutherland', 'West Lothian', 'Wigtownshire']
NorthernIreland = ['Antrim', 'Armagh', 'Down',
                   'Fermanagh', 'Londonderry', 'Tyrone']

# branch_keyword = ['Abergavenny', 'Alderley Edge', "Eastbourne", "Edenbridge", "Pontprennau"]
# branch_keyword = ['Abingdon', 'Canary Wharf']
# all_branch_keyword = ['Yateley', 'Canary Wharf', 'Workingham', 'Firmley']
all_branch_keyword = list(branch_keyword_bu_num.keys())

branch_keyword = []

# countries = [England, Wales, Scotland, NorthernIreland]
countries = [England]

final = []

# final_prod = pd.DataFrame()
status_val = []

def googleNews():
    d1 = datetime.strptime(start_date[0], "%Y-%m-%d").strftime("%m/%d/%Y")
    d2 = datetime.strptime(end_date[0], "%Y-%m-%d").strftime("%m/%d/%Y")
    # dif = d2 - d1
    data = pd.DataFrame()
    for keyword in keywords:
            news = GoogleNews(start=d1,end=d2)
            news.search(keyword)
            results = news.result()
            df = pd.DataFrame.from_dict(results)
            df['keyword'] = keyword
            df['city'] = ""
            df['branch'] = ""
            print(df)
            print(df.columns)
            print(df["link"])

    # print the dataframe
    if len(data.columns) > 4:
      data = data.drop(columns=["img", "site"])
      data.head(15)
      final.append(data)

def googleNewsByCity():
    d1 = datetime.strptime(start_date[0], "%Y-%m-%d")
    d2 = datetime.strptime(end_date[0], "%Y-%m-%d")
    dif = d2 - d1
    print(d1,d2)
    data = pd.DataFrame()
    for country in countries:
        for city in country:
            for keyword in keywords:
                news = GoogleNews()
                # news.search(city + ' ' + keyword)
                news.set_period(str(dif.days) + 'd')
                news.get_news(city + ' ' + keyword)
                results = news.result()
                df = pd.DataFrame.from_dict(results)
                df['keyword'] = keyword
                df['city'] = city
                print(df)
                # df['branch'] = ','.join(branch_keyword[city])
                df.head(5)
                data = data.append(df, ignore_index=True)

    # print the dataframe
    if len(data.columns) > 4:
      data = data.drop(columns=["img", "site"])
      final.append(data)

def googleNewsByStreet():
    d1 = datetime.strptime(start_date[0], "%Y-%m-%d")
    d2 = datetime.strptime(end_date[0], "%Y-%m-%d")
    print(d1,d2)
    dif = d2 - d1
    # print(str(dif.days),dif.days)
    data = pd.DataFrame()
    for branch in branch_keyword:
        for keyword in keywords:
            news = GoogleNews()
            # news.search(branch + ' ' + keyword)
            news.set_period(str(dif.days) + 'd')
            news.get_news(branch + ' ' + keyword)
            results = news.result()
            df = pd.DataFrame.from_dict(results)
            df['keyword'] = keyword
            df['branch'] = branch
            df['bu_num'] = branch_keyword_bu_num[branch]
            print(df)
            df.head(5)
            data = data.append(df, ignore_index=True)

    # print the dataframe
    if len(data.columns) > 4:
      data = data.drop(columns=["img", "site"])
      final.append(data)

# googleNewsByStreet()

def newAPI():
    api_key = '6b850797f0564befbca89e3595013e6c'
    results = []
    print(start_date, end_date)
    for source in sources:
        query_params = {
            "source": source,
            "sortBy": "top",
            "apiKey": api_key,
            "from": start_date[0],
            "to": end_date[0],
            "language": "en",
            "country": "gb"
        }
        main_url = "https://newsapi.org/v1/articles"
        res = requests.get(main_url, params=query_params)
        open_news_page = res.json()
        if "articles" in open_news_page:
            article = open_news_page["articles"]
            # data = pd.DataFrame.from_dict(article)
            for ar in article:
                # results.append((source, ar["title"], ar["datetime"]))
                results.append({
                    "title": ar['title'],
                    "desc": ar['description'],
                    "link": ar['url']
                })
    pf = pd.DataFrame(results)
    pf['city'] = 'All'
    pf['branch'] = 'All'
    final.append(pf)
    print(pf)

# newAPI()

def _removeNonAscii(s):
    return "".join(i for i in s if ord(i) < 128)

"""function to remove the punctuations, apostrophe, special characters using regular expressions"""

def clean_text(text):
    text = text.lower()
    text = re.sub(r"what's", "what is ", text)
    text = text.replace('(ap)', '')
    text = re.sub(r"\'s", " is ", text)
    text = re.sub(r"\'ve", " have ", text)
    text = re.sub(r"can't", "cannot ", text)
    text = re.sub(r"n't", " not ", text)
    text = re.sub(r"i'm", "i am ", text)
    text = re.sub(r"\'re", " are ", text)
    text = re.sub(r"\'d", " would ", text)
    text = re.sub(r"\'ll", " will ", text)
    text = re.sub(r'\W+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r"\\", "", text)
    text = re.sub(r"\'", "", text)
    text = re.sub(r"\"", "", text)
    text = re.sub('[^a-zA-Z ?!]+', '', text)
    text = _removeNonAscii(text)
    text = text.strip()
    return text

"""stop words are the words that convery little to no information about the actual content like the words:the, of, for etc"""

def remove_stopwords(word_tokens):
    filtered_sentence = []
    stop_words = stopwords.words('english')
    specific_words_list = ['char', 'u', 'hindustan', 'doj', 'washington']
    stop_words.extend(specific_words_list)
    for w in word_tokens:
        if w not in stop_words:
            filtered_sentence.append(w)
    return filtered_sentence

"""function for lemmatization"""

def lemmatize(x):
    lemmatizer = WordNetLemmatizer()
    return ' '.join([lemmatizer.lemmatize(word) for word in x])

"""splitting a string, text into a list of tokens"""

tokenizer = RegexpTokenizer(r'\w+')

def tokenize(x):
    return tokenizer.tokenize(x)

nltk.download('all')

def sentiment_analysis(prod):
    prod['combined_text'] = prod['title'].map(str)

    # applying all of these functions to the our dataframe
    prod['combined_text'] = prod['combined_text'].map(clean_text)
    prod['tokens'] = prod['combined_text'].map(tokenize)
    prod['tokens'] = prod['tokens'].map(remove_stopwords)
    prod['lems'] = prod['tokens'].map(lemmatize)
    sia = SIA()
    results = []
    for line in prod['lems']:
        pol_score = sia.polarity_scores(line)
        pol_score['lems'] = line
        results.append(pol_score)
    headlines_polarity = pd.DataFrame.from_records(results)
    temp = []
    # for line in prod['branch']:
        # temp.append(line)
    # headlines_polarity['branch'] = temp
    headlines_polarity['label'] = 0
    headlines_polarity.loc[headlines_polarity['compound'] > 0.2, 'label'] = 1
    headlines_polarity.loc[headlines_polarity['compound'] < -0.2, 'label'] = -1
    headlines_polarity['word_count'] = headlines_polarity['lems'].apply(lambda x: len(str(x).split()))
    headlines_polarity.head()
    # gk = headlines_polarity.groupby(['branch', 'label'])
    # fk = headlines_polarity.groupby('branch')['compound'].mean()
    # fk = fk.to_frame()
    result = [prod, headlines_polarity]
    headlines_polarity = headlines_polarity.rename_axis(index=None)
    return pd.merge(prod, headlines_polarity, on=["lems"], how="left")

from datetime import date

def outsource_news():
    googleNewsByCity()
    googleNewsByStreet()
    googleNews()
    # newAPI()
    # GoogleNewsClient()
    # twitterTrends()
    # twitterTrendsByStreet()
    prod = pd.concat(final)
    prod = prod.drop_duplicates('title', keep='first')
    print(prod)
    status_val.append(30)

    final_prod = sentiment_analysis(prod)

    final_prod = final_prod.replace(np.nan,'',regex=True)

    # forecast_keywords = ['sale', 'sport', 'beverage', 'retail', 'vendor', 'market', 'morrisons', 'tesco', 'coles', 'business', 'shopping', 'weather',
    #                      'parties', 'events', 'walmart']

    second_keywords = ['bank holiday', 'heatwave', 'inflation', 'street party', 'rainfall', 'snow', 'retail', 'beverage', 'tesco', 'walmart', 'morrisons', 'weather',
                       'brc', 'mothers day', 'new store launch', 'lidl', 'homebase', 'walmart', 'new tesco store', 'coles', 'supermarket', 'shoppers', 'store', 'grocery', 'strike', 'holiday'
                       'shops', 'markets','holiday', 'lockdown','grocery sales', 'carnival', 'festival', 'party', "sainsbury", "supply chain", "flood", "wendys"]

    remove_keywords = ['accident', 'incident', 'injury', 'political', 'police', 'death', 'traffic', 'lord', 'war', 'actor', 'movie', 'star', 'lord', 'sex', 'gay',
                       'fight', 'crash', 'life', 'weapons', 'dating', 'radio', 'tv', 'guinness', 'husband']

    store_keywords = ['opens', 'closes', 'closed', 'opened', 'open', 'close',
                      'finis', 'shut', 'confining', 'unopen', 'opening'
                      'close down', 'closing', 'shut down', 'conclude', 'ending', 'shutdown', 'closedown', 'warehouse'
                      'closing', 'closure', 'temporary', 'extended']

    competitor_keywords = ['tesco', 'wendys', 'lidl', 'homebase', 'sainburys', 'aldi', 'morrisons', 'marks & spencer', 'asda', 'wendys', 'supermarket', 'store'
                            'shop']

    print(final_prod)
    for index, row in final_prod.iterrows():
        if (len(np.intersect1d(row['tokens'], store_keywords)) == 0):
          # if(len(np.intersect1d(row['tokens'], competitor_keywords)) == 0):
          final_prod.drop(index=index, axis=0, inplace=True)
        else:
          if(len(np.intersect1d(row['tokens'], competitor_keywords)) == 0):
            final_prod.drop(index=index, axis=0, inplace=True)

    # for index, row in final_prod.iterrows():
    #     if (row['city']):
    #         if (len(np.intersect1d(row['tokens'], remove_keywords)) >= 1):
    #             final_prod.drop(index=index, axis=0, inplace=True)
    # for index, row in final_prod.iterrows():
        # if (row['city'] or row['branch_x']):
            # if (len(np.intersect1d(row['tokens'], second_keywords)) == 0):
                # final_prod.drop(index=index, axis=0, inplace=True)
    final_prod = final_prod.drop_duplicates('title', keep='first')
    final_prod = final_prod.drop_duplicates('lems', keep='first')
    final_prod = final_prod.drop_duplicates('tokens', keep='first')

    final_prod['title'] = final_prod['title'].astype(str)

    # for index, row in final_prod.iterrows():
    #   if (row['city']):
    #       if (len(np.intersect1d(row['tokens'], forecast_keywords)) < 1):
    #           final_prod.drop(index=index, axis=0, inplace=True)
    # final_prod = final_prod.drop_duplicates('title', keep='first')

    final_prod['competitor_evt_indchar'] = ['Yes' if(len(np.intersect1d(x,competitor_keywords)) > 0) else 'No' for x in final_prod['tokens']]

    counter_guid = int(date.today().strftime("%Y%m%d"))
    final_prod['efsevt_guid'] = [(counter_guid*1000)+i for i in range(len(final_prod))]

    print(final_prod.dtypes)
    print(final_prod_events.dtypes)

    foriegn_key = []

    for index, row in final_prod.iterrows():
      flag = False
      for index_event, row_event in final_prod_events.iterrows():
        if(row['keyword'] != '' ):
          if(row['keyword'] in row_event['NAME']):
            print(row['keyword'],row_event['NAME'])
            foriegn_key.append(row_event['GUID'])
            flag = True
      if(flag == False):
        foriegn_key.append(0)

    print(foriegn_key)
    final_prod['guid'] = [(counter_guid*2000)+i for i in range(len(final_prod))]
    final_prod['fixed_annual_ind'] = 'n'
    final_prod['perm_env_ind'] = 'n'
    final_prod['cancelled_ind'] = 'n'
    final_prod['create_user'] = ''
    final_prod['update_user'] = ''
    final_prod['perm_env_ind'] = 'n'
    final_prod['crt_timestamp'] = date.today()
    final_prod['upd_timestamp'] = date.today()

    final_prod.rename(columns = {'link':'source_of_event'}, inplace = True)

    final_prod[["datetime"]] = final_prod[["datetime"]].astype(str)
    final_prod.columns = final_prod.columns.str.upper()
    # print(final_prod)
    return final_prod

import pandas as pd
from gspread_dataframe import set_with_dataframe
import gspread

def upload_data(final_prod):
  final_prod = outsource_news()
  final_prod = final_prod.drop_duplicates('LEMS', keep='first')

  credentials = {
    "installed":{"client_id":"431703076976-vah4cpp44uu47l75vunkslfn1f0tjos3.apps.googleusercontent.com","project_id":"cogent-node-241403","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_secret":"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","redirect_uris":["http://localhost:5000"]}  }
  gc, authorized_user = gspread.oauth_from_dict(credentials)
  print("Entered")
  status_val.append(50)
  final_prod = final_prod.append([], ignore_index=True)
  sh = gc.create(date.today().strftime("%d/%m/%Y"))
  worksheet = gc.open(date.today().strftime("%d/%m/%Y")).sheet1
  set_with_dataframe(worksheet, final_prod)

  gc3, authorized_user = gspread.oauth_from_dict(credentials)
  sh = gc3.create(date.today().strftime("%d/%m/%Y") + '_event_occurence')
  worksheet3 = gc3.open(date.today().strftime("%d/%m/%Y") + '_event_occurence').sheet1
  final_prod_occurence = pd.DataFrame()
  final_prod_occurence['GUID'] = final_prod['GUID']
  final_prod_occurence['SDATE'] = final_prod['DATETIME']
  final_prod_occurence['EDATE'] = final_prod['DATETIME']
  final_prod_occurence['FIXED_ANNUAL_IND'] = final_prod['FIXED_ANNUAL_IND']
  final_prod_occurence['PERM_ENV_IND'] = final_prod['PERM_ENV_IND']
  final_prod_occurence['CANCELLED_IND'] = final_prod['CANCELLED_IND']
  final_prod_occurence['CREATE_USER'] = final_prod['CREATE_USER']
  final_prod_occurence['UPDATE_USER'] = final_prod['UPDATE_USER']
  final_prod_occurence['CRT_TIMESTAMP'] = final_prod['CRT_TIMESTAMP']
  final_prod_occurence['UPD_TIMESTAMP'] = final_prod['UPD_TIMESTAMP']
  final_prod_occurence['EFSEVT_GUID'] = final_prod['EFSEVT_GUID']
  final_prod_occurence['SOURCE_OF_EVENT'] = final_prod['SOURCE_OF_EVENT']
  final_prod_occurence['COMMENTS'] = " "
  set_with_dataframe(worksheet3, final_prod_occurence)


  gc1, authorized_user = gspread.oauth_from_dict(credentials)
  sh1 = gc1.create(date.today().strftime("%d/%m/%Y") + '_event_type')
  worksheet1 = gc1.open(date.today().strftime("%d/%m/%Y") + '_event_type').sheet1
  final_prod_events['GUID'] = final_prod['EFSEVT_GUID']
  final_prod_events['NAME'] = final_prod['TITLE']
  final_prod_events['CREATE_USER'] = ' '
  final_prod_events['UPDATE_USER'] = ' '
  final_prod_events['INCLUDED_IND'] = 'y'
  final_prod_events['COMPETITOR_EVT_INDCHAR'] = final_prod['COMPETITOR_EVT_INDCHAR']
  # final_prod_events['NAME_TOKENS'] = events.map(remove_stopwords)
  # print(final_prod_events['NAME_TOKENS'])
  final_prod_events['OSO_NAME'] = final_prod['TITLE']
  final_prod_events['CRT_TIMESTAMP'] = '26-01-2023'
  final_prod_events['UPD_TIMESTAMP'] = '26-01-2023'
  set_with_dataframe(worksheet1, final_prod_events)

  gc2, authorized_user = gspread.oauth_from_dict(credentials)
  sh2 = gc2.create(date.today().strftime("%d/%m/%Y") + '_E2B')
  worksheet2 = gc2.open(date.today().strftime("%d/%m/%Y") + '_E2B').sheet1
  e2b_dataframe = final_prod[['EFSEVT_GUID', 'BU_NUM']].copy()
  e2b_dataframe.dropna()
  set_with_dataframe(worksheet2, e2b_dataframe)

  return final_prod


def keyword_addition(sent):
  new_keywords = sent.split(' ')
  # gc = gspread.authorize(creds)
  # worksheet = gc.open(date.today().strftime("%d/%m/%Y") + '_event_type').sheet1
  print(new_keywords)
  events.append(sent)
  # final_prod_events['GUID'] = [i for i in range(len(events))]
  # final_prod_events['NAME'] = events
  # final_prod_events['CREATE_USER'] = ' '
  # final_prod_events['UPDATE_USER'] = ' '
  # final_prod_events['INCLUDED_IND'] = 'y'
  # final_prod_events['CRT_TIMESTAMP'] = '26-01-2023'
  # final_prod_events['UPD_TIMESTAMP'] = '26-01-2023'
  new_event_addition = []
  new_event_addition.append({
      'GUID': len(events),
      'NAME': events[len(events)-1],
      'CREATE_USER': ' ',
      'UPDATE_USER': ' ',
      'INCLUDED_IND': 'y',
      'CRT_TIMESTAMP': '26-01-2023',
      'UPD_TIMESTAMP': '26-01-2023'
  })
  final_prod_events.append(new_event_addition)
  for word in new_keywords:
    keywords.append(word)
    keywords = list(set(keywords))
  print(keywords)
  final_keyword = keywords
  # set_with_dataframe(worksheet, final_prod_events)
  return "Event Type Added"

from datetime import datetime, timedelta, date

def daterange():
    for n in range(10):
        yield date.today() - timedelta(n)

# !pip install flask
# !pip install flask-ngrok

from flask import Flask, jsonify, Response, request
# from flask_ngrok import run_with_ngrok
from json import loads
from gspread.exceptions import SpreadsheetNotFound

app = Flask(__name__)
# run_with_ngrok(app)

view_events = pd.DataFrame()
final_fetch_response = pd.DataFrame()

time_range = ["18:15", "17:58", "01:20", "05:15", "21:00", "17:10", "12:58", "08:34", "19:22", ""]

@app.route('/gsheetlinks', methods = ['GET'])
def gsheet_links():
  credentials = {
    "installed":{"client_id":"431703076976-vah4cpp44uu47l75vunkslfn1f0tjos3.apps.googleusercontent.com","project_id":"cogent-node-241403","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_secret":"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","redirect_uris":["http://localhost:5000"]}  }
  gc, authorized_user = gspread.oauth_from_dict(credentials)

  sheet_links = []
  date_range = []
  count = 0
  for date in daterange():
    print(date)
    try:
      spreadsheet = gc.open(date.strftime("%d/%m/%Y"))
      print(spreadsheet)
      spreadsheet_url = "https://docs.google.com/spreadsheets/d/%s" % spreadsheet.id
      sheet_links.append(spreadsheet_url)
      date_range.append(date.strftime("%d %b %Y"))
      print(spreadsheet_url)
      count += 1
    except SpreadsheetNotFound:
      print("Spreadsheet doesn't exist")
  history_df = pd.DataFrame()
  history_df["DATE"] = date_range
  history_df["SPREADSHEET_URL"]= sheet_links
  history_df["TIME"] = time_range[:count]
  history_df[["DATE"]] = history_df[["DATE"]].astype(str)
  print(sheet_links)
  print(history_df)
  return Response(history_df.to_json(orient="index"), mimetype='application/json')

@app.route('/events')
def main_call():
  # try:
  print('Enter')
  final_prod = outsource_news()
  final_fetch_response.append(final_prod)
  view_events_2 = pd.DataFrame()
  if(final_prod.empty):
    return jsonify({'error': 'Admin access is required'}), 401
  global view_events
  view_events = pd.DataFrame()
  view_events = final_prod.copy()
  print("######### Finish #########")
  # except:
  #   keywords.clear()
  #   branch_keyword.clear()
  #   start_date.clear()
  #   end_date.clear()
  #   print("failed")
  #   return jsonify({'error': 'Admin access is required'}), 401
  keywords.clear()
  branch_keyword.clear()
  start_date.clear()
  end_date.clear()
  global final
  final.clear()
  return Response(final_prod.to_json(orient="index"), mimetype='application/json')

@app.route('/fetchevents')
def main_fetch_call():
  global view_events
  if(view_events.empty):
    view_events = pd.DataFrame()
    return jsonify({'error': 'Admin access is required'}), 401
  print(view_events)
  print("######### Fetch Finish #########")
  return Response(view_events.to_json(orient="index"), mimetype='application/json')

@app.route('/postevents', methods = ['POST'])
def post_main_call():
  # language = request.args.get('data')
  language = request.get_json()
  print(language)
  print(language['data'])
  res = language['data']
  upload_events_df = pd.DataFrame(res)
  print(upload_events_df)
  upload_data(upload_events_df)

@app.route('/postkeywords', methods = ['POST'])
def post_main_keywords_call():
  # language = request.args.get('data')
  language = request.get_json()
  print(language)
  print(language['data'])
  print(language['data'][0]['label'])
  for word in language['data']:
    keywords.append(word['label'])
  res = language['data']
  print(keywords)

@app.route('/postbranches', methods = ['POST'])
def post_main_branches_call():
  # language = request.args.get('data')
  language = request.get_json()
  print(language)
  print(language['data'])
  print(language['data'][0]['label'])
  for word in language['data']:
    branch_keyword.append(word['label'])
  res = language['data']
  print(branch_keyword)
  res = language['data']

@app.route('/postadddates', methods = ['POST'])
def post_main_new_date():
  language = request.get_json()
  print(language)
  new_date = language['data']
  start_date.append(new_date[0])
  end_date.append(new_date[1])
  print(start_date,end_date)
  print(new_date)
  return "Success", 200

@app.route('/finishevents', methods = ['POST'])
def clear_keyword_branches():
  keywords.clear()
  branch_keyword.clear()
  start_date.clear()
  end_date.clear()
    
@app.route('/')
# ‘/’ URL is bound with hello_world() function.
def hello_world():
    return 'Hello World

if __name__ == '__main__':
  app.run()

