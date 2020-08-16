from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import threading
from time import sleep


class Bot(object):
    """
    用于自动化完成Checkmate对局。
    灵感来自Div5和5d %%%%%
    """

    def __init__(self, username, password, roomId, isSecret=False, isAutoReady=True):
        self.kanaLink = "https://kana.byha.top:444/"
        self.t_game = threading.Thread(target=self.Game, name="game")    # 主线程
        self.t_countTime = threading.Thread(target=self.CountTime, name="timeCounter")    # 计时线程
        self.t_ft = threading.Thread(target=self.FT, name="ft")    # 防踢线程
        self.t_gameCtrl = threading.Thread(target=self.GameCtrl, name="cg")    # 检测游戏状态
        self.driver = webdriver.Chrome()    # 浏览器
        #self.driver = webdriver.Firefox()
        self.username = username    # 用户名
        self.password = password    # 密码
        self.roomId = roomId    # 房间号
        self.isSecret = isSecret    # 是否为私密房间
        self.isAutoReady = isAutoReady    # 是否主动准备
        self.enableFT = True    # 是否开启防踢（在游戏开始后关闭
        self.enableCountTime = False    # 是否开启计时
        self.time = 0   # 游戏时间，以秒为单位
        self.mode = "maze"


    def SendKeyToTable(self, key):
        ac = ActionChains(self.driver)
        ac.send_keys_to_element(self.driver, key)


    def SmallMap(self, mode):
        pass


    def LargeMap(self, mode):
        pass


    def GameCtrl(self):
        WebDriverWait(self.driver, 3600).until(EC.visibility_of_element_located((By.CLASS_NAME, "swal2-content")))

        self.driver.refresh()

    def Game(self):
        self.enableCountTime = True
        self.enableFT = False
        self.table = self.driver.find_element_by_tag_name("tbody")

        if self.userCount == 2:
            self.SmallMap(self.mode)
        else:
            self.LargeMap(self.mode)


    def Say(self, pattern):
        """
        在聊天框发送一句话
        :param pattern:要发送的话
        :return:
        """
        ac = ActionChains(self.driver)
        input = self.driver.find_element_by_id("msg-sender")
        ac.click(input).send_keys_to_element(input, pattern, Keys.ENTER)


    def CountTime(self):
        while self.enableCountTime:
            sleep(1)
            self.time += 1


    def FT(self):
        while self.enableFT:
            sleep(20)
            self.SendKeyToTable("F")


    def Login(self):
        """
        登录，如果出现异常则在5S后退出
        :return:
        """
        print("正在登录…")
        self.driver.get(self.kanaLink)
        usernameBox = self.driver.find_element_by_name("username")
        passwordBox = self.driver.find_element_by_name("pwd")
        ac = ActionChains(self.driver)

        # 输入账号密码并登录
        ac.send_keys_to_element(usernameBox, self.username)
        ac.send_keys_to_element(passwordBox, self.password)
        ac.click(self.driver.find_element_by_id("submitButton")).perform()

        try:
            WebDriverWait(self.driver, 8).until(EC.url_to_be(self.kanaLink))
            print("登录成功！")
        except TimeoutException:
            print("网络连接出现问题或账密错误！\n程序将在5秒后退出")
            sleep(5)
            self.driver.close()
            del self


    def EnterRoom(self):
        """
        进入指定房间
        :return:
        """
        self.driver.get("https://kana.byha.top:444/checkmate/room/" + self.roomId)
        if self.isSecret:
            settingBtn = self.driver.find_element_by_class_name("form-check-input")
            ac = ActionChains(self.driver)
            ac.click(settingBtn).perform()
        print("Bot已就位！")


    def GetCoordinate(self):
        pass


    def GameEnd(self):
        """
        游戏结束时的清理工作
        :return:
        """
        self.enableFT = True
        self.enableCountTime = False

        self.time = 0


    def Ready(self):
        """
        准备开始，如果300秒未开始，程序退出
        :return:
        """
        sleep(1)
        try:
            self.userCount = int(self.driver.find_element_by_id("total-user").text)
        except ValueError:
            self.userCount = 2
        ac = ActionChains(self.driver)
        ac.click(self.driver.find_element_by_id("ready")).perform()


    def Kill(self):
        self.driver.close()
        del self


    def Main(self):
        self.Login()
        self.EnterRoom()
        self.t_ft.start()
        if self.isAutoReady:
            self.Ready()
        try:
            WebDriverWait(self.driver, 300).until(EC.visibility_of_element_located((By.TAG_NAME, "tbody")))
        except TimeoutException:
            print("房间内无人开始，过一会再试试吧")
            sleep(5)
            self.Kill()
        self.t_game.start()
        self.t_gameCtrl.start()
        self.t_countTime.start()


    def test(self):
        self.Login()
        self.EnterRoom()
        while True:
            self.t_ft.start()
            if self.isAutoReady:
                self.Ready()
            try:
                WebDriverWait(self.driver, 300).until(EC.visibility_of_element_located((By.TAG_NAME, "tbody")))
            except TimeoutException:
                print("房间内无人开始，过一会再试试吧")
                sleep(5)
                self.Kill()
            self.t_game.start()
            self.t_gameCtrl.start()
            self.t_countTime.start()


