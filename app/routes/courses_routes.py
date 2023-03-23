from fastapi import APIRouter, Body, Request, HTTPException, status, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from bson import ObjectId
from bson.json_util import dumps

import json

router = APIRouter()


# GET a of courses
@router.get("/courses/list")
async def courses_list(request: Request):
    list_of_courses_name = []
    list_of_courses_date = []
    list_of_courses_rating = []
    list_of_courses_all = []
    courses_qrysets1 = (
        await request.app.mongodb["courses"]
        .find({}, {"name": 1})
        .sort("name", 1)
        .collation({"locale": "en", "caseLevel": True})
        .to_list(length=2000)
    )
    for courses_qryset1 in courses_qrysets1:
        list_of_courses_name.append(courses_qryset1["name"])

    courses_qrysets2 = (
        await request.app.mongodb["courses"]
        .find({}, {"name": 1})
        .sort("date", -1)
        .to_list(length=2000)
    )
    for courses_qryset2 in courses_qrysets2:
        list_of_courses_date.append(courses_qryset2["name"])

    courses_qrysets3 = (
        await request.app.mongodb["courses"]
        .find({}, {"name": 1})
        .sort("rating", -1)
        .to_list(length=2000)
    )
    for courses_qryset3 in courses_qrysets3:
        list_of_courses_rating.append(courses_qryset3["name"])

    courses_qrysets_all = (
        await request.app.mongodb["courses"]
        .find({}, {"name": 1})
        .sort([("name", 1), ("date", -1), ("rating", -1)])
        .to_list(length=2000)
    )
    for courses_qryset_all in courses_qrysets_all:
        list_of_courses_all.append(courses_qryset_all["name"])

    print(list_of_courses_all)
    return JSONResponse(status_code=status.HTTP_200_OK, content=list_of_courses_name)


# add a of courses
@router.post("/courses/add")
async def courses_add(request: Request, upload_file: UploadFile = File(...)):
    json_data = json.load(upload_file.file)
    try:
        db_ = await request.app.mongodb["courses"].insert_many(json_data)
    except Exception as e:
        print(e)
    return JSONResponse(status_code=status.HTTP_200_OK, content={})


# overview a of courses
@router.post("/courses/overview")
async def courses_overview(request: Request, name=str("")):
    try:
        print(name)
        db_ = await request.app.mongodb["courses"].find_one({"name": name})
        return JSONResponse(status_code=status.HTTP_200_OK, content=dumps(db_))

    except Exception as e:
        print(e)
        return JSONResponse(status_code=status.HTTP_200_OK, content=e)


# 3 get specific chapeter
@router.post("/courses/chapter")
async def chapter_overview(request: Request, chapter_name=str("")):
    try:
        print(chapter_name)
        db_ = (
            await request.app.mongodb["courses"]
            .aggregate(
                [
                    {"$match": {"chapters.name": "Big Picture: Derivatives"}},
                    {
                        "$project": {
                            "chapters": {
                                "$filter": {
                                    "input": "$chapters",
                                    "as": "chapters",
                                    "cond": {
                                        "$eq": [
                                            "$$chapters.name",
                                            "Big Picture: Derivatives",
                                        ]
                                    },
                                }
                            },
                            "name": 1,
                        }
                    },
                ]
            )
            .to_list(length=200000000)
        )
        print(db_)

        return JSONResponse(status_code=status.HTTP_200_OK, content=dumps(db_))

    except Exception as e:
        print(e)
        return JSONResponse(status_code=status.HTTP_200_OK, content={"err": "in err"})


# add ratings
@router.post("/courses/rating")
async def add_chapter_rating(
    request: Request, course_name=str(""), chapter_name=str(""), rating=int()
):
    rating = int(rating)
    if rating > 1 or rating < -1:
        print("ture flas")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"msg": "Please entere value 1 or -1 "},
        )
    else:
        try:
            
            
            db_ = await request.app.mongodb["courses"].update_one(
                {"chapters": {"$elemMatch": {"name": chapter_name}}},
                {"$inc": {"chapters.$.rating": rating}},
                False,
                True,
            )
            # print(db_)
            db__ = (
                await request.app.mongodb["courses"]
                .aggregate(
                    [
                        {
                            "$project": {
                                "_id": 0,
                                "name": "$name",
                                "totalRating": {
                                    "$reduce": {
                                        "input": "$chapters",
                                        "initialValue": 0,
                                        "in": {"$sum": ["$$value", "$$this.rating"]},
                                    }
                                },
                                "all_chapters": "$chapters",
                            }
                        },
                        {"$sort": {"totalRating": -1}},
                    ]
                )
                .to_list(length=200)
            )
            return JSONResponse(status_code=status.HTTP_200_OK, content=dumps(db__))

        except Exception as e:
            print(e)
            return JSONResponse(status_code=status.HTTP_200_OK, content=e)
