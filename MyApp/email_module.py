from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


class EmailTemplates(EmailMessage):

    def __init__(self, uuid):
        super().__init__()
        self.uuid64 = urlsafe_base64_encode(force_bytes(uuid)) if uuid else None

    def send_register_confirmation(self, *args, **kwargs):
        self.subject = "Aktywuj swoje konto na Oddaj Niechciane"
        self.body = self.render_register_message(kwargs['name'], kwargs['uuid'])
        self.from_email = settings.EMAIL_HOST_USER
        self.to = kwargs['to']
        self.send()

    def create_activation_link(self, request):
        domain = get_current_site(request).domain
        link_uuid = self.uuid64
        activate_link = f'{domain}/verify/{link_uuid}'

        reverse('verify-activation-link', kwargs={
            'link': link_uuid,
        })
        return activate_link

    @staticmethod
    def render_register_message(name, uuid):
        message = f"""
        Witaj, {name}\n\n\n\tCieszymy sie, ze dolaczasz do naszej spolecznosci.
        Przekonaj sie sam, ze niesienie pomocy nie jest wcale takie trudne czy czasochlonne.
        
        Potwierdz swoje konto, aby stac sie czlonkiem 
        naszej spolecznosci i popraiwac sytuacje potrzebujacych.Jedyne 
        czego potrzebujemy to potwierdzenia twojego konta. 
        
        Aby to zrobic kliknij w link ponizej.
        {uuid}
        
        Witamy na pokladzie!
        Zespol Oddaj Niechciane
        """
        return message

    def send_reset_password_link(self, *args, **kwargs):
        self.subject = "Zresetuj hasło na Oddaj niechciane"

        self.body = self.render_reset_password_message(
            kwargs['name'], kwargs['uuid']
        )

        self.from_email = settings.EMAIL_HOST_USER
        self.to = kwargs['to']
        self.send()

    def create_reset_password_link(self, request):
        domain = get_current_site(request).domain
        link_uuid = self.uuid64
        activate_link = f'{domain}/password/reset/{link_uuid}'

        reverse('reset-password', kwargs={
            'link': link_uuid,
        })
        return activate_link

    @staticmethod
    def render_reset_password_message(name, uuid):
        message = f"""
            Witaj, {name}\n\t
            
            Zresetuj swoje haslo.
            Aby to zrobic kliknij w link ponizej.
            {uuid}
            
            Zespol Oddaj Niechciane
            """
        return message
