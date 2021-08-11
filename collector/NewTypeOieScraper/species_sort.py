# coding = UTF-8

import pandas as pd, re

'''
새로운 축종은 species_dic에 딕셔너리(key: value) 형태로 추가
소문자로 추가해야 함
'''

species_dict = {
    'accipitridae (unidentified):accipitridae (incognita)(accipitridae)': '수리과',"american mink (neovison vison):mustelidae-carnivora":"아메리카밍크속",
    "barnacle goose (branta leucopsis):anatidae-anseriformes":"흑기러기속","black swan (cygnus atratus):anatidae-anseriformes":"고니속",
    "brent goose (branta bernicla):anatidae-anseriformes":"흑기러기","canada goose (branta canadensis):anatidae-anseriformes":"캐나다기러기",
    "common coot (fulica atra):rallidae-gruiformes":"유라시아 물닭","common pheasant (phasianus colchicus):phasianidae-galliformes":"꿩",
    "common starling (sturnus vulgaris):sturnidae-pelecaniformes":"유럽찌르레기","common wood-pigeon (columba palumbus):columbidae-columbiformes":"숲비둘기",
    "dalmatian pelican (pelecanus crispus):pelecanidae-phaethontiformes":"사다새","eurasian buzzard (common buzzard) (buteo buteo):accipitridae-accipitriformes":"말똥가리",
    "eurasian jay (garrulus glandarius):corvidae-pelecaniformes":"유라시아어치","eurasian sparrowhawk (accipiter nisus):accipitridae-accipitriformes":"새매",
    "garganey (spatula querquedula):anatidae-anseriformes":"발구지","great egret (ardea alba):ardeidae-phaethontiformes":"대백로",
    "grey heron (ardea cinerea):ardeidae-phaethontiformes":"왜가리","greylag goose (anser anser):anatidae-anseriformes":"회색기러기",
    "indian peafowl (pavo cristatus):phasianidae-galliformes":"보통 공작새","mallard (anas platyrhynchos):anatidae-anseriformes":"청둥오리",\
    "mew gull (larus canus):laridae-charadriiformes":"갈매기","muscovy duck (cairina moschata):anatidae-anseriformes":"머스코비오리",
    "mustelidae":"족제비과","mute swan (cygnus olor):anatidae-anseriformes":"혹고니",
    "nene (branta sandvicensis):anatidae-anseriformes":"하와이기러기","northern goshawk (accipiter gentilis):accipitridae-accipitriformes":"참매",
    "peregrin falcon (falco peregrinus):falconidae-falconiformes":"매","red kite (milvus milvus):accipitridae-accipitriformes":"붉은 솔개",
    "redwing (turdus iliacus):turdidae-pelecaniformes":"붉은 날개 지빠귀","whooper swan (cygnus cygnus):anatidae-anseriformes":"큰고니",
    "wild boar (sus scrofa):suidae-artiodactyla":"멧돼지","wild turkey (meleagris gallopavo):phasianidae-galliformes":"야생 칠면조",
    'african black oystercatcher :haematopus moquini(haematopodidae)': '아프리카오이스터캐처', 'african buffalo (cape buffalo):syncerus caffer(bovidae)': '아프리카물소', 'african elephant:loxodonta africana(elephantidae)': '아프리카코끼리', 'african rock pigeon:columba guinea(columbidae)': '아프리카비둘기', 'alexandrine parakeet:psittacula eupatria(psittacidae)': '대본청', 'alpaca:lama pacos(camelidae)': '알파카', 'alpine marmot:marmota marmota(sciuridae)': '알프스마못', 'american mink:neovison vison(mustelidae)': '아메리카밍크', 'american wigeon:anas americana(anatidae)': '아메리카홍머리오리', 'anatidae (unidentified):anatidae (incognita)(anatidae)': '오리과', 'anserinae (unidentified):anserinae (incognita)(anatidae)': '기러기아과', 'antelope jackrabbit :lepus alleni(leporidae)': '영양산토끼', 'arctic fox:vulpes lagopus(canidae)': '북극여우', 'ardeidae (unidentified):ardeidae (incognita)(ardeidae)': '왜가리과', 'armenian gull:larus armenicus(laridae)': '아르메니아 갈매기', 'asian house shrew:suncus murinus(soricidae)': '사향땃쥐', 'asian openbill:anastomus oscitans(ciconiidae)': '아시아 오픈빌 황새', 'asiatic golden cat:catopuma temminckii(felidae)': '아시아 황금고양이', 'aves (unidentified):aves (incognita)(aves)': '조류', 'bald eagle:haliaeetus leucocephalus(accipitridae)': '흰머리수리', 'bar-headed goose:anser indicus(anatidae)': '줄기러기', 'barn owl (common barn-owl):tyto alba(tytonidae)': '원숭이 올빼미', 'barn swallow:hirundo rustica(hirundinidae)': '제비', 'bean goose:anser fabalis(anatidae)': '큰기러기', 'bees (hives)': '벌(벌집)', "bernier's teal:anas bernieri(anatidae)": '마다가스카르 청록새', 'birds': '조류', 'black swan:cygnus atratus(anatidae)': '흑고니', 'black wildebeest:connochaetes gnou(bovidae)': '흰꼬리누', 'black-backed jackal:canis mesomelas(canidae)': '검은등자칼', 'black-crowned night-heron:nycticorax nycticorax(ardeidae)': '해오라기', 'black-faced spoonbill:platalea minor(threskiornithidae)': '저어새', 'black-headed gull:larus ridibundus(laridae)': '붉은부리갈매기', 'black-headed heron :ardea melanocephala(ardeidae)': '검은머리헤론새', 'black-necked grebe:podiceps nigricollis(podicipedidae)': '검은목논병아리', 'black-tailed jackrabbit:lepus californicus(leporidae)': '캘리포니아멧토끼', 'black-winged stilt:himantopus himantopus(charadriidae)': '장다리물떼새', 'blue crane:grus paradisea(gruidae)': '청두루미', 'bombycillidae (unidentified):bombycillidae (incognita)(bombycillidae)': '여새류', "bonelli's eagle:hieraaëtus fasciatus(accipitridae)": '흰배줄무늬수리', 'brent goose:branta bernicla(anatidae)': '흑기러기', 'brown hare (european hare):lepus europaeus(leporidae)': '산토끼속', 'budgerigar:melopsittacus undulatus(psittacidae)': '사랑앵무속', 'buffaloes': '버팔로', 'bush duiker (gray duiker):sylvicapra grimmia(bovidae)': '다이커영양', 'bushpig:potamochoerus larvatus(suidae)': '부시피그', 'cackling goose:branta hutchinsii(anatidae)': '케클링구스', 'camelidae': '낙타과', 'camelidae (unidentified):camelidae (incognita)(camelidae)': '낙타과', 'canada goose:branta canadensis(anatidae)': '캐나다구스', 'cape cormorant:phalacrocorax capensis(phalacrocoracidae)': '케이프 가마우지', 'cape gannet :sula capensis(sulidae)': '케이프가넷', 'carrion crow:corvus corone(corvidae)': '송장까마귀', 'cats': '고양이', 'cattle': '소', 'cervidae': '사슴과', 'chamois:rupicapra rupicapra(bovidae)': '샤무아', 'charadriidae (unidentified):charadriidae (incognita)(charadriidae)': '물떼새과', 'chinese ferret-badger:melogale moschata(mustelidae)': '중국족제비오소리', 'ciconiidae (unidentified):ciconiidae(incognita)(ciconiidae)': '황새과', 'clay-colored thrush:turdus grayi(turdidae)': '흙색지빠귀', 'cockatiel:nymphicus hollandicus(psittacidae)': '왕관앵무', 'columbidae (unidentified):columbidae (incognita)(columbidae)': '비둘기', 'common chimpanzee:pan troglodytes(hominidae)': '침팬지속', 'common coot:fulica atra(rallidae)': '유라시아 물닭', 'common crane:grus grus(gruidae)': '검은목두루미', 'common eider:somateria mollissima(anatidae)': '참솜깃오리', 'common goldeneye:bucephala clangula(anatidae)': '흰뺨오리', 'common grackle:quiscalus quiscula(icteridae)': '큰검은찌르레기', 'common guineafowl:numida meleagris(numididae)': '호로새', 'common kestrel:falco tinnunculus(falconidae)': '황조롱이', 'common magpie:pica pica(corvidae)': '유라시아까치', 'common merganser:mergus merganser(anatidae)': '비오리', 'common moorhen:gallinula chloropus(rallidae)': '쇠물닭', 'common pheasant:phasianus colchicus(phasianidae)': '꿩', 'common pochard:aythya ferina(anatidae)': '흰죽지속', 'common raven:corvus corax(corvidae)': '큰까마귀', 'common ringed plover:charadrius hiaticula(charadriidae)': '흰죽지꼬마물떼새', 'common shelduck:tadorna tadorna(anatidae)': '혹부리오리', 'common starling:sturnus vulgaris(sturnidae)': '유럽찌르레기', 'common teal:anas crecca(anatidae)': '쇠오리', 'common tern:sterna hirundo(laridae)': '제비갈매기', 'common wood-pigeon:columba palumbus(columbidae)': '숲비둘기', "cooper's hawk:accipiter cooperii(accipitridae)": '쿠퍼매', 'corsac fox:vulpes corsac(canidae)': '코사크여우', 'corvidae (unidentified):corvidae (incognita)(corvidae)': '까마귀과', 'coscoroba swan:coscoroba coscoroba(anatidae)': '코스코로바고니', 'cottontail rabbits:sylvilagus(leporidae)': '솜꼬리토끼', 'crested myna:acridotheres cristatellus(sturnidae)': '중국 찌르레기', 'crowned cormorant :microcarbo coronatus(phalacrocoracidae)': '가마우지', 'cygnus (unidentified):cygnus (incognita)(anatidae)': '백조', 'dalmatian pelican:pelecanus crispus(pelecanidae)': '사다새', 'desert cottontail:sylvilagus audubonii(leporidae)': '사막솜꼬리토끼', 'dog:canis familiaris(canidae)': '개', 'dogs': '개', 'domestic dog:canis lupus familiaris(canidae)': '개', 'dorcas gazelle:gazella dorcas(bovidae)': '도르카스가젤', 'dromaiidae (unidentified):dromaiidae (incognita)(dromaiidae)': '에뮤속', 'eastern grey kangaroo:macropus giganteus(macropodidae)': '동부회색캥거루', 'egyptian goose:alopochen aegyptiaca(anatidae)': '이집트기러기', 'emu:dromaius novaehollandiae(dromaiidae)': '에뮤', 'equidae': '말과', 'eurasian bittern:botaurus stellaris(ardeidae)': '알락해오라기', 'eurasian blackbird:turdus merula(turdidae)': '대륙검은지빠귀', 'eurasian buzzard (common buzzard):buteo buteo(accipitridae)': '말똥가리', 'eurasian collared-dove:streptopelia decaocto(columbidae)': '염주비둘기', 'eurasian curlew:numenius arquata(scolopacidae)': '마도요', 'eurasian eagle-owl:bubo bubo(strigidae)': '수리부엉이', 'eurasian griffon:gyps fulvus(accipitridae)': '흰목대머리수리', 'eurasian hobby:falco subbuteo(falconidae)': '새호리기', 'eurasian jackdaw:corvus monedula(corvidae)': '서양갈까마귀', 'eurasian sparrowhawk:accipiter nisus(accipitridae)': '새매', 'eurasian spoonbill:platalea leucorodia(threskiornithidae)': '노랑부리저어새', 'eurasian wigeon:anas penelope(anatidae)': '홍머리오리', 'european badger:meles meles(mustelidae)': '유럽오소리', 'european bison (wisent):bison bonasus(bovidae)': '유럽들소', 'european pine marten:martes martes(mustelidae)': '소나무담비', 'european rabbit:oryctolagus cuniculus(leporidae)': '굴토끼', 'falcated duck:anas falcata(anatidae)': '청머리오리', 'falconidae (unidentified):falconidae (incognita)(falconidae)': '매과', 'fallow deer:dama dama(cervidae)': '다마사슴', 'ferruginous pochard:aythya nyroca(anatidae)': '검은흰죽지', 'fieldfare:turdus pilaris(turdidae)': '회색머리지빠귀', 'gadwall:anas strepera(anatidae)': '알락오리', 'galliformes (inidentified):galliformes (incognita)(galliformes)': '닭목', 'gemsbok:oryx gazella(bovidae)': '겜스복', 'glossy ibis:plegadis falcinellus(threskiornithidae)': '글로시아이비스', 'goats': '산양', 'goitered gazelle:gazella subgutturosa(bovidae)': '갑상선가젤 ', 'golden jackal:canis aureus(canidae)': '황금자칼', 'granada hare:lepus granatensis(leporidae)': '그라나다멧토끼', "grant's gazelle:gazella granti(bovidae)": '그랜트가젤', 'grass owl:tyto longimembris(tytonidae)': '동쪽풀올빼미 ', 'great black-backed gull:larus marinus(laridae)': '큰검은등갈매기', 'great black-headed gull:larus ichthyaetus(laridae)': '큰머리검은갈매기', 'great cormorant:phalacrocorax carbo(phalacrocoracidae)': '민물가마우지', 'great crested grebe:podiceps cristatus(podicipedidae)': '뿔논병아리', 'great crested tern:thalasseus bergii(laridae)': '큰제비갈매기 ', 'great egret:ardea alba(ardeidae)': '대백로', 'great grey owl:strix nebulosa(strigidae)': '큰회색올빼미', 'great horned owl:bubo virginianus(strigidae)': '미국수리부엉이', 'great tit:parus major(paridae)': '박새', 'great white pelican:pelecanus onocrotalus(pelecanidae)': '분홍사다새 ', 'greater flamingo:phoenicopterus roseus(phoenicopteridae)': '대홍학 ', 'greater kudu:tragelaphus strepsiceros(bovidae)': '큰쿠두', 'greater rhea:rhea americana(rheidae)': '아메리카레아', 'greater scaup:aythya marila(anatidae)': '검은머리흰죽지', 'greater white-fronted goose:anser albifrons(anatidae)': '쇠기러기', 'green sandpiper:tringa ochropus(scolopacidae)': '삑삑도요', 'green-winged teal:anas carolinensis(anatidae)': '미국쇠오리 ', 'grey heron:ardea cinerea(ardeidae)': '왜가리', 'grey parrot:psittacus erithacus(psittacidae)': '회색앵무', 'grey-headed gull:chroicocephalus cirrocephalus(laridae)': '회색 머리 갈매기', 'greylag goose:anser anser(anatidae)': '회색기러기', 'gruidae (unidentified):gruidae (incognita)(gruidae)': '두루미과', 'gyrfalcon:falco rusticolus(falconidae)': '백송고리', 'haematopodidae (unidentified):haematopodidae (incognita)(haematopodidae)': '검은머리물떼새류', 'hares / rabbits': '토끼', "hartlaub's gull:chroicocephalus hartlaubii(laridae)": '왕 갈매기', 'herring gull:larus argentatus(laridae)': '재갈매기 ', 'hippopotamidae (unidentified):hippopotamidae (incognita)(hippopotamidae)': '하마과', 'hippopotamus:hippopotamus amphibius(hippopotamidae)': '하마', 'hirundinidae (unidentified):hirundinidae (incognita)(hirundinidae)': '제비과', 'hooded crane:grus monacha(gruidae)': '흑두루미 ', 'hooded crow:corvus cornix(corvidae)': '뿔까마귀', 'house crow:corvus splendens(corvidae)': '집까마귀', 'house sparrow:passer domesticus(passeridae)': '집참새', 'ibex:capra ibex(bovidae)': '알파인 아이벡스', 'impala:aepyceros melampus(bovidae)': '임팔라', 'imperial eagle:aquila heliaca(accipitridae)': '흰죽지수리 ', 'indian hog deer:hyelaphus porcinus(cervidae)': '인도돼지사슴', 'indian peafowl:pavo cristatus(phasianidae)': '보통 공작새', 'indian pond heron:ardeola grayii(ardeidae)': '인도폰드헤론', 'jackal buzzard:buteo rufofuscus(accipitridae)': '자칼 독수리', 'jackass penguin:spheniscus demersus(spheniscidae)': '아프리카펭귄', 'jackrabbit:lepus(leporidae)': '잭토끼', 'japanese white-eye:zosterops japonicus(zosteropidae)': '동박새 ', 'kentish plover:charadrius alexandrinus(charadriidae)': '흰물떼새', 'key deer:odocoileus virginianus clavium(cervidae)': '키사슴', 'large-billed crow:corvus macrorhynchos(corvidae)': '큰부리까마귀', 'laridae (unidentified):laridae (incognita)(laridae)': '갈매기과', 'laughing dove:streptopelia senegalensis(columbidae)': '웃는비둘기', 'leporidae (unidentified):leporidae (incognita)(leporidae)': '토끼', 'lesser adjutant:leptoptilos javanicus(ciconiidae)': '대머리황새속', 'lesser black-backed gull:larus fuscus(laridae)': '줄무늬노랑발갈매기', 'lesser kestrel:falco naumanni(falconidae)': '작은황조롱이', 'lesser spotted eagle:aquila pomarina(accipitridae)': '작은점무늬수리', 'lesser white-fronted goose:anser erythropus(anatidae)': '흰이마기러기', 'light-vented bulbul:pycnonotus sinensis(pycnonotidae)': '검은이마직박구리', 'lion:panthera leo(felidae)': '사자', 'little egret:egretta garzetta(ardeidae)': '쇠백로 ', 'little grebe:tachybaptus ruficollis(podicipedidae)': '논병아리', 'little owl:athene noctua(strigidae)': '금눈쇠올빼미', 'little ringed plover:charadrius dubius(charadriidae)': '꼬마물떼새', 'little stint:calidris minuta(scolopacidae)': '작은도요', 'llama:lama glama(camelidae)': '라마', 'long-eared owl:asio otus(strigidae)': '칡부엉이', "lord derby's parakeet:psittacula derbiana(psittacidae)": '대달마 앵무', 'mallard (domestic):anas platyrhynchos domesticus(anatidae)': '청둥오리', 'mallard:anas platyrhynchos(anatidae)': '청둥오리', 'mandarin duck:aix galericulata(anatidae)': '원앙', 'marbled teal:marmaronetta angustirostris(anatidae)': '대리석무늬오리', 'mew gull:larus canus(laridae)': '갈매기', 'mongolian saiga:saiga tatarica mongolica(bovidae)': '사이가산양', 'moose:alces alces(cervidae)': '말코손바닥사슴', 'mouflon:ovis orientalis(bovidae)': '무플론', 'mountain cottontail:sylvilagus nuttallii(leporidae)': '산솜꼬리토끼', 'mountain gazelle:gazella gazella(bovidae)': '마운틴가젤', 'mountain hare:lepus timidus(leporidae)': '고산토끼', 'muscovy duck:cairina moschata(anatidae)': '머스코비오리', 'mute swan:cygnus olor(anatidae)': '혹고니', 'northern goshawk:accipiter gentilis(accipitridae)': '참매', 'northern pintail:anas acuta(anatidae)': '고방오리', 'northern shoveler:anas clypeata(anatidae)': '넓적부리', 'nubian ibex:capra nubiana(bovidae)': '들 염소', 'numididae (unidentified):numididae (incognita)(numididae)': '뿔닭과', 'nyala:tragelaphus angasii(bovidae)': '니알라', 'oriental magpie-robin:copsychus saularis(muscicapidae)': '오리엔탈 개똥지빠귀', 'oriental white ibis:threskiornis melanocephalus(threskiornithidae)': '검은머리흰따오기', 'other species:other species()': '기타(other)', 'pale thrush:turdus pallidus(turdidae)': '흰배지빠귀', 'passeridae (unidentified):passeridae (incognita)(passeridae)': '참새과', 'patagonian mara:dolichotis patagonum(caviidae)': '마라', 'pelecanidae (unidentified):pelecanidae (incognita)(pelecanidae)': '사다새과', 'peregrin falcon:falco peregrinus(falconidae)': '매 ', 'phalacrocoracidae (unidentified):phalacrocoracidae (incognita)(phalacrocoracidae)': '가마우지과', 'phasianidae (unidentified):phasianidae (incognita)(phasianidae)': '꿩과', 'philippine flying lemur:cynocephalus volans(cynocephalidae)': '필리핀날원숭이', 'phoenicopteridae (unidentified):phoenicopteridae (incognita)(phoenicopteridae)': '홍학과', 'pied avocet:recurvirostra avosetta(recurvirostridae)': '구대륙뒷부리장다리물떼새', 'pied crow:corvus albus(corvidae)': '흰가슴까마귀', 'pink-footed goose:anser brachyrhynchus(anatidae)': '분홍발기러기', 'plain chachalaca:ortalis vetula(cracidae)': '닭목', 'psittacidae (unidentified):psittacidae (incognita)(psittacidae)': '앵무과', 'puma:puma concolor(felidae)': '푸마', 'pygmy brocket :mazama nana(cervidae)': '마자마사슴속', 'pygmy cormorant:phalacrocorax pygmaeus(phalacrocoracidae)': '난쟁이가마우지', 'rabbits': '토끼', 'raccoon dog:nyctereutes procyonoides(canidae)': '너구리', 'racoon (northern raccoon):procyon lotor(procyonidae)': '너구리', 'rallidae (unidentified):rallidae (incognita)(rallidae)': '뜸부기과', 'red deer:cervus elaphus(cervidae)': '말사슴', 'red fox:vulpes vulpes(canidae)': '붉은여우', 'red headed trogon:harpactes erythrocephalus(trogonidae)': '비단날개새목', 'red-and-green macaw:ara chloropterus(psittacidae)': '홍금강앵무', 'red-crested pochard:netta rufina(anatidae)': '붉은부리흰죽지', 'red-crowned crane:grus japonensis(gruidae)': '두루미', 'red-tailed hawk:buteo jamaicensis(accipitridae)': '붉은꼬리매 ', 'red-whiskered bulbul:pycnonotus jocosus(pycnonotidae)': '붉은수염직박구리', "reeves's pheasant:syrmaticus reevesii(phasianidae)": '긴꼬리꿩', 'rhea:rhea(struthionidae)': '레아', 'ring-necked dove:streptopelia capicola(columbidae)': '고리무늬목비둘기', 'ring-necked duck:aythya collaris(anatidae)': '고리무늬목비둘기', 'rock pigeon (rock dove):columba livia(columbidae)': '바위비둘기', 'rook:corvus frugilegus(corvidae)': '떼까마귀', 'rose-ringed parakeet:psittacula krameri(psittacidae)': '장미목도리앵무', 'rosy-faced lovebird:agapornis roseicollis(psittacidae)': '벚꽃모란앵무', 'ruddy shelduck:tadorna ferruginea(anatidae)': '황오리', 'ruff:philomachus pugnax(scolopacidae)': '목도리도요', 'sacred ibis:threskiornis aethiopicus(threskiornithidae)': '아프리카흑따오기', 'saiga antelope:saiga tatarica(bovidae)': '사이가산양', 'saker falcon:falco cherrug(falconidae)': '세이커매', 'sambar:cervus unicolor(cervidae)': '물사슴', 'sandwich tern:thalasseus sandvicensis(laridae)': '샌드위치제비갈매기', 'scarlet macaw:ara macao(psittacidae)': '금강앵무', 'scolopacidae (unidentified):scolopacidae (incognita)(scolopacidae)': '도요과', 'sheep': '면양', 'sheep / goats': '면양/산양', 'short-eared owl:asio flammeus(strigidae)': '쇠부엉이', 'siberian ibex:capra sibirica(bovidae)': '시베리아 아이벡스', 'silver teal:anas versicolor(anatidae)': '오리속', 'snow goose:anser caerulescens(anatidae)': '흰기러기속', 'snowy owl:bubo scandiacus(strigidae)': '흰올빼미', 'solomons cockatoo:cacatua ducorpsii(psittacidae)': '솔로몬유황앵무', 'song thrush:turdus philomelos(turdidae)': '노래지빠귀', 'southern masked-weaver:ploceus velatus(ploceidae)': '남아프리카 베짜기새', 'spheniscidae (unidentified):spheniscidae (incognita)(spheniscidae)': '펭귄', 'spot-billed pelican:pelecanus philippensis(pelecanidae)': '사다새', 'spotted eagle-owl:bubo africanus(strigidae)': '수리부엉이속', 'spotted wood owl:strix seloputo(strigidae)': '수리부엉이속', 'spur-winged goose:plectropterus gambensis(anatidae)': '박차날개기러기', 'spur-winged lapwing:vanellus spinosus(charadriidae)': '아프리카발톱깃물떼새', 'steppe eagle:aquila nipalensis(accipitridae)': '초원수리', 'strigidae (unidentified):strigidae (incognita)(strigidae)': '올빼미과', 'suidae (unidentified):suidae (incognita)(suidae)': '멧돼지과', 'svalbard reindeer:rangifer tarandus platyrhynchus(cervidae)': '스발바르 순록', 'swine': '돼지', 'tawny owl:strix aluco(strigidae)': '올빼미', 'threskiornithidae (unidentified):threskiornithidae (incognita)(threskiornithidae)': '저어새과', 'tiger:panthera tigris(felidae)': '호랑이', 'tufted duck:aythya fuligula(anatidae)': '댕기흰죽지', 'tundra swan:cygnus columbianus(anatidae)': '고니', 'turdidae (unidentified):turdidae (incognita)(turdidae)': '개똥지빠귀', 'unidentified:incognita(incognita)': '기타', 'unknown species': '기타', 'viverridae (unidentified):viverridae (incognita)(viverridae)': '사향고양이과', 'western cattle egret:bubulcus ibis(ardeidae)': '황로속', 'western marsh harrier:circus aeruginosus(accipitridae)': '유럽개구리매', 'western roe deer:capreolus capreolus(cervidae)': '유럽노루', 'white rhinoceros:ceratotherium simum(rhinocerotidae)': '흰코뿔소', 'white stork:ciconia ciconia(ciconiidae)': '홍부리황새', 'white-naped crane:grus vipio(gruidae)': '재두루미', 'white-rumped munia:lonchura striata(estrildidae)': '십자매', 'white-tailed eagle:haliaeetus albicilla(accipitridae)': '흰꼬리수리', 'white-winged tern:chlidonias leucopterus(laridae)': '흰죽지갈매기 ', 'whooper swan:cygnus cygnus(anatidae)': '큰고니', 'wild boar:sus scrofa(suidae)': '멧돼지', 'wild species': '야생종', 'wolf (gray wolf):canis lupus(canidae)': '회색 늑대', 'wood duck:aix sponsa(anatidae)': '아메리카원앙', 'wood sandpiper:tringa glareola(scolopacidae)': '알락도요', 'yak (grunting ox):bos grunniens(bovidae)': '야크', 'yellow-billed duck:anas undulata(anatidae)': '노랑 부리 오리', 'yellow-collared lovebird:agapornis personatus(psittacidae)': '황금모란앵무', 'zebra finch:taeniopygia guttata(estrildidae)': '금화조', 'roan antelope:hippotragus equinus(bovidae)': '론영양', "chapman's zebra:equus quagga chapmani(equidae)": '채프먼얼룩말',
    }    


'''축종 딕셔너리를 이용해 한글화'''

def species_match(species_en):

    try:
        species_kr = species_dict[species_en.lower()]  # lower(): 소문자로 변환
    
    except:
        species_kr = species_en

    return species_kr


'''구분의 '사육'/'야생' 분류'''

# 장소 분류
stock_place_dic = {'사육': ['Apiary', 'Backyard', 'Farm', 'Livestock market', 'Slaughterhouse', 'Village']}
wild_place_dic = {'야생': ['Forest', 'Natural park', 'Zoo']}

# 축종 분류
stock_species_dic = {'사육': ['돼지', '소', '말과', '산양', '면양', '면양/산양']}
wild_species_dic = {'야생': ['멧돼지', '야생종', '오리과', '굴토끼', '청둥오리', '큰고니']}

stockable_species_dic = {'사육 가능성': ['가금', '돼지', '소', '말과', '산양', '면양', '면양/산양', '벌(벌집)', '조류', '버팔로', '고양이', '낙타과', '개', '토끼']}

# 세부 축종 분류
stock_keywords = {'사육': ['backyard', 'domestic', 'household', 'pet', 'pets']} 
wild_keywords = {'야생': ['wild']}

'''
장소 분류 딕셔너리를 이용해 구분 반환
    - 우선, '장소' 값이 결측치(None, NaN 등)인 것 제외
        1. 장소가 '사육 장소(stock_place_dic)'에 속한 경우: '사육'
            - 단, 축종이 '사육 동물일 가능성이 높은 동물'에 해당하지 않고 사육 두수에 값이 없으면(예: NaN, None, 0): '야생'
        2. 장소가 '야생 장소(wild_place_dic)'에 속한 경우: '야생'
    - 위 조건들에 해당이 안 되면 원래 값 그대로 반환    
'''

def place_sort(place, species, susceptible):

    sort = place

    if pd.notna(place):  # pd.notna로 결측값 제외

        if place in stock_place_dic['사육']:
            
            '''0 또는 결측치일 경우 논리값이 False임을 활용'''
            if (not species in stockable_species_dic['사육 가능성']) and (pd.isna(susceptible) or susceptible == 0):
                sort = '야생'
            
            else:
                sort = '사육'
        
        elif place in wild_place_dic['야생']:
            sort = '야생'
        
    return sort


'''
축종 분류 딕셔너리를 이용해 구분 반환
    - 우선, '장소' 값이 결측치(None, NaN 등)인 것 제외
    - 아직 '구분' 값이 '사육' 또는 '야생'으로 변환되지 않은 것 중에,
        1. 축종이 '사육 동물(stock_species_dic)'에 속한 경우: '사육'
        2. 축종이 '야생 동물(wild_species_dic)'에 속한 경우: '야생'
    - 위 조건들에 해당이 안 되면 원래 값 그대로 반환    
'''

def place_species_sort(place, species):

    sort = place

    if pd.notna(place):

        if not (place == '사육' or place == '야생'):
        
            if species in stock_species_dic['사육']:
                sort = '사육'
            
            elif species in wild_species_dic['야생']:
                sort = '야생'

    return sort


'''
세부 축종 딕셔너리를 이용해 구분 변환
    - 우선, '장소' 값이 결측치(None, NaN 등)인 것 제외
    - 아직 '구분' 값이 '사육' 또는 '야생'으로 변환되지 않은 것 중에,
        1. 세부 축종 내용을 모두 소문자로 변환
        2. 세부 축종 내용에 가축 키워드(stock_keywords)가 들어 있는 경우: '사육'
        3. 세부 축종 내용에 야생 키워드(wild_keywords)가 들어 있는 경우: '야생'
    - 위 조건들에 해당이 안 되면 원래 값 그대로 반환    
'''

def place_species_detail_sort(place, sentence):

    sort = place

    if pd.notna(place) and pd.notna(sentence):

        if not (place == '사육' or place == '야생'):
    
            lower_sentence = sentence.lower()  # 해당 키워드가 대문자로 되어 있는 경우가 있음
            
            '''
            위 문장에서 해당 키워드를 찾는 함수 만듦
            정규식 패턴에 정규식 기호인 '\b'를 이용하여 해당 키워드의 앞뒤로 경계를 만듦
            (예: wildlife는 제외, semi-wild나 (wild dogs)는 포함)
            '''
            match_word = lambda word, string: re.search(r'\b' + word + r'\b', string)
            
            for keyword in stock_keywords['사육']:
                
                if match_word(keyword, lower_sentence):
                    sort = '사육'
                    
                    return sort
                
            '''사육 키워드를 모두 확인 후 야생을 확인해야 함'''
            for keyword in wild_keywords['야생']:
                
                if match_word(keyword, lower_sentence):
                    sort = '야생'
                    
    return sort


'''
사육 두수가 있을 때 '사육' 반환
    - 우선, '장소' 값이 결측치(None, NaN 등)인 것 제외
    - 아직 '구분' 값이 '사육' 또는 '야생'으로 변환되지 않은 것 중에,
        1. 사육 두수에 값이 없으면(예: NaN, None, 0) '구분'에 '야생'을 반환
        2. 나머지는 '사육'을 반환
    -> 여기서 모든 '장소' 값이 '사육' 또는 '야생'으로 나뉨
'''

def place_susceptible_sort(place, susceptible):

    sort = place

    if pd.notna(place):
    
        if not (place == '사육' or place == '야생'):
        
            if pd.isna(susceptible) or susceptible == 0:
                sort = '야생'
                
            else:
                sort = '사육'

    return sort
