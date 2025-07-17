import pygame
import random
import sys

#混音器初始化（采样频率，16位深度，双声道立体声，音频缓冲区512位）
pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
# 初始化pygame
pygame.init()

# 游戏常量
BG_COLOR = (240, 240, 240)#背景颜色
BUTTON_COLOR = (255, 255, 255)#按钮颜色
BUTTON_HOVER_COLOR = (200, 200, 200)#按钮悬停颜色
TEXT_COLOR = (0, 0, 0)#文本颜色
FONT_SIZE = 24#字体大小
BUTTON_PADDING = 20#按钮内边距
FONT_NAME='SimHei'#字体名称

#这一部分地址需要注意修改！！！！！！！！

# 风格1：木质风格
STYLE1 = {
    "background": "D:\\Python文件\\wood.jpg",
    "cell_bg": "D:\\Python文件\\cell_bg2.jpg"
}
# 风格2：金属风格
STYLE2 = {
    "background": "D:\\Python文件\\mental_background.jpg",  
    "cell_bg": "D:\\Python文件\\mental_cell_bg.jpg"  
}
#风格3：冰块风格
STYLE3 = {
    "background": "D:\\Python文件\\ice_background.jpg",  
    "cell_bg": "D:\\Python文件\\ice_cell_bg1.jpg"  
}
STYLE4 = {
    "background": "D:\\Python文件\\leather_background2.jpg",  
    "cell_bg": "D:\\Python文件\\leather_cell_bg.png"  
}

# 当前使用的风格
current_style = 1  
background_image_paths = [STYLE1["background"], STYLE2["background"],STYLE3["background"],STYLE4["background"]]
cell_bg_paths = [STYLE1["cell_bg"], STYLE2["cell_bg"],STYLE3["cell_bg"],STYLE4["cell_bg"]]

#使用混音器加载音频文件
pygame.mixer.music.load("D:\\Python文件\\Various Artists - SpongeBob Closing Theme_H.ogg")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1) 
move_sound=pygame.mixer.Sound("D:\\Python文件\\a480001.wav")

#游戏窗口基本设置
SCREEN_WIDTH, SCREEN_HEIGHT = 600, 500
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("数字华容道")
font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)

background_image = pygame.image.load(background_image_paths[current_style - 1]).convert()
cell_bg_image = pygame.image.load(cell_bg_paths[current_style - 1]).convert_alpha()



class Puzzle:
    def __init__(self, grid_size=3):
        self.grid_size = grid_size
        self.reset()
    
    def reset(self):
        # 初始化游戏状态
        self.board = [[i + j * self.grid_size + 1 for i in range(self.grid_size)] 
                      for j in range(self.grid_size)]
        self.board[self.grid_size-1][self.grid_size-1] = self.grid_size * self.grid_size  # 最后一格为空白
        self.empty_pos = (self.grid_size-1, self.grid_size-1)
        self.moves = 0
        self.solved = False
        self.counting_moves = True#标记：开始计数（真）暂停计数（假）

        # 打乱棋盘（确保有解）
        self.shuffle()
        self.counting_moves = True
    def get_empty_neighbors(self):
        # 获取空白格子的相邻可移动位置
        x, y = self.empty_pos
        neighbors = []
        
        # 检查上下左右四个方向
        if x > 0:
            neighbors.append((x-1, y))
        if x < self.grid_size-1:
            neighbors.append((x+1, y))
        if y > 0:
            neighbors.append((x, y-1))
        if y < self.grid_size-1:
            neighbors.append((x, y+1))
            
        return neighbors
    
    def is_solvable(self):
        # 检查拼图是否有解（仅适用于奇数网格）
        flat_board = []
        for row in self.board:
            flat_board.extend(row)
        flat_board.remove(self.grid_size * self.grid_size)
        
        inversions = 0
        for i in range(len(flat_board)):
            for j in range(i + 1, len(flat_board)):
                if flat_board[i] > flat_board[j]:
                    inversions += 1
                    
        # 对于奇数网格，逆序数必须为偶数才有解
        # 对于偶数网格，需要更复杂的判断逻辑
        if self.grid_size % 2 == 1:
            return inversions % 2 == 0
        else:
            # 偶数网格判断：空白行号(从下往上)为奇数时，逆序数需为偶数；空白行号为偶数时，逆序数需为奇数
            blank_row = self.grid_size - self.empty_pos[0]
            return (inversions % 2 == 0) == (blank_row % 2 == 1)
    
    def shuffle(self):
        self.counting_moves = False #新增
        # 打乱棋盘
        # 先确保有解
        while True:
            # 生成随机排列
            numbers = list(range(1, self.grid_size * self.grid_size + 1))
            random.shuffle(numbers)
            
            # 填充棋盘
            for i in range(self.grid_size):
                for j in range(self.grid_size):
                    self.board[i][j] = numbers[i * self.grid_size + j]
                    if numbers[i * self.grid_size + j] == self.grid_size * self.grid_size:
                        self.empty_pos = (i, j)
            
            # 检查是否有解
            if self.is_solvable():
                break
        
        # 进行随机移动使打乱更彻底
        for _ in range(100 * self.grid_size):
            neighbors = self.get_empty_neighbors()
            if neighbors:
                self._move_without_count(random.choice(neighbors))
            
    
    def move(self, pos):
        # 只有计数开启时，才累加 moves
        if not self.counting_moves:
            return self._move_without_count(pos)#新增
        
        
        # 移动数字到空白位置
        if pos not in self.get_empty_neighbors():
            return False
            
        x, y = pos
        empty_x, empty_y = self.empty_pos
        
        # 交换位置
        self.board[empty_x][empty_y], self.board[x][y] = self.board[x][y], self.board[empty_x][empty_y]
        self.empty_pos = (x, y)
        self.moves += 1
        move_sound.play()
        
        # 检查是否解决
        self.check_solved()
        return True
    #新增
    def _move_without_count(self, pos):
            # 辅助方法：仅交换位置，不增加 moves（打乱时用）
            if pos not in self.get_empty_neighbors():
                return False
            
            x, y = pos
            empty_x, empty_y = self.empty_pos
        
            self.board[empty_x][empty_y], self.board[x][y] = self.board[x][y], self.board[empty_x][empty_y]
            self.empty_pos = (x, y)
            return True

    
    def check_solved(self):
        # 检查是否完成拼图
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.board[i][j] != i * self.grid_size + j + 1 and self.board[i][j] != self.grid_size * self.grid_size:
                    self.solved = False
                    return
        self.solved = True
    
    def draw(self):
        global screen ,background_image,cell_bg_image # 声明使用全局 screen 变量
        # 计算格子大小和窗口尺寸
        cell_size = min(500 // self.grid_size, 100)
        gap = 10
        window_size = (cell_size * self.grid_size + gap * (self.grid_size - 1), 
                       cell_size * self.grid_size + gap * (self.grid_size - 1) + 50)
        
        # 调整窗口大小
        screen = pygame.display.set_mode(window_size)
        #screen.fill(BG_COLOR)
        scaled_bg = pygame.transform.scale(background_image, window_size)
        screen.blit(scaled_bg,(0,0))
        
        
        cell_bg_image = pygame.transform.scale(cell_bg_image, (cell_size, cell_size))#缩放图片使其适应格子大小  
        # 绘制每个格子
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.board[i][j] != self.grid_size * self.grid_size:
                    # 计算格子位置
                    x = j * (cell_size + gap)
                    y = i * (cell_size + gap)
                    #添加阴影增加立体感
                    #圆形素材单独添加阴影
                    if current_style==4:
                        shadow_surface=pygame.Surface((cell_size,cell_size),pygame.SRCALPHA)
                        pygame.draw.ellipse(shadow_surface, (0, 0, 0, 80), (0, 0, cell_size, cell_size))
                    #方形素材添加方形阴影
                    else:
                         # 阴影：在格子下方偏移 (3,3)，半透明黑色
                        shadow_surface = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
                        shadow_surface.fill((0, 0, 0, 80))  # 80 是透明度（0-255）
                    # 阴影偏移
                    screen.blit(shadow_surface, (x + 3, y + 3))
                    
                    # 绘制格子
                    scaled_cell_bg = pygame.transform.scale(cell_bg_image, (cell_size, cell_size))
                    screen.blit(cell_bg_image, (x, y))  # 绘制格子背景图
                    # 绘制数字
                    text = font.render(str(self.board[i][j]), True, (0,0,0))
                    text_rect = text.get_rect(center=(x + cell_size//2, y + cell_size//2))
                    screen.blit(text, text_rect)
        
        # 显示移动次数
        
        moves_text = font.render(f"移动次数: {self.moves}", True, TEXT_COLOR)
        screen.blit(moves_text, (10, window_size[1] - 40))
        
        # 如果游戏完成，显示提示
        if self.solved:
    # 分成两行文本
            line1 = "恭喜！你完成了拼图！"
            line2 = "按ESC键返回选关界面"
    
    # 分别渲染两行文本
            text1 = font.render(line1, True, (0, 0, 0))
            text2 = font.render(line2, True, (0, 0, 0))
    
    # 计算文本位置（垂直居中并间隔30像素）
            center_x = window_size[0] // 2
            center_y = window_size[1] // 2
    
            rect1 = text1.get_rect(center=(center_x, center_y - 30))
            rect2 = text2.get_rect(center=(center_x, center_y + 30))
    
    # 绘制文本
            screen.blit(text1, rect1)
            screen.blit(text2, rect2)
        
        
        '''
        if self.solved:
            solved_text = font.render("恭喜！你完成了拼图！按ESC键返回选关界面", True, (0, 150, 0))
            text_rect = solved_text.get_rect(center=(window_size[0]//2, window_size[1]//2))
            screen.blit(solved_text, text_rect)
        '''
        pygame.display.flip()#更新屏幕

def reset_screen_to_start_size():
    #重置窗口大小为开始界面的尺寸
    global screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))    

def draw_start_screen():
    global screen,background_image,cell_bg_image,current_style
    #screen.fill(BG_COLOR)
    scaled_bg = pygame.transform.scale(background_image, (SCREEN_WIDTH,SCREEN_HEIGHT))
    screen.blit(scaled_bg,(0,0))
    
    # 标题
    title = font.render("数字华容道", True, (0, 0, 0))
    title_rect = title.get_rect(center=(300, 100))
    screen.blit(title, title_rect)
    
    # 按钮定义
    buttons = [
        {"text": "3x3", "rect": pygame.Rect(200, 180, 200, 60)},
        {"text": "4x4", "rect": pygame.Rect(200, 260, 200, 60)},
        {"text": "5x5", "rect": pygame.Rect(200, 340, 200, 60)},
        {"text": "换肤", "rect": pygame.Rect(500, 10, 50, 50)}  # 新增的切换风格按钮
    ]
    
    # 绘制按钮
    mouse_pos = pygame.mouse.get_pos()
    for button in buttons:
        if button["rect"].collidepoint(mouse_pos):
            pygame.draw.rect(screen, BUTTON_HOVER_COLOR, button["rect"], border_radius=10)
        else:
            pygame.draw.rect(screen, BUTTON_COLOR, button["rect"], border_radius=10)
        
        text = font.render(button["text"], True, TEXT_COLOR)
        text_rect = text.get_rect(center=button["rect"].center)
        screen.blit(text, text_rect)
    
    pygame.display.flip()
    return buttons

def main():
    global current_style, background_image, cell_bg_image
    current_state = "start"  # start, game
    puzzle = None
    
    while True:
        if current_state == "start":
            reset_screen_to_start_size() 
            buttons = draw_start_screen()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    # 检查是否点击了切换风格按钮
                    if buttons[3]["rect"].collidepoint(mouse_pos):
                        current_style = current_style % 4 + 1  # 4种风格循环切换
                        # 重新加载对应风格的图片
                        background_image = pygame.image.load(background_image_paths[current_style - 1]).convert()
                        cell_bg_image = pygame.image.load(cell_bg_paths[current_style - 1]).convert_alpha()
                    else:
                        for button in buttons:
                            if button["rect"].collidepoint(mouse_pos):
                                grid_size = int(button["text"][0])
                                puzzle = Puzzle(grid_size)
                                current_state = "game"
        
        elif current_state == "game":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and not puzzle.solved:
                    # 处理鼠标点击
                    cell_size = min(500 // puzzle.grid_size, 100)
                    gap = 10
                    window_height = cell_size * puzzle.grid_size + gap * (puzzle.grid_size - 1) + 50
                    
                    x, y = event.pos
                    # 忽略底部的移动次数区域
                    if y < window_height - 50:
                        cell_x = x // (cell_size + gap)
                        cell_y = y // (cell_size + gap)
                        
                        # 检查点击是否在有效范围内
                        if 0 <= cell_x < puzzle.grid_size and 0 <= cell_y < puzzle.grid_size:
                            puzzle.move((cell_y, cell_x))
            
            # 绘制游戏
            puzzle.draw()
            
            # 检查是否想返回开始界面（按ESC键）
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                current_state = "start"
        
        pygame.time.delay(30)

if __name__ == "__main__":
    main()