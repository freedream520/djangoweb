# coding=utf-8
def backup():
    '''
    class Reply(models.Model):
        gmt_create = models.DateTimeField()
        gmt_modify = models.DateTimeField()
        comment_id = models.IntegerField()
        from_id = models.IntegerField()
        to_id = models.IntegerField()
        content = models.CharField(max_length=10240)
        status = models.CharField(max_length=32)
    # 对评论进行回复
    def reply(request):
        commentid = request.POST.get('commentid')
        toid = request.POST.get('toid')
        content = request.POST.get('content')
        fromid = _get_current_userid(request)

        # check params
        if not commentid or not Comment.objects.filter(id=commentid).exists():
            return HttpResponse(json.dumps({'success': 1, 'error_msg': "commentid参数不合法"}))
        if not fromid or not User.objects.filter(id=fromid).exists():
            return HttpResponse(json.dumps({'success': 1, 'error_msg': "fromid参数不合法"}))
        if not toid or not User.objects.filter(id=toid).exists():
            return HttpResponse(json.dumps({'success': 1, 'error_msg': "toid参数不合法"}))
        if not content or len(content) > 10240:
            return HttpResponse(json.dumps({'success': 1, 'error_msg': "content参数不合法"}))

        # insert new reply
        reply = Reply(
            gmt_create=datetime.now(),
            gmt_modify=datetime.now(),
            comment_id=commentid,
            from_id=fromid,
            to_id=toid,
            content=content,
            status='enabled')
        reply.save()
        return HttpResponse(json.dumps({'success': 0, 'error_msg': ""}))
    def evaluate(request, field, resId):
        # check field
        if field not in ('good', 'bad'):
            return HttpResponse(0)
            # update filed value
        retVal = 0;
        res = Resources.objects.filter(id=int(resId))
        if res:
            if field == 'good':
                retVal = Resources.objects.filter(id=resId).update(good=res[0].good + 1)
            else:
                retVal = Resources.objects.filter(id=resId).update(bad=res[0].bad + 1)

        return HttpResponse(retVal)
    '''
