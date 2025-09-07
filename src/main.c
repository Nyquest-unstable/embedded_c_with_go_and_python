#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <termios.h>

int main() {

    int fd = open("/dev/ttyUSB2", O_RDWR | O_NOCTTY | O_NDELAY);
    if (fd == -1) {
        perror("无法打开串口 /dev/ttyUSB2");
        return 1;
    }

    struct termios options;
    tcgetattr(fd, &options);
    cfsetispeed(&options, B115200);
    cfsetospeed(&options, B115200);
    options.c_cflag |= (CLOCAL | CREAD);
    options.c_cflag &= ~PARENB;
    options.c_cflag &= ~CSTOPB;
    options.c_cflag &= ~CSIZE;
    options.c_cflag |= CS8;
    options.c_lflag &= ~(ICANON | ECHO | ECHOE | ISIG);
    options.c_iflag &= ~(IXON | IXOFF | IXANY);
    options.c_oflag &= ~OPOST;
    tcsetattr(fd, TCSANOW, &options);


    // 设置短信为文本模式
    write(fd, "AT+CMGF=1\r\n", strlen("AT+CMGF=1\r\n"));
    usleep(200000);
    char buf[1024] = {0};
    read(fd, buf, sizeof(buf) - 1);

    while (1) {
        // 查询未读短信
        write(fd, "AT+CMGL=\"REC UNREAD\"\r\n", strlen("AT+CMGL=\"REC UNREAD\"\r\n"));
        usleep(500000); // 等待模块返回
        memset(buf, 0, sizeof(buf));
        int r = read(fd, buf, sizeof(buf) - 1);
        if (r > 0 && strstr(buf, "+CMGL")) {
            printf("收到短信：\n%s\n", buf);
        }
        sleep(5); // 每5秒轮询一次
    }

    close(fd);
    return 0;
}
