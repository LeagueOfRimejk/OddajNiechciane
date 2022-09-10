import json
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Sum


# Create your models here.

class ExtendedUser(AbstractUser):

    account_is_active = models.BooleanField(default=False)

    @classmethod
    def validate_user_data(cls, email, password):
        user = cls.objects.all().filter(username=email).first()
        if user and user.check_password(password):
            return user

    def save(self, *args, **kwargs):
        super().save()
        if hasattr(self, 'account'):
            self.account.save()
        else:
            self.activation = Account.objects.create(
                activation=self,
                activation_uuid=uuid.uuid4()
            )


class Account(models.Model):

    activation = models.OneToOneField(
        ExtendedUser,
        on_delete=models.CASCADE,
    )

    activation_uuid = models.UUIDField(unique=True, null=True, blank=True)
    reset_password_uuid = models.UUIDField(null=True, blank=True, unique=True)


class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Institution(models.Model):

    # Institution type choices.
    class InstitutionTypeChoices(models.IntegerChoices):
        FOUNDATION = 1, 'Fundacja'
        N_GOV_ORGANIZATION = 2, 'Organizacja pozarządowa'
        LOCAL_COLLECTION = 3, 'Zbiórka lokalna'

    # Institution trust assess.
    class InstitutionIsTrustedChoices(models.IntegerChoices):
        TRUSTED = 1, 'Zaufana'
        UNTRUSTED = 0, 'Niezaufana'

    name = models.CharField(max_length=128)
    description = models.TextField()

    type = models.IntegerField(
        choices=InstitutionTypeChoices.choices,
        default=InstitutionTypeChoices.FOUNDATION
    )

    categories = models.ManyToManyField(Category)

    is_trusted = models.IntegerField(
        choices=InstitutionIsTrustedChoices.choices,
        default=0
    )

    @classmethod
    def query_set_to_json(cls, query_set):
        data = []
        [data.append(
            {'name': query.name,
             'description': f'Cel i misja: {query.description}',
             'categories': query.display_all_categories(),
             'type': query.type,
             }
        ) for query in query_set]
        return json.dumps(data)

    def display_all_categories(self):
        categories = self.categories.all()
        if not categories:
            return 'Przyjmiemy każdą pomoc.'
        return ', '.join([cat.name for cat in categories])

    def accepted_donations_id(self):
        return [category.pk for category in self.categories.all()]

    def __str__(self):
        return self.name


class Donation(models.Model):

    # Pick up status.
    class DonationPickUpStatusChoices(models.IntegerChoices):
        PICKED_UP = 1, 'Odebrana'
        NOT_PICKED_UP = 0, 'Nieodebrana'

    quantity = models.IntegerField()
    categories = models.ManyToManyField(Category)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    address = models.CharField(max_length=64)
    phone_number = models.CharField(max_length=64)
    city = models.CharField(max_length=64)
    post_code = models.CharField(max_length=64)
    pick_up_date = models.DateField(null=True, blank=True)
    pick_up_time = models.TimeField(null=True, blank=True)
    pick_up_remarks = models.TextField(null=True, blank=True)

    is_taken = models.IntegerField(
        choices=DonationPickUpStatusChoices.choices,
        default=0
    )

    archive_date = models.DateTimeField(null=True, blank=True)

    user = models.ForeignKey(
        ExtendedUser,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    @classmethod
    def quantity_sum(cls):
        bags = cls.objects.all().aggregate(q_sum=Sum('quantity'))['q_sum']
        return bags if bags else 0

    @classmethod
    def count_supported_institutions(cls):
        return cls.objects.all().count()

    def __str__(self):
        return self.institution
