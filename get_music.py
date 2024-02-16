from urllib.parse import parse_qs, urlparse
import requests
import plugins
from plugins import *
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger

BASE_URL_LINHUN = "https://api.linhun.vip/api/"  #https://api.linhun.vip/


@plugins.register(name="get_music",
                  desc="get_music插件",
                  version="1.0",
                  author="masterke",
                  desire_priority=100)
class get_music(Plugin):
    config_data = None
    content = None

    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        logger.info("[get_music] inited")

    def get_help_text(self, **kwargs):
        help_text = f""
        return help_text

    def on_handle_context(self, e_context: EventContext):
        # 只处理文本消息
        if e_context['context'].type != ContextType.TEXT:
            return
        self.content = e_context["context"].content.strip()

        if (self.content.startswith("https://i.y.qq.com")
                or self.content.startswith("https://y.music.163.com")):
            logger.info(f"[{__class__.__name__}] 收到消息: {self.content}")
            # 读取配置文件
            config_path = os.path.join(os.path.dirname(__file__),"config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r') as file:
                    self.config_data = json.load(file)
            else:
                logger.error(f"请先配置{config_path}文件")
                return 
            
            reply = Reply()
            result = self.get_music()
            if result != None:
                reply.type = ReplyType.TEXT
                reply.content = result
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS
            else:
                reply.type = ReplyType.ERROR
                reply.content = "获取失败,等待修复⌛️"
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS

    def get_music(self):
        parsed_url = urlparse(self.content)
        query_params = parse_qs(parsed_url.query)
        if "i.y.qq.com" in self.content:
            link_type = 1
        if "y.music.163.com" in self.content:
            link_type = 2
        match (link_type):
            case 1:
                song_id = query_params.get('songmid', [None])[0]
            case 2:
                song_id = query_params.get('id', [None])[0]

        if song_id:
            match (link_type):
                case 1:
                    url = BASE_URL_LINHUN + "vipqqmusic"
                    params = f"id={song_id}&apiKey={self.config_data['get_music_qq_api_key']}"
                    headers = {
                        'Content-Type': "application/x-www-form-urlencoded"
                    }
                    try:
                        response = requests.get(url=url,
                                                params=params,
                                                headers=headers)
                        json_data = response.json()
                        if response.status_code == 200:
                            text = (f"🎵音乐名称:{json_data['name']}\n"
                                    f"👧作者:{json_data['author']}\n"
                                    f"🚀下载链接:{json_data['music']}")
                            logger.info(json_data)
                            return text
                        else:
                            logger.error(json_data)
                            return None
                    except Exception as e:
                        logger.error(f"抛出异常:{e}")
                        return None
                case 2:
                    url = BASE_URL_LINHUN + "NetEaseCloud"
                    params = f"id={song_id}&apiKey={self.config_data['get_music_wy_api_key']}"
                    headers = {
                        'Content-Type': "application/x-www-form-urlencoded"
                    }
                    try:
                        response = requests.get(url=url,
                                                params=params,
                                                headers=headers)
                        json_data = response.json()
                        if response.status_code == 200:
                            text = (f"🎵音乐名称:{json_data['Song']}\n"
                                    f"👧作者:{json_data['singer']}\n"
                                    f"🚀下载链接:{json_data['MusicLink']}")
                            logger.info(json_data)
                            return text
                        else:
                            logger.error(json_data)
                            return None
                    except Exception as e:
                        logger.error(f"抛出异常:{e}")
                        return None
        else:
            return "链接不正确,去看看帮助文档吧😄"
        
        logger.error("所有接口都挂了,无法获取")
        return None
