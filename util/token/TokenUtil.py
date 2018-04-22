from selenium import webdriver
from threading import Lock

import time
import json
import requests
import traceback
import collections
import datetime

# from http import cookiejar


class TokenUtil(object):
    def __init__(self):

        mobileEmulation = {'deviceName': 'iPhone 6'}
        options = webdriver.ChromeOptions()
        options.add_experimental_option('mobileEmulation', mobileEmulation)

        self.driver = webdriver.Chrome(chrome_options=options)

        # self.driver = webdriver.Chrome()
        self.driver.get("file:\\C:\\Users\\Administrator\\Desktop\\meituan\\category.html")
        self.mu = Lock()
        self.mu2 = Lock()
        self.session = requests.session()
        self.token = collections.defaultdict(str)

    def flashToken(self,encrypt_url):
        with self.mu:
            print("刷新token")
            jsScript = """
                            var token  = Rohr_Opt.reload('%s');
                            return token;
                        """ % encrypt_url
            self.token[encrypt_url] = self.driver.execute_script(jsScript)

    def getToken(self,encrypt_url):
        with self.mu:
            # print("token数量",len(self.token))
            if len(self.token)>=800:
                print("toke数超出限制，进行清空")
                self.token = collections.defaultdict(str)
            if not self.token.get(encrypt_url):
                print("获取新token",encrypt_url)
                jsScript = """
                           var token  = Rohr_Opt.reload('%s');
                           return token;
                       """ % encrypt_url
                self.token[encrypt_url] = self.driver.execute_script(jsScript)

        return self.token[encrypt_url]

    def flashToken2(self,encrypt_url):
        with self.mu2:
            print("刷新token")
            jsScript = """
                            var token  = Rohr_Opt.reload('%s');
                            return token;
                        """ % encrypt_url
            self.token = self.driver.execute_script(jsScript)

    def getToken2(self,encrypt_url):
        with self.mu:
            print("获取token",encrypt_url)
            if not self.token:
                jsScript = """
                              var token  = Rohr_Opt.reload('%s');
                              return token;
                          """ % encrypt_url
                self.token = self.driver.execute_script(jsScript)

        return self.token


    def proxiesPost(self,url,headers=None,data=None,params=None):
        """
            通过代理获取数据
        :param url:
        :param data:
        :param header:
        :return:
        """
        i = 0
        while True:
            i += 1
            print("第",i,"次请求",url)
            if i>20:
                print("请求异常超出次数:",url)
                return []
            try:
                response = self.session.post(
                    url,
                    headers=headers,
                    data=data,
                    params = params,
                    timeout=10
                )
                result = json.loads(response.text)
                print("正常返回数据",result)
                if self.validate(result):
                    return result
            except Exception as e:
                print("获取数据报错",e)


    def proxiesPostByToken(self,format_url,encrypt_url,headers=None,data=None):
        """
            通过代理和token获取数据
        :param url:
        :param data:
        :param header:
        :return:
        """

        i = 0
        while True:
            i+=1
            if i>30:
                print("请求超过限制，判定没有数据",encrypt_url)
                return []

            print("第", i, "次请求",encrypt_url)

            token = self.getToken2(encrypt_url)
            try:
                url = format_url.format(token)
                print("token", token)
                response = self.session.post(
                    url,
                    headers=headers,
                    data=data,
                    timeout=10
                )
                print("请求返回数据", response.text)
                result = json.loads(response.text)
                flag = self.validate(result)
                if flag:
                    return result

            except Exception as e:
                print("获取数据报错",traceback.print_exc())
                pass

    def validate(self,data):
        """
            验证获取的数据是否是异常数据
        :param data:
        :return:
        """
        flag = False
        try:
            if data['code'] == 0:
                flag = True
            elif data['code'] == 200404:

                print("访问被限制休息2秒",200404)
                time.sleep(2)
            elif data['code'] == 406:

                print("网络问题休息2秒",406)
                time.sleep(2)
            elif data['code'] == 801:

                print("网络问题休息2秒:",801)
            else:
                print('被封',data)
        except:
            print("判断是否被封报错", data)
        return flag

    def getShopInfo(self, poiid):
        """
            获取指定店铺的店铺信息
        :param poiid:
        :return:
        """
        cookie = "_lxsdk=15c802ee501c8-0dc0965e47615a-71226d35-3653d-15c802ee502c8; UM_distinctid=15ca59742b34af-01b1a3d6a79587-71226d35-33b9d-15ca59742b4420; rvct=55; _lxsdk_cuid=15ca948fc97c8-07dd00d21c5f23-323f5c0f-100200-15ca948fc97c8; iuuid=E1A4E28BE15F46861FA74C0E966284C5BA705FCF135431A8DD0E18DE02E8BFDF; abt=1498091600.0%7CBCE; __mta=222690980.1498091407148.1498091407148.1498091407148.1; CNZZDATA1261825573=527413498-1493350587-%7C1493350587; CNZZDATA1261883731=472701187-1498000090-null%7C1503276500; cityname=\"%E5%8D%97%E4%BA%AC\"; i_extend=H__a100040__b3; webp=1; mtsi-real-ip=36.149.92.230; mtsi-cur-time=\"2017-11-11 100946\"; Hm_lvt_f66b37722f586a240d4621318a5a6ebe=1510657192; __utma=211559370.947114224.1496799124.1510657192.1510657192.1; __utmz=211559370.1510657192.1.1.utmcsr=baidu|utmccn=baidu|utmcmd=organic|utmcct=zt_search; uuid=c84b40ba2520c9cbb13e.1497488937.0.0.0; oc=0SSHZRQvb-Vnf_kKFQYRENtdy0fiGnrJXdgGrF-H71uN68aB5jK_md9KmiIMxk70Gp_okRHmwZ4-dy2e0tdqL3IzrIxSIWms_vE7hE7HYJ8zgylW7eM6U9_GtdkCpXId9fBhQhc8BUZkLbE1HwFxmPlzKBY4nCsmepJHvmMeceY; ci=55; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; __mta=222690980.1498091407148.1498091407148.1510972659525.2; _ga=GA1.3.947114224.1496799124; _gid=GA1.3.386874317.1510889250; _ga=GA1.2.947114224.1496799124; _gid=GA1.2.386874317.1510889250; _ga=GA1.4.947114224.1496799124; _gid=GA1.4.386874317.1510889250; wx_channel_id=0; w_addr=-%E6%B1%9F%E8%8B%8F%E7%9C%81; utm_source=0; w_latlng=32061707,118763232; w_cid=110100; w_cpy=beijing; w_cpy_cn=\"%E5%8C%97%E4%BA%AC\"; w_visitid=3b3e418d-39aa-4d21-902f-72787654d6f9; wm_poi_view_id={}; poiid={}; JSESSIONID=kjy9jimp7gp3326u5agkqqvk; _lxsdk_s=15fcddaf145-2e4-f7e-bf4%7C%7C27; __mta=222690980.1498091407148.1498091407148.1510991483874.2; terminal=i; w_utmz=\"utm_campaign=(direct)&utm_source=5801&utm_medium=(none)&utm_content=(none)&utm_term=(none)\"; w_uuid=tXer8Q-B69ZBScFXOTQ9tXp97fBYBOjunMc73wE9GGck5vJCQdnaEgH2QrDYWukQ".format(poiid,poiid)
        headers = {
            'accept': "*/*",
            'accept-encoding': "gzip, deflate",
            'accept-language': "zh-CN,zh;q=0.9",
            'connection': "keep-alive",
            'content-length': "114",
            'content-type': "application/x-www-form-urlencoded",
            'cookie':cookie,
            'host': "i.waimai.meituan.com",
            'origin': "http//i.waimai.meituan.com",
            'referer': "http//i.waimai.meituan.com/restaurant/526585455566679",
            'user-agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1",
            'x-requested-with': "XMLHttpRequest"
        }

        data = {
            'wmpoiid': poiid,
            'uuid': 'tXer8Q-B69ZBScFXOTQ9tXp97fBYBOjunMc73wE9GGck5vJCQdnaEgH2QrDYWukQ',
            'platform': 3,
            'partner': 4
        }

        format_url = 'http://i.waimai.meituan.com/ajax/v6/poi/info?_token=%s'
        encrypt_url = "/ajax/v6/poi/info?wmpoiid=%s" % poiid

        result = self.proxiesPostByToken(format_url, encrypt_url, headers=headers, data=data)
        # if result:
            # self.putIntoQueue('food',poiid,result)
            # print("info", result)

    def getFood(self,poiid):
        cookie = "_lxsdk=15c802ee501c8-0dc0965e47615a-71226d35-3653d-15c802ee502c8; UM_distinctid=15ca59742b34af-01b1a3d6a79587-71226d35-33b9d-15ca59742b4420; _ga=GA1.4.947114224.1496799124; rvct=55; _lxsdk_cuid=15ca948fc97c8-07dd00d21c5f23-323f5c0f-100200-15ca948fc97c8; iuuid=E1A4E28BE15F46861FA74C0E966284C5BA705FCF135431A8DD0E18DE02E8BFDF; abt=1498091600.0%7CBCE; __mta=222690980.1498091407148.1498091407148.1498091407148.1; CNZZDATA1261825573=527413498-1493350587-%7C1493350587; CNZZDATA1261883731=472701187-1498000090-null%7C1503276500; cityname=\"%E5%8D%97%E4%BA%AC\"; i_extend=H__a100040__b3; webp=1; mtsi-real-ip=36.149.92.230; mtsi-cur-time=\"2017-11-11 100946\"; _lx_utm=utm_source%3Di.waimai.meituan.com%26utm_medium%3Dreferral%26utm_content%3D%252Frestaurant%252F522432221319191; Hm_lvt_f66b37722f586a240d4621318a5a6ebe=1510657192; __utma=211559370.947114224.1496799124.1510657192.1510657192.1; __utmz=211559370.1510657192.1.1.utmcsr=baidu|utmccn=baidu|utmcmd=organic|utmcct=zt_search; _ga=GA1.2.947114224.1496799124; _gid=GA1.2.386874317.1510889250; uuid=c84b40ba2520c9cbb13e.1497488937.0.0.0; oc=0SSHZRQvb-Vnf_kKFQYRENtdy0fiGnrJXdgGrF-H71uN68aB5jK_md9KmiIMxk70Gp_okRHmwZ4-dy2e0tdqL3IzrIxSIWms_vE7hE7HYJ8zgylW7eM6U9_GtdkCpXId9fBhQhc8BUZkLbE1HwFxmPlzKBY4nCsmepJHvmMeceY; ci=55; _ga=GA1.3.947114224.1496799124; _gid=GA1.3.386874317.1510889250; __mta=222690980.1498091407148.1498091407148.1510889784971.2; wx_channel_id=0; utm_source=0; w_latlng=32060254,118796877; w_visitid=2acd264d-32fb-4bda-adab-f42ded88716c; w_cid=110100; w_cpy=beijing; w_cpy_cn=\"%E5%8C%97%E4%BA%AC\"; __mta=222690980.1498091407148.1498091407148.1510899467605.2; _lxsdk_s=15fc8931842-fc4-dd6-1e9%7C%7C22; terminal=i; w_utmz=\"utm_campaign=(direct)&utm_source=5801&utm_medium=(none)&utm_content=(none)&utm_term=(none)\"; w_uuid=tXer8Q-B69ZBScFXOTQ9tXp97fBYBOjunMc73wE9GGck5vJCQdnaEgH2QrDYWukQ; wm_poi_view_id={}; poiid={}; JSESSIONID=1lliliryzr3s612a4a5t1qmqjb".format(poiid,poiid)
        headers = {
            'accept': "*/*",
            'accept-encoding': "gzip, deflate",
            'accept-language': "zh-CN,zh;q=0.9",
            'connection': "keep-alive",
            'content-length': "116",
            'content-type': "application/x-www-form-urlencoded",
            'cookie': "w_visitid=742c5169-3468-4d47-a6d4-93c84cb39d39; webp=1; _lxsdk_cuid=15fe308bb3fc8-05286aafd36e7b-574e6e46-4a640-15fe308bb40c8; _lxsdk=15fe308bb3fc8-05286aafd36e7b-574e6e46-4a640-15fe308bb40c8; wx_channel_id=0; utm_source=0; w_cid=320100; w_cpy_cn=\"%E5%8D%97%E4%BA%AC\"; w_cpy=nanjing; w_latlng=32060591,118782981; __mta=251901494.1511342522167.1511343070837.1511343091853.36; _lxsdk_s=15fe308bb42-45c-3b8-0fd%7C%7C72; terminal=i; w_utmz=\"utm_campaign=(direct)&utm_source=5000&utm_medium=(none)&utm_content=(none)&utm_term=(none)\"; w_uuid=xpIYXWQkPoZiTyotSq1RXGh88jOxX8hfocDU9mooBzfPM7B1MKFOOuIhuiDJdccl; wm_poi_view_id=522432222433303; poiid=522432222433303; JSESSIONID=10ecnvoetusny11vbv8ma7480a",
            'host': "i.waimai.meituan.com",
            'origin': "http//i.waimai.meituan.com",
            'referer': "http//i.waimai.meituan.com/restaurant/522432222433303",
            'user-agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1",
            'x-requested-with': "XMLHttpRequest"
        }

        data = {
            'wm_poi_id':str(poiid),
            'uuid':'xpIYXWQkPoZiTyotSq1RXGh88jOxX8hfocDU9mooBzfPM7B1MKFOOuIhuiDJdccl',
            'platform':'3',
            'partner':'4',
        }


        format_url = 'http://i.waimai.meituan.com/ajax/v8/poi/food?_token=%s'
        encrypt_url = "/ajax/v8/poi/food?wm_poi_id=%s" % poiid

        result = self.proxiesPostByToken(format_url,encrypt_url,headers=headers,data=data)
        if result:
            print("food",result)


    def getCommentPage(self,poiid,index=0):
        cookie = "_lxsdk=15c802ee501c8-0dc0965e47615a-71226d35-3653d-15c802ee502c8; UM_distinctid=15ca59742b34af-01b1a3d6a79587-71226d35-33b9d-15ca59742b4420; _ga=GA1.4.947114224.1496799124; rvct=55; _lxsdk_cuid=15ca948fc97c8-07dd00d21c5f23-323f5c0f-100200-15ca948fc97c8; iuuid=E1A4E28BE15F46861FA74C0E966284C5BA705FCF135431A8DD0E18DE02E8BFDF; abt=1498091600.0%7CBCE; __mta=222690980.1498091407148.1498091407148.1498091407148.1; CNZZDATA1261825573=527413498-1493350587-%7C1493350587; CNZZDATA1261883731=472701187-1498000090-null%7C1503276500; cityname=\"%E5%8D%97%E4%BA%AC\"; i_extend=H__a100040__b3; webp=1; mtsi-real-ip=36.149.92.230; mtsi-cur-time=\"2017-11-11 100946\"; _lx_utm=utm_source%3Di.waimai.meituan.com%26utm_medium%3Dreferral%26utm_content%3D%252Frestaurant%252F522432221319191; Hm_lvt_f66b37722f586a240d4621318a5a6ebe=1510657192; __utma=211559370.947114224.1496799124.1510657192.1510657192.1; __utmz=211559370.1510657192.1.1.utmcsr=baidu|utmccn=baidu|utmcmd=organic|utmcct=zt_search; w_addr=%E5%8D%97%E4%BA%AC%E5%B8%82-%E6%B1%9F%E8%8B%8F%E7%9C%81; _ga=GA1.2.947114224.1496799124; _gid=GA1.2.386874317.1510889250; uuid=c84b40ba2520c9cbb13e.1497488937.0.0.0; oc=0SSHZRQvb-Vnf_kKFQYRENtdy0fiGnrJXdgGrF-H71uN68aB5jK_md9KmiIMxk70Gp_okRHmwZ4-dy2e0tdqL3IzrIxSIWms_vE7hE7HYJ8zgylW7eM6U9_GtdkCpXId9fBhQhc8BUZkLbE1HwFxmPlzKBY4nCsmepJHvmMeceY; ci=55; _ga=GA1.3.947114224.1496799124; _gid=GA1.3.386874317.1510889250; __mta=222690980.1498091407148.1498091407148.1510889784971.2; wx_channel_id=0; utm_source=0; w_latlng=32060254,118796877; w_visitid=2acd264d-32fb-4bda-adab-f42ded88716c; w_cid=110100; w_cpy=beijing; w_cpy_cn=\"%E5%8C%97%E4%BA%AC\"; __mta=222690980.1498091407148.1498091407148.1510899467605.2; _lxsdk_s=15fc8931842-fc4-dd6-1e9%7C%7C22; terminal=i; w_utmz=\"utm_campaign=(direct)&utm_source=5801&utm_medium=(none)&utm_content=(none)&utm_term=(none)\"; w_uuid=tXer8Q-B69ZBScFXOTQ9tXp97fBYBOjunMc73wE9GGck5vJCQdnaEgH2QrDYWukQ; wm_poi_view_id={}; poiid={}; JSESSIONID=1lliliryzr3s612a4a5t1qmqjb".format(poiid, poiid)
        headers = {
            'accept': "*/*",
            'accept-encoding': "gzip, deflate",
            'accept-language': "zh-CN,zh;q=0.9",
            'connection': "keep-alive",
            'content-length': "187",
            'content-type': "application/x-www-form-urlencoded",
            'cookie': cookie,
            'host': "i.waimai.meituan.com",
            'origin': "http//i.waimai.meituan.com",
            'referer': "http//i.waimai.meituan.com/restaurant/478163994198361",
            'user-agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1",
            'x-requested-with': "XMLHttpRequest"
        }

        data = {
            'wmpoiid':poiid,
            'page_offset':0,
            'page_size':20,
            'comment_score_type':0,
            'filter_type':0,
            'label_id':0,
            'uuid':'tXer8Q-B69ZBScFXOTQ9tXp97fBYBOjunMc73wE9GGck5vJCQdnaEgH2QrDYWukQ',
            'platform':3,
            'partner':4
        }

        format_url = 'http://i.waimai.meituan.com/ajax/poi/comment?_token=%s'
        encrypt_url = "/ajax/v8/poi/comment?wm_poi_id=%s" % poiid

        result = self.proxiesPostByToken(format_url, encrypt_url, headers=headers, data=data)
        if result:
            print("comment", result)


    def getSearchHotWord(self,poiid,lat,lng):
        str_la = str(float(lat)* 1000000)[:8]
        str_lo = str(float(lng)* 1000000)[:9]
        print(str_la+"=",str_lo)

        cookie = '_lxsdk=15c802ee501c8-0dc0965e47615a-71226d35-3653d-15c802ee502c8; UM_distinctid=15ca59742b34af-01b1a3d6a79587-71226d35-33b9d-15ca59742b4420; rvct=55; _lxsdk_cuid=15ca948fc97c8-07dd00d21c5f23-323f5c0f-100200-15ca948fc97c8; iuuid=E1A4E28BE15F46861FA74C0E966284C5BA705FCF135431A8DD0E18DE02E8BFDF; abt=1498091600.0%7CBCE; __mta=222690980.1498091407148.1498091407148.1498091407148.1; CNZZDATA1261825573=527413498-1493350587-%7C1493350587; CNZZDATA1261883731=472701187-1498000090-null%7C1503276500; cityname="%E5%8D%97%E4%BA%AC"; i_extend=H__a100040__b3; webp=1; mtsi-real-ip=36.149.92.230; mtsi-cur-time="2017-11-11 10:09:46"; Hm_lvt_f66b37722f586a240d4621318a5a6ebe=1510657192; __utma=211559370.947114224.1496799124.1510657192.1510657192.1; __utmz=211559370.1510657192.1.1.utmcsr=baidu|utmccn=baidu|utmcmd=organic|utmcct=zt_search; uuid=c84b40ba2520c9cbb13e.1497488937.0.0.0; oc=0SSHZRQvb-Vnf_kKFQYRENtdy0fiGnrJXdgGrF-H71uN68aB5jK_md9KmiIMxk70Gp_okRHmwZ4-dy2e0tdqL3IzrIxSIWms_vE7hE7HYJ8zgylW7eM6U9_GtdkCpXId9fBhQhc8BUZkLbE1HwFxmPlzKBY4nCsmepJHvmMeceY; ci=55; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; __mta=222690980.1498091407148.1498091407148.1510972659525.2; _ga=GA1.3.947114224.1496799124; _ga=GA1.2.947114224.1496799124; _ga=GA1.4.947114224.1496799124; w_visitid=d46d8208-fdca-47cd-bd97-826da2343cce; wm_poi_view_id=397809451270120; poiid=397809451270120; w_addr=%E5%8D%97%E4%BA%AC%E5%A4%A7%E5%AD%A6%E9%BC%93%E6%A5%BC%E6%A0%A1%E5%8C%BA; wx_channel_id=0; utm_source=0; w_cid=320100; w_cpy_cn="%E5%8D%97%E4%BA%AC"; w_cpy=nanjing; w_latlng={},{}; __mta=222690980.1498091407148.1498091407148.1511146774196.2; _lxsdk_s=15fd74cd91c-9be-6c-34e%7C%7C30; terminal=i; w_utmz="utm_campaign=(direct)&utm_source=5801&utm_medium=(none)&utm_content=(none)&utm_term=(none)"; w_uuid=tXer8Q-B69ZBScFXOTQ9tXp97fBYBOjunMc73wE9GGck5vJCQdnaEgH2QrDYWukQ; JSESSIONID=1j2c8k5m1nerd1iwwwad2w8vyn'.format(str_la,str_lo)

        headers = {
            'accept': "*/*",
            'accept-encoding': "gzip, deflate",
            'accept-language': "zh-CN,zh;q=0.9",
            'connection': "keep-alive",
            'content-length': "0",
            'cookie': cookie,
            'host': "i.waimai.meituan.com",
            'origin': "http//i.waimai.meituan.com",
            'referer': "http//i.waimai.meituan.com/search/init",
            'user-agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1",
            'x-requested-with': "XMLHttpRequest"
        }

        url = 'http://i.waimai.meituan.com/search/ajax/v7/home/hotlabel'
        print("htoword",url)
        result = self.proxiesPost(url,headers = headers)
        if result:
            print("hot_word",result)

    def __del__(self):
        print("关闭浏览器")
        self.driver.close()

    def getCategoryShopList(self, category_type,second_category_type,lat,lng):
        """
            根据品类获取店铺列表信息
        :param category_level1:
        :param category_level2:
        :return:
        """
        i = 0
        while True:
            try:
                print(category_type, "=",second_category_type,"第",i,"页")
                result = self.getCategoryShopPage(category_type, second_category_type, lat,lng,i)
                for shop in result['data']['poilist']:
                    yield shop
                if not result['data']['poi_has_next_page']:
                    break
                i += 1
            except:
                return []

    def getCategoryShopPage(self,category_type, second_category_type,index = 0):
        """
            获取某个品类下店铺某页的店铺列表信息
        :param category_level1: 一级品类名称
        :param category_level2: 二级品类名称
        :param index: 页数
        :return:
        """

        cookie = "_ga=GA1.3.1409960380.1511489319; _gid=GA1.3.2137867047.1511489319; __mta=142906250.1511489319599.1511489319599.1511489319599.1; webp=1; _lxsdk_cuid=15febc9a484c8-0fe20151585fbd-574e6e46-3d10d-15febc9a484c8; _lxsdk=15febc9a484c8-0fe20151585fbd-574e6e46-3d10d-15febc9a484c8; wx_channel_id=0; w_addr=%E5%8D%97%E4%BA%AC%E5%B8%82-%E6%B1%9F%E8%8B%8F%E7%9C%81; utm_source=1522; w_cid=320100; w_cpy_cn=\"%E5%8D%97%E4%BA%AC\"; w_cpy=nanjing; w_latlng=32060254,118796877; w_visitid=3e985e10-d983-49e2-a1cf-a1050b618ef1; __mta=142906250.1511489319599.1511489319599.1511525284257.2; JSESSIONID=1clo6lqrjdk921jl4jahtz146h; _lxsdk_s=15fedce5331-82d-0f9-19a%7C%7C28; terminal=i; w_utmz=\"utm_campaign=(direct)&utm_source=1522&utm_medium=(none)&utm_content=(none)&utm_term=(none)\"; w_uuid=FAn-6qCal6kzDr9oTlQM5d5Mo8fBTX3zZAgR7Ao9igUtUYjOiK4OlOrKoLwzkUZ5"

        headers = {
            'accept': "application/json",
            'accept-encoding': "gzip, deflate",
            'accept-language': "zh-CN,zh;q=0.9",
            'content-length': "111",
            'content-type': "application/x-www-form-urlencoded",
            'cookie': "_ga=GA1.3.1409960380.1511489319; _gid=GA1.3.2137867047.1511489319; __mta=142906250.1511489319599.1511489319599.1511489319599.1; webp=1; _lxsdk_cuid=15febc9a484c8-0fe20151585fbd-574e6e46-3d10d-15febc9a484c8; _lxsdk=15febc9a484c8-0fe20151585fbd-574e6e46-3d10d-15febc9a484c8; wx_channel_id=0; w_addr=%E5%8D%97%E4%BA%AC%E5%B8%82-%E6%B1%9F%E8%8B%8F%E7%9C%81; utm_source=1522; w_cid=320100; w_cpy_cn=\"%E5%8D%97%E4%BA%AC\"; w_cpy=nanjing; w_latlng=32060254,118796877; w_visitid=3e985e10-d983-49e2-a1cf-a1050b618ef1; __mta=142906250.1511489319599.1511489319599.1511525284257.2; JSESSIONID=1clo6lqrjdk921jl4jahtz146h; _lxsdk_s=15fedce5331-82d-0f9-19a%7C%7C28; terminal=i; w_utmz=\"utm_campaign=(direct)&utm_source=1522&utm_medium=(none)&utm_content=(none)&utm_term=(none)\"; w_uuid=FAn-6qCal6kzDr9oTlQM5d5Mo8fBTX3zZAgR7Ao9igUtUYjOiK4OlOrKoLwzkUZ5",
            'host': "i.waimai.meituan.com",
            'origin': "http//i.waimai.meituan.com",
            'proxy-connection': "keep-alive",
            'referer': "http//i.waimai.meituan.com/channel?category_type=101085&second_category_type=101119",
            'user-agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1",
            'x-requested-with': "XMLHttpRequest"
        }

        data = {
            'uuid': 'FAn-6qCal6kzDr9oTlQM5d5Mo8fBTX3zZAgR7Ao9igUtUYjOiK4OlOrKoLwzkUZ5',
            'platform': '3',
            'partner': '4',
            'page_index': '1',
            'apage': '1'
        }

        format_url = "http://i.waimai.meituan.com/ajax/v6/poi/filter?category_type=101085&second_category_type=101119&_token={}"
        encrypt_url = "/ajax/v6/poi/filter?category_type=101085&second_category_type=101119&page_index=1&apage=1"
        result = self.proxiesPostByToken(format_url, encrypt_url, headers=headers, data=data)

        if result:
            print(result)
            return result

if __name__ == '__main__':
    t = TokenUtil()
    jiami_url = '/ajax/v6/poi/filter?category_type=101085&second_category_type=101119&page_index=%s&apage=1'
    # 32.055015,118.77943
    t.getToken2(jiami_url)

    # shop_list = t.getCategoryShopList(101085,101119,32.055015,118.77943)
    # for shop in shop_list:
    #     print(shop)
    # print(t.getToken2('123'))


