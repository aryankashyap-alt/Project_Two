
import tkinter as tk
from tkinter import ttk, messagebox
import math, re

ACCENT = "#6366F1"
SUCCESS = "#10B981"
DANGER = "#EF4444"
BG = "#0F172A"
CARD = "#1E293B"
TEXT = "#E2E8F0"

try:
    import sympy as sp
except Exception:
    sp = None

class ProCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Advance Calculator")
        self.root.geometry("700x800")
        self.root.configure(bg=BG)

        self.expr = tk.StringVar()
        self.preview = tk.StringVar()
        self.memory = 0
        self.angle_mode = "DEG"

        self.build_ui()

    def build_ui(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except:
            pass

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True)

        calc_tab = tk.Frame(notebook, bg=BG)
        conv_tab = tk.Frame(notebook, bg=BG)
        eq_tab = tk.Frame(notebook, bg=BG)

        notebook.add(calc_tab, text="Calculator")
        notebook.add(conv_tab, text="Converter")
        notebook.add(eq_tab, text="Equation Solver")

        self.build_calculator(calc_tab)
        self.build_converter(conv_tab)
        self.build_solver(eq_tab)

    def build_calculator(self, parent):
        tk.Label(parent,text="Advance Calculator",
                 bg=BG,fg=ACCENT,font=("Times New Roman",18,"bold")).pack(pady=10)

        tk.Label(parent,textvariable=self.preview,bg=BG,fg="#94A3B8").pack(anchor="e",padx=15)

        tk.Entry(parent,textvariable=self.expr,justify="right",
                 font=("Times New Roman",24),bg=CARD,fg=TEXT,
                 insertbackground=TEXT).pack(fill="x",padx=15,pady=5,ipady=12)

        self.expr.trace_add("write", lambda *a: self.live_preview())

        top = tk.Frame(parent,bg=BG)
        top.pack(fill="x",padx=15)

        tk.Button(top,text="DEG/RAD",bg=ACCENT,fg="white",
                  command=self.toggle_mode).pack(side="left")

        tk.Button(top,text="COPY",bg=SUCCESS,fg="white",
                  command=self.copy).pack(side="right")

        frame = tk.Frame(parent,bg=BG)
        frame.pack(fill="both",expand=True,padx=10,pady=10)

        buttons = [
            "MC","MR","M+","M-",
            "C","(",")","/",
            "sin(","7","8","9",
            "cos(","4","5","6",
            "tan(","1","2","3",
            "log(","0",".","=",
            "ln(","sqrt(","!","Del",
            "pi","e","**","+",
            "abs(","exp(","%","-"
        ]

        for r in range(8):
            frame.rowconfigure(r,weight=1)
        for c in range(4):
            frame.columnconfigure(c,weight=1)

        for i,b in enumerate(buttons):
            color = CARD
            if b in ["+","-","/"]: color = ACCENT
            if b in ["="]: color = SUCCESS
            if b in ["C","Del","MC"]: color = DANGER

            tk.Button(frame,text=b,bg=color,fg="white",
                      command=lambda x=b:self.press(x)).grid(
                      row=i//4,column=i%4,sticky="nsew",padx=3,pady=3)

        self.history = tk.Text(parent,height=7,bg=CARD,fg=TEXT)
        self.history.pack(fill="x",padx=15,pady=10)

    def build_converter(self,parent):
        tk.Label(parent,text="UNIT CONVERTER",
                 bg=BG,fg=ACCENT,font=("Times New Roman",18,"bold")).pack(pady=15)

        self.conv_value = tk.StringVar()
        self.conv_result = tk.StringVar()

        self.conversions = {
            "Meters → Feet": lambda x:x*3.28084,
            "Feet → Meters": lambda x:x/3.28084,
            "Kg → Pounds": lambda x:x*2.20462,
            "Pounds → Kg": lambda x:x/2.20462,
            "Celsius → Fahrenheit": lambda x:(x*9/5)+32,
            "Fahrenheit → Celsius": lambda x:(x-32)*5/9,
            "Liters → Gallons": lambda x:x*0.264172,
            "Gallons → Liters": lambda x:x/0.264172,
        }

        self.combo = ttk.Combobox(parent,values=list(self.conversions.keys()),state="readonly")
        self.combo.pack(fill="x",padx=30,pady=10)
        self.combo.current(0)

        tk.Entry(parent,textvariable=self.conv_value,bg=CARD,fg=TEXT).pack(fill="x",padx=30,pady=10)

        tk.Button(parent,text="Convert",bg=ACCENT,fg="white",
                  command=self.convert).pack(pady=10)

        tk.Label(parent,textvariable=self.conv_result,bg=BG,fg=SUCCESS,
                 font=("Times New Roman",14,"bold")).pack()

    def build_solver(self,parent):
        tk.Label(parent,text="EQUATION SOLVER",
                 bg=BG,fg=ACCENT,font=("Times New Roman",18,"bold")).pack(pady=15)

        self.eq = tk.StringVar()
        self.eq_result = tk.StringVar()

        tk.Label(parent,text="Example: 2*x+5=15",
                 bg=BG,fg=TEXT).pack()

        tk.Entry(parent,textvariable=self.eq,bg=CARD,fg=TEXT,
                 font=("Times New Roman",14)).pack(fill="x",padx=30,pady=10)

        tk.Button(parent,text="Solve",bg=SUCCESS,fg="white",
                  command=self.solve_equation).pack(pady=10)

        tk.Label(parent,textvariable=self.eq_result,bg=BG,fg=SUCCESS,
                 font=("Times New Roman",14,"bold")).pack()

    def toggle_mode(self):
        self.angle_mode = "RAD" if self.angle_mode=="DEG" else "DEG"

    def copy(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.expr.get())

    def press(self,v):
        if v=="C": self.expr.set("")
        elif v=="Del": self.expr.set(self.expr.get()[:-1])
        elif v=="=": self.calculate()
        elif v=="MC": self.memory=0
        elif v=="MR": self.expr.set(self.expr.get()+str(self.memory))
        elif v=="M+": 
            try:self.memory+=float(self.expr.get())
            except:pass
        elif v=="M-":
            try:self.memory-=float(self.expr.get())
            except:pass
        else:
            self.expr.set(self.expr.get()+v)

    def preprocess(self,e):
        e=e.replace("pi",str(math.pi))
        e=e.replace("e",str(math.e))
        e=re.sub(r'(\d+(\.\d+)?)%',r'(\1/100)',e)
        while "!" in e:
            e=re.sub(r'(\d+)!',lambda m:str(math.factorial(int(m.group(1)))),e,1)
        return e

    def funcs(self):
        conv=lambda x: math.radians(x) if self.angle_mode=="DEG" else x
        return {
            "sin":lambda x: math.sin(conv(x)),
            "cos":lambda x: math.cos(conv(x)),
            "tan":lambda x: math.tan(conv(x)),
            "sqrt":math.sqrt,
            "log":math.log10,
            "ln":math.log,
            "exp":math.exp,
            "abs":abs
        }

    def live_preview(self):
        try:
            r=eval(self.preprocess(self.expr.get()),{"__builtins__":{}},self.funcs())
            self.preview.set(f"= {r}")
        except:
            self.preview.set("")

    def calculate(self):
        try:
            ex=self.expr.get()
            r=eval(self.preprocess(ex),{"__builtins__":{}},self.funcs())
            self.history.insert("end",f"{ex} = {r}\n")
            self.expr.set(str(r))
        except Exception as e:
            messagebox.showerror("Error",str(e))

    def convert(self):
        try:
            v=float(self.conv_value.get())
            r=self.conversions[self.combo.get()](v)
            self.conv_result.set(f"Result: {round(r,6)}")
        except Exception as e:
            messagebox.showerror("Converter",str(e))

    def solve_equation(self):
        if sp is None:
            self.eq_result.set("Install sympy: pip install sympy")
            return
        try:
            x=sp.Symbol("x")
            left,right=self.eq.get().split("=")
            ans=sp.solve(sp.sympify(left)-sp.sympify(right),x)
            self.eq_result.set(f"x = {ans}")
        except Exception as e:
            messagebox.showerror("Solver",str(e))

if __name__=="__main__":
    root=tk.Tk()
    ProCalculator(root)
    root.mainloop()
