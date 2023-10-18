from django.db import models
from django.contrib.postgres.fields import ArrayField

from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin, Group, Permission
from simple_history.models import HistoricalRecords

from django.utils.translation import gettext as _

# Gestion de usuarios
class UserManager(BaseUserManager):
    def _create_user(self,username,email,first_name,last_name,password,is_staff,is_superuser,**extra_fields):
        user = self.model(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_staff=is_staff,
            is_superuser=is_superuser,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self.db)
        return user
    
    def create_user(self,username,email,first_name,last_name,password=None,**extra_fields):
        return self._create_user(username,email,first_name,last_name,password,False,False,**extra_fields)
    
    def create_superuser(self,username,email,first_name,last_name,password=None,**extra_fields):
        return self._create_user(username,email,first_name,last_name,password,True,True,**extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255,unique=True)
    email = models.EmailField('Correo Electrónico',max_length=255,unique=True)
    first_name = models.CharField('Nombres',max_length=255,blank=True,null=True)
    last_name = models.CharField('Apellidos',max_length=255,blank=True,null=True)
    image = models.ImageField('Imagen de perfil',upload_to='perfil/',max_length=255,null=True,blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    historical = HistoricalRecords()
    objects = UserManager()
    groups = models.ManyToManyField(Group, verbose_name=_('groups'), related_name='queryapp_users')
    user_permissions = models.ManyToManyField(Permission, verbose_name=_('user permissions'), related_name='queryapp_users')

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email','first_name','last_name']

    def natural_key(self):
        return (self.username)
    
    def __str__(self):
        return f'{self.first_name} {self.last_name}'

# Create your models here.
class Dbauth(models.Model):
    email = models.CharField(max_length=30, null=1)
    password = models.CharField(max_length=30, null=1)
    token = models.CharField(max_length=30, null=1)
    user_type = models.IntegerField(null=1)

class Client(models.Model):
    name = models.CharField(max_length=80)
    dni_ruc = models.CharField(max_length=11)
    phone_number = models.CharField(max_length=9)
    email = models.CharField(max_length=30, null=1)

    def __str__(self):
        return self.name

class Car(models.Model):
    vin = models.CharField(max_length=17)
    brand = models.CharField(max_length=11)
    model = models.CharField(max_length=20)
    year = models.CharField(max_length=4)
    bodywork = models.CharField(max_length=16,null=1)
    plate = models.CharField(max_length=7,null=1)
    fuel = models.CharField(max_length=18,null=1)
    displacement = models.CharField(max_length=5,null=1)
    wheel_drive = models.CharField(max_length=9,null=1)
    gas_tank = models.CharField(max_length=14,null=1)
    net_weight = models.IntegerField(null=1)
    gross_weight = models.IntegerField(null=1)
    rows_seats = models.IntegerField(null=1)
    mileage_km = models.IntegerField(null=1)
    original_tire_width = models.IntegerField(null=1)
    original_aspect_ratio = models.IntegerField(null=1)
    original_wheel_diameter = models.IntegerField(null=1)
    installed_tire_width = models.IntegerField(null=1)
    installed_aspect_ratio = models.IntegerField(null=1)
    installed_wheel_diameter = models.IntegerField(null=1)
    car_use = models.CharField(max_length=18,null=1)
    extra_charge = models.CharField(max_length=25,null=1)

    def __str__(self):
        return self.brand + " " + self.model + " " + self.year

class Spring(models.Model):
    wire = models.DecimalField(max_digits=4, decimal_places=2)
    diam_ext1 = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    diam_ext2 = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    diam_int1 = models.DecimalField(max_digits=6, decimal_places=3, default=0)
    diam_int2 = models.DecimalField(max_digits=6, decimal_places=3, default=0)
    length = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    coils = models.DecimalField(max_digits=6, decimal_places=3, default=0)
    coil_direction = models.CharField(max_length=20, default="-")
    end1 = models.CharField(max_length=50, default="-")
    luz1 = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    coils_red_1 = models.DecimalField(max_digits=6, decimal_places=3, default=0)
    coils_amp_1 = models.DecimalField(max_digits=6, decimal_places=3, default=0)
    detail1_end1 = models.CharField(max_length=15, default="-")
    detail2_end1 = models.CharField(max_length=15, default="-")
    detail3_end1 = models.CharField(max_length=15, default="-")
    eccentricity1 = models.DecimalField(max_digits=6, decimal_places=3, default=0)
    end2 = models.CharField(max_length=50, default="-")
    luz2 = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    coils_red_2 = models.DecimalField(max_digits=6, decimal_places=3, default=0)
    coils_amp_2 = models.DecimalField(max_digits=6, decimal_places=3, default=0)
    detail1_end2 = models.CharField(max_length=15, default="-")
    detail2_end2 = models.CharField(max_length=15, default="-")
    detail3_end2 = models.CharField(max_length=15, default="-")
    eccentricity2 = models.DecimalField(max_digits=6, decimal_places=3, default=0)
    grade = models.IntegerField(default=2)

    def to_dict(self):
        return {
            'wire': self.wire,
            'diam_ext1': self.diam_ext1,
            'diam_ext2': self.diam_ext2,
            'diam_int1': self.diam_int1,
            'diam_int2': self.diam_int2,
            'length': self.length,
            'coils': self.coils,
            'coil_direction': self.coil_direction,
            'end1': self.end1,
            'luz1': self.luz1,
            'coils_red_1': self.coils_red_1,
            'coils_amp_1': self.coils_amp_1,
            'detail1_end1': self.detail1_end1,
            'detail2_end1': self.detail2_end1,
            'detail3_end1': self.detail3_end1,
            'eccentricity1': self.eccentricity1,
            'end2': self.end2,
            'luz2': self.luz2,
            'coils_red_2': self.coils_red_2,
            'coils_amp_2': self.coils_amp_2,
            'detail1_end2': self.detail1_end2,
            'detail2_end2': self.detail2_end2,
            'detail3_end2': self.detail3_end2,
            'eccentricity2': self.eccentricity2,
            'grade': self.grade
        }

class Forces(models.Model):
    forces = ArrayField(models.DecimalField(max_digits=5, decimal_places=1), default=list)
    displacements = ArrayField(models.DecimalField(max_digits=5, decimal_places=1), default=list)
    spring = models.ForeignKey(Spring, on_delete=models.CASCADE, default="0")

    def __str__(self):
        arr = []
        for i in self.forces:
            print(i)
            arr.append(i)
        return f'{arr}'
    
class Points(models.Model):
    posx = ArrayField(models.DecimalField(max_digits=5, decimal_places=1), default=list)
    posy = ArrayField(models.DecimalField(max_digits=5, decimal_places=1), default=list)
    posz = ArrayField(models.DecimalField(max_digits=5, decimal_places=1), default=list)
    esf = ArrayField(models.DecimalField(max_digits=5, decimal_places=1), default=list)
    spring = models.ForeignKey(Spring, on_delete=models.CASCADE, default="0")

class CargoControl(models.Model):
    f1 = models.DecimalField(max_digits=6, decimal_places=2, null=1)
    f2 = models.DecimalField(max_digits=6, decimal_places=2, null=1) 
    f3 = models.DecimalField(max_digits=6, decimal_places=2, null=1)
    f4 = models.DecimalField(max_digits=6, decimal_places=2, null=1)
    f5 = models.DecimalField(max_digits=6, decimal_places=2, null=1)
    f6 = models.DecimalField(max_digits=6, decimal_places=2, null=1)
    f7 = models.DecimalField(max_digits=6, decimal_places=2, null=1) 
    f8 = models.DecimalField(max_digits=6, decimal_places=2, null=1)
    f9 = models.DecimalField(max_digits=6, decimal_places=2, null=1)
    f10 = models.DecimalField(max_digits=6, decimal_places=2, null=1)
    l1 = models.DecimalField(max_digits=6, decimal_places=2, null=1)
    l2 = models.DecimalField(max_digits=6, decimal_places=2, null=1) 
    l3 = models.DecimalField(max_digits=6, decimal_places=2, null=1)
    l4 = models.DecimalField(max_digits=6, decimal_places=2, null=1)
    l5 = models.DecimalField(max_digits=6, decimal_places=2, null=1)
    l6 = models.DecimalField(max_digits=6, decimal_places=2, null=1)
    l7 = models.DecimalField(max_digits=6, decimal_places=2, null=1) 
    l8 = models.DecimalField(max_digits=6, decimal_places=2, null=1)
    l9 = models.DecimalField(max_digits=6, decimal_places=2, null=1)
    l10 = models.DecimalField(max_digits=6, decimal_places=2, null=1)
    spring =models.OneToOneField(Spring, on_delete=models.CASCADE, null=False, blank=False, default=1)

class SampleSpring(models.Model):
    spring_type = models.CharField(max_length=10)
    spring_position = models.CharField(max_length=9)
    suspension_type = models.CharField(max_length=16)
    source = models.CharField(max_length=15)
    coil_spacer = models.CharField(max_length=20)
    spacer_height = models.IntegerField()
    spring = models.OneToOneField(Spring, on_delete=models.CASCADE, null=False, blank=False)

class DesignedSpring(models.Model):
    osis_code = models.IntegerField()
    selected = models.BooleanField(default=0)
    l_inst = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    l_charg = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    l_max = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    l_4 = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    raw_material = models.CharField(max_length=20, default='-')
    weight = models.DecimalField(max_digits=6, decimal_places=3, default=0)
    transition_point = models.IntegerField(null=1)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    lda = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    spring = models.OneToOneField(Spring, on_delete=models.CASCADE, null=False, blank=False)

class Design(models.Model):
    correlative = models.IntegerField()
    status = models.CharField(max_length=11)
    registration_date = models.DateField()
    development = models.CharField(max_length=12)
    request_reason = models.CharField(max_length=100)
    aplication = models.CharField(max_length=100)
    osis_code = models.IntegerField()
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    sample_spring = models.ForeignKey(SampleSpring, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    designed_spring = models.ForeignKey(DesignedSpring, on_delete=models.CASCADE)

class SpringPointsDesign(models.Model):
    length = models.DecimalField(max_digits=5, decimal_places=2)
    coils = models.DecimalField(max_digits=6, decimal_places=3)
    include_point = models.BooleanField()

class ProducedSpring(models.Model):
    osis_code = models.IntegerField()
    produced_date = models.DateField()
    spring = models.ForeignKey(Spring, on_delete=models.CASCADE,null=False, blank=False)

class QualityControlReport(models.Model):
    report_number = models.CharField(max_length=15)
    production_requirement = models.CharField(max_length=15)
    work_order = models.CharField(max_length=15)
    design = models.ForeignKey(Design, on_delete=models.CASCADE)
    designed_spring = models.ForeignKey(DesignedSpring, on_delete=models.CASCADE)
    produced_spring = models.ForeignKey(ProducedSpring, on_delete=models.CASCADE)
