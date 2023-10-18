from django.contrib import admin
from .models import User, Client, Car, CargoControl, Spring, SampleSpring, Design, SpringPointsDesign, DesignedSpring, ProducedSpring, QualityControlReport

# Register your models here.
admin.site.register(User)
admin.site.register(Client)
admin.site.register(Car)
admin.site.register(CargoControl)
admin.site.register(Spring)
admin.site.register(SampleSpring)
admin.site.register(Design)
admin.site.register(SpringPointsDesign)
admin.site.register(DesignedSpring)
admin.site.register(ProducedSpring)
admin.site.register(QualityControlReport)