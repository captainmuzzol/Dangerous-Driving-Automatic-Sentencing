import fitz


def get_bookmarks_2(pdf_path):
    global result, page_split
    result = []
    with fitz.open(pdf_path) as doc:
        outlines = doc.get_toc()
        for outline in outlines:
            result.append(outline[1])
            result.append(str(outline[2] + 1))
    '''获取目录页码'''

    def searchMarks(result, search_term):
        i = 0
        get_index = 0
        for index, title in enumerate(result):
            if search_term in title:
                get_index = index
                break
        # 提取目标项后页码数
        pages = []
        for i in range(get_index, len(result) - 1):
            if '第' in result[i]:
                pages.append(result[i])
                if i + 2 < len(result):
                    if result[i + 1].isdigit() and not ('第' in result[i + 2]):
                        break
                else:
                    pages.append(result[i])
        search_list = [s.replace('第', '').replace('页', '') for s in pages]
        search_pages = search_list[0] + '~' + search_list[-1]
        return search_pages

    '''获取目录页码，以便使得页码为实际页码（通过减去目录页数+1)'''
    mulu = int(searchMarks(result, '目录')[-1])

    def true_page(page):
        page_get = page.split('~')
        page_start = int(page_get[0])
        page_end = int(page_get[-1])
        if page_start <= 0 or page_end <= 0:
            return '未找到该项'
        if page_start == page_end:
            return 'P' + str(page_start)
        else:
            return 'P' + str(page_start) + '-P' + str(page_end)

    '''开始获取各项页码'''
    # page1 = searchMarks(result, '物证')
    page1 = true_page(searchMarks(result, '讯问笔录'))
    page2 = true_page(searchMarks(result, '归案经过'))
    page3 = true_page(searchMarks(result, '户籍资料'))
    page4 = true_page(searchMarks(result, '现场酒精呼气'))
    page5 = true_page(searchMarks(result, '交通管理强制措施'))
    page6 = true_page(searchMarks(result, '提取血样登记表'))
    page7 = true_page(searchMarks(result, '车辆信息'))
    page8 = true_page(searchMarks(result, '驾驶证'))
    page9 = true_page(searchMarks(result, '情况说明'))
    page10 = true_page(searchMarks(result, '现场照片'))
    page11 = true_page(searchMarks(result, '物证（照片）'))
    page12 = true_page(searchMarks(result, '认罪认罚承诺书'))
    page13 = true_page(searchMarks(result, '情况记录表'))
    page14 = true_page(searchMarks(result, '检验鉴定'))
    page15 = true_page(searchMarks(result, '责任认定'))
    page16 = true_page(searchMarks(result, '谅解'))
    page17 = true_page(searchMarks(result, '询问笔录'))
    page18 = true_page(searchMarks(result, '车辆检验鉴定'))

    final_pages_get = page1 + ',' + page2 + ',' + page3 + ',' + page4 + ',' + page5 + ',' + page6 + ',' + page7 + ',' + page8 + ',' + page9 + ',' + page10 + ',' + page11 + ',' + page12 + ',' + page13 + ',' + page14 + ',' + page15 + ',' + page16 + ',' + page17 + ',' + page18
    final_pages = final_pages_get.split(',')
    return final_pages



def get_bookmarks(pdf_path):
    global result, page_split
    result = []
    with fitz.open(pdf_path) as doc:
        outlines = doc.get_toc()
        for outline in outlines:
            result.append(outline[1])
            result.append(str(outline[2] + 1))
    '''获取目录页码'''

    def searchMarks(result, search_term):
        i = 0
        get_index = 0
        for index, title in enumerate(result):
            if search_term in title:
                get_index = index
                break
        # 提取目标项后页码数
        pages = []
        for i in range(get_index, len(result) - 1):
            if '第' in result[i]:
                pages.append(result[i])
                if i + 2 < len(result):
                    if result[i + 1].isdigit() and not ('第' in result[i + 2]):
                        break
                else:
                    pages.append(result[i])
        search_list = [s.replace('第', '').replace('页', '') for s in pages]
        search_pages = search_list[0] + '~' + search_list[-1]
        return search_pages

    '''获取目录页码，以便使得页码为实际页码（通过减去目录页数+1)'''
    mulu = int(searchMarks(result, '目录')[-1])

    def true_page(page):
        page_get = page.split('~')
        page_start = int(page_get[0]) - mulu
        page_end = int(page_get[-1]) - mulu
        if page_start <= 0 or page_end <= 0:
            return '未找到该项'
        if page_start == page_end:
            return 'P' + str(page_start)
        else:
            return 'P' + str(page_start) + '-P' + str(page_end)

    '''开始获取各项页码'''
    # page1 = searchMarks(result, '物证')
    page1 = true_page(searchMarks(result, '讯问笔录'))
    page2 = true_page(searchMarks(result, '归案经过'))
    page3 = true_page(searchMarks(result, '户籍资料'))
    page4 = true_page(searchMarks(result, '现场酒精呼气'))
    page5 = true_page(searchMarks(result, '交通管理强制措施'))
    page6 = true_page(searchMarks(result, '提取血样登记表'))
    page7 = true_page(searchMarks(result, '车辆信息'))
    page8 = true_page(searchMarks(result, '驾驶证'))
    page9 = true_page(searchMarks(result, '情况说明'))
    page10 = true_page(searchMarks(result, '现场照片'))
    page11 = true_page(searchMarks(result, '物证（照片）'))
    page12 = true_page(searchMarks(result, '认罪认罚承诺书'))
    page13 = true_page(searchMarks(result, '情况记录表'))
    page14 = true_page(searchMarks(result, '检验鉴定'))

    final_pages_get = page1 + ',' + page2 + ',' + page3 + ',' + page4 + ',' + page5 + ',' + page6 + ',' + page7 + ',' + page8 + ',' + page9 + ',' + page10 + ',' + page11 + ',' + page12 + ',' + page13 + ',' + page14
    final_pages = final_pages_get.split(',')
    return final_pages


