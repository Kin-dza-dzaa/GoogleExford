from googletrans import Translator
import requests
import csv
import time

language = "en-us"

# Считывание счетчика
with open('Counter.txt', mode='r', encoding='utf-8') as f:
    counter = f.readlines()
    counter = int(counter[-1].strip())

# Запоминание новых слов через сет, чтобы исключить повторения
with open("New eng words.txt", "r", encoding='utf-8') as f:
    words = set()
    for i in f:
        if i != "\n":
            words.add(i.strip().lower())

# Старые слова в множестве
with open("Words which i'm learning eng.txt", "r", encoding='utf-8') as f:
    old_words = set()
    for i in f:
        if i != "\n":
            old_words.add(i.strip().lower())

# СЛОВА КОТОРЫЕ УХОДЯТ НА ПЕРЕВОД
words -= old_words
print(words)


for word in words:
    """
    Гугл часть, тут огромный словарь который парситься, а переводы и определения раскидываются в словари в которых часть речи это ключ
    """
    translator = Translator(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36" )
    definitions = {}
    all_translations = {}
    verbs_form = [] # Формы глаголов
    phrasal_verbs = [] # Фразовые глаголы
    final_string = "" # Финальная строка
    translations_google = translator.translate(word, dest='ru', src="en")
    try:
        for q in translations_google.extra_data["parsed"][3][1][0]: # Definitions
            key = q[0] # Part of speech
            value = []
            for j in q[1]:
                try:
                    value.append(f"Def: {j[0]},<br>Example: {j[1]}<br>")
                except IndexError:
                    value.append(f"Def: {j[0]},<br>Example: None<br>")
            definitions[key] = value
    except (TypeError, IndexError) as e:
        print(word, f"Error: {e}")
    try:
        for w in translations_google.extra_data["parsed"][3][5][0]:
            key = w[0] # Part of speech
            value = []
            for j in w[1]:
                value.append(j[0])
            all_translations[key] = value
    except (TypeError, IndexError) as e:
        print(word, f"Error: {e}")
    """
    Oxford api часть выдергиваем фразовые глаголы если есть и формы глаголов если есть:
    """
    url = "https://od-api.oxforddictionaries.com:443/api/v2/entries/" + language + "/" + word
    r = requests.get(url, headers={"app_id": 'Put here your app_id', "app_key": 'Put here your app_key'}).json()
    if 'error' not in r:
        for index, i in enumerate(r['results'][0]['lexicalEntries']):
            part_of_speech = i["lexicalCategory"]["id"] # Часть речи
            if part_of_speech == 'verb':
                try:
                    for c in r['results'][0]['lexicalEntries'][index]['entries'][0]['inflections']:  # Формы слова, если их нет то дальше
                        verbs_form.append(c['inflectedForm'])
                except KeyError:
                    pass
                try:
                    for c1 in r['results'][0]['lexicalEntries'][index]['phrasalVerbs']:  # Фразовые глаголы, если их нет то дальше
                        phrasal_verbs.append(c1['text'])
                except KeyError:
                    pass
    # Тут начинается запись, но для начала формируется final_string
    if len(verbs_form) != 0:
        final_string += "verbs forms: "
        for v in verbs_form:
            final_string += v + " "
        final_string += "<br>"
    if len(phrasal_verbs) != 0:
        final_string += "phrasal verbs: "
        for v in phrasal_verbs:
            final_string += v + ", "
        final_string += "<br>"
    final_string += f"Главный перевод: {translations_google.text}<br>"
    for k, v in all_translations.items():
        final_string += f'Часть речи: <font color="#0000ff">{k}</font><br>'
        for i in v:
            final_string += i + '<br>'
    for k, v in definitions.items():
        final_string += f'Часть речи: <font color="#0000ff">{k}</font><br>'
        for i in v:
            final_string += i
    final_string = '<p align="left">' + final_string + '</p>' # Для ореинтации по левому краю
    with open('Counter.txt', mode='w', encoding='utf-8') as count, open('Eng anki.csv', mode='a', encoding='utf-8') as anki, \
            open("Words which i'm learning eng.txt", mode='a', encoding='utf-8') as learning_words:
        file_writer = csv.writer(anki, delimiter=",")
        file_writer.writerow([word + ", слово номер: " + str(counter), final_string])
        print(str(counter), word)
        counter += 1
        count.write(str(counter))
        learning_words.write(word + "\n")
        if counter % 10 == 0: # Спим 3.5 сек каждые 10 слов
            time.sleep(3.5)
