import pygame
import requests
import config
import sys
import os
import math

try:
    from pygeotile import point
except:
    try:
        os.system('pip install pygeotile')
    except:
        print('Не удалось поставить pygeotile.')
    finally:
         from pygeotile import point


class Label:
    def __init__(self, rect, text):
        self.pressed = False
        self.rect = pygame.Rect(rect)
        self.text = text
        self.bgcolor = (240, 248, 255)
        self.font_color = (59, 68, 75)
        # Рассчитываем размер шрифта в зависимости от высоты
        self.font = pygame.font.Font(None, self.rect.height - 4)
        self.rendered_text = None
        self.rendered_rect = None

    def render(self, surface):
        surface.fill(self.bgcolor, self.rect)
        self.rendered_text = self.font.render(self.text, 1, self.font_color)
        self.rendered_rect = self.rendered_text.get_rect(x=self.rect.x + 2, centery=self.rect.centery)
        # выводим текст
        if self.rendered_rect.w == width:
            print(self.rendered_rect.x)
        surface.blit(self.rendered_text, self.rendered_rect)

    def get_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.pressed = self.rect.collidepoint(event.pos)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.pressed = False

class GUI:
    def __init__(self):
        self.elements = []

    def add_element(self, element):
        self.elements.append(element)

    def render(self, surface):
        for element in self.elements:
            render = getattr(element, "render", None)
            if callable(render):
                element.render(surface)

    def update(self):
        for element in self.elements:
            update = getattr(element, "update", None)
            if callable(update):
                element.update()

    def get_event(self, event):
        for element in self.elements:
            get_event = getattr(element, "get_event", None)
            if callable(get_event):
                element.get_event(event)


class Button(Label):
    def __init__(self, rect, text):  # font_color=(59, 68, 75), font=None, bgcolor=(240, 248, 255)
        super().__init__(rect, text)
        # self.bgcolor = pygame.Color((240, 248, 255))
        # при создании кнопка не нажата
        self.pressed = False
        self.can_click = False
        self.one_click_flag = False

    def render(self, surface):
        if self.can_click:
            surface.fill((59, 68, 75), self.rect)
            self.rendered_text = self.font.render(self.text, 1, self.bgcolor)

        else:
            surface.fill(self.bgcolor, self.rect)
            self.rendered_text = self.font.render(self.text, 1, self.font_color)

        if not self.pressed:
            color1 = pygame.Color("white")
            color2 = pygame.Color("black")
            self.rendered_rect = self.rendered_text.get_rect(x=self.rect.x + 5, centery=self.rect.centery)
        else:
            color1 = pygame.Color("black")
            color2 = pygame.Color("white")
            self.rendered_rect = self.rendered_text.get_rect(x=self.rect.x + 7, centery=self.rect.centery + 2)

        # рисуем границу
        pygame.draw.rect(surface, color1, self.rect, 2)
        pygame.draw.line(surface, color2, (self.rect.right - 1, self.rect.top), (self.rect.right - 1, self.rect.bottom),
                         2)
        pygame.draw.line(surface, color2, (self.rect.left, self.rect.bottom - 1),
                         (self.rect.right, self.rect.bottom - 1), 2)
        # выводим текст
        surface.blit(self.rendered_text, self.rendered_rect)

    def get_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.pressed = self.rect.collidepoint(event.pos)
            if self.rect.collidepoint(event.pos):
                self.pressed = True
                self.one_click_flag = True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.pressed = False

        elif event.type == pygame.MOUSEMOTION:
            self.can_click = self.rect.collidepoint(event.pos)


class TextBox(Label):
    def __init__(self, rect, text):
        super().__init__(rect, text)
        self.active = True
        self.blink = True
        self.blink_timer = 0
        self.entered = False

    def get_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.pressed = self.rect.collidepoint(event.pos)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.pressed = False

        elif event.type == pygame.KEYDOWN and self.active:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.entered = True

            elif event.key == pygame.K_BACKSPACE:
                if len(self.text) > 0:
                    self.text = self.text[:-1]
            else:
                self.text += event.unicode
        elif event.type == pygame.MOUSEBUTTONDOWN:
            was = self.active
            if event.button == 1:
                self.active = self.rect.collidepoint(event.pos)
                if self.active and not was:
                    self.text = ''

    def update(self):
        if pygame.time.get_ticks() - self.blink_timer > 200:
            self.blink = not self.blink
            self.blink_timer = pygame.time.get_ticks()

    def render(self, surface):
        super(TextBox, self).render(surface)
        if self.blink and self.active:
            pygame.draw.line(surface, pygame.Color("black"),
                            (self.rendered_rect.right + 2, self.rendered_rect.top + 2),
                            (self.rendered_rect.right + 2, self.rendered_rect.bottom - 2))


class Checkbox:
    def __init__(self, coors, text):
        self.text = text
        self.activated = False
        self.rect = pygame.Rect(coors)
        self.second_color = (59, 68, 75)
        self.one_time = False
        self.pressed = False

    def get_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.rect.collidepoint(event.pos):
                    self.pressed = True
                    self.one_time = True
                    self.activated = not self.activated
        elif event.type == pygame.MOUSEBUTTONUP:
            self.pressed = False

    def render(self, surface):
        surface.fill((240, 248, 255), self.rect)
        if self.activated:
            pygame.draw.rect(surface, self.second_color, self.rect)
        else:
            pygame.draw.rect(surface, (59, 68, 75), self.rect, 1)

        font = pygame.font.Font(None, 20)
        rendered_text = font.render(self.text, 1, (59, 68, 75))
        rendered_rect = rendered_text.get_rect(x=self.rect.right + 10, centery=self.rect.centery)
        surface_text = pygame.Surface([rendered_rect.w + 6, rendered_rect.h + 4])
        surface_text.fill((255, 255, 255))
        surface.blit(surface_text, (rendered_rect.x - 3, rendered_rect.y - 2))
        surface.blit(rendered_text, rendered_rect)


class App:
    def __init__(self, surface):
        # Инициализация с начальными значениями

        self.lon, self.lat = 50, 0
        self.new_lon, self.new_lat = self.lon, self.lat
        self.curr_layer = layer[0]
        self.surface = surface

        # Интерфейс
        self.gui = GUI()
        self.text_box = TextBox((10, 10, width - 20, 40), '')
        self.gui.add_element(self.text_box)

        self.address_checkbox = Checkbox((10, 60, 20, 20), 'Почтовый индекс')
        self.gui.add_element(self.address_checkbox)

        self.sbros = Button((10, 90, 100, 30), 'Сбросить')
        self.gui.add_element(self.sbros)

        self.change_layer_button = Button((10, 130, 60, 30), layer[0])
        self.gui.add_element(self.change_layer_button)

        # Вспомогательные переменные
        self.height_of_messagebox = 40
        self.font = pygame.font.Font(None, self.height_of_messagebox - 4)

        self.metka = ''
        self.const_change = 0.5
        self.postal_code = '000000'
        self.with_variables = False
        self.key = None
        self.pressed = False
        self.running = True
        self.changed = True
        self.index = False
        self.spns = [0.001, 0.002, 0.004, 0.008, 0.016, 0.032, 0.064, 0.128, 0.256, 0.512, 1.024, 2.048, 4.096, 8.192,
                     16.384, 32.768]  # 65.536, 90
        self.zooms = {32.768: 4, 16.384: 5, 8.192: 6, 4.096: 7, 2.048: 8, 1.024: 9, 0.512: 10, #90: 1, 65.536: 2,
                      0.256: 11, 0.128: 12, 0.064: 13, 0.032: 14, 0.016: 15, 0.008: 16, 0.004: 17, 0.002: 18, 0.001: 19}
        self.zoomsN = {32.768: 3, 16.384: 4, 8.192: 5, 4.096: 6, 2.048: 7, 1.024: 8, 0.512: 9,
                      0.256: 10, 0.128: 11, 0.064: 12, 0.032: 13, 0.016: 14, 0.008: 15, 0.004: 16, 0.002: 17, 0.001: 18} #90: 1, 65.536: 2

        self.spn = 32.768
        # Запросы и прогрузка
        self.geocode_request = None
        self.response = None
        self.map_file = None
        self.api_key = config.api_key
        self.map_request()  # Меняет response(API запрос)
        self.load_image()   # Меняет map_file(surface)


    def calculate_from_pixels(self, pos):
        x_pixel, y_pixel = pos
        delta_x, delta_y = x_pixel - width / 2, y_pixel - height / 2

        central_point = point.Point.from_latitude_longitude(self.lat, self.lon)

        if 32.768 > self.lat:
            zoom = self.zooms[self.spn]
        else:
            zoom = self.zoomsN[self.spn]
        # zoom = 11
        c_x, c_y = central_point.pixels(zoom=zoom)

        click_point = point.Point.from_pixel(int(c_x + delta_x), int(c_y + delta_y), zoom=zoom)
        new_lat, new_lon = click_point.latitude_longitude

        self.new_lon = new_lon
        self.new_lat = new_lat

    # Обработчик событий, потому что возможен случай, когда событий нет, но обновлять надо
    def event_tracker(self, event):
        self.gui.get_event(event)
        if event.type == pygame.QUIT:
            global running
            running = False
            return 0

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                possible = True
                for element in self.gui.elements:
                    if element.pressed:
                        possible = False
                        break

                if possible:
                    self.reset()
                    self.calculate_from_pixels(event.pos)
                    self.metka = ','.join([str(i) for i in [self.new_lon, self.new_lat]])
                    self.rv_geocode()
                # self.find_organisations()

            elif event.button == 3:
                self.with_variables = True
                self.reset()
                self.calculate_from_pixels(event.pos)
                self.find_organisations(','.join([str(i) for i in [self.new_lon, self.new_lat]]))

        if self.text_box.text != '' and self.text_box.entered:  # Обрабатываем введенный текст
            self.with_variables = False
            self.reset()
            self.text_box.entered = False   # Выставляем флаг до следующего enter
            self.geocode_request = self.text_box.text
            self.geocode()                  # Запрос на поиск топонима

        if self.address_checkbox.one_time:  # Проверка изменения чекбокса
            self.address_checkbox.one_time = False
            self.with_variables = False
            self.reset()
            if self.geocode_request != '':  # TODO checkbox
                self.geocode()

        if self.curr_layer != self.change_layer_button.text:  # Проверка на нажатие кнопки
            self.changed = True
        self.curr_layer = self.change_layer_button.text

        if self.change_layer_button.pressed and self.change_layer_button.one_click_flag:
            self.change_layer_button.one_click_flag = False
            if layer.index(self.change_layer_button.text) < 2:
                self.change_layer_button.text = layer[layer.index(self.change_layer_button.text) + 1]
            else:
                self.change_layer_button.text = layer[0]

        if self.sbros.pressed == 1:
            self.with_variables = True
            self.reset()

        self.resize(event)              # Меняет spn
        self.filter_events(event)       # Считываем нажатия клавиш (запомниаем нажатые)

    # И update, и render (не зависит от событий)
    def update(self):
        self.gui.update()               # Обновляем элементы интерфейса (внешний вид)
        self.move()                     # Двигаемся по карте в зависимости от нажатых клавиш
        if self.changed:                # Запрос, если изменились параметры
            if self.curr_layer == 'skl':
                self.curr_layer = 'sat' # Костыль для отрисовки карты, следующий запрос для отрисовки наименований обьектов
                self.map_request()      # Меняет response
                self.load_image()       # Меняет map_file(surface)
                self.curr_layer = 'skl'
                self.surface.blit(pygame.image.load(self.map_file), (0, 0))

            if not self.pressed:
                self.changed = False
            self.map_request()          # Меняет response(API запрос)
            self.load_image()           # Меняет map_file(surface)
            self.surface.blit(pygame.image.load(self.map_file), (0, 0))
        self.gui.render(self.surface)
        pygame.display.flip()

    # Запрос
    def map_request(self):
        try:
            # print(self.curr_layer)
            # Все данные берем из self
            api_server = "http://static-maps.yandex.ru/1.x/"
            params = {
                "ll": ",".join([str(self.lon), str(self.lat)]),
                "spn": ",".join([str(self.spn), str(self.spn)]),
                "l": self.curr_layer,
                'z': '8',
            }
            if self.metka:
                params['pt'] = "{0},pm2dgl".format(self.metka)
            response = requests.get(api_server, params=params)  # Пробный запрос

            if not response:
                print("Ошибка выполнения запроса:")
                print(self.map_request)
                print("Http статус:", response.status_code, "(", response.reason, ")")
                sys.exit(1)

            self.response = response

        except:
            print(self.spn)
            print(self.lon, self.lat)
            print("Запрос не удалось выполнить. Проверьте наличие сети Интернет.")
            sys.exit(1)

    # Прогрузка
    def load_image(self):
        map_file = "map.png"
        try:
            with open(map_file, "wb") as file:
                file.write(self.response.content)
            self.map_file = map_file  # Присваиваем surface классовой переменной
        except IOError as ex:
            print("Ошибка записи временного файла:", ex)
            sys.exit(2)

    # Масштабирование
    def resize(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_PAGEUP:
                spn = self.spns.index(self.spn)
                self.changed = True
                if spn < len(self.spns) - 1:
                    spn += 1
                self.spn = self.spns[spn]
            elif event.key == pygame.K_PAGEDOWN and self.spn * 0.5 >= 0:
                spn = self.spns.index(self.spn)
                self.changed = True
                if spn > 0:
                    spn -= 1
                self.spn = self.spns[spn]
        # print(self.spn)

    # Поиск по запросу
    def find_organisations(self, coords):
        search_api_server = "https://search-maps.yandex.ru/v1/"
        search_params = {
            "apikey": self.api_key,
            "lang": "ru_RU",
            "ll": coords,
            "spn": "0.00032,0.00032",
            "type": "biz"
        }
        response = requests.get(search_api_server, params=search_params)
        if not response:
            # ...
            pass
        json_response = response.json()
        try:
            organization = json_response["features"][0]["properties"]["CompanyMetaData"]
            org_name = organization["name"]
            rendered_text = self.font.render(org_name, 1, (0, 0, 0))
            rendered_rect = rendered_text.get_rect()
            label = Label((0, 350, rendered_rect.w + 8, 40), org_name)
            self.gui.add_element(label)
        except:
            rendered_text = self.font.render('Организация не надена', 1, (0, 0, 0))
            rendered_rect = rendered_text.get_rect()
            label = Label((0, 350, rendered_rect.w + 8, 40), 'Организация не найдена')
            self.gui.add_element(label)

        self.changed = True

    # Поиск по запросу
    def rv_geocode(self):
        geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
        geocoder_params = {"geocode": str(self.new_lon)+',' + str(self.new_lat), "format": "json"}
        response = requests.get(geocoder_api_server, params=geocoder_params)
        if not response:
            # обработка ошибочной ситуации
            pass
        # Преобразуем ответ в json-объект
        json_response = response.json()
        # Получаем первый топоним из ответа геокодера.

        adr = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["metaDataProperty"][
            "GeocoderMetaData"]["text"]
        if self.address_checkbox.activated:
            try:
                self.postal_code = \
                json_response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty'][
                    'GeocoderMetaData']['Address']['postal_code']
            except:
                self.postal_code = '000000'
            self.adr = adr + ", " + self.postal_code
        else:
            self.geocode_request = adr
            self.adr = adr

        self.changed = True
        rendered_text = self.font.render(self.adr, 1, (0, 0, 0))
        rendered_rect = rendered_text.get_rect()
        label = Label((0, 400, rendered_rect.w + 8, 40), self.adr)
        self.gui.add_element(label)

    # Поиск по запросу
    def geocode(self):
        geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
        geocoder_params = {"geocode": self.geocode_request, "format": "json"}

        response = requests.get(geocoder_api_server, params=geocoder_params)
        if not response:
            # обработка ошибочной ситуации
            pass

        # Преобразуем ответ в json-объект
        json_response = response.json()
        # Получаем первый топоним из ответа геокодера.
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"]
        if len(toponym) > 0:
            toponym = toponym[0]["GeoObject"]
        # Координаты центра топонима:
            toponym_coodrinates = toponym["Point"]["pos"]
        # Долгота и Широта :
            toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
            self.lat, self.lon = float(toponym_lattitude), float(toponym_longitude)
            self.spn = 0.032
            self.new_lon, self.new_lat = self.lon, self.lat
            self.metka = ','.join([str(i) for i in [toponym_longitude, toponym_lattitude]])
            self.rv_geocode()

        else:
            label = Label((0, 400, 300, 30), 'Ничего не удалось найти')
            self.gui.add_element(label)
        self.changed = True

    # Считываем нажатия клавиш
    def filter_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_RIGHT, pygame.K_DOWN, pygame.K_LEFT, pygame.K_UP]:
                self.key = event.key
                self.pressed = True

        if event.type == pygame.KEYUP:
            if event.key in [pygame.K_RIGHT, pygame.K_DOWN, pygame.K_LEFT, pygame.K_UP]:
                self.key = None
                self.pressed = False

    # Меняем координаты для перемещения
    def move(self):
        delta = None
        if self.pressed:
            if self.key == pygame.K_RIGHT:    # Смещаемся вверх
                self.lon += self.const_change * self.spn
                delta = self.lon - self.const_change * self.spn
            elif self.key == pygame.K_DOWN:   # Смещаемся вниз
                self.lat -= self.const_change * self.spn
                delta = "lat+"
            elif self.key == pygame.K_LEFT:   # Смещаемся влево
                self.lon -= self.const_change * self.spn
                delta = self.lon + self.const_change * self.spn
            elif self.key == pygame.K_UP:     # Смещаемся вправо
                self.lat += self.const_change * self.spn
                delta = "lat-"

            self.changed = True

        try:
            self.map_request()
        except:
            if type(delta) == float:
                self.lon = -(delta)

            elif type(delta) == str:
                if delta == "lat-":
                    self.lat -= self.const_change * self.spn
                else:
                    self.lat += self.const_change * self.spn

    def reset(self):
        if self.with_variables:
            self.metka = ''
            self.address_checkbox.activated = False
            self.text_box.text = ''
        for element in range(len(self.gui.elements) - 1, -1, -1):
            if type(self.gui.elements[element]) == Label:
                del self.gui.elements[element]
                self.changed = True
    # def find_organisations(self):
        # self.mouse_click_position


pygame.init()
size = width, height = 600, 450

screen = pygame.display.set_mode(size)
layer = ('map', 'sat', 'skl')
running = True
app = App(screen)
while running:
    for event in pygame.event.get():
        # if event.type != pygame.MOUSEMOTION:  # Баг pygame - реакция на MOUSEMOTION.
        app.event_tracker(event)
    app.update()

pygame.quit()
os.remove(app.map_file)
