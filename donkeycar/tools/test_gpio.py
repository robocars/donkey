import pigpio
import time

if __name__ == "__main__":
    
    import pigpio

    import test_remote;

    pi = pigpio.pi()

    pi.set_mode(21, pigpio.OUTPUT)
    pi.set_mode(20, pigpio.OUTPUT)
    pi.set_mode(19, pigpio.OUTPUT)
    pi.write(21, 1)
    time.sleep(1)
    pi.write(21, 0)
    pi.write(20, 1)
    time.sleep(1)
    pi.write(20, 0)
    pi.write(19, 1)
    time.sleep(1)
    pi.write(19, 0)

