"""夏启圣的代码详解！"""

# 这里一段是import需要的库，tkinter是ui框架，ttkbootstrap是tkinter的美化库
# time 用于准确暂停时间，requests用于获取课程id与发送抢课申请。
# threading 用于创建多线程，以实现在保证ui界面不卡死的同时进行抢课指令
import tkinter as tk
import tkinter.messagebox
from tkinter import messagebox
from ttkbootstrap import Style
import time
import requests
import threading

# 初始化线程变量
stop_thread = False


# 本def用于判断一个str是否是阿拉伯数字。用于限制场次号填中文数字。
def can_convert_to_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


# 本def是核心逻辑代码
def start_registration():
    # 将抢课代码放置在单独def,这样方便threading库创建独立线程
    def registration_thread():
        # global参数：使def里的参数和def外的参数是同一个。(这个作者很懒，这种写法容易在长期运行时导致报错。应该使用queue。)
        global stop_thread
        stop_thread = False

        attempts = 800
        attempt_count = 0
        # 思广还是漫思？
        class_type = int(class_type_var.get())
        # 几个课？
        repeat = int(repeat_var.get())
        # 几月几号？
        date = date_var.get()
        # student id
        student_id = student_id_var.get()
        # 暂停时间
        pause_time = float(pause_var.get())

        # 是储存lab场次和名字的列表，这两个数据用于获得lab id
        lab_names = []
        time_slots = []

        # 这个代码用于从tkinter界面输入框中提取信息储存在表里。为什么会工作请详见tkinter文档。
        # lab_name_entries与time_slot_entries储存的是类的实例。将类理解为面条制作手册的话，实例就是做好面条了，接下来的代码在吃面条。所以可以使用.get()
        for i in range(repeat):
            lab_name = lab_name_entries[i].get()
            time_slot = time_slot_entries[i].get()
            lab_names.append(lab_name)
            time_slots.append(time_slot)

        succeeded_class_id = []
        succeeded_class_name = []

        # 该判断语句用于暂停抢课。
        while not stop_thread:
            time.sleep(pause_time)
            # 这里开始直到68行在获取课程列表，为什么这么写？网页逆向出来反正是这样的。
            url = "https://www.youkehulian.com/teachaicms/laboratorySessionMapping/getLaboratorySession"
            json_data = {
                "userId": student_id,
                "laboratoryType": class_type,
                "studentId": student_id,
                "startDate": date,
                "sessionsDictId": []
            }

            try:
                response = requests.post(url, json=json_data)
                data = response.json()
            except:
                log_output("网络炸了！")
                continue

            # 0即正常获得了课程列表
            if data["code"] == 0:
                data = data["data"]
                log_output("已开始抢票")
            else:
                log_output("未开始抢票")
                # continue用于跳过之后的代码，重新执行while循环。
                continue

            attempt_count += 1
            # 这个代码在通过lab名称和场次查找相符的lab id
            for a in range(len(lab_names)):
                class_id = None
                for x in data:
                    if lab_names[a] in x["laboratoryName"] and time_slots[a] in x["timeSlot"]:
                        log_output("正在查找：" + lab_names[a] + " " + time_slots[a])
                        class_id = x["id"]
                # class_id is None 就说明上一行代码从未执行过。
                if class_id is None:
                    log_output("未找到你的课程！" + + lab_names[a] + " " + time_slots[a])
                    continue
                elif class_id in succeeded_class_id:
                    log_output("这节课已经抢到了！")
                    continue
                else:
                    # 这里在发送reserve申请。为什么是这些参数，也是因为网页是这样写的。
                    tick_url = "https://www.youkehulian.com/teachaicms/laboratoryUserMapping/registration"
                    tick_json_data = {"userId": student_id, "studentId": student_id, "laboratorySessionId": class_id}
                    try:
                        response = requests.post(tick_url, json=tick_json_data)
                    except:
                        log_output("网络炸了！")
                        continue

                if response.json()["code"] == 0:
                    log_output("抢票成功")
                    succeeded_class_id.append(class_id)
                    succeeded_class_name.append("场次：" + time_slots[a] + " , 教室：" + lab_names[a])
                    # return 结束循环。
                else:
                    log_output("抢票失败: " + response.json()["message"])

            if len(succeeded_class_id) == repeat:
                messagebox.showinfo("抢票成功！", "抢票成功！")
                return
            else:
                if attempt_count == attempts:
                    messagebox.showinfo("抢票失败！",
                                        "抢票失败！抢到的课程：\n" + "\n".join(succeeded_class_name) + "\n其余的未抢到.")
                    return

    # 确认开始抢课的提示窗口
    if can_convert_to_int(time_slot_entries[0].get()):
        messagebox.showerror("场次要输入中文汉字数字！", "场次要输入中文汉字数字！")
    else:
        if messagebox.askokcancel("确认",
                                  "请确保所有内容都正确填写！否则一定抢不到！\n不建议暂停时间小于0.3秒\n只能选择自己需要的课(＾Ｕ＾)ノ~！\n\n确定要开始抢课吗？"):
            threading.Thread(target=registration_thread, daemon=True).start()


def stop_registration():
    global stop_thread
    stop_thread = True
    log_output("抢课已结束")


def log_output(message):
    log_text.insert(tk.END, message + "\n")
    log_text.see(tk.END)


def add_course_fields():
    lab_name_entries.clear()
    time_slot_entries.clear()

    for widget in course_frame.winfo_children():
        widget.destroy()

    for i in range(int(repeat_var.get())):
        tk.Label(course_frame, text=f"课程 {i + 1} 教室号:").grid(row=i, column=0, padx=0, pady=5, sticky="e")
        lab_name_entry = tk.Entry(course_frame, width=18)
        lab_name_entry.grid(row=i, column=1, padx=5, pady=5, sticky="w")
        lab_name_entries.append(lab_name_entry)

        tk.Label(course_frame, text="场次:").grid(row=i, column=2, padx=5, pady=5, sticky="e")
        time_slot_entry = tk.Entry(course_frame, width=18)
        time_slot_entry.grid(row=i, column=3, padx=5, pady=5, sticky="w")
        time_slot_entries.append(time_slot_entry)


# 创建主窗口
style = Style(theme='cosmo')  # 选择一个白色的主题
root = style.master
root.title("原神！启动！")

# 禁止放大窗口
root.resizable(False, False)

# 输入框和标签左侧留空白的宽度
padding_x = 10  # 你可以调整这个值来控制空白的宽度

# 输入课程种类
tk.Label(root, text="课程种类(漫思课程输入:1,思广课程输入:2):").grid(row=0, column=0, padx=padding_x, pady=5,
                                                                     sticky="w")
class_type_var = tk.StringVar()
tk.Entry(root, textvariable=class_type_var).grid(row=0, column=1, padx=padding_x, pady=5, sticky="w")

# 课程数量和暂停秒数框架
course_pause_frame = tk.Frame(root)
course_pause_frame.grid(row=1, column=0, columnspan=2, padx=padding_x, pady=5, sticky="w")

# 输入课程个数
tk.Label(course_pause_frame, text="课程个数:").grid(row=0, column=0, padx=0, pady=0, sticky="e")
repeat_var = tk.StringVar()
tk.Entry(course_pause_frame, textvariable=repeat_var, width=10).grid(row=0, column=1, padx=33, pady=0, sticky="w")

# 输入暂停秒数
tk.Label(course_pause_frame, text="暂停秒数:").grid(row=0, column=2, padx=33, pady=0, sticky="e")
pause_var = tk.StringVar(value="0.3")
tk.Entry(course_pause_frame, textvariable=pause_var, width=10).grid(row=0, column=3, padx=5, pady=0, sticky="w")

# 输入课程日期
tk.Label(root, text="课程日期(格式:yyyy-mm-dd):").grid(row=2, column=0, padx=padding_x, pady=5, sticky="w")
date_var = tk.StringVar()
tk.Entry(root, textvariable=date_var).grid(row=2, column=1, padx=padding_x, pady=5, sticky="w")

# 输入学生id
tk.Label(root, text="学生id(四位数字):").grid(row=3, column=0, padx=padding_x, pady=5, sticky="w")
student_id_var = tk.StringVar()
tk.Entry(root, textvariable=student_id_var).grid(row=3, column=1, padx=padding_x, pady=5, sticky="w")

# 动态添加课程信息输入框
course_frame = tk.Frame(root)
course_frame.grid(row=4, column=0, columnspan=2, padx=padding_x, pady=5, sticky="w")

lab_name_entries = []
time_slot_entries = []

# 选择课程个数后生成对应的输入框
repeat_var.trace_add("write", lambda *args: add_course_fields())

# 日志输出窗口
log_text = tk.Text(root, height=10, width=56)
log_text.grid(row=5, column=0, columnspan=2, padx=padding_x, pady=5, sticky="w")

# 按钮框架
button_frame = tk.Frame(root)
button_frame.grid(row=6, column=0, columnspan=2, pady=10)

# 开始抢课按钮
tk.Button(button_frame, text="开始抢课", command=start_registration).pack(side=tk.LEFT, padx=(0, 10))

# 结束抢课按钮
tk.Button(button_frame, text="结束抢课", command=stop_registration).pack(side=tk.LEFT)

# 运行主循环
root.mainloop()
