import csv
import telebot
from telebot import types
from datetime import date, timedelta, datetime
import os
from dotenv import load_dotenv

load_dotenv(".env")

TOKEN = os.getenv("TOKEN")
SRC_R = os.getenv("SRC_R")
SRC_F = os.getenv("SRC_F")
LINKNAME = os.getenv("LINKNAME")
INSTRUCTION = os.getenv("INSTRUCTION")
ID_ADMIN=os.getenv("ID_ADMIN")

today = date.today()
print(str(datetime.now().strftime("%H:%M:%S")))
monday = today - timedelta(days=today.weekday())
REPORT=str(monday.strftime("%d.%m.%y"))+"-"+str((monday + timedelta(days=4)).strftime("%d.%m.%y"))
PLAN=str((monday + timedelta(days=7)).strftime("%d.%m.%y"))+"-"+str((monday + timedelta(days=11)).strftime("%d.%m.%y"))

def logtime():
  now=str(datetime.now().strftime("%H:%M:%S"))
  return now

print("Бот запущен")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start_message(message):
  markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
  btn1=types.KeyboardButton("Инструкция")
  btn2=types.KeyboardButton("Текущая неделя")
  markup.add(btn1, btn2)
  bot.send_message(message.chat.id,"Перед началом работы ознакомься с инструкцией"+"\n\n"+"Отчет будет составляться для текущей рабочей недели, которая соответсвует датам: "+REPORT, reply_markup=markup)
  
@bot.message_handler(content_types=['text'])
def func(message):
  if(message.text == "Инструкция"):
    bot.send_message(message.chat.id,"Инструкция:"+"\n"+INSTRUCTION)
  elif(message.text == "Текущая неделя"):
    bot.send_message(message.chat.id,"Текущая неделя: "+REPORT)
  
@bot.message_handler(func=lambda message: True, content_types=['audio', 'photo', 'voice', 'video','text', 'location', 'contact', 'sticker']) #обработчик других типов сообщений
def default_command(message):
    bot.send_message(message.chat.id, "Это не то что я ожидал увидеть, следуй инструкции")

@bot.message_handler(content_types=['document']) #обработчик получения сообщения с файлом
def handle_document(message):
  file_info = bot.get_file(message.document.file_id)
  downloaded_file = bot.download_file(file_info.file_path) #присутпаем к обработке файла
  
  if ('.csv' in str(message.document.file_name)) and (message.document.file_size<50000):  #проверяем тип файла и размер
    print (logtime()+"\nThe file from user "+str(message.chat.id)+" is CSV.\nThe file size is "+str(message.document.file_size)+" bytes"+"\n#log")
    bot.send_message(ID_ADMIN,logtime()+"\nThe file from user "+str(message.chat.id)+" is CSV.\nThe file size is "+str(message.document.file_size)+" bytes"+"\n#log")
    FILENAME = str(message.chat.id)+"_"+message.document.file_name #сохраняем файл с ИД чата 
    src = SRC_R + FILENAME
    with open(src, 'wb') as new_file:
      new_file.write(downloaded_file) #сохранили файл
    bot.send_message(message.chat.id, f"Принял документ, попробую обработать")
    results = []
    newOrder = []
    count = 1
    with open(src, encoding="utf-8") as File:
      try:
        reader = csv.reader(File, delimiter=';')
        for row in reader:
            results.append(row[3])
      except:
        print("Некорректный файл")
        bot.send_message(message.chat.id, f"Документ с недопустимыми значениями, повтори шаги по инструкции")
        bot.send_message(ID_ADMIN,logtime()+"\nThe file size is unreadable"+"\n#log")
        File.close()
        os.remove(src)
        return        
    for row in results:
      newRow=str(row)
      newOrder.append(newRow[newRow.find(':')+2:len(newRow)]+"\n"+LINKNAME+newRow[newRow.find('#')+1:newRow.find('#')+7])
    newOrder.pop(0)
    uniqOrder=set(newOrder)
    newOrder=list(uniqOrder)
    file_path = SRC_F+"newOrder_ID" + str(message.chat.id) + ".txt"
    with open(file_path, 'w', encoding="utf-8") as file:
      file.write("Отчет "+REPORT+'\n\n')
      for item in newOrder:
        file.write(str(count)+") "+item+'\n')
        count+=1
      file.write('\n'+"План "+PLAN+'\n')     
    with open(file_path, 'r', encoding="utf-8") as file:
      data = file.read()
      bot.send_message(message.chat.id, data)
      bot.send_message(ID_ADMIN,logtime()+"\nReport was forwarded"+"\n#log")
    
  else:
    print (logtime()+" The file from "+str(message.chat.id)+" is NOT CSV")
    bot.send_message(ID_ADMIN,logtime()+"\nThe file from user "+str(message.chat.id)+" is not CSV or file is too big"+"\n#log")  
    bot.send_message(message.chat.id, f"Некорректный формат документа и/или превышен размер файла. Направь файл с типом CSV и весом не более 50Кбайт")
    
if __name__ == '__main__':
    bot.polling(non_stop=True)