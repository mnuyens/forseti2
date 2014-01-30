import lcm
import forseti2

class spam_thread(threading.Thread):
    msg = forseti2.piemos_health()
    def __init__(self):
        threading.Thread.__init__(self)
	    lc = lcm.LCM()
        spam = True

    def run(self):
        while (spam):
            with open('/proc/uptime', 'r') as f:
                spam_thread.msg.uptime= float(f.readline().split()[0])
            lc.publish("Piemos Health", spam_thread.msg.encode())
            sleep(30)

    def handle_health(channel, data):
        incMsg = forseti2.to_piemos.decode(data)
        spam_thread.msg.auton = incMsg.auton
        spam_thread.msg.enabled = incMsg.enabled

if __name__=='__main__':
    lc = lcm.LCM()
    lcm.subscribe("To Piemos", spam_thread.hande_health)
    spam_thread().start()
    try:
        while(true):
            lc.handle()
    except KeyboardInterrupt:
        pass
