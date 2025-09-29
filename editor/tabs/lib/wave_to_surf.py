import pygame
from pydub import AudioSegment
import numpy as np

# FIXME: 파형 에디터에 표시하기


# ===== 1. 오디오 불러오기 & 파형 압축 =====
def load_waveform(filename, height):
    # 오디오 불러오기
    song = AudioSegment.from_file(filename)

    # numpy 배열로 변환
    samples = np.array(song.get_array_of_samples())
    if song.channels == 2:  # 스테레오면 모노 변환
        samples = samples.reshape(-1, 2).mean(axis=1)

    # 파형 압축 (픽셀 수에 맞게)
    step = max(1, len(samples) // height)
    compressed = np.array([samples[i:i+step].mean() for i in range(0, len(samples), step)])

    return compressed, song.frame_rate, len(samples) / song.frame_rate  # (파형, 샘플레이트, 총 길이(초))


# ===== 2. 파형 Surface 그리기 =====
def render_waveform(data, size):
    width, height = size
    surf = pygame.Surface(size)
    surf.fill((0, 0, 0))

    mid_x = width // 2
    max_amp = max(abs(data.min()), abs(data.max()))

    # 데이터가 화면보다 많으면 downsample
    step = max(1, len(data) // height)
    reduced = data[::step]

    points = [
        (mid_x + int(sample / max_amp * (width // 2)), y)
        for y, sample in enumerate(reduced[:height])
    ]

    if len(points) > 1:
        pygame.draw.lines(surf, (0, 255, 0), False, points, 1)

    return surf


if __name__ == "__main__":
    filename = r"D:\chris\my_python\MathDash\assets\tutorial\music.wav"  # 사용할 음악 파일
    display_size = (400, 600)  # 화면 크기 (세로형)
    waveform_height = 20000     # 전체 파형 해상도 (너무 작으면 뭉개짐)

    # 오디오 불러오기
    waveform, frame_rate, song_length = load_waveform(filename, waveform_height)

    # pygame 초기화
    pygame.init()
    pygame.mixer.init()
    pygame.display.set_caption("Waveform Viewer")
    screen = pygame.display.set_mode(display_size)
    clock = pygame.time.Clock()

    # 파형 Surface 준비
    waveform_surf = render_waveform(waveform, (display_size[0], waveform_height))

    # 음악 재생
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 현재 재생 위치
        pos_ms = pygame.mixer.music.get_pos()
        pos_s = pos_ms / 1000.0

        # 스크롤 위치 계산 (세로 기준)
        scroll_y = int((pos_s / song_length) * waveform_surf.get_height())

        # 화면 그리기
        screen.fill((30, 30, 30))
        screen.blit(waveform_surf, (0, -scroll_y + display_size[1] // 2))

        # 중앙 커서 (가로선)
        pygame.draw.line(screen, (255, 0, 0),
                         (0, display_size[1] // 2),
                         (display_size[0], display_size[1] // 2), 2)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
