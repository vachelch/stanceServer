from opinionManager import OpinionManager

if __name__ == "__main__":

    keyword = '年金改革'
    num_news = 50

    manager = OpinionManager(db_path='./OpinionDB/opinion.db')

    json_data = manager.retrieve(keyword,num_news)

    pie_chart_data, line_chart_data = manager.convert_to_chart_data(json_data)

    import pdb; pdb.set_trace()
