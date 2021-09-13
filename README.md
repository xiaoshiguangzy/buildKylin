### Kylin 构建脚本
- use api to build kylin cube

#### 2、脚本功能

- 利用任务调度，构建Kylin cube
- 日志输出构建进度，并在构建完成后，任务退出
- 构建失败后，根据构建失败的原因，做出相应动作
  - 超过构建10个数量限制，等待一分钟后，重新构建。
  - 存在一个比要构建的分片更大的分片，获取该分片的开始日期和结束日期，重新构建该分片。
  - 存在 一个正在构建的相同的分片时，任务退出。

#### 4、使用方式

- 运行命令：python /home/work/zhouyang/python_zy/putKylin.py $cubeName BUILD $startTime(yyyyMMdd) $endTime(yyyyMMdd) 
