import os
from flask import Flask, request
from enum import IntEnum

from utils.accountOperation import create_account_sql
from utils.standardPlugin import StandardPlugin, PluginGroupManager, EmptyPlugin, PokeStandardPlugin, AddGroupStandardPlugin, EmptyAddGroupPlugin

from plugins.autoRepoke import AutoRepoke
from plugins.faq_v2 import MaintainFAQ, AskFAQ, HelpFAQ, createFaqDb, createFaqTable
from plugins.groupCalendar import GroupCalendarHelper, GroupCalendarManager
from plugins.greetings import MorningGreet, NightGreet
from plugins.checkCoins import CheckCoins, AddAssignedCoins, CheckTransactions
from plugins.superEmoji import FirecrackersFace, FireworksFace, BasketballFace, HotFace
from plugins.news import ShowNews, YesterdayNews, UpdateNewsAndReport
from plugins.hotSearch import WeiboHotSearch, BaiduHotSearch, ZhihuHotSearch
from plugins.signIn import SignIn
from plugins.stocks import *
from plugins.sjtuInfo import SjtuCanteenInfo, SjtuLibInfo
from plugins.sjmcStatus_v2 import ShowSjmcStatus
from plugins.roulette import RoulettePlugin
from plugins.lottery import LotteryPlugin, createLotterySql
from plugins.show2cyPic import Show2cyPIC, ShowSePIC
from plugins.help_v2 import ShowHelp, ShowStatus, ServerMonitor
from plugins.groupBan import GroupBan
from plugins.privateControl import PrivateControl
from plugins.bilibiliSubscribe import createBilibiliTable, BilibiliSubscribe, BilibiliSubscribeHelper, BilibiliUpSearcher
try:
    from plugins.chatWithNLP import ChatWithNLP
except:
    ChatWithNLP = EmptyPlugin
from plugins.chatWithAnswerbook import ChatWithAnswerbook
try:
    from plugins.getDekt import SjtuDekt, SjtuDektMonitor
except:
    SjtuDekt, SjtuDektMonitor = EmptyPlugin, EmptyPlugin
from plugins.getJwc import GetSjtuNews, GetJwc, SjtuJwcMonitor#, SubscribeJwc
from plugins.sjtuBwc import SjtuBwc, SjtuBwcMonitor, createBwcSql
from plugins.canvasSync import CanvasiCalBind, CanvasiCalUnbind, GetCanvas
from plugins.getPermission import GetPermission, AddPermission, DelPermission, ShowPermission, AddGroupAdminToBotAdmin
from plugins.goBang import GoBangPlugin
from plugins.messageRecorder import GroupMessageRecorder
from plugins.addGroupRecorder import AddGroupRecorder
from plugins.fileRecorder import GroupFileRecorder
from plugins.sjmcLive import GetSjmcLive, GetFduMcLive, SjmcLiveMonitor, FduMcLiveMonitor
from plugins.sjtuHesuan import SjtuHesuan
from plugins.groupActReport import ActReportPlugin, ActRankPlugin
from plugins.groupWordCloud import wordCloudPlugin, GenWordCloud
from plugins.randomNum import TarotRandom, RandomNum, ThreeKingdomsRandom
from plugins.sjtuClassroom import SjtuClassroom, SjtuClassroomRecommend, SjtuClassroomPeopleNum
from plugins.makeJoke import MakeJoke
from plugins.uniAgenda import GetUniAgenda
try:
    from plugins.notPublished.jile import Chai_Jile, Yuan_Jile
except:
    Chai_Jile = EmptyPlugin
    Yuan_Jile = EmptyPlugin
try:
    from plugins.notPublished.getMddStatus import GetMddStatus, MonitorMddStatus#, SubscribeMdd
    GetMddStatus()
except:
    GetMddStatus, MonitorMddStatus = EmptyPlugin, EmptyPlugin

try:
    from plugins.notPublished.EE0502 import ShowEE0502Comments
    ShowEE0502Comments()
except:
    ShowEE0502Comments = EmptyPlugin

try:
    from plugins.notPublished.sjtuPlusGroupingVerication import SjtuPlusGroupingVerify
except:
    SjtuPlusGroupingVerify = EmptyAddGroupPlugin

from plugins.gocqWatchDog import GocqWatchDog

###### end not published plugins

def sqlInit():
    createGlobalConfig()
    create_account_sql()
    createFaqDb()
    createBilibiliTable()
    createLotterySql()
    createBwcSql()
    for group in get_group_list():
        groupId = group['group_id']
        createFaqTable(str(groupId))
sqlInit()

ROOT_PATH = os.path.dirname(os.path.realpath(__file__))
RESOURCES_PATH = os.path.join(ROOT_PATH, "resources")

# 特殊插件需要复用的放在这里
helper = ShowHelp() # 帮助插件
gocqWatchDog = GocqWatchDog(60)
groupMessageRecorder = GroupMessageRecorder() # 群聊消息记录插件


GroupPluginList:List[StandardPlugin]=[ # 指定群启用插件
    groupMessageRecorder,
    helper,ShowStatus(),ServerMonitor(), # 帮助
    GetPermission(), 
    PluginGroupManager([AddPermission(), DelPermission(), ShowPermission(), AddGroupAdminToBotAdmin()], 'permission'), # 权限
    PluginGroupManager([AskFAQ(), MaintainFAQ(), HelpFAQ()],'faq'), # 问答库与维护
    PluginGroupManager([GroupCalendarHelper(), GroupCalendarManager()], 'calendar'),
    PluginGroupManager([MorningGreet(), NightGreet()], 'greeting'), # 早安晚安
    PluginGroupManager([CheckCoins(), AddAssignedCoins(),CheckTransactions()],'money'), # 查询金币,查询记录,增加金币（管理员）
    PluginGroupManager([FireworksFace(), FirecrackersFace(), BasketballFace(), HotFace(), MakeJoke()], 'superemoji'), # 超级表情
    PluginGroupManager([ShowNews(), YesterdayNews(), 
                        PluginGroupManager([UpdateNewsAndReport()], 'newsreport')],'news'),  # 新闻
    PluginGroupManager([WeiboHotSearch(), BaiduHotSearch(), ZhihuHotSearch(),], 'hotsearch'),
    PluginGroupManager([SjtuCanteenInfo(),SjtuLibInfo(), SjtuClassroom(), SjtuClassroomPeopleNum(),
                        SjtuClassroomRecommend(), GetMddStatus(), #SubscribeMdd(), # 交大餐厅, 图书馆, 核酸点, 麦当劳
                        PluginGroupManager([MonitorMddStatus()], 'mddmonitor'),],'sjtuinfo'), 
    # PluginGroupManager([QueryStocksHelper(), QueryStocks(), BuyStocksHelper(), BuyStocks(), QueryStocksPriceHelper(), QueryStocksPrice()],'stocks'), # 股票
    PluginGroupManager([Chai_Jile(), Yuan_Jile()],'jile'), # 柴/元神寄了
    PluginGroupManager([SignIn()], 'signin'),  # 签到
    PluginGroupManager([ShowSjmcStatus(), GetSjmcLive(), GetFduMcLive(),
                        PluginGroupManager([SjmcLiveMonitor(),FduMcLiveMonitor()], 'mclive')], 'sjmc'), #MC社服务
    PluginGroupManager([GetJwc(), SjtuBwc(), #SubscribeJwc() ,
                        SjtuJwcMonitor(), GetSjtuNews(), SjtuDekt(),# jwc服务, jwc广播, 交大新闻, 第二课堂
                        PluginGroupManager([SjtuDektMonitor()], 'dekt'),
                        PluginGroupManager([SjtuBwcMonitor()], 'bwcreport'),], 'jwc'), 
    PluginGroupManager([RoulettePlugin()],'roulette'), # 轮盘赌
    PluginGroupManager([LotteryPlugin()],'lottery'), # 彩票 TODO
    # PluginGroupManager([GoBangPlugin()],'gobang'),
    PluginGroupManager([Show2cyPIC()], 'anime'), #ShowSePIC(), # 来点图图，来点涩涩(关闭)
    PluginGroupManager([ChatWithAnswerbook(), ChatWithNLP()], 'chat'), # 答案之书/NLP
    PluginGroupManager([GetCanvas(), GetUniAgenda(), CanvasiCalBind(), CanvasiCalUnbind()], 'canvas'), # 日历馈送
    # PluginGroupManager([DropOut()], 'dropout'), # 一键退学
    PluginGroupManager([ShowEE0502Comments()], 'izf'), # 张峰
    PluginGroupManager([ActReportPlugin(), ActRankPlugin(), wordCloudPlugin(), PluginGroupManager([GenWordCloud()], 'wcdaily')], 'actreport'), #水群报告
    PluginGroupManager([RandomNum(), ThreeKingdomsRandom(), TarotRandom()], 'random'),
    PluginGroupManager([BilibiliSubscribeHelper(), BilibiliSubscribe()], 'bilibili'),
    PrivateControl(),
]
PrivatePluginList:List[StandardPlugin]=[ # 私聊启用插件
    helper, 
    ShowStatus(),ServerMonitor(),
    CheckCoins(),AddAssignedCoins(),CheckTransactions(),
    ShowNews(), YesterdayNews(),
    MorningGreet(), NightGreet(),
    SignIn(),
    QueryStocksHelper(), QueryStocks(), BuyStocksHelper(), BuyStocks(), QueryStocksPriceHelper(), QueryStocksPrice(),
    SjtuCanteenInfo(),SjtuLibInfo(),ShowSjmcStatus(),SjtuDekt(),GetJwc(), SjtuBwc(), #SubscribeJwc(), 
    GetSjtuNews(),
    LotteryPlugin(),
    Show2cyPIC(), #ShowSePIC(),
    GetCanvas(), CanvasiCalBind(), CanvasiCalUnbind(),
    ShowEE0502Comments(),
    GetSjmcLive(), GetFduMcLive(),
    GetMddStatus(),#SubscribeMdd(),
    SjtuHesuan(),
    RandomNum(), ThreeKingdomsRandom(), TarotRandom(),
    MakeJoke(),
    SjtuClassroom(), SjtuClassroomPeopleNum(), SjtuClassroomRecommend(),
    PrivateControl(),
]
GroupPokeList:List[PokeStandardPlugin] = [
    AutoRepoke(), # 自动回复拍一拍
]
AddGroupVerifyPluginList:List[AddGroupStandardPlugin] = [
    AddGroupRecorder(), # place this plugin to the first place
    SjtuPlusGroupingVerify('test',[123, 456]),
]
helper.updatePluginList(GroupPluginList, PrivatePluginList)

app = Flask(__name__)

class NoticeType(IntEnum):
    NoProcessRequired = 0
    GroupMessageNoProcessRequired = 1
    GocqHeartBeat = 5
    GroupMessage = 11
    GroupPoke = 12
    GroupRecall = 13
    GroupUpload = 14
    PrivateMessage = 21
    PrivatePoke = 22
    PrivateRecall = 23
    AddGroup = 31
    AddPrivate = 32

def eventClassify(json_data: dict)->NoticeType: 
    """事件分类"""
    if json_data['post_type'] == 'meta_event' and json_data['meta_event_type'] == 'heartbeat':
        return NoticeType.GocqHeartBeat
    elif json_data['post_type'] == 'message':
        if json_data['message_type'] == 'group':
            if json_data['group_id'] in APPLY_GROUP_ID:
                return NoticeType.GroupMessage
            else:
                return NoticeType.GroupMessageNoProcessRequired
        elif json_data['message_type'] == 'private':
            return NoticeType.PrivateMessage
    elif json_data['post_type'] == 'notice':
        if json_data['notice_type'] == 'notify':
            if json_data['sub_type'] == "poke":
                if json_data.get('group_id', None) in APPLY_GROUP_ID:
                    return NoticeType.GroupPoke
        elif json_data['notice_type'] == 'group_recall':
            return NoticeType.GroupRecall
        elif json_data['notice_type'] == 'group_upload':
            return NoticeType.GroupUpload
    elif json_data['post_type'] == 'request':
        print(json_data)
        if json_data['request_type'] == 'friend':
            return NoticeType.AddPrivate
        elif json_data['request_type'] == 'group':
            return NoticeType.AddGroup
    else:
        return NoticeType.NoProcessRequired

@app.route('/', methods=["POST"])
def post_data():
    # 获取事件上报
    data = request.get_json()
    # 筛选并处理指定事件
    flag=eventClassify(data)
    # 群消息处理
    if flag==NoticeType.GroupMessage: 
        msg=data['message'].strip()
        for event in GroupPluginList:
            event: StandardPlugin
            try:
                if event.judgeTrigger(msg, data):
                    ret = event.executeEvent(msg, data)
                    if ret != None:
                        return ret
            except TypeError as e:
                warning("type error in main.py: {}\n\n{}".format(e, event))
    elif flag == NoticeType.GroupMessageNoProcessRequired:
        groupMessageRecorder.executeEvent(data['message'], data)
    elif flag == NoticeType.GroupRecall:
        for plugin in [groupMessageRecorder]:
            plugin.recallMessage(data)

    # 私聊消息处理
    elif flag == NoticeType.PrivateMessage:
        # print(data)
        msg=data['message'].strip()
        for event in PrivatePluginList:
            if event.judgeTrigger(msg, data):
                if event.executeEvent(msg, data)!=None:
                    break

    elif flag == NoticeType.AddGroup:
        for p in AddGroupVerifyPluginList:
            if p.judgeTrigger(data):
                if p.addGroupVerication(data) != None:
                    break
    # 上传文件处理
    elif flag == NoticeType.GroupUpload:
        for event in [GroupFileRecorder()]:
            event.uploadFile(data)
    # 群内拍一拍回拍
    elif flag==NoticeType.GroupPoke: 
        for p in GroupPokeList:
            if p.judgeTrigger(data):
                if p.pokeMessage(data)!=None:
                    break
            
    # 自动加好友
    elif flag==NoticeType.AddPrivate:
        set_friend_add_request(data['flag'], True)
    elif flag==NoticeType.GocqHeartBeat:
        gocqWatchDog.feed()
    return "OK"

def initCheck():
    # do some check
    for p in GroupPluginList:
        infoDict = p.getPluginInfo()
        assert 'name' in infoDict.keys() and 'description' in infoDict.keys() \
            and 'commandDescription' in infoDict.keys() and 'usePlace' in infoDict.keys()
        if 'group' not in infoDict['usePlace']:
            print("plugin [{}] can not be used in group talk!".format(infoDict['name']))
            exit(1)
    for p in PrivatePluginList:
        infoDict = p.getPluginInfo()
        assert 'name' in infoDict.keys() and 'description' in infoDict.keys() \
            and 'commandDescription' in infoDict.keys() and 'usePlace' in infoDict.keys()
        if 'private' not in infoDict['usePlace']:
            print("plugin [{}] can not be used in private talk!".format(infoDict['name']))
            exit(1)
    gocqWatchDog.start()

if __name__ == '__main__':
    initCheck()
    app.run(host="127.0.0.1", port=5986)