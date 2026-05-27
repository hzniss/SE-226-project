"""
REQ 9: Uzun süren işlemler (Gemini API çağrısı, Last.fm sorguları, görsel
       indirme) arka plan thread'inde (threading.Thread) çalışmalıdır; böylece
       GUI donmaz. Bir status label kullanıcıyı mevcut adım hakkında
       bilgilendirir ("Gemini is thinking...", "Fetching tracks...",
       "Generating cover...").

Bu modül app.py tarafından kullanılır. Ham threading.Thread kullanımını
sarmalayan bir WorkerThread sınıfı sunar. Tkinter thread-safe olmadığı için,
worker thread içinde üretilen tüm success/error/status callback'leri
root.after() ile ana (GUI) thread'ine taşınır.
"""

import threading


# ARKA PLAN İŞ ÇALIŞTIRICI (WORKER THREAD)

class WorkerThread:
    """
    Uzun süren bir fonksiyonu arka plan thread'inde çalıştıran yardımcı sınıf.

    Tkinter widget'ları yalnızca ana thread'den güvenle güncellenebildiği için,
    callback'ler doğrudan worker thread'inden çağrılmaz; root.after(0, ...) ile
    ana thread'in event loop'una iletilir.

    Parametreler
    ------------
    root       : Tkinter kök penceresi (tk.Tk). Callback'leri ana thread'e taşır.
    target     : Arka planda çalıştırılacak fonksiyon (örn. generate_full_album).
    args       : target'a geçilecek positional argümanlar (tuple).
    kwargs     : target'a geçilecek keyword argümanlar (dict).
    on_success : target başarıyla dönerse çağrılır; argümanı target'ın dönüş değeri.
    on_error   : target Exception fırlatırsa çağrılır; argümanı Exception nesnesi.
    on_status  : (opsiyonel) ilerleme mesajları için callback; argümanı str mesaj.
                 Verilirse target'a "status_callback" keyword argümanı olarak geçilir.
    """

    def __init__(self, root, target, args=(), kwargs=None,
                 on_success=None, on_error=None, on_status=None):
        self._root = root
        self._target = target
        self._args = args
        self._kwargs = kwargs or {}
        self._on_success = on_success
        self._on_error = on_error
        self._on_status = on_status
        self._thread = None

    def _emit_status(self, message):
        """
        Worker thread içinden çağrılır; status mesajını root.after() ile
        ana (GUI) thread'ine taşır. Böylece Tkinter güvenli şekilde güncellenir.

        Parametreler
        ------------
        message : Status label'da gösterilecek metin
        """
        if self._on_status is not None:
            self._root.after(0, self._on_status, message)

    def _run(self):
        """
        Thread gövdesi. target fonksiyonunu çalıştırır; sonucu on_success'e,
        hatayı on_error'a iletir (her ikisi de root.after() ile ana thread'e).
        on_status verilmişse target'a status_callback olarak _emit_status geçilir.
        """
        kwargs = dict(self._kwargs)          # orijinal kwargs dict'ini bozma
        try:
            if self._on_status is not None:
                kwargs.setdefault("status_callback", self._emit_status)
            result = self._target(*self._args, **kwargs)
        except Exception as e:
            # Hata ana thread'e taşınır; uygulama çökmez, GUI hata kutusu gösterir
            if self._on_error is not None:
                self._root.after(0, self._on_error, e)
            return
        if self._on_success is not None:
            self._root.after(0, self._on_success, result)

    def start(self):
        """
        Daemon thread'i başlatır ve self'i döner (zincirleme kullanım için).
        Daemon olduğundan, uygulama kapanınca thread otomatik sonlanır.

        Dönen değer
        -----------
        WorkerThread  ->  self
        """
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        return self