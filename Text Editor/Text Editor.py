import tkinter as tk
from tkinter import font
from tkinter import ttk
from lib.Menu import Menu
from lib.Finder import Finder
from assets.Constants import *
from time import time


class TextEditor(tk.Frame):
    def __init__(self,parent):
        """this function initializes the text editor widget"""
        tk.Frame.__init__(self, parent)
        #adding the text widget with its verticall scrollbar
        self.text = tk.Text(self, wrap="char")
        self.scroll = tk.Scrollbar(self, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=self.scroll.set)
        self.scroll.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)
        self.text.bind('<KeyRelease>',lambda e : self.keyPressed(e))
        #initialize elements
        self.initializeElements()
        #add the menu and initialize file saving related variables 
        self.menu=Menu(parent,self)
        parent.config(menu=self.menu)
        #initialize configuration variables
        self.autoGuess=False
        self.programming=False
        #initialize a finder which is going to search for completions when autoGuess mode is on
        self.finder=Finder()
        
    def initializeElements(self):
        """this function is used to initialize elements such as font, color, usefull lists etc ..."""
        #initializing text related attributs(font, foreground color ...)
        self.font=DEFAULT_FONT
        self.color=DEFAULT_COLOR
        self.text.config(font=self.font, fg=self.color)
        self.lastWord=''
        self.currentWord=''
        self.lastIsSaved=True #this variable is used to check if the latest state of the document has been saved (((it's set to true once the user saves a copy and turned to false at any key press)))
        self.pathOfSavedVersion=None #this variable holds the path of the file if it's saved at least once in order to save automatically
        #initialize the label to be placed near the cursor every time we start typing something
        self.labels=tk.Label(self.text)
        self.labelsList=list() #it contains a maximum of four sub_labels to show proposed words each time a char key is pressed 
        self.labelCounter=-1  #label counter is used to know which proposed word to highlight when the user presses on teh right arrow key
        #initialize the list of all tags added because of the find method in the menu
        self.findMethodTag=None
        
    def keyPressed(self,event):
        """this function deals with keyPresses in the text widget"""
        #when a key is pressed we first change the state of the file to not saved
        self.lastIsSaved=False
        #we remove tag added from find method
        if(not(self.findMethodTag==None)):
           self.text.tag_delete(self.findMethodTag)
           self.findMethodTag=None
        
        if(self.autoGuess):
            #then we check which key was pressed to figure out what to do 
            if(event.char == ' '): #the space bar is pressed
                self.spacePressed(event)
            elif event.keysym_num > 0 and event.keysym_num < 60000: # a printable key is pressed
                #we destroy labels of proposed words and we re-initialize self.labelsList and we hide the label of potential words' completion
                self.labelsList=list()
                for label in self.labels.pack_slaves():
                    label.destroy()
                self.labels.place_forget()
                #average time needed to execute this function is 120ms ~ almost the time needed to execute the finder.startsWith method 
                self.charPressed(event)
            elif event.keysym_num == 65363: #the right arrow key is pressed
                self.rightArrowPressed(event)
            else:
                #we destroy labels of proposed words and we re-initialize self.labelsList and we hide the label of potential words' completion
                self.labelsList=list()
                for label in self.labels.pack_slaves():
                    label.destroy()
                self.labels.place_forget()
                self.labelCounter=-1
        else:
            pass
            
    def spacePressed(self,event):
        """this function stores the last word after a whitespace so that could be used later using the bi-gram frequency document or put a proposed word chosen by the user"""
        if(self.autoGuess):
            if(self.labelCounter != -1):#if the label counter is different from -1 meaning that the user has chosen a word to put automatically so we replace the letters typed by the user
                self.labelsList[self.labelCounter].config(background='SystemButtonFace')#we remove the highlighting
                word_to_remove=self.text.get("1.0",'end-2c').replace('\n',' ').rsplit(' ', 1)[-1].strip()#we extart the typed letters
                self.text.delete("end-"+str(len(word_to_remove)+2)+"c","end")#we delete them
                self.text.insert("end",self.labelsList[self.labelCounter]["text"]+" ")#we insert the chosen word with a white space
                self.labelCounter=-1
            #we destroy labels of proposed words and we re-initialize self.labelsList and we hide the label of potential words' completion
            self.labelsList=list()
            for label in self.labels.pack_slaves():
                label.destroy()
            self.labels.place_forget()
            #we update the last and current word 
            self.lastWord = self.text.get("1.0",'end-2c').replace('\n',' ').rsplit(' ', 1)[-1].strip()
            self.currentWord=''
        else:
            pass

    def charPressed(self,event):
        """this function deals with chars being pressed to show for the user possible words if the auto guess mode is enabled"""
        if(self.autoGuess):
            self.labelCounter=-1
            self.currentWord=self.text.get("1.0",'end-1c').rsplit(' ', 1)[-1].strip()#we update current word in fact current word is the letters typed by the user
            _font=font.Font(family=self.font[0], size=self.font[1])#we define a tk.Font tool to use it later to determine the height and width of the text in pixels to know where to place the label of potential words' completion 
            _defaultFont=font.Font(family=DEFAULT_FONT[0], size=DEFAULT_FONT[1])#this the same tk.Font tool for DEFAULT_FONT (go to Constants.py in the assets folder)
            height=_font.metrics("linespace")#determine the height of a row in a text which will be used as a height unit later 
            default_height=_defaultFont.metrics("linespace")#determine the height of a proposed word 
            heightUnit=height
            cursorPosition=self.text.index("insert").split('.')#determine the position of the typing cursor in the text
            #calculating height and width (initial calculations)
            for i in range(1,int(cursorPosition[0])):
                height +=((_font.measure(self.text.get(str(i)+".0",str(i+1)+".0"))//680)+1)*heightUnit
            height +=_font.measure(self.text.get(cursorPosition[0]+".0","end-1c"))//680*heightUnit
            width=(_font.measure(self.text.get(cursorPosition[0]+".0","end-1c"))%680)+5 #the +5 is for better visual aspect nothing more
            
            possibleWords=self.finder.startsWith(self.currentWord)
            propositionMaxWidth=0
            numberOfShowenLabels=0
            for i in range(4):                                       
                try:
                    if(_defaultFont.measure(possibleWords[i])>propositionMaxWidth):
                        propositionMaxWidth=_defaultFont.measure(possibleWords[i])
                    self.labelsList.append(tk.Label(self.labels, font=DEFAULT_FONT, text=possibleWords[i],background='SystemButtonFace'))
                    numberOfShowenLabels+=1
                    self.labelsList[numberOfShowenLabels-1].pack()
                except:
                    pass
            #we update the height and width so that the label of potential words' completion doesn't exceed the text widget
            width=min(width,WINDOW_WIDTH-25-propositionMaxWidth)
            height=min(height,WINDOW_HEIGHT-25-default_height*numberOfShowenLabels)
            self.labels.place(x=width, y=height)
        else:
            pass

    def rightArrowPressed(self,event):
        """this function gives the user the possibility to choose a word that was proposed to him so that he types faster"""
        if(self.autoGuess):
            if(len(self.labelsList) != 0):
                self.labelCounter = (self.labelCounter+1)%len(self.labelsList)
                self.labelsList[self.labelCounter].config(bg="light blue")
                for i in range(len(self.labelsList)):
                    if(i!=self.labelCounter):
                        self.labelsList[i].config(background='SystemButtonFace')
        else:
            pass
            
            

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry(str(WINDOW_WIDTH)+"x"+str(WINDOW_HEIGHT)+"+0+0")
    root.resizable(width=False, height=False)
    TextEditor(root).pack(side="top", fill="both", expand=True)
    root.mainloop()
