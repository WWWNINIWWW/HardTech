from rest_framework import status
from rest_framework.response import Response
from rest_framework import generics
from backend.models import PC, Dados
from backend.serializers import (
    PCSerializer, 
    PCFanStatusSerializer, 
    PCFanUpdateSerializer, 
    PCUpdateFlagSerializer
)
from rest_framework.decorators import api_view
from django.db.models import Avg, DateTimeField
from django.db.models.functions import TruncDate
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from rest_framework.views import APIView


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




class PCFanStatusListView(generics.ListAPIView):
    queryset = PC.objects.all()
    serializer_class = PCFanStatusSerializer

# 2. Rota para visualizar (GET) e alterar (PUT) os valores de fan mode de usuário específico
class PCFanDetailAndUpdateView(generics.RetrieveUpdateAPIView):
    queryset = PC.objects.all()
    lookup_field = 'user'

    def get_serializer_class(self):
        # Se for para atualizar, usa o serializer que converte o update para True
        if self.request.method in ['PUT', 'PATCH']:
            return PCFanUpdateSerializer
        # Se for apenas leitura (GET), mostra os dados e o usuário
        return PCFanStatusSerializer

# 3. Rota de PUT apenas para a variável update (ex: para a placa informar que já leu o dado)
class PCUpdateFlagView(generics.UpdateAPIView):
    queryset = PC.objects.all()
    serializer_class = PCUpdateFlagSerializer
    lookup_field = 'user'
    
class PCFanUpdateByJSONView(APIView):
    def put(self, request, *args, **kwargs):
        # Extrai os dados do JSON recebido
        user_nome = request.data.get('user')
        mode_fan = request.data.get('mode_fan')


        # Verifica se ambos os campos foram enviados
        if not user_nome or mode_fan is None:
            return Response(
                {"erro": "Os campos 'user' e 'mode_fan' são obrigatórios no JSON."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Busca o PC pelo nome do usuário
            pc = PC.objects.get(user=user_nome)
            
            # Atualiza os valores
            pc.mode_fan = mode_fan
            pc.update = True  # Ativa a flag para avisar que houve mudança
            pc.save()
            
            # Retorna o status atualizado do PC para confirmar
            serializer = PCFanStatusSerializer(pc)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except PC.DoesNotExist:
            return Response(
                {"erro": f"Usuário '{user_nome}' não encontrado no banco de dados."},
                status=status.HTTP_404_NOT_FOUND
            )