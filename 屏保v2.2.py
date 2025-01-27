import pygame
import random
import threading
import gc

# 初始化字体大小和字符列表
font_size = 36
characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+-=[]{}|;':\",.<>?/"

class TextDrop:
    def __init__(self, min_speed, max_speed):
        self.text = random.choice(characters)
        self.angle = random.randint(-180, 180)
        self.rotation_angle = random.uniform(-5, 5)
        self.speed_y = random.uniform(min_speed, max_speed)
        self.x = random.randint(0, pygame.display.Info().current_w)
        self.y = -font_size
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def update(self):
        self.angle += self.rotation_angle
        self.y += self.speed_y

def draw_text_drops(drops, screen, font, batch_size):
    screen.fill(pygame.Color('black'))
    for i in range(0, len(drops), batch_size):
        batch = drops[i:i + batch_size]
        for drop in batch:
            text_surface = font.render(drop.text, True, drop.color)
            text_rect = text_surface.get_rect(center=(drop.x, drop.y))
            # 更新旋转角度
            drop.update()
            # 旋转并绘制表面
            rotated_text_surface = pygame.transform.rotate(text_surface, drop.angle)
            rotated_rect = rotated_text_surface.get_rect(center=text_rect.center)
            screen.blit(rotated_text_surface, rotated_rect.topleft)

def update_drops(drops, start, end):
    for i in range(start, end):
        drops[i].update()

def optimized_main(num_drops=500, min_speed=1, max_speed=5, batch_size=200):
    pygame.init()
    infoObject = pygame.display.Info()
    width, height = infoObject.current_w, infoObject.current_h
    screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
    # 隐藏鼠标光标
    pygame.mouse.set_visible(False)
    font = pygame.font.Font(None, font_size)
    # 初始化下落物列表
    drops = [TextDrop(min_speed, max_speed) for _ in range(num_drops)]
    running = True
    clock = pygame.time.Clock()
    num_threads = 5  # 减少线程数量以减少开销
    gc.disable()
    frame_count = 0
    while running:
        draw_text_drops(drops, screen, font, batch_size)
        # 创建并启动线程
        threads = []
        for i in range(num_threads):
            start = i * (num_drops // num_threads)
            end = (i + 1) * (num_drops // num_threads)
            thread = threading.Thread(target=update_drops, args=(drops, start, end))
            threads.append(thread)
            thread.start()
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                running = False
        # 移除屏幕外的下落物并添加新的下落物
        drops = [drop for drop in drops if drop.y < height + font_size]
        drops += [TextDrop(min_speed, max_speed) for _ in range(num_drops - len(drops))]
        pygame.display.flip()
        clock.tick(60)
        # 每120帧手动运行垃圾回收
        frame_count += 1
        if frame_count % 120 == 0:
            gc.collect()
        # 输出调试信息
        print(f"Frame {frame_count}: Number of drops = {len(drops)}")
    pygame.quit()

# 调用优化后的主函数而不是原始的主函数
if __name__ == "__main__":
    optimized_main()