import tkinter as tk
from tkinter import filedialog, ttk, messagebox, scrolledtext
import os
from tkinter import font

class NumberingRenamer:
    def __init__(self, root):
        self.root = root
        self.root.title("文件编号命名工具")
        self.root.geometry("750x550")
        self.root.resizable(False, False)
        
        # 设置中文字体
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("SimHei", 10))
        self.style.configure("TButton", font=("SimHei", 10))
        self.style.configure("TCombobox", font=("SimHei", 10))
        self.style.configure("TEntry", font=("SimHei", 10))
        
        # 存储文件信息
        self.folder_path = tk.StringVar()
        self.file_list = []  # 存储(文件目录, 原文件名)元组
        self.include_subfolders = tk.BooleanVar(value=False)
        
        # 创建界面
        self.create_widgets()
        
        # 状态标记
        self.renaming = False

    def create_widgets(self):
        # 标题
        title_label = ttk.Label(self.root, text="文件编号命名工具", font=("SimHei", 16, "bold"))
        title_label.pack(pady=15)
        
        # 文件夹选择区域
        folder_frame = ttk.LabelFrame(self.root, text="目标文件夹")
        folder_frame.pack(fill=tk.X, padx=50, pady=5)
        
        ttk.Label(folder_frame, text="路径:").grid(row=0, column=0, padx=5, pady=10, sticky=tk.W)
        
        folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_path, width=50)
        folder_entry.grid(row=0, column=1, padx=5, pady=10, sticky=tk.W)
        
        browse_btn = ttk.Button(folder_frame, text="浏览", command=self.browse_folder)
        browse_btn.grid(row=0, column=2, padx=5, pady=10)
        
        # 包含子文件夹选项
        subfolder_check = ttk.Checkbutton(
            folder_frame, 
            text="包含子文件夹", 
            variable=self.include_subfolders,
            command=self.refresh_file_list
        )
        subfolder_check.grid(row=0, column=3, padx=5, pady=10)
        
        # 文件列表预览区域
        preview_frame = ttk.LabelFrame(self.root, text="文件列表 (原文件名 → 新文件名)")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=5)
        
        self.preview_text = scrolledtext.ScrolledText(preview_frame, height=12, font=("SimHei", 9))
        self.preview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 编号规则设置区域
        rule_frame = ttk.LabelFrame(self.root, text="编号规则")
        rule_frame.pack(fill=tk.X, padx=50, pady=5)
        
        # 前缀设置
        ttk.Label(rule_frame, text="前缀:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.prefix = ttk.Entry(rule_frame, width=15)
        self.prefix.grid(row=0, column=1, padx=5, pady=10, sticky=tk.W)
        self.prefix.bind("<KeyRelease>", self.update_preview)
        
        # 起始编号
        ttk.Label(rule_frame, text="起始编号:").grid(row=0, column=2, padx=10, pady=10, sticky=tk.W)
        self.start_num = ttk.Entry(rule_frame, width=8)
        self.start_num.insert(0, "1")
        self.start_num.grid(row=0, column=3, padx=5, pady=10, sticky=tk.W)
        self.start_num.bind("<KeyRelease>", self.update_preview)
        
        # 编号位数（补零）
        ttk.Label(rule_frame, text="编号位数:").grid(row=0, column=4, padx=10, pady=10, sticky=tk.W)
        self.num_digits = ttk.Combobox(rule_frame, values=["1", "2", "3", "4", "5"], width=5)
        self.num_digits.current(1)  # 默认2位（01, 02...）
        self.num_digits.grid(row=0, column=5, padx=5, pady=10, sticky=tk.W)
        self.num_digits.bind("<<ComboboxSelected>>", self.update_preview)
        
        # 后缀设置
        ttk.Label(rule_frame, text="后缀:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        self.suffix = ttk.Entry(rule_frame, width=15)
        self.suffix.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        self.suffix.bind("<KeyRelease>", self.update_preview)
        
        # 编号位置
        ttk.Label(rule_frame, text="编号位置:").grid(row=1, column=2, padx=10, pady=5, sticky=tk.W)
        self.num_position = ttk.Combobox(
            rule_frame, 
            values=["前缀+编号+后缀", "编号+前缀+后缀", "前缀+后缀+编号"], 
            width=15
        )
        self.num_position.current(0)  # 默认"前缀+编号+后缀"
        self.num_position.grid(row=1, column=3, columnspan=2, padx=5, pady=5, sticky=tk.W)
        self.num_position.bind("<<ComboboxSelected>>", self.update_preview)
        
        # 按钮区域
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=15)
        
        self.rename_btn = ttk.Button(btn_frame, text="执行编号命名", command=self.execute_rename)
        self.rename_btn.pack(side=tk.LEFT, padx=10)
        
        self.refresh_btn = ttk.Button(btn_frame, text="刷新列表", command=self.refresh_file_list)
        self.refresh_btn.pack(side=tk.LEFT, padx=10)
        
        # 状态标签
        self.status_label = ttk.Label(self.root, text="就绪", foreground="blue")
        self.status_label.pack(pady=5)

    def browse_folder(self):
        """选择文件夹并加载文件"""
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)
            self.refresh_file_list()

    def refresh_file_list(self):
        """刷新文件列表（按加载顺序排序）"""
        folder = self.folder_path.get()
        if not folder or not os.path.exists(folder):
            self.file_list = []
            self.preview_text.delete(1.0, tk.END)
            return
        
        # 收集文件（按系统默认顺序）
        self.file_list = []
        if self.include_subfolders.get():
            # 递归子文件夹（按目录深度排序）
            for root_dir, _, files in os.walk(folder):
                for file in sorted(files):  # 按文件名排序
                    self.file_list.append((root_dir, file))
        else:
            # 仅当前文件夹（按文件名排序）
            for file in sorted(os.listdir(folder)):
                file_path = os.path.join(folder, file)
                if os.path.isfile(file_path):
                    self.file_list.append((folder, file))
        
        self.update_preview()
        self.status_label.config(text=f"已加载 {len(self.file_list)} 个文件，按顺序编号", foreground="blue")

    def update_preview(self, event=None):
        """实时预览编号后的文件名"""
        if not self.file_list:
            return
        
        self.preview_text.delete(1.0, tk.END)
        
        try:
            # 获取编号参数
            prefix = self.prefix.get()
            suffix = self.suffix.get()
            start_num = int(self.start_num.get()) if self.start_num.get().isdigit() else 1
            num_digits = int(self.num_digits.get())
            position = self.num_position.get()
            
            # 生成新文件名并预览
            for i, (_, old_name) in enumerate(self.file_list):
                # 分离文件名和扩展名（如"image.jpg" → "image"和".jpg"）
                name, ext = os.path.splitext(old_name)
                
                # 生成编号（如start_num=3, i=0 → 3；补零至指定位数）
                current_num = start_num + i
                num_str = f"{current_num:0{num_digits}d}"  # 格式化编号（01, 002等）
                
                # 根据位置规则组合文件名
                if position == "前缀+编号+后缀":
                    new_name = f"{prefix}{num_str}{suffix}{ext}"
                elif position == "编号+前缀+后缀":
                    new_name = f"{num_str}{prefix}{suffix}{ext}"
                else:  # 前缀+后缀+编号
                    new_name = f"{prefix}{suffix}{num_str}{ext}"
                
                # 预览显示（截断过长名称）
                display_old = old_name if len(old_name) <= 30 else old_name[:27] + "..."
                display_new = new_name if len(new_name) <= 30 else new_name[:27] + "..."
                self.preview_text.insert(tk.END, f"{display_old.ljust(35)}→  {display_new}\n")
        
        except Exception as e:
            self.status_label.config(text=f"参数错误: {str(e)}", foreground="red")

    def execute_rename(self):
        """执行编号命名"""
        if not self.file_list:
            messagebox.showwarning("提示", "请先选择文件夹并加载文件")
            return
        
        if self.renaming:
            return
        
        self.renaming = True
        self.rename_btn.config(state=tk.DISABLED)
        self.status_label.config(text="正在执行编号命名...", foreground="orange")
        
        # 计算新文件名
        new_file_list = []
        try:
            prefix = self.prefix.get()
            suffix = self.suffix.get()
            start_num = int(self.start_num.get()) if self.start_num.get().isdigit() else 1
            num_digits = int(self.num_digits.get())
            position = self.num_position.get()
            
            for i, (dir_path, old_name) in enumerate(self.file_list):
                name, ext = os.path.splitext(old_name)
                current_num = start_num + i
                num_str = f"{current_num:0{num_digits}d}"
                
                # 生成新文件名
                if position == "前缀+编号+后缀":
                    new_name = f"{prefix}{num_str}{suffix}{ext}"
                elif position == "编号+前缀+后缀":
                    new_name = f"{num_str}{prefix}{suffix}{ext}"
                else:
                    new_name = f"{prefix}{suffix}{num_str}{ext}"
                
                new_file_list.append((dir_path, old_name, new_name))
        
        except Exception as e:
            self.status_label.config(text=f"参数错误: {str(e)}", foreground="red")
            self.renaming = False
            self.rename_btn.config(state=tk.NORMAL)
            return
        
        # 执行重命名
        success = 0
        fail = 0
        fail_list = []
        
        for dir_path, old_name, new_name in new_file_list:
            old_path = os.path.join(dir_path, old_name)
            new_path = os.path.join(dir_path, new_name)
            
            # 跳过同名（无需处理）
            if old_name == new_name:
                success += 1
                continue
            
            try:
                os.rename(old_path, new_path)
                success += 1
            except Exception as e:
                fail += 1
                fail_list.append(f"{old_name} → {new_name}: {str(e)}")
        
        # 完成后更新状态
        self.renaming = False
        self.rename_btn.config(state=tk.NORMAL)
        self.refresh_file_list()  # 刷新列表显示新名称
        
        # 显示结果
        result = f"编号完成: 成功 {success} 个, 失败 {fail} 个"
        if fail > 0:
            result += "\n失败项（可能因文件被占用或重名）:\n" + "\n".join(fail_list[:5])
            messagebox.showerror("结果", result)
        else:
            messagebox.showinfo("结果", result)
        
        self.status_label.config(text=result, foreground="green" if fail == 0 else "orange")

if __name__ == "__main__":
    root = tk.Tk()
    # 全局字体设置
    default_font = font.nametofont("TkDefaultFont")
    default_font.configure(family="SimHei")
    root.option_add("*Font", default_font)
    
    app = NumberingRenamer(root)
    root.mainloop()
