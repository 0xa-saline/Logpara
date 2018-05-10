# coding:utf-8
# 模拟一个进城池 线程池，可以向里面添加任务，

import threading
import time
import traceback
import logger
import Queue
import random

class new_threadpool:

    def __init__(self,threadnum,func_scan,Isjoin = False):
        self.thread_count = self.thread_nums = threadnum
        self.scan_count_lock = threading.Lock()
        self.thread_count_lock = threading.Lock()
        self.load_lock = threading.Lock()
        self.scan_count = 0
        self.isContinue = True
        self.func_scan = func_scan
        self.queue = Queue.Queue()
        self.isjoin = Isjoin

    def push(self,payload):
        self.queue.put(payload)

    def changeScanCount(self,num):
        self.scan_count_lock.acquire()
        self.scan_count += num
        self.scan_count_lock.release()

    def changeThreadCount(self,num):
        self.thread_count_lock.acquire()
        self.thread_count += num
        self.thread_count_lock.release()

    def run(self):
        th = []
        for i in range(self.thread_nums):
            t = threading.Thread(target=self.scan)
            t.setDaemon(True)
            t.start()
            th.append(t)
        
        # It can quit with Ctrl-C
        if self.isjoin:
            for tt in th:
                tt.join()
        else:
            while 1:
                if self.thread_count > 0 and self.isContinue:
                    time.sleep(0.01)
                else:
                    break
                    
    def stop(self):
        self.load_lock.acquire()
        self.isContinue = False
        self.load_lock.release()
        
    def scan(self):
        while 1:
            self.load_lock.acquire()
            if self.queue.qsize() > 0 and self.isContinue:
                payload = self.queue.get()

                self.load_lock.release()
            else:
                self.load_lock.release()
                break
            try:
                # 在执行时报错如果不被处理，线程会停止并退出
                self.func_scan(payload)
                time.sleep(0.3)
            except KeyboardInterrupt:
                self.isContinue = False
                raise KeyboardInterrupt
            except Exception:
                errmsg = traceback.format_exc()
                self.isContinue = False
                print_error(errmsg)

        self.changeThreadCount(-1)


if __name__ == '__main__':
    def calucator(args):
        num,numt = args
        print numt
        i = random.randint(1, 100)
        u = num
        a = i * u
        if (a % 6 == 0):
            for x in range(5):
                print "new thread",x
                #p.push(x)

    p = new_threadpool(3, calucator)
    for i in range(20):
        args=(i,i+1,)
        p.push(args)
    p.run()

