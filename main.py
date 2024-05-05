from PyQt6.QtCore import Qt, QUrl, QSize
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWidgets import (QApplication, QFileDialog, QHBoxLayout,
        QPushButton, QSlider, QStyle, QVBoxLayout, QWidget, QStatusBar)
from moviepy.editor import VideoFileClip, concatenate_videoclips

'''
TODO    Предпросмотр обрезки
        Маркеры вырезаемых видео
        Клавиши для движения по кадрам
'''

def crop_and_concat_video(input_video, frame_ranges, output_path):
    video_clip = VideoFileClip(input_video)
    cropped_clips = []

    for frame_range in frame_ranges:
        start_frame, end_frame = [i/1000 for i in frame_range]
        cropped_clip = video_clip.subclip(t_start=start_frame, t_end=end_frame)
        cropped_clips.append(cropped_clip)
    
    final_clip = concatenate_videoclips(cropped_clips)
    
    final_clip.write_videofile(output_path, codec='libx264', fps=video_clip.fps)
    
    # Освобождение ресурсов
    final_clip.close()
    video_clip.close()

class VideoPlayer(QWidget):

    def __init__(self, parent=None):
        super(VideoPlayer, self).__init__(parent)

        self.marker = None
        self.intervalArr = []

        self.mediaPlayer = QMediaPlayer()

        btnSize = QSize(16, 16)
        videoWidget = QVideoWidget()
        self._audio_output = QAudioOutput()
        self.mediaPlayer.setAudioOutput(self._audio_output)
        openButton = QPushButton("Open")   
        openButton.setToolTip("Open Video File")
        openButton.setStatusTip("Open Video File")
        openButton.clicked.connect(self.abrir)

        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.clicked.connect(self.play)
        self.playButton.clicked.connect(self.getCurrentTime)

        exportButton = QPushButton("Export")
        # exportButton.setEnabled(False)
        exportButton.clicked.connect(self.export)

        leftButton = QPushButton("<")

        markButton = QPushButton("∧")
        # markButton.setEnabled(False)
        markButton.clicked.connect(self.markerSet)

        rightButton = QPushButton(">")

        markLayout = QHBoxLayout()
        markLayout.setContentsMargins(0, 0, 0, 0)
        markLayout.setSpacing(0)
        markLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        markLayout.addWidget(leftButton)
        markLayout.addWidget(markButton)
        markLayout.addWidget(rightButton)

        self.positionSlider = QSlider(Qt.Orientation.Horizontal)
        # self.positionSlider.setTickPosition(QSlider.TickPosition.TicksAbove)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.setSingleStep(1)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        self.statusBar = QStatusBar()
        self.statusBar.setFixedHeight(14)

        controlLayout = QHBoxLayout()
        controlLayout.setSpacing(1)
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(openButton)
        controlLayout.addWidget(exportButton)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.positionSlider)

        layout = QVBoxLayout()
        layout.addWidget(videoWidget)
        layout.addLayout(controlLayout)
        layout.addLayout(markLayout)
        layout.addWidget(self.statusBar)
        
        self.setLayout(layout)

        #help(self.mediaPlayer)
        self.mediaPlayer.setVideoOutput(videoWidget)
        
        self.mediaPlayer.playbackStateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.errorChanged.connect(self.handleError)
        self.statusBar.showMessage("Ready")

    def abrir(self):
        self.fileName, _ = QFileDialog.getOpenFileName(self, "Select Media",
                ".", "Video Files (*.mp4 *.flv *.ts *.mts *.avi)")

        if self.fileName != '':
            self.mediaPlayer.setSource(QUrl.fromLocalFile(self.fileName))
            self.playButton.setEnabled(True)
            self.statusBar.showMessage(self.fileName)
            self.play()

    def play(self):
        if self.mediaPlayer.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def mediaStateChanged(self, state):
        if self.mediaPlayer.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        else:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))

    def getCurrentTime(self, position):
        print(self.positionSlider.value())

    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def markerSet(self, position):
        v = self.mediaPlayer.position()
        
        print(self.marker, v)
        if self.marker == None:
            self.marker = v
        elif self.marker == v:
            self.marker = None
        else:
            self.intervalArr.append([self.marker, v])
            self.marker = None
        print(self.intervalArr)

    def handleError(self):
        self.playButton.setEnabled(False)
        self.statusBar.showMessage("Error: " + self.mediaPlayer.errorString())

    def export(self):
        print(self.intervalArr)
        crop_and_concat_video(self.fileName, self.intervalArr, "outp.mp4")

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.setWindowTitle("Player")
    player.resize(900, 600)
    player.show()
    sys.exit(app.exec())