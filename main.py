from gpt2 import GPT2
from bert_ner import NER
from bert_question_answering import QA
import re
from tkinter import *
from tkinter import font
import json
import os


file_path = "./diary.json"
isWriting = False
slots = []

def show_frame(frame):
    frame.tkraise()

def openDiary(data):
    bold_font = font.Font(weight="bold")

    date = Label(diaryFrame, wraplength=500, text=data['date'])
    date.pack()

    tagsText = Label(diaryFrame, wraplength=500, text="tags", font=bold_font)
    tagsText.pack()
    txt = ""
    for i in data['tags']:
        txt += ", "+i
    tags = Label(diaryFrame, wraplength=500, text=txt)
    tags.pack()

    diaryText = Label(diaryFrame, wraplength=500, text="diary", font=bold_font)
    diaryText.pack()
    diary = Label(diaryFrame, wraplength=500, text=data['diary'])
    diary.pack()

    replyText = Label(diaryFrame, wraplength=500, text="AI's reply", font=bold_font)
    replyText.pack()
    reply = Label(diaryFrame, wraplength=500, text=data['reply'])
    reply.pack()

    goReadingDiaryButton = Button(diaryFrame, text='go back', command=openReadingDiary)
    goReadingDiaryButton.pack(padx=10,pady=10)

    show_frame(diaryFrame)

def openReadingDiary():
    for slot in slots:
        slot.destroy()

    with open(file_path, 'r') as f:
        json_data = json.load(f)

    for data in json_data["data"]:
        btn = Button(scrollFrame, text=data["date"], command=lambda : openDiary(data))
        btn.pack(pady=5)
        slots.append(btn)

    show_frame(diaryReadingFrame)

def openWritingDiary():
    dateEntry.delete(0, END)
    entry.delete(0, END)
    show_frame(diaryWritingFrame)

def openMain():
    show_frame(mainFrame)

def writeDiary():
    global isWriting
    if not isWriting:
        with open(file_path, 'r') as f:
            json_data = json.load(f)

        date = dateEntry.get()

        isWriting = True
        input_text = entry.get()
        input_text = re.sub(r'\n+', '\n', input_text)

        ner_result = ner.generate(input_text)
        tags = ner_result

        questions = [
            "what is the most important part of this paragraph?",
            "what is the topic of the paragraph?"
        ]

        def get_small_tag(input_text, depth):
            qa = QA(input_text.split('\n'))
            res = []
            for question in questions:
                qa_results = qa.generate(question)
                for qa_result in qa_results:
                    if len(qa_result.split(" ")) > 6:
                        if depth < 5:
                            res += get_small_tag(qa_result, depth+1)
                    else:
                        res.append(qa_result)
            return res

        tags += get_small_tag(input_text, 0)
        tags = list(set(tags))

        gpt_result = gpt2.generate(input_text)
        newData = {
            "diary": input_text,
            "tags": tags,
            "reply": gpt_result,
            "date": date
        }
        json_data["data"].append(newData)

        with open(file_path, 'w') as f : 
            json.dump(json_data, f, indent=4)

        openMain()

        isWriting = False


if __name__ == "__main__":
    if not os.path.isfile(file_path):
        print("no file")
        data = {"data": []}
        with open(file_path, 'w') as f : 
            json.dump(data, f, indent=4)

    gpt2 = GPT2()
    ner = NER()

    tk = Tk() 
    tk.title("diary app")
    tk.geometry("540x360")

    mainFrame = Frame(tk)

    readButton = Button(mainFrame, text='read diary', command=openReadingDiary)
    writeButton = Button(mainFrame, text='write diary', command=openWritingDiary)
    readButton.pack(padx=10, pady= 10)
    writeButton.pack(padx=10,pady=10)

    diaryWritingFrame = Frame(tk)

    label1 = Label(diaryWritingFrame, text="Enter date:")
    label1.pack()
    dateEntry = Entry(diaryWritingFrame, width=50)
    dateEntry.pack()
    
    label2 = Label(diaryWritingFrame, text="Enter text:")
    label2.pack()
    entry = Entry(diaryWritingFrame, width=50)
    entry.pack()

    confirmButton = Button(diaryWritingFrame, text='confirm', command=writeDiary)
    cancelButton = Button(diaryWritingFrame, text='cancel', command=openMain)
    confirmButton.pack(padx=10,pady=10)
    cancelButton.pack(padx=10, pady= 10)

    diaryReadingFrame = Frame(tk)

    goBackButton = Button(diaryReadingFrame, text='go back', command=openMain)
    goBackButton.pack(side=RIGHT,padx=10,pady=10)

    def on_configure(event):
        canvas.configure(scrollregion=canvas.bbox('all'))

    scrollbar = Scrollbar(diaryReadingFrame)
    scrollbar.pack(side=RIGHT,fill=Y)

    canvas = Canvas(diaryReadingFrame, yscrollcommand=scrollbar.set)
    canvas.pack(side=LEFT, fill=BOTH, expand=True)

    scrollbar.config(command=canvas.yview)

    scrollFrame = Frame(canvas)
    canvas.create_window((0, 0), window=scrollFrame, anchor='nw')

    scrollFrame.bind('<Configure>', on_configure)

    diaryFrame = Frame(tk)

    mainFrame.grid(row=0, column=0, sticky="nsew")
    diaryWritingFrame.grid(row=0, column=0, sticky="nsew")
    diaryReadingFrame.grid(row=0, column=0, sticky="nsew")
    diaryFrame.grid(row=0, column=0, sticky="nsew")

    show_frame(mainFrame)
    tk.mainloop()