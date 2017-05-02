from pymongo import MongoClient

conn = MongoClient("10.8.8.111:27017")

chapters = conn["onions"]["chapters"]
themes = conn["onions"]["themes"]
topics = conn["onions"]["topics"]
mrjing = conn["ronfedb"]["mrjing"]


def reduce_list(x):
    return set([item for sublist in x for item in sublist])


def get_value(goal_doc, field):
    result = list()
    if field[-2:] == "pv":
        result = 0
    if field in goal_doc:
        result = goal_doc[field]
    return result


def get_first_page_data(topic_list, startDate, endDate):
    pipeline = [
        {"$match": {
            "topicId": {"$in": topic_list},
            "date": {"$gte": startDate, "$lte": endDate}
        }},
        {"$group": {
            "_id": "$topicId",
            "clickThemeTopic_pv": {"$sum": "$clickThemeTopic_pv"},
            "clickThemeTopic_uv": {"$push": "$clickThemeTopic_uv"},
            "startVideo_pv": {"$sum": "$startVideo_pv"},
            "startVideo_uv": {"$push": "$startVideo_uv"},
            "startPractice_pv": {"$sum": "$startPractice_pv"},
            "startPractice_uv": {"$push": "$startPractice_uv"},
        }}
    ]
    x = mrjing.aggregate(pipeline, allowDiskUse=True)
    result = list()
    for row in x:
        y = topics.find_one(row["_id"])
        topic_name = y["name"]
        temp_json = {
            "topicId": str(row["_id"]),
            "topicName": topic_name,
            "topicType": y["type"],
            "topicPayable": y["pay"],
            "startTopic": {
                "pv": row["clickThemeTopic_pv"],
                "uv": len(reduce_list(row["clickThemeTopic_uv"]))
            },
            "startVideo": {
                "pv": row["startVideo_pv"],
                "uv": len(reduce_list(row["startVideo_uv"]))
            },
            "startPractice": {
                "pv": row["startPractice_pv"],
                "uv": len(reduce_list(row["startPractice_uv"]))
            }
        }
        result.append(temp_json)
    return result

