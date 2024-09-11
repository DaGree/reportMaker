import csv
import telebot
from telebot import types
from datetime import date, timedelta
import os
from dotenv import load_dotenv

load_dotenv(".env")

TOKEN = os.getenv("TOKEN")
SRC_R = os.getenv("SRC_R")
SRC_F = os.getenv("SRC_F")
LINKNAME = os.getenv("LINKNAME")
INSTRUCTION = os.getenv("INSTRUCTION")

today = date.today()
monday = today - timedelta(days=today.weekday())
REPORT=str(monday.strftime("%d.%m.%y"))+"-"+str((monday + timedelta(days=4)).strftime("%d.%m.%y"))
PLAN=str((monday + timedelta(days=7)).strftime("%d.%m.%y"))+"-"+str((monday + timedelta(days=11)).strftime("%d.%m.%y"))
# print(REPORT+" "+PLAN)

print("Бот запущен")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start_message(message):
  bot.send_message(message.chat.id,"Перед началом работы ознакомься с инструкцией (/instruction)"+"\n\n"+"Отчет будет составляться для текущей рабочей недели, которая соответсвует датам: "+REPORT)
  
@bot.message_handler(commands=['instruction'])
def start_message(message):
  bot.send_message(message.chat.id,"Инструкция:"+"\n"+INSTRUCTION)
  
  
@bot.message_handler(func=lambda message: True, content_types=['audio', 'photo', 'voice', 'video','text', 'location', 'contact', 'sticker']) #обработчик других типов сообщений
def default_command(message):
    bot.send_message(message.chat.id, "Это не то что я ожидал увидеть, следуй инструкции")

@bot.message_handler(content_types=['document']) #обработчик получения сообщения с файлом
def handle_document(message):
  file_info = bot.get_file(message.document.file_id)
  downloaded_file = bot.download_file(file_info.file_path) #присутпаем к обработке файла
  
  if ('.csv' in str(message.document.file_name)) and (message.document.file_size<20000):  #проверяем тип файла и размер
    print ("The file is CSV. The file size is>")
    print (message.document.file_size)
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
        bot.send_message(message.chat.id, f"Документ с недопустимыми значнеиями, повтори шаги по инструкции")
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
    
  else:
    print ("The file is NOT CSV")  
    bot.send_message(message.chat.id, f"Некорректный формат документа и/или превышен размер файла. Направь файл с типом CSV и весом не более 20Кбайт")
    
if __name__ == '__main__':
    bot.polling(non_stop=True)