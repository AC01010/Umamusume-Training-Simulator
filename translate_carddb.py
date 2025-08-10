import json

# Translation dictionary for Chinese to English
TRANSLATIONS = {
    # Character names
    "特别周": "Special Week",
    "无声铃鹿": "Silence Suzuka", 
    "东海帝王": "Tokai Teio",
    "丸善斯基": "Maruzensky",
    "富士奇迹": "Fuji Kiseki",
    "小栗帽": "Oguri Cap",
    "黄金船": "Gold Ship",
    "伏特加": "Vodka",
    "大和赤骥": "Daiwa Scarlet",
    "大树快车": "Taiki Shuttle",
    "草上飞": "Grass Wonder",
    "菱亚马逊": "Hishi Amazon",
    "目白麦昆": "Mejiro McQueen",
    "神鹰": "El Condor Pasa",
    "好歌剧": "Opera O",
    "成田白仁": "Narita Brian",
    "鲁道夫象征": "Symboli Rudolf",
    "气槽": "Air Groove",
    "爱丽数码": "Agnes Digital",
    "青云天空": "Seiun Sky",
    "玉藻十字": "Tamamo Cross",
    "美妙姿势": "Fine Motion",
    "琵琶晨光": "Biwa Hayahide",
    "重炮": "Heavy Tank",
    "醒目飞鹰": "Admire Vega",
    "荣进闪耀": "Eishin Flash",
    "真机伶": "Machikazen",
    "河童川": "Kawakami Princess",
    "黄金城": "Gold City",
    "樱花进王": "Sakura Bakushin O",
    "采珠": "Seeking the Pearl",
    "新光风": "Shinko Windy",
    "东商变革": "Sweep Tosho",
    "超级小海湾": "Super Creek",
    "智能飞鹰": "Smart Falcon",
    "星云天空": "Nebula Sky",
    "待兼福来": "Matikanefukukitaru",
    "米浴": "Rice Shower",
    "艾尼斯风神": "Agnes Tachyon",
    "爱慕织姬": "Admire Vega",
    "目白善信": "Mejiro Palmer",
    "京都大道": "Kyoto Daisho",
    "目白阿露丝": "Mejiro Ardan",
    "中山庆典": "Narita Top Road",
    "成田路": "Narita Top Road",
    "吉兆": "Kitasan Black",
    "大进军": "Satono Diamond",
    "胜利奖券": "Winning Ticket",
    "青竹回忆": "Take Chikarato",
    "东瀛佐敦": "Tokai Teio",
    "荒漠英雄": "Desert Hero",
    "雪中送炭": "Yukino Bijin",
    "丸文莫斯科": "Marvelous Sunday",
    "代大战车": "Daitaku Helios",
    "大拓太阳神": "Daitaku Helios",
    "美浦波旁": "Miho no Bourbon",
    "名门淑女": "Nice Nature",
    "春乌拉拉": "Haru Urara",
    "鸣钟": "Narita Taishin",
    "星座": "Constellation",
    "久立前": "Kuriko May",
    "中津樱": "Naritsu Sakura",
    "双重闪电": "Twin Turbo",
    "成田大新": "Narita Taishin",
    "菱曙": "Hishi Akebono",
    "雄鹰": "Yaeno Muteki",
    "美丽周日": "Marvelous Sunday",
    "樱花王": "Sakura Bakushin O",
    "目白善跃": "Mejiro Dober",
    "春城": "Haru Urara",
    "小小战车": "Taiki Shuttle",
    "竹竹泽": "Takechiyu",
    "白鹿直行": "Biwa Hayahide",
    "多拉戈": "Dragon Force",
    "多拉兹": "Dragon",
    "目白义武": "Mejiro Ramonu",
    "中山青": "Narita Brian",
    "青云之志": "Seiun Sky",
    "樱花特使": "Sakura Bakushin O",
    "菱梦": "Hishi Miracle",
    "夏暴风雨": "Summer Tempest",
    "贵妇人": "Winning Ticket",
    "菱空": "Hishi Akebono",
    "春神": "Divine Spirit",
    "田野竹": "Takechiyu",
    "优秀魅力": "Fine Motion",
    "拓荒女神": "Frontier Goddess",
    "战争装甲": "War Emblem",
    "凯撒风暴": "Caesar's Storm",
    "闪电红": "Lightning Red",
    "晓神": "Akatsuki Deity",
    "武尊": "Warrior Emperor",
    "新竹": "New Bamboo",
    "优秀风尚": "Fine Motion",
    "优秀举止": "Fine Motion",
    "龙王": "Dragon King",
    "未来的光": "Future Light",
    "胜利信仰": "Victory Faith",
    "胜利希望": "Victory Hope",
    "不可思议": "Wonderful",
    "凤凰神": "Phoenix God",
    "神话": "Mythology",
    "灵魂": "Soul",
    "天使": "Angel",
    "恶魔": "Demon",
    "幻想": "Fantasy",
    "现实": "Reality",
    "梦幻": "Dream",
    "真实": "Truth",
    
    # Prefixes/Titles
    "[根]": "[Root]",
    "[夏]": "[Summer]",
    "[新年]": "[New Year]",
    "[情人节]": "[Valentine]",
    "[万圣节]": "[Halloween]",
    "[圣诞节]": "[Christmas]",
    "[泳装]": "[Swimsuit]",
    "[制服]": "[Uniform]",
    "[和服]": "[Kimono]",
    "[特雷森学园]": "[Tracen Academy]",
    "[URA优胜]": "[URA Winner]",
    "[天皇赏·春]": "[Tenno Sho Spring]",
    "[日本杯]": "[Japan Cup]",
    "[有马纪念]": "[Arima Kinen]",
    "[宝冢纪念]": "[Takarazuka Kinen]",
    "[菊花赏]": "[Kikuka Sho]",
    "[皋月赏]": "[Satsuki Sho]",
    "[日本德比]": "[Tokyo Yushun]",
    "[桜花赏]": "[Oka Sho]",
    "[优骏牝马]": "[Yushun Himba]",
    "[秋华赏]": "[Shuka Sho]",
    "[マイルCS]": "[Mile Championship]",
    "[スプリンターズS]": "[Sprinters Stakes]",
    "[安田記念]": "[Yasuda Kinen]",
    "[高松宮記念]": "[Takamatsunomiya Kinen]",
    "[フェブラリーS]": "[February Stakes]",
    "[チャンピオンズC]": "[Champions Cup]",
    "[ジャパンC]": "[Japan Cup]",
    "[エリザベス女王杯]": "[Queen Elizabeth II Cup]",
    "[天皇賞・秋]": "[Tenno Sho Autumn]",
    
    # Common phrases
    "崭新的自我": "A New Me",
    "准时遵守": "Punctual Observance",
    "燃烧!!": "Burning!!",
    "爆炸起飞!": "Blast Off!",
    "你快乐吗?": "Are you merry?",
    "让我们跳舞吧?": "Balliamo?",
    "黎明时我将获胜!": "All'alba vincerò!",
    "预示胜利": "A Win Foreshadowed",
    "警告大门": "///WARNING GATE///",
    "燃烧": "Burning",
    "闪耀": "Shining",
    "胜利": "Victory",
    "奇迹": "Miracle",
    "传说": "Legend",
    "英雄": "Hero",
    "女王": "Queen",
    "公主": "Princess",
    "皇帝": "Emperor",
    "国王": "King",
    "骑士": "Knight",
    "战士": "Warrior",
    "冠军": "Champion",
    "大师": "Master",
    "专家": "Expert",
    "天才": "Genius",
    "精英": "Elite",
    "超级": "Super",
    "终极": "Ultimate",
    "完美": "Perfect",
    "无敌": "Invincible"
}

def translate_text(text):
    """Translate Chinese text to English using the translation dictionary"""
    # Try exact match first
    if text in TRANSLATIONS:
        return TRANSLATIONS[text]
    
    # Try to translate parts of the text
    translated = text
    for chinese, english in TRANSLATIONS.items():
        translated = translated.replace(chinese, english)
    
    return translated

def translate_carddb():
    """Create English version of cardDB.json"""
    try:
        # Read the original JSON file
        with open('cardDB.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Create translated version
        translated_data = {}
        
        for card_id, card_data in data.items():
            if isinstance(card_data, dict):
                translated_card = card_data.copy()
                
                # Translate cardName
                if 'cardName' in card_data:
                    translated_card['cardName'] = translate_text(card_data['cardName'])
                
                # Translate fullName  
                if 'fullName' in card_data:
                    translated_card['fullName'] = translate_text(card_data['fullName'])
                
                translated_data[card_id] = translated_card
            else:
                translated_data[card_id] = card_data
        
        # Save translated version
        with open('cardDB_EN.json', 'w', encoding='utf-8') as f:
            json.dump(translated_data, f, ensure_ascii=False, indent=2)
        
        print("Created cardDB_EN.json with English translations")
        
        # Show some examples
        print("\nTranslation examples:")
        count = 0
        for card_id, card_data in translated_data.items():
            if isinstance(card_data, dict) and 'cardName' in card_data:
                original_card = data[card_id]
                if 'cardName' in original_card:
                    print(f"Original: {original_card['cardName']}")
                    print(f"English:  {card_data['cardName']}")
                    print()
                    count += 1
                    if count >= 5:
                        break
        
    except FileNotFoundError:
        print("Error: cardDB.json not found")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in cardDB.json")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    translate_carddb()