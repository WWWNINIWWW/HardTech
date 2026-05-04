from rest_framework import serializers
from backend.models import PC, Dados

class DadosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dados
        fields = ['temperatura', 'uso_CPU', 'uso_RAM', 'data_recebimento']
        
    def to_representation(self, instance):
        data = instance.data_recebimento.strftime('%d/%m/%Y %H:%M:%S')
        return {
            'temperatura': f"{instance.temperatura} ºC",
            'uso_CPU': f"{instance.uso_CPU} %",
            'uso_RAM': f"{instance.uso_RAM} %",
            'data_recebimento': data
        }

class PCSerializer(serializers.ModelSerializer):
    dados = DadosSerializer(many=True)

    class Meta:
        model = PC
        fields = ['user', 'mode_fan', 'update', 'dados']

    def create(self, validated_data):
        user = validated_data.pop('user')
        dados_data = validated_data.pop('dados')
        
        pc, created = PC.objects.get_or_create(user=user)

        for dado_data in dados_data:
            Dados.objects.create(pc=pc, **dado_data)

        return pc

# --- Novos Serializers para o Fan Mode ---

# Usado para visualizar o status de um ou todos os usuários
class PCFanStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = PC
        fields = ['user', 'mode_fan', 'update']

# Usado no PUT para trocar o modo da Fan e ativar o update automaticamente
class PCFanUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PC
        fields = ['mode_fan']

    def update(self, instance, validated_data):
        instance.mode_fan = validated_data.get('mode_fan', instance.mode_fan)
        instance.update = True  # Troca automaticamente para True quando o modo altera
        instance.save()
        return instance

# Usado no PUT para atualizar exclusivamente a variável update (ex: para voltar pra False)
class PCUpdateFlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = PC
        fields = ['update']