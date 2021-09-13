# -*- coding:utf-8 -*-
'''
reated on 2021年8月26日
@author: zy
'''
import os
import sys
import time
import json
import re

reload(sys)
sys.setdefaultencoding("utf-8")


def get_json_value(jsonString, jsonKey):
    jsonDict = json.loads(jsonString)
    if jsonDict.has_key(jsonKey):
        return jsonDict[jsonKey]
    else:
        return '-1'


def json_has_key(jsonString, jsonKey):
    jsonDict = json.loads(jsonString)
    return jsonDict.has_key(jsonKey)


def get_build_result(startTime, endTime, buildType, cubeName):
    curlCMD = 'curl -s -X PUT -H "Authorization: Basic yourauthorization" -H "Content-Type: application/json;charset=UTF-8" ' \
              '-d "{\\"startTime\\":\\"%s\\",\\"endTime\\":\\"%s\\",\\"buildType\\":\\"%s\\"}" ' \
              'http://youraddress/kylin/api/cubes/%s/rebuild '
    curlCMD = curlCMD % (startTime, endTime, buildType, cubeName)
    buildResult = os.popen(curlCMD).readline()
    #print 'buildResult-->:{}'.format(buildResult)
    return buildResult


def get_build_status(jobId):
    curlCMD = 'curl -s -X GET -H "Authorization: Basic yourauthorization -H "Content-Type: application/json;charset=UTF-8"  http://youraddress/kylin/api/jobs/%s' % (jobId)
    statusStr = os.popen(curlCMD).readline()
    return statusStr


cubeName = sys.argv[1]
print 'cubeName:{}'.format(cubeName)

buildType = sys.argv[2]
print 'buildType:{}'.format(buildType)
# BUILD MERGE REFRESH

startTimeArray = time.strptime(sys.argv[3], '%Y%m%d')  # $3:20190101
startTime = int(time.mktime(startTimeArray) * 1000 + 28800000)
print 'startTime:{}'.format(startTime)

endTimeArray = time.strptime(sys.argv[4], '%Y%m%d')  # $4:20190102
endTime = int(time.mktime(endTimeArray) * 1000 + 28800000)
print 'endTime:{}'.format(endTime)

jobId = ''
buildCode = ''
buildMsg = ''

buildResult = get_build_result(startTime, endTime, buildType, cubeName)

if json_has_key(buildResult, 'uuid'):
    jobId = get_json_value(buildResult, 'uuid')
    print 'build succeed！！！'
elif json_has_key(buildResult, 'code') and json_has_key(buildResult, 'msg'):
    buildCode = get_json_value(buildResult, 'code')
    buildMsg = get_json_value(buildResult, 'msg')
    print 'build faild！！！'
    print 'buildCode:%s;buildMsg:%s;' % ( buildCode, buildMsg)
else:
    print " code or msg not exist!"
    sys.exit(1)


is_building = False

while not is_building:

    if jobId != '':
        is_building = True
        break
    print 'waiting...'
    if buildCode == '999' and buildMsg.__contains__('There is already 10 building segment; '):
        print 'There is already 10 building segment; '
        time.sleep(60)
        # rebuild
        print 'reBuilding...'
        buildResult = get_build_result(startTime, endTime, buildType, cubeName)

        if json_has_key(buildResult, 'uuid'):
            jobId = get_json_value(buildResult, 'uuid')
        elif json_has_key(buildResult, 'code') and json_has_key(buildResult, 'msg'):
            buildCode = get_json_value(buildResult, 'code')
            buildMsg = get_json_value(buildResult, 'msg')
        else:
            print " code or msg not exist!"
            sys.exit(1)
        print 'job_id:{};buildCode:{};buildMsg:{};'.format(jobId, buildCode, buildMsg)

    elif buildCode == '999' and buildMsg.__contains__('Segments overlap'):
        # "Segments overlap: cube_o_ba_gaap_summary_mbbi[20210809000000_20210811000000] and cube_o_ba_gaap_summary_mbbi[20210809000000_20210810000000]"
        print 'Segments overlap'
        segment = re.search("\[[0-9_]+\]", buildMsg, 0).group()
        segmentAll = re.findall("\[[0-9_]+\]", buildMsg, 0)
        if segmentAll[0] == segmentAll[1]  :
            print 'these segment is same'
            sys.exit(1)
        segment = segment.replace('[', '').replace(']', '')
        dates = segment.split('_')
        startTimeStr = dates[0][0:8]
        startTime = int(time.mktime(time.strptime(startTimeStr, '%Y%m%d')) * 1000 + 28800000)
        endTimeStr = dates[1][0:8]
        endTime = int(time.mktime(time.strptime(endTimeStr, '%Y%m%d')) * 1000 + 28800000)
        print 'startTime:{},endTime:{}'.format(startTime, endTime)
        # rebuild
        print 'reBuilding...'
        buildResult = get_build_result(startTime, endTime, buildType, cubeName)

        if json_has_key(buildResult, 'uuid'):
            jobId = get_json_value(buildResult, 'uuid')
        elif json_has_key(buildResult, 'code') and json_has_key(buildResult, 'msg'):
            buildCode = get_json_value(buildResult, 'code')
            buildMsg = get_json_value(buildResult, 'msg')
        else:
            print " code or msg not exist!"
            sys.exit(1)
        print 'job_id:{};buildCode:{};buildMsg:{};'.format(jobId, buildCode, buildMsg)

    elif buildCode == '999' and buildMsg.__contains__('The cube cube_build_test has segments'):
        print 'The cube cube_build_test has segments'
        sys.exit(0)
    else :
        sys.exit(1)

while True:
    statusStr = get_build_status(jobId)
    jobStatus = get_json_value(statusStr, 'job_status')
    jobProgress = get_json_value(statusStr, 'progress')
    if jobStatus == "FINISHED":
        print '运行状态:{}'.format(jobStatus)
        print '运行进度:{}'.format(jobProgress)
        sys.exit(0)
    print '运行状态:{}'.format(jobStatus)
    print '运行进度:{}'.format(jobProgress)
    time.sleep(60)


