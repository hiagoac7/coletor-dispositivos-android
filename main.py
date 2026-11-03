# -*- coding: utf-8 -*-
"""
Coletor de Dispositivos Android - leitor de hardware do aparelho + envio para planilha Google.
Reconstruido a partir do APK original (inventarioti-0.1).
O usuario escolhe seu nome na lista, o app le o hardware e envia para o
Google Sheets (via Apps Script Web App).
"""
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.utils import platform
import threading
import ssl
import urllib.request
import urllib.parse

from pathlib import Path
import json

# Configure localmente; config.json nao deve ser publicado.
CONFIG_PATH = Path(__file__).with_name('config.json')
try:
    CONFIG = json.loads(CONFIG_PATH.read_text(encoding='utf-8'))
except FileNotFoundError:
    CONFIG = {}
SHEETS_URL = CONFIG.get('sheets_url', '').strip()
USUARIOS = ['Selecione o usuario...'] + [
    nome.strip() for nome in CONFIG.get('usuarios', [])
    if isinstance(nome, str) and nome.strip()
]


def coletar_dados():
    """Le os dados de hardware do aparelho Android."""
    dados = {'fabricante': '', 'modelo': '', 'serial': '', 'android': '', 'imei': ''}
    if platform == 'android':
        try:
            from jnius import autoclass
            Build = autoclass('android.os.Build')
            VERSION = autoclass('android.os.Build$VERSION')
            dados['fabricante'] = Build.MANUFACTURER or ''
            dados['modelo'] = Build.MODEL or ''
            dados['android'] = VERSION.RELEASE or ''
            # Serial: tenta getSerial(), depois SERIAL, depois ID
            try:
                dados['serial'] = Build.getSerial()
            except Exception:
                dados['serial'] = Build.SERIAL or Build.ID or ''
            # Identificador unico do dispositivo: ANDROID_ID
            try:
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                context = PythonActivity.mActivity
                Settings = autoclass('android.provider.Settings$Secure')
                dados['imei'] = Settings.getString(context.getContentResolver(), 'android_id') or ''
            except Exception:
                dados['imei'] = ''
        except Exception as e:
            dados['fabricante'] = 'Erro: %s' % e
    else:
        # Fora do Android (teste no PC) usa valores ficticios.
        dados = {'fabricante': 'Samsung', 'modelo': 'Galaxy A32',
                 'serial': 'TEST123', 'android': '13', 'imei': '123456789012345'}
    return dados


def enviar_sheets(payload):
    """Envia os dados para o Google Sheets via POST. Retorna a resposta do servidor."""
    try:
        ctx = ssl.create_default_context()
        if not SHEETS_URL.startswith('https://script.google.com/macros/s/') or not SHEETS_URL.endswith('/exec'):
            return 'Erro: configure uma URL HTTPS valida do Google Apps Script em config.json'
        data = urllib.parse.urlencode(payload).encode()
        req = urllib.request.Request(SHEETS_URL, data=data)
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resposta:
            return resposta.read().decode()
    except Exception as e:
        return 'Erro: %s' % e


class InventarioApp(App):
    def build(self):
        self.dados = coletar_dados()
        root = BoxLayout(orientation='vertical', padding=20, spacing=12)
        root.add_widget(Label(text='Coletor de Dispositivos Android', font_size='20sp',
                              bold=True, size_hint_y=None, height=50))
        info = ('Fabricante: %s\n'
                'Modelo:     %s\n'
                'Serial:     %s\n'
                'Android:    %s\n'
                'Android ID: %s') % (self.dados['fabricante'], self.dados['modelo'],
                                     self.dados['serial'], self.dados['android'],
                                     self.dados['imei'])
        root.add_widget(Label(text=info, font_size='13sp', halign='left', valign='top',
                              size_hint_y=None, height=140))
        root.add_widget(Label(text='Selecione seu nome:', font_size='14sp',
                              size_hint_y=None, height=30))
        self.spinner = Spinner(text=USUARIOS[0], values=USUARIOS, size_hint_y=None, height=44)
        root.add_widget(self.spinner)
        self.btn = Button(text='ENVIAR INVENTARIO', font_size='16sp', bold=True,
                          background_color=(0.16, 0.65, 0.27, 1), size_hint_y=None, height=56)
        self.btn.bind(on_press=self.enviar)
        root.add_widget(self.btn)
        self.status = Label(text='', font_size='13sp', size_hint_y=None, height=40)
        root.add_widget(self.status)
        if not SHEETS_URL or len(USUARIOS) == 1:
            self.btn.disabled = True
            self.status.text = 'Configure config.json antes de compilar.'
        return root

    def enviar(self, *args):
        if self.spinner.text == USUARIOS[0]:
            self.status.text = 'Selecione seu nome primeiro!'
            self.status.color = (1, 0.3, 0.3, 1)
            return
        self.btn.disabled = True
        self.status.text = 'Enviando...'
        self.status.color = (1, 1, 1, 1)
        payload = {
            'usuario': self.spinner.text,
            'fabricante': self.dados['fabricante'],
            'modelo': self.dados['modelo'],
            'serial': self.dados['serial'],
            'android': self.dados['android'],
            'imei': self.dados['imei'],
        }
        threading.Thread(target=self._bg, args=(payload,), daemon=True).start()

    def _bg(self, payload):
        resultado = enviar_sheets(payload)
        Clock.schedule_once(lambda dt: self._fim(resultado), 0)

    def _fim(self, resultado):
        self.btn.disabled = False
        if 'Erro' in resultado:
            self.status.text = 'Falha: %s' % resultado
            self.status.color = (1, 0.3, 0.3, 1)
            return
        self.status.text = 'Dados enviados com sucesso!'
        self.status.color = (0.16, 0.65, 0.27, 1)


if __name__ == '__main__':
    InventarioApp().run()
