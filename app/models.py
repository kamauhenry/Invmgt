from django.db import models
from django.db.models import Sum, F
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.crypto import get_random_string

# Utility function to generate a unique username
def generate_unique_username():
    """Generates a unique username with a maximum of 10 retries."""
    default_name = "user"
    max_retries = 10

    for _ in range(max_retries):
        unique_username = f"{default_name}_{get_random_string(length=8)}"
        if not CustomUser.objects.filter(username=unique_username).exists():
            return unique_username

    raise ValueError("Failed to generate unique username after %d attempts" % max_retries)

# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if extra_fields.get('tenant') is None:
            extra_fields['tenant'] = self.model.objects.create(username=generate_unique_username())

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        user = self.create_user(email, password=password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

# Custom User model
class CustomUser(AbstractUser):
    tenant = models.OneToOneField('self', on_delete=models.CASCADE, null=True, related_name='tenant_user')
    objects = CustomUserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

# Customizing the related name for permissions and groups
CustomUser._meta.get_field('groups').remote_field.related_name = 'customuser_groups'
CustomUser._meta.get_field('user_permissions').remote_field.related_name = 'customuser_user_permissions'

# Define the sqlserverconn model with Subtotal property
class sqlserverconn(models.Model):
    tenant = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    Item_id = models.BigAutoField(primary_key=True, db_column='Item_id')
    Item = models.CharField(max_length=30, db_index=True, db_column='Item')
    Item_Description = models.CharField(max_length=30, null=True, blank=True)
    Units = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    Unit_of_measurement = models.CharField(max_length=15, null=True, blank=True)
    Unit_cost = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    Date = models.DateField()
    Subtotal = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    grouped_item = models.ForeignKey(
        'GroupedItems',
        on_delete=models.CASCADE,
        related_name='sqlserverconns',
        to_field='grouped_item',
    )

    def associate_similar_items(self):
        grouped_item, created = GroupedItems.objects.get_or_create(grouped_item=self.Item)
        self.grouped_item = grouped_item
        self.save()

    def __str__(self):
        return self.Item

    def save(self, *args, **kwargs):
        self.associate_similar_items()
        self.Subtotal = self.Unit_cost * self.Units
        super().save(*args, **kwargs)
        self.grouped_item.calculate_totals()

    class Meta:
        indexes = [
            models.Index(fields=['Item'], name='item_idx'),
        ]

class Labour(models.Model):
    tenant = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    labour_type = models.CharField(max_length=20)
    NOL = models.PositiveIntegerField()
    Date = models.DateField(default=timezone.now)
    labourer_cost = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    sub_total = models.DecimalField(max_digits=15, decimal_places=4, default=0)

    def __str__(self):
        return self.labour_type

    def save(self, *args, **kwargs):
        self.sub_total = self.labourer_cost * self.NOL
        super().save(*args, **kwargs)

# Define the GroupedItems model
class GroupedItems(models.Model):
    id = models.BigAutoField(primary_key=True)
    grouped_item = models.CharField(max_length=30, unique=True)
    total_units = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    total = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    used_units = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    units_available = models.DecimalField(max_digits=15, decimal_places=4, default=0)

    def calculate_totals(self):
        issue_items = self.issue_items.all()
        self.used_units = issue_items.aggregate(units_used=Sum('units_used'))['units_used'] or 0
        self.units_available = F('total_units') - F('used_units')
        
        sqlserverconn_aggregate = sqlserverconn.objects.filter(grouped_item=self).aggregate(
            total_units=Sum('Units'),
            total=Sum(F('Subtotal'))
        )
        self.total_units = sqlserverconn_aggregate['total_units'] or 0
        self.total = sqlserverconn_aggregate['total'] or 0
        self.save()

    def __str__(self):
        return self.grouped_item

    class Meta:
        indexes = [
            models.Index(fields=['grouped_item', 'total_units'], name='grouped_item_total_units_idx'),
        ]

class Person(models.Model):
    tenant = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    person = models.CharField(max_length=20)

    def __str__(self):
        return self.person

class IssueItem(models.Model):
    id = models.BigAutoField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    grouped_item = models.ForeignKey(
        GroupedItems,
        on_delete=models.CASCADE,
        related_name='issue_items'
    )
    units_issued = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    units_returned = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    units_used = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    Date = models.DateField(default=timezone.now)

    def save(self, *args, **kwargs):
        self.units_used = self.units_issued - self.units_returned
        super().save(*args, **kwargs)
        self.grouped_item.calculate_totals()

    def __str__(self):
        return str(self.person)

class Custom_UOM(models.Model):
    UOM = models.CharField(max_length=20, primary_key=True)

    def __str__(self):
        return self.UOM

# Signal handlers
@receiver(post_save, sender=IssueItem)
@receiver(post_save, sender=sqlserverconn)
def update_totals_on_related_save(sender, instance, **kwargs):
    instance.grouped_item.calculate_totals()

@receiver(post_save, sender=sqlserverconn)
def create_issue_item(sender, instance, **kwargs):
    grouped_item, _ = GroupedItems.objects.get_or_create(grouped_item=instance.Item)
    instance.grouped_item = grouped_item
    if instance.pk is None:
        grouped_item.save()
