import tkinter as tk
from tkinter import filedialog as fd
from tkinter import simpledialog as sd
import tkinter.messagebox as mb
import re
from pynput.keyboard import Key, Controller
import sys
sys.path.insert(0,'C:/Users/Asus/Desktop/GitHub Projects/projets terminés/Text Editor/assets')#put here the directory of the assets folder
from Constants import *


class Menu(tk.Menu):
    def __init__(self,parent,controller):
        """this function creates the menu for the text editor"""
        #create a main menu
        tk.Menu.__init__(self,parent)
        #store the text widget in a variable to access the frame attributs for future modifications
        self.textWidget=controller
        #initialise a keyboard controller to handle (undo, redo, cut, paste, copy ...)
        self.keyboard=Controller()
        #add the file sub-menu
        self.filemenu=tk.Menu(self, tearoff=0)
        self.filemenu.add_command(label="New File", command=lambda: self.newFile())
        self.filemenu.add_command(label="Open...", command=lambda: self.openFile())
        self.filemenu.add_separator()
        self.filemenu.add_command(label = "Save", command=lambda: self.saveFile())
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command =lambda:parent.destroy())
        self.add_cascade(label="File", menu=self.filemenu)
        #add the Edit sub-menu
        self.editmenu=tk.Menu(self, tearoff=0)
        self.editmenu.add_command(label="Undo", command=lambda: self.undo())
        self.editmenu.add_command(label="Redo", command=lambda: self.redo())
        self.editmenu.add_separator()
        self.editmenu.add_command(label="Cut", command=lambda: self.cut())
        self.editmenu.add_command(label="Copy", command=lambda: self.copy())
        self.editmenu.add_command(label="Paste", command=lambda: self.paste())
        self.editmenu.add_separator()
        self.editmenu.add_command(label="Find", command=lambda: self.find())
        self.add_cascade(label="Edit", menu=self.editmenu)
        #add the configuration sub-menu
        self.configmenu=tk.Menu(self, tearoff=0)
        self.autoGuess=tk.StringVar()
        self.configmenu.add_checkbutton(label="Enable Guessing Mode", variable=self.autoGuess,onvalue="Enabled",offvalue="Disabled",command=lambda:self.config_autoGuess())
        self.programming=tk.StringVar()
        self.configmenu.add_checkbutton(label="Enable Programming Mode", variable=self.programming,onvalue="Enabled",offvalue="Disabled",command=lambda:self.config_programming())
        self.add_cascade(label="Configuration", menu=self.configmenu)
        #add the graphics sub-menu
        self.graphicmenu=tk.Menu(self, tearoff=0)
        ###adding colors' choice (black, red, blue, green ...)
        colors=tk.Menu(self.graphicmenu,tearoff=0)
        self.color=tk.StringVar()
        for element in COLORS:
            colors.add_radiobutton(label=element.upper(), background=element.lower(), foreground="white", variable=self.color, value=element, command=lambda:self.color_choice())
        self.graphicmenu.add_cascade(label="Color",menu=colors)
        ###adding fonts' choice (Arial, comic sans ms, verdana ...)
        fonts=tk.Menu(self.graphicmenu, tearoff=0)
        self.font=tk.StringVar()
        for element in FONTS:
            fonts.add_radiobutton(label=element, variable=self.font, value=element, command=lambda:self.font_choice())
        self.graphicmenu.add_cascade(label="Font",menu=fonts)
        ###adding fontSizes' choice (Small, medium, Large)
        fontSizes=tk.Menu(self.graphicmenu, tearoff=0)
        self.fontSize=tk.StringVar()
        for element in list(FONT_SIZES.keys()):
            fontSizes.add_radiobutton(label=element.upper(), variable=self.fontSize, value=FONT_SIZES[element], command=lambda:self.fontSize_choice())
        self.graphicmenu.add_cascade(label="Font Size",menu=fontSizes)
        ###adding fontStyles' choice ( Bold, Italian)
        fontStyles=tk.Menu(self.graphicmenu, tearoff=0)
        self.bold=tk.StringVar()
        fontStyles.add_checkbutton(label="BOLD", variable=self.bold,onvalue="Enabled",offvalue="Disabled",command=lambda:self.Bold())
        self.italian=tk.StringVar()
        fontStyles.add_checkbutton(label="ITALIC", variable=self.italian,onvalue="Enabled",offvalue="Disabled",command=lambda:self.Italic())
        self.graphicmenu.add_cascade(label="Font Styles", menu=fontStyles)
        self.add_cascade(label="Graphics", menu=self.graphicmenu)
        #add the help sub-menu
        self.helpmenu = tk.Menu(self, tearoff=0)
        message = "This is an editor made by Maher OUALI"
        self.helpmenu.add_command(label="About", command = lambda: mb.showinfo("About!",message))
        self.add_cascade(label="Help", menu=self.helpmenu)
    
    def newFile(self): #finished
        """this function generates a new file"""
        if(not(self.textWidget.lastIsSaved)):
            #here before saving launch a dialog file to see if the user want to save the file or not 
            self.saveFile()
        #here we have to destroy the first frame and launch a second one
        self.textWidget.pathOfSavedVersion=None
        self.textWidget.lastIsSaved=True
        self.textWidget.text.delete("1.0","end")
        self.textWidget.initializeElements()
        
    
    def openFile(self): #finished
        """this function opens an existing file chosen by the user"""
        if(not(self.textWidget.lastIsSaved)):
            #here before saving launch a dialog file to see if the user want to save the file or not
            answer = mb.askokcancel("Save or not","Do you want to save this file?")
            if answer:
                self.saveFile()
        #here we have to destroy the first frame and launch a second one
        file = fd.askopenfile()
        if file is None: # asksaveasfile return `None` if dialog closed with "cancel".
            return
        self.textWidget.pathOfSavedVersion=file.name
        self.textWidget.lastIsSaved=True
        text2open=file.read()
        file.close()
        self.textWidget.text.delete("1.0","end")
        self.textWidget.text.insert("end",text2open)
        self.textWidget.text.config(font=DEFAULT_FONT, fg=DEFAULT_COLOR)
        self.textWidget.font=DEFAULT_FONT
        self.textWidget.color=DEFAULT_COLOR
        
    
    def saveFile(self): #finished
        """this function saves the file edited by the user"""
        if(not(self.textWidget.lastIsSaved)):
            if(self.textWidget.pathOfSavedVersion == None):
                #here launch a file dialog to choose a path and then save it there and update both self.pathOfSavedVersion and self.lastIsSaved
                file = fd.asksaveasfile(mode='w', defaultextension=".txt")
                if file is None: # asksaveasfile return `None` if dialog closed with "cancel".
                    return
                self.textWidget.pathOfSavedVersion=file.name
                self.textWidget.lastIsSaved=True
                text2save = str(self.textWidget.text.get("1.0", "end")) # starts from `1.0`, not `0.0`
                file.write(text2save)
                file.close()	
            else:
                try:
                    file=open(self.textWidget.pathOfSavedVersion,mode='w')
                    text2save = str(self.textWidget.text.get("1.0", "end")) # starts from `1.0`, not `0.0`
                    file.write(text2save)
                    file.close()
                except:
                    mb.showinfo("Error!!","Original file not found")
                    self.textWidget.pathOfSavedVersion = None
                    self.saveFile()
        else:
            return
    
    def undo(self): #finished
        """this function mimic the undo of the text widget"""
        self.keyboard.press(Key.ctrl)
        self.keyboard.press("z")
        self.keyboard.release(Key.ctrl)
        self.keyboard.release("z")
        
    def redo(self): #finished
        """this function mimic the redo of the text widget"""
        self.keyboard.press(Key.ctrl)
        self.keyboard.press("y")
        self.keyboard.release(Key.ctrl)
        self.keyboard.release("y")
     
    def cut(self): #finished
        """this function mimic the cut of the text widget"""
        self.keyboard.press(Key.ctrl)
        self.keyboard.press("x")
        self.keyboard.release(Key.ctrl)
        self.keyboard.release("x")
    
    def copy(self): #finished
        """this function mimic the copy of the text widget"""
        self.keyboard.press(Key.ctrl)
        self.keyboard.press("c")
        self.keyboard.release(Key.ctrl)
        self.keyboard.release("c")
    
    def paste(self): #finished
        """this function mimic the paste of the text widget"""
        self.keyboard.press(Key.ctrl)
        self.keyboard.press("v")
        self.keyboard.release(Key.ctrl)
        self.keyboard.release("v")

    def find(self): #finished
        """this function gives the user the posibility of finding a word in the text widget"""
        #here we simply launch a dialog for the user to type the word that he wants to look for and then we highlight it in all possible positions in the text widget
        if(not(self.textWidget.findMethodTag==None)):
           self.textWidget.text.tag_delete(self.textWidget.findMethodTag)
        word=sd.askstring("Search", "What do you want to search for?")
        if word is not None:
            #we look for the word in the text file and we highlight all occurennces
            self.textWidget.findMethodTag=word
            text=self.textWidget.text.get("1.0","end")
            listOfOccurrence=[(m.start(),m.end()) for m in re.finditer(word, text)]
            for element in listOfOccurrence:
                self.textWidget.text.tag_add(word,"1.0+"+str(element[0])+"c","1.0+"+str(element[1])+"c")   
            self.textWidget.text.tag_config(word,background=TAGS_COLORS[self.textWidget.color])
        else:
            return

    def config_autoGuess(self): #finished
        if(self.autoGuess.get() == "Enabled"):
            self.textWidget.autoGuess=True
        else:
            self.textWidget.autoGuess=False

    def config_programming(self): #finished
        if(self.programming.get() == "Enabled"):
            self.textWidget.programming=True
        else:
            self.textWidget.programming=False

    def color_choice(self): #finished
        self.textWidget.color=self.color.get()
        self.textWidget.text.config(fg=self.textWidget.color)

    def font_choice(self): #finished
        temp_list=list(self.textWidget.font)
        temp_list[0]=self.font.get()
        self.textWidget.font=tuple(temp_list)
        self.textWidget.text.config(font=self.textWidget.font)

    def fontSize_choice(self): #finished
        temp_list=list(self.textWidget.font)
        temp_list[1]=int(self.fontSize.get())
        self.textWidget.font=tuple(temp_list)
        self.textWidget.text.config(font=self.textWidget.font)
    
    def Bold(self): #finished
        temp_list=list(self.textWidget.font)
        if(self.bold.get() == "Enabled"):
            if(len(temp_list)==2):
                temp_list.append("bold")
            else:
                if(not("bold" in temp_list[2])):
                    temp_list[2] += " bold"
        else:
            if(len(temp_list)==3):
                if("bold" in temp_list[2]):
                    temp_list[2] = temp_list[2].replace("bold","")
        self.textWidget.font=tuple(temp_list)
        self.textWidget.text.config(font=self.textWidget.font)
        
    def Italic(self): #finished
        temp_list=list(self.textWidget.font)
        if(self.italian.get() == "Enabled"):
            if(len(temp_list)==2):
                temp_list.append("italic")
            else:
                if(not("italic" in temp_list[2])):
                    temp_list[2] += " italic"
        else:
            if(len(temp_list)==3):
                if("italic" in temp_list[2]):
                    temp_list[2] = temp_list[2].replace("italic","")
        self.textWidget.font=tuple(temp_list)
        self.textWidget.text.config(font=self.textWidget.font)
    

    
