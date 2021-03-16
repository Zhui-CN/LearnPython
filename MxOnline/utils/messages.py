def send_single_sms(code, mobile):
    return code


def message_nums(request):
    result = dict()
    if request.user.is_authenticated:
        result = dict(unread_nums=request.user.usermessage_set.filter(has_read=False).count())
    return result
