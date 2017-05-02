from flask import Flask, request, jsonify, send_from_directory
import config as cfg
from collections import defaultdict
from bson.objectid import ObjectId


app = Flask(__name__)


@app.route('/')
def send_index():
    print('des')
    return send_from_directory('../frontend', 'index.html')


@app.route('/<path:path>')
def send_file(path):
    return send_from_directory('../frontend', path)


@app.route('/api/publishers')
def hello():
    x = cfg.chapters.distinct("publisher")
    return jsonify(x)


@app.route('/api/semesters/<publisher>')
def semester(publisher):
    x = cfg.chapters.distinct("semester", {"publisher": publisher})
    return jsonify(x)


@app.route('/api/chapters/<publisher>/<semester>')
def chapter(publisher, semester):
    x = list(cfg.chapters.find({"publisher": publisher, "semester": semester}, {"name": 1}))
    x = [{"chapterId": str(t["_id"]), "chapterName": t["name"]} for t in x]
    return jsonify(x)


@app.route('/api/topicStats/<chapterId>/<startDate>/<endDate>')
def get_topics(chapterId, startDate, endDate):
    # populate topics (in order)
    this_chapter = cfg.chapters.find_one(ObjectId(chapterId))
    this_themes = cfg.themes.find({"_id": {"$in": this_chapter["themes"]}}, {"topics": 1})
    topic_result = list()
    for doc in this_themes:
        topic_result += doc["topics"]

    final_topic_result = cfg.get_first_page_data(topic_result, startDate, endDate)
    # topic_result = [str(t) for t in topic_result]
    return jsonify(final_topic_result)


@app.route('/api/videoStats/<topicId>/<startDate>/<endDate>')
def get_videos(topicId, startDate, endDate):
    x = cfg.mrjing.find({"topicId": ObjectId(topicId), "date": {"$gte": startDate, "$lte": endDate}})
    final_result = {
        "topicName": "",
        "enterVideo_pv": 0,
        "enterVideo_uv": list(),
        "startVideo_pv": 0,
        "startVideo_uv": list(),
        "clickVideoExit_pv": 0,
        "clickVideoExit_uv": list(),
        "finishVideo_pv": 0,
        "finishVideo_uv": list()
    }
    for doc in x:
        final_result["enterVideo_pv"] += cfg.get_value(doc, "enterVideo_pv")
        final_result["startVideo_pv"] += cfg.get_value(doc, "startVideo_pv")
        final_result["clickVideoExit_pv"] +=cfg.get_value(doc, "clickVideoExit_pv")
        final_result["finishVideo_pv"] += cfg.get_value(doc, "finishVideo_pv")
        final_result["enterVideo_uv"] += cfg.get_value(doc, "enterVideo_uv")
        final_result["startVideo_uv"] += cfg.get_value(doc, "startVideo_uv")
        final_result["clickVideoExit_uv"] += cfg.get_value(doc, "clickVideoExit_uv")
        final_result["finishVideo_uv"] += cfg.get_value(doc, "finishVideo_uv")

    final_result["enterVideo_uv"] = len(set(final_result["enterVideo_uv"]))
    final_result["startVideo_uv"] = len(set(final_result["startVideo_uv"]))
    final_result["clickVideoExit_uv"] = len(set(final_result["clickVideoExit_uv"]))
    final_result["finishVideo_uv"] = len(set(final_result["finishVideo_uv"]))

    final_result["topicName"] = cfg.topics.find_one(ObjectId(topicId))["name"]
    return jsonify(final_result)


@app.route('/api/practiceStats/<topicId>/<startDate>/<endDate>')
def get_practice(topicId, startDate, endDate):
    x = cfg.mrjing.find({"topicId": ObjectId(topicId), "date": {"$gte": startDate, "$lte": endDate}})
    final_result = {
        "topicName": "",
        "startPractice_pv": 0,
        "startPractice_uv": list(),
        "clickProblemSubmit_pv": 0,
        "clickProblemSubmit_uv": list(),
        "clickProblemExit_pv": 0,
        "clickProblemExit_uv": list(),
        "enterPracticeFailure_pv": 0,
        "enterPracticeFailure_uv": list(),
        "enterTopicFinish_pv": 0,
        "enterTopicFinish_uv": list(),
        "layers": [None for _ in range(10)]
    }
    for doc in x:
        final_result["startPractice_pv"] += cfg.get_value(doc, "startPractice_pv")
        final_result["startPractice_uv"] += cfg.get_value(doc, "startPractice_uv")
        final_result["clickProblemSubmit_pv"] += cfg.get_value(doc, "clickProblemSubmit_pv")
        final_result["clickProblemSubmit_uv"] += cfg.get_value(doc, "clickProblemSubmit_uv")
        final_result["clickProblemExit_pv"] += cfg.get_value(doc, "clickProblemExit_pv")
        final_result["clickProblemExit_uv"] += cfg.get_value(doc, "clickProblemExit_uv")
        final_result["enterPracticeFailure_pv"] += cfg.get_value(doc, "enterPracticeFailure_pv")
        final_result["enterPracticeFailure_uv"] += cfg.get_value(doc, "enterPracticeFailure_uv")
        final_result["enterTopicFinish_pv"] += cfg.get_value(doc, "enterTopicFinish_pv")
        final_result["enterTopicFinish_uv"] += cfg.get_value(doc, "enterTopicFinish_uv")
        for layer_index, layer in doc["layers"].items():
            layer_index = int(layer_index)
            if final_result["layers"][layer_index] is None:
                final_result["layers"][layer_index] = {
                    "layerIndex": layer_index,
                    "right_pv": 0,
                    "right_uv": list(),
                    "wrong_pv": 0,
                    "wrong_uv": list()
                }
            final_result["layers"][layer_index]["right_pv"] += layer["right_pv"]
            final_result["layers"][layer_index]["right_uv"] += layer["right_uv"]
            final_result["layers"][layer_index]["wrong_pv"] += layer["wrong_pv"]
            final_result["layers"][layer_index]["wrong_uv"] += layer["wrong_uv"]

    final_result["startPractice_uv"] = len(set(final_result["startPractice_uv"]))
    final_result["clickProblemSubmit_uv"] = len(set(final_result["clickProblemSubmit_uv"]))
    final_result["clickProblemExit_uv"] = len(set(final_result["clickProblemExit_uv"]))
    final_result["enterPracticeFailure_uv"] = len(set(final_result["enterPracticeFailure_uv"]))
    final_result["enterTopicFinish_uv"] = len(set(final_result["enterTopicFinish_uv"]))

    final_result["layers"] = [t for t in final_result["layers"] if t is not None]
    for i, each in enumerate(final_result["layers"]):
        x = each.copy()
        x["right_uv"] = len(set(x["right_uv"]))
        x["wrong_uv"] = len(set(x["wrong_uv"]))
        final_result["layers"][i] = x

    final_result["topicName"] = cfg.topics.find_one(ObjectId(topicId))["name"]
    return jsonify(final_result)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
