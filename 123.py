import tkinter as tk
import pyautogui
import random
import time
from pynput import mouse, keyboard
import threading

# 문장을 코드 내에 저장
sentences = [
    "How is school today?",
    "How is the problem solved?",
    "How is your report card?",
    "How long do I have to wait till the dishes come out?",
    "How long does each class last?",
    "How long does it take by walking?",
    "How long have you lived there?",
    "How long is it?",
    "How long is this vacation?",
    "How long should we play?",
    "How long will we stay?",
    "How many apples are on the plate?",
    "How many are left?",
    "How many birds are left?",
    "How many birds are there in all?",
    "How many blocks can we stack?",
    "How many books are we going to read?",
    "How many books can I borrow?",
    "How many candles do we need?",
    "How many days are left till the due date?",
    "How many days are left until I go back to school?",
    "How many do you have now?",
    "How many do you want to invite?",
    "How many eyes does Mom have?",
    "How many girls are there?",
    "How many more nights are left?",
    "How many more plates do we need?",
    "How many more stops are left to get to Myeongdong?",
    "How many pairs of scissors do you have?",
    "How many pencils can each have?",
    "How many pencils do I have?",
    "How many people are there in your family?",
    "How many people do you have in your family?",
    "How many students are in your class?",
    "How many times do I have to tell you to be quiet?",
    "How many times should I tell you?",
    "How much are you going to give me?",
    "How much do you love me, Mommy?",
    "How much do you want?",
    "How much is this?",
    "How much more do we have to go?",
    "How much older than your brother are you?",
    "How much should I pour?",
    "How much TV is too much TV?",
    "How nice.",
    "How old are you?",
    "How old is Arthur?",
    "How old is your grandfather?",
    "How old is your school?",
    "How old is your younger sister?",
    "How was school today?",
    "How was the book?",
    "How was your day?",
    "How was your field trip?",
    "How was your weekend.",
    "How would he have felt in this situation?",
    "How would you like the story to end?",
    "How's everything going?",
    "How's the preparation for the competition going?",
    "How's the weather today?"
]

current_index = None

# 화면의 오른쪽 상단 영역 설정
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()
RIGHT_TOP_REGION = (SCREEN_WIDTH - 200, 0, 200, 200)  # 오른쪽 상단 200x200

# 창 생성 및 초기화
def create_window():
    window = tk.Tk()
    window.overrideredirect(True)
    window.configure(bg="#0441B6")
    label = tk.Label(window, text="", font=("Arial", 16), fg="#D3D3D3", bg="#0441B6")
    label.pack()
    return window, label

window, label = create_window()
window_visible = False

# 창 위치 및 텍스트 업데이트
def update_window(text):
    label.config(text=text)
    window.update_idletasks()
    text_width = label.winfo_reqwidth()
    text_height = label.winfo_reqheight()
    window.geometry(f"{text_width}x{text_height}+{SCREEN_WIDTH - text_width - 20}+20")

# 문장 랜덤 선택
def get_random_sentence():
    global current_index
    if current_index is None:
        current_index = random.randint(0, len(sentences) - 1)
    return sentences[current_index]

# 이전 문장
def get_previous_sentence():
    global current_index
    if current_index is not None:
        current_index = (current_index - 1) % len(sentences)
    return sentences[current_index]

# 다음 문장
def get_next_sentence():
    global current_index
    if current_index is not None:
        current_index = (current_index + 1) % len(sentences)
    return sentences[current_index]

# 마우스 클릭 이벤트 핸들러
def on_click(x, y, button, pressed):
    global window_visible
    if pressed and window_visible:
        if button == mouse.Button.left:  # 왼쪽 클릭
            tk_call(lambda: update_window(get_previous_sentence()))
        elif button == mouse.Button.right:  # 오른쪽 클릭
            tk_call(lambda: update_window(get_next_sentence()))

# 키보드 이벤트 핸들러
def on_key_press(key):
    if key == keyboard.Key.esc:  # Esc 키로 종료
        print("프로그램 종료")
        mouse_listener.stop()
        keyboard_listener.stop()
        tk_call(window.destroy)
        return False

# tkinter 호출을 메인 스레드에서 실행
def tk_call(func):
    window.after(0, func)

# 마우스 이벤트 리스너 설정
mouse_listener = mouse.Listener(on_click=on_click)
mouse_listener.start()

# 키보드 이벤트 리스너 설정
keyboard_listener = keyboard.Listener(on_press=on_key_press)
keyboard_listener.start()

def main_loop():
    global window_visible
    try:
        while True:
            x, y = pyautogui.position()
            if RIGHT_TOP_REGION[0] <= x <= RIGHT_TOP_REGION[0] + RIGHT_TOP_REGION[2] and RIGHT_TOP_REGION[1] <= y <= RIGHT_TOP_REGION[3]:
                if not window_visible:
                    tk_call(lambda: update_window(get_random_sentence()))
                    tk_call(window.deiconify)
                    window_visible = True
            else:
                if window_visible:
                    tk_call(window.withdraw)
                    window_visible = False
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        mouse_listener.stop()
        keyboard_listener.stop()
        tk_call(window.destroy)

# 메인 루프를 별도의 스레드에서 실행
threading.Thread(target=main_loop, daemon=True).start()
window.mainloop()