import datetime
import pprint

import uuid

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.password_validation import validate_password

from django.core.paginator import Paginator
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect

from django.utils.http import urlsafe_base64_decode
from django.views import View

from django.core.exceptions import ObjectDoesNotExist, ValidationError

from MyApp import models as m
from MyApp.email_module import EmailTemplates
from MyApp import contact_form_handler


# Create your views here.


class LandingPageView(View):
    def get(self, request):
        cls = m.Donation
        institutions = m.Institution.objects.all()

        items_per_page = 2

        # Filter to extract all types of institutions.
        institutions_dict = {

            1: Paginator(institutions.filter(type=1), items_per_page),

            2: Paginator(institutions.filter(type=2), items_per_page),

            3: Paginator(institutions.filter(type=3), items_per_page),
        }

        page = request.META.get('HTTP_CURRENT_PAGE', None)
        if page:
            institution_type = int(request.META.get('HTTP_INSTITUTION_TYPE', 1))
            query_set = institutions_dict[institution_type].get_page(page)
            data = m.Institution.query_set_to_json(query_set)
            return JsonResponse(data, safe=False)

        # Handle contact form.
        if contact_form_handler.send(
            request,
            m.ExtendedUser,
            EmailTemplates,
            settings.EMAIL_HOST_USER
        ):
            return redirect('user-confirmation')

        context = {
            'bags': cls.quantity_sum(),
            'institutions_count': cls.count_supported_institutions(),

            'foundations': institutions_dict[1].get_page(1),
            'foundations_pages': institutions_dict[1].page_range,

            'n_gov_organizations': institutions_dict[2].get_page(1),
            'organization_pages': institutions_dict[2].page_range,

            'local_collections': institutions_dict[3].get_page(1),
            'collections_pages': institutions_dict[3].page_range,
        }

        return render(request, 'MyApp/index.html', context=context)


class AddDonationView(LoginRequiredMixin, View):
    login_url = settings.LOGIN_URL

    def get(self, request):
        categories = m.Category.objects.all()
        institutions = m.Institution.objects.all()
        context = {
            'categories': categories,
            'institutions': institutions,
        }

        return render(request, 'MyApp/form.html', context=context)

    def post(self, request):

        # User provided data.
        data = request.POST
        quantity = data.get('bags', 1)
        categories = data.getlist('categories')
        institution = m.Institution.objects.get(id=data.get('organization'))
        address = data.get('address')
        phone_number = data.get('phone')
        city = data.get('city')
        post_code = data.get('postcode')
        pick_up_date = data.get('data')
        pick_up_time = data.get('time')
        pick_up_remarks = data.get('more_info')

        try:
            donation = m.Donation.objects.create(
                quantity=quantity,
                institution=institution,
                address=address,
                phone_number=phone_number,
                city=city,
                post_code=post_code,
                pick_up_date=pick_up_date,
                pick_up_time=pick_up_time,
                pick_up_remarks=pick_up_remarks,
                user=request.user
            )
            donation.categories.set(categories)
            donation.save()
        except (ValidationError, ValueError):
            return redirect('landing-page')

        return redirect('form-confirmation')


class AddDonationConfirmationView(View):
    def get(self, request):
        context = {
            'display_donation': True
        }
        return render(request, 'MyApp/form-confirmation.html', context=context)


class LoginView(View):
    def get(self, request):
        context = {
            'display_login_register_navbar': True
        }
        return render(request, 'MyApp/login.html', context=context)

    def post(self, request):
        data = request.POST
        email = data.get('email')
        password = data.get('password')
        if user := m.ExtendedUser.validate_user_data(email, password):

            if not user.account_is_active:

                msg = """Konto nie zostalo aktywowane. 
                Link zostal przeslany na podany adres e-mail."""

                messages.add_message(request, messages.INFO, msg)
                return redirect('login')

            login(request, user)
            return redirect('landing-page')

        return redirect('register')


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('landing-page')


class RegisterView(View):
    def get(self, request):
        context = {
            'display_login_register_navbar': True
        }

        return render(request, 'MyApp/register.html', context=context)

    def post(self, request):
        data = request.POST

        first_name = data.get('name')
        surname = data.get('surname')
        user_email = data.get('email')
        password = data.get('password')
        password2 = data.get('password2')

        error = None
        password_not_equal = None
        try:
            validate_password(password)
        except ValidationError as err:
            error = err

        if password != password2:
            password_not_equal = "Hasla sie roznia."

        if error or password_not_equal:
            messages.add_message(request, messages.ERROR, password_not_equal)
            for e in error:
                messages.add_message(request, messages.ERROR, e)
            return redirect('register')

        if user := m.ExtendedUser.objects.create_user(
            first_name=first_name,
            last_name=surname,
            email=user_email,
            username=user_email,
            password=password,
        ):

            email = EmailTemplates(user.activation.activation_uuid)
            email.send_register_confirmation(
                name=first_name,
                uuid=email.create_activation_link(request),
                to=[user_email]
            )

            msg = """
                    Dziękujemy za rejestracje w naszym serwisie. 
                    Link aktywacyjny zostanie przeslany na podany adres e-mail.
                """

            messages.add_message(request, messages.INFO, msg)

            return redirect('user-confirmation')

        return redirect('register')


class UserProfileView(View):
    def get(self, request):
        return render(request, 'MyApp/user-profile.html')


class UserProfileModifyAccessView(View):
    def get(self, request):
        return render(request, 'MyApp/user-profile-modify-access.html')

    def post(self, request):
        password = request.POST.get('password')
        user = authenticate(username=request.user.username, password=password)
        if user:
            return redirect('user-profile-modify')
        return redirect('landing-page')


class UserProfileModifyView(View):
    def get(self, request):
        return render(request, 'MyApp/user-profile-modify.html')

    def post(self, request):
        data = request.POST

        # User profile data.
        last_name = data.get('last_name')
        first_name = data.get('first_name')
        email = data.get('email')

        # User password.
        user_password_update = {
            'old_password': data.get('old_password'),
            'new_password': data.get('new_password'),
            'new_password2': data.get('new_password2'),
        }
        check_password_string = (
                user_password_update['new_password']
                ==
                user_password_update['new_password2']
        )

        assess_passwords = (
                request.user.check_password(
                    user_password_update['old_password'])
                and check_password_string
        )

        user = request.user
        if any(user_password_update.values()) and assess_passwords:
            user.set_password(user_password_update['new_password'])
            authenticate(request)

        user.last_name = last_name
        user.first_name = first_name
        user.email = email
        user.username = email
        user.save()

        login(request, user)
        return redirect('user-profile-modify')


class UserDonationView(View):
    def get(self, request):
        filter_query = request.GET.get('search')
        donations = request.user.donation_set.all().order_by(
            'is_taken', 'pick_up_date'
        )

        context = {
            'donations': donations.filter(is_taken=filter_query) if filter_query else donations
        }
        return render(request, 'MyApp/user-donations.html', context=context)

    def post(self, request):
        donation = m.Donation.objects.get(id=request.POST.get('donation'))
        donation.is_taken = 1
        donation.archive_date = datetime.datetime.today()
        donation.save()
        return redirect(request.META['HTTP_REFERER'])


class UserConfirmationsView(View):
    def get(self, request):
        return render(request, 'MyApp/emails/email_confirmations.html')


class UserRegisterVerifyActivateLinkView(View):

    def get(self, request, link):
        try:
            rfc_4122_format = urlsafe_base64_decode(link).decode("UTF-8")
            user = m.ExtendedUser.objects.get(
                account__activation_uuid=uuid.UUID(rfc_4122_format)
            )
            user.account_is_active = True
            user.account.activation_uuid = None
            user.save()

        except (UnicodeDecodeError, ValueError, ObjectDoesNotExist):
            raise Http404

        return redirect('login')


class UserRemindPasswordView(View):
    def get(self, request):
        return render(request, 'MyApp/remind-password.html')

    def post(self, request):
        user_email = request.POST.get('email')
        if user := m.ExtendedUser.objects.get(email=user_email):
            reset_uuid = uuid.uuid4()
            user.account.reset_password_uuid = reset_uuid
            user.save()

            email = EmailTemplates(reset_uuid)
            email.send_reset_password_link(
                name=user.first_name,
                uuid=email.create_reset_password_link(request),
                to=[user_email]
            )

            msg = "Link do zresetowania hasla zostal przeslany na podany email."
            messages.add_message(request, messages.INFO, msg)

            return redirect('user-confirmation')

        return redirect('remind-password')


class UserPasswordResetView(View):
    def get(self, request, link):
        try:
            rfc_4122_format = urlsafe_base64_decode(link).decode("UTF-8")
            m.ExtendedUser.objects.get(
                account__reset_password_uuid=uuid.UUID(rfc_4122_format)
            )
        except (ValueError, UnicodeDecodeError, ObjectDoesNotExist):
            raise Http404

        return render(request, 'MyApp/reset-password.html')

    def post(self, request, link):
        try:
            rfc_4122_format = urlsafe_base64_decode(link).decode("UTF-8")
            user = m.ExtendedUser.objects.get(
                account__reset_password_uuid=uuid.UUID(rfc_4122_format)
            )
            data = request.POST
            password = data.get('password')
            password2 = data.get('password2')

            if password != password2:
                msg = 'Podane hasła się roznia.'
                messages.add_message(request, messages.ERROR, msg)
                return redirect('reset-password', link)

            user.set_password(password)
            user.account.reset_password_uuid = None
            user.save()

        except (UnicodeDecodeError, ValueError, ObjectDoesNotExist):
            raise Http404

        return redirect('login')
