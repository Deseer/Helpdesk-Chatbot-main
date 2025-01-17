from pytz import timezone
from datetime import datetime
from nonebot_plugin_orm import get_session
from nonebot_plugin_chatrecorder import get_message_records
from typing import Optional
from nonebot.adapters.onebot.v11 import MessageEvent, PrivateMessageEvent, Message, GroupMessageEvent
from nonebot.internal.adapter.bot import Bot
from nonebot_plugin_chatrecorder import MessageRecord
from .config import plugin_config
from .model import Ticket
from nonebot import get_bot, require

# 获取中国时区
cst = timezone('Asia/Shanghai')


async def send_combined_msg(
        bot: Bot,
        msgs: list[Message],
        event: Optional[MessageEvent] = None,
        target_group_id: Optional[str | int] = None,
        target_user_id: Optional[str | int] = None,
        block_event: bool = False,
):
    """
    发送合并转发消息。
    * `bot`: Bot 实例
    * `event`: 消息事件
    * `msgs`: 消息列表
    * `target_group_id`: 目标群号
    * `target_user_id`: 目标用户号
    * `block_event`: 是否阻止用event返回消息
    """

    def to_node(msg: Message):
        return {"type": "node", "data": {"name": "name", "uin": "10010", "content": msg}}

    messages = [to_node(msg) for msg in msgs]
    if target_group_id:
        await bot.call_api(
            "send_group_forward_msg", group_id=target_group_id, messages=messages
        )
    if target_user_id:
        await bot.call_api(
            "send_private_forward_msg", user_id=target_user_id, messages=messages
        )
    if not block_event and event:
        if isinstance(event, PrivateMessageEvent):
            await bot.call_api(
                "send_private_forward_msg", user_id=event.user_id, messages=messages
            )
        elif isinstance(event, GroupMessageEvent):
            await bot.call_api(
                "send_group_forward_msg", group_id=event.group_id, messages=messages
            )

async def send_forward_message(
        bot: Bot,
        msgs: list[MessageRecord],
        event: Optional[MessageEvent] = None,
        target_group_id: Optional[str | int] = None,
        target_user_id: Optional[str | int] = None,
        block_event: bool = False,):
    def to_node(msg: MessageRecord):
        print(msg.message_id,msg.message)
        return {"type": "node", "data": {"id": msg.message_id}}
    message_nodes = [to_node(msg) for msg in msgs]
    if target_group_id:
        await bot.call_api(
        "send_forward_msg", group_id=target_group_id,messages=message_nodes
    )
    if target_user_id:
        await bot.call_api(
        "send_forward_msg", user_id=target_user_id,messages=message_nodes
    )
    if not block_event and event:
        if isinstance(event, PrivateMessageEvent):
            await bot.call_api(
                "send_forward_msg", user_id=event.user_id, messages=message_nodes
            )
        elif isinstance(event, GroupMessageEvent):
            await bot.call_api(
                "send_forward_msg", group_id=event.group_id, messages=message_nodes
            )


async def print_ticket(ticket: Ticket) -> Message:
    if not ticket:
        # no ticket record
        raise (ValueError)
    msg = f'工单:{ticket.id}\n状态:{ticket.status}\n机主:{ticket.customer_id}\n'
    if ticket.engineer_id:
        msg = msg+f'工程师:{ticket.engineer_id}\n'
    if ticket.begin_at:
        msg = msg+f'创建时间:{ticket.begin_at.strftime("%Y-%m-%d %H:%M:%S")}\n'
    if ticket.end_at:
        msg = msg+f'结束时间:{ticket.end_at.strftime("%Y-%m-%d %H:%M:%S")}\n'
    if ticket.scheduled_time:
        msg = msg+f'预约时间:{ticket.scheduled_time}\n'
    if ticket.description:
        msg = msg+f'描述:{ticket.description}'
    return Message(msg)

async def print_ticket_history(ticket:Ticket) -> list[MessageRecord]:
    if not ticket:
        raise (ValueError)
    # 下面打印历史消息
    if plugin_config.front_bot:
        bot_id = [str(plugin_config.front_bot)]
    else:
        bot_id = None
    ticket_end_at = None if not ticket.end_at else cst.localize(
        ticket.end_at)
    message_records = await get_message_records(id1s=[ticket.customer_id], time_start=cst.localize(ticket.begin_at), time_stop=ticket_end_at, id2s=[''], bot_ids=bot_id)
    return message_records

async def print_ticket_info(ticket: Ticket) -> list[Message]:
    msgs = []
    if not ticket:
        # no ticket record
        raise (ValueError)
    ticket_id = ticket.id
    ticket_status = ticket.status
    ticket_begin_at = cst.localize(ticket.begin_at)
    ticket_end_at = None if not ticket.end_at else cst.localize(
        ticket.end_at)
    ticket_customer_id = ticket.customer_id
    ticket_engineer_id = ticket.engineer_id
    ticket_scheduled_time = ticket.scheduled_time
    ticket_description = ticket.description
    msgs.append(Message(f"工单号: {ticket_id:0>3}"))
    msgs.append(Message(f"状态: {ticket_status}"))
    msgs.append(
        Message("创建时间: " + ticket_begin_at.strftime("%Y-%m-%d %H:%M:%S")))
    if ticket_end_at:
        msgs.append(
            Message("结束时间: " + ticket_end_at.strftime("%Y-%m-%d %H:%M:%S")))
    if ticket_scheduled_time:
        msgs.append(Message("预约时间: " + ticket_scheduled_time))
    msgs.append(Message(f"机主名片[CQ:contact,type=qq,id={ticket_customer_id}]"))
    if ticket_engineer_id:
        msgs.append(
            Message(f"工程师名片[CQ:contact,type=qq,id={ticket_engineer_id}]"))
    if ticket_description:
        msgs.append(
            Message(f'描述:{ticket_description}')
        )
    # 下面打印历史消息
    if plugin_config.front_bot:
        bot_id = [str(plugin_config.front_bot)]
    else:
        bot_id = None
    message_records = await get_message_records(id1s=[ticket_customer_id], time_start=ticket_begin_at, time_stop=ticket_end_at, id2s=[''], bot_ids=bot_id)
    # Python
    if not message_records:
        return msgs

    for i, record in enumerate(message_records):
        if i == 0 or record.type != message_records[i-1].type:
            if record.type == "message_sent":
                msgs.append(Message("~~~~~~~Engineer~~~~~~~"))
            else:
                msgs.append(Message("---------Customer---------"))
        msgs.append(record.message)
    return msgs


def get_backend_bot(bot):
    if plugin_config.backend_bot:
        return get_bot(str(plugin_config.backend_bot))
    else:
        return bot


def get_front_bot(bot):
    if plugin_config.front_bot:
        return get_bot(str(plugin_config.front_bot))
    else:
        return bot
