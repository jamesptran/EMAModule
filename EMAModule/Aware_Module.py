
# import requests


# url = "https://unite.healthscitech.org/api/aware/{{group-id}}/user/{{user-id}}/device/{{aware-device-id}}/aware_fields"
# payload={}

# headers = {
#   'Authorization': '{{admin-token}}'
# }
# # response = requests.request("GET", url, headers=headers, data=payload)
# # print(response.text)





import pymongo
from bson.objectid import ObjectId


class AwareModule():
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.client["savoring"]


        self.data_field = self.db['aware_data_field']
        self.data_points = self.db['aware_data_point']

    def get_data_past_day(self, device_id, sensor_type):

        return [{'_id': ObjectId('611105ca0523a54aa3d23b9e'), 'value': {'double_altitude': -4.400000095367432, 'double_longitude': -117.8331387, 'double_latitude': 33.6466024, 'double_bearing': 0, 'double_speed': 0, 'device_id': 'fff825dd-3616-4966-b542-fb167894d54e', 'provider': 'network', 'accuracy': '11.472', 'label': '', 'timestamp': 1628504237711}}]

        sensor_id  = self.data_field.find_one({'device_id': ObjectId(device_id), 'name': sensor_type}, {'_id': 1})['_id']
        iterator = self.data_points.find({'field': sensor_id}, {'_id': 0 ,'value': 1})

        count = 0
        data_list = []
        max_timestamp = 0
        min_timestamp = float('inf')
        for point in iterator:
            count += 1
            data_list.append(point)

            if point['value']['timestamp'] <= min_timestamp:
                min_timestamp = point['value']['timestamp']

            if point['value']['timestamp'] >= max_timestamp:
                max_timestamp = point['value']['timestamp']

            if max_timestamp - min_timestamp >= 86400000:
                break

            if count == 500:
                break


        return data_list


    def get_latest_data(self, device_id, sensor_type):

        return {'_id': ObjectId('611105ca0523a54aa3d23b9e'), 'value': {'double_altitude': -4.400000095367432, 'double_longitude': -117.8331387, 'double_latitude': 33.6466024, 'double_bearing': 0, 'double_speed': 0, 'device_id': 'fff825dd-3616-4966-b542-fb167894d54e', 'provider': 'network', 'accuracy': '11.472', 'label': '', 'timestamp': 1628504237711}}

        sensor_id  = self.data_field.find_one({'device_id': ObjectId(device_id), 'name': sensor_type}, {'_id': 1})['_id']
        latest_point = self.data_points.find_one({'field': sensor_id}, {'_id': 1 ,'value': 1}, sort=[( '_id', pymongo.DESCENDING )])

        return latest_point






if __name__ == '__main__':
    mod = AwareModule()
    result = mod.get_latest_data('60dbb425b439293c48e93e48', 'locations')
    print(result) # {'_id': ObjectId('611105ca0523a54aa3d23b9e'), 'value': {'double_altitude': -4.400000095367432, 'double_longitude': -117.8331387, 'double_latitude': 33.6466024, 'double_bearing': 0, 'double_speed': 0, 'device_id': 'fff825dd-3616-4966-b542-fb167894d54e', 'provider': 'network', 'accuracy': '11.472', 'label': '', 'timestamp': 1628504237711}}
    # print(len(result))
    # print(result[0])
    # print(result[-1])


# response = requests.request("GET", url, headers=headers, data=payload)
# print(response.text)

# client = pymongo.MongoClient("mongodb://localhost:27017/")

# db = client["savoring"]

# device_id = ObjectId('60dbb425b439293c48e93e48')
# data_field = db['aware_data_field']
# sensor_id  = data_field.find_one({'device_id': device_id, 'name': 'locations'}, {'_id': 1})['_id']


# data_list = db['aware_data_point']
# x = data_list.find({'field': sensor_id}, {'_id': 0 ,'value': 1})

# count = 0
# for a in x:
#     count += 1
#     if count == 5:
#         break
#     else:
#         print(a)





