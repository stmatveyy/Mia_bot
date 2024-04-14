from database.database_func import Database
from datetime import datetime

async def get_todays_schedule(database:Database) -> any:
    int_to_date = {1:'mon',
                2:'tue',
                3:'wen',
                4:'thu',
                5:'fri',
                6:'sat',
                7:'sun'}

    curr_weekday = int_to_date[datetime.now().isoweekday()]
    curr_week_num = datetime.now().date().isocalendar()[1]
    week_to_select = ''
    if curr_week_num % 2 == 0:
        week_to_select = 'public.schedule_uneven'
    else:
        week_to_select = 'public.schedule_even'
    
    if curr_weekday == 'sat' or curr_weekday == 'sun':
        return 'Сегодня выходной!'
    else:
        data = await database.view(query=f'''
    SELECT {curr_weekday} FROM "{week_to_select}"''')
        fin_list= []
        for i in range(len(data)):
            try:
                fin_list.append(data[i][0] + "\n")
            except TypeError:
                pass
        return ''.join(fin_list)
