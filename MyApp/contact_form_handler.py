from django.contrib import messages


def send(request, user_model, email, host):
    data = request.GET
    if data.get('name') and data.get('surname') and data.get('message'):
        try:

            users = [user.email for user in user_model.objects.all() if user.is_superuser]
            e = email(None)
            e.subject = 'Zlozono nowy formularz kontaktowy.'
            e.body = f"""
                Uzytkownik {data.get('name')} {data.get('surname')} napisal:
            
            
                {data.get('message')}
                """
            e.from_email = host
            e.to = users
            e.send()

        except KeyError:
            return False

        msg = "Dziekujemy za kontakt. Odpowiemy najszybciej jak jest to mozliwe!"
        messages.add_message(request, messages.INFO, msg)
        return True

