# coding = UTF-8

'''
새로운 국가는 country_dic와 해당 대륙 dic에 딕셔너리(key: value) 형태로 추가
'''

# 국가명 딕셔너리
country_dic = {'Afghanistan': '아프가니스탄', 'Albania': '알바니아', 'Algeria': '알제리', 'Andorra': '안도라', 'Angola': '앙골라',
               'Argentina': '아르헨티나', 'Armenia': '아르메니아', 'Australia': '호주', 'Austria': '오스트리아', 'Azerbaijan': '아제르바이잔',
               'Bahamas': '바하마', 'Bahrain': '바레인', 'Bangladesh': '방글라데시', 'Barbados': '바베이도스', 'Belarus': '벨라루스',
               'Belgium': '벨기에', 'Belize': '벨리즈', 'Benin': '베냉', 'Bhutan': '부탄', 'Bolivia': '볼리비아',
               'Bosnia and Herzegovina': '보스니아헤르체고비나', 'Botswana': '보츠와나', 'Brazil': '브라질', 'Brunei': '브루나이',
               'Bulgaria': '불가리아', 'Burkina Faso': '부르키나파소', 'Burundi': '브룬디', 'Cabo Verde': '카보베르데',
               'Cambodia': '캄보디아', 'Cameroon': '카메룬', 'Canada': '캐나다', 'Central African (Rep.)': '중앙아프리카공화국',
               'Ceuta': '세우타', 'Chad': '차드', 'Chile': '칠레', "China (People's Rep. of)": '중국', 'Colombia': '콜롬비아',
               'Commonwealth of Dominica': '도미니카연방', 'Comoros': '코모로', 'Congo (Dem. Rep. of the)': '콩고민주공화국',
               'Congo (Rep. of the)': '콩고', 'Costa Rica': '코스타리카',
               "Cote D'Ivoire": '코트디부아르', 'Croatia': '크로아티아', 'Cuba': '쿠바', 'Curacao': '퀴라소', 'Cyprus': '키프로스',
               'Czech Republic': '체코', 'Denmark': '덴마크', 'Djibouti': '지부티', 'Dominican (Rep.)': '도미니카공화국',
               'Dominican Republic': '도미니카공화국', 'Ecuador': '에콰도르', 'Egypt': '이집트', 'El Salvador': '엘살바도르',
               'Equatorial Guinea': '적도기니', 'Eritrea': '에리트레아', 'Estonia': '에스토니아', 'Eswatini': '에스와티니',
               'Ethiopia': '에티오피아', 'Fiji': '피지', 'Finland': '핀란드', 'Former Yug. Rep. of Macedonia': '북마케도니아',
               'France': '프랑스', 'Gabon': '가봉', 'Gambia': '감비아', 'Georgia': '조지아', 'Germany': '독일', 'Ghana': '가나',
               'Greece': '그리스',
               'Guatemala': '과테말라', 'Guinea': '기니', 'Guinea-Bissau': '기니비사우', 'Guyana': '가이아나', 'Haiti': '아이티',
               'Honduras': '온두라스', 'Hong Kong (SAR - PRC)': '홍콩', 'Hungary': '헝가리', 'Iceland': '아이슬란드', 'India': '인도',
               'Indonesia': '인도네시아', 'Iran': '이란', 'Iraq': '이라크', 'Ireland': '아일랜드', 'Israel': '이스라엘', 'Italy': '이탈리아',
               'Jamaica': '자메이카', 'Japan': '일본', 'Jordan': '요르단', 'Kazakhstan': '카자흐스탄', 'Kenya': '케냐',
               "Korea (Dem. People's Rep.)": '북한', 'Korea (Rep. of)': '대한민국', 'Kuwait': '쿠웨이트', 'Kyrgyzstan': '키르기스스탄',
               'Laos': '라오스', 'Latvia': '라트비아', 'Lebanon': '레바논', 'Lesotho': '레소토', 'Liberia': '라이베리아', 'Libya': '리비아',
               'Liechtenstein': '리히텐슈타인', 'Lithuania': '리투아니아', 'Luxembourg': '룩셈부르크', 'Madagascar': '마다가스카르',
               'Malawi': '말라위', 'Malaysia': '말레이시아', 'Maldives': '몰디브', 'Mali': '말리', 'Malta': '몰타',
               'Mauritania': '모리타니',
               'Mauritius': '모리셔스', 'Melilla': '멜리야', 'Mexico': '멕시코', 'Micronesia (Federated States of)': '미크로네시아 연방',
               'Moldova': '몰도바', 'Mongolia': '몽골', 'Montenegro': '몬테네그로', 'Morocco': '모로코', 'Mozambique': '모잠비크',
               'Myanmar': '미얀마', 'Namibia': '나미비아', 'Nepal': '네팔', 'Netherlands (The)': '네덜란드',
               'New Caledonia': '누벨칼레도니',
               'New Zealand': '뉴질랜드', 'Nicaragua': '니카라과', 'Niger': '니제르', 'Nigeria': '나이지리아',
               'North Macedonia (Rep. of)': '북마케도니아', 'Norway': '노르웨이', 'Oman': '오만', 'Pakistan': '파키스탄',
               'Palestinian Auton. Territories': '팔레스타인', 'Panama': '파나마', 'Papua New Guinea': '파푸아뉴기니',
               'Paraguay': '파라과이',  'Peru': '페루', 'Philippines': '필리핀', 'Poland': '폴란드', 'Portugal': '포르투갈',
               'Qatar': '카타르', 'Romania': '루마니아',
               'Russia': '러시아', 'Rwanda': '르완다', 'Saharan Arab Democratic Republic': '사하라아랍민주공화국',
               'Saint Lucia': '세인트루시아', 'San Marino': '산마리노', 'Sao Tome And Principe': '상투메프린시페',
               'Saudi Arabia': '사우디아라비아', 'Senegal': '세네갈', 'Serbia': '세르비아', 'Seychelles': '세이셸',
               'Sierra Leone': '시에라리온',
               'Singapore': '싱가포르', 'Slovakia': '슬로바키아', 'Slovenia': '슬로베니아', 'Somalia': '소말리아',
               'South Africa': '남아프리카공화국', 'South Sudan': '남수단', 'Spain': '스페인', 'Sri Lanka': '스리랑카',
               'Sudan': '수단', 'Suriname': '수리남', 'Swaziland': '에스와티니', 'Sweden': '스웨덴', 'Switzerland': '스위스',
               'Syria': '시리아', 'Chinese Taipei': '대만', 'Tajikistan': '타지키스탄', 'Tanzania': '탄자니아', 'Thailand': '태국',
               'Timor-Leste': '동티모르', 'Togo': '토고', 'Trinidad And Tobago': '트리니다드 토바고', 'Tunisia': '튀니지',
               'Turkey': '터키',
               'Turkmenistan': '투르크메니스탄', 'Uganda': '우간다', 'Ukraine': '우크라이나', 'United Arab Emirates': '아랍에미리트',
               'United Kingdom': '영국', 'United States of America': '미국', 'Uruguay': '우루과이', 'Uzbekistan': '우즈베키스탄',
               'Vanuatu': '바누아투', 'Venezuela': '베네수엘라', 'Vietnam': '베트남', 'Western Sahara': '서사하라', 'Yemen': '예멘',
               'Zambia': '잠비아', 'Zimbabwe': '짐바브웨', 'Netherlands': '네덜란드', 'Central African Republic': '중앙아프리카공화국',
               'Mayotte (France)': '마요트', 'Guadeloupe (France)': '과들루프', 'French Guiana': '프랑스령기아나',
               'French Polynesia': '프랑스령폴리네시아', 'Reunion (France)': '레위니옹', 'Samoa': '사모아',
               'Serbia and Montenegro': '세르비아몬테네그로', 'St. Helena': '세인트헬레나'
               }  # 국가 딕셔너리


# 대륙별 국가 분류
asia_dic = {
    '아시아': ['대한민국', '북한', '일본', '몽골', '중국', '대만', '마카오', '홍콩', '브루나이', '인도네시아', '캄보디아', '라오스', '말레이시아', '미얀마', '필리핀',
            '싱가포르', '태국', '동티모르', '베트남', '네팔', '몰디브', '방글라데시', '부탄', '스리랑카', '인도', '파키스탄', '이란', '아프가니스탄', '우즈베키스탄',
            '카자흐스탄', '키르기스스탄', '타지키스탄', '투르크메니스탄', '레바논', '바레인', '사우디아라비아', '시리아', '아랍에미리트', '아르차흐공화국', '예멘', '오만',
            '요르단', '이라크', '이스라엘', '카타르', '쿠웨이트', '키프로스', '북키프로스', '팔레스타인', '남오세티야', '압하지야'
            ]
    }

africa_dic = {
    '아프리카': ['코모로', '지부티', '에리트레아', '에티오피아', '케냐', '세이셸', '소말리아', '소말릴란드', '탄자니아', '중앙아프리카공화국', '콩고민주공화국', '우간다',
             '브룬디', '르완다', '남수단', '베냉', '부르키나파소', '카보베르데', '차드', '코트디부아르', '감비아', '가나', '기니', '기니비사우', '라이베리아', '말리',
             '모리타니', '니제르', '나이지리아', '비아프라', '세네갈', '시에라리온', '토고', '콩고', '적도기니', '가봉', '카메룬', '상투메프린시페', '알제리',
             '이집트', '리비아', '모로코', '수단', '튀니지', '사하라아랍민주공화국', '서사하라', '앙골라', '보츠와나', '에스와티니', '레소토', '마다가스카르',
             '말라위', '모리셔스', '모잠비크', '나미비아', '남아프리카공화국', '잠비아', '멜리야', '세우타', '짐바브웨', '마요트', '레위니옹', '세인트헬레나'
             ]
    }

europe_dic = {
    '유럽': ['아르메니아', '아제르바이잔', '터키', '러시아', '포르투갈', '몰타', '스페인', '산마리노', '바티칸', '세르비아', '몬테네그로', '슬로베니아', '그리스',
           '보스니아헤르체고비나', '북마케도니아', '알바니아', '크로아티아', '코소보', '이탈리아', '아이슬란드', '영국', '잉글랜드', '스코틀랜드', '북아일랜드', '웨일스',
           '아일랜드', '덴마크', '핀란드', '노르웨이', '스웨덴', '에스토니아', '라트비아', '리투아니아', '루마니아', '몰도바', '트란스니스트리아', '벨라루스', '불가리아',
           '슬로바키아', '우크라이나', '체코', '폴란드', '헝가리', '프랑스', '룩셈부르크', '벨기에', '네덜란드', '독일', '스위스', '안도라', '모나코', '오스트리아',
           '리히텐슈타인', '세르비아몬테네그로', '조지아'
           ]
    }

america_dic = {
    '아메리카': ['미국', '캐나다', '멕시코', '과테말라', '그레나다', '니카라과', '도미니카공화국', '도미니카연방', '바베이도스', '바하마', '벨리즈', '세인트루시아',
             '세인트빈센트그레나딘', '세인트키츠네비스', '아이티', '앤티가바부다', '엘살바도르', '온두라스', '자메이카', '코스타리카', '쿠바', '트리니다드토바고',
             '파나마', '가이아나', '베네수엘라', '볼리비아', '브라질', '수리남', '아르헨티나', '에콰도르', '우루과이', '칠레', '콜롬비아', '파라과이', '페루',
             '퀴라소', '과들루프', '프랑스령기아나'
             ]
    }

oceania_dic = {
    '오세아니아': ['괌', '나우루', '뉴질랜드', '니우에', '마셜제도', '미크로네시아연방', '바누아투', '북마리아나제도', '사모아', '솔로몬제도', '호주', '쿡제도',
              '키리바시', '통가', '투발루', '파푸아뉴기니', '팔라우', '피지', '누벨칼레도니', '프랑스령폴리네시아'
              ]
    }


# 대륙 전체 딕셔너리
continent_dic = {**asia_dic, **africa_dic, **america_dic, **europe_dic, **oceania_dic}  # **dic: dic 합치기


'''국가 딕셔너리를 이용해 한글화'''

def country_match(country_en):

    try:
        country_en = country_en.strip()
        country_kr = country_dic[country_en]
    except:
        country_kr = country_en

    return country_kr


'''
해당 국가의 대륙 넣기
    - 각 대륙 딕셔너리에 해당 국가 찾음
    - 모두 다 해당 안 되면 None 반환
'''

def continent_match(country_kr):

    continent = None

    if type(country_kr) == str:

        if country_kr in continent_dic['아시아']:
            continent = '아시아'
        elif country_kr in continent_dic['아프리카']:
            continent = '아프리카'
        elif country_kr in continent_dic['아메리카']:
            continent = '아메리카'
        elif country_kr in continent_dic['유럽']:
            continent = '유럽'
        elif country_kr in continent_dic['오세아니아']:
            continent = '오세아니아'

    return continent


