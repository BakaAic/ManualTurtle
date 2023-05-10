import turtle
from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog,messagebox
import math
import os
from PIL import Image,ImageDraw,ImageTk
import threading

class TurtleRecord():
    def __init__(self,turtle):
        self.turtle=turtle
        self.operationBuffer=[]
        self.operation=[]
    def addOperation(self,operation):
        self.operationBuffer.append(operation)
    def fillOperation(self):
        if len(self.operationBuffer)!=0:
            self.operation.append(tuple(self.operationBuffer))
            self.operationBuffer.clear()
    def addHeader(self):
        self.addOperation('import turtle')
        self.addOperation('turtle.setup(width=500,height=500)')
        self.addOperation('turtle.title("Painting")')
        self.addOperation('turtle.speed(0)')
        self.fillOperation()
    def addTail(self):
        self.addOperation('turtle.hideturtle()')
        self.addOperation('turtle.done()')
        self.fillOperation()
    #=====================以下为turtle操作映射=====================#
    def setup(self,*args):
        _arg=','.join([str(i) for i in args])
        self.addOperation('turtle.setup('+_arg+')')
        self.turtle.setup(*args)
    def bgcolor(self,*args):
        _arg=','.join([str(i) for i in args])
        self.addOperation('turtle.bgcolor("'+_arg+'")')
        self.turtle.bgcolor(*args)
    def pencolor(self,*args):
        _arg=','.join([str(i) for i in args])
        self.addOperation('turtle.pencolor("'+_arg+'")')
        self.turtle.pencolor(*args)
    def pensize(self,*args):    
        _arg=','.join([str(i) for i in args])
        self.addOperation('turtle.pensize('+_arg+')')
        self.turtle.pensize(*args)
    def speed(self,*args):
        _arg=','.join([str(i) for i in args])
        self.addOperation('turtle.speed('+_arg+')')
        self.turtle.speed(*args)
    def pendown(self):
        self.addOperation('turtle.pendown()')
        self.turtle.pendown()
    def penup(self):
        self.addOperation('turtle.penup()')
        self.turtle.penup()
    def goto(self,*args):
        _arg=','.join([str(i) for i in args])
        self.addOperation('turtle.goto('+_arg+')')
        self.turtle.goto(*args)
    def fillcolor(self,*args):
        _arg=','.join([str(i) for i in args])
        self.addOperation('turtle.fillcolor("'+_arg+'")')
        self.turtle.fillcolor(*args)
    def begin_fill(self):
        self.addOperation('turtle.begin_fill()')
        self.turtle.begin_fill()
    def end_fill(self):
        self.addOperation('turtle.end_fill()')
        self.turtle.end_fill()
    def forward(self,*args):
        _arg=','.join([str(i) for i in args])
        self.addOperation('turtle.forward('+_arg+')')
        self.turtle.forward(*args)
    def backward(self,*args):
        _arg=','.join([str(i) for i in args])
        self.addOperation('turtle.backward('+_arg+')')
        self.turtle.backward(*args)
    def circle(self,*args):
        _arg=','.join([str(i) for i in args])
        self.addOperation('turtle.circle('+_arg+')')
        self.turtle.circle(*args)
    def left(self,*args):
        _arg=','.join([str(i) for i in args])
        self.addOperation('turtle.left('+_arg+')')
        self.turtle.left(*args)
    def right(self,*args):
        _arg=','.join([str(i) for i in args])
        self.addOperation('turtle.right('+_arg+')')
        self.turtle.right(*args)
    def seth(self,*args):
        _arg=','.join([str(i) for i in args])
        self.addOperation('turtle.seth('+_arg+')')
        self.turtle.seth(*args)
    def dot(self,*args):
        _arg=','.join([str(i) for i in args])
        self.addOperation('turtle.dot('+_arg+')')
        self.turtle.dot(*args)
    def hideturtle(self):
        self.addOperation('turtle.hideturtle()')
        self.turtle.hideturtle()
    def update(self):
        self.addOperation('turtle.update()')
        self.turtle.update()
        
class DrawingBoard():
    def __init__(self):
        self.toolBar=Tk()
        self.author='Aikko'
        #====================param====================
        self.pressPos=None
        self.undoCount=[]
        self.pencilPoint=[]
        self.tmpLinePoint=None
        self.ToolDict={0:'直线',1:'铅笔',2:'矩形',3:'椭圆'}
        self.shiftState=False
        self.ctrlState=False
        self.curTool=0
        self.FullSharp=BooleanVar()
        self.FullSharp.set(False)
        self.outlineColor='#000000'
        self.fillColor='#000000'
        self.record_outlineColor='#000000'
        self.record_fillColor='#000000'
        self.outline_choice=[255,255]
        self.fill_choice=[255,255]
        self.quickcolor_pos=None
        self.quickcolor_state=False
        self.edit_flag=0
        self.LineAssistOffset=9
        #====================Window====================
        self.toolBar.title('Tools')
        self.toolBar.attributes('-toolwindow',True)
        self.toolBar.attributes('-topmost',True)
        self.toolBar.geometry(f'280x500')
        self.toolBar.resizable(False,False)
        self.toolBar.protocol('WM_DELETE_WINDOW',self.destroy)#
        self.toolFrame=LabelFrame(self.toolBar,text='Tool -> 直线',width=266,height=480)
        self.toolFrame.place(anchor=CENTER,relx=0.5,rely=0.5)
        self.painter=Toplevel(self.toolBar)
        self.painter.overrideredirect(True)
        self.painter.attributes('-topmost',True)
        self.showTurtle()
        self.record=TurtleRecord(self.turtle)
        self.record.addHeader()
        self.painter.attributes("-transparentcolor", 'white')
        self.paint=Canvas(self.painter,width=500,height=500,bg='white')
        self.paint.place(anchor=CENTER,relx=0.5,rely=0.5)
        self.painter.bind_all('<Control-z>',self.shortcut)
        self.toolBar.bind_all('<Control-z>',self.shortcut)
        self.painter.bind_all('<KeyPress>',self.PressCheck)
        self.painter.bind_all('<KeyRelease>',self.ReleaseCheck)
        self.colorMapping()
        self.quickColorBoard=None
        #====================ToolButton====================
        self.Tool_line=Button(self.toolFrame,text='直线',width=25,command=lambda:self.ToolChoice(0))
        self.Tool_line.place(anchor=CENTER,relx=0.5,rely=0.08)
        self.Tool_pencil=Button(self.toolFrame,text='铅笔',width=25,command=lambda:self.ToolChoice(1))
        self.Tool_pencil.place(anchor=CENTER,relx=0.5,rely=0.16)
        self.Tool_rect=Button(self.toolFrame,text='矩形',width=25,command=lambda:self.ToolChoice(2))
        self.Tool_rect.place(anchor=CENTER,relx=0.5,rely=0.24)
        self.Tool_circle=Button(self.toolFrame,text='椭圆',width=25,command=lambda:self.ToolChoice(3))
        self.Tool_circle.place(anchor=CENTER,relx=0.5,rely=0.32)
        self.Tool_fill=Checkbutton(self.toolFrame,text='填充',variable=self.FullSharp)
        self.Tool_fill.place(anchor=CENTER,relx=0.3,rely=0.44)
        self.Tool_output=Button(self.toolFrame,text='输出',width=10,command=self.output)
        self.Tool_output.place(anchor=CENTER,relx=0.7,rely=0.44)
        
        self._choiceIndicator_outline=Canvas(self.toolFrame,width=58,height=33,bg='#FFAA00')
        self._choiceIndicator_outline.place(anchor=CENTER,relx=0.25,y=250,x=-20)
        self.Tool_color_outline_label=Label(self.toolFrame,text='线条颜色：'+self.outlineColor)
        self.Tool_color_outline_label.place(anchor=CENTER,relx=0.63,y=250,x=-20)
        self.Tool_color_outline=Canvas(self.toolFrame,bg=self.outlineColor,width=50,height=25)
        self.Tool_color_outline.place(anchor=CENTER,relx=0.25,y=250,x=-20)
        self.Tool_color_outline.bind('<Button-1>',self.editorChoice_out)
        
        self._choiceIndicator_fill=Canvas(self.toolFrame,width=58,height=33,bg='#F0F0F0')
        self._choiceIndicator_fill.place(anchor=CENTER,relx=0.25,y=290,x=-20)
        self.Tool_color_fill_label=Label(self.toolFrame,text='填充颜色：'+self.outlineColor)
        self.Tool_color_fill_label.place(anchor=CENTER,relx=0.63,y=290,x=-20)
        self.Tool_color_fill=Canvas(self.toolFrame,bg=self.outlineColor,width=50,height=25)
        self.Tool_color_fill.place(anchor=CENTER,relx=0.25,y=290,x=-20)
        self.Tool_color_fill.bind('<Button-1>',self.editorChoice_fill)
        
        self._pickerIndicator_color=Canvas(self.toolFrame,width=256,height=62,bg='#F0F0F0')
        self._pickerIndicator_color.place(anchor=CENTER,relx=0.5,y=350)
        self._pickerIndicator_light=Canvas(self.toolFrame,width=256,height=62,bg='#F0F0F0')
        self._pickerIndicator_light.place(anchor=CENTER,relx=0.5,y=420)
        
        self.Tool_colorPicker=Canvas(self.toolFrame,width=256,height=40,bg='white')
        self.Tool_colorPicker.place(anchor=CENTER,relx=0.5,y=350)
        self.Tool_colorPicker.bind('<Button-1>',self.colorPicker)
        self.Tool_colorPicker.bind('<B1-Motion>',self.colorPicker)
        
        self.Tool_lightPicker=Canvas(self.toolFrame,width=256,height=40,bg='white')
        self.Tool_lightPicker.place(anchor=CENTER,relx=0.5,y=420)
        self.Tool_lightPicker.bind('<Button-1>',self.lightPicker)
        self.Tool_lightPicker.bind('<B1-Motion>',self.lightPicker_ex)
        
        self.PickerFill(45)
        self.loadQuickColorBoard()
        self.toolBar.after(1,self.listenLoading_QuickColorBoard)
        
        self._pickerIndicator_light.create_line(130,2,130,10,fill='#CCCCCC',width=2)
        self._pickerIndicator_light.create_line(130,52,130,62,fill='#CCCCCC',width=2)
        self.indicatorSetting('color',255)
        self.indicatorSetting('light',255)
        
        self.showReminder('快速调色板加载中,性能可能暂时受到影响...')
        
        self.toolBar.mainloop()
        
    def loadQuickColorBoard(self):
        _t=threading.Thread(target=self.loadQuickColorBoard_thread)
        _t.start()
        
    def listenLoading_QuickColorBoard(self):
        if self.quickColorBoard==None:
            self.toolBar.after(1000,self.listenLoading_QuickColorBoard)
            return 
        else:
            self.clearReminder()
            self.showReminder('加载完成， ~ 键可以唤出')
            self.toolBar.after(4000,self.clearReminder)
            self.buildingQuickColorBoard()    
            
    def buildingQuickColorBoard(self):
        self.quick=Toplevel(self.toolBar)
        self.quick.overrideredirect(True)
        self.quick.geometry(f'398x306+{self.toolBar.winfo_x()+283}+{self.toolBar.winfo_y()+225}')
        self.quick.attributes('-topmost',True)
        self.selectBoard=Canvas(self.quick,width=390,height=298)
        self.selectBoard.place(anchor=CENTER,relx=0.5,rely=0.5)
        self.selectBoard.create_image(2,2,anchor=NW,image=self.quickColorBoard.tkimg)
        self.selectBoard.bind('<Button-1>',self.quickColorPicker)
        self.selectBoard.bind('<B1-Motion>',self.quickColorPicker)
        self.quick.withdraw()
        
    def loadQuickColorBoard_thread(self):
        _tmp=QuickColor()
        self.quickColorBoard=_tmp
        
    def callQuickBoard(self,event):
        self.quick.deiconify()
        self.quick.geometry(f'398x306+{self.toolBar.winfo_x()+283}+{self.toolBar.winfo_y()+225}')
        
    def hideQuickBoard(self,event):
        self.quick.withdraw()
        
    def output(self):
        savepath=filedialog.asksaveasfilename(title='保存文件',filetypes=[('Python文件','.py')])
        if savepath:
            self.record.addTail()
            if savepath[-3:]!='.py':
                if os.path.isfile(savepath+'.py'):
                    r=messagebox.askyesno('文件已存在','文件已存在，是否覆盖？')
                    if not r:
                        return
                savepath+='.py'
            ret=self.save(savepath)
            if ret:
                messagebox.showinfo('文件保存','文件保存成功')
            else:
                messagebox.showerror('文件保存','文件保存失败！')
            
    def save(self,filename):
        try:
            with open(filename,'w+') as f:
                for actions in self.record.operation:
                    for action in actions:
                        f.write(action+'\n')
        except:
            return False
        else:
            return True
        
    def editorChoice_out(self,event):
        self.editorChoice(0)
        
    def editorChoice_fill(self,event):
        self.editorChoice(1)
    
    def editorChoice(self,choice):
        self.edit_flag=choice
        if self.edit_flag==0:
            self._choiceIndicator_outline.config(bg='#FFAA00')
            self._choiceIndicator_fill.config(bg='#F0F0F0')
            self.indicatorSetting('color',self.outline_choice[0])
            self.indicatorSetting('light',self.outline_choice[1])
        elif self.edit_flag==1:
            self._choiceIndicator_outline.config(bg='#F0F0F0')
            self._choiceIndicator_fill.config(bg='#FFAA00')
            self.indicatorSetting('color',self.fill_choice[0])
            self.indicatorSetting('light',self.fill_choice[1])
        else:
            assert False,'错误的输入'
    
    def colorMapping(self):
        self.mapping=[(255,x,0) for x in range(0,256,6)]
        self.mapping.extend([(255-i,255,0) for i in range(0,256,6)])
        self.mapping.extend([(0,255,i) for i in range(0,256,6)])
        self.mapping.extend([(0,255-i,255) for i in range(0,256,6)])
        self.mapping.extend([(i,0,255) for i in range(0,256,6)])
        self.mapping.extend([(255,0,255-i) for i in range(0,256,6)])
        self.mapping[-3:]=[(128,128,128),(128,128,128),(128,128,128)]
        
    def colorConvert(self,color,light):
        _r,_g,_b=self.mapping[color]
        _lightDev=(128-light)*2
        if _lightDev==-254:
            _lightDev=-255
        _r+=_lightDev
        _g+=_lightDev
        _b+=_lightDev
        if _r>255:
            _r=255
        if _r<0:
            _r=0
        if _g>255:
            _g=255
        if _g<0:
            _g=0
        if _b>255:
            _b=255
        if _b<0:
            _b=0
        return self.rgb(_r,_g,_b)
    
    def quickColorPicker(self,event):
        _pos=[event.x,event.y]
        if _pos[0]<0:
            _pos[0]=0
        if _pos[0]>387:
            _pos[0]=387
        if _pos[1]<0:
            _pos[1]=0
        if _pos[1]>295:
            _pos[1]=295
        _color=self.quickColorBoard.getColor(*_pos)
        print(_pos,_color)
        self.quickcolor_pos=_pos
        self.indicatorSetting('quickcolor',_pos,self.reverseColor(_color))
        if not self.edit_flag:
            self.outlineColor=self.rgb(*_color)
            self.Tool_color_outline.config(bg=self.outlineColor)
            self.Tool_color_outline_label.config(text='线条颜色：'+self.outlineColor)
        else:    
            self.fillColor=self.rgb(*_color)
            self.Tool_color_fill.config(bg=self.fillColor)
            self.Tool_color_fill_label.config(text='填充颜色：'+self.fillColor)
    
    def colorPicker(self,event):
        value=event.x if event.x<256 else 255
        if value<0:
            value=0
        self.indicatorSetting('color',value)
        if not self.edit_flag:
            self.outline_choice[0]=value
            self.outlineColor=self.colorConvert(self.outline_choice[0],self.outline_choice[1])
            self.Tool_color_outline.config(bg=self.outlineColor)
            self.Tool_color_outline_label.config(text='线条颜色：'+self.outlineColor)
        else:    
            self.fill_choice[0]=value
            self.fillColor=self.colorConvert(self.fill_choice[0],self.fill_choice[1])
            self.Tool_color_fill.config(bg=self.fillColor)
            self.Tool_color_fill_label.config(text='填充颜色：'+self.fillColor)
        
    def lightPicker(self,event):
        value=event.x if event.x<256 else 255
        if value<0:
            value=0
        self.indicatorSetting('light',value)
        if not self.edit_flag:
            self.outline_choice[1]=value
            self.outlineColor=self.colorConvert(self.outline_choice[0],self.outline_choice[1])
            self.Tool_color_outline.config(bg=self.outlineColor)
            self.Tool_color_outline_label.config(text='线条颜色：'+self.outlineColor)
        else:    
            self.fill_choice[1]=value
            self.fillColor=self.colorConvert(self.fill_choice[0],self.fill_choice[1])
            self.Tool_color_fill.config(bg=self.fillColor)
            self.Tool_color_fill_label.config(text='填充颜色：'+self.fillColor)
    
    def lightPicker_ex(self,event):
        sorption=8
        value=event.x if event.x<256 else 255
        if value<0:
            value=0
        if abs(value-128)<=sorption:
            value=128
        if abs(value)<=sorption//2:
            value=0
        if abs(value-255)<=sorption//2:
            value=255
        self.indicatorSetting('light',value)
        if not self.edit_flag:
            self.outline_choice[1]=value
            self.outlineColor=self.colorConvert(self.outline_choice[0],self.outline_choice[1])
            self.Tool_color_outline.config(bg=self.outlineColor)
            self.Tool_color_outline_label.config(text='线条颜色：'+self.outlineColor)
        else:    
            self.fill_choice[1]=value
            self.fillColor=self.colorConvert(self.fill_choice[0],self.fill_choice[1])
            self.Tool_color_fill.config(bg=self.fillColor)
            self.Tool_color_fill_label.config(text='填充颜色：'+self.fillColor)
    
    def PickerFill(self,high):
        _d=43
        _colorDict=['(255,i,0)','(255-i,255,0)','(0,255,i)','(0,255-i,255)','(i,0,255)','(255,0,255-i)']
        for i in range(0,256):
            for j in range(6):
                self.Tool_colorPicker.create_line(i//6+_d*j,0,i//6+_d*j,high,fill=self.rgb(*eval(_colorDict[j])))
            self.Tool_lightPicker.create_line(i+2,0,i+2,high,fill=self.rgb(255-i,255-i,255-i))
        self.Tool_colorPicker.create_line(257,0,257,high,fill='#808080')
    
    def indicatorSetting(self,Type,value,color='#000000'):
        #value:0-255
        _offset=2
        _indicatorHigh=7+_offset
        _indicatorWidth=14
        _indicatorLine=1
        if Type!='quickcolor':
            value+=_offset
            
        if Type=='color':
            self._pickerIndicator_color.delete('indicator')
            
            self.Tool_colorPicker.delete('indicator')
            self.Tool_colorPicker.create_line(value,0,value,66,fill='#000000',width=2,tags='indicator')
            
            self._pickerIndicator_color.create_line(value,_indicatorHigh,value-_indicatorWidth//2,_offset,fill=color,width=_indicatorLine,tags='indicator')
            self._pickerIndicator_color.create_line(value,_indicatorHigh,value+_indicatorWidth//2,_offset,fill=color,width=_indicatorLine,tags='indicator')
            self._pickerIndicator_color.create_line(value-_indicatorWidth//2,_offset,value+_indicatorWidth//2,_offset,fill=color,width=_indicatorLine,tags='indicator')
            self._pickerIndicator_color.create_line(value,64-_indicatorHigh,value-_indicatorWidth//2,62,fill=color,width=_indicatorLine,tags='indicator')
            self._pickerIndicator_color.create_line(value,64-_indicatorHigh,value+_indicatorWidth//2,62,fill=color,width=_indicatorLine,tags='indicator')
            self._pickerIndicator_color.create_line(value-_indicatorWidth//2,62,value+_indicatorWidth//2,62,fill=color,width=_indicatorLine,tags='indicator')
        elif Type=='light':
            self._pickerIndicator_light.delete('indicator')
            
            self.Tool_lightPicker.delete('indicator')
            self.Tool_lightPicker.create_line(value,0,value,66,fill='#FF0000',width=2,tags='indicator')
            
            self._pickerIndicator_light.create_line(value,_indicatorHigh,value-_indicatorWidth//2,_offset,fill=color,width=_indicatorLine,tags='indicator')
            self._pickerIndicator_light.create_line(value,_indicatorHigh,value+_indicatorWidth//2,_offset,fill=color,width=_indicatorLine,tags='indicator')
            self._pickerIndicator_light.create_line(value-_indicatorWidth//2,_offset,value+_indicatorWidth//2,_offset,fill=color,width=_indicatorLine,tags='indicator')
            self._pickerIndicator_light.create_line(value,64-_indicatorHigh,value-_indicatorWidth//2,62,fill=color,width=_indicatorLine,tags='indicator')
            self._pickerIndicator_light.create_line(value,64-_indicatorHigh,value+_indicatorWidth//2,62,fill=color,width=_indicatorLine,tags='indicator')
            self._pickerIndicator_light.create_line(value-_indicatorWidth//2,62,value+_indicatorWidth//2,62,fill=color,width=_indicatorLine,tags='indicator')
        elif Type=='quickcolor':
            self.selectBoard.delete('indicator')
            self.selectBoard.create_line(value[0]-15,value[1],value[0]+15,value[1],fill=color,width=_indicatorLine,tags='indicator')
            self.selectBoard.create_line(value[0],value[1]-15,value[0],value[1]+15,fill=color,width=_indicatorLine,tags='indicator')
        else:
            assert False,'错误的输入'
                    
    def reverseColor(self,color):
        _r=255-color[0]
        _g=255-color[1]
        _b=255-color[2]
        return self.rgb(_r,_g,_b)
                    
    def rgb(self,red,green,blue):
        _rgbCode='#'+hex(red)[2:].upper().zfill(2)+hex(green)[2:].upper().zfill(2)+hex(blue)[2:].upper().zfill(2)
        return _rgbCode
    
    def ToolChoice(self,tool):
        self.curTool=tool
        self.toolFrame.config(text=f'Tool -> {self.ToolDict[self.curTool]}')
    
    def destroy(self):
        try:
            self.painter.destroy()
            self.toolBar.destroy()
        except:
            pass
        finally:
            exit()
        
    def dragging(self,event):
        pos_turtle=self.getTurtlePos()
        self.toolBar.geometry(f'275x500+{(pos_turtle[0]+500)}+{(pos_turtle[1]-30)}')
        self.painter.geometry(f'500x500+{pos_turtle[0]}+{pos_turtle[1]}')
        if self.quickcolor_state:
            self.quick.geometry(f'398x306+{self.toolBar.winfo_x()+283}+{self.toolBar.winfo_y()+225}')
        self.painter.focus_force()
        
    def PressCheck(self,event):
        if event.keycode==16:
            self.shiftState=True
            self.Tool_circle.config(text='正圆')
            if self.ctrlState:
                self.Tool_line.config(text='连续辅直')
            else:
                self.Tool_line.config(text='辅直')
        if event.keycode==17:
            self.ctrlState=True
            if self.shiftState:
                self.Tool_line.config(text='连续辅直')
            else:
                self.Tool_line.config(text='连续直线')
                
        if event.keycode in (229,183,192):
            self.quickcolor_state=True
            if self.quickColorBoard!=None:
                self.callQuickBoard(event)
                
    def ReleaseCheck(self,event):
        if event.keycode==16:
            self.shiftState=False
            self.Tool_circle.config(text='椭圆')
            if self.ctrlState:
                self.Tool_line.config(text='连续直线')
            else:
                self.Tool_line.config(text='直线')
        if event.keycode==17:
            self.ctrlState=False
            if self.shiftState:
                self.Tool_line.config(text='辅直')
            else:
                self.Tool_line.config(text='直线')
            self.tmpLinePoint=None
            self.paint.delete('spec_reminder')
            
        if event.keycode==192:
            self.quickcolor_state=False
            if self.quickColorBoard!=None:
                self.hideQuickBoard(event)
            
    def test(self,*event):
        self.colorConvert(self.outline_choice[0],self.outline_choice[1])
    
    def penPress(self,event):
        self.pressPos=(event.x,event.y)
        if self.ctrlState:
            if self.tmpLinePoint==None:
                self.tmpLinePoint=self.pressPos
        if self.curTool==1:
            self.pencilPoint.append(self.posConvert_Turtle(self.pressPos))
        undoCount=0
        if self.record_outlineColor!=self.outlineColor:
            self.record_outlineColor=self.outlineColor
            self.record.pencolor(self.outlineColor)
            undoCount+=1
        if self.record_fillColor!=self.fillColor and self.FullSharp.get():
            self.record_fillColor=self.fillColor
            self.record.fillcolor(self.fillColor)
            undoCount+=1
        if undoCount!=0:
            self.undoCount.append(undoCount)
        self.record.fillOperation()
    
    def penRelease(self,event):
        self.paint.delete('reminder')
        releasePos=(event.x,event.y)
        _posTurtle_start=self.posConvert_Turtle(self.pressPos)
        _posTurtle_stop=self.posConvert_Turtle(releasePos)
        
        if self.curTool==0:
            if self.ctrlState:
                _tmpLine=self.posConvert_Turtle(self.tmpLinePoint)
                _calibration=None
                if _posTurtle_stop!=_tmpLine:
                    _calibration=self.penFunction_Line(_tmpLine,_posTurtle_stop)
                if self.shiftState and _calibration!=None:
                    self.tmpLinePoint=(releasePos[0]+_calibration[0],releasePos[1]+_calibration[1])
                else:
                    self.tmpLinePoint=releasePos
            else:
                self.penFunction_Line(_posTurtle_start,_posTurtle_stop)
        elif self.curTool==1:
            self.penFunction_pencil()
        elif self.curTool==2:
            self.penFunction_rect(_posTurtle_start,_posTurtle_stop)
        elif self.curTool==3:
            self.penFunction_circle(_posTurtle_start,_posTurtle_stop)    
        turtle.update()
        
    def penFunction_Line(self,startPos,stopPos):
        _calibration=None
        if self.shiftState:
            if abs(startPos[0]-stopPos[0])<=self.LineAssistOffset:
                _calibration=(-(stopPos[0]-startPos[0]),0)
                stopPos[0]=startPos[0]
            elif abs(startPos[1]-stopPos[1])<=self.LineAssistOffset:
                _calibration=(0,(stopPos[1]-startPos[1]))
                stopPos[1]=startPos[1]
            elif abs(abs(startPos[0]-stopPos[0])-abs(startPos[1]-stopPos[1]))<=self.LineAssistOffset*1.5:
                if startPos[0]-stopPos[0]>0:
                    _calibration=(-(stopPos[0]-(startPos[0]-abs(startPos[1]-stopPos[1]))),0)
                    stopPos[0]=startPos[0]-abs(startPos[1]-stopPos[1])
                else:
                    _calibration=(-(stopPos[0]-(startPos[0]+abs(startPos[1]-stopPos[1]))),0)
                    stopPos[0]=startPos[0]+abs(startPos[1]-stopPos[1])
        
        self.record.penup()
        self.record.goto(*startPos)
        self.record.pendown()
        self.record.goto(*stopPos)
        self.undoCount.append(4)
        self.record.fillOperation()
        return _calibration
    
    def penFunction_pencil(self):
        if len(self.pencilPoint)==0:
            return
        baseUndoCount=3        
        _single=False
        if len(self.pencilPoint)==1:
            _single=True
        if self.FullSharp.get() and not _single:
            self.record.fillcolor(self.fillColor)
            self.record.begin_fill()
        self.record.penup()
        self.record.goto(*self.pencilPoint[0])
        self.record.pendown()
        _firstPos=self.pencilPoint.pop(0)
        if len(self.pencilPoint)!=0:
            for _pos in self.pencilPoint:
                self.record.goto(*_pos)
                baseUndoCount+=1
        else:
            self.record.dot(2)
            baseUndoCount+=1
        if self.FullSharp.get() and not _single:
            self.record.goto(*_firstPos)
            self.record.end_fill()
            baseUndoCount+=3
        self.pencilPoint.clear()
        self.undoCount.append(baseUndoCount)
        self.record.fillOperation()
        
    def penFunction_rect(self,startPos,stopPos):
        baseUndoCount=12
        if self.FullSharp.get():
            self.record.fillcolor(self.fillColor)
            self.record.begin_fill()
        self.record.penup()
        self.record.goto(*startPos)
        self.record.pendown()
        self.record.seth(0)
        self.record.forward(stopPos[0]-startPos[0])
        self.record.right(90)
        self.record.forward(startPos[1]-stopPos[1])
        self.record.right(90)
        self.record.forward(stopPos[0]-startPos[0])
        self.record.right(90)
        self.record.forward(startPos[1]-stopPos[1])
        self.record.seth(0)
        if self.FullSharp.get():
            self.record.end_fill()
            baseUndoCount=14
        self.undoCount.append(baseUndoCount)
        self.record.fillOperation()
        
    def penFunction_circle(self,startPos,stopPos):
        if self.FullSharp.get():
            self.record.fillcolor(self.fillColor)
            self.record.begin_fill()
            
        if self.shiftState:
            _distance_x=abs(stopPos[0]-startPos[0])
            if startPos[1]>=stopPos[1]:
                if startPos[0]>=stopPos[0]:
                    stopPos[1]=startPos[1]+_distance_x
                    _offset_x=-0.5*_distance_x
                    _offset_y=_distance_x
                else:
                    stopPos[1]=startPos[1]-_distance_x
                    _offset_x=0.5*_distance_x
                    _offset_y=_distance_x
            else:
                if startPos[0]>=stopPos[0]:
                    stopPos[1]=startPos[1]-_distance_x
                    _offset_x=-0.5*_distance_x
                    _offset_y=0
                else:   
                    stopPos[1]=startPos[1]+_distance_x
                    _offset_x=0.5*_distance_x
                    _offset_y=0

        baseUndoCount=1    
        self.record.penup()
        if self.shiftState:
            self.record.goto(round(startPos[0]+_offset_x,2),round(startPos[1]-_offset_y,2))
            self.record.pendown()
            self.record.circle(0.5*abs(stopPos[0]-startPos[0]))
            baseUndoCount+=3
        else:
            a=(stopPos[0]-startPos[0])/2
            b=-(stopPos[1]-startPos[1])/2
            self.record.goto(round(startPos[0]+a,2),round(startPos[1],2))
            if abs(stopPos[0]-startPos[0])*abs(stopPos[1]-startPos[1])<=50:
                _pointCount=6
            elif abs(stopPos[0]-startPos[0])*abs(stopPos[1]-startPos[1])<=1000:
                _pointCount=16
            elif abs(stopPos[0]-startPos[0])*abs(stopPos[1]-startPos[1])<=10000:
                _pointCount=24
            elif abs(stopPos[0]-startPos[0])*abs(stopPos[1]-startPos[1])<=100000:
                _pointCount=50
            else:
                _pointCount=80
            minAngle = 2*math.pi /_pointCount
            for i in range(_pointCount):
                if i==0:
                    self.record.pendown()
                self.record.goto(round(a*math.sin((i+1)*minAngle)+a+startPos[0],2),round(b*math.cos((i+1)*minAngle)+startPos[1]-b,2))
            self.record.goto(round(startPos[0]+a,2),round(startPos[1],2))
            baseUndoCount+=_pointCount+3
            
        if self.FullSharp.get():
            self.record.end_fill()
            baseUndoCount+=2
        self.undoCount.append(baseUndoCount)
        self.record.fillOperation()
        
    def showReminder(self,_text):
        self.paint.create_text((250,490),text=_text,fill='#808080',tags='text_reminder')
        
    def clearReminder(self):
        self.paint.delete('text_reminder')
        
    def penMove(self,event):
        self.paint.delete('spec_reminder')
        if self.curTool==0:
            if self.tmpLinePoint!=None:
                _start=self.posConvert_Reminder(self.tmpLinePoint)
                _stop=self.posConvert_Reminder((event.x,event.y))
                
                if self.shiftState:
                    if abs(_start[0]-_stop[0])<=self.LineAssistOffset:
                        _stop[0]=_start[0]
                    if abs(_start[1]-_stop[1])<=self.LineAssistOffset:
                        _stop[1]=_start[1]
                        
                    if abs(abs(_start[0]-_stop[0])-abs(_start[1]-_stop[1]))<=self.LineAssistOffset*1.5:                  
                        if _start[0]-_stop[0]>0:
                            _stop[0]=_start[0]-abs(_start[1]-_stop[1])
                        else:
                            _stop[0]=_start[0]+abs(_start[1]-_stop[1])
                
                self.paint.create_line((_start[0],_start[1],_stop[0],_stop[1]),fill='red',tags='spec_reminder')
        
    def penDrag(self,event):
        if self.curTool!=1:
            self.paint.delete('reminder')
        releasePos=(event.x,event.y)
        _posReminder_start=self.posConvert_Reminder(self.pressPos)
        _posReminder_stop=self.posConvert_Reminder(releasePos)
        
        if self.curTool==0:
            if self.shiftState:
                if abs(_posReminder_start[0]-_posReminder_stop[0])<=self.LineAssistOffset:
                    _posReminder_stop[0]=_posReminder_start[0]
                if abs(_posReminder_start[1]-_posReminder_stop[1])<=self.LineAssistOffset:
                    _posReminder_stop[1]=_posReminder_start[1]
                    
                if abs(abs(_posReminder_start[0]-_posReminder_stop[0])-abs(_posReminder_start[1]-_posReminder_stop[1]))<=self.LineAssistOffset*1.5:                  
                    if _posReminder_start[0]-_posReminder_stop[0]>0:
                        _posReminder_stop[0]=_posReminder_start[0]-abs(_posReminder_start[1]-_posReminder_stop[1])
                    else:
                        _posReminder_stop[0]=_posReminder_start[0]+abs(_posReminder_start[1]-_posReminder_stop[1])
            self.paint.create_line((_posReminder_start[0],_posReminder_start[1],_posReminder_stop[0],_posReminder_stop[1]),fill='red',tags='reminder')
        elif self.curTool==1:
            _posPencil=self.posConvert_Turtle(releasePos)
            self.paint.create_line((_posReminder_stop[0],_posReminder_stop[1],_posReminder_stop[0]+1,_posReminder_stop[1]+1),fill='red',tags='reminder')
            self.pencilPoint.append(_posPencil)
        elif self.curTool==2:
            self.paint.create_rectangle((_posReminder_start[0],_posReminder_start[1],_posReminder_stop[0],_posReminder_stop[1]),outline='red',tags='reminder')
        elif self.curTool==3:
            if self.shiftState:
                _distance_x=(_posReminder_stop[0]-_posReminder_start[0])
                if _posReminder_start[1]>=_posReminder_stop[1]:
                    if _posReminder_start[0]>=_posReminder_stop[0]:
                        _posReminder_stop[1]=_posReminder_start[1]+_distance_x
                    else:
                        _posReminder_stop[1]=_posReminder_start[1]-_distance_x
                else:
                    if _posReminder_start[0]>=_posReminder_stop[0]:
                        _posReminder_stop[1]=_posReminder_start[1]-_distance_x
                    else:
                        _posReminder_stop[1]=_posReminder_start[1]+_distance_x
                        
            self.paint.create_oval((_posReminder_start[0],_posReminder_start[1],_posReminder_stop[0],_posReminder_stop[1]),outline='red',tags='reminder')
    
    def getTurtlePos(self):
        return self.screen.cv.winfo_rootx(),self.screen.cv.winfo_rooty()
    
    def posConvert_Turtle(self,pos):
        _x=pos[0]-250-2
        _y=250-pos[1]+2
        return [_x,_y]
    def posConvert_Reminder(self,pos):
        _x=pos[0]+3
        _y=pos[1]+3
        return [_x,_y]

    def shortcut(self,*event):
        if self.undoCount:
            for _ in range(self.undoCount[-1]):
                self.turtle.undo()
            self.undoCount.pop()
            self.record.operation.pop()
    
    def showTurtle(self):
        self.turtle=turtle.Turtle()
        turtle.setup(width=500,height=500)
        turtle.title('Painting')
        turtle.tracer(False)
        self.screen=turtle.Screen()
        self.screen.cv._rootwindow.attributes('-topmost',False)
        self.screen.cv._rootwindow.resizable(False,False)
        self.screen.cv.bind_all('<Configure>',self.dragging)
        self.screen.cv.bind_all('<Button-1>',self.penPress)
        self.screen.cv.bind_all('<B1-Motion>',self.penDrag)
        self.screen.cv.bind_all('<Motion>',self.penMove)
        self.screen.cv.bind_all('<ButtonRelease-1>',self.penRelease)
        self.screen.cv.bind_all('<Control-z>',self.shortcut)
        self.turtle.hideturtle()
        turtle.update()

class QuickColor:
    def __init__(self):
        self.size=[388,256]
        self.margin_high=20
        self.size[1]+=self.margin_high*2
        self.img=Image.new('RGB',self.size,color='white')
        self.colorFill()
        self.tkimg=ImageTk.PhotoImage(self.img)
    def getColor(self,pos_x,pos_y):
        return self.img.getpixel((pos_x,pos_y))    
    
    def colorFill(self):
        _img=ImageDraw.Draw(self.img)
        _img.rectangle((0,0,388,self.margin_high),fill='white')
        _d=64
        _colorDict=['(255,i,0)','(255-i,255,0)','(0,255,i)','(0,255-i,255)','(i,0,255)','(255,0,255-i)']
        for h in range(0,513):
            for i in range(0,256):
                for j in range(6):
                    color=eval(_colorDict[j])
                    color=self.rgbGradient(*color,256-h)
                    _img.point((i//4+_d*j,h//2+self.margin_high),fill=self.rgb(*color))
                _color=(128,128,128)
                _color=self.rgbGradient(*_color,256-h)
                _img.line((384,h//2+self.margin_high,390,h//2+self.margin_high),fill=self.rgb(*_color))
        _img.rectangle((0,self.size[1]-self.margin_high,388,self.size[1]),fill='black')        
    def rgb(self,red,green,blue):
        _rgbCode='#'+hex(red)[2:].upper().zfill(2)+hex(green)[2:].upper().zfill(2)+hex(blue)[2:].upper().zfill(2)
        return _rgbCode
    def rgbGradient(self,_r,_g,_b,change):
        _r+=change
        _g+=change
        _b+=change
        if _r<0:
            _r=0
        elif _r>255:
            _r=255
        if _g<0:
            _g=0
        elif _g>255:
            _g=255
        if _b<0:
            _b=0
        elif _b>255:    
            _b=255
        return _r,_g,_b
    
    
if __name__=='__main__':
    paint=DrawingBoard()
