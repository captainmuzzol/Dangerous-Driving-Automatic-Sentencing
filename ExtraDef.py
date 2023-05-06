# coding=utf-8
import re


# 信息格式改写
def Rep_info(info):
    if info.find("居民身份证") != -1:
        info = info.replace("居民身份证", "公民身份证")
    else:
        info = info.replace("身份证", "公民身份证")
    if info.find("暂住") != -1:
        info = info.replace("暂住", "现住")
    if info.find("，住") != -1:
        info = info.replace("，住", "，户籍所在地：")
    return info


# 强制措施情况截取
def catch(info):
    info_catch = ""
    info_new = ""
    start = "涉嫌危险驾驶"
    end = "。我局"
    i = 0
    info_splits = info.split("。")
    for info_split in info_splits:
        if not (info_split.find("工作") != -1 or (info_split.find("归案") != -1) or (info_split.find("一案") != -1)):
            info_new += info_split + "。"
    # 句首没有涉嫌危险驾驶罪的情况：
    index = info_new.find("涉嫌危险驾驶")
    if index != -1 and index + len("涉嫌危险驾驶") < len(info_new):
        if info_new[index + len("涉嫌危险驾驶")] != "于":
            start = "202"
        else:
            pass
    else:
        pass
    # end公安没写句号的情况
    if not info_new.find("。我局") != -1:
        end = "。。"
    else:
        pass
    # print(info_new)
    if (start and end) in info_new:
        for i in range(info_new.index(start), info_new.index(end)):
            info_catch = info_catch + info_new[i]
            i += 1
    else:
        info_catch = "start or end not in info"
    if "我局" in info_catch:
        info_catch = info_catch.replace("我局", "温岭市公安局")
    else:
        print("未找到”我局“")
    # print(info_catch)
    return info_catch + "。"


# fact = '经依法侦查查明：2023年2月17日20时27分许，犯罪嫌疑人毛文君酒后驾驶浙JDK3922号小型轿车，途经林石线27km+300m' \
# '即温岭市石塘镇钢毅机械厂前路段，被执勤民警当场查获。经温岭市公安司法鉴定中心鉴定，犯罪嫌疑人毛文君的血液中检出乙醇成份，乙醇含量为150mg/100ml。 '

# 第一人称事实
def human_fact(fact, name):
    fact_human = ''
    if fact.find('经依法侦查查明：') != -1:
        fact_human = fact.replace('经依法侦查查明：', "")
        # if fact.find('根据第331081420230001692号道路交通事故认定书，') != -1:
        #    fact_human = fact.replace('根据第331081420230001692号道路交通事故认定书，', "")
        # if fact.find('根据第331081420230001691号道路交通事故认定书，') != -1:
        #    fact_human = fact.replace('根据第331081420230001691号道路交通事故认定书，', "")
        fact_human = fact_human.replace("犯罪嫌疑人", "")
        fact_human = fact_human.replace(name, "我")
    else:
        fact_human = fact.replace("犯罪嫌疑人", "")
        fact_human = fact_human.replace(name, "我")
    return fact_human


# 归案地点
def place_fact(fact):
    fact_place = ''
    start = "途经"
    end = "路段"
    if fact.find("路口") != -1 and "路口" < "途经":
        end = "路口"
    i = 0
    if start and end in fact:
        if start > end:
            for i in range(fact.index(start), fact.index(end)):
                fact_place = fact_place + fact[i]
                i += 1
        else:
            fact_place = "start not < end"
    else:
        fact_place = "start or end not in info"
    return fact_place


# 归案时间
def time_fact(fact):
    fact_no_head = fact.lstrip('经依法侦查查明：')
    if (fact_no_head.find("分") != -1) or (fact_no_head.find("日") != -1):
        try:  # 防止公安不写“分”
            time = fact_no_head[:fact_no_head.index("分")] + "分"
        except:
            time = fact_no_head[:fact_no_head.index("日")] + "日"
    return time


# 身份证号码提取
def id_get(info):
    info = info.replace(',', '，')  # 英文逗号替换为中文
    info = info.replace(':', '：')  # 英文逗号替换为中文
    start_index = info.find("身份证号码：")
    end_index = info.find('，', start_index)
    id_number = info[start_index:end_index]
    id_number = re.search(r"\d{17}[\dXx]|\d{18}", id_number).group()
    return id_number


# 提取户籍所在地
def place_get(info):
    info = info.replace(',', '，')  # 英文逗号替换为中文
    info = info.replace('，', '。')  # 英文逗号替换为中文
    place = '未找到户籍所在地'
    place_now = ''
    info_splits = []
    info_splits = info.split('。')
    for info_split in info_splits:
        if info_split.startswith('户籍所在地：'):
            place = info_split
        if info_split.startswith('现住'):
            place_now = info_split
    place += place_now
    return place
