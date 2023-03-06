# coding=utf-8
def catch(info):
    info_catch = ""
    start = "因涉嫌危险驾驶罪"
    end = "。犯罪嫌疑人"
    i = 0
    if start and end in info:
        if start > end:
            for i in range(info.index(start), info.index(end)):
                info_catch = info_catch + info[i]
                i += 1
        else:
            info_catch = "start not < end"
    else:
        info_catch = "start or end not in info"
    if "我局" in info_catch:
        info_catch = info_catch.replace("我局", "XX市公安局")
    else:
        print("不包含‘我局‘")
    return info_catch


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


def place_fact(fact):
    fact_place = ''
    start = "途经"
    end = "路段"
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


def time_fact(fact):
    fact_no_head = fact.lstrip('经依法侦查查明：')
    try:  # 防止公安不写“分”
        time = fact_no_head[:fact_no_head.index("分")] + "分"
    except:
        time = fact_no_head[:fact_no_head.index("日")] + "日"
    return time
