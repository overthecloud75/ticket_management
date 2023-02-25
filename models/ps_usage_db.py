from .db import BasicModel

class UsageModel(BasicModel):

    def __init__(self, model='ps_usage_logs'):
        super().__init__(model=model)

    def get(self, begin_timestamp):
        data_dict = {'timestamp': [], 'cpu': [], 'mem': []}
        data_list = self.collection.find({'timestamp':{'$gt': begin_timestamp}}).sort('timestamp', -1)
        for i, data in enumerate(data_list):
            data_dict['timestamp'].append(i)
            data_dict['cpu'].append(data['cpu'])
            data_dict['mem'].append(data['mem'])
        return data_dict

    def post(self, usage):
        self.collection.insert_one(usage)


