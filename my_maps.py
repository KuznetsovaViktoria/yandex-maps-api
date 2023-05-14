import PyQt5
from PyQt5 import QtWidgets, QtCore
from mydesign import Ui_MainWindow
import sys
import requests
from PyQt5 import Qt
from urllib import request


class mywindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(mywindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.show_btn.clicked.connect(self.btnClicked)

        self.ui.type.addItem("Схема местности и названия географических объектов")
        self.ui.type.addItem("Местность, сфотографированная со спутника")
        self.ui.type.addItem("Названия географических объектов")
        self.ui.type.addItem("Слой пробок")
        self.ui.type.activated[str].connect(self.onActivated_type)
        self.ui.lang.addItem("Русский")
        self.ui.lang.addItem("Английский")
        self.ui.lang.addItem("Турецкий")
        self.ui.lang.activated[str].connect(self.onActivated_lang)
        self.ui.scale.setValue(17)
        self.ui.scale.valueChanged.connect(self.onActivated_scale)
        self.ui.measure.addItem("километры")
        self.ui.measure.addItem("мили")
        self.ui.measure.activated[str].connect(self.onActivated_meas)

    def onActivated_scale(self):
        if not beginnig:
            self.btnClicked()

    def onActivated_meas(self, chosen_m):
        global measure, lang
        if lang != "tr":
            if chosen_m == "километры":
                measure = "RU"
            else:
                measure = "US"

    def onActivated_lang(self, chosen_l):
        global lang, measure
        if chosen_l == "Русский":
            lang = "ru"
        if chosen_l == "Английский":
            lang = "en"
        if chosen_l == "Турецкий":
            lang = "tr"
            measure = "TR"

    def onActivated_type(self, chosen_t):
        global map_type
        if chosen_t == "Схема местности и названия географических объектов":
            map_type = 'map'
        if chosen_t == "Местность, сфотографированная со спутника":
            map_type = 'sat'
        if chosen_t == "Названия географических объектов":
            map_type = 'map,skl'
        if chosen_t == "Слой пробок":
            map_type = 'map,trf'

    def btnClicked(self):
        global map_type, z, lang, measure, beginnig
        try:
            beginnig = False
            address = self.ui.address.text()
            response = requests.get('http://geocode-maps.yandex.ru/1.x/',
                                    {'format': 'json', 'apikey': 'c75d8015-3980-4e89-b9b3-aa53671ac43a',
                                     'geocode': address})
            pos = response.json()['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']["Point"]['pos']
            pos = pos.replace(' ', ',')
            z = str(self.ui.scale.value())
            r = requests.get('http://static-maps.yandex.ru/1.x/',
                             {'ll': pos, 'l': map_type, 'z': z, 'pt': pos + ',flag', 'lang': lang + '_' + measure})
            data = request.urlopen(r.url).read()
            pixmap = Qt.QPixmap()
            pixmap.loadFromData(data)
            self.ui.l_picture.setScaledContents(True)
            self.ui.l_picture.setPixmap(pixmap)

            pos = pos.split(',')
            weather = requests.get('http://api.weather.yandex.ru/v2/forecast', params={'lat': pos[1], 'lon': pos[0]},
                                   headers={'X-Yandex-API-Key': 'b89c2d13-37bb-4db0-a0c1-bdcfbc98013e'})
            weather_pic = f"http://yastatic.net/weather/i/icons/blueye/color/svg/{weather.json()['fact']['icon']}.svg"
            data_1 = request.urlopen(weather_pic).read()
            pixmap_1 = Qt.QPixmap()
            pixmap_1.loadFromData(data_1)
            pixmap_1 = pixmap_1.scaled(64, 64, QtCore.Qt.KeepAspectRatio)
            self.ui.forecast_pic.setPixmap(pixmap_1)
            self.ui.forecast_pic.move(300, 600)
            self.ui.forecast_text.setText(
                f"Температура {weather.json()['fact']['temp']}°C, ощущается как {weather.json()['fact']['feels_like']}°C")


        except Exception:
            self.ui.l_picture.setText(
                'Что-то пошло не так... Попробуйте исправить адрес и/или проверить соединение с интернетом')
            self.ui.forecast_pic.setText('')
            self.ui.forecast_text.setText('')


map_type = 'map'
z = '17'
lang = 'ru'
measure = 'RU'
beginnig = True
app = QtWidgets.QApplication([])
application = mywindow()
application.show()
sys.exit(app.exec())
