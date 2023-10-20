from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .models import Client, Car, Spring, Forces, Points
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
import time
from .utils.model3d import generatePoints
from .utils.fem import fem

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.views import APIView

from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm

from rest_framework.decorators import authentication_classes
from queryapp.authentication_mixins import Authentication
from queryapp.serializers import UserTokenSerializer

from datetime import datetime
import logging

def home(request):
    return render(request,'home.html')

def signup(request):

    if request.method == 'GET':
        return render(request,'signup.html', {
            'form': UserCreationForm
        })
    else:
        if request.POST['password1'] == request.POST['password2']:
            # register user
            try:
                user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1'])
                user.save()
                return HttpResponse('User created successfully')
            except:
                return render(request,'signup.html', {
                    'form': UserCreationForm,
                    'error': 'Username already exists'
                })
        return render(request,'signup.html', {
            'form': UserCreationForm,
            'error': 'Password do not match'
        }) 
    
class UserToken(APIView):
	
    def get(self, request, *args, **kwargs):
        username = request.GET.get('username')
        print(f"Received username: {username}")

        try:
            user = UserTokenSerializer().Meta.model.objects.filter(username=username).first()
            print(f"Retrieved user: {user}")
            print(f"Query: {str(UserTokenSerializer().Meta.model.objects.filter(username=username).query)}")

            if user:
                user_token = Token.objects.get(user=user)
                print(f"Retrieved token: {user_token.key}")

                return Response({
                    'token': user_token.key
                })
            else:
                return Response({
                    'error': 'User not found.'
                }, status=status.HTTP_404_NOT_FOUND)

        except Token.DoesNotExist:
            return Response({
                'error': 'Token not found for the user.'
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            # Log the exception for debugging
            logging.error(str(e))
            return Response({
                'error': 'An error occurred.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Login(ObtainAuthToken):

    def post(self,request,*args,**kwargs):
        login_serializer = self.serializer_class(data = request.data, context = {'request':request})
        if login_serializer.is_valid():
            user = login_serializer._validated_data['user']
            if user.is_active:
                token,created = Token.objects.get_or_create(user=user)
                user_serializer = UserTokenSerializer(user)
                if created:
                    return Response({
                        'token': token.key,
                        'user': user_serializer.data,
                        'message': 'Inicio de Sesión Exitoso.'
                    },status=status.HTTP_201_CREATED)
                else:
                    # Gestion de sesiones: Solo una sesion activa por Pc. Se borran todas las sesiones cuando se tiene más de 1 sesión por usuario.
                    """
                    all_sessions = Session.objects.filter(expire_date__gte = datetime.now())
                    if all_sessions.exists():
                        for session in all_sessions:
                            session_data = session.get_decoded()
                            if user.id == int(session_data.get('_auth_user_id')):
                                session.delete()
                    token.delete()
                    token = Token.objects.create(user = user)
                    return Response({
                        'token': token.key,
                        'user': user_serializer.data,
                        'message': 'Inicio de Sesión Exitoso.'
                    },status=status.HTTP_201_CREATED)
                    """
                    # Gestión de login: Solo se puede iniciar sesion una vez, se tiene que cerrar la sesion anterior para iniciar nuevamanete en otro equipo.
                    token.delete()
                    return Response({
                        'error':'Ya se ha iniciado sesión con este usuario.'
                    }, status= status.HTTP_409_CONFLICT)
            else:
                return Response({'error':'Este usuario no puede iniciar sesión.'},status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'error':'Nombre de usuario o contraseña incorrectos.'},status=status.HTTP_400_BAD_REQUEST)
        return Response({'mensaje':'Hola desde response'},status=status.HTTP_200_OK)
    
class Logout(APIView):

    def get(self,request,*args,**kwargs):
        try:
            token = request.GET.get('token') # El frontend debe enviar el token con ese nombre de la varibale para que funcione.
            print(token)
            token = Token.objects.filter(key=token).first()
            
            if token:
                user = token.user

                all_sessions = Session.objects.filter(expire_date__gte = datetime.now())
                if all_sessions.exists():
                    for session in all_sessions:
                        session_data = session.get_decoded()
                        if user.id == int(session_data.get('_auth_user_id')):
                            session.delete()

                token.delete()

                session_message = 'Sesiones de usuario eliminadas.'
                token_message = 'Token eliminado'
                return Response({'token_message': token_message, 'session_message': session_message}, status=status.HTTP_200_OK)

            return Response({'error':'No se ha encontrado un usuario con estas credenciales.'}, status=status.HTTP_400_BAD_REQUEST)
        
        except:
            return Response({'error':'No se ha encontrado token en la petición.'}, status=status.HTTP_409_CONFLICT)

@api_view(['POST'])
def login(request):

    username = request.POST.get('username')
    password = request.POST.get('password')

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response("Usuario inválido")
    
    pwd_valid = check_password(password,user.password)

    if not pwd_valid:
        return Response("Contraseña inválida")

    token, created = Token.objects.get_or_create(user=user)

    print(token.key)
    return Response(token.key)

def log_out(request):
    logout(request)
    return redirect('home')

class Prueba(Authentication, viewsets.ModelViewSet):
    # Define your ModelViewSet configuration here
    
    def prueba(self, request):
        return HttpResponse("<h1>Hello</h1>")

# Create your views here.

def clients(request):
    clients = list(Client.objects.values())
    return JsonResponse(clients, safe=False)

@method_decorator(csrf_exempt)
def create_client(request):
    if request.method == 'POST':
        jd = json.loads(request.body)

        if jd['name'] and jd['dni_ruc']:
            client = Client.objects.create(name=jd['name'],dni_ruc=jd['dni_ruc'], phone_number=jd['phone_number'], email=jd['email'])
            client.save()
            return JsonResponse({'message':'Client created successfully!'})
        else:
            return JsonResponse({'message':'Invalid data, Both name and dni/ruc are required.'}, status=400)
        
    return JsonResponse({'message':'POST method required.'}, status=405)

@method_decorator(csrf_exempt)
def create_spring(request):
    if request.method == 'POST':
        jd = json.loads(request.body)

        if jd['wire'] and jd['coils']:
            spring = Spring.objects.create(
                wire=jd['wire'],
                diam_ext1=jd['diam_ext1'],
                diam_ext2=jd['diam_ext2'],
                diam_int1=jd['diam_int1'],
                diam_int2=jd['diam_int2'],
                length=jd['length'],
                coils=jd['coils'],
                coil_direction=jd['coil_direction'],
                end1=jd['end1'],
                luz1=jd['luz1'],
                coils_red_1=jd['coils_red_1'],
                coils_amp_1=jd['coils_amp_1'],
                detail1_end1=jd['detail1_end1'],
                detail2_end1=jd['detail2_end1'],
                detail3_end1=jd['detail3_end1'],
                eccentricity1=jd['eccentricity1'],
                end2=jd['end2'],
                luz2=jd['luz2'],
                coils_red_2=jd['coils_red_2'],
                coils_amp_2=jd['coils_amp_2'],
                detail1_end2=jd['detail1_end2'],
                detail2_end2=jd['detail2_end2'],
                detail3_end2=jd['detail3_end2'],
                eccentricity2=jd['eccentricity2'],
                grade=jd['grade']
                )
            spring.save()
            points = generatePoints(spring)
            return JsonResponse(points, safe=False)
        else:
            return JsonResponse({'message':'Invalid data, Both wire and coils are required.'}, status=400)
        
    return JsonResponse({'message':'POST method required.'}, status=405)

@method_decorator(csrf_exempt)
def simulate_spring(request):
    if request.method == 'POST':
        jd = json.loads(request.body)

        if jd['wire'] and jd['coils']:
            spring = Spring.objects.create(
                wire=jd['wire'],
                diam_ext1=jd['diam_ext1'],
                diam_ext2=jd['diam_ext2'],
                diam_int1=jd['diam_int1'],
                diam_int2=jd['diam_int2'],
                length=jd['length'],
                coils=jd['coils'],
                coil_direction=jd['coil_direction'],
                end1=jd['end1'],
                luz1=jd['luz1'],
                coils_red_1=jd['coils_red_1'],
                coils_amp_1=jd['coils_amp_1'],
                detail1_end1=jd['detail1_end1'],
                detail2_end1=jd['detail2_end1'],
                detail3_end1=jd['detail3_end1'],
                eccentricity1=jd['eccentricity1'],
                end2=jd['end2'],
                luz2=jd['luz2'],
                coils_red_2=jd['coils_red_2'],
                coils_amp_2=jd['coils_amp_2'],
                detail1_end2=jd['detail1_end2'],
                detail2_end2=jd['detail2_end2'],
                detail3_end2=jd['detail3_end2'],
                eccentricity2=jd['eccentricity2'],
                grade=jd['grade']
                )
            
            start_time = time.time()
            NodeX, NodeY,NodeZ, storeForceSum, storeDispl, storeStress, deform, simulations = fem(spring)

            force = Forces(
                    forces= storeForceSum,
                    displacements = [(deform + deform*j) for j in range(simulations)],
                    spring = spring
            )

            force_data = {
                'forces': list(force.forces),
                'displacements': list(force.displacements)
            }

            points=[]

            points_data = []
            
            for i in range(len(NodeX)):
                posX, posY, posZ, stress = ([] for k in range(4))
                for j in range(len(storeDispl)):
                    posX.append(NodeX[i] + storeDispl[j][i][0])
                    posY.append(NodeY[i] + storeDispl[j][i][1])
                    posZ.append(NodeZ[i] + storeDispl[j][i][2])
                    if i == len(NodeX) - 1:
                        stress.append(storeStress[j][i-1])
                    else:  
                        stress.append(storeStress[j][i])

                point = Points(posx = posX,
                                posy = posY,
                                posz = posZ,
                                esf = stress,
                                spring = spring)
                points.append(point)

                point_data = {
                    'posx': point.posx,
                    'posy': point.posy,
                    'posz': point.posz,
                    'esf': point.esf,
                }
                points_data.append(point_data)

            print(time.time() - start_time)
            
            datos={'message': 'Success', 'spring': spring.to_dict(),'points': points_data, 'forces': force_data}
            return JsonResponse(datos, safe=False)

        else:
            return JsonResponse({'message':'Invalid data, Both wire and coils are required.'}, status=400)
        
    return JsonResponse({'message':'POST method required.'}, status=405)

def cars(request, id):
    #car = Car.objects.get(id=id)
    car = get_object_or_404(Car, id=id)
    return HttpResponse('Car: %s ' % car.brand + ' ' + car.model)