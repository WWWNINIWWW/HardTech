from rest_framework import status
from rest_framework.response import Response
from rest_framework import generics
from backend.models import PC, Dados
from backend.serializers import PCSerializer, PCPowerUpdateSerializer
from rest_framework.decorators import api_view
from django.db.models import Avg, DateTimeField
from django.db.models.functions import TruncDate
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP


class PCList(generics.ListCreateAPIView):
    queryset = PC.objects.all()
    serializer_class = PCSerializer

    def create(self, request, *args, **kwargs):
        user = request.data.get('user')
        dados_data = request.data.get('dados', [])

        try:
            pc = PC.objects.get(user=user)
            created = False
        except PC.DoesNotExist:
            pc = PC.objects.create(user=user)
            created = True

        for dado_data in dados_data:
            dado_data['pc'] = pc.id  # Adiciona a referência ao PC
            Dados.objects.create(
                pc=pc,
                temperatura=dado_data['temperatura'],
                uso_CPU=dado_data['uso_CPU'],
                uso_RAM=dado_data['uso_RAM'],
                data_recebimento=datetime.now()  # Adiciona a data de recebimento atual
            )

        serializer = self.get_serializer(pc)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(serializer.data, status=status_code)

class PCPowerUpdateView(generics.UpdateAPIView):
    queryset = PC.objects.all()
    serializer_class = PCPowerUpdateSerializer
    lookup_field = 'user'

    def put(self, request, *args, **kwargs):
        user = self.kwargs.get('user')
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()  # Aqui o serializer vai chamar o método update do PCPowerUpdateSerializer
        return Response(serializer.data)


class UserPCList(generics.ListAPIView):
    serializer_class = PCSerializer

    def get_queryset(self):
        user = self.kwargs['user']
        return PC.objects.filter(user=user)


@api_view(['GET'])
def media_view(request):
    user = request.query_params.get('user', None)
    queryset = Dados.objects.all()
    if user:
        queryset = queryset.filter(pc__user=user)

    start_date = request.query_params.get('start_date', None)
    end_date = request.query_params.get('end_date', None)
    if start_date and end_date:
        queryset = queryset.filter(data_recebimento__range=[start_date, end_date])

    media_por_usuario_e_data = {}
    for dado in queryset:
        key = dado.pc.user
        if key not in media_por_usuario_e_data:
            media_por_usuario_e_data[key] = {}
        data = dado.data_recebimento.strftime('%Y-%m-%d')
        if data not in media_por_usuario_e_data[key]:
            media_por_usuario_e_data[key][data] = {
                'media_temperatura': Decimal(0),
                'media_uso_CPU': Decimal(0),
                'media_uso_RAM': Decimal(0),
                'count': 0
            }
        media_por_usuario_e_data[key][data]['media_temperatura'] += dado.temperatura
        media_por_usuario_e_data[key][data]['media_uso_CPU'] += dado.uso_CPU
        media_por_usuario_e_data[key][data]['media_uso_RAM'] += dado.uso_RAM
        media_por_usuario_e_data[key][data]['count'] += 1

    for user, data_dict in media_por_usuario_e_data.items():
        for data, values in data_dict.items():
            values['media_temperatura'] /= values['count']
            values['media_temperatura'] = values['media_temperatura'].quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
            values['media_uso_CPU'] /= values['count']
            values['media_uso_CPU'] = values['media_uso_CPU'].quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
            values['media_uso_RAM'] /= values['count']
            values['media_uso_RAM'] = values['media_uso_RAM'].quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
            del values['count']
            values['media_temperatura'] = f"{values['media_temperatura']} ºC"
            values['media_uso_CPU'] = f"{values['media_uso_CPU']} %"
            values['media_uso_RAM'] = f"{values['media_uso_RAM']} %"

    return Response(media_por_usuario_e_data)

@api_view(['GET'])
def user_media_view(request, user):
    queryset = Dados.objects.filter(pc__user=user)

    start_date = request.query_params.get('start_date', None)
    end_date = request.query_params.get('end_date', None)
    if start_date and end_date:
        queryset = queryset.filter(data_recebimento__range=[start_date, end_date])

    media_por_usuario_e_data = {}
    for dado in queryset:
        key = dado.pc.user
        if key not in media_por_usuario_e_data:
            media_por_usuario_e_data[key] = {}
        data = dado.data_recebimento.strftime('%Y-%m-%d')
        if data not in media_por_usuario_e_data[key]:
            media_por_usuario_e_data[key][data] = {
                'media_temperatura': Decimal(0),
                'media_uso_CPU': Decimal(0),
                'media_uso_RAM': Decimal(0),
                'count': 0
            }
        media_por_usuario_e_data[key][data]['media_temperatura'] += dado.temperatura
        media_por_usuario_e_data[key][data]['media_uso_CPU'] += dado.uso_CPU
        media_por_usuario_e_data[key][data]['media_uso_RAM'] += dado.uso_RAM
        media_por_usuario_e_data[key][data]['count'] += 1

    for user, data_dict in media_por_usuario_e_data.items():
        for data, values in data_dict.items():
            values['media_temperatura'] /= values['count']
            values['media_temperatura'] = values['media_temperatura'].quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
            values['media_uso_CPU'] /= values['count']
            values['media_uso_CPU'] = values['media_uso_CPU'].quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
            values['media_uso_RAM'] /= values['count']
            values['media_uso_RAM'] = values['media_uso_RAM'].quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
            del values['count']
            values['media_temperatura'] = f"{values['media_temperatura']} ºC"
            values['media_uso_CPU'] = f"{values['media_uso_CPU']} %"
            values['media_uso_RAM'] = f"{values['media_uso_RAM']} %"

    return Response(media_por_usuario_e_data)