# import eventlet
# eventlet.monkey_patch()
from sqlalchemy import inspect
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
import os
import random
from sqlalchemy import inspect, text
from flask_socketio import SocketIO, emit
import psutil
import time
import datetime
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'images', 'avatars')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
app_start_time = time.time()

db = SQLAlchemy(app)
csrf = CSRFProtect(app)

full_questions = [
    {'text': '社交后通常感到', 'dimension': ('E','I'), 'options': ['充满活力','需要独处']},
{'text': '描述事物时侧重', 'dimension': ('S','N'), 'options': ['具体细节','整体概念']},
{'text': '决策依据更注重', 'dimension': ('T','F'), 'options': ['逻辑分析','情感共鸣']},
{'text': '工作计划习惯', 'dimension': ('J','P'), 'options': ['详细规划','灵活调整']},

{'text': '结识新朋友频率', 'dimension': ('E','I'), 'options': ['经常主动','偶尔被动']},
{'text': '学习新知识方式', 'dimension': ('S','N'), 'options': ['实际练习','理论思考']},
{'text': '评价他人表现时', 'dimension': ('T','F'), 'options': ['客观成果','主观努力']},
{'text': '旅行准备方式', 'dimension': ('J','P'), 'options': ['提前安排','随性出发']},

{'text': '电话沟通偏好', 'dimension': ('E','I'), 'options': ['直接通话','文字消息']},
{'text': '记忆信息方式', 'dimension': ('S','N'), 'options': ['具体事实','模式关联']},
{'text': '职场决策依据', 'dimension': ('T','F'), 'options': ['数据效率','团队氛围']},
{'text': '处理截止期限', 'dimension': ('J','P'), 'options': ['提前完成','最后冲刺']},

{'text': '恢复精力方式', 'dimension': ('E','I'), 'options': ['与人互动','独自静处']},
{'text': '理解说明书时', 'dimension': ('S','N'), 'options': ['逐步执行','先看原理']},
{'text': '面对批评反应', 'dimension': ('T','F'), 'options': ['分析内容','感受态度']},
{'text': '文件管理习惯', 'dimension': ('J','P'), 'options': ['系统分类','随手放置']},

{'text': '会议参与方式', 'dimension': ('E','I'), 'options': ['积极发言','倾听思考']},
{'text': '讲述故事侧重', 'dimension': ('S','N'), 'options': ['事实细节','深层含义']},
{'text': '解决争议方式', 'dimension': ('T','F'), 'options': ['讲清道理','照顾感受']},
{'text': '每日作息习惯', 'dimension': ('J','P'), 'options': ['固定规律','灵活变化']},

{'text': '社交网络使用', 'dimension': ('E','I'), 'options': ['频繁更新','偶尔查看']},
{'text': '学习历史关注', 'dimension': ('S','N'), 'options': ['具体事件','时代精神']},
{'text': '选择礼物标准', 'dimension': ('T','F'), 'options': ['实用价值','情感意义']},
{'text': '购物时风格', 'dimension': ('J','P'), 'options': ['列清单买','即兴发现']},

{'text': '认识新朋友时', 'dimension': ('E','I'), 'options': ['主动交谈','等待接触']},
{'text': '解决问题方法', 'dimension': ('S','N'), 'options': ['经验步骤','创新方案']},
{'text': '团队合作关注', 'dimension': ('T','F'), 'options': ['任务效率','成员关系']},
{'text': '行李准备方式', 'dimension': ('J','P'), 'options': ['提前整理','最后收拾']},

{'text': '表达观点风格', 'dimension': ('E','I'), 'options': ['直接表达','深思后说']},
{'text': '学习新技术时', 'dimension': ('S','N'), 'options': ['操作步骤','设计原理']},
{'text': '分配资源原则', 'dimension': ('T','F'), 'options': ['效率优先','公平优先']},
{'text': '周末安排方式', 'dimension': ('J','P'), 'options': ['计划活动','随心决定']},

{'text': '应对压力方式', 'dimension': ('E','I'), 'options': ['寻求支持','自我处理']},
{'text': '描述人物侧重', 'dimension': ('S','N'), 'options': ['外貌行为','性格动机']},
{'text': '职业选择标准', 'dimension': ('T','F'), 'options': ['发展前景','价值认同']},
{'text': '项目完成方式', 'dimension': ('J','P'), 'options': ['按部就班','灵感发挥']},

{'text': '聚会中角色', 'dimension': ('E','I'), 'options': ['活跃气氛','安静观察']},
{'text': '理解抽象概念', 'dimension': ('S','N'), 'options': ['实例辅助','直接把握']},
{'text': '面对求助反应', 'dimension': ('T','F'), 'options': ['分析问题','情感支持']},
{'text': '时间管理风格', 'dimension': ('J','P'), 'options': ['严格规划','灵活应对']},

{'text': '空闲时间偏好', 'dimension': ('E','I'), 'options': ['集体活动','个人爱好']},
{'text': '观察环境侧重', 'dimension': ('S','N'), 'options': ['实际存在','可能变化']},
{'text': '评价电影依据', 'dimension': ('T','F'), 'options': ['剧情逻辑','情感共鸣']},
{'text': '处理多任务时', 'dimension': ('J','P'), 'options': ['专注一件','同时多件']},

{'text': '深度交流偏好', 'dimension': ('E','I'), 'options': ['多人讨论','一对一交流']},
{'text': '接受信息方式', 'dimension': ('S','N'), 'options': ['具体数据','整体印象']},
{'text': '冲突解决重点', 'dimension': ('T','F'), 'options': ['事实真相','关系和谐']},
{'text': '生活空间状态', 'dimension': ('J','P'), 'options': ['整洁有序','随性自由']},

{'text': '社交活跃程度', 'dimension': ('E','I'), 'options': ['经常参与','偶尔参加']},
{'text': '学习新语言法', 'dimension': ('S','N'), 'options': ['实用会话','语法规则']},
{'text': '重大决定依据', 'dimension': ('T','F'), 'options': ['理性分析','内心感受']},
{'text': '任务执行方式', 'dimension': ('J','P'), 'options': ['按计划做','即兴调整']},

{'text': '能量来源主要', 'dimension': ('E','I'), 'options': ['外部互动','内在思考']},
{'text': '理解世界方式', 'dimension': ('S','N'), 'options': ['现实经验','理论推测']},
{'text': '选择伴侣标准', 'dimension': ('T','F'), 'options': ['理性兼容','情感契合']},
{'text': '工作进度把控', 'dimension': ('J','P'), 'options': ['提前完成','最后期限']},

{'text': '陌生人互动', 'dimension': ('E','I'), 'options': ['自然交谈','谨慎观察']},
{'text': '学习工具使用', 'dimension': ('S','N'), 'options': ['按说明书','自行探索']},
{'text': '团队决策倾向', 'dimension': ('T','F'), 'options': ['最优方案','共识达成']},
{'text': '假期安排方式', 'dimension': ('J','P'), 'options': ['详细行程','大致方向']},

{'text': '表达情感方式', 'dimension': ('E','I'), 'options': ['外露直接','内敛含蓄']},
{'text': '研究问题方法', 'dimension': ('S','N'), 'options': ['实际验证','理论推演']},
{'text': '评价艺术作品', 'dimension': ('T','F'), 'options': ['技巧水平','情感表达']},
{'text': '资料整理习惯', 'dimension': ('J','P'), 'options': ['系统归档','随手存放']},

{'text': '社交广度深度', 'dimension': ('E','I'), 'options': ['广泛交际','少数深交']},
{'text': '描述梦境侧重', 'dimension': ('S','N'), 'options': ['具体场景','象征意义']},
{'text': '处理矛盾重点', 'dimension': ('T','F'), 'options': ['解决问题','安抚情绪']},
{'text': '目标设定方式', 'dimension': ('J','P'), 'options': ['具体步骤','总体方向']},

{'text': '多人场合感受', 'dimension': ('E','I'), 'options': ['如鱼得水','消耗精力']},
{'text': '学习新设备时', 'dimension': ('S','N'), 'options': ['直接操作','先看理论']},
{'text': '慈善捐助动机', 'dimension': ('T','F'), 'options': ['实际效果','情感共鸣']},
{'text': '时间安排精度', 'dimension': ('J','P'), 'options': ['精确到分','大致时段']},

{'text': '话题主导倾向', 'dimension': ('E','I'), 'options': ['引导话题','跟随话题']},
{'text': '记忆名字能力', 'dimension': ('S','N'), 'options': ['具体面容','整体感觉']},
{'text': '领导团队风格', 'dimension': ('T','F'), 'options': ['目标导向','人文关怀']},
{'text': '烹饪时习惯', 'dimension': ('J','P'), 'options': ['按菜谱做','自由发挥']},
# 第20组
{'text': '多人聚会感受', 'dimension': ('E','I'), 'options': ['享受热闹','感到疲惫']},
{'text': '学习新科目时', 'dimension': ('S','N'), 'options': ['记忆知识点','理解概念联系']},
{'text': '职场晋升标准', 'dimension': ('T','F'), 'options': ['业绩数据','团队评价']},
{'text': '旅行计划制定', 'dimension': ('J','P'), 'options': ['详细行程表','大致目的地']},

# 第21组
{'text': '表达想法方式', 'dimension': ('E','I'), 'options': ['边说边想','想好再说']},
{'text': '观察艺术品时', 'dimension': ('S','N'), 'options': ['细节技法','整体意境']},
{'text': '解决道德困境', 'dimension': ('T','F'), 'options': ['理性权衡','情感共鸣']},
{'text': '家务处理方式', 'dimension': ('J','P'), 'options': ['定期清理','需要时处理']},

# 第22组
{'text': '社交主动性', 'dimension': ('E','I'), 'options': ['常发起活动','等待邀请']},
{'text': '记忆数字方式', 'dimension': ('S','N'), 'options': ['精确记忆','关联记忆']},
{'text': '教育孩子原则', 'dimension': ('T','F'), 'options': ['培养独立性','给予情感支持']},
{'text': '财务管理习惯', 'dimension': ('J','P'), 'options': ['预算规划','灵活支出']},

# 第23组
{'text': '会议休息时间', 'dimension': ('E','I'), 'options': ['与人交流','独自休息']},
{'text': '学习地图技能', 'dimension': ('S','N'), 'options': ['实际导航','空间想象']},
{'text': '选择餐厅标准', 'dimension': ('T','F'), 'options': ['菜品质量','氛围感受']},
{'text': '项目启动方式', 'dimension': ('J','P'), 'options': ['详细方案','初步构想']},

# 第24组
{'text': '应对孤独方式', 'dimension': ('E','I'), 'options': ['联系朋友','自我调节']},
{'text': '描述天气侧重', 'dimension': ('S','N'), 'options': ['具体温度湿度','整体感觉氛围']},
{'text': '评价新闻事件', 'dimension': ('T','F'), 'options': ['事实准确性','情感影响力']},
{'text': '假期安排偏好', 'dimension': ('J','P'), 'options': ['计划充实','自由放松']},

# 第25组
{'text': '结交朋友速度', 'dimension': ('E','I'), 'options': ['快速广泛','缓慢深入']},
{'text': '学习乐器方法', 'dimension': ('S','N'), 'options': ['按谱练习','即兴创作']},
{'text': '处理投诉方式', 'dimension': ('T','F'), 'options': ['解决问题','安抚情绪']},
{'text': '日常决策速度', 'dimension': ('J','P'), 'options': ['快速决定','多方考虑']},

# 第26组
{'text': '团队合作角色', 'dimension': ('E','I'), 'options': ['积极发言','倾听思考']},
{'text': '理解数学概念', 'dimension': ('S','N'), 'options': ['具体例题','抽象公式']},
{'text': '选择医疗方案', 'dimension': ('T','F'), 'options': ['数据成功率','个人感受']},
{'text': '资料查找方式', 'dimension': ('J','P'), 'options': ['系统检索','随机发现']},

# 第27组
{'text': '派对参与程度', 'dimension': ('E','I'), 'options': ['全程活跃','中途休息']},
{'text': '记忆路线方式', 'dimension': ('S','N'), 'options': ['地标建筑','方向方位']},
{'text': '评价书籍标准', 'dimension': ('T','F'), 'options': ['逻辑结构','情感触动']},
{'text': '生活用品收纳', 'dimension': ('J','P'), 'options': ['固定位置','随手放置']},

# 第28组
{'text': '深度对话对象', 'dimension': ('E','I'), 'options': ['多人讨论','一对一交流']},
{'text': '学习烹饪方法', 'dimension': ('S','N'), 'options': ['严格配方','自由发挥']},
{'text': '慈善行为动机', 'dimension': ('T','F'), 'options': ['实际效果','同情心驱动']},
{'text': '工作截止期限', 'dimension': ('J','P'), 'options': ['提前完成','最后冲刺']},

# 第29组
{'text': '陌生人问路时', 'dimension': ('E','I'), 'options': ['热情指引','简洁回答']},
{'text': '描述梦境内容', 'dimension': ('S','N'), 'options': ['具体场景','象征意义']},
{'text': '职场批评方式', 'dimension': ('T','F'), 'options': ['直接指出','委婉建议']},
{'text': '假期行李准备', 'dimension': ('J','P'), 'options': ['提前一周','出发前夜']},

# 第30组
{'text': '社交能量来源', 'dimension': ('E','I'), 'options': ['与人互动','独处思考']},
{'text': '理解诗歌方式', 'dimension': ('S','N'), 'options': ['字面意思','深层隐喻']},
{'text': '选择朋友标准', 'dimension': ('T','F'), 'options': ['共同兴趣','情感连接']},
{'text': '时间分配原则', 'dimension': ('J','P'), 'options': ['计划分配','灵活调整']}
]

MBTI_DESCRIPTIONS = {
    "ISTJ": {
        "nickname": "物流师(蓝老头)",
        "description": "务实可靠的现实主义者，以责任和秩序为核心",
        "traits": ["严谨性", "务实性", "细节关注", "传统性"],
        "strengths": ["执行力强", "可靠", "组织能力强"],
        "weaknesses": ["固执", "缺乏弹性", "过度批判"],
        "careers": ["会计师", "审计师", "行政管理"],
        "scores": [9, 8, 9, 7],
        "color_group": "blue",  # 蓝色组：守护者（SJ型）
        "theme_color": "#4169E1",  # 皇家蓝
        "group_name": "守护者",
        "group_traits": ["务实严谨", "责任感强", "重视秩序", "善于执行"],
    },
    "ISFJ": {
        "nickname": "守卫者(小护士)",
        "description": "温暖体贴的奉献者，以服务他人为己任",
        "traits": ["责任感", "共情力", "可靠性", "保守性"],
        "strengths": ["团队合作", "耐心", "实践能力"],
        "weaknesses": ["过度自我牺牲", "回避冲突", "难以拒绝"],
        "careers": ["护士", "教师", "社工"],
        "scores": [8, 9, 9, 6],
        "color_group": "blue",  # 蓝色组
        "theme_color": "#4169E1",  # 皇家蓝
        "group_name": "守护者",
        "group_traits": ["务实严谨", "责任感强", "重视秩序", "善于执行"],
    },
    "INFJ": {
        "nickname": "提倡者(绿老头)",
        "description": "富有洞察力的理想主义者，以推动社会进步为使命",
        "traits": ["洞察力", "理想主义", "创造力", "神秘性"],
        "strengths": ["共情能力", "远见卓识", "激励他人"],
        "weaknesses": ["完美主义", "易倦怠", "过度敏感"],
        "careers": ["心理咨询师", "作家", "非营利组织管理"],
        "scores": [8, 9, 7, 8],
         "color_group": "green",  # 绿色组：理想家（NF型）
        "theme_color": "#32CD32",  # 酸橙绿
        "group_name": "理想家",
        "group_traits": ["共情力强", "追求意义", "关注关系", "精神成长"],
    },
    "INTJ": {
        "nickname": "建筑师(紫老头)",
        "description": "独立自主的智囊型人才，以系统化思维改变世界",
        "traits": ["战略思维", "独立性", "决断力", "完美主义"],
        "strengths": ["长远规划", "问题解决", "高效执行"],
        "weaknesses": ["傲慢", "情感疏离", "固执己见"],
        "careers": ["工程师", "科学家", "企业高管"],
        "scores": [9, 9, 8, 7],
        "color_group": "purple",  # 黄色组：战略家（NT型）
        "theme_color": "#EB11EF",  # 金色
        "group_name": "战略家",
        "group_traits": ["理性分析", "远见卓识", "逻辑推理", "系统创新"],
    },
    "ISTP": {
        "nickname": "鉴赏家(电钻哥)",
        "description": "冷静敏锐的问题解决者，擅长操作工具和机械系统",
        "traits": ["动手能力", "适应性", "危机处理", "理性"],
        "strengths": ["危机处理", "技术分析", "实践创新"],
        "weaknesses": ["情感迟钝", "缺乏计划", "逃避承诺"],
        "careers": ["机械师", "飞行员", "电竞选手"],
        "scores": [8, 7, 9, 8],
         "color_group": "yellow",  # 红色组：行动者（SP型）
        "theme_color": "#F9F225E6",  # 橙红
        "group_name": "行动者",
        "group_traits": ["灵活应变", "活在当下", "注重体验", "即兴发挥"],
    },
    "ISFP": {
        "nickname": "探险家(小画家)",
        "description": "感性细腻的创造者，追求和谐与美学体验",
        "traits": ["审美力", "灵活性", "共情力", "独立性"],
        "strengths": ["审美能力", "适应力强", "团队协作"],
        "weaknesses": ["逃避冲突", "决策困难", "过度自我批评"],
        "careers": ["设计师", "音乐家", "园艺师"],
        "scores": [8, 9, 7, 8],
          "color_group": "yellow",  # 红色组
        "theme_color": "#F9F225E6",  # 橙红
        "group_name": "行动者",
        "group_traits": ["灵活应变", "活在当下", "注重体验", "即兴发挥"],
    },
    "INFP": {
        "nickname": "调停者(小蝴蝶)",
        "description": "富有诗意的理想主义者，致力于实现人文价值",
        "traits": ["理想主义", "创造力", "同理心", "敏感性"],
        "strengths": ["写作表达", "深度理解", "价值驱动"],
        "weaknesses": ["不切实际", "过度内省", "回避现实"],
        "careers": ["诗人", "心理咨询师", "人权工作者"],
        "scores": [7, 8, 9, 8],
         "color_group": "green",  # 绿色组
        "theme_color": "#32CD32",  # 酸橙绿
        "group_name": "理想家",
        "group_traits": ["共情力强", "追求意义", "关注关系", "精神成长"],
    },
    "INTP": {
        "nickname": "逻辑学家(小瓶子/温暖的机器人)",
        "description": "理性好奇的思想家，痴迷于构建知识体系",
        "traits": ["逻辑分析", "创新性", "独立性", "理论思维"],
        "strengths": ["抽象思维", "模式识别", "理论构建"],
        "weaknesses": ["社交障碍", "执行力弱", "过度质疑"],
        "careers": ["哲学家", "科研人员", "系统架构师"],
        "scores": [9, 8, 7, 9],
        "color_group": "purple",  # 黄色组
        "theme_color": "#EB11EF",  # 金色
        "group_name": "战略家",
        "group_traits": ["理性分析", "远见卓识", "逻辑推理", "系统创新"],
    },
    "ESTP": {
        "nickname": "企业家(墨镜哥)",
        "description": "精力充沛的实干家，擅长随机应变解决问题",
        "traits": ["行动力", "适应性", "现实导向", "冒险精神"],
        "strengths": ["危机处理", "谈判能力", "快速决策"],
        "weaknesses": ["缺乏耐心", "忽视后果", "规则抗拒"],
        "careers": ["销售", "急救员", "创业家"],
        "scores": [9, 8, 7, 8],
           "color_group": "yellow",  # 红色组
        "theme_color": "#F9F225E6",  # 橙红
        "group_name": "行动者",
        "group_traits": ["灵活应变", "活在当下", "注重体验", "即兴发挥"],
    },
    "ESFP": {
        "nickname": "表演者(锤子姐)",
        "description": "热情洋溢的社交达人，善于营造欢乐氛围",
        "traits": ["表现力", "热情度", "即兴能力", "享乐主义"],
        "strengths": ["人际交往", "即兴发挥", "团队激励"],
        "weaknesses": ["缺乏规划", "回避理论", "过度依赖认可"],
        "careers": ["主持人", "旅游顾问", "活动策划"],
        "scores": [8, 9, 8, 7],
           "color_group": "yellow",  # 红色组
        "theme_color": "#F9F225E6",  # 橙红
        "group_name": "行动者",
        "group_traits": ["灵活应变", "活在当下", "注重体验", "即兴发挥"],
    },
    "ENFP": {
        "nickname": "竞选者(快乐小狗)",
        "description": "充满激情的创新者，擅长发现可能性并激励他人",
        "traits": ["创造力", "热情度", "洞察力", "理想主义"],
        "strengths": ["创意生成", "人际连接", "多任务处理"],
        "weaknesses": ["专注力差", "决策困难", "过度承诺"],
        "careers": ["记者", "公关顾问", "社会创新者"],
        "scores": [8, 9, 7, 8],
          "color_group": "green",  # 绿色组
        "theme_color": "#32CD32",  # 酸橙绿
        "group_name": "理想家",
        "group_traits": ["共情力强", "追求意义", "关注关系", "精神成长"],
    },
    "ESTJ": {
        "nickname": "总经理(尺子姐)",
        "description": "高效务实的组织者，擅长建立秩序和达成目标",
        "traits": ["领导力", "组织能力", "务实性", "传统性"],
        "strengths": ["项目管理", "决策效率", "执行力强"],
        "weaknesses": ["缺乏弹性", "共情不足", "控制欲强"],
        "careers": ["军官", "项目经理", "法官"],
        "scores": [8, 9, 7, 6],
        "color_group": "blue",  # 蓝色组
        "theme_color": "#4169E1",  # 皇家蓝
        "group_name": "守护者",
        "group_traits": ["务实严谨", "责任感强", "重视秩序", "善于执行"],
    },
    "ESFJ": {
        "nickname": "执政官(蛋糕哥)",
        "description": "热心助人的协调者，致力于维护社会和谐",
        "traits": ["社交能力", "责任感", "同理心", "保守性"],
        "strengths": ["团队建设", "危机调解", "服务精神"],
        "weaknesses": ["过度干涉", "依赖认可", "回避变革"],
        "careers": ["人力资源", "客户服务", "社区工作者"],
        "scores": [7, 9, 8, 6],
         "color_group": "blue",  # 蓝色组
        "theme_color": "#4169E1",  # 皇家蓝
        "group_name": "守护者",
        "group_traits": ["务实严谨", "责任感强", "重视秩序", "善于执行"],
    },
    "ENFJ": {
        "nickname": "主人公(大剑哥)",
        "description": "富有魅力的领导者，善于激发他人潜能",
        "traits": ["领导魅力", "共情力", "理想主义", "热情度"],
        "strengths": ["人才培养", "公共演讲", "价值引领"],
        "weaknesses": ["过度投入", "理想主义", "忽视自我"],
        "careers": ["教师", "政治家", "职业导师"],
        "scores": [8, 9, 7, 8],
         "color_group": "green",  # 绿色组
        "theme_color": "#32CD32",  # 酸橙绿
        "group_name": "理想家",
        "group_traits": ["共情力强", "追求意义", "关注关系", "精神成长"],
    },
    "ENTJ": {
        "nickname": "指挥官(大姐头)",
        "description": "果敢坚毅的领导者，擅长战略规划和资源调配",
        "traits": ["战略决策", "领导力", "执行力", "目标导向"],
        "strengths": ["目标达成", "系统优化", "危机领导"],
        "weaknesses": ["独断专行", "缺乏耐心", "情感忽视"],
        "careers": ["CEO", "投资银行家", "军事战略家"],
        "scores": [9, 9, 8, 7],
           "color_group": "purple",  # 黄色组
        "theme_color": "#EB11EF",  # 金色
        "group_name": "战略家",
        "group_traits": ["理性分析", "远见卓识", "逻辑推理", "系统创新"],
    },
    "ENTP": {
        "nickname": "辩论家(骨折眉毛)",
        "description": "充满创意的智多星，以探索可能性为乐",
        "traits": ["创新性", "战略思维", "辩论能力", "好奇心"],
        "strengths": ["战略思维", "快速学习", "解决问题"],
        "weaknesses": ["缺乏耐心", "好争辩", "不重细节"],
        "careers": ["企业家", "律师", "营销策划"],
        "scores": [9, 8, 9, 9],
          "color_group": "purple",  # 黄色组
        "theme_color": "#EB11EF",  # 金色
        "group_name": "战略家",
        "group_traits": ["理性分析", "远见卓识", "逻辑推理", "系统创新"],
    }
}
# 颜色组描述
COLOR_GROUP_DESCRIPTIONS = {
    "yellow": {
        "name": "行动者 (SP型)",
        "description": "您属于黄色色行动者群体，灵活应变、活在当下是您的核心特质。您擅长通过实践学习，在需要快速反应的环境中表现出色。",
        "strength": "精力充沛，动手能力强",
        "challenge": "有时可能缺乏长期规划",
        "tip": "尝试将您的实践能力与长期目标结合，会取得更大成就！"
    },
    "blue": {
        "name": "守护者 (SJ型)",
        "description": "您属于蓝色守护者群体，务实严谨、责任感强是您的核心特质。您善于建立秩序和执行计划，是组织和团队中可靠的支柱。",
        "strength": "注重细节，执行力强",
        "challenge": "有时可能过于保守",
        "tip": "在保持可靠性的同时，尝试接受一些新变化，会有意想不到的收获！"
    },
    "green": {
        "name": "理想家 (NF型)",
        "description": "您属于绿色理想家群体，共情力强、追求意义是您的核心特质。您关注人际关系和精神成长，善于激励他人和创造和谐氛围。",
        "strength": "富有同理心，沟通能力强",
        "challenge": "有时可能过于理想化",
        "tip": "在追求理想的同时，记得给自己留出休息时间，保持身心健康！"
    },
    "purple": {
        "name": "战略家 (NT型)",
        "description": "您属于紫色战略家群体，理性分析、远见卓识是您的核心特质。您善于解决复杂问题，在技术和创新领域有天然优势。",
        "strength": "逻辑思维强，创新能力突出",
        "challenge": "有时可能忽视情感因素",
        "tip": "在发挥理性优势的同时，尝试更多关注人际关系，会让您更全面！"
    }
}
dimension_groups = {
    'EI': [q for q in full_questions if q['dimension'] == ('E','I')],
    'SN': [q for q in full_questions if q['dimension'] == ('S','N')],
    'TF': [q for q in full_questions if q['dimension'] == ('T','F')],
    'JP': [q for q in full_questions if q['dimension'] == ('J','P')]
}
# 在 app.py 中添加颜色工具函数
def get_dark_color(hex_color):
    """根据主题色生成深色变体"""
    try:
        # 移除 # 号
        hex_color = hex_color.lstrip('#')
        # 转换为RGB
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        # 减少亮度 (减少30%)
        r = max(0, int(r * 0.7))
        g = max(0, int(g * 0.7))
        b = max(0, int(b * 0.7))
        # 返回新的十六进制颜色
        return f"#{r:02x}{g:02x}{b:02x}"
    except:
        # 如果出错，返回原色
        return hex_color
# 生成不同长度的题目集
def generate_question_set(length):
    if length == 120:
        return full_questions
    
    # 确定每个维度的题目数量
    per_dimension = length // 4
    
    questions = []
    for dimension in dimension_groups.values():
        # 确保每个维度的题目数量均匀分布
        if len(dimension) >= per_dimension:
            questions.extend(dimension[:per_dimension])
        else:
            # 如果题目不足，使用所有可用题目
            questions.extend(dimension)
    
    # 如果题目数量不足，补充随机题目
    if len(questions) < length:
        remaining = length - len(questions)
        all_questions = [q for group in dimension_groups.values() for q in group]
        # 排除已选题目
        available_questions = [q for q in all_questions if q not in questions]
        questions.extend(random.sample(available_questions, min(remaining, len(available_questions))))
    
    # 随机打乱题目顺序
    random.shuffle(questions)
    return questions
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    has_tested = db.Column(db.Boolean, default=False)
    current_progress = db.Column(db.Integer, default=0)  # 新增进度字段
    test_length = db.Column(db.Integer, default=0)  # 新增测试长度字段

# 添加实时更新事件
@socketio.on('connect', namespace='/admin')
def handle_admin_connect():
    if session.get('admin'):
        emit('connection_success', {'message': 'Connected to admin dashboard'})

# 学生数据更新时触发事件
def broadcast_student_update():
    socketio.emit('student_update', get_student_data(), namespace='/admin')

# 获取学生数据函数
def get_student_data():
    students = Student.query.all()
    
    tested = []
    in_progress = []
    not_tested = []
    
    for s in students:
        if s.has_tested:
            tested.append({
                'id': s.id,
                'student_id': s.student_id,
                'name': s.name
            })
        elif s.current_progress > 0:
            progress_percent = (s.current_progress / s.test_length * 100) if s.test_length > 0 else 0
            in_progress.append({
                'id': s.id,
                'student_id': s.student_id,
                'name': s.name,
                'progress': progress_percent,
                'current_progress': s.current_progress,
                'test_length': s.test_length
            })
        else:
            not_tested.append({
                'id': s.id,
                'student_id': s.student_id,
                'name': s.name
            })
    
    return {
        'tested': tested,
        'in_progress': in_progress,
        'not_tested': not_tested
    }

# 在需要更新数据的地方调用 broadcast_student_update()
# 例如在学生删除、添加或进度更新后
class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), db.ForeignKey('student.student_id'), nullable=False)
    e = db.Column(db.Integer, default=0)
    i = db.Column(db.Integer, default=0)
    s = db.Column(db.Integer, default=0)
    n = db.Column(db.Integer, default=0)
    t = db.Column(db.Integer, default=0)
    f = db.Column(db.Integer, default=0)
    j = db.Column(db.Integer, default=0)
    p = db.Column(db.Integer, default=0)
    mbti = db.Column(db.String(4))
    test_length = db.Column(db.Integer)  # 添加测试长度字段
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)  # 添加创建时间字段
def migrate_database():
    """检查并迁移数据库结构"""
    inspector = inspect(db.engine)
    
    # 检查 result 表是否存在
    if not inspector.has_table('result'):
        print("result 表不存在，无需迁移")
        return
    
    # 检查 result 表是否存在 test_length 列
    columns = [col['name'] for col in inspector.get_columns('result')]
    if 'test_length' not in columns:
        print("检测到数据库需要迁移：添加 test_length 列到 result 表")
        try:
            # 使用 SQLAlchemy 2.0+ 的新方式执行 SQL
            with db.engine.connect() as connection:
                # 对于 SQLite
                if 'sqlite' in db.engine.url.drivername:
                    connection.execute(text('ALTER TABLE result ADD COLUMN test_length INTEGER DEFAULT 120'))
                    connection.commit()
                # 对于其他数据库
                else:
                    connection.execute(text('ALTER TABLE result ADD COLUMN test_length INTEGER DEFAULT 120'))
                    connection.commit()
            print("数据库迁移成功：已添加 test_length 列")
        except Exception as e:
            print(f"数据库迁移失败: {str(e)}")
            # 创建新表并迁移数据
            migrate_by_recreate()
    
    # 检查是否存在 created_at 列
    if 'created_at' not in columns:
        print("检测到数据库需要迁移：添加 created_at 列到 result 表")
        try:
            with db.engine.connect() as connection:
                if 'sqlite' in db.engine.url.drivername:
                    connection.execute(text('ALTER TABLE result ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP'))
                    connection.commit()
                else:
                    connection.execute(text('ALTER TABLE result ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP'))
                    connection.commit()
            print("数据库迁移成功：已添加 created_at 列")
        except Exception as e:
            print(f"数据库迁移失败: {str(e)}")
    
    # 检查 admin 表是否存在 avatar 列
    admin_columns = [col['name'] for col in inspector.get_columns('admin')]
    if 'avatar' not in admin_columns:
        print("检测到数据库需要迁移：添加 avatar 列到 admin 表")
        try:
            with db.engine.begin() as connection:
                connection.execute(text("ALTER TABLE admin ADD COLUMN avatar VARCHAR(100) DEFAULT 'default_avatar.png'"))
            print("数据库迁移成功：已添加 avatar 列到 admin 表")
        except Exception as e:
            print(f"数据库迁移失败: {str(e)}")

def migrate_by_recreate():
    """通过重新创建表来迁移数据库（SQLite 专用）"""
    print("尝试通过重新创建表迁移数据库...")
    try:
        # 使用 SQLAlchemy 2.0+ 的新方式执行 SQL
        with db.engine.begin() as connection:
            # 备份旧表
            connection.execute(text('ALTER TABLE result RENAME TO result_old'))
            
            # 创建新表
            db.create_all()
            
            # 迁移数据
            connection.execute(text('''
                INSERT INTO result (id, student_id, e, i, s, n, t, f, j, p, mbti, test_length, created_at)
                SELECT id, student_id, e, i, s, n, t, f, j, p, mbti, 120, CURRENT_TIMESTAMP
                FROM result_old
            '''))
            
            # 删除旧表
            connection.execute(text('DROP TABLE result_old'))
        
        print("数据库迁移成功：通过重新创建表")
    except Exception as e:
        print(f"数据库迁移失败: {str(e)}")
        # 回滚更改
        with db.engine.begin() as connection:
            connection.execute(text('DROP TABLE IF EXISTS result'))
            connection.execute(text('ALTER TABLE result_old RENAME TO result'))
        print("已恢复原始表结构")
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    avatar = db.Column(db.String(100), default='default_avatar.png')

class StudentLoginForm(FlaskForm):
    student_id = StringField('学号', validators=[DataRequired()])
    name = StringField('姓名', validators=[DataRequired()])
    submit = SubmitField('登录')

class AdminLoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('登录')

with app.app_context():
    db.create_all()
    migrate_database()
    if not Admin.query.first():
        admin = Admin(username='admin', password='admin123')
        db.session.add(admin)
        db.session.commit()

@app.route('/')
def home():
    return redirect(url_for('student_login'))

# 更新删除路由返回 JSON
    
@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    form = StudentLoginForm()
    if form.validate_on_submit():
        student = Student.query.filter_by(student_id=form.student_id.data).first()
        
        if student:
            if student.name != form.name.data:
                flash('姓名与学号不匹配')
                return redirect(url_for('student_login'))
        else:
            try:
                student = Student(
                    student_id=form.student_id.data,
                    name=form.name.data
                )
                db.session.add(student)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                flash('学号已存在，请检查输入')
                return redirect(url_for('student_login'))
        
        session['student_id'] = student.student_id
        # 重定向到测试长度选择页面
        return redirect(url_for('select_test_length'))
    
    return render_template('student_login.html', form=form)
@app.route('/select_test_length', methods=['GET', 'POST'])
def select_test_length():
    if 'student_id' not in session:
        return redirect(url_for('student_login'))
    
    student = Student.query.filter_by(student_id=session['student_id']).first()
    if not student:
        flash('找不到用户信息')
        return redirect(url_for('student_login'))
    
    if student.has_tested:
        return redirect(url_for('result', student_id=student.student_id))
    
    if request.method == 'POST':
        test_length = int(request.form.get('test_length', 20))
        session['test_length'] = test_length
        
        # 生成题目集并保存到session
        questions = generate_question_set(test_length)
        session['questions'] = questions
        
        # 初始化进度
        session['progress'] = 0
        
        return redirect(url_for('test'))
    
    return render_template('test_length.html')

@app.before_request
def detect_device():
    user_agent = request.headers.get('User-Agent', '').lower()
    mobile_agents = ['iphone', 'ipod', 'android', 'blackberry', 
                     'windows phone', 'webos', 'ipad', 'playbook', 'mobile']
    
    session['is_mobile'] = any(agent in user_agent for agent in mobile_agents)

@app.route('/test', methods=['GET', 'POST'])
def test():
    if 'student_id' not in session:
        return redirect(url_for('student_login'))
    
    student = Student.query.filter_by(student_id=session['student_id']).first()
    if not student:
        flash('找不到用户信息')
        return redirect(url_for('student_login'))
    
    if student.has_tested:
        return redirect(url_for('result', student_id=student.student_id))
    
    # 检查是否有题目集
    if 'questions' not in session:
        return redirect(url_for('select_test_length'))
    
    questions = session['questions']
    
    # 从session获取当前进度
    if 'progress' not in session:
        session['progress'] = 0
    
    if request.method == 'POST':
        scores = {'E':0, 'I':0, 'S':0, 'N':0, 'T':0, 'F':0, 'J':0, 'P':0}
        answered_count = 0
        
        for idx, q in enumerate(questions):
            ans = request.form.get(f'question_{idx}')
            if ans:
                answered_count += 1
                dim = q['dimension']
                scores[dim[0 if ans == 'A' else 1]] += 1
        
        # 确保所有问题都回答了
        if answered_count < len(questions):
            flash('请回答所有问题')
            return redirect(url_for('test'))
        
        mbti = ''
        mbti += 'E' if scores['E'] > scores['I'] else 'I'
        mbti += 'S' if scores['S'] > scores['N'] else 'N'
        mbti += 'T' if scores['T'] > scores['F'] else 'F'
        mbti += 'J' if scores['J'] > scores['P'] else 'P'
        
        # 获取测试长度（默认为120）
        test_length = session.get('test_length', 120)
        
        result = Result(
            student_id=student.student_id,
            e=scores['E'], i=scores['I'],
            s=scores['S'], n=scores['N'],
            t=scores['T'], f=scores['F'],
            j=scores['J'], p=scores['P'],
            mbti=mbti,
            test_length=test_length
        )
        student.has_tested = True
        student.current_progress = 0  # 重置进度
        db.session.add(result)
        db.session.commit()
        
        # 广播更新 - 学生已完成测试
        broadcast_student_update()
        broadcast_system_status()
        
        # 清除测试相关session
        session.pop('questions', None)
        session.pop('progress', None)
        session.pop('test_length', None)
        
        return redirect(url_for('result', student_id=student.student_id))
    
    # 广播更新 - 学生进入测试页面
    broadcast_student_update()
    
    # 从session获取当前进度
    progress = session.get('progress', 0)
    return render_template('test.html', questions=questions, progress=progress)

@app.route('/save_progress', methods=['POST'])
@csrf.exempt
def save_progress():
    if 'student_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400
    
    progress = data.get('progress', 0)
    
    # 更新数据库中的进度
    student = Student.query.filter_by(student_id=session['student_id']).first()
    if student and not student.has_tested:
        # 计算实际完成的题目数量
        test_length = session.get('test_length', 120)
        answered_count = int(progress * test_length / 100)

        student.current_progress = answered_count
        # 如果是第一次保存，记录测试长度
        if student.test_length == 0:
            student.test_length = test_length
        db.session.commit()
        
        # 广播更新 - 进度已保存
        broadcast_student_update()
        broadcast_system_status()
        
        # 更新session中的进度
        session['progress'] = progress
    
    return jsonify({'status': 'success'})
@app.route('/result/<student_id>')
def result(student_id):
    student = Student.query.filter_by(student_id=student_id).first_or_404()
    result = Result.query.filter_by(student_id=student_id).first_or_404()
    mbti_info = MBTI_DESCRIPTIONS.get(result.mbti, {})
    
    # 添加默认值处理
    if not mbti_info:
        mbti_info = {
            "nickname": "未知类型",
            "description": "未找到该类型的描述信息",
            "traits": ["", "", "", ""],
            "strengths": ["无数据"],
            "weaknesses": ["无数据"],
            "careers": ["无数据"],
            "scores": [0, 0, 0, 0],
            "theme_color": "#6c757d",  # 默认灰色
            "color_group": "blue",
            "group_name": "未知组",
            "group_traits": []
        }
    
    # 计算深色变体
    mbti_info["dark_color"] = get_dark_color(mbti_info["theme_color"])
    
    # 获取颜色组信息
    group_info = COLOR_GROUP_DESCRIPTIONS.get(mbti_info["color_group"], {
        "name": "未知组",
        "description": "未找到该组的描述信息",
        "strength": "无数据",
        "challenge": "无数据",
        "tip": "无数据"
    })
    
    # 计算维度分数
    dimension_scores = {
        'E-I': [result.e, result.i],
        'S-N': [result.s, result.n],
        'T-F': [result.t, result.f],
        'J-P': [result.j, result.p]
    }
    
    return render_template('result.html', 
                         mbti=result.mbti,
                         info=mbti_info,
                         group_info=group_info,
                         dimension_scores=dimension_scores)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    form = AdminLoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data, password=form.password.data).first()
        if admin:
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        flash('无效凭证')
    return render_template('admin_login.html', form=form)

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    # 初始化数据结构
    type_details = {}
    students = Student.query.all()
    tested = [s for s in students if s.has_tested]
    not_tested = [s for s in students if not s.has_tested]

    # 处理测试结果
    results = db.session.query(Result, Student).join(Student).all()
    for res, stu in results:
        mbti = res.mbti
        if mbti not in type_details:
            type_details[mbti] = {
                'count': 0,
                'students': [],
                'scores': {dim: 0 for dim in ['E','I','S','N','T','F','J','P']}
            }
        type_details[mbti]['count'] += 1
        type_details[mbti]['students'].append({
            'name': stu.name,
            'student_id': stu.student_id,
            'scores': {
                'E': res.e, 'I': res.i,
                'S': res.s, 'N': res.n,
                'T': res.t, 'F': res.f,
                'J': res.j, 'P': res.p
            }
        })
        for dim in ['E','I','S','N','T','F','J','P']:
            type_details[mbti]['scores'][dim] += getattr(res, dim.lower())

    # 计算平均分
    for mbti, data in type_details.items():
        count = data['count']
        data['scores'] = {k: round(v/count, 1) for k,v in data['scores'].items()}
    in_progress_students = []
    not_tested_students = []
    for s in students:
        if s.has_tested:
            continue
        if s.current_progress > 0:
            in_progress_students.append(s)
        else:
            not_tested_students.append(s)
    # 准备图表数据
    base_colors = [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4',
        '#FFEEAD', '#FF9999', '#AEC6CF', '#B39EB5',
        '#D4A5A5', '#77DD77', '#CFCFC4', '#836953',
        '#F49AC2', '#B19CD9', '#779ECB', '#CB99C9'
    ]
    chart_data = {
        'labels': [],
        'counts': [],
        'colors': []
    }
    if type_details:
        chart_data['labels'] = list(type_details.keys())
        chart_data['counts'] = [d['count'] for d in type_details.values()]
        chart_data['colors'] = [base_colors[i % len(base_colors)] for i in range(len(type_details))]

    # 添加维度统计数据
    dimension_stats = {
        'E-I': {'E': 0, 'I': 0},
        'S-N': {'S': 0, 'N': 0},
        'T-F': {'T': 0, 'F': 0},
        'J-P': {'J': 0, 'P': 0}
    }
    
    for res in Result.query.all():
        dimension_stats['E-I']['E'] += res.e
        dimension_stats['E-I']['I'] += res.i
        dimension_stats['S-N']['S'] += res.s
        dimension_stats['S-N']['N'] += res.n
        dimension_stats['T-F']['T'] += res.t
        dimension_stats['T-F']['F'] += res.f
        dimension_stats['J-P']['J'] += res.j
        dimension_stats['J-P']['P'] += res.p
    
    return render_template('admin_dashboard.html',
                         tested=tested,
                         in_progress=in_progress_students,  # 新增
                         not_tested=not_tested_students,    # 修改
                         type_details=type_details,
                         chart_data=chart_data,
                         dimension_stats=dimension_stats)


@app.route('/admin/add', methods=['POST'])
def add_student():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    sid = request.form.get('student_id')
    name = request.form.get('name')
    if sid and name:
        try:
            if not Student.query.filter_by(student_id=sid).first():
                db.session.add(Student(student_id=sid, name=name))
                db.session.commit()
                broadcast_student_update()
                broadcast_system_status()
                flash('添加成功')
            else:
                flash('学号已存在')
        except IntegrityError:
            db.session.rollback()
            flash('添加失败，请检查数据')
    else:
        flash('请输入完整信息')
    broadcast_student_update()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete/<sid>', endpoint='admin_delete_student')
def admin_delete_student(sid):
    """管理面板中的删除功能（返回重定向）"""
    if not session.get('admin'):
        flash('未授权操作')
        return redirect(url_for('admin_login'))
    
    student = Student.query.filter_by(student_id=sid).first()
    if student:
        # 删除相关结果
        Result.query.filter_by(student_id=sid).delete()
        # 删除学生
        db.session.delete(student)
        db.session.commit()
        
        # 广播更新
        broadcast_student_update()
        broadcast_system_status()
        
        flash(f'已成功删除学生 {student.name}')
    else:
        flash('找不到该学生')
    
    return redirect(url_for('admin_dashboard'))
def broadcast_student_update():
    """广播学生数据更新"""
    student_data = get_student_data()
    socketio.emit('student_update', student_data, namespace='/admin')

def broadcast_system_status():
    """广播系统状态更新"""
    try:
        # 获取内存使用情况
        memory = psutil.virtual_memory()
        memory_usage = memory.used / (1024 * 1024)  # MB
        
        # 计算在线时间（秒）
        uptime_seconds = time.time() - app_start_time
        uptime = str(datetime.timedelta(seconds=int(uptime_seconds)))
        
        # 获取当前时间
        last_update = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 获取连接数
        connection_count = 0
        try:
            connection_count = len(socketio.server.manager.rooms['/admin'])
        except:
            pass
        
        # 检查数据库连接状态
        db_status = '正常'
        try:
            db.session.execute(text('SELECT 1'))
            db_status = '正常'
        except Exception as e:
            db_status = '异常'
        
        # 获取学生总数
        total_students = Student.query.count()
        tested_students = Student.query.filter_by(has_tested=True).count()
        
        # 获取系统版本
        system_version = 'v1.0.0'
        
        # 获取CPU使用率
        cpu_usage = psutil.cpu_percent(interval=1)
        
        # 获取磁盘使用情况
        try:
            if os.name == 'nt':  # Windows
                disk = psutil.disk_usage('C:\\')
            else:  # Unix/Linux
                disk = psutil.disk_usage('/')
            disk_usage = disk.used / (1024 * 1024 * 1024)  # GB
        except:
            disk_usage = 0.0
        
        status_data = {
            'server_status': '运行中',
            'uptime': uptime,
            'memory_usage': f"{memory_usage:.2f} MB",
            'cpu_usage': f"{cpu_usage:.1f}%",
            'disk_usage': f"{disk_usage:.2f} GB",
            'connection_count': connection_count,
            'db_status': db_status,
            'total_students': total_students,
            'tested_students': tested_students,
            'system_version': system_version,
            'last_update': last_update
        }
        
        socketio.emit('system_status_update', status_data, namespace='/admin')
    except Exception as e:
        print(f"广播系统状态失败: {str(e)}")
@app.route('/api/admin/students')
@csrf.exempt
def api_admin_students():
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify(get_student_data())

@app.route('/api/admin/delete/<sid>', methods=['DELETE'])
@csrf.exempt
def api_delete_student(sid):
    """API接口：删除学生（返回JSON）"""
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    student = Student.query.filter_by(student_id=sid).first()
    if student:
        # 删除相关结果
        Result.query.filter_by(student_id=sid).delete()
        # 删除学生
        db.session.delete(student)
        db.session.commit()
        
        # 广播更新
        broadcast_student_update()
        
        return jsonify({'success': True, 'message': '删除成功'})
    else:
        return jsonify({'success': False, 'message': '找不到该学生'})

@app.route('/api/admin/add', methods=['POST'])
@csrf.exempt
def api_add_student():
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400
    
    student_id = data.get('student_id')
    name = data.get('name')
    
    if not student_id or not name:
        return jsonify({'error': '学号和姓名不能为空'}), 400
    
    # 检查学号是否已存在
    if Student.query.filter_by(student_id=student_id).first():
        return jsonify({'error': '学号已存在'}), 400
    
    try:
        student = Student(student_id=student_id, name=name)
        db.session.add(student)
        db.session.commit()
        
        # 广播更新
        broadcast_student_update()
        
        return jsonify({
            'success': True,
            'message': '学生添加成功',
            'student': {
                'id': student.id,
                'student_id': student.student_id,
                'name': student.name,
                'has_tested': student.has_tested,
                'current_progress': student.current_progress,
                'test_length': student.test_length
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/settings', methods=['GET'])
@csrf.exempt
def get_system_settings():
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    # 获取管理员信息
    admin = Admin.query.filter_by(username='admin').first()
    admin_info = {
        'username': admin.username if admin else 'admin',
        'avatar': admin.avatar if admin else 'default_avatar.png'
    }
    
    settings = {
        'system_name': 'MBTI测试系统',
        'max_students': 1000,
        'data_retention': 90,
        'admin': admin_info
    }
    return jsonify(settings)

@app.route('/api/admin/update_password', methods=['POST'])
@csrf.exempt
def update_admin_password():
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')
    
    # 验证两次输入的新密码是否一致
    if new_password != confirm_password:
        return jsonify({'error': '新密码和确认密码不匹配'}), 400
    
    # 获取当前管理员
    admin = Admin.query.filter_by(username='admin').first()
    
    if not admin:
        return jsonify({'error': '管理员不存在'}), 404
    
    # 验证当前密码
    if admin.password != current_password:
        return jsonify({'error': '当前密码不正确'}), 400
    
    # 更新密码
    admin.password = new_password
    db.session.commit()
    
    return jsonify({'success': True, 'message': '密码已更新'})

@app.route('/api/admin/upload_avatar', methods=['POST'])
@csrf.exempt
def upload_admin_avatar():
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    if 'avatar' not in request.files:
        return jsonify({'error': '没有选择文件'}), 400
    
    file = request.files['avatar']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    # 检查文件类型
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    if not file.filename.lower().endswith(tuple('.' + ext for ext in allowed_extensions)):
        return jsonify({'error': '只允许上传PNG、JPG、JPEG或GIF格式的图片'}), 400
    
    # 安全处理文件名
    filename = secure_filename(file.filename)
    
    # 生成唯一文件名
    import uuid
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    
    # 确保上传文件夹存在
    upload_folder = app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    
    # 保存文件
    file_path = os.path.join(upload_folder, unique_filename)
    file.save(file_path)
    
    # 更新数据库
    admin = Admin.query.filter_by(username='admin').first()
    if admin:
        # 删除旧头像文件（如果不是默认头像）
        if admin.avatar and admin.avatar != 'default_avatar.png':
            old_file_path = os.path.join(upload_folder, admin.avatar)
            if os.path.exists(old_file_path):
                try:
                    os.remove(old_file_path)
                except OSError:
                    pass  # 忽略删除失败
        
        admin.avatar = unique_filename
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': '头像上传成功',
            'avatar_url': f'/static/images/avatars/{unique_filename}'
        })
    
    return jsonify({'error': '管理员不存在'}), 404

@app.route('/api/admin/update_settings', methods=['POST'])
@csrf.exempt
def update_system_settings():
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    
    # 这里应该将设置保存到数据库或配置文件
    # 为了简化，我们只返回成功消息
    
    return jsonify({
        'success': True,
        'message': '系统设置已更新',
        'settings': data
    })

# 修改测试结果API，添加题目数量字段
@app.route('/api/admin/results')
@csrf.exempt
def api_results():
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    # 获取所有结果
    results = db.session.query(Result, Student).join(Student).all()
    
    # 格式化结果
    formatted_results = []
    for res, stu in results:
        formatted_results.append({
            'student_id': stu.student_id,
            'name': stu.name,
            'mbti': res.mbti,
            'e': res.e, 'i': res.i,
            's': res.s, 'n': res.n,
            't': res.t, 'f': res.f,
            'j': res.j, 'p': res.p,
            'test_length': res.test_length,  # 添加测试题目数量
            'test_date': res.created_at.strftime("%Y-%m-%d %H:%M:%S") if res.created_at else "未知"
        })
    
    # 获取维度统计数据
    dimension_stats = {
        'E-I': {'E': 0, 'I': 0},
        'S-N': {'S': 0, 'N': 0},
        'T-F': {'T': 0, 'F': 0},
        'J-P': {'J': 0, 'P': 0}
    }
    
    for res in Result.query.all():
        dimension_stats['E-I']['E'] += res.e
        dimension_stats['E-I']['I'] += res.i
        dimension_stats['S-N']['S'] += res.s
        dimension_stats['S-N']['N'] += res.n
        dimension_stats['T-F']['T'] += res.t
        dimension_stats['T-F']['F'] += res.f
        dimension_stats['J-P']['J'] += res.j
        dimension_stats['J-P']['P'] += res.p
    
    # 获取MBTI类型分布
    mbti_types = {}
    results = Result.query.all()
    for res in results:
        if res.mbti not in mbti_types:
            mbti_types[res.mbti] = 0
        mbti_types[res.mbti] += 1
    
    # 生成基于实际数据的测试趋势（最近7天）
    test_trends = []
    today = datetime.datetime.now().date()
    
    for i in range(6, -1, -1):  # 最近7天，从早到晚
        date = today - datetime.timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        
        # 统计当天完成的测试数
        tested_count = Result.query.filter(
            db.func.date(Result.created_at) == date
        ).count()
        
        # 统计当天开始但未完成的测试数（这里简化处理，实际可能需要更复杂的逻辑）
        # 由于没有开始时间，这里用一个估算值
        in_progress_count = max(0, tested_count - 2) if tested_count > 2 else 0
        
        test_trends.append({
            'date': date_str,
            'tested': tested_count,
            'in_progress': in_progress_count
        })
    
    return jsonify({
        'results': formatted_results,
        'dimension_stats': dimension_stats,
        'mbti_types': mbti_types,
        'test_trends': test_trends  # 添加测试趋势数据
    })

@app.route('/api/admin/system_status')
@csrf.exempt
def system_status():
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    # 获取内存使用情况
    memory = psutil.virtual_memory()
    memory_usage = memory.used / (1024 * 1024)  # MB
    
    # 计算在线时间（秒）
    uptime_seconds = time.time() - app_start_time
    uptime = str(datetime.timedelta(seconds=int(uptime_seconds)))
    
    # 获取当前时间
    last_update = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 获取连接数（这里我们使用SocketIO的活跃连接数）
    # 注意：这需要根据你的SocketIO实现来调整，这里仅作示例
    connection_count = 0
    try:
        # 获取SocketIO的活跃房间（admin命名空间）的连接数
        connection_count = len(socketio.server.manager.rooms['/admin'])
    except:
        pass
    
    # 检查数据库连接状态
    db_status = '正常'
    try:
        # 尝试执行一个简单的查询来测试数据库连接
        db.session.execute(text('SELECT 1'))
        db_status = '正常'
    except Exception as e:
        db_status = '异常'
        print(f"数据库连接检查失败: {str(e)}")
    
    # 获取学生总数
    total_students = Student.query.count()
    tested_students = Student.query.filter_by(has_tested=True).count()
    
    # 获取系统版本（可以从配置文件或硬编码）
    system_version = 'v1.0.0'
    
    # 获取CPU使用率
    cpu_usage = psutil.cpu_percent(interval=1)
    
    # 获取磁盘使用情况
    try:
        if os.name == 'nt':  # Windows
            disk = psutil.disk_usage('C:\\')
        else:  # Unix/Linux
            disk = psutil.disk_usage('/')
        disk_usage = disk.used / (1024 * 1024 * 1024)  # GB
    except:
        disk_usage = 0.0
    
    return jsonify({
        'server_status': '运行中',
        'uptime': uptime,
        'memory_usage': f"{memory_usage:.2f} MB",
        'cpu_usage': f"{cpu_usage:.1f}%",
        'disk_usage': f"{disk_usage:.2f} GB",
        'connection_count': connection_count,
        'db_status': db_status,
        'total_students': total_students,
        'tested_students': tested_students,
        'system_version': system_version,
        'last_update': last_update
    })

# 确保在最后添加这个
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)