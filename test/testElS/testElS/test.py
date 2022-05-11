for id in json_file:
    menus = list()
    prices = list()
    # print(id['s_menu'])
    try:
        if id['s_menu'] != None:
            for menu in id['s_menu']:
                key = list(menu.keys())
                menus.append(key[0])
                prices.append(menu[key[0]])
    except KeyError:
        pass
    except AttributeError:
        menus = id['s_menu']
        prices = id['s_price']
    id_int = int(id['id'])
    try:
        if file_name == 'dining' or file_name == 'naver':
            str_expr = f'total_id == {id_int}'
            df_q = csv_text.query(str_expr)
            id_int = int(df_q.iloc[0]['s_id'])
            print(df_q.iloc[0]['s_id'], id['s_name'])
    except IndexError:
        continue
    # print(id_int, id['s_name'])
    id_di = result[id_int]
    id_di['id'] = id_int
    try:
        if file_name == 'dining':
            if id['s_tel'] != None:
                id_di['s_name'] = id['s_name']
        else:
            id_di['s_name'] = id['s_name']
    except KeyError:
        id_di['s_name'] = None
    try:
        id_di['s_tel'] = id['s_tel']
    except KeyError:
        id_di['s_tel'] = None
    try:
        id_di['s_etc'] = id['s_etc']
    except KeyError:
        id_di['s_etc'] = None
    try:
        id_di['s_hour'] = id['s_hour']
    except KeyError:
        id_di['s_hour'] = None
    try:
        content_dict = dict()
        content_dict['content'] = id['s_photo']
        id_di['s_photo'] = content_dict
    except KeyError:
        id_di['s_photo'] = None
    if len(menus) != 0:
        menu_dict, prices_dict = dict(), dict()
        menu_dict['content'] = menus
        prices_dict['content'] = prices
        id_di['s_menu'] = menu_dict
        id_di['s_price'] = prices_dict
    else:
        id_di['s_menu'] = None
        id_di['s_price'] = None