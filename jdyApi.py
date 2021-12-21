import requests
import time
import json



class APIUtils:

    WEBSITE = "https://www.jiandaoyun.com"
    RETRY_IF_LIMITED = True

    # 构造函数
    def __init__(self, appId, entryId, api_key):
        self.url_get_widgets = APIUtils.WEBSITE + '/api/v1/app/' + appId + '/entry/' + entryId + '/widgets'
        self.url_get_data = APIUtils.WEBSITE + '/api/v1/app/' + appId + '/entry/' + entryId + '/data'
        self.url_retrieve_data = APIUtils.WEBSITE + '/api/v1/app/' + appId + '/entry/' + entryId + '/data_retrieve'
        self.url_update_data = APIUtils.WEBSITE + '/api/v1/app/' + appId + '/entry/' + entryId + '/data_update'
        self.url_create_data = APIUtils.WEBSITE + '/api/v1/app/' + appId + '/entry/' + entryId + '/data_create'
        self.url_delete_data = APIUtils.WEBSITE + '/api/v1/app/' + appId + '/entry/' + entryId + '/data_delete'
        self.api_key = api_key

    # 带有认证信息的请求头
    def get_req_header(self):
        return {
            'Authorization': 'Bearer ' + self.api_key,
            'Content-Type': 'application/json;charset=utf-8'
        }

    # 发送http请求
    def send_request(self, method, request_url, data):
        headers = self.get_req_header()
        if method == 'GET':
            res = requests.get(request_url, params=data, headers=headers, verify=False, proxies=proxies)
        if method == 'POST':
            res = requests.post(request_url, data=json.dumps(data), headers=headers, verify=False, proxies=proxies)
        result = res.json()
        if res.status_code >= 400:
            if result['code'] == 8303 and APIUtils.RETRY_IF_LIMITED:
                # 5s后重试
                time.sleep(5)
                return self.send_request(method, request_url, data)
            else:
                raise Exception('请求错误！', result)
        else:
            return result

    # 获取表单字段
    def get_form_widgets(self):
        result = self.send_request('POST', self.url_get_widgets, {})
        return result['widgets']

    # 根据条件获取表单中的数据
    def get_form_data(self, dataId, limit, fields, data_filter):
        result = self.send_request('POST', self.url_get_data, {
            'data_id': dataId,
            'limit': limit,
            'fields': fields,
            'filter': data_filter
        })
        return result['data']

    # 获取表单中满足条件的所有数据
    def get_all_data(self, fields, data_filter):
        form_data = []

        # 递归取下一页数据
        def get_next_page(dataId):
            data = self.get_form_data(dataId, 1500, fields, data_filter)
            if data:
                for v in data:
                    form_data.append(v)
                dataId = data[len(data) - 1]['_id']
                get_next_page(dataId)
        get_next_page('')
        return form_data

    # 检索一条数据
    def retrieve_data(self, dataId):
        result = self.send_request('POST', self.url_retrieve_data, {
            'data_id': dataId
        })
        return result['data']

    # 创建一条数据
    def create_data(self, data):
        result = self.send_request('POST', self.url_create_data, {
            'data': data
        })
        return result['data']

    # 更新数据
    def update_data(self, dataId, data):
        result = self.send_request('POST', self.url_update_data, {
            'data_id': dataId,
            'data': data
        })
        return result['data']

    # 删除数据
    def delete_data(self, dataId):
        result = self.send_request('POST', self.url_delete_data, {
            'data_id': dataId
        })
        return result