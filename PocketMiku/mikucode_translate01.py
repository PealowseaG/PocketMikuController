# python3
# mikucode_translate: Trnaslate japanese text file to voice code list for PocketMiku
# for mikucode_translate
# Constant Value
SINGLE_CHAR = 0
DOUBLE_CHAR = 1
NMJNNG_CHAR = 2
# Dictionary
char_to_mikucode = {'あ':0, 'い':1, 'う':2, 'え':3, 'お':4,
'か':5, 'き':6, 'く':7, 'け':8, 'こ':9,
'が':10, 'ぎ':11, 'ぐ':12, 'げ':13, 'ご':14,
'きゃ':15, 'きゅ':16, 'きょ':17, 'ぎゃ':18, 'ぎゅ':19, 'ぎょ':20,
'さ':21, 'すぃ':22, 'す':23, 'せ':24, 'そ':25,
'ざ':26, 'ずぃ':27, 'ず':28, 'ぜ':29, 'ぞ':30,
'づぁ':26, 'づぃ':27, 'づ':28, 'づぇ':29, 'づぉ':30,
'しゃ':31, 'し':32, 'しゅ':33, 'しぇ':34, 'しょ':35,
'じゃ':36, 'じ':37, 'じゅ':38, 'じぇ':39, 'じょ':40,
'た':41, 'てぃ':42, 'とぅ':43, 'て':44, 'と':45,
'だ':46, 'でぃ':47, 'どぅ':48, 'で':49, 'ど':50, 'てゅ':51, 'でゅ':52,
'ちゃ':53, 'ち':54, 'ちゅ':55, 'ちぇ':56, 'ちょ':57,
'つぁ':58, 'つぃ':59, 'つ':60, 'つぇ':61, 'つぉ':62,
'な':63, 'に':64, 'ぬ':65, 'ね':66, 'の':67,
'にゃ':68, 'にゅ':69, 'にょ':70,
'は':71, 'ひ':72, 'ふ':73, 'へ':74, 'ほ':75,
'ば':76, 'び':77, 'ぶ':78, 'べ':79, 'ぼ':80,
'ぱ':81, 'ぴ':82, 'ぷ':83, 'ぺ':84, 'ぽ':85,
'ひゃ':86, 'ひゅ':87, 'ひょ':88,
'びゃ':89, 'びゅ':90, 'びょ':91,
'ぴゃ':92, 'ぴゅ':93, 'ぴょ':94,
'ふぁ':95, 'ふぃ':96, 'ふゅ':97, 'ふぇ':98, 'ふぉ':99,
'ま':100, 'み':101, 'む':102, 'め':103, 'も':104,
'みゃ':105, 'みゅ':106, 'みょ':107,
'や':108, 'ゆ':109, 'よ':110,
'ら':111, 'り':112, 'る':113, 'れ':114, 'ろ':115,
'りゃ':116, 'りゅ':117, 'りょ':118,
'わ':119, 'うぃ':120, 'うぇ':121, 'うぉ':122, 'ゐ':120, 'ゑ':121, 'を':122, 'ん':127,
'ん(N\)':123, 'ん(m)':124, 'ん(N)':125, 'ん(J)':126, 'ん(n)':127}
# Taple / Lists
code_double = ('き', 'ぎ', 'す', 'ず', 'づ', 'し', 'じ', 'て', 'と', 'で', 'ど', 'ち', 'つ', 'に', 'ひ', 'び', 'ぴ', 'ふ', 'み', 'り', 'う') # 
jn_follow = ('に')   # 'ん(J)':126, ん + に,にゃ,にゅ,にょ, (ち,じ)
nm_follow = ('ふ', 'ま', 'み', 'む', 'め', 'も', 'ば', 'び', 'ぶ', 'べ', 'ぼ', 'ぱ', 'ぴ', 'ぷ', 'ぺ', 'ぽ')   # 'ん(m)':124, ん + ば,ま,ぱ行
nb_follow = ('あ', 'い', 'う', 'え', 'お', 'さ', 'し', 'す', 'せ', 'そ', 'は', 'ひ', '(ふ)', 'へ', 'ほ', 
'ざ', 'じ', 'ず', 'ぜ', 'ぞ', 'や', 'ゆ', 'よ', 'わ', 'ゐ', 'ゑ', 'を', 'ん', 'ぢ', 'づ',' ', '　') # 'ん(N\)':123, あ, や, わ, さ, は, ざ行 & 語末(スペース)
ng_follow = ('か', 'き', 'く', 'け', 'こ', 'が', 'ぎ', 'ぐ', 'げ', 'ご')   # 'ん(N)':125, ん + か,が行
nn_follow = ('た', 'ち', 'つ', 'て', 'と', 'だ', '(ぢ)', '(づ)', 'で', 'ど',
'な', '(に)', 'ぬ', 'ね', 'の', 'ら', 'り', 'る', 'れ', 'ろ' )   # 'ん(n)':127, ん + た,だ,な(に以外),ら行など 

# Trnaslate japanese text file to voice code list for PocketMiku
def mikucode_translate(lyrictxt):
    lyric_code = []
    f = open(lyrictxt)
    for strline in f:
        line_code = []
        passed_code = SINGLE_CHAR    # pass_code 0:single char, 1:double char, 2:N/n/jn/ng char
        for char in strline:
            if passed_code == NMJNNG_CHAR:    # 'ん' treatment
                if char in jn_follow:
                    voice_code = 126    # 'ん(J)':126
                elif char in nm_follow:
                    voice_code = 124    # 'ん(m)':124
                elif char in nb_follow:
                    voice_code = 123    # 'ん(N\)':123
                elif char in ng_follow:
                    voice_code = 125    # 'ん(N)':125
                else:
                    voice_code = char_to_mikucode[last_char]    # 'ん(n)':127
                #print(last_char,':',voice_code)    # for debug
                line_code.append(voice_code)
            elif passed_code == DOUBLE_CHAR:  # doble char treatment
                comp_double = last_char + char
                if comp_double in char_to_mikucode:
                    voice_code = char_to_mikucode[comp_double]
                    #print(comp_double,':',voice_code)  # for debug
                    line_code.append(voice_code)
                else:
                    voice_code = char_to_mikucode[last_char]
                    #print(last_char,':',voice_code)    # for debug
                    line_code.append(voice_code)
            if char in char_to_mikucode:    # check each char & single char translate 
                if char in code_double:
                    last_char = char
                    passed_code = DOUBLE_CHAR
                elif char == 'ん':
                    last_char = char
                    passed_code = NMJNNG_CHAR
                else:
                    voice_code = char_to_mikucode[char]
                    passed_code = SINGLE_CHAR
                    #print(char,':',voice_code) # for debug
                    line_code.append(voice_code)
            else:
                passed_code = SINGLE_CHAR
        lyric_code.append(line_code)
    f.close()
    return lyric_code
# main for check
#lyrictxt = 'aiueo_wawon.txt'
#lyric_code = mikucode_translate(lyrictxt)
#print(lyric_code)
