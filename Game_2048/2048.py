
# game2048 
# --------------------------------------------------------------------------
import random
import curses

#开始生成2个方块
START_QUBE = 2
#随机生成方块出4概率
FOUR_PROB = 0.2
#面板
BOARD = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
#分数
SCORE = 0
#是否通关(2048)
HAS2048 = False
#是否能动
BNDONG = False
#是否问过是否继续
ASK_FOR_ASKCONTINUE = False
#方向
LEFT, RIGHT, UP, DOWN = 0, 1, 2, 3
#用来代表是否可以结束游戏的常量
CAN_END = True
VECTOR = [[-1, 0],[1, 0],[0, -1],[0, 1]]
SUCESS = True
FAIL = False
# curses
SCREEN = None

def clip(number, lowerbound, upperbound):
    if number < lowerbound:
        return lowerbound
    elif number > upperbound:
        return upperbound
    else:
        return number

def print_score():
    global SCREEN
    SCREEN.addstr(9, 0,''.join(['游戏结束啦,得分:',str(SCORE),'.']))

def print_prompt(PROMPT):
    global SCREEN
    SCREEN.addstr(10, 0, PROMPT)

def get_usr_input(PROMPT, request_input):
    global SCREEN
    error_prompt_str = ''.join(['请输入',','.join([str(x) for x in request_input]),'的其中之一'])
    print_prompt(PROMPT)
    usr_input = SCREEN.getkey()
    while usr_input not in request_input:
        print_prompt(error_prompt_str)
        usr_input = SCREEN.getkey()
    return usr_input

def get_random_tile_number():
    return 4 if random.random() <= FOUR_PROB else 2

def get_empty_position():
    l = []
    for y , row in enumerate(BOARD):
        for x , _ in enumerate(row):
            if BOARD[y][x] == 0:
                l.append((x,y))
    return l

def get_random_empty_position():
    try:
        col, row = random.choice(get_empty_position())
        return row, col
    except IndexError:
        return None

def gen_tile():
    position = get_random_empty_position()
    if position is None:
        return FAIL
    row, col = position
    number = get_random_tile_number()
    BOARD[row][col] = number
    return SUCESS

#startGame
def new_game():
    global BOARD, SCORE, HAS2048, ASK_FOR_ASKCONTINUE, BNDONG
    #清空分数
    BOARD = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    #分数
    SCORE = 0
    #是否通关(2048)
    HAS2048 = False
    #是否能动
    BNDONG = False
    #是否问过是否继续
    ASK_FOR_ASKCONTINUE = False
    #随机生成起始方块
    for _ in range(START_QUBE):
        gen_tile()
    while True:
        print_board()
        check_board()
        if HAS2048 and ASK_FOR_ASKCONTINUE == False:
            INFO = get_usr_input('2048888888! 赠送孔俐裸照一张!\
                按y继续,按q退出',["Y","Q","y","q"])
            if info in 'yY':
                print_prompt('好的,继续游戏...')
                ASK_FOR_ASKCONTINUE = True
            elif INFO in 'qQ':
                print_prompt('好的,结束游戏...')
                break
        elif BNDONG:
            break
        #读取用户输入
        direc = get_usr_input('------孔俐智障小游戏----------',["KEY_UP",'KEY_DOWN', 'KEY_LEFT', "KEY_RIGHT", 'Q', "q"])
        if direc in 'Qq':
            break
        elif direc == "KEY_DOWN":
            direc = DOWN
        elif direc == "KEY_UP":
            direc = UP
        elif direc == 'KEY_LEFT':
            direc = LEFT
        elif direc == "KEY_RIGHT":
            direc = RIGHT
        move_result = move_tile(direc)
        if move_result:
            gen_tile()
    print_score()

#整块板分为(1)顶部的边框和(2)数字和数字下边的边框
#横向同理, (1)左边的边框和(2)数字和数字右边边框

def print_board():
    #顶部边框
    SCREEN.addstr(0, 0, '+----+----+----+----+')
    for y, row in enumerate(BOARD):
        #左侧边框
        SCREEN.addstr(y * 2 + 1, 0, '|')
        #the number
        for x, num in enumerate(row):
            #用0表示当前位置没有方块
            num_str = str(num) if num != 0 else ''
            SCREEN.addstr(y * 2 + 1, x * 5 + 1,\
                num_str + (' ' * (4 - len(num_str))) + '|')
        SCREEN.addstr(y * 2 + 2, 0, '+----+----+----+----+')

def move_tile(direc):
    global SCORE

    def get_line(offset: int, direc: int):
        global BOARD
        if direc == LEFT:
            return BOARD[offset]
        elif direc == RIGHT:
            return list(reversed(BOARD[offset]))
        elif direc == UP:
            return [BOARD[y][offset]for y in range(4)]
        elif direc == DOWN:
            return [BOARD[y][offset]for y in range(3,-1,-1)]

    def put_line(line: list, offset: int , direc: int):
        global BOARD
        if direc == LEFT:
            BOARD[offset] = line
        elif direc == RIGHT:
            BOARD[offset] = list(reversed(line))
        elif direc == UP:
            for y in range(4):
                BOARD[y][offset]= line[y]
        elif direc == DOWN:
            for y in range(4):
                BOARD[y][offset] = line[3 - y]

    def move(line: list):
        new_line = []
        gained_score = 0
        i = 0
        while i < 4:
            if line[i] == 0:
                i += 1
            else:
                old_tile = line[i]
                i += 1
                while i < 4 and line[i] == 0:
                    i += 1
                if i >= 4 or line[i] != old_tile:
                    new_line.append(old_tile)
                else:
                    gained_score += line[i] + old_tile
                    new_line.append(line[i] + old_tile)
                    i += 1
        while len(new_line) < 4:
            new_line.append(0)
        if new_line == line:
            return None
        else:
            return new_line, gained_score

    board_moved = False
    for offset in range(4):
        line = get_line(offset,direc)
        moved_line = move(line)
        if moved_line is not None:
            board_moved = True
            line, gained_score = moved_line
            put_line(line, offset, direc)
            SCORE += gained_score
            put_line(line, offset, direc)
    return board_moved

def get_neighber(x, y, wide, high):
    global VECTOR
    l = []
    for vec in VECTOR:
        n_x = x + vec[0]
        n_y = y + vec[1]
        if 0 <= n_x < wide and 0 <= n_y < high:
            l.append((n_x, n_y))
        return l

def check_board():
    global BOARD, HAS2048, BNDONG
    for y, row in enumerate(BOARD):
        for x, num in enumerate(row):
            if num == 2048:
                HAS2048 = True
                return
            elif num == 0:
                BNDONG = False
                return
            else:
                for n_x, n_y in get_neighber(x,y,4,4):
                    if BOARD[n_y][n_x]==num:
                        BNDONG = False
                        return
    BNDONG = True
    return

def main(stdscr):
    global SCREEN
    SCREEN = stdscr
    while True:
        SCREEN.clear()
        new_game()
        usr_choice = get_usr_input('是否开启下一盘?(输入Y开始,输入Q退出',\
            ['Y','y','Q','q'])
        if usr_choice in 'Qq':
            print_prompt('正在退出...')
            break
        elif usr_choice in 'Yy':
            print_prompt('开始下一盘...')
            continue

if __name__ == '__main__':
    curses.wrapper(main)






























































