import sys
import json
import webbrowser
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QPushButton, QListWidget, QLabel, QInputDialog)
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
import requests

class KakaoFriendsApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
        self.CLIENT_ID = "069bd62145d0e4923041dbea4fb7984b"
        self.REDIRECT_URI = "https://katalkloadfriend.vercel.app/auth/kakao/callback"
        self.TOKEN = None
        
    def initUI(self):
        self.setWindowTitle('카카오톡 친구목록')
        self.setGeometry(100, 100, 800, 600)
        
        # 메인 위젯과 레이아웃 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 로그인 버튼
        self.login_button = QPushButton('카카오톡 로그인', self)
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)
        
        # 인증 코드 입력 버튼
        self.code_button = QPushButton('인증 코드 입력', self)
        self.code_button.clicked.connect(self.input_auth_code)
        layout.addWidget(self.code_button)
        
        # 친구목록 가져오기 버튼
        self.friends_button = QPushButton('친구목록 가져오기', self)
        self.friends_button.clicked.connect(self.get_friends)
        self.friends_button.setEnabled(False)
        layout.addWidget(self.friends_button)
        
        # 친구목록을 표시할 리스트 위젯
        self.friends_list = QListWidget(self)
        layout.addWidget(self.friends_list)
        
        # 상태 표시 라벨
        self.status_label = QLabel('로그인이 필요합니다', self)
        layout.addWidget(self.status_label)
        
    def login(self):
        scope = "friends"
        auth_url = f"https://kauth.kakao.com/oauth/authorize?client_id={self.CLIENT_ID}&redirect_uri={self.REDIRECT_URI}&response_type=code&scope={scope}"
        webbrowser.open(auth_url)
    
    def input_auth_code(self):
        code, ok = QInputDialog.getText(self, '인증 코드 입력', 
                                      '카카오 인증 후 받은 코드를 입력하세요:')
        if ok and code:
            self.get_token(code)
    
    def get_token(self, code):
        token_url = "https://kauth.kakao.com/oauth/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": self.CLIENT_ID,
            "redirect_uri": self.REDIRECT_URI,
            "code": code
        }
        try:
            response = requests.post(token_url, data=data)
            if response.status_code != 200:
                self.status_label.setText(f'토큰 획득 실패: {response.text}')
                return
                
            token_info = response.json()
            self.TOKEN = token_info.get('access_token')
            if self.TOKEN:
                self.status_label.setText('로그인 성공!')
                self.friends_button.setEnabled(True)
            else:
                self.status_label.setText('토큰을 받지 못했습니다.')
        except Exception as e:
            self.status_label.setText(f'오류 발생: {str(e)}')
    
    def get_friends(self):
        if not self.TOKEN:
            self.status_label.setText('먼저 로그인해주세요')
            return
            
        url = "https://kapi.kakao.com/v1/api/talk/friends"
        headers = {
            "Authorization": f"Bearer {self.TOKEN}",
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
        }
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                self.status_label.setText(f'친구 목록 가져오기 실패: {response.text}')
                return
                
            friends = response.json().get('elements', [])
            
            # 친구목록 표시
            self.friends_list.clear()
            for friend in friends:
                nickname = friend.get('profile_nickname', 'Unknown')
                user_id = friend.get('uuid', 'No ID')
                self.friends_list.addItem(f"{nickname} ({user_id})")
            
            self.status_label.setText(f'총 {len(friends)}명의 친구를 불러왔습니다')
            
        except Exception as e:
            self.status_label.setText(f'오류 발생: {str(e)}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = KakaoFriendsApp()
    ex.show()
    sys.exit(app.exec_())