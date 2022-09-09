from asyncio.tasks import sleep
from asyncio import sleep
from os import remove
import numpy as np
import random
from vkbottle import DocMessagesUploader
from vkbottle.bot import Bot, Message
from vkbottle import Keyboard, KeyboardButtonColor, Text
from apiclient import discovery
from httplib2 import Http
from oauth2client import client, file, tools
from time import localtime, strftime
from qrcode import make
from pandas import Timestamp, DataFrame, ExcelWriter, read_excel
from oauth2client.tools import argparser

# надо будет ещё путь для кредов указать...

#client_json_path = "/home/terrd14/test/service_account.json"
#GoogleAuth.DEFAULT_SETTINGS['client_config_file'] = client_json_path


SCOPES = "https://www.googleapis.com/auth/drive"
DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"

def _edit_dist_step(lev, i, j, s1, s2, substitution_cost=1, transpositions=False):
    c1 = s1[i - 1]
    c2 = s2[j - 1]

    # skipping a character in s1
    a = lev[i - 1][j] + 1
    # skipping a character in s2
    b = lev[i][j - 1] + 1
    # substitution
    c = lev[i - 1][j - 1] + (substitution_cost if c1 != c2 else 0)

    # transposition
    d = c + 1  # never picked by default
    if transpositions and i > 1 and j > 1:
        if s1[i - 2] == c2 and s2[j - 2] == c1:
            d = lev[i - 2][j - 2] + 1

    # pick the cheapest
    lev[i][j] = min(a, b, c, d)
def _edit_dist_init(len1, len2):
    lev = []
    for i in range(len1):
        lev.append([0] * len2)  # initialize 2D array to zero
    for i in range(len1):
        lev[i][0] = i  # column 0: 0,1,2,3,4,...
    for j in range(len2):
        lev[0][j] = j  # row 0: 0,1,2,3,4,...
    return lev
def edit_distance(s1, s2, substitution_cost=1, transpositions=False):
    # set up a 2-D array
    len1 = len(s1)
    len2 = len(s2)
    lev = _edit_dist_init(len1 + 1, len2 + 1)

    # iterate over the array
    for i in range(len1):
        for j in range(len2):
            _edit_dist_step(
                lev,
                i + 1,
                j + 1,
                s1,
                s2,
                substitution_cost=substitution_cost,
                transpositions=transpositions,
            )
    return lev[len1][len2]


def color_negative(v, color): #вместо неё должна была быть лямбда функция
     return f"background-color: {color};" if v > 0 else None

#перевожу в нижний регистр и избавляюсь от знаков, отличных от алфавита
def clean(text):
  output_text = ''
  for char in text.lower():
    if char in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя':
      output_text = output_text + char
  return output_text

def cleaNum(text):
  try:
    type(int(text)) == int # нужно было юзать is_number, а не это
    return int(text)
  except ValueError:  
     output_text = ''
     for char in text:
       if char in '1234567890':
         output_text = output_text + char
     try:
       type(int(output_text)) == int
       return int(output_text)
     except ValueError:
       return True

#по ID нахожу человека, если он есть в БД, далее вывожу необходимую ему инфу
#называю все исключения в лице рандомных челиков

def choice(n, peer_id):
  try:
     s = data[data[3] == int(peer_id)] #Нужно не забывать про перевод буквенного ID в численный
     print(s)
     try:
       a = s.index.to_list()[0]
     except IndexError:
       return True
     return(s.loc[a].to_list()[n])
  except KeyError:
     return False

def roomFind(numb):   
   ident = []
   k=0
   try:
      for ids in data[data[2] == int(numb)][3].to_list():
         try: 
            if ident==[]:
               print(ids)
               ident = f'http://vk.com/id{int(ids)}'
               k+=1
            else:  
               ident = f'{ident}, http://vk.com/id{int(ids)}'
               k+=1
         except:
            pass
      return ident
   except KeyError:
         return True

def reverseRoomFind(id): 
   '''SELECT оценки по ID'''  
   try:
      #numb = data[data[3] == id][2].to_list()
      for ids in data[data[3] == int(id)][2].to_list():
         try:
            print(ids)
            numb = ids
         except:
            print('no')
      s = sanData[sanData[0] == numb]
      return s.iloc[0].to_list()[-1]
   except KeyError:
         return 'Нет'

def lastName (peer):
   '''На вход подаётся fromId'''
   fam = choice(1, int(peer))
   out_fam = ''
   for char in fam.lower():
      if char != ' ':
         out_fam = out_fam + char
      else:
         break
   return out_fam   

def cooRoom (peer):
   '''На вход подаётся fromId'''
   room = choice(2, int(peer))
   ident = []
   for names in data[data[2] == room][1].to_list():
      ident = ident.append(names)
   return names

# даже если юзер опечатался, система поймёт. При условии, что первой идёт фамилия...
def cleanLastName(peer, work):
   try:
      newS = set(work[2]) # TO change?
      room = str(choice(2, peer))
      lenSet = len(newS)
      nameList = work[1] # TO change?
      newS.add(room)
   except KeyError:
      return 0
   if lenSet == len(newS):
      for names in nameList:
         count = nameList.index(names)
         z = 0
         text = ''
         for char in names.lower():
            if char != ' ':
               text = text + char
            elif z != 1 and char == ' ':
               z += 1
            else:
               if len(text) != 0:
                  if edit_distance(text, lastName(peer)) / max(len(text), len(lastName(peer))) < 0.4:
                     if work[3][count].isnull():
                        return 1    # проверить, работает ли 
                     else:
                        return 1 * work[3][count] # в случае чего, оставить только эту строку
      return 0           
   else:
      return 0       

def getRoom(r): #на входе строка с КРЫЛОМ, а не комнатой; на выходе СПИСОК комнат
    setRoom = set()
    st = data[2].to_list()
    for mem in st:
      try:
        setRoom.add(int(mem))
      except:
        pass
    setFirst = []
    setSecond = []
    setThirdL = []
    setThirdR = []
    setQuadrL = []
    setQuadrR = []
    for numRoom in setRoom:
      if numRoom < 33:
        setFirst.append(numRoom)
      elif numRoom <69:
        setSecond.append(numRoom)
      elif numRoom <86:
        setThirdL.append(numRoom)
      elif numRoom <106:
        setThirdR.append(numRoom)
      elif numRoom <124 or numRoom == 129:
        setQuadrL.append(numRoom)
      else:
        setQuadrR.append(numRoom)
    roomDict = dict()    
    roomDict = {'First': setFirst,\
    'Second': setSecond,\
      'ThirdL': setThirdL,\
        'ThirdR': setThirdR,\
          'QuadrL': setQuadrL,\
            'QuadrR': setQuadrR
      }
    return roomDict.get(r)   

def choice(n, peer_id):
  try:
     s = data[data[3] == int(peer_id)] #Нужно не забывать про перевод буквенного ID в численный
     try:
       a = s.index.to_list()[0]
     except IndexError:
       return True
     return(s.loc[a].to_list()[n])
  except KeyError:
     return False

def mini(rows, n):
  tab = DataFrame.from_records(rows)
  gapList = np.zeros(len(getRoom(n)))
  newList = getRoom(n)
  print('ЭТО НАДО НАЙТИ -', int(tab[2].to_list()[1]))
  print('ИСХОДНИК:' ,newList)
  lastRoomIndex = newList.index(int(tab[2].to_list()[1]))
  for i in range(lastRoomIndex):
    newList = newList[1:]+newList[:1]

  lis = []
  s = tab[0].to_list() #Нужно не забывать про перевод строки ID в инт
  b = tab[1].to_list()
  for i in s:
    try:
      print(newList.index(int(i)))
      gapList[newList.index(int(i))] = int(b[s.index(i)])
    except:
      pass  
  lis.append(gapList)
  lis.append(lastRoomIndex)
  print(lis[0])
  return lis
  #пройтись по пандас версии гугл таблицы для кухни и получить нужные числа

def tiny (tab):
  nichi = Timestamp.now(tz= 'Europe/Moscow').day
  ind = tab[nichi].to_list().index(1)
  heya = tab.index.to_list()[ind]
  idents = []
  try:
    for ids in data[data[2] == int(heya)][3].to_list():
      idents.append(ids)
  except KeyError:
    pass
  return idents
#

bot = Bot(
    ""
)

def cleanText(t):
  try: 
     output_text = ''
     textList = []
     for char in t.lower():
       if char in '1234567890':
         output_text = output_text + char
       elif char == ' ':
          textList.append(output_text)
          output_text = '' 
       elif char == ',':
         return True 
     return textList
  except ValueError:
     return True

def update():
    shCult, shInt, shEco, \
    shTrud, shSport, shSan = \
    read_excel('/Users/admin/Desktop/2022-2023/Культур.xlsx', None, header = None), \
    read_excel('/Users/admin/Desktop/2022-2023/Инт.xlsx', None, header = None), \
    read_excel('/Users/admin/Desktop/2022-2023/Эко.xlsx', None, header = None), \
    read_excel('/Users/admin/Desktop/2022-2023/Труд.xlsx', None, header = None), \
    read_excel('/Users/admin/Desktop/2022-2023/Спорт.xlsx', None, header = None), \
    read_excel('/Users/admin/Desktop/2022-2023/Иност.xlsx', None, header = None)  
    pdList = [shCult, shInt, shEco, shTrud, shSport, shSan]
    print(pdList)
    values_list = data[1].to_list() 
    id_list = data[3].to_list()  
    values_list.pop(0)
    id_list.pop(0)
    try:
      for n in values_list: # прохожусь по людям из рейтинга
         print(n)
         nameInd = id_list[values_list.index(n)]
         cell_list = [0] * 12
         if nameInd != '': # прохожусь по листам с мероприятиями
               for i in range(len(pdList)):
                  j = 0
                  sum = 0
                  while j != len(pdList[i]):
                     worksh = pdList[i][j-1]
                     sum = sum + cleanLastName(nameInd, worksh)
                     j+=1          
                  cell_list[i] = sum
                  cell_list[i+6] = j
               data.loc[n , (i-1):(i + 6)] = cell_list
      data.to_excel('/Users/admin/Desktop/2022-2023/Рейтинг.xlsx')
    except KeyError:
      pass

data = read_excel('/Users/admin/Desktop/2022-2023/Рейтинг.xlsx', header = None)
shed = read_excel('/Users/admin/Desktop/2022-2023/raw kitch shed.xlsx', header = None)
sanData = read_excel('/Users/admin/Desktop/2022-2023/Сансектор2021-2022_рейтинг.xlsx', header = None)

bot.labeler.vbml_ignore_case = True

update()

@bot.on.private_message(text="Привет")
async def hi_handler(message: Message):
    users_info = await bot.api.users.get(message.from_id)
    print(users_info)
    await message.answer("Привет, {}".format(users_info[0].first_name))
    await sleep(1)

@bot.on.private_message(text='Подписаться')
async def subs_handler(message: Message):
   global data 
   data = read_excel('/Users/admin/Desktop/2022-2023/Рейтинг.xlsx') 
   fromId = message.from_id
   if type(choice(1, message.from_id)) != bool:
      if type(choice(4,fromId)) != float or type(choice(4,fromId)) == float:
         data.iat[f'G{int(choice(0, int(fromId)))}'] = 1
         data.to_excel('/Users/admin/Desktop/2022-2023/Рейтинг.xlsx')
         await message.answer('Теперь я буду напоминать вам о дежурствах и сообщать о некоторых субботниках,\
         если у вас недостаточное для заселения количество баллов. Чтобы отписаться, напишите "Отписаться", либо напишите "Хай" и нажмите на кнопку "Отписаться"')  
   await sleep(1)       
            
@bot.on.private_message(text='рассылка')
async def send_handler(message: Message):
   fromId = message.from_id
   ls = [data[3].to_list()[i] for i in range(len(data[3].to_list())) if data[6].to_list()[i] != 'permission' and int(data[6].to_list()[i]) == 1 ]
   if fromId == 282418233:
      for i in ls:
         try:
            await bot.api.messages.send(peer_id = i, \
                             random_id = random.randint(-2147483648, 2147483647), \
                             message = 'Советую прямо сейчас заглянуть в беседу "Копилки"! \n\
                                если ещё не входите в неё, переходите по ссылке: https://vk.me/join/AJQ1d/p8wxidjWBgu6YhgpwS')
         except:
            message.answer(f'Чекни ID {i}')
         await sleep(1)
   else:
      await message.answer(sticker_id=18471)      

@bot.on.private_message(text='Отписаться')
async def cancel_handler(message: Message):
   global data 
   data = read_excel('/Users/admin/Desktop/2022-2023/Рейтинг.xlsx') 
   fromId = message.from_id
   fromId = message.from_id
   if type(choice(1, message.from_id)) != bool:
      if type(choice(4,fromId)) != float or type(choice(4,fromId)) == float:
         data.iat[f'G{int(choice(0, int(fromId)))}'] = 0
         data.to_excel('/Users/admin/Desktop/2022-2023/Рейтинг.xlsx')
         await message.answer('Напоминать о дежурствах больше не буду. Если передумаете, напишите "Подписаться"')
   await sleep(1)      

@bot.on.private_message(text='брс')
async def balls_handler(message: Message):
   fromId = message.from_id
   if type(choice(1, message.from_id)) != bool:
      if type(choice(4,fromId)) != float or type(choice(4,fromId)) == float:
         await message.answer('За участие в любом мероприятии можно получить 2 балла, а за организацию - 15; \
            первые 4 субботника оцениваются в 2,5 балла каждый, а последующие в 5 за каждый! Подробнее о других \
               способах получить баллы вы можете узнать на странице КФУ')
   await sleep(1) 

@bot.on.private_message(text='Хай')
async def hay_handler(message: Message):
   fromId = message.from_id
   await message.answer('Здравствуй! Мне нужно кое-что проверить, так что, если будет задержка, прошу прощения')
   if type(choice(1, fromId)) != bool:
# Нужно проверить работу этого условия!
      if choice(4,fromId) != '':
         await bot.api.messages.send(peer_id = fromId, \
                             random_id = random.randint(-2147483648, 2147483647), \
                             message = 'Кроме стандартных'\
                             '"баллы", "брс", "Подписаться", "Отписаться", "код", вам доступна функция нахождения страниц проживающих по комнатам. \
                                Для этого введите номер интересующей вас комнаты. А ещё у некоторых есть команды "расписание" и "субботник"', keyboard=(\
        Keyboard(one_time=False, inline=False)\
        .add(Text("Подписаться на уведомления", {"cmd": "sender"}), color=KeyboardButtonColor.POSITIVE)\
        .add(Text("Отписаться", {"cmd": "canceller"}), color=KeyboardButtonColor.NEGATIVE)\
        .add(Text("ЭкоПамятка", {"cmd": "eco"}), color=KeyboardButtonColor.POSITIVE)).get_json())   
#"payload": {"cmd": "canceller"},
      else:
         await bot.api.messages.send(peer_id = message.from_id, random_id = \
                             random.randint(-2147483648, 2147483647), message = 'Можете спросить, сколько у вас баллов за мероприятия, \
                                какие основные способы заработать балы БРС существуют, а также можете попросить меня \
      напоминать вам о дежурствах и сообщать о субботниках, если у вас мало баллов. Для этого введите соответственно: "баллы", "брс", "Подписаться".\n \
         Если есть какая-то ошибка или вопросы к моему создателю, пишите "ошибка". Команда "дежурство", чтобы узнать, кто сегодня дежурит', keyboard=(\
        Keyboard(one_time=False, inline=False)\
        .add(Text("Подписаться на уведомления", {"cmd": "sender"}), color=KeyboardButtonColor.POSITIVE)\
        .add(Text("Отписаться", {"cmd": "canceller"}), color=KeyboardButtonColor.NEGATIVE)\
        .add(Text("ЭкоПамятка", {"cmd": "eco"}), color=KeyboardButtonColor.POSITIVE)).get_json())
   else:
      await bot.api.messages.send(peer_id = message.from_id, random_id = \
                             random.randint(-2147483648, 2147483647), message = 'Похоже, вы секретный житель общежития!' \
                             'Если хотите воспользоваться моим функционалом, обратитесь к представителю студсовета, чтобы вас добавили в базу данных')

@bot.on.private_message(text='Баллы')
async def mero_handler(message: Message):
   fromId = message.from_id
   users_info = await bot.api.users.get(fromId)
   if type(choice(4,fromId)) != float or type(choice(4,fromId)) == float:
      await message.answer('Веду подсчёт. Пожалуйста, подождите') 
   if type(choice(1, fromId)) != bool:
      if type(choice(4,fromId)) != float or type(choice(4,fromId)) == float:
         await message.answer(f'Общий балл за мероприятия c учётом множителей: \
                           {choice(-4, fromId)}; подробнее: культурный сектор - {choice(7, fromId)}, \
                           интеллектуальный - {choice(8, fromId)}, экологический - {choice(9, fromId)}, \
                           трудовой -  {choice(10, fromId)}, спортивный - {choice(11, fromId)}, \
                           сансектор - {choice(12, fromId)}, иностранный - {choice(-1, fromId)}, \
                           организовано мероприятий - {choice(-2, fromId)}')                           
   await sleep(1)

# хэндлер команды "нухня", чтобы обновлять таблички кухонь!

@bot.on.message(text = 'обнова')
async def kinchRem(message: Message):
   fromId = message.from_id
   if fromId == 282418233:
      await message.answer('Таблицу кухонь обновляю...')   
      read_excel('raw kitch shed.xlsx')
      await sleep(1)
      await message.answer('Обновил')

@bot.on.message(text = 'субботник')
async def helpHandler(message: Message):
   fromId = message.from_id
   if fromId == 72381975 or fromId == 282418233 \
   or fromId == 140234000 or fromId == 99815966:
      med = data[20].to_list()[0]
      listing = data[19].to_list()
      userList = data[3].to_list()
      ls = [userList[i] for i in range(len(listing)) if listing[i] < med]
      print(med, ls)
      await message.answer('Будет исполнено!')
      z = 0
      for i in ls: 
         try:
        #тут отправка сообщения и сон   
               await sleep(1)
               await bot.api.messages.send(peer_id = int(i), random_id = \
                             random.randint(-2147483648, 2147483647), message = 'У нас есть задание! Чтобы узнать подробности, \
                                обратитесь к Альбине Рашидовне или спросите у старосты этажа.') 
               z+=1              
         except:
            pass           
      await message.answer(f'Готово! Сообщение было отправлено стольким жильцам - {z}')

@bot.on.message(text = 'таблица')
async def sender(message: Message):
   fromId = message.from_id
   #tab_name = '/home/opc/2022_2023/Рейтинг.xlsx'
   if choice(4,fromId) != '':
      tab_name = '/Users/admin/Desktop/2022-2023/Рейтинг.xlsx'
      tab_upd = DocMessagesUploader(bot.api)
      shed_tab = await tab_upd.upload(title = tab_name, file_source = tab_name, peer_id = message.peer_id)
      await message.answer('Благодарю. Теперь проверьте табличку, которую я прислал.' \
            , attachment = shed_tab)

@bot.on.message(text = 'эко')
async def helpHandler(message: Message):
   fromId = message.from_id
   if fromId == 282418233:
      userList = data[3].to_list()
      await message.answer('Будет исполнено!')
      for i in userList: 
         try:
        #тут отправка сообщения и сон   
               await sleep(1)
               await bot.api.messages.send(peer_id = int(i), random_id = \
                             random.randint(-2147483648, 2147483647), message = 'Рад представить вам памятку от экологического сектора!\n \
                                Нами осуществляется сбор следующих фракций (также ниже правила приёма):\n \n \
                                   1. Пластик \n \n \
                                      ● Бутылки PET - из-под напитков, молока и масла \n \
                                      ● Бытовая химия - шампуни, гели, крема и тд. \n \
                                      ● Контейнеры - из-под еды (типа плавленного сыра, йогуртов и тд.) \n \
                                    Важно! Пластик нужно сдавать чистым, без остатков пищи. \n \
                                       Крышечки из-под бутылок сдавать отдельно, этикетки НЕ снимать \n \n  \
                                    2. Макулатура \n \n \
                                       ● Бумага - принимаем офисную а4, газеты, тетради, флаеры, журналы глянцевые, крафтовые пакеты \n \
                                       ● Картон - упаковки, обложки тетрадей, картон от посылок, из-под пиццы \n \
                                    Можно сдавать немного жирным, мокрым, грязным, разрисованным, глянцевым \n \n \
                                    3. Металл - из-под консервов, напитков, крышки от стеклянных банок, фольга \n \n \
                                    4. TetraPack - упаковки от соков, молока. Перед тем, как сдать, нужно \n \
                                        ОБЯЗАТЕЛЬНО разрезать упаковку по швам, тщательно промыть, снять крышку и крепление для неё \n \n \
                                    5. Стекло - цветное, прозрачное. Бумажную этикетку НЕ НУЖНО снимать')
               await sleep(1)
               await bot.api.messages.send(peer_id = int(i), random_id = \
                             random.randint(-2147483648, 2147483647), message = 'Если в будущем захотите воспользоваться памяткой, жмите на кнопку "Экопамятка"')                                  
         except:
            pass

@bot.on.message(text = 'оценка')
async def helpHandler(message: Message):
   await message.answer(f'Средний балл - {reverseRoomFind(message.from_id)}')

@bot.on.message(text = 'ошибка')
async def helpHandler(message: Message):
   fromId = message.from_id
   await message.answer('Передано представителю студсовета')
   await bot.api.messages.send(peer_id = 282418233, random_id = \
                             random.randint(-2147483648, 2147483647), message = f'Ошибка у \n vk.com/id{fromId}')

@bot.on.message(text = 'код')
async def qrcoder(message: Message):
   ''' Функция для отправки любому члену студсовета QR кода для регистрации на мероприятие '''
   fromId = message.from_id
   if choice(4,fromId) != '':
      NEW_FORM = {
         "info": {
           "title": f"Мероприятие {strftime('%c', localtime())}",
         }
      }

# Request body to add a multiple-choice question
      QUESTION = {
       "requests": [{
        "createItem": {
            "item": {
                "title": "ФИО",
                "questionItem": {
                    "question": 
                        {
                        "required": True,
                        "textQuestion": {
                        }
                    }
                },
            },
            "location": {
                "index": 0
            }
        }
       },
       {
        "createItem": {
            "item": {
                "title": "Номер комнаты",
                "questionItem": {
                    "question": 
                        {
                        "required": True,
                        "textQuestion": {
                        }
                    }
                },
            },
            "location": {
                "index": 0
            }
        }
       }]
      }
      store = file.Storage('token.json')
      creds = None
      if not creds or creds.invalid:
         flow = client.flow_from_clientsecrets('/Users/admin/Desktop/vk_bot/client_secrets.json', SCOPES)
         #flow = client.flow_from_clientsecrets('/home/opc/bot/client_secrets.json', SCOPES) 
         creds = tools.run_flow(flow, store)

      form_service = discovery.build('forms', 'v1', http=creds.authorize(
         Http()), discoveryServiceUrl=DISCOVERY_DOC, static_discovery=False)
      result = form_service.forms().create(body=NEW_FORM).execute()
      question_setting = form_service.forms().batchUpdate(formId=result["formId"], body=QUESTION).execute()
      print(result.get('responderUri'))
      img = make(result.get('responderUri'))  
      path = '/home/opc/bot/qr.png' 
      #path = '/Users/admin/Desktop/qr.png'
      img.save(path) # сменить путь
      # отправляем сообщение с кодом
      tab_upd = DocMessagesUploader(bot.api)
      shed_tab = await tab_upd.upload(title = path, file_source = path, peer_id = message.peer_id)
      await message.answer('Можете проверить его работоспособность.', attachment = shed_tab)

@bot.on.private_message(text = 'дежурство')
async def ExtraDef(message: Message):
   now = Timestamp.now(tz='Europe/Moscow')
   hour = 20
   idents = [] 
   sos_list = ['первый этаж', 'второй этаж', 'третий этаж л',\
              'третий этаж п', 'четвёртый этаж л', 'четвёртый этаж п']
   fromId = message.from_id
   global data, shed 
   data = read_excel('/Users/admin/Desktop/2022-2023/Рейтинг.xlsx')
   shed = read_excel('/Users/admin/Desktop/2022-2023/raw kitch shed.xlsx')

   for floour in sos_list:
            tab = shed[7 + sos_list.index(floour)]
            nichi = Timestamp.now(tz= 'Europe/Moscow').day
            ind = tab[int(nichi)].to_list().index('1')
            heya = tab.loc[ind].to_list()[0]
            try:
              for ids in data[data[2] == str(heya)][3].to_list():
                idents.append(ids)
            except KeyError:
              pass
   newSet = set()
   for j in idents:
         print(j, '!!!', choice(6, j)) # это permission 
         room = choice(2, j) # это комната
         lenSet = len(newSet)
         newSet.add(room)
         if now.hour >= hour and j != '' and int(choice(6, j)) == 1 and now.hour < hour + 2:
        #тут отправка сообщения и сон
            try:
               if len(newSet) != lenSet:
                  await bot.api.messages.send(peer_id = fromId, random_id = \
                  random.randint(-2147483648, 2147483647), message = f'Дежурит {room} комната')
                  await sleep(0.7)                               
            except:
               await sleep(0.3)
               await bot.api.messages.send(peer_id = 282418233, random_id = \
                  random.randint(-2147483648, 2147483647), message = f'чекни {j}')     
  
@bot.on.private_message(payload={'cmd':'eco'})
async def eco_note(message:Message):
   await message.answer(message = 'Какая фракция вас интересует?',keyboard=(Keyboard(one_time=False, inline=False)\
        .add(Text("Пластик", {"cmd": "plast"}), color=KeyboardButtonColor.POSITIVE)\
        .add(Text("Макулатура", {"cmd": "paper"}), color=KeyboardButtonColor.POSITIVE)\
        .add(Text("Металл", {"cmd": "metall"}), color=KeyboardButtonColor.POSITIVE)\
        .add(Text("TetraPack", {"cmd": "tetra"}), color=KeyboardButtonColor.POSITIVE)\
                 
        .add(Text("Стекло", {"cmd": "glass"}), color=KeyboardButtonColor.POSITIVE)).get_json())

@bot.on.private_message(payload={"cmd": "plast"})
async def ecoDealer(message: Message):
   await message.answer('1. Пластик \n \n \
                                      ● Бутылки PET - из-под напитков, молока и масла \n \
                                      ● Бытовая химия - шампуни, гели, крема и тд. \n \
                                      ● Контейнеры - из-под еды (типа плавленного сыра, йогуртов и тд.) \n \
                                    ВАЖНО! Пластик нужно сдавать чистым, без остатков пищи. \n \
                                    Крышечки из-под бутылок сдавать отдельно, этикетки НЕ снимать')

@bot.on.private_message(payload={"cmd": "paper"})
async def ecoDealer(message: Message):
   await message.answer('2. Макулатура \n \n \
                                       ● Бумага - принимаем офисную а4, газеты, тетради, флаеры, журналы глянцевые, крафтовые пакеты \n \
                                       ● Картон - упаковки, обложки тетрадей, картон от посылок, из-под пиццы \n \
                                    Можно сдавать немного жирным, мокрым, грязным, разрисованным, глянцевым')

@bot.on.private_message(payload={"cmd": "metall"})
async def ecoDealer(message: Message):
   await message.answer('3. Металл - из-под консервов, напитков, крышки от стеклянных банок, фольга')   

@bot.on.private_message(payload={"cmd": "tetra"})
async def ecoDealer(message: Message):
   await message.answer('4. TetraPack - принимаем упаковки от соков, молока. Перед тем, как сдать, нужно \n \
                        ОБЯЗАТЕЛЬНО разрезать упаковку по швам, тщательно промыть, снять крышку и крепление для неё')

@bot.on.private_message(payload={"cmd": "glass"})
async def ecoDealer(message: Message):
   await message.answer('5. Стекло - принимаем и цветное, и прозрачное. Бумажную этикетку НЕ НУЖНО снимать')   

@bot.on.private_message(payload={"cmd": "sender"})
async def subs_handler(message: Message):
   fromId = message.from_id
   if type(choice(1, message.from_id)) != bool:
      if type(choice(4,fromId)) != float or type(choice(4,fromId)) == float:
         data.iat[f'G{int(choice(0, int(fromId)))}'] = 1
         data.to_excel('/Users/admin/Desktop/2022-2023/Рейтинг.xlsx')
         await message.answer('Теперь я буду напоминать вам о дежурствах и сообщать о некоторых субботниках,\
         если у вас мало баллов. Чтобы отписаться, напишите "Отписаться", либо напишите "Хай" и нажмите на кнопку "Отписаться"')
   await sleep(1)      

@bot.on.private_message(payload={"cmd": "canceller"})
async def cancel_handler(message: Message):
   fromId = message.from_id
   if type(choice(1, message.from_id)) != bool:
      if type(choice(4,fromId)) != float or type(choice(4,fromId)) == float:
         data.iat[f'G{int(choice(0, int(fromId)))}'] = 0
         data.to_excel('/Users/admin/Desktop/2022-2023/Рейтинг.xlsx')
         await message.answer('Напоминать о дежурствах больше не буду. Если передумаете, напишите "Подписаться"')
   await sleep(1)      

@bot.on.private_message()
async def room_handler(message: Message):
    if message.text.isnumeric():
      try:
         if len(choice(4,message.from_id)) != 0 or message.from_id == 72381975:
            await bot.api.messages.send(peer_id = message.from_id, \
                             random_id = random.randint(-2147483648, 2147483647), \
                             message = roomFind(cleaNum(message.text)))
      except:
         await message.answer('ID некоторых жильцов запрашиваемой комнаты нет в списке!')
    else:
        await message.answer('Пишите "Хай", чтобы список команд увидеть') 
    await sleep(1)             

# every 4 hours checks and do aknowledge to 'starostas' throughout the link
@bot.loop_wrapper.interval(hours = 2)
async def before_my_task():
   now = Timestamp.now(tz='Europe/Moscow')
   hour = 20
   idents = [] 
   sos_list = ['первый этаж', 'второй этаж', 'третий этаж л',\
              'третий этаж п', 'четвёртый этаж л', 'четвёртый этаж п']
   global data, shed 
   data = read_excel('/Users/admin/Desktop/2022-2023/Рейтинг.xlsx')
   shed = read_excel('/Users/admin/Desktop/2022-2023/raw kitch shed.xlsx')

   for floour in sos_list:
            tab = shed[7 + sos_list.index(floour)]
            nichi = Timestamp.now(tz= 'Europe/Moscow').day
            ind = tab[int(nichi)].to_list().index('1')
            heya = tab.loc[ind].to_list()[0]
            try:
              for ids in data[data[2] == str(heya)][3].to_list():
                idents.append(ids)
            except KeyError:
              pass

   for j in idents:
         print(j, '!!!', choice(6, j)) 
         if now.hour >= hour and j != '' and int(choice(6, j)) == 1 and now.hour < hour + 2:
        #тут отправка сообщения и сон
            try:
               await bot.api.messages.send(peer_id = int(j), random_id = \
                  random.randint(-2147483648, 2147483647), message = 'Не забудьте продежурить сегодня!')
               await sleep(0.7)
               await bot.api.messages.send(peer_id = 282418233, random_id = \
                  random.randint(-2147483648, 2147483647), message = j)
               await sleep(0.3)                               
            except:
               await sleep(0.3)
               await bot.api.messages.send(peer_id = 282418233, random_id = \
                  random.randint(-2147483648, 2147483647), message = f'чекни {j}')

   if now.day == now.daysinmonth and now.hour >= hour and now.hour < hour + 2:
      ll = [205405844, 112083106, 332845674, 103954938, 215180035, 220977532]
      #тут надо вручную id старост записать!
      for k in ll:   
         try:
        #тут отправка сообщения и сон
            await sleep(1)
            await bot.api.messages.send(peer_id = int(k), random_id = \
               random.randint(-2147483648, 2147483647), message = '\
      Составьте расписание тут:\
      https://docs.google.com/spreadsheets/d/14qj6wr242d2A-H4z7ntMIRQs0KjeeKXyFshGeTo9w9s/edit#gid=0 .', \
               keyboard=(Keyboard(one_time=True, inline=False)\
        .add(Text("Получить!", {"cmd": "last_gain"}), color=KeyboardButtonColor.POSITIVE)).get_json())
         except:
            pass
   if now.day == now.daysinmonth and now.hour >= (hour + 1) and now.hour < hour + 4:
      await bot.api.messages.send(peer_id = 282418233, random_id = \
         random.randint(-2147483648, 2147483647), message = 'Не забудь табличку для кухонь чекнуть сегодня!')                       

bot.run_forever()
