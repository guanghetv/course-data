from pymongo import MongoClient
from collections import defaultdict
from bson.objectid import ObjectId
import datetime


def get_conn(path="10.8.8.22:27017"):
    return MongoClient(path)


def get_topicid_by_video(video_id, video_topics):
    if isinstance(video_id, str):
        video_id = ObjectId(video_id)
    if video_id in video_topics:
        return video_topics[video_id]

    return None


def get_daily_stat(date_str):

    conn = get_conn("10.8.8.111:27017")
    mrjing = conn["eventsV4"]["eventV4"]
    output = conn["ronfedb"]["mrjing"]

    start = datetime.datetime.strptime(date_str, "%Y%m%d")
    end = start + datetime.timedelta(days=1)

    video_topics = dict()

    topics = conn["onions"]["topics"]

    for doc in topics.find({"hyperVideo": {"$exists": True}}, {"hyperVideo": 1}):
        video_topics["hyperVideo"] = str(doc["_id"])

    query = {
        "eventKey": {"$in": [
            "clickThemeTopic",
            "enterVideo",
            "startVideo",
            "clickVideoExit",
            "finishVideo",
            "startPractice",
            "clickProblemSubmit",
            "clickProblemExit",
            "enterPracticeFailure",
            "enterTopicFinish"
        ]},
        "serverTime": {"$gte": start, "$lt": end},
        "platform": "app",
        "user": {"$exists": True}
    }
    x = mrjing.find(query, {"eventKey": 1, "topicId": 1, "videoId": 1, "user": 1, "correct": 1, "layerIndex": 1})

    topic_pv = dict()
    topic_uv = dict()
    layer_pv = dict()
    for doc in x:
        if "topicId" not in doc:
            if "videoId" in doc:
                topic_id = get_topicid_by_video(doc["videoId"], video_topics)
                if topic_id is None:
                    continue
            else:
                continue
        else:
            topic_id = doc["topicId"]
        if topic_id not in topic_pv:
            topic_pv[topic_id] = defaultdict(int)
            topic_uv[topic_id] = defaultdict(set)
            layer_pv[topic_id] = dict()

        topic_pv[topic_id][doc["eventKey"]] += 1
        topic_uv[topic_id][doc["eventKey"]].add(doc["user"])
        if doc["eventKey"] == "clickProblemSubmit" and "correct" in doc:
            if "layerIndex" not in doc:
                print("here")
                continue
            if "layerIndex" in doc and int(doc["layerIndex"]) not in layer_pv[topic_id]:
                layer_pv[topic_id][int(doc["layerIndex"])] = {
                    "right_pv": 0,
                    "wrong_pv": 0,
                    "right_uv": set(),
                    "wrong_uv": set()
                }
            if doc["correct"]:
                layer_pv[topic_id][int(doc["layerIndex"])]["right_pv"] += 1
                layer_pv[topic_id][int(doc["layerIndex"])]["right_uv"].add(doc["user"])
            else:
                layer_pv[topic_id][int(doc["layerIndex"])]["wrong_pv"] += 1
                layer_pv[topic_id][int(doc["layerIndex"])]["wrong_uv"].add(doc["user"])

    for k, v in topic_pv.items():
        if not ObjectId.is_valid(k):
            continue
        output_doc = {
            "topicId": ObjectId(k),
            "date": date_str
        }
        for k2, v2 in v.items():
            output_doc[k2 + "_pv"] = v2
            output_doc[k2 + "_uv"] = list(topic_uv[k][k2])

        layer_records = layer_pv[k]
        if layer_records:
            max_layer = int(max(list(layer_records)))
            layer_output = dict()
            for i in range(max_layer):
                layer_ind = i + 1
                if layer_ind in layer_records:
                    layer_output[str(layer_ind)] = layer_records[layer_ind].copy()
                    layer_output[str(layer_ind)]["right_uv"] = list(layer_output[str(layer_ind)]["right_uv"])
                    layer_output[str(layer_ind)]["wrong_uv"] = list(layer_output[str(layer_ind)]["wrong_uv"])
                else:
                    layer_output[str(layer_ind)] = {
                        "right_pv": 0,
                        "wrong_pv": 0,
                        "right_uv": list(),
                        "wrong_uv": list()
                    }

            output_doc["layers"] = layer_output

        output.insert_one(output_doc)

get_daily_stat("20170429")
