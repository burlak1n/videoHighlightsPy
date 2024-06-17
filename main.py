from PyQt6.QtCore import Qt, QUrl, QPoint
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel, QGridLayout,
        QPushButton, QSlider, QStyle, QVBoxLayout, QWidget, QStatusBar, QStyleOptionSlider)
from PyQt6.QtGui import QColor, QPixmap, QPen, QPainter, QBrush, QPolygon
from moviepy.editor import VideoFileClip, concatenate_videoclips

from entities import MarkDeq, arrSide, bookmarkM

class Marker(QLabel):
    def __init__(self, parent=None):
        super(Marker, self).__init__(parent)
        self._slider = None
        # self.setAcceptDrops(True) 
        pix = QPixmap(30, 30)
        pix.fill(QColor("transparent"))
        paint = QPainter(pix)
        slider_color = QColor(255, 255, 255)
        handle_pen = QPen(QColor(slider_color.darker(200)))
        handle_pen.setWidth(3)
        paint.setPen(handle_pen)
        paint.setBrush(QBrush(slider_color, Qt.BrushStyle.SolidPattern))
        points = QPolygon([
            QPoint(5, 5),
            QPoint(5, 19),
            QPoint(13, 27),
        
            QPoint(21, 19),
            QPoint(21, 5),

        ])
        paint.drawPolygon(points)
        del paint
        self.setPixmap(pix)

class myTimeline(QWidget):
    def __init__(self, parent=None):
        super(myTimeline, self).__init__(parent)
        layout = QGridLayout(self)
        self.intervalValues = MarkDeq()
        layout.setSpacing(0)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        # self.slider.setTickPosition(QSlider.TickPosition.TicksAbove)
        # self.slider.setTickInterval(1)
        self.slider.setSingleStep(1)
        self.slider.setRange(0, 0)
        # self.slider.setAcceptDrops(True)
        self.resize(self.width(), 50)
        layout.addWidget(self.slider)

    def create_marker(self):
        bookmark = Marker(self)
        opt = QStyleOptionSlider()
        self.slider.initStyleOption(opt)
        rect = self.slider.style().subControlRect(
            QStyle.ComplexControl.CC_Slider,
            opt,
            QStyle.SubControl.SC_SliderHandle,
            self.slider
        )
        bookmark.move(rect.center().x(), 0)
        bookmark.show()
        self.slider.style()
        bookmarkM[rect.center().x()] = bookmark

    def delete_marker(self, x):
        # print("del", bookmarkM, x)
        bookmarkM[x].clear()
        del bookmarkM[x]

    def mouseDoubleClickEvent(self, event):
        self.create_marker()

        # [i/1000 for i in frame_range] ------_!
    # def paintEvents(self):
    #     # super().paintEvent(event)
    #     painter = QPainter(self)
    #     painter.setPen(Qt.PenStyle.NoPen)
    #     painter.setBrush(QColor('green'))


        # handle_rect = self.handleRect()
        # for range in self.intervalValues:
        #     start = self.__value

    # def paintEvent(self, event):
    #     super().paintEvent(event)
    #     painter = QPainter(self)
    #     painter.setPen(Qt.PenStyle.NoPen)
    #     painter.setBrush(QColor('green'))

    #     for range in self.green_ranges:
    #         start = self.__value_to_pos(range[0])
    #         end = self.__value_to_pos(range[1])
    #         rect = QRect(start, 0, end - start, self.height())
    #         painter.drawRect(rect)

    # def mous
class VideoPlayer(QWidget):

    def __init__(self, parent=None):
        super(VideoPlayer, self).__init__(parent)

        self.marker = None

        self.mediaPlayer = QMediaPlayer()

        videoWidget = QVideoWidget()
        self._audio_output = QAudioOutput()
        self.mediaPlayer.setAudioOutput(self._audio_output)
        openButton = QPushButton("Open")   
        openButton.setToolTip("Open Video File")
        openButton.setStatusTip("Open Video File")
        openButton.clicked.connect(self.abrir)

        self.playButton = QPushButton()
        self.playButton.clicked.connect(self.play)
        self.playButton.clicked.connect(self.getCurrentTime)

        exportButton = QPushButton("Export")
        exportButton.clicked.connect(self.export)

        leftButton = QPushButton("<")
        leftButton.clicked.connect(self.changePosition)

        markButton = QPushButton("∧")
        markButton.clicked.connect(self.markerSet)

        rightButton = QPushButton(">")
        rightButton.clicked.connect(self.changePosition)

        self.positionSlider = QSlider(Qt.Orientation.Horizontal)
        # Не работает на маке
        # self.positionSlider.setTickPosition(QSlider.TickPosition.TicksAbove)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.setSingleStep(1)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        self.timeline = myTimeline()
        self.timeline.slider.sliderMoved.connect(self.setPosition)

        markLayout = QHBoxLayout()
        markLayout.setContentsMargins(0, 0, 0, 0)
        markLayout.setSpacing(0)
        markLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        markLayout.addWidget(leftButton)
        markLayout.addWidget(markButton)
        markLayout.addWidget(rightButton)
        markLayout.addWidget(self.playButton)
        markLayout.addWidget(self.timeline)

        self.statusBar = QStatusBar()
        self.statusBar.setFixedHeight(14)

        controlLayout = QHBoxLayout()
        controlLayout.setSpacing(1)
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(openButton)
        controlLayout.addWidget(exportButton)

        layout = QVBoxLayout()
        layout.addWidget(videoWidget)
        layout.addLayout(markLayout)
        layout.addLayout(controlLayout)
        layout.addWidget(self.statusBar)
        
        self.setLayout(layout)

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
        # handle_rect = self.timeline.slider.handleRect()
        # x = handle_rect.x()
        # y = handle_rect.y()
        # print(self.timeline.slider.value())
        pass

    def positionChanged(self, position):
        self.timeline.slider.setValue(position)

    def durationChanged(self, duration):
        self.timeline.slider.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def markerSet(self, position):
        v = self.mediaPlayer.position()
        # print(v)
        if self.timeline.intervalValues.insertV(v):
            # self.timeline.paintEvent()
            self.timeline.create_marker()
        else:
            opt = QStyleOptionSlider()
            self.timeline.slider.initStyleOption(opt)
            self.timeline.delete_marker(self.timeline.slider.style().subControlRect(
                QStyle.ComplexControl.CC_Slider,
                opt,
                QStyle.SubControl.SC_SliderHandle,
                self.timeline.slider
            ).center().x())
            self.screenError("Маркер удалён")
            # print(bookmarkM, len(bookmarkM))

        
        # print(self.marker, v)
        # if self.marker == None:
        #     self.marker = v
        # elif self.marker == v:
        #     self.marker = None
        # else:
        #     #draw rectangle 
        #     self.marker = None
    def screenError(self, s):
        self.statusBar.showMessage(s)
    def changePosition(self):

        v = self.timeline.intervalValues.pos(
            self.mediaPlayer.position(), 
            arrSide[self.sender().text()]
        )
        if v:
            self.setPosition(v)
            # self.positionChanged(v)
            return
        self.screenError("Добавьте маркер")

    def handleError(self):
        self.playButton.setEnabled(False)
        self.statusBar.showMessage("Error: " + self.mediaPlayer.errorString())

    def export(self):
        a = self.timeline.intervalValues.pairs()
        # print(self.timeline.intervalValues, a)
        if a:
            crop_and_concat_video(self.fileName, a, "outp.mp4")
            self.screenError("Файл сохранён в папке app, из которой производился запуск")
        else:
            self.screenError("Нечётное количество маркеров, добавьте или удалите один")

def crop_and_concat_video(input_video, frame_ranges, output_path):
    video_clip = VideoFileClip(input_video)
    cropped_clips = []
    print(frame_ranges)
    for start_frame, end_frame in frame_ranges:
        cropped_clip = video_clip.subclip(t_start=start_frame, t_end=end_frame)
        cropped_clips.append(cropped_clip)
    
    final_clip = concatenate_videoclips(cropped_clips)
    
    final_clip.write_videofile(output_path, codec='libx264', fps=video_clip.fps)
    
    # Освобождение ресурсов
    final_clip.close()
    video_clip.close()

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.setWindowTitle("Player")
    player.resize(900, 600)
    player.show()
    sys.exit(app.exec())