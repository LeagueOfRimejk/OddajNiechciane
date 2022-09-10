from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import re


class PasswordCapitalLettersValidator:
    """
    Validate if password contains at least one capital letter.
    """

    def validate(self, password, user=None, *args, **kwargs):

        # pattern = """
        # [A-Z]|\u00C4|\u00CB|\u00D3|\u00D6|\u00DC|\u0106|\u0118|\u0141|\u0143|
        # \u0150|\u015A|\u0170|\u0179|\u017B|\u01EA|\u0228
        # """

        found = re.search(
            """[A-Z]|\u00C4|\u00CB|\u00D3|\u00D6|\u00DC|\u0106|\u0118|\u0141|
            \u0143|\u0150|\u015A|\u0170|\u0179|\u017B|\u01EA|\u0228""",
            password
        )

        if not found:
            raise ValidationError(
                _("Haslo nie zawiera wielkiej litery."),
                code="password_no_capital_letter",
            )

    def get_help_text(self):
        return _("Your password does not contain Capital letter.")


class PasswordAllCapitalLettersValidator:
    """
    Validate if password mades of capital letters.
    """

    def validate(self, password, user=None, *args, **kwargs):

        if password.isupper():
            raise ValidationError(
                _("Haslo nie moze skladac sie wylacznie z wielkich liter."),
                code="password_made_of_capital_letters",
            )

    def get_help_text(self):
        return _("Your password is made of all capital letters.")


class PasswordSpecialSignValidator:
    """
    Validate if password contains at least one special sign.
    """

    def validate(self, password, user=None, *args, **kwargs):
        pattern = r"""\u0021|\u0022|\u0023|\u0024|\u0025|\u0026|\u0027|\u0028|
        \u0029|\u002A|\u002B|\u002C|\u002D|\u002E|\u002F|\u003A|\u003B|\u003C|
        \u003D|\u003E|\u003F|\u0040|\u005B|\u005C|\u005D|\u005E|\u005F|\u0060|
        \u007B|\u007C|\u007D|\u007E|\u00A8|\u00AF|\u00B7|\u00B8"""

        if not re.search(pattern, password):
            raise ValidationError(
                _("Haslo nie zawiera znaku specjalnego."),
                code="password_no_special_sign",
            )

    def get_help_text(self):
        return _("Your password does not contain special character.")


class PasswordWhiteSignValidator:
    """
    Validate if password contains white sign.
    """

    def validate(self, password, user=None, *args, **kwargs):
        pattern = r"\u0020"

        if re.search(pattern, password):
            raise ValidationError(
                _("Haslo nie moze zawierac bialych znakow."),
                code="password_white_sign",
            )

    def get_help_text(self):
        return _("Your password contains white signs.")


VALIDATORS = [
    PasswordCapitalLettersValidator,
    PasswordAllCapitalLettersValidator,
    PasswordSpecialSignValidator,
    PasswordWhiteSignValidator,
]
