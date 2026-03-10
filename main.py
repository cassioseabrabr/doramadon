
import os, sys, threading, asyncio
from pathlib import Path
os.environ["KIVY_NO_ENV_CONFIG"] = "1"
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.gridlayout import GridLayout
from kivy.uix.checkbox import CheckBox
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.utils import get_color_from_hex

BG=get_color_from_hex("#0d0f1a");BG2=get_color_from_hex("#141728")
BG3=get_color_from_hex("#1c2035");ACCENT=get_color_from_hex("#e94560")
SUCCESS=get_color_from_hex("#2ecc71");TEXT=get_color_from_hex("#eaf0fb")
MUTED=get_color_from_hex("#5a6480");ACCENT2=get_color_from_hex("#f5a623")
Window.clearcolor=BG

try:
    from android.storage import primary_external_storage_path
    STORAGE=Path(primary_external_storage_path())/"DoramaDown"
except:
    STORAGE=Path.home()/"DoramaDown"
SESSION_FILE=STORAGE/"sessao"
DOWNLOAD_DIR=STORAGE/"Videos"
SESSION_FILE.parent.mkdir(parents=True,exist_ok=True)
DOWNLOAD_DIR.mkdir(parents=True,exist_ok=True)
API_ID=2040;API_HASH="b18441a1ff607e10a989891a5462e627"
_client=None;_loop=None

def get_loop():
    global _loop
    if _loop is None or _loop.is_closed():
        _loop=asyncio.new_event_loop()
        threading.Thread(target=_loop.run_forever,daemon=True).start()
    return _loop

def run_async(coro):
    return asyncio.run_coroutine_threadsafe(coro,get_loop())

def lbl(text,size=14,color=None,bold=False,halign="left"):
    l=Label(text=text,font_size=dp(size),color=color or TEXT,bold=bold,
            halign=halign,valign="middle",size_hint_y=None)
    l.bind(texture_size=lambda i,v:setattr(i,"height",v[1]+dp(8)))
    l.bind(width=lambda i,v:setattr(i,"text_size",(v,None)))
    return l

def btn(text,on_press,bg=None,color=None,size=14):
    b=Button(text=text,font_size=dp(size),size_hint_y=None,height=dp(48),
             background_normal="",background_color=bg or ACCENT,
             color=color or TEXT,bold=True)
    b.bind(on_press=on_press)
    return b

def sep():
    from kivy.uix.widget import Widget
    from kivy.graphics import Color,Rectangle
    w=Widget(size_hint_y=None,height=dp(1))
    with w.canvas:
        Color(*MUTED);w._r=Rectangle(pos=w.pos,size=w.size)
    w.bind(pos=lambda i,v:setattr(i._r,"pos",v))
    w.bind(size=lambda i,v:setattr(i._r,"size",v))
    return w

def inp(hint,pw=False,text=""):
    return TextInput(hint_text=hint,text=text,password=pw,font_size=dp(15),
                     size_hint_y=None,height=dp(48),background_color=BG3,
                     foreground_color=TEXT,cursor_color=TEXT,
                     hint_text_color=MUTED,multiline=False,
                     padding=(dp(12),dp(12)))

class LoginScreen(Screen):
    def __init__(self,**kw):
        super().__init__(**kw)
        root=BoxLayout(orientation="vertical",padding=dp(20),spacing=dp(16))
        root.add_widget(lbl("DoramaDown",size=22,bold=True,halign="center"))
        root.add_widget(lbl("Baixador de vídeos do Telegram",size=13,color=MUTED,halign="center"))
        root.add_widget(sep())
        root.add_widget(lbl("Número de telefone",size=13,color=MUTED))
        self.tel=inp("Ex: +5511999998888",text="+55")
        root.add_widget(self.tel)
        self.status=lbl("",size=12,color=MUTED,halign="center")
        root.add_widget(self.status)
        self.btn_l=btn("Entrar no Telegram",self._login)
        root.add_widget(self.btn_l)
        ok=Path(str(SESSION_FILE)+".session").exists()
        root.add_widget(lbl("Sessão salva encontrada!" if ok else f"Sessão: {SESSION_FILE}.session",
                            size=11,color=SUCCESS if ok else MUTED,halign="center"))
        from kivy.uix.widget import Widget
        root.add_widget(Widget())
        self.add_widget(root)

    def _login(self,*a):
        tel=self.tel.text.strip()
        if not tel or tel=="+55":
            self.status.text="Digite seu número";self.status.color=ACCENT;return
        self.btn_l.disabled=True;self.status.text="Conectando...";self.status.color=MUTED
        threading.Thread(target=self._worker,args=(tel,),daemon=True).start()

    def _worker(self,tel):
        try:
            from telethon import TelegramClient
            global _client
            SESSION_FILE.parent.mkdir(parents=True,exist_ok=True)
            _client=TelegramClient(str(SESSION_FILE),API_ID,API_HASH)
            run_async(_client.connect()).result(timeout=30)
            if run_async(_client.is_user_authorized()).result(timeout=10):
                me=run_async(_client.get_me()).result(timeout=10)
                Clock.schedule_once(lambda dt:self._ok(f"{me.first_name} ({me.phone})"))
                return
            run_async(_client.send_code_request(tel)).result(timeout=30)
            Clock.schedule_once(lambda dt:self._pedir_codigo(tel))
        except Exception as ex:
            Clock.schedule_once(lambda dt:self._erro(str(ex)))

    def _pedir_codigo(self,tel):
        c=BoxLayout(orientation="vertical",padding=dp(16),spacing=dp(12))
        c.add_widget(lbl("Código do Telegram:",size=14,halign="center"))
        ci=inp("Digite o código")
        c.add_widget(ci)
        pop=Popup(title="Verificação",content=c,size_hint=(0.85,None),height=dp(250),background_color=BG2)
        def ok(*a):
            pop.dismiss()
            threading.Thread(target=self._codigo,args=(tel,ci.text.strip()),daemon=True).start()
        c.add_widget(btn("Confirmar",ok))
        pop.open()

    def _codigo(self,tel,codigo):
        try:
            from telethon.errors import SessionPasswordNeededError
            try:
                run_async(_client.sign_in(tel,codigo)).result(timeout=30)
            except SessionPasswordNeededError:
                Clock.schedule_once(lambda dt:self._pedir_senha());return
            me=run_async(_client.get_me()).result(timeout=10)
            Clock.schedule_once(lambda dt:self._ok(f"{me.first_name} ({me.phone})"))
        except Exception as ex:
            Clock.schedule_once(lambda dt:self._erro(str(ex)))

    def _pedir_senha(self):
        c=BoxLayout(orientation="vertical",padding=dp(16),spacing=dp(12))
        c.add_widget(lbl("Senha 2FA:",size=14,halign="center"))
        si=inp("Senha",pw=True)
        c.add_widget(si)
        pop=Popup(title="2FA",content=c,size_hint=(0.85,None),height=dp(250),background_color=BG2)
        def ok(*a):
            pop.dismiss()
            threading.Thread(target=self._senha,args=(si.text.strip(),),daemon=True).start()
        c.add_widget(btn("Confirmar",ok))
        pop.open()

    def _senha(self,senha):
        try:
            run_async(_client.sign_in(password=senha)).result(timeout=30)
            me=run_async(_client.get_me()).result(timeout=10)
            Clock.schedule_once(lambda dt:self._ok(f"{me.first_name} ({me.phone})"))
        except Exception as ex:
            Clock.schedule_once(lambda dt:self._erro(str(ex)))

    def _ok(self,nome):
        self.status.text=f"✓ {nome}";self.status.color=SUCCESS
        self.btn_l.text="✓ Conectado!"
        self.manager.get_screen("grupos").carregar()
        self.manager.transition=SlideTransition(direction="left")
        self.manager.current="grupos"

    def _erro(self,msg):
        self.status.text=f"Erro: {msg}";self.status.color=ACCENT
        self.btn_l.disabled=False;self.btn_l.text="Tentar novamente"

class GruposScreen(Screen):
    def __init__(self,**kw):
        super().__init__(**kw)
        self._grupos=[]
        root=BoxLayout(orientation="vertical",padding=dp(16),spacing=dp(10))
        hdr=BoxLayout(size_hint_y=None,height=dp(44))
        hdr.add_widget(lbl("Grupos e Canais",size=17,bold=True))
        hdr.add_widget(btn("↺",lambda *a:self.carregar(),bg=BG3,size=13))
        root.add_widget(hdr)
        root.add_widget(sep())
        self.status=lbl("Carregando...",size=12,color=MUTED)
        root.add_widget(self.status)
        scroll=ScrollView()
        self.lista=GridLayout(cols=1,spacing=dp(6),size_hint_y=None,padding=dp(4))
        self.lista.bind(minimum_height=self.lista.setter("height"))
        scroll.add_widget(self.lista)
        root.add_widget(scroll)
        self.add_widget(root)

    def carregar(self):
        threading.Thread(target=self._worker,daemon=True).start()

    def _worker(self):
        global _client
        try:
            async def _l():
                g=[]
                async for d in _client.iter_dialogs():
                    if d.is_group or d.is_channel:
                        g.append({"id":d.id,"nome":d.name})
                return g
            self._grupos=run_async(_l()).result(timeout=60)
            Clock.schedule_once(self._mostrar)
        except Exception as ex:
            Clock.schedule_once(lambda dt:setattr(self.status,"text",f"Erro: {ex}"))

    def _mostrar(self,*a):
        self.lista.clear_widgets()
        self.status.text=f"{len(self._grupos)} grupos/canais"
        for g in self._grupos:
            b=Button(text=f"  {g[\"nome\"]}",font_size=dp(14),size_hint_y=None,height=dp(52),
                     background_normal="",background_color=BG2,color=TEXT,
                     halign="left",text_size=(Window.width-dp(40),None))
            b.grupo=g
            b.bind(on_press=self._abrir)
            self.lista.add_widget(b)

    def _abrir(self,b):
        self.manager.get_screen("videos").carregar(b.grupo)
        self.manager.transition=SlideTransition(direction="left")
        self.manager.current="videos"

class VideosScreen(Screen):
    def __init__(self,**kw):
        super().__init__(**kw)
        self._videos=[];self._grupo=None;self._checks={};self._baixando=False
        root=BoxLayout(orientation="vertical",padding=dp(16),spacing=dp(10))
        hdr=BoxLayout(size_hint_y=None,height=dp(44))
        self.titulo=lbl("Vídeos",size=17,bold=True)
        hdr.add_widget(self.titulo)
        hdr.add_widget(btn("←",self._voltar,bg=BG3,size=13))
        root.add_widget(hdr);root.add_widget(sep())
        self.status=lbl("",size=12,color=MUTED);root.add_widget(self.status)
        self.prog=ProgressBar(max=100,value=0,size_hint_y=None,height=dp(12))
        self.prog_info=lbl("",size=11,color=MUTED)
        root.add_widget(self.prog);root.add_widget(self.prog_info)
        sr=BoxLayout(size_hint_y=None,height=dp(40),spacing=dp(8))
        sr.add_widget(btn("✓ Todos",lambda *a:[setattr(c,"active",True) for c in self._checks.values()],bg=BG3,size=12))
        sr.add_widget(btn("✗ Nenhum",lambda *a:[setattr(c,"active",False) for c in self._checks.values()],bg=BG3,size=12))
        root.add_widget(sr)
        scroll=ScrollView()
        self.lista=GridLayout(cols=1,spacing=dp(4),size_hint_y=None,padding=dp(4))
        self.lista.bind(minimum_height=self.lista.setter("height"))
        scroll.add_widget(self.lista);root.add_widget(scroll)
        self.btn_b=btn("⬇  BAIXAR SELECIONADOS",self._baixar,size=15)
        root.add_widget(self.btn_b)
        self.add_widget(root)

    def _voltar(self,*a):
        self.manager.transition=SlideTransition(direction="right")
        self.manager.current="grupos"

    def carregar(self,grupo):
        self._grupo=grupo;self._videos=[];self._checks={}
        self.lista.clear_widgets()
        self.titulo.text=grupo["nome"][:25]
        self.status.text="Buscando vídeos..."
        threading.Thread(target=self._worker,daemon=True).start()

    def _worker(self):
        global _client
        try:
            from telethon.tl.types import MessageMediaDocument
            async def _l():
                vids=[]
                async for msg in _client.iter_messages(self._grupo["id"],limit=200):
                    if msg.media and isinstance(msg.media,MessageMediaDocument):
                        doc=msg.media.document
                        if doc and doc.mime_type and doc.mime_type.startswith("video"):
                            nome=f"video_{msg.id}.mp4"
                            for a in doc.attributes:
                                if hasattr(a,"file_name") and a.file_name:
                                    nome=a.file_name;break
                            vids.append({"id":msg.id,"nome":nome,
                                         "tamanho":round(doc.size/1024/1024,1),
                                         "data":msg.date.strftime("%d/%m/%y"),"msg":msg})
                return vids
            self._videos=run_async(_l()).result(timeout=120)
            Clock.schedule_once(self._mostrar)
        except Exception as ex:
            Clock.schedule_once(lambda dt:setattr(self.status,"text",f"Erro: {ex}"))

    def _mostrar(self,*a):
        self.lista.clear_widgets();self._checks={}
        self.status.text=f"{len(self._videos)} vídeos"
        for v in self._videos:
            row=BoxLayout(size_hint_y=None,height=dp(56),spacing=dp(8))
            cb=CheckBox(size_hint_x=None,width=dp(40),active=True,color=ACCENT)
            self._checks[v["id"]]=cb;row.add_widget(cb)
            info=BoxLayout(orientation="vertical")
            info.add_widget(Label(text=v["nome"],font_size=dp(12),color=TEXT,
                                  halign="left",valign="middle",text_size=(Window.width-dp(120),None)))
            info.add_widget(Label(text=f"{v[\"tamanho\"]} MB • {v[\"data\"]}",font_size=dp(11),color=MUTED,
                                  halign="left",valign="middle",text_size=(Window.width-dp(120),None)))
            row.add_widget(info)
            self.lista.add_widget(row)

    def _baixar(self,*a):
        if self._baixando:return
        sel=[v for v in self._videos if self._checks.get(v["id"]) and self._checks[v["id"]].active]
        if not sel:
            self.status.text="Selecione ao menos um vídeo!";self.status.color=ACCENT;return
        self._baixando=True;self.btn_b.disabled=True;self.btn_b.text="Baixando..."
        threading.Thread(target=self._baixar_worker,args=(sel,),daemon=True).start()

    def _baixar_worker(self,videos):
        global _client
        import time
        total=len(videos)
        for i,v in enumerate(videos,1):
            inicio=time.time()
            caminho=DOWNLOAD_DIR/v["nome"]
            Clock.schedule_once(lambda dt,n=v["nome"],ii=i,t=total:
                setattr(self.status,"text",f"[{ii}/{t}] {n[:30]}..."))
            def cb(atual,tot,_i=i,_t=total,_ini=inicio):
                if tot:
                    pct=int((atual/tot)*100);mb=round(atual/1024/1024,1)
                    mbt=round(tot/1024/1024,1);el=time.time()-_ini
                    vel=mb/el if el>0 else 0
                    g=int(((_i-1)/_t)*100+pct/_t)
                    Clock.schedule_once(lambda dt:(setattr(self.prog,"value",g),
                        setattr(self.prog_info,"text",f"{mb}/{mbt} MB • {vel:.1f} MB/s")))
            try:
                run_async(_client.download_media(v["msg"],str(caminho),progress_callback=cb)).result(timeout=3600)
            except Exception as ex:
                Clock.schedule_once(lambda dt,e=ex:setattr(self.status,"text",f"Erro: {e}"))
        Clock.schedule_once(self._concluido)

    def _concluido(self,*a):
        self._baixando=False;self.prog.value=100
        self.prog_info.text="Concluído!"
        self.status.text=f"✓ Salvos em: {DOWNLOAD_DIR}";self.status.color=SUCCESS
        self.btn_b.disabled=False;self.btn_b.text="⬇  BAIXAR SELECIONADOS"

class DoramaDownApp(App):
    def build(self):
        sm=ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(GruposScreen(name="grupos"))
        sm.add_widget(VideosScreen(name="videos"))
        return sm

if __name__=="__main__":
    DoramaDownApp().run()

