from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import QDir, Qt, QUrl, QSize
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel, QStyleFactory,
        QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget, QStatusBar)
import ffmpeg
from functools import reduce

'''
TODO: предпросмотр обрезки
'''

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

        markButton = QPushButton("mark")
        # markButton.setEnabled(False)
        markButton.clicked.connect(self.markerSet)

        self.positionSlider = QSlider(Qt.Orientation.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        self.statusBar = QStatusBar()
        self.statusBar.setFont(QFont("Noto Sans", 7))
        self.statusBar.setFixedHeight(14)

        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(openButton)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(markButton)
        controlLayout.addWidget(exportButton)
        controlLayout.addWidget(self.positionSlider)

        layout = QVBoxLayout()
        layout.addWidget(videoWidget)
        layout.addLayout(controlLayout)
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
        v = self.positionSlider.value()
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
        #!!!
        print(self.intervalArr)
        in_file = ffmpeg.input(self.fileName)
        def combine_intervals(a, b):
            return in_file.trim(start_frame=a, end_frame=b)
        a = reduce(combine_intervals, self.intervalArr)
        print(a)
        (
            ffmpeg
            .concat(a)
            .output('output.mp4')
            .run()
        )

        # (
        # ffmpeg
        # .concat(
        #     [in_file.trim(
        #         start_frame=self.intervalArr[i][0],
        #         end_frame=self.intervalArr[i][1]
        #     )
        #     for i in range(len(self.intervalArr))]
        # )
        # .output('output.mp4')
        # .run()
        # )
        

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.setWindowTitle("Player")
    player.resize(900, 600)
    player.show()
    sys.exit(app.exec())