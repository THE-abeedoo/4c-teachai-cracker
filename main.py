import time
import requests
repeat = int(input("输入你想要选择的课程个数: "))
date = input("请输入课程日期：格式:yyyy-mm-dd: ")
student_id = input("请输入学生id(即teachai 账户id)，四位数字: ")
lab_names = []
time_slots = []
for x in range(repeat):
    lab_names.append(input("请输入教室号，例如：404: "))
    time_slots.append(input("请输入场次，例如：场次十三 :"))

while 1:
    time.sleep(0.3)
    url = "https://www.youkehulian.com/teachaicms/laboratorySessionMapping/getLaboratorySession"
    json_data = {"userId":student_id,"laboratoryType":1,"studentId":student_id,"startDate":date,"sessionsDictId":[]}

    response = requests.post(url, json=json_data)
    data = response.json()
    if data["code"] == 0:
        data = data["data"]
        print("已开始抢票")
    else:
        print("未开始抢票")
        continue
        # sys.exit()
    for a in range(len(lab_names)):
        class_id = None
        for x in data:
            if lab_names[a] in x["laboratoryName"] and time_slots[a] in x["timeSlot"]:
                print("正在查找："+lab_names[a]+" "+time_slots[a])
                class_id = x["id"]

        if class_id == None:
            print("未找到你的课程！")
        else:
            tick_url = "https://www.youkehulian.com/teachaicms/laboratoryUserMapping/registration"
            tick_json_data = {"userId": student_id, "studentId": student_id, "laboratorySessionId": class_id}
            response = requests.post(tick_url, json=tick_json_data)
            print(response.text)
    break