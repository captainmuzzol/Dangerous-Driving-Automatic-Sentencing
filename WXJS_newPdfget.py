# -*- coding: utf-8 -*-
# import PyMuPDF
# from typing import final
import datetime
import os
import re

import docx
import fitz

# from docx import Document
# from docx.oxml.ns import qn
# from docx.shared import Pt
# import shutil
import ExtraDef

'''字典'''
# 实刑条例
shixing_dict = {
    1: "致使他人轻伤",
    2: "有酒驾或醉驾前科",
    3: "无证驾驶机动车",
    4: "驾驶中型以上货车"
}
# 数字转化
num_dict = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}
unit_dict = {'十': 10, '百': 100, '千': 1000, '万': 10000}

'''初值'''
global fact_start
global fact_end, lxjy_C
global N_middle_word
N_middle_word = ""
fact_start = 0
fact_end = 0
i = 0
j = 0
chengshu = 0.75  # 乘数初值
lxqk_d = 0  # 量刑日期初值
lxqk_m = 0  # 量刑月份初值
minus_date = datetime.date.today()  # 日期差初值
wj_minus_date = 30000  # 危驾日期差初值

'''函数'''


# 中文数字转阿拉伯
def atc(arab_num):
    digits = {'0': '', '1': '一', '2': '二', '3': "三", '4': '四', '5': '五', '6': '六', '7': '七', '8': '八', '9': '九'}
    units = ['', '十', '百', '千', '万']
    result = ''
    l = len(arab_num) - 1
    m = 0
    need_zero = False
    while l >= 0:
        if arab_num[l] != '0':
            result = digits[arab_num[l]] + units[m] + result
        else:
            # 如果这一位是零，则需要在数字前面加上一个零
            if not need_zero and result:
                result = '零' + result
                need_zero = True
        l -= 1
        m += 1
        # 防止过万
        if l == 5 or m == 5:
            result = units[m] + result
            m = 0
            need_zero = False
    return result


# 阿拉伯转中文数字
def cta(chinese_num):
    result = 0
    num = 0
    for k in chinese_num:
        if k in num_dict:
            num = num_dict[k]
        elif k in unit_dict:
            result += num * unit_dict[k]
            num = 0
        elif k.isdigit():
            num = num * 10 + int(k)
        else:
            pass
    result += num
    result = str(result)
    return result


'''开始量刑'''


def LX(file):
    print("newPdfget调试信息：进入LX函数")
    global fact, J_middle_word, final_result, info, extra, lxjy, lxjy_C, lxqk, chengshu
    global lxjg, N_middle_word, douhao, fact_start, fact_end
    chengshu = 0.75
    minus_date = datetime.date.today()  # 日期差初值
    wj_minus_date = 30000  # 危驾日期差初值
    lxjy = ""  # 量刑建议初值
    lxjy_C = ""
    info = ""  # 嫌疑人基本信息
    extra = ""  # 额外情节识别
    J_middle_word = 0  # 酒精含量初值
    N_middle_word = ""  # 嫌疑人姓名初值
    final_result = ""  # 第一次量刑结果
    fact = ""
    fact_start = 0
    fact_end = 0

    # 读取输出文件并拆分成自然段
    with open(file, 'r', encoding='gbk', errors='ignore') as file:
        print("newPdfget调试信息：打开文件成功")
        text = file.read()
        print("newPdfget调试信息：读取文件成功")

        # 将文本按换行符和句号拆分成自然段
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        paragraphs = [p.strip() for para in paragraphs for p in para.split('.') if p.strip()]

        # 获取息与事实段落
        for para in paragraphs:
            if para.find("经依法侦查查明") != -1:
                fact_start = paragraphs.index(para)
            if para.find("认定上述") != -1:
                fact_end = paragraphs.index(para)
        i = fact_start
        while i <= fact_end - 1:
            # fact_list.append(paragraphs[i])
            fact = fact + paragraphs[i].strip('\n')
            i += 1
        j = 0
        while j <= fact_start - 1:
            info = info + paragraphs[j].strip('\n')
            j += 1

    # 获取工作路径
    file_load = os.getcwd()

    # 查找酒精含量
    J_start_keyword = '量为'
    J_end_keyword = 'mg'
    J_middle_words = []
    # for para in paragraphs:
    if J_start_keyword in fact and J_end_keyword in fact:
        start_index = fact.find(J_start_keyword) + len(J_start_keyword)
        end_index = fact.find(J_end_keyword)
        if start_index < end_index:
            try:
                J_middle_text = fact[start_index:end_index].strip()
                # 提取两个关键词中间的词语
                J_middle_word = J_middle_text.split()[0]
                J_middle_words.append(J_middle_word)
            except BaseException:
                print("未知错误")
        else:
            pass
    else:
        pass
    # print("info:"+info)
    # 查赵嫌疑人姓名
    N_start_keyword = '犯罪嫌疑人'
    N_end_keyword = '男，'  # Windows
    # N_end_keyword = '涉嫌危险驾驶罪一案'  # Mac
    N_middle_words = []
    if N_start_keyword in info and N_end_keyword in info:
        # print("1!")
        start_index = info.find(N_start_keyword) + len(N_start_keyword)
        end_index = info.find(N_end_keyword)
        if start_index < end_index:
            # print("2!")
            N_middle_text = info[start_index:end_index].strip()
            # 提取两个关键词中间的词语
            N_middle_word = N_middle_text.split()[0]
            N_middle_words.append(N_middle_word)
        else:
            pass
    else:
        N_end_keyword = '女，'
        if N_start_keyword in info and N_end_keyword in info:
            start_index = info.find(N_start_keyword) + len(N_start_keyword)
            end_index = info.find(N_end_keyword)
            if start_index < end_index:
                N_middle_text = info[start_index:end_index].strip()
                # 提取两个关键词中间的词语
                N_middle_word = N_middle_text.split()[0]
                N_middle_words.append(N_middle_word)

    N_middle_word = N_middle_word.rstrip('，')

    # 输出结果
    douhao = "," + "，"
    final_result += '犯罪嫌疑人: ' + N_middle_word + '，' + '酒精含量为: ' + str(J_middle_word) + 'mg/100ml'
    print("newPdfget调试信息：final_result:" + final_result)
    NumGet = int(J_middle_word)
    Basic_num = "%.2f" % (NumGet / 80)
    # 量刑计算部分
    lxqk = 0  # 量刑情节（初步量刑）初值
    lxjg = 0  # 量刑结果初值
    fj = 0  # 罚金初值
    ewfjpd = 0  # 额外罚金判断初值
    shixing_attention = 0  # 实刑提示
    hx = 0  # 缓刑期初值
    moto_attention = 0  # 摩托初值
    money_attention = 0  # 损失量初值
    czqj = ""
    judge = 0

    # 前科劣迹判断
    info = ExtraDef.Rep_info(info)  # 修改info表述格式
    print("newPdfget调试信息info:" + info)
    global info_split_list
    info_split_list = (re.split('[。；]', info))  # 此处还需要split分号，分割信息部分(re.split('。|；', info))
    print("newPdfget调试信息info_split_list:" , info_split_list)
    for info_split in info_split_list:
        if info_split.startswith("2"):

            try:  # 防止公安不写“日”
                qk_date = info_split[:info_split.index("日")] + "日"
                first_date = datetime.date(int(qk_date[:info_split.index("年")]),
                                           int(cta(qk_date[info_split.index("年") + 1:info_split.index("月")])),
                                           int(cta(qk_date[
                                                   info_split.index("月") + 1:info_split.index("日")])))  # 转化为时间格式
            except:
                qk_date = info_split[:info_split.index("因")] + "日"
                first_date = datetime.date(int(qk_date[:info_split.index("年")]),
                                           int(cta(qk_date[info_split.index("年") + 1:info_split.index("月")])),
                                           int(cta(qk_date[
                                                   info_split.index("月") + 1:info_split.index("因")])))  # 转化为时间格式
            now_date = datetime.date.today()  # 获取当前时间
            minus_date = now_date - first_date  # 计算日期差
            minus_date = minus_date.days  # 转化为int类型，不然无法比较大小
            # print(minus_date)

            if info_split.find("醉") != -1 or info_split.find("饮") != -1 or info_split.find("危险驾驶") != -1:
                wj_minus_date = minus_date
                if 1800 >= minus_date >= 60 and (info_split.find("醉") != -1):
                    czqj = czqj + "g"  # 5年醉驾
                    judge = "1"
                elif 1080 >= minus_date >= 60 and info_split.find("饮") != -1:
                    czqj = czqj + "g"  # 3年醉驾
                    judge = "1"
                elif 1080 <= minus_date and info_split.find("饮") != -1:
                    judge = "1"
                    czqj = czqj + "r"  # 有关前科劣迹
                elif 1800 <= minus_date:
                    judge = "1"
                    czqj = czqj + "r"  # 有关前科劣迹
            elif minus_date >= 60:
                judge = "1"
                czqj = czqj + "q"  # 无关前科劣迹

    # print(czqj)

    '''数据传递 额外情节识别'''
    if fact.find("事故") != -1 and fact.find("两车") != -1:  # 撞车事故
        judge = "1"
        czqj = czqj + "f"
    if fact.find("交通事故") != -1 and fact.find("发生碰撞") != -1:  # 撞车事故
        judge = "1"
        czqj = czqj + "f"
    if fact.find("受伤") != -1 and not fact.find("轻伤") != -1:  # 一般受伤
        czqj = czqj + "d"
    if fact.find("摩托") != -1 or fact.find("二轮") != -1:  # 摩托车    暂无法使用
        judge = "1"
        czqj = czqj + "4"
        moto_attention = 1
        final_result += '\n' + "对不起，摩托车相关案件暂时无法量刑，请关闭程序。"
        # exit()
    if fact.find("无有效机动车") != -1 or fact.find("无证") != -1 or fact.find("扣留期间") != -1:    # 无证驾驶
        judge = "1"
        czqj = czqj + "h"
    if fact.find("牌照") != -1 or fact.find("无牌") != -1:  # 无证驾驶
        judge = "1"
        czqj = czqj + "m"
    if fact.find("轻伤") != -1 or fact.find("轻伤") != -1:  # 轻伤
        judge = "1"
        czqj = czqj + "m"
    if fact.find("营运") != -1 or fact.find("营运") != -1:  # 营运
        judge = "1"
        czqj = czqj + "m"
    if fact.find("驾车逃离") != -1 or fact.find("逃离") != -1:  # 事故后逃离现场
        judge = "1"
        czqj = czqj + "c"

    # 如果只有事故没有人受伤，且酒精含量小于170，可不起诉
    czqj_cant_do = ['q', 'f', 'qf']
    if czqj.rstrip('0123456789') in czqj_cant_do and int(J_middle_word) <= 150 and not fact.find("伤") != -1:
        judge = "0"

    jishu = float(Basic_num)
    '''量刑规范'''
    if jishu * 0.75 <= 0.8:
        final_result += '\n' + "酒精含量低于最小值，请确认是否正确。"
    if jishu * 0.75 == jishu * 0.75 <= 1.2:
        lxqk_m = 1
        lxqk_d = 0
    elif jishu * 0.75 <= 1.4:
        lxqk_m = 1
        lxqk_d = 10
    elif jishu * 0.75 <= 1.6:
        lxqk_m = 1
        lxqk_d = 15
    elif jishu * 0.75 <= 1.8:
        lxqk_m = 1
        lxqk_d = 20
    elif jishu * 0.75 <= 2.2:
        lxqk_m = 2
        lxqk_d = 0
    elif jishu * 0.75 <= 2.4:
        lxqk_m = 2
        lxqk_d = 10
    elif jishu * 0.75 <= 2.6:
        lxqk_m = 2
        lxqk_d = 15
    elif jishu * 0.75 <= 2.8:
        lxqk_m = 2
        lxqk_d = 20
    elif jishu * 0.75 <= 3.2:
        lxqk_m = 3
        lxqk_d = 0
    elif jishu * 0.75 <= 3.4:
        lxqk_m = 3
        lxqk_d = 10
    elif jishu * 0.75 <= 3.6:
        lxqk_m = 3
        lxqk_d = 15
    elif jishu * 0.75 <= 3.8:
        lxqk_m = 3
        lxqk_d = 20
    elif jishu * 0.75 <= 4.2:
        lxqk_m = 4
        lxqk_d = 0
    elif jishu * 0.75 <= 4.4:
        lxqk_m = 4
        lxqk_d = 10
    elif jishu * 0.75 <= 4.6:
        lxqk_m = 4
        lxqk_d = 15

    '''缓刑期计算'''
    if jishu * 0.75 <= 1.4:
        hx = 2
    elif jishu * 0.75 < 2:
        hx = 3
    elif 2 <= jishu * 0.75 <= 2.6:
        hx = 4
    elif 2.6 < jishu * 0.75 <= 3.2:
        hx = 5
    elif 3.2 < jishu * 0.75 <= 3.8:
        hx = 6

    print('newPdfget调试信息czqj:', czqj)
    if czqj == "":  # 设卡（无额外情节）
        final_result += '\n' + "未识别到任何额外情节。"
        if jishu * 0.75 <= 1.593:
            lxjy = "相对不起诉"
            lxjy_C = "相对不起诉"
            final_result += '\n' + '\n' + '    ▶>>>建议量刑：可考虑做不起诉处理<<<◀' + '\n'
        else:
            fj = int(fj) + lxqk_m * 2000
            fj = int(fj)
            if lxqk_d > 0:
                fj = fj + (lxqk_d - 5) / 5 * 500
                fj = int(fj)
            lxjy = str(lxqk_m) + '个月' + str(lxqk_d) + '天，缓刑' + str(hx) + '个月，并处罚金人民币' + str(fj) + '元'
            lxjy_C = atc(str(lxqk_m)) + '个月' + atc(str(lxqk_d)) + '天，缓刑' + atc(str(hx)) + '个月，并处罚金人民币' + atc(
                str(fj)) + '元'
            final_result += '\n' + '     ▶>>>建议量刑：' + str(lxqk_m) + '个月' + str(lxqk_d) + '天，缓刑' + str(
                hx) + '个月，并处罚金人民币' + str(fj) + '元<<<◀'
            final_result += '\n' + '本结果仅供参考，请结合实际情况量刑'
    else:  # 非设卡（有额外情节）
        hx = 0  # 避免反复加缓刑
        fj = 0
        # czqj = "0"    #检验用
        if czqj.find('a') != -1:  # 自撞
            chengshu += 0.05
            lxjg = int(lxjg) + 5
            money_attention = 1  # 判断损失量
            extra += "自撞；"
        if czqj.find('b') != -1:  # 自撞后逃离现场
            chengshu += 0.05
            lxjg = int(lxjg) + 5
            extra += "自撞后逃离；"
        if czqj.find('c') != -1:  # 造成他人受伤或损失后逃逸/轻微抗拒执法
            chengshu += 0.1
            lxjg = int(lxjg) + 10
            extra += "造成他人受伤或损失后逃逸/轻微抗拒执法；"
        if czqj.find('d') != -1:  # 对他人造成一般伤势
            lxjg = int(lxjg) + 15
            extra += "对他人造成一般伤势；"
        if czqj.find('e') != -1:  # 造成他人轻伤
            jishu += 1
            lxjg = int(lxjg) + 20
            shixing_attention = 1
            extra += "造成他人轻伤；"
        if czqj.find('f') != -1:  # 损坏他人/公共财物
            chengshu += 0.1
            lxjg = int(lxjg) + 15
            money_attention = 1  # 判断损失量
            extra += "损坏他人财物；"
        if czqj.find('g') != -1:  # 有三年酒驾、五年醉驾情节
            jishu += 1
            lxjg = int(lxjg) + 20
            shixing_attention = 2
            extra += "有三年酒驾、五年醉驾情节；"
        if czqj.find('h') != -1:  # 无证驾驶
            print('newPdfget调试信息：find_h成功')
            print('wj_minus_date', wj_minus_date)
            # print(wj_minus_date)
            if wj_minus_date < 1800:
                jishu += 0.5
            else:
                jishu += 1
            lxjg = int(lxjg) + 20
            shixing_attention = 3
            extra += "无证驾驶；"
        if czqj.find('i') != -1:  # 校车业务/营运车辆（旅客运输、危险化学品运输）
            jishu += 1
            lxjg = int(lxjg) + 20
            ewfjpd = int(ewfjpd) + 1
            extra += "校车业务/营运车辆（旅客运输、危险化学品运输）；"
        if czqj.find('j') != -1:  # 营运车辆（货物运输，不含旅客）
            jishu += 1
            lxjg = int(lxjg) + 20
            extra += "营运车辆（货物运输，不含旅客）；"
        if czqj.find('k') != -1:  # 取保候审期间再次醉酒驾驶
            jishu += 2
            lxjg = int(lxjg) + 40
            extra += "取保候审期间再次醉酒驾驶；"
        if czqj.find('m') != -1:  # 无牌上路
            jishu += 1
            lxjg = int(lxjg) + 20
            extra += "无牌上路；"
        if czqj.find('n') != -1:  # 中型以上机动车(和营运车辆不重复选择）
            jishu += 2
            lxjg = int(lxjg) + 40
            shixing_attention = 4
            extra += "中型以上机动车；"
        if czqj.find('o') != -1:  # 在高速公路上行驶
            jishu += 1
            lxjg = int(lxjg) + 20
            extra += "高速公路行驶；"
        if czqj.find('p') != -1:  # 严重超员、超载、超速驾驶
            jishu += 1
            lxjg = int(lxjg) + 20
            extra += "严重超员、超载、超速驾驶；"
        if czqj.find('q') != -1:  # 与危驾无关的前科劣迹
            chengshu += 0.05
            lxjg = int(lxjg) + 5
            extra += "与危驾无关的前科劣迹；"
        if czqj.find('r') != -1:  # 与危驾有关的前科劣迹
            chengshu += 0.05
            lxjg = int(lxjg) + 5
            extra += "与危驾有关的前科劣迹；"
        if czqj.find('1') != -1:  # 自首（明知他人报警不逃离现场）
            chengshu -= 0.05
            lxjg = int(lxjg) - 5
            extra += "自首；"
        if czqj.find('2') != -1:  # 取得谅解未赔偿
            chengshu -= 0.05
            lxjg = int(lxjg) - 5
            extra += "取得谅解未赔偿；"
        if czqj.find('3') != -1:  # 赔偿并取得谅解
            chengshu -= 0.1
            lxjg = int(lxjg) - 10
            extra += "赔偿并取得谅解；"
        if czqj.find('4') != -1:  # 驾驶摩托车
            chengshu -= 0.3
            lxjg = int(lxjg) - 30
            moto_attention = 1  # 判断摩托提示
            extra += "驾驶摩托车；"
        # 避免乘数增减过高过低
        if chengshu <= 0.6:
            chengshu = 0.6
        elif chengshu >= 1:
            chengshu = 1

        # 刑期计算
        # print(str(jishu) + '\n' + str(chengshu))
        jishu = jishu * chengshu
        jishu = round(jishu, 1)

        '''量刑规范'''
        if jishu <= 0.8:
            final_result += '\n' + '该酒精含量低于最低量刑标准'
        if jishu == jishu <= 1.2:
            lxqk_m = 1
            lxqk_d = 0
        elif jishu <= 1.4:
            lxqk_m = 1
            lxqk_d = 10
        elif jishu <= 1.6:
            lxqk_m = 1
            lxqk_d = 15
        elif jishu <= 1.8:
            lxqk_m = 1
            lxqk_d = 20
        elif jishu <= 2.2:
            lxqk_m = 2
            lxqk_d = 0
        elif jishu <= 2.4:
            lxqk_m = 2
            lxqk_d = 10
        elif jishu <= 2.6:
            lxqk_m = 2
            lxqk_d = 15
        elif jishu <= 2.8:
            lxqk_m = 2
            lxqk_d = 20
        elif jishu <= 3.2:
            lxqk_m = 3
            lxqk_d = 0
        elif jishu <= 3.4:
            lxqk_m = 3
            lxqk_d = 10
        elif jishu <= 3.6:
            lxqk_m = 3
            lxqk_d = 15
        elif jishu <= 3.8:
            lxqk_m = 3
            lxqk_d = 20
        elif jishu <= 4.2:
            lxqk_m = 4
            lxqk_d = 0
        elif jishu <= 4.4:
            lxqk_m = 4
            lxqk_d = 10
        elif jishu <= 4.6:
            lxqk_m = 4
            lxqk_d = 15
        elif jishu > 4.6:
            final_result += '\n' + '超出最大值'

        '''缓刑期计算'''
        if jishu <= 1.4:
            hx = hx + 2
        elif jishu < 2:
            hx = hx + 3
        elif 2 <= jishu <= 2.6:
            hx = hx + 4
        elif 2.6 < jishu <= 3.2:
            hx = hx + 5

        if extra != "":
            if len(extra) <= 33:
                final_result += '\n' + ("识别到情节：" + extra)
            else:
                extra = extra[0:33] + '\n' + extra[33:]
                final_result += '\n' + ("识别到情节：" + extra)
        else:
            final_result += '\n' + ("未识别到任何额外情节。")

        '''完善月份日期显示'''
        # lxqk_d = int(lxqk_d) + lxjg   # 加法计算刑期

        if lxqk_d < 0:
            lxqk_m = int(lxqk_m) - 1
            lxqk_d = 30 + lxqk_d
        elif 60 > lxqk_d >= 30:
            lxqk_d = lxqk_d - 30
            lxqk_m = int(lxqk_m) + 1
        elif 90 > lxqk_d >= 60:
            lxqk_d = lxqk_d - 60
            lxqk_m = int(lxqk_m) + 2
        elif 120 > lxqk_d >= 90:
            lxqk_d = lxqk_d - 90
            lxqk_m = int(lxqk_m) + 3
        elif 150 > lxqk_d >= 120:
            lxqk_d = lxqk_d - 120
            lxqk_m = int(lxqk_m) + 4
        elif 180 > lxqk_d >= 150:
            lxqk_d = lxqk_d - 150
            lxqk_m = int(lxqk_m) + 5
        elif 210 > lxqk_d >= 180:
            lxqk_d = lxqk_d - 180
            lxqk_m = int(lxqk_m) + 6

        # 去除5、25天的量刑情况
        extra_no_num = extra.rstrip('0123456789')  # 去除减刑项
        if lxqk_d == 5:
            if len(extra_no_num) >= 2:
                lxqk_d += 5
            else:
                lxqk_d -= 5
        elif lxqk_d == 25:
            if len(extra_no_num) >= 2:
                lxqk_d += 5
                lxqk_m += 1
            else:
                lxqk_d -= 5

        '''罚金计算'''
        if ewfjpd == 0:  # 没有额外罚金的情况
            fj = int(fj) + lxqk_m * 2000
            if lxqk_d > 0:
                fj = fj + (lxqk_d - 5) / 5 * 500
        else:  # 有额外罚金的情况（营运等）
            fj = int(fj) + lxqk_m * 5000
            if lxqk_d > 0:
                fj = fj + (lxqk_d - 5) / 5 * 1250
        fj = int(fj)
        '''额外缓刑计算'''
        if lxqk_d >= 20 and lxqk_m * 2 >= hx:
            hx = hx + 1
        if lxqk_m == 2 and lxqk_d == 0 and jishu < 2.75:
            hx = 3
        # 如果前科过多，则增加缓刑期限
        if czqj.count("q") >= 3 and lxqk_m == 2 and hx == 3:
            hx += 1

        '''量刑输出'''
        if shixing_attention == 0:  # 没有上述的实刑条件时
            if int(judge) == 0:
                lxjy = "相对不起诉"
                lxjy_C = "相对不起诉"
                final_result += '\n' + '     ▶>>>建议量刑：可考虑做不起诉处理<<<◀'
            else:
                fj = int(fj)
                lxjy = str(lxqk_m) + '个月' + str(lxqk_d) + '天，缓刑' + str(hx) + '个月，并处罚金人民币' + str(fj) + '元'
                lxjy_C = atc(str(lxqk_m)) + '个月' + atc(str(lxqk_d)) + '天，缓刑' + atc(str(hx)) + '个月，并处罚金人民币' + atc(
                    str(fj)) + '元'
                final_result += '\n' + '     ▶>>>建议量刑：' + str(lxqk_m) + '个月' + str(lxqk_d) + '天，缓刑' + str(
                    hx) + '个月，并处罚金人民币' + str(fj) + '元<<<◀''\n'
        else:  # 包含上述的实刑条件时
            fj = int(fj)
            lxjy = str(lxqk_m) + '个月' + str(lxqk_d) + '天，并处罚金人民币' + str(fj) + '元'
            lxjy_C = atc(str(lxqk_m)) + '个月' + atc(str(lxqk_d)) + '天，缓刑' + atc(str(hx)) + '个月，并处罚金人民币' + atc(
                str(fj)) + '元'
            final_result += '\n' + '      ▶>>>建议量刑：' + str(lxqk_m) + '个月' + str(lxqk_d) + '天' + ',并处罚金人民币' + str(
                fj) + '元<<<◀''\n'
            final_result += '\n' + '注意：因其' + shixing_dict[shixing_attention] + '，建议不做缓刑处理'
        if money_attention == 1:  # 判断损失量
            final_result += '\n' + ' 如造成较大金额损失（如>十万元）,可适当增加刑期。如已赔偿谅解，可适当减少刑期。''\n'
        if moto_attention == 1:
            final_result += '\n' + '如果是驾驶摩托且酒精含量<200、认罪悔罪时，可考虑不起诉处理，其他情况也可考虑缓刑'

        if czqj.find("4") != -1:
            final_result = '    ▶>>>十分抱歉，摩托车因为量刑较为复杂，暂不支持自动生成，请尝试手动！<<<◀'
        final_result += '\n' + ' 软件获取信息有限！结果仅供参考，请点击左下角手动量刑！'
    # 先创建原来的量刑建议
    '''
    print('file_load', file_load)
    LX_file = file_load + '/模板/LX_change.txt'
    print('lxjy',lxjy)
    with open(LX_file, 'w', encoding='gbk') as LX_file2:
        LX_file2.write(lxjy)
    '''
    return final_result

# print(LX('/Users/xumuzhi/coding/pdfGet/起诉意见书.pdf'))         # Mac
# print(LX(r'C:\Users\Administrator\Desktop\测试用起诉意见书\起诉意见书 (1).pdf'))  # windows
# print(LX('output.txt'))  # windows
